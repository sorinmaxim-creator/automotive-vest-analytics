"""
Streamlit Main Application
Automotive Vest Analytics Dashboard
Design modern și profesionist
"""

import streamlit as st
import os
import sys
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Add current directory to path
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import autentificare și stiluri
from auth import require_auth, show_user_info, is_authenticated, get_current_user
from styles import get_main_css, get_sidebar_css, page_header, section_header, COLORS

# Page configuration - trebuie să fie primul lucru
st.set_page_config(
    page_title="Automotive Vest Analytics",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verifică autentificarea
require_auth()

# Aplică stilurile CSS globale
st.markdown(get_main_css(), unsafe_allow_html=True)
st.markdown(get_sidebar_css(), unsafe_allow_html=True)

# API URL & Environment
API_URL = os.getenv("API_URL", "http://localhost:8000")
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

# Sidebar cu design modern
with st.sidebar:
    # Logo și titlu
    st.markdown("""
    <div class="logo-container">
        <p class="logo-text">🚗 Automotive Vest</p>
        <p class="logo-subtitle">Analytics Platform</p>
    </div>
    """, unsafe_allow_html=True)

    # Info utilizator
    user = get_current_user()
    if user:
        st.markdown(f"""
        <div class="user-info">
            <div class="user-info-name">👤 {user['name']}</div>
            <div class="user-info-role">{user['role']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Grupuri de meniuri
    st.markdown("""
    <div class="menu-group">
        <div class="menu-group-title">📊 Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    <div class="menu-group">
        <div class="menu-group-title">🔧 Filtre Globale</div>
    </div>
    """, unsafe_allow_html=True)

    # Filtre globale
    selected_year = st.selectbox(
        "📅 An",
        options=list(range(2025, 2019, -1)),
        index=0,
        key="global_year_filter"
    )

    selected_counties = st.multiselect(
        "🗺️ Județe",
        options=["Timiș", "Arad", "Hunedoara", "Caraș-Severin"],
        default=["Timiș", "Arad", "Hunedoara", "Caraș-Severin"],
        key="global_county_filter"
    )

    st.markdown("---")

    # Buton deconectare
    if st.button("🚪 Deconectare", use_container_width=True, key="main_logout_btn"):
        from auth import logout
        logout()
        st.rerun()

    st.markdown("---")

    # Info versiune
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <p style="color: rgba(255,255,255,0.5); font-size: 0.75rem; margin: 0;">
            Versiune 1.0.0<br>
            © 2025 Vest Policy Lab
        </p>
    </div>
    """, unsafe_allow_html=True)

# Main content - Header
st.markdown(page_header(
    "Dashboard Principal",
    "Monitorizare și analiză sector automotive - Regiunea Vest",
    "🚗"
), unsafe_allow_html=True)

# Mesaj de bun venit
user = get_current_user()
if user:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {COLORS['success']}20 0%, {COLORS['success']}10 100%);
                padding: 1rem 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;
                border-left: 4px solid {COLORS['success']};">
        <span style="font-size: 1.1rem;">👋 Bine ai venit, <strong>{user['name']}</strong>!</span>
    </div>
    """, unsafe_allow_html=True)

# KPI Section
st.markdown(section_header("Indicatori Cheie (KPIs)", "📊"), unsafe_allow_html=True)

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

st.markdown("<br>", unsafe_allow_html=True)

# Charts Row 1
st.markdown(section_header("Evoluție și Distribuție", "📈"), unsafe_allow_html=True)

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("""
    <div class="chart-container">
        <h4 style="margin: 0 0 1rem 0; color: #1a365d;">📈 Evoluție Angajați (2019-2023)</h4>
    """, unsafe_allow_html=True)

    years = [2019, 2020, 2021, 2022, 2023]
    employees = [52000, 49650, 53150, 57200, 60550]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years,
        y=employees,
        mode='lines+markers',
        name='Total Angajați',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=10, color=COLORS['primary']),
        fill='tozeroy',
        fillcolor=f"rgba(26, 54, 93, 0.1)"
    ))

    fig.update_layout(
        xaxis_title="An",
        yaxis_title="Număr Angajați",
        hovermode='x unified',
        height=320,
        margin=dict(l=20, r=20, t=10, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif"),
        xaxis=dict(gridcolor='#e2e8f0'),
        yaxis=dict(gridcolor='#e2e8f0')
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_chart2:
    st.markdown("""
    <div class="chart-container">
        <h4 style="margin: 0 0 1rem 0; color: #1a365d;">🥧 Distribuție pe Județe (2023)</h4>
    """, unsafe_allow_html=True)

    county_data = {
        'Județ': ['Timiș', 'Arad', 'Hunedoara', 'Caraș-Severin'],
        'Angajați': [33200, 21500, 4600, 1250]
    }

    fig2 = px.pie(
        county_data,
        values='Angajați',
        names='Județ',
        color_discrete_sequence=[COLORS['primary'], COLORS['primary_light'], COLORS['secondary'], COLORS['accent']]
    )

    fig2.update_layout(
        height=320,
        margin=dict(l=20, r=20, t=10, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
    )

    fig2.update_traces(textposition='inside', textinfo='percent+label')

    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Charts Row 2
st.markdown(section_header("Performanță Financiară", "💰"), unsafe_allow_html=True)

col_chart3, col_chart4 = st.columns(2)

with col_chart3:
    st.markdown("""
    <div class="chart-container">
        <h4 style="margin: 0 0 1rem 0; color: #1a365d;">💰 Cifră de Afaceri vs Export</h4>
    """, unsafe_allow_html=True)

    years = [2019, 2020, 2021, 2022, 2023]
    turnover = [8.5, 7.8, 9.2, 10.5, 11.2]
    exports = [6.8, 6.1, 7.4, 8.4, 8.9]

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=years,
        y=turnover,
        name='Cifră de Afaceri',
        marker_color=COLORS['primary'],
        marker_line_width=0
    ))
    fig3.add_trace(go.Bar(
        x=years,
        y=exports,
        name='Export',
        marker_color=COLORS['secondary'],
        marker_line_width=0
    ))

    fig3.update_layout(
        barmode='group',
        xaxis_title="An",
        yaxis_title="Miliarde EUR",
        height=320,
        margin=dict(l=20, r=20, t=10, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif"),
        xaxis=dict(gridcolor='#e2e8f0'),
        yaxis=dict(gridcolor='#e2e8f0'),
        bargap=0.15,
        bargroupgap=0.1
    )

    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_chart4:
    st.markdown("""
    <div class="chart-container">
        <h4 style="margin: 0 0 1rem 0; color: #1a365d;">📊 Comparație Județe - Productivitate</h4>
    """, unsafe_allow_html=True)

    counties = ['Timiș', 'Arad', 'Hunedoara', 'Caraș-Severin']
    productivity = [195, 180, 165, 140]
    avg_productivity = 185

    colors = [COLORS['primary'] if p >= avg_productivity else COLORS['accent'] for p in productivity]

    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=counties,
        y=productivity,
        marker_color=colors,
        marker_line_width=0,
        text=[f"€{p}k" for p in productivity],
        textposition='outside'
    ))

    fig4.add_hline(
        y=avg_productivity,
        line_dash="dash",
        line_color=COLORS['error'],
        line_width=2,
        annotation_text=f"Media: €{avg_productivity}k",
        annotation_position="right"
    )

    fig4.update_layout(
        xaxis_title="Județ",
        yaxis_title="€ mii / angajat",
        height=320,
        margin=dict(l=20, r=20, t=10, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif"),
        xaxis=dict(gridcolor='#e2e8f0'),
        yaxis=dict(gridcolor='#e2e8f0', range=[0, 220])
    )

    st.plotly_chart(fig4, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Table with latest data
st.markdown(section_header("Date Detaliate per Județ (2023)", "📋"), unsafe_allow_html=True)

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
    hide_index=True,
    column_config={
        "Județ": st.column_config.TextColumn("Județ", width="medium"),
        "Nr. Firme": st.column_config.NumberColumn("Nr. Firme", format="%d"),
        "Angajați": st.column_config.TextColumn("Angajați"),
        "CA (mil. EUR)": st.column_config.TextColumn("CA (mil. EUR)"),
        "Export (mil. EUR)": st.column_config.TextColumn("Export (mil. EUR)"),
        "Productivitate (€k/ang)": st.column_config.NumberColumn("Productivitate", format="%d €k"),
        "Vs. Media": st.column_config.TextColumn("Vs. Media")
    }
)

# Footer
st.markdown(f"""
<div class="app-footer">
    <p style="margin: 0;">
        <strong>Automotive Vest Analytics</strong> v1.0.0 |
        Surse date: INS, Eurostat, ADR Vest |
        Ultima actualizare: Ianuarie 2025
    </p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.75rem;">
        © 2025 Vest Policy Lab - Toate drepturile rezervate
    </p>
</div>
""", unsafe_allow_html=True)
