import streamlit as st
import pandas as pd

# Session state initialization for Aisle page
def init_aisle_state():
    defaults = {
        "aisle_show_all": False,
        "submitted_aisles": [],
        "show_aisle_bundle": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# Render function for Aisle page
def render_aisle():

    init_aisle_state()

    df = pd.read_csv("data/aisles.csv")
    aisles = df["aisle"].dropna().astype(str).tolist()

    left, right = st.columns([1, 1.2], gap="large")

    # Left panel for aisle selection
    with left:
        # Title and anchor for styling
        st.markdown('<div class="department-aisle-title">List of Aisles</div>', unsafe_allow_html=True)
        st.markdown('<div class="department-aisle-anchor"></div>', unsafe_allow_html=True)
        # Search and sorting controls
        c1, c2 = st.columns([3,1])
        with c1:
            search = st.text_input("", placeholder="Search ...", label_visibility="collapsed", key="aisle_search")
        with c2:
            order = st.selectbox("", ["A → Z", "Z → A"], label_visibility="collapsed", key="aisle_sort")
        # Filter aisle list based on search and sort order
        filtered = [a for a in aisles if search.lower() in a.lower()]
        filtered.sort(reverse=(order == "Z → A"))
        # Show only first 5 unless expanded
        display_list = filtered if st.session_state.aisle_show_all else filtered[:5]

        selected = []
        # Checkbox list for aisles
        for aisle in display_list:
            key = f"aisle_{aisle}"
            if st.checkbox(aisle.capitalize(), key=key):
                selected.append(aisle)
        # Toggle full list if more than 5 aisles
        if len(filtered) > 5:
            if st.button("........", key="toggle_aisle_list"):
                st.session_state.aisle_show_all = not st.session_state.aisle_show_all
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        # Submit button to trigger bundle recommendations
        btn_col1, btn_col2, btn_col3 = st.columns([1,2,1])
        with btn_col2:
            submit = st.button(
                "Submit",
                key="submit_aisles",
                type="primary",
                use_container_width=True
            )

        if submit:
            st.session_state.submitted_aisles = selected.copy()
            st.session_state.show_aisle_bundle = True

    # Right panel for bundle recommendations based on selected aisles
    with right:
        # Bundle recommendation title and anchor for styling
        st.markdown('<div class="bundle-title">Bundle Recommendation</div>', unsafe_allow_html=True)
        st.markdown('<div class="bundle-anchor"></div>', unsafe_allow_html=True)
        # Show bundle recommendations if aisles are selected and submitted
        if st.session_state.show_aisle_bundle and st.session_state.submitted_aisles:
            # Load bundle recommendations data
            bundle_df = pd.read_csv("data/bundle_top10_by_aisle.csv")
            # Get selected aisles from session state
            selected = st.session_state.submitted_aisles
            # Loop through selected aisles and display their bundle recommendations
            for aisle in selected:

                aisle_key = aisle.strip().lower()

                aisle_bundle = (
                    bundle_df[bundle_df["aisle"].str.lower() == aisle_key]
                    .sort_values("lift", ascending=False)
                    .head(6)
                )
                # If no bundles found for the aisle, show info message and skip to next
                if aisle_bundle.empty:
                    st.info(f"No bundle recommendations found for {aisle.title()}. Explore top-selling products below.")
                    continue
                    # If bundles found, display them in a styled format
                st.markdown(
                    f"""
                    <div class="dept-bundle-title">
                        Bundles we found for <strong>{aisle.title()}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                # Create two columns for bundle display
                col1, col2 = st.columns(2, gap="large")

                for i, (_, row) in enumerate(aisle_bundle.iterrows()):

                    html = '<div class="bundle-row">'
                    html += f'<div class="bundle-card">{row["product_name_base"]}</div>'
                    html += f'''
                        <div class="bundle-card best-item">
                            <span class="best-badge"></span>
                            {row["product_name_recommended"]}
                        </div>
                    '''
                    html += '</div>'
                    # Alternate rows between the two columns
                    if i < 3:
                        col1.markdown(html, unsafe_allow_html=True)
                    else:
                        col2.markdown(html, unsafe_allow_html=True)

        else:
            st.info("Select aisle(s) and click Submit")

    # Top products section (only shows after bundle recommendations are triggered)
    if st.session_state.show_aisle_bundle and st.session_state.submitted_aisles:
        # Load top products data for aisles
        product_df = pd.read_csv("data/top5_selling_by_aisle.csv")
        selected = st.session_state.submitted_aisles

        html_output = """
        <div class="top-wrapper-main">
            <div class="top-title-main">Top 5 Best-Selling Products</div>
            <div class="top-subtitle">Based on your selected aisles</div>
        """
        # Loop through selected aisles and append their top products to the HTML
        for aisle in selected:

            aisle_products = (
                product_df[product_df["aisle"].str.lower() == aisle]
                .sort_values("total_orders", ascending=False)
                .head(5)
            )
            # If no products found for the aisle, skip to next
            if aisle_products.empty:
                continue

            html_output += f"<div class='dept-header'>Bestsellers in {aisle.capitalize()}</div>"
            html_output += '<div class="product-row">'
            # Loop through top products for the aisle and create product cards, marking the top one as bestseller
            for i, (_, row) in enumerate(aisle_products.iterrows()):
                badge = '<span class="badge-bestseller">🔥 Bestseller</span>' if i == 0 else ''
                html_output += f'<div class="card-unit">{badge}<div class="bundle-card">{row["product_name"]}</div></div>'

            html_output += '</div>'

        html_output += "</div>"

        st.markdown(html_output.replace('\n', ''), unsafe_allow_html=True)


