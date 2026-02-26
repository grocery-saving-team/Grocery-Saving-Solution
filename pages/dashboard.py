import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

# Render function for Dashboard page
def render_dashboard():
    # Dashboard title
    st.markdown(
    """
    <h1 class="dashboard-title">
        📊 Customer Segmentation Dashboard
    </h1>
    """,
    unsafe_allow_html=True
)
    # Path to pre-generated charts
    charts_path = Path("charts")

    # Dashboard layout with 2 rows and 2 columns each
    col1, col2 = st.columns(2)
    # Render charts in Row 1
    with col1:
        with open(charts_path / "busiest_hours.html", "r", encoding="utf-8") as f:
            components.html(f.read(), height=500)
    # Render second chart in Row 1
    with col2:
        with open(charts_path / "busiest_days.html", "r", encoding="utf-8") as f:
            components.html(f.read(), height=500)

    # Render charts in Row 2
    col3, col4 = st.columns(2)
    # Render first chart in Row 2
    with col3:
        with open(charts_path / "orders_per_cluster.html", "r", encoding="utf-8") as f:
            components.html(f.read(), height=650)
    # Render second chart in Row 2
    with col4:
        with open(charts_path / "cluster_department_profiles.html", "r", encoding="utf-8") as f:
            components.html(f.read(), height=650)