import streamlit as st
import pandas as pd


def render_aisle():
    st.header("🛒 Aisle Page")

    # Load aisle data
    df = pd.read_csv("data/aisles.csv")
    aisles = df["aisle"].tolist()

    col1, col2 = st.columns([1, 1.2])

    # ================= LEFT PANEL =================
    with col1:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">List of Aisle</div>', unsafe_allow_html=True)

        selected = []
        for aisle in aisles:
            if st.checkbox(aisle.capitalize(), key=f"aisle_{aisle}"):
                selected.append(aisle)

        st.markdown("<br>", unsafe_allow_html=True)

        submit = st.button("Submit", key="submit_aisle", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ================= RIGHT PANEL =================
    with col2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Bundle Recommendation</div>', unsafe_allow_html=True)

        if submit and selected:
            st.success(f"Selected: {', '.join(selected)}")
        else:
            st.info("Select aisle(s) and click Submit")

        st.markdown('</div>', unsafe_allow_html=True)

