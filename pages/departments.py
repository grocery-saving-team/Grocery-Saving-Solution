import streamlit as st
import pandas as pd
import ast
from pathlib import Path

# =========================
# Data loaders (cached)
# =========================

@st.cache_data
def load_departments_lookup():
    """
    departments.csv in your project contains many extra columns.
    We only keep department_id + department.
    """
    df = pd.read_csv("data/departments.csv")
    df.columns = [str(c).strip() for c in df.columns]

    if "department_id" not in df.columns or "department" not in df.columns:
        return pd.DataFrame()

    out = df[["department_id", "department"]].dropna().drop_duplicates().copy()
    out["department_id"] = pd.to_numeric(out["department_id"], errors="coerce")
    out = out.dropna(subset=["department_id"])
    out["department_id"] = out["department_id"].astype(int)
    out["department"] = out["department"].astype(str)
    return out.sort_values("department")


@st.cache_data
def load_products_df():
    # Expected: product_id, product_name, department_id
    df = pd.read_csv("data/products.csv")
    df.columns = [str(c).strip() for c in df.columns]

    required = {"product_id", "product_name", "department_id"}
    if not required.issubset(set(df.columns)):
        return pd.DataFrame()

    df = df.copy()
    df["product_id"] = pd.to_numeric(df["product_id"], errors="coerce")
    df["department_id"] = pd.to_numeric(df["department_id"], errors="coerce")
    df = df.dropna(subset=["product_id", "department_id"])
    df["product_id"] = df["product_id"].astype(int)
    df["department_id"] = df["department_id"].astype(int)
    df["product_name"] = df["product_name"].astype(str)
    return df


@st.cache_data
def load_rules_df():
    # Expected: antecedents, consequents, lift (+ confidence optional)
    df = pd.read_csv("data/fpg_rules.csv")
    df.columns = [str(c).strip() for c in df.columns]
    return df


# =========================
# Helpers
# =========================

def _parse_itemset_to_ints(x):
    """
    Converts:
      frozenset({'31717'}) -> {31717}
      frozenset({31717})   -> {31717}
    Key fix: convert digit-strings to int so they match products.csv keys.
    """
    if isinstance(x, (set, frozenset, list, tuple)):
        items = list(x)
    else:
        s = str(x).strip()
        if s.startswith("frozenset("):
            s = s[len("frozenset("):-1]
        try:
            v = ast.literal_eval(s)
            items = list(v) if isinstance(v, (set, frozenset, list, tuple)) else []
        except Exception:
            items = []

    out = set()
    for item in items:
        if isinstance(item, str) and item.strip().isdigit():
            out.add(int(item.strip()))
        elif isinstance(item, (int, float)) and not pd.isna(item):
            out.add(int(item))
        # else: ignore non-numeric items
    return out


def generate_basket_for_departments(
    selected_department_ids,
    rules_df,
    products_df,
    basket_size=8,
    min_lift=1.01,
    min_conf=0.0,
):
    selected_department_ids = set(selected_department_ids)
    if rules_df.empty or products_df.empty: return []

    # Map Product -> Dept
    prod2dept = dict(zip(products_df["product_id"], products_df["department_id"]))

    df = rules_df.copy()
    # Parse both sides of the rule (A = Antecedents, C = Consequents)
    df["A"] = df["antecedents"].apply(_parse_itemset_to_ints)
    df["C"] = df["consequents"].apply(_parse_itemset_to_ints)

    # Filter by strength
    df = df[df["lift"] >= float(min_lift)].sort_values("lift", ascending=False)

    # AGGRESSIVE MATCHING: A rule matches if ANY item in the bundle belongs to the department
    def rule_matches(row):
        full_bundle = row["A"].union(row["C"])
        return any(prod2dept.get(pid) in selected_department_ids for pid in full_bundle)

    df = df[df.apply(rule_matches, axis=1)]
    
    if df.empty: return []

    # Build the basket
    basket, seen = [], set()
    for _, row in df.iterrows():
        for pid in row["A"].union(row["C"]):
            if pid not in seen:
                basket.append(pid)
                seen.add(pid)
            if len(basket) >= basket_size: return basket
    return basket


# =========================
# SESSION STATE INITIALIZATION
# =========================
def init_state():
    defaults = {
        "show_all": False,
        "submitted_departments": [],
        "show_bundle": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# =========================
# RENDER FUNCTION
# =========================
def render_departments():
    init_state()

    # Ensure files exist
    if not Path("data/products.csv").exists():
        st.error("Missing file: data/products.csv")
        return
    if not Path("data/fpg_rules.csv").exists():
        st.error("Missing file: data/fpg_rules.csv")
        return

    dept_lookup = load_departments_lookup()
    products_df = load_products_df()
    rules_df = load_rules_df()

    if dept_lookup.empty:
        st.error("departments.csv must contain 'department_id' and 'department'.")
        return
    if products_df.empty:
        st.error("products.csv must contain: product_id, product_name, department_id.")
        return

    departments = dept_lookup["department"].tolist()

    left, right = st.columns([1, 1.2], gap="large")

    # ================= LEFT PANEL =================
    with left:
        st.markdown('<div class="department-aisle-title">List of Department</div>', unsafe_allow_html=True)
        st.markdown('<div class="department-aisle-anchor"></div>', unsafe_allow_html=True)

        c1, c2 = st.columns([3, 1])
        with c1:
            search = st.text_input("", placeholder="Search ...", label_visibility="collapsed")
        with c2:
            order = st.selectbox("", ["A → Z", "Z → A"], label_visibility="collapsed")

        filtered = [d for d in departments if search.lower() in d.lower()]
        filtered.sort(reverse=(order == "Z → A"))
        display_list = filtered if st.session_state.show_all else filtered[:5]

        selected = []
        for dep in display_list:
            key = f"dep_{dep}"
            if st.checkbox(dep.capitalize(), key=key):
                selected.append(dep)

        if len(filtered) > 5:
            if st.button("........", key="toggle_list"):
                st.session_state.show_all = not st.session_state.show_all
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        _, mid, _ = st.columns([1, 2, 1])
        with mid:
            submit = st.button("Submit", key="submit_departments", type="primary", use_container_width=True)

        if submit:
            st.session_state.submitted_departments = selected.copy()
            st.session_state.show_bundle = True

    # ================= RIGHT PANEL =================
    with right:
        st.markdown('<div class="bundle-title">Bundle Recommendation</div>', unsafe_allow_html=True)
        st.markdown('<div class="bundle-anchor"></div>', unsafe_allow_html=True)

        selected = st.session_state.submitted_departments

        if st.session_state.show_bundle and selected:
            name_to_id = dict(
                zip(
                    dept_lookup["department"].astype(str).str.strip().str.lower(),
                    dept_lookup["department_id"].astype(int),
                )
            )
            selected_ids = [name_to_id.get(d.strip().lower()) for d in selected]
            selected_ids = [int(x) for x in selected_ids if x is not None]

            if not selected_ids:
                st.warning("Could not map selected departments to IDs.")
                return

            basket_ids = generate_basket_for_departments(
                selected_department_ids=selected_ids,
                rules_df=rules_df,
                products_df=products_df,
                basket_size=8,
                min_lift=1.01,
                min_conf=0.0,
            )

            if not basket_ids:
                st.warning("No basket found from rules.")
                return

            id_to_name = dict(zip(products_df["product_id"], products_df["product_name"]))
            basket_items = [id_to_name.get(pid, f"Product {pid}") for pid in basket_ids]

            bundle = ["Selected Departments"] + basket_items

            html = '<div class="bundle-row">'
            for i, item in enumerate(bundle):
                card_class = "bundle-card"
                if i == 0:
                    card_class += " bundle-dept"
                elif i == 1:
                    card_class += " best-item"
                html += f'<div class="{card_class}">{item}</div>'
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)

        else:
            st.info("Select department(s) and click Submit")