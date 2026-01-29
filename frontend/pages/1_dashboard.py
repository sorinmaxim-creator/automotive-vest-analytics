"""
Dashboard Principal - Pagină detaliată
Design modern și profesionist
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests
import os
import sys
if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import require_auth
from styles import (
    init_page_style, page_header, section_header, chart_container,
    chart_container_end, COLORS, get_plotly_layout_defaults, alert_box
)

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# Verifică autentificarea
require_auth()

# Aplică stilurile moderne
init_page_style(st)

API_URL = os.getenv("API_URL", "http://localhost:8000")

# Header pagină
st.markdown(page_header(
    "Dashboard Principal",
    "Vedere de ansamblu asupra sectorului automotive din Regiunea Vest",
    "📊"
), unsafe_allow_html=True)

# Filtre în sidebar
with st.sidebar:
    st.markdown("""
    <div class="menu-group">
        <div class="menu-group-title">🔧 Filtre Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    selected_year = st.selectbox(
        "📅 An",
        range(2023, 2009, -1),
        key="dashboard_year"
    )

    selected_indicator = st.selectbox(
        "📊 Indicator principal",
        ["Angajați", "Cifră de Afaceri", "Export", "Productivitate"],
        key="dashboard_indicator"
    )

    comparison_type = st.selectbox(
        "🔄 Comparație",
        ["Pe județe", "Evoluție temporală", "Vs. media națională"],
        key="dashboard_comparison"
    )

# KPIs Section
st.markdown(section_header("Indicatori Cheie", "📊"), unsafe_allow_html=True)

# Sample data - în producție vine de la API
kpi_data = {
    2023: {"employees": 60550, "turnover": 11.2, "exports": 8.9, "productivity": 185},
    2022: {"employees": 57200, "turnover": 10.5, "exports": 8.4, "productivity": 183}
}

current = kpi_data[selected_year] if selected_year in kpi_data else kpi_data[2023]
previous = kpi_data.get(selected_year - 1, kpi_data[2022])

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    delta = ((current["employees"] - previous["employees"]) / previous["employees"]) * 100
    st.metric(
        "Total Angajați",
        f"{current['employees']:,}",
        f"{delta:+.1f}%"
    )

with kpi_col2:
    delta = ((current["turnover"] - previous["turnover"]) / previous["turnover"]) * 100
    st.metric(
        "Cifră de Afaceri",
        f"€{current['turnover']} mld",
        f"{delta:+.1f}%"
    )

with kpi_col3:
    delta = ((current["exports"] - previous["exports"]) / previous["exports"]) * 100
    st.metric(
        "Export Total",
        f"€{current['exports']} mld",
        f"{delta:+.1f}%"
    )

with kpi_col4:
    delta = ((current["productivity"] - previous["productivity"]) / previous["productivity"]) * 100
    st.metric(
        "Productivitate",
        f"€{current['productivity']}k/ang",
        f"{delta:+.1f}%"
    )

st.markdown("<br>", unsafe_allow_html=True)

# Main charts
st.markdown(section_header("Evoluție și Structură", "📈"), unsafe_allow_html=True)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown(chart_container("Evoluție Sector (2015-2023)", "📈"), unsafe_allow_html=True)

    years = list(range(2015, 2024))
    employees = [42000, 44500, 47200, 49800, 52000, 49650, 53150, 57200, 60550]
    turnover = [5.8, 6.2, 6.9, 7.5, 8.5, 7.8, 9.2, 10.5, 11.2]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=years,
        y=employees,
        name="Angajați",
        yaxis="y",
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(size=8)
    ))

    fig.add_trace(go.Scatter(
        x=years,
        y=turnover,
        name="CA (mld EUR)",
        yaxis="y2",
        line=dict(color=COLORS['accent'], width=3, dash="dash"),
        marker=dict(size=8)
    ))

    layout_defaults = get_plotly_layout_defaults()
    fig.update_layout(
        xaxis=dict(title="An", gridcolor='#e2e8f0'),
        yaxis=dict(title="Angajați", side="left", showgrid=False, color=COLORS['primary']),
        yaxis2=dict(title="CA (mld EUR)", side="right", overlaying="y", showgrid=False, color=COLORS['accent']),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
        hovermode="x unified",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif"),
        margin=dict(l=20, r=20, t=20, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown(chart_container_end(), unsafe_allow_html=True)

with chart_col2:
    st.markdown(chart_container("Structura pe Subsectoare", "🏭"), unsafe_allow_html=True)

    subsector_data = {
        "Subsector": ["Componente", "Asamblare", "Echipamente electrice", "R&D", "Altele"],
        "Angajați": [28000, 18000, 8500, 3500, 2550],
        "Pondere": [46.2, 29.7, 14.0, 5.8, 4.2]
    }

    fig2 = px.treemap(
        subsector_data,
        path=["Subsector"],
        values="Angajați",
        color="Pondere",
        color_continuous_scale=[[0, COLORS['primary_light']], [0.5, COLORS['primary']], [1, COLORS['secondary']]]
    )

    fig2.update_layout(
        height=380,
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif"),
        margin=dict(l=10, r=10, t=10, b=10),
        coloraxis_showscale=False
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown(chart_container_end(), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Comparison by county
st.markdown(section_header("Comparație pe Județe", "🗺️"), unsafe_allow_html=True)

county_comparison = pd.DataFrame({
    "Județ": ["Timiș", "Arad", "Hunedoara", "Caraș-Severin"],
    "Angajați": [33200, 21500, 4600, 1250],
    "Nr. Firme": [245, 142, 48, 13],
    "CA (mil EUR)": [6474, 3870, 759, 175],
    "Productivitate": [195, 180, 165, 140],
    "Pondere Regiune": ["54.8%", "35.5%", "7.6%", "2.1%"]
})

col_table, col_chart = st.columns([1, 2])

with col_table:
    st.dataframe(county_comparison, hide_index=True, use_container_width=True)

with col_chart:
    st.markdown(chart_container("Angajați și Productivitate per Județ", "📊"), unsafe_allow_html=True)

    # Bar chart
    avg_productivity = county_comparison["Productivitate"].mean()
    colors = [COLORS['primary'] if p >= avg_productivity else COLORS['accent'] for p in county_comparison["Productivitate"]]

    fig3 = go.Figure()

    fig3.add_trace(go.Bar(
        x=county_comparison["Județ"],
        y=county_comparison["Angajați"],
        marker_color=colors,
        text=county_comparison["Pondere Regiune"],
        textposition="outside"
    ))

    layout_defaults = get_plotly_layout_defaults()
    fig3.update_layout(
        xaxis_title="Județ",
        yaxis_title="Număr Angajați",
        height=320,
        **layout_defaults
    )

    st.plotly_chart(fig3, use_container_width=True)
    st.markdown(chart_container_end(), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Alerts & Insights
st.markdown(section_header("Alerte și Insight-uri", "💡"), unsafe_allow_html=True)

alert_col1, alert_col2, alert_col3 = st.columns(3)

with alert_col1:
    st.markdown(alert_box(
        """<strong>📈 Trend Pozitiv</strong><br><br>
        Numărul de angajați a crescut cu 5.4% față de anul anterior,
        depășind media națională de 3.2%.""",
        "info",
        None
    ), unsafe_allow_html=True)

with alert_col2:
    st.markdown(alert_box(
        """<strong>⚠️ Atenție</strong><br><br>
        Productivitatea în Caraș-Severin este cu 24%
        sub media regională. Se recomandă analiză detaliată.""",
        "warning",
        None
    ), unsafe_allow_html=True)

with alert_col3:
    st.markdown(alert_box(
        """<strong>✅ Performanță</strong><br><br>
        Regiunea Vest contribuie cu 28% la exporturile
        automotive naționale, în creștere de la 25%.""",
        "success",
        None
    ), unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div class="app-footer">
    <p style="margin: 0;">© 2025 Vest Policy Lab - Automotive Vest Analytics</p>
</div>
""", unsafe_allow_html=True)
