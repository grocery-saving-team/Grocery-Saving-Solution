import streamlit as st
import pandas as pd
import ast
import os
from pathlib import Path

# =========================
# 1. Data loaders (cached)
# =========================

@st.cache_data
def load_aisle_lookup():
    """Load aisle names and IDs from aisles.csv."""
    path = "data/aisles.csv"
    if not os.path.exists(path): return pd.DataFrame()
    df = pd.read_csv(path)
    # Clean column names
    df.columns = [str(c).strip() for c in df.columns]
    if "aisle_id" not in df.columns or "aisle" not in df.columns:
        return pd.DataFrame()
    out = df[["aisle_id", "aisle"]].dropna().drop_duplicates().copy()
    out["aisle_id"] = pd.to_numeric(out["aisle_id"], errors="coerce").fillna(0).astype(int)
    return out.sort_values("aisle")

@st.cache_data
def load_products_df():
    """Load product details and their aisle mappings."""
    path = "data/products.csv"
    if not os.path.exists(path): return pd.DataFrame()
    df = pd.read_csv(path)
    df.columns = [str(c).strip() for c in df.columns]
    df["product_id"] = pd.to_numeric(df["product_id"], errors="coerce")
    df["aisle_id"] = pd.to_numeric(df["aisle_id"], errors="coerce")
    df = df.dropna(subset=["product_id", "aisle_id"])
    df["product_id"] = df["product_id"].astype(int)
    df["aisle_id"] = df["aisle_id"].astype(int)
    return df

@st.cache_data
def load_rules_df():
    """Load the generated FP-Growth association rules."""
    path = "data/fpg_rules.csv"
    if not os.path.exists(path): return pd.DataFrame()
    return pd.read_csv(path)

# =========================
# 2. Recommendation Logic
# =========================

def _parse_itemset_to_ints(x):
    """Safely converts rule strings into sets of integer IDs."""
    if isinstance(x, (set, frozenset, list, tuple)):
        items = list(x)
    else:
        s = str(x).strip()
        if s.startswith("frozenset("): s = s[len("frozenset("):-1]
        try:
            v = ast.literal_eval(s)
            items = list(v) if isinstance(v, (set, frozenset, list, tuple)) else []
        except: items = []
    
    out = set()
    for item in items:
        # Clean ID: handles '26209.0' or '26209'
        clean = str(item).strip("'").strip('"').split('.')[0]
        if clean.isdigit():
            out.add(int(clean))
    return out

def generate_basket_for_aisles(selected_aisle_ids, rules_df, products_df, basket_size=8):
    """Generates a combined basket for the selected aisles using association rules."""
    selected_aisle_ids = set(selected_aisle_ids)
    if rules_df.empty or products_df.empty or not selected_aisle_ids:
        return []

    # Map Product -> Aisle ID
    prod2aisle = dict(zip(products_df["product_id"], products_df["aisle_id"]))
    
    df = rules_df.copy()
    df["A"] = df["antecedents"].apply(_parse_itemset_to_ints)
    df["C"] = df["consequents"].apply(_parse_itemset_to_ints)

    # Aggressive Matching: Check if ANY item in the rule (Input or Output) belongs to the aisle
    def rule_matches(row):
        full_bundle = row["A"].union(row["C"])
        return any(prod2aisle.get(pid) in selected_aisle_ids for pid in full_bundle)

    # Filter and Sort by Lift (strength of association)
    df = df[df.apply(rule_matches, axis=1)].sort_values("lift", ascending=False)
    
    if df.empty: return []

    basket, seen = [], set()
    for _, row in df.iterrows():
        # Collect unique items from the rule to form the basket
        for pid in row["A"].union(row["C"]):
            if pid not in seen:
                basket.append(pid)
                seen.add(pid)
            if len(basket) >= basket_size: return basket
    return basket

# =========================
# 3. Render Function
# =========================

def init_state():
    defaults = {
        "aisle_show_all": False,
        "submitted_aisles": [],
        "show_aisle_bundle": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def render_aisle():
    init_state()

    # Load All Data
    aisle_lookup = load_aisle_lookup()
    products_df = load_products_df()
    rules_df = load_rules_df()

    if aisle_lookup.empty or products_df.empty:
        st.error("Could not load aisles or products. Check your 'data/' folder.")
        return

    left, right = st.columns([1, 1.2], gap="large")

    # --- LEFT PANEL: Selection ---
    with left:
        st.markdown('<div class="department-aisle-title">List of Aisles</div>', unsafe_allow_html=True)
        st.markdown('<div class="department-aisle-anchor"></div>', unsafe_allow_html=True)

        c1, c2 = st.columns([3, 1])
        with c1:
            search = st.text_input("", placeholder="Search ...", label_visibility="collapsed", key="aisle_search")
        with c2:
            order = st.selectbox("", ["A → Z", "Z → A"], label_visibility="collapsed", key="aisle_sort")

        all_aisles = aisle_lookup["aisle"].tolist()
        filtered = [a for a in all_aisles if search.lower() in a.lower()]
        filtered.sort(reverse=(order == "Z → A"))
        
        display_list = filtered if st.session_state.aisle_show_all else filtered[:5]

        selected_names = []
        for aisle in display_list:
            if st.checkbox(aisle.title(), key=f"aisle_{aisle}"):
                selected_names.append(aisle)

        if len(filtered) > 5:
            if st.button("........", key="toggle_aisle_list"):
                st.session_state.aisle_show_all = not st.session_state.aisle_show_all
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        _, mid, _ = st.columns([1, 2, 1])
        with mid:
            if st.button("Submit", key="submit_aisles", type="primary", use_container_width=True):
                st.session_state.submitted_aisles = selected_names
                st.session_state.show_aisle_bundle = True

    # --- RIGHT PANEL: Recommendations ---
    with right:
        st.markdown('<div class="bundle-title">Bundle Recommendation</div>', unsafe_allow_html=True)
        st.markdown('<div class="bundle-anchor"></div>', unsafe_allow_html=True)

        selected = st.session_state.submitted_aisles

        if st.session_state.show_aisle_bundle and selected:
            # Convert selected names back to IDs
            name_to_id = dict(zip(aisle_lookup["aisle"].str.lower(), aisle_lookup["aisle_id"]))
            selected_ids = [name_to_id.get(name.lower()) for name in selected]
            selected_ids = [int(i) for i in selected_ids if i is not None]

            if not selected_ids:
                st.warning("Please select at least one aisle.")
                return

            # Generate recommendations from the model
            basket_ids = generate_basket_for_aisles(
                selected_aisle_ids=selected_ids,
                rules_df=rules_df,
                products_df=products_df,
                basket_size=8
            )

            if not basket_ids:
                st.warning("No associations found for these aisles. Try more popular categories like 'Yogurt' or 'Water'.")
                return

            # Map IDs to names for UI display
            id_to_name = dict(zip(products_df["product_id"], products_df["product_name"]))
            basket_items = [id_to_name.get(pid, f"Product {pid}") for pid in basket_ids]

            # Display following the "Departments" style
            display_data = ["Selected Aisles"] + basket_items
            
            html = '<div class="bundle-row">'
            for i, item in enumerate(display_data):
                card_class = "bundle-card"
                if i == 0: card_class += " bundle-dept"
                elif i == 1: card_class += " best-item"
                html += f'<div class="{card_class}">{item}</div>'
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.info("Select aisle(s) on the left and click Submit.")