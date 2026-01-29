"""
Dashboard Principal - Pagină detaliată
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

from auth import require_auth, show_user_info

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# Verifică autentificarea
require_auth()
show_user_info()

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.title("📊 Dashboard Principal")
st.markdown("Vedere de ansamblu asupra sectorului automotive din Regiunea Vest")

# Filtre
col_filter1, col_filter2, col_filter3 = st.columns(3)

with col_filter1:
    selected_year = st.selectbox("An", range(2023, 2009, -1))

with col_filter2:
    selected_indicator = st.selectbox(
        "Indicator principal",
        ["Angajați", "Cifră de Afaceri", "Export", "Productivitate"]
    )

with col_filter3:
    comparison_type = st.selectbox(
        "Comparație",
        ["Pe județe", "Evoluție temporală", "Vs. media națională"]
    )

st.markdown("---")

# KPIs
st.subheader("Indicatori Cheie")

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

# Sample data - în producție vine de la API
kpi_data = {
    2023: {"employees": 60550, "turnover": 11.2, "exports": 8.9, "productivity": 185},
    2022: {"employees": 57200, "turnover": 10.5, "exports": 8.4, "productivity": 183}
}

current = kpi_data[selected_year] if selected_year in kpi_data else kpi_data[2023]
previous = kpi_data.get(selected_year - 1, kpi_data[2022])

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

st.markdown("---")

# Main charts
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Evoluție Sector (2015-2023)")

    years = list(range(2015, 2024))
    employees = [42000, 44500, 47200, 49800, 52000, 49650, 53150, 57200, 60550]
    turnover = [5.8, 6.2, 6.9, 7.5, 8.5, 7.8, 9.2, 10.5, 11.2]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=years,
        y=employees,
        name="Angajați",
        yaxis="y",
        line=dict(color="#1E3A5F", width=2)
    ))

    fig.add_trace(go.Scatter(
        x=years,
        y=turnover,
        name="CA (mld EUR)",
        yaxis="y2",
        line=dict(color="#E63946", width=2, dash="dash")
    ))

    fig.update_layout(
        xaxis=dict(title="An"),
        yaxis=dict(title="Angajați", side="left", showgrid=False),
        yaxis2=dict(title="CA (mld EUR)", side="right", overlaying="y", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=400,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

with chart_col2:
    st.subheader("Structura pe Subsectoare")

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
        color_continuous_scale="Blues"
    )

    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# Comparison by county
st.subheader("Comparație pe Județe")

county_comparison = pd.DataFrame({
    "Județ": ["Timiș", "Arad", "Hunedoara", "Caraș-Severin"],
    "Angajați": [33200, 21500, 4600, 1250],
    "Nr. Firme": [245, 142, 48, 13],
    "CA (mil EUR)": [6474, 3870, 759, 175],
    "Productivitate": [195, 180, 165, 140],
    "Pondere Regiune": ["54.8%", "35.5%", "7.6%", "2.1%"]
})

# Bar chart
fig3 = px.bar(
    county_comparison,
    x="Județ",
    y="Angajați",
    color="Productivitate",
    color_continuous_scale="RdYlGn",
    text="Pondere Regiune"
)

fig3.update_traces(textposition="outside")
fig3.update_layout(height=350)

col_table, col_chart = st.columns([1, 2])

with col_table:
    st.dataframe(county_comparison, hide_index=True, use_container_width=True)

with col_chart:
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# Alerts & Insights
st.subheader("Alerte și Insight-uri")

alert_col1, alert_col2, alert_col3 = st.columns(3)

with alert_col1:
    st.info("""
    **📈 Trend Pozitiv**

    Numărul de angajați a crescut cu 5.4% față de anul anterior,
    depășind media națională de 3.2%.
    """)

with alert_col2:
    st.warning("""
    **⚠️ Atenție**

    Productivitatea în Caraș-Severin este cu 24%
    sub media regională. Se recomandă analiză detaliată.
    """)

with alert_col3:
    st.success("""
    **✅ Performanță**

    Regiunea Vest contribuie cu 28% la exporturile
    automotive naționale, în creștere de la 25%.
    """)
