"""
Pagina Tendințe și Scenarii
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import os
import sys
if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import require_auth, show_user_info

st.set_page_config(page_title="Tendințe", page_icon="📉", layout="wide")

# Verifică autentificarea
require_auth()
show_user_info()

st.title("📉 Tendințe și Scenarii")
st.markdown("Analiză tendințe istorice și proiecții viitoare")

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Tendințe Istorice", "🔮 Proiecții", "🔗 Corelații"])

with tab1:
    st.subheader("Evoluție Indicatori Cheie (2010-2023)")

    # Selectare indicatori
    selected_indicators = st.multiselect(
        "Selectează indicatorii",
        ["Angajați", "Cifră de afaceri", "Export", "Productivitate", "Nr. Firme"],
        default=["Angajați", "Cifră de afaceri"]
    )

    # Date istorice simulate
    years = list(range(2010, 2024))

    historical_data = {
        "Angajați": [32000, 34500, 37200, 39800, 42000, 44500, 47200, 49800, 52000, 49650, 53150, 57200, 60550, 63000],
        "Cifră de afaceri": [3.8, 4.2, 4.7, 5.2, 5.8, 6.2, 6.9, 7.5, 8.5, 7.8, 9.2, 10.5, 11.2, 12.1],
        "Export": [3.0, 3.4, 3.8, 4.2, 4.6, 5.0, 5.5, 6.0, 6.8, 6.1, 7.4, 8.4, 8.9, 9.7],
        "Productivitate": [119, 122, 126, 131, 138, 139, 146, 151, 163, 157, 173, 183, 185, 192],
        "Nr. Firme": [280, 295, 310, 325, 340, 355, 365, 375, 385, 372, 398, 425, 448, 470]
    }

    # Grafic
    fig = go.Figure()

    colors = ["#1E3A5F", "#E63946", "#457B9D", "#2A9D8F", "#F4A261"]

    for i, indicator in enumerate(selected_indicators):
        if indicator in historical_data:
            fig.add_trace(go.Scatter(
                x=years,
                y=historical_data[indicator],
                name=indicator,
                mode="lines+markers",
                line=dict(color=colors[i % len(colors)], width=2)
            ))

    fig.update_layout(
        xaxis_title="An",
        yaxis_title="Valoare",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=450,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Statistici
    st.subheader("Statistici Descriptive")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("CAGR Angajați (2010-2023)", "+5.2%")
    with col2:
        st.metric("CAGR Cifră de Afaceri", "+9.4%")
    with col3:
        st.metric("CAGR Export", "+9.6%")
    with col4:
        st.metric("CAGR Productivitate", "+3.7%")

    # Tabel cu date
    if st.checkbox("Afișează date complete"):
        df = pd.DataFrame({"An": years})
        for indicator in selected_indicators:
            if indicator in historical_data:
                df[indicator] = historical_data[indicator]
        st.dataframe(df, hide_index=True, use_container_width=True)

with tab2:
    st.subheader("Scenarii de Evoluție (2024-2030)")

    scenario = st.radio(
        "Selectează scenariul",
        ["Optimist", "Bază", "Pesimist"],
        horizontal=True
    )

    indicator_forecast = st.selectbox(
        "Indicator pentru prognoză",
        ["Angajați", "Cifră de afaceri", "Export", "Productivitate"]
    )

    # Date istorice
    hist_years = list(range(2019, 2024))
    forecast_years = list(range(2024, 2031))
    all_years = hist_years + forecast_years

    # Valori istorice
    base_values = {
        "Angajați": [52000, 49650, 53150, 57200, 60550],
        "Cifră de afaceri": [8.5, 7.8, 9.2, 10.5, 11.2],
        "Export": [6.8, 6.1, 7.4, 8.4, 8.9],
        "Productivitate": [163, 157, 173, 183, 185]
    }

    historical = base_values[indicator_forecast]
    last_value = historical[-1]

    # Scenarii de creștere
    growth_rates = {
        "Optimist": {"Angajați": 0.06, "Cifră de afaceri": 0.08, "Export": 0.09, "Productivitate": 0.04},
        "Bază": {"Angajați": 0.03, "Cifră de afaceri": 0.05, "Export": 0.05, "Productivitate": 0.025},
        "Pesimist": {"Angajați": 0.00, "Cifră de afaceri": 0.02, "Export": 0.02, "Productivitate": 0.01}
    }

    # Calcul proiecții
    def project_values(start_value, growth_rate, years):
        values = []
        current = start_value
        for _ in years:
            current = current * (1 + growth_rate)
            values.append(round(current, 2))
        return values

    optimist_proj = project_values(last_value, growth_rates["Optimist"][indicator_forecast], forecast_years)
    base_proj = project_values(last_value, growth_rates["Bază"][indicator_forecast], forecast_years)
    pesimist_proj = project_values(last_value, growth_rates["Pesimist"][indicator_forecast], forecast_years)

    # Grafic
    fig = go.Figure()

    # Istoric
    fig.add_trace(go.Scatter(
        x=hist_years,
        y=historical,
        name="Date istorice",
        mode="lines+markers",
        line=dict(color="#1E3A5F", width=3)
    ))

    # Scenarii
    if scenario == "Optimist" or scenario == "Toate":
        fig.add_trace(go.Scatter(
            x=forecast_years,
            y=optimist_proj,
            name="Scenariu Optimist",
            mode="lines+markers",
            line=dict(color="#2A9D8F", width=2, dash="dash")
        ))

    if scenario == "Bază" or scenario == "Toate":
        fig.add_trace(go.Scatter(
            x=forecast_years,
            y=base_proj,
            name="Scenariu Bază",
            mode="lines+markers",
            line=dict(color="#F4A261", width=2, dash="dash")
        ))

    if scenario == "Pesimist" or scenario == "Toate":
        fig.add_trace(go.Scatter(
            x=forecast_years,
            y=pesimist_proj,
            name="Scenariu Pesimist",
            mode="lines+markers",
            line=dict(color="#E63946", width=2, dash="dash")
        ))

    # Zona de incertitudine
    fig.add_vrect(
        x0=2023.5, x1=2030,
        fillcolor="gray", opacity=0.1,
        annotation_text="Proiecție", annotation_position="top left"
    )

    fig.update_layout(
        xaxis_title="An",
        yaxis_title=indicator_forecast,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=450
    )

    st.plotly_chart(fig, use_container_width=True)

    # Rezumat scenarii
    col1, col2, col3 = st.columns(3)

    with col1:
        st.success(f"""
        **Scenariu Optimist (2030)**

        {indicator_forecast}: {optimist_proj[-1]:,.0f}
        Creștere: +{growth_rates['Optimist'][indicator_forecast]*100:.0f}%/an
        """)

    with col2:
        st.info(f"""
        **Scenariu Bază (2030)**

        {indicator_forecast}: {base_proj[-1]:,.0f}
        Creștere: +{growth_rates['Bază'][indicator_forecast]*100:.0f}%/an
        """)

    with col3:
        st.warning(f"""
        **Scenariu Pesimist (2030)**

        {indicator_forecast}: {pesimist_proj[-1]:,.0f}
        Creștere: +{growth_rates['Pesimist'][indicator_forecast]*100:.0f}%/an
        """)

with tab3:
    st.subheader("Analiză Corelații între Indicatori")

    st.markdown("""
    Analiza corelațiilor ajută la înțelegerea relațiilor cauză-efect
    între diferiți indicatori economici.
    """)

    # Matrice de corelație
    indicators = ["Angajați", "CA", "Export", "Productivitate", "R&D", "Investiții"]

    # Matrice simulată
    corr_matrix = np.array([
        [1.00, 0.92, 0.88, 0.45, 0.52, 0.78],
        [0.92, 1.00, 0.95, 0.62, 0.58, 0.85],
        [0.88, 0.95, 1.00, 0.55, 0.48, 0.72],
        [0.45, 0.62, 0.55, 1.00, 0.75, 0.68],
        [0.52, 0.58, 0.48, 0.75, 1.00, 0.82],
        [0.78, 0.85, 0.72, 0.68, 0.82, 1.00]
    ])

    fig_corr = px.imshow(
        corr_matrix,
        x=indicators,
        y=indicators,
        color_continuous_scale="RdBu_r",
        aspect="auto",
        text_auto=".2f"
    )

    fig_corr.update_layout(
        title="Matrice de Corelație între Indicatori",
        height=500
    )

    st.plotly_chart(fig_corr, use_container_width=True)

    # Interpretare
    st.markdown("### Interpretare Corelații Cheie")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Corelații Puternice (>0.8):**
        - CA ↔ Export: 0.95 (logică: exporturile domină CA)
        - CA ↔ Angajați: 0.92 (mai mulți angajați = CA mai mare)
        - R&D ↔ Investiții: 0.82 (investițiile susțin R&D)
        """)

    with col2:
        st.markdown("""
        **Corelații Moderate (0.5-0.8):**
        - Productivitate ↔ R&D: 0.75 (R&D crește productivitatea)
        - Investiții ↔ Angajați: 0.78 (investițiile creează locuri de muncă)
        """)

    # Scatter plot pentru perechi selectate
    st.markdown("### Analiză Detaliată Pereche")

    pair_col1, pair_col2 = st.columns(2)

    with pair_col1:
        ind1 = st.selectbox("Indicator X", indicators, index=0)
    with pair_col2:
        ind2 = st.selectbox("Indicator Y", indicators, index=3)

    # Date simulate pentru scatter
    np.random.seed(42)
    n_points = 14  # 2010-2023

    x_data = np.linspace(30, 65, n_points) + np.random.normal(0, 2, n_points)
    y_data = 100 + x_data * 1.5 + np.random.normal(0, 5, n_points)

    fig_scatter = px.scatter(
        x=x_data,
        y=y_data,
        trendline="ols",
        labels={"x": ind1, "y": ind2},
        title=f"Relația {ind1} vs {ind2}"
    )

    fig_scatter.update_layout(height=400)
    st.plotly_chart(fig_scatter, use_container_width=True)
