import streamlit as st

# This is the home page with a hero section and navigation cards to other pages
def render_home():
    # HERO SECTION
    st.markdown("""
    <div class="hero">
        <div class="hero-content">
            <h1>Turn raw grocery data into actionable insights</h1>
            <p>This web application transforms raw grocery transaction data into interactive analytical insights. By examining product associations, bundle lift scores, department performance, and top-selling trends, the system reveals meaningful patterns in consumer purchasing behavior. The goal is to demonstrate how data mining techniques can support smarter retail decisions through practical, real-world analytics.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Navigation cards to other pages
    col1, col2 = st.columns(2)
    # Navigation card 1 - Departments
    with col1:
        st.markdown("""
        <a href="?page=DEPARTMENTS" class="card-link">
            <div class="card-box">
                <img src="https://cdn-icons-png.flaticon.com/512/2921/2921822.png" width="120"/>
                <h3>Departments</h3>
                <p>Analyze customer behavior by department</p>
            </div>
        </a>
        """, unsafe_allow_html=True)
    # Navigation card 2 - Aisle
    with col2:
        st.markdown("""
        <a href="?page=AISLE" class="card-link">
            <div class="card-box">
                <img src="https://cdn-icons-png.flaticon.com/512/3081/3081559.png" width="120"/>
                <h3>Aisle</h3>
                <p>Explore product performance by aisle</p>
            </div>
        </a>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Navigation card 3 - Dashboard (full width)

    st.markdown("""
    <a href="?page=DASHBOARD" class="card-link">
        <div class="card-box dashboard-wide">
            <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRu-gALsAaxPAv3KTAdtYBsVhqQr1DNq-Cbzg&s" width="80"/>
            <h3>Dashboard</h3>
            <p>Explore interactive charts and business insights</p>
        </div>
    </a>
    """, unsafe_allow_html=True)




