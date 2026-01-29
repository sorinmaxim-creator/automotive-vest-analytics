"""
Streamlit Main Application
Automotive Vest Analytics Dashboard
"""

import streamlit as st
import os
import sys
# Add current directory to path
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import autentificare
from auth import require_auth, show_user_info, is_authenticated, get_current_user

# Page configuration - trebuie să fie primul lucru
st.set_page_config(
    page_title="Automotive Vest Analytics",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verifică autentificarea
require_auth()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A5F;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1E3A5F;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# API URL & Environment
API_URL = os.getenv("API_URL", "http://localhost:8000")
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

# Info utilizator în sidebar
show_user_info()

# Sidebar
with st.sidebar:
    st.markdown("## 🚗 Automotive Vest")
    st.markdown("---")

    st.markdown("### 📊 Navigare")
    st.markdown("""
    - 📊 Dashboard
    - 📈 Comparații
    - 🗺️ Hărți
    - 📉 Tendințe
    - 📄 Rapoarte
    - 💰 Salarii
    - 👷 Piața Muncii
    - 🏭 Industrie
    """)
    st.markdown("---")

    # Filtre globale
    st.markdown("### 🔧 Filtre")
    selected_year = st.selectbox(
        "Selectează anul",
        options=list(range(2025, 2022, -1)),
        index=0
    )

    selected_counties = st.multiselect(
        "Selectează județele",
        options=["Timiș", "Arad", "Hunedoara", "Caraș-Severin"],
        default=["Timiș", "Arad", "Hunedoara", "Caraș-Severin"]
    )

    st.markdown("---")
    st.markdown("#### ℹ️ Despre")
    st.markdown("""
    Aplicație de analiză a sectorului
    automotive din Regiunea Vest.

    **Versiune:** 1.0.0
    """)

# Main content
st.markdown('<p class="main-header">🚗 Automotive Vest Analytics</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Monitorizare și analiză sector automotive - Regiunea Vest</p>', unsafe_allow_html=True)

# Salut utilizator
user = get_current_user()
if user:
    st.success(f"👋 Bine ai venit, **{user['name']}**!")

# KPI Row
st.markdown("### 📊 Indicatori Cheie (KPIs)")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Total Angajați",
        value="60,550",
        delta="+5.4%",
        delta_color="normal"
    )

with col2:
    st.metric(
        label="Cifră de Afaceri",
        value="€11.2 mld",
        delta="+6.7%",
        delta_color="normal"
    )

with col3:
    st.metric(
        label="Export",
        value="€8.9 mld",
        delta="+4.2%",
        delta_color="normal"
    )

with col4:
    st.metric(
        label="Productivitate",
        value="€185k/ang",
        delta="+3.1%",
        delta_color="normal"
    )

with col5:
    st.metric(
        label="Nr. Firme",
        value="448",
        delta="+23",
        delta_color="normal"
    )

st.markdown("---")

# Charts Row
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("### 📈 Evoluție Angajați (2019-2023)")

    import plotly.graph_objects as go

    years = [2019, 2020, 2021, 2022, 2023]
    employees = [52000, 49650, 53150, 57200, 60550]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years,
        y=employees,
        mode='lines+markers',
        name='Total Angajați',
        line=dict(color='#1E3A5F', width=3),
        marker=dict(size=8)
    ))

    fig.update_layout(
        xaxis_title="An",
        yaxis_title="Număr Angajați",
        hovermode='x unified',
        height=350,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)

with col_chart2:
    st.markdown("### 🥧 Distribuție pe Județe (2023)")

    import plotly.express as px

    county_data = {
        'Județ': ['Timiș', 'Arad', 'Hunedoara', 'Caraș-Severin'],
        'Angajați': [33200, 21500, 4600, 1250]
    }

    fig2 = px.pie(
        county_data,
        values='Angajați',
        names='Județ',
        color_discrete_sequence=['#1E3A5F', '#2E5A8F', '#4E7ABF', '#7E9ACF']
    )

    fig2.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Second Row of Charts
col_chart3, col_chart4 = st.columns(2)

with col_chart3:
    st.markdown("### 💰 Cifră de Afaceri vs Export")

    years = [2019, 2020, 2021, 2022, 2023]
    turnover = [8.5, 7.8, 9.2, 10.5, 11.2]
    exports = [6.8, 6.1, 7.4, 8.4, 8.9]

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=years,
        y=turnover,
        name='Cifră de Afaceri',
        marker_color='#1E3A5F'
    ))
    fig3.add_trace(go.Bar(
        x=years,
        y=exports,
        name='Export',
        marker_color='#4E7ABF'
    ))

    fig3.update_layout(
        barmode='group',
        xaxis_title="An",
        yaxis_title="Miliarde EUR",
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig3, use_container_width=True)

with col_chart4:
    st.markdown("### 📊 Comparație Județe - Productivitate")

    counties = ['Timiș', 'Arad', 'Hunedoara', 'Caraș-Severin']
    productivity = [195, 180, 165, 140]
    avg_productivity = 185

    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=counties,
        y=productivity,
        marker_color=['#1E3A5F', '#2E5A8F', '#4E7ABF', '#7E9ACF']
    ))

    # Add average line
    fig4.add_hline(
        y=avg_productivity,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Media regională: €{avg_productivity}k"
    )

    fig4.update_layout(
        xaxis_title="Județ",
        yaxis_title="€ mii / angajat",
        height=350,
        margin=dict(l=20, r=20, t=20, b=20)
    )

    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# Table with latest data
st.markdown("### 📋 Date Detaliate per Județ (2023)")

import pandas as pd

table_data = pd.DataFrame({
    'Județ': ['Timiș', 'Arad', 'Hunedoara', 'Caraș-Severin', 'TOTAL REGIUNE'],
    'Nr. Firme': [245, 142, 48, 13, 448],
    'Angajați': ['33,200', '21,500', '4,600', '1,250', '60,550'],
    'CA (mil. EUR)': ['6,474', '3,870', '759', '175', '11,278'],
    'Export (mil. EUR)': ['5,179', '3,096', '531', '122', '8,928'],
    'Productivitate (€k/ang)': [195, 180, 165, 140, 185],
    'Vs. Media': ['+5.4%', '-2.7%', '-10.8%', '-24.3%', '-']
})

st.dataframe(
    table_data,
    use_container_width=True,
    hide_index=True
)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    Automotive Vest Analytics v1.0.0 | Date: INS, Eurostat, ADR Vest |
    Ultima actualizare: Ianuarie 2025
</div>
""", unsafe_allow_html=True)
