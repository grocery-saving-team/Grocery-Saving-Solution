import streamlit as st
import pandas as pd

#Session state initialization for Departments page
def init_dep_state():
    defaults = {
        "show_all": False,
        "submitted_departments": [],
        "show_bundle": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Render function for Departments page
def render_departments():
    init_dep_state()
    # Load department data
    df = pd.read_csv("data/departments.csv")
    # Extract department list
    departments = df["department"].dropna().astype(str).tolist()
    # Create two columns for layout
    left, right = st.columns([1, 1.2], gap="large")

    # Left panel for department selection
    with left:
        # Title and anchor for styling
        st.markdown('<div class="department-aisle-title">List of Department</div>', unsafe_allow_html=True)
        st.markdown('<div class="department-aisle-anchor"></div>', unsafe_allow_html=True)

        # Search and sorting controls
        c1, c2 = st.columns([3, 1])
        with c1:
            search = st.text_input("", placeholder="Search ...", label_visibility="collapsed")
        with c2:
            order = st.selectbox("", ["A → Z", "Z → A"], label_visibility="collapsed")

        #Filter department list
        filtered = [d for d in departments if search.lower() in d.lower()]
        filtered.sort(reverse=(order == "Z → A"))

        # Show only first 5 unless expanded 
        display_list = filtered if st.session_state.show_all else filtered[:5]

        selected = []

        # Checkbox list 
        for dep in display_list:
            key = f"dep_{dep}"
            checked = st.checkbox(dep.capitalize(), key=key)

            if checked:
                selected.append(dep)

        # Toggle full list 
        if len(filtered) > 5:
            if st.button("........", key="toggle_list"):
                st.session_state.show_all = not st.session_state.show_all
                st.rerun()

        # Submit button 
        st.markdown("<br>", unsafe_allow_html=True)

        btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])
        with btn_col2:
            submit = st.button(
                "Submit",
                key="submit_departments",
                type="primary",
                use_container_width=True
            )

        # Save selection ONLY when submit pressed
        if submit:
            st.session_state.submitted_departments = selected.copy()
            st.session_state.show_bundle = True

    # Right panel for bundle recommendations
    with right:
        # Title and anchor for styling
        st.markdown('<div class="bundle-title">Bundle Recommendation</div>', unsafe_allow_html=True)
        st.markdown('<div class="bundle-anchor"></div>', unsafe_allow_html=True)
        # Check if we should show bundle recommendations
        if st.session_state.show_bundle and st.session_state.submitted_departments:
            # Load bundle data
            bundle_df = pd.read_csv("data/bundle_top10_by_department.csv")
            selected = st.session_state.submitted_departments
            # Loop through selected departments and display bundles
            for dept in selected:

                dept_key = dept.strip().lower()

                dept_bundle_full = (
                    bundle_df[bundle_df["department"].str.lower() == dept_key]
                    .sort_values("lift", ascending=False)
                )
                # If no bundles found, show info message
                if dept_bundle_full.empty:
                    st.info(f"No bundle recommendations found for {dept.title()}. Explore top-selling products below.")
                    continue
                # Department header
                st.markdown(
                    f"""
                    <div class="dept-bundle-title">
                        Bundles we found for <strong>{dept.title()}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Toggle key for this department's bundle list
                toggle_key = f"show_all_{dept_key}"

                if toggle_key not in st.session_state:
                    st.session_state[toggle_key] = False

                # Show first 6 or full list
                if not st.session_state[toggle_key]:
                    dept_bundle = dept_bundle_full.head(6)
                else:
                    dept_bundle = dept_bundle_full

                # Render bundle recommendations in two columns
                col1, col2 = st.columns(2, gap="large")

                for i, (_, row) in enumerate(dept_bundle.iterrows()):

                    html = '<div class="bundle-row">'

                    # Base product
                    html += f'<div class="bundle-card">{row["product_name_base"]}</div>'

                    # Recommended product
                    html += f'''
                        <div class="bundle-card best-item">
                            <span class="best-badge"></span>
                            {row["product_name_recommended"]}
                        </div>
                    '''

                    html += '</div>'

                    # Alternate between columns (3-3 layout)
                    if i % 6 < 3:
                        col1.markdown(html, unsafe_allow_html=True)
                    else:
                        col2.markdown(html, unsafe_allow_html=True)

                # Show toggle button if more than 6 bundles
                
                if not st.session_state[toggle_key] and len(dept_bundle_full) > 6:

                    # Use unique keys for each button to avoid conflicts
                    if st.button(f"🔽", key=f"btn_more_{dept_key}"):
                        st.session_state[toggle_key] = True
                        st.rerun()
                    
                # If already showing full list, offer option to collapse back
                elif st.session_state[toggle_key]:

                    # Use unique keys for each button to avoid conflicts
                    if st.button(f"🔼", key=f"btn_less_{dept_key}"):
                        st.session_state[toggle_key] = False
                        st.rerun()
                
        else:
            st.info("Select department(s) and click Submit")
    # Top products section (only shows after bundle recommendations are triggered)
    if st.session_state.show_bundle and st.session_state.submitted_departments:
        # Load top products data
        product_df = pd.read_csv("data/top5_selling_by_department.csv")
        selected = st.session_state.submitted_departments

        # Build entire HTML for top products section in one go to avoid Streamlit's multiple render issues
        html_output = f"""
        <div class="top-wrapper-main">
            <div class="top-title-main">Top 5 Best-Selling Products</div>
            <div class="top-subtitle">Based on your selected departments</div>
        """
        # Loop through selected departments and append their top products to the HTML
        for dept in selected:
            dept_products = product_df[product_df["department"].str.lower() == dept].sort_values("total_orders", ascending=False).head(5)
            if dept_products.empty: continue
            # Department header
            html_output += f"<div class='dept-header'>Bestsellers in {dept.capitalize()}</div>"
            
            # Product cards row
            html_output += '<div class="product-row">'
            
            for i, (_, row) in enumerate(dept_products.iterrows()):
                badge = '<span class="badge-bestseller ">🔥 Bestseller</span>' if i == 0 else ''
                
                html_output += f'<div class="card-unit">{badge}<div class="bundle-card">{row["product_name"]}</div></div>'
                
            html_output += '</div>' 

        html_output += "</div>" 

        # Render the entire section at once to ensure styles are applied correctly
        st.markdown(html_output.replace('\n', ''), unsafe_allow_html=True)


