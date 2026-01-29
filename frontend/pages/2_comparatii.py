"""
Pagina de Comparații
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import os
import sys
if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import require_auth, show_user_info

st.set_page_config(page_title="Comparații", page_icon="📈", layout="wide")

# Verifică autentificarea
require_auth()
show_user_info()

st.title("📈 Analize Comparative")
st.markdown("Comparații între județe, sectoare și perioade")

# Tabs pentru diferite tipuri de comparații
tab1, tab2, tab3 = st.tabs([
    "🏛️ Comparație Județe",
    "🏭 Comparație Sectoare",
    "🌍 Regiunea Vest vs România vs UE"
])

with tab1:
    st.subheader("Comparație între Județele Regiunii Vest")

    # Selectare indicator
    indicator = st.selectbox(
        "Selectează indicatorul",
        ["Număr angajați", "Cifră de afaceri", "Productivitate", "Număr firme", "Export"]
    )

    year_range = st.slider("Perioada", 2015, 2023, (2019, 2023))

    # Data
    counties = ["Timiș", "Arad", "Hunedoara", "Caraș-Severin"]
    years = list(range(year_range[0], year_range[1] + 1))

    # Sample data pentru angajați
    data = {
        "Timiș": [28500, 27200, 29100, 31500, 33200],
        "Arad": [18200, 17500, 18800, 20100, 21500],
        "Hunedoara": [4200, 3900, 4100, 4400, 4600],
        "Caraș-Severin": [1100, 1050, 1150, 1200, 1250]
    }

    # Line chart
    fig = go.Figure()
    colors = ["#1E3A5F", "#E63946", "#457B9D", "#A8DADC"]

    for i, county in enumerate(counties):
        fig.add_trace(go.Scatter(
            x=years,
            y=data[county][-len(years):],
            name=county,
            mode="lines+markers",
            line=dict(color=colors[i], width=2)
        ))

    fig.update_layout(
        xaxis_title="An",
        yaxis_title=indicator,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=450,
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tabel comparativ
    st.subheader(f"Date Detaliate ({year_range[1]})")

    comparison_df = pd.DataFrame({
        "Județ": counties,
        "Valoare 2023": [33200, 21500, 4600, 1250],
        "Valoare 2019": [28500, 18200, 4200, 1100],
        "Creștere (%)": ["+16.5%", "+18.1%", "+9.5%", "+13.6%"],
        "Pondere Regiune": ["54.8%", "35.5%", "7.6%", "2.1%"],
        "Rang": [1, 2, 3, 4]
    })

    st.dataframe(comparison_df, hide_index=True, use_container_width=True)

with tab2:
    st.subheader("Comparație între Subsectoare Automotive")

    subsector_data = pd.DataFrame({
        "Subsector": ["Fabricare componente", "Asamblare vehicule", "Echipamente electrice",
                      "Cercetare-Dezvoltare", "Caroserii și remorci"],
        "CAEN": ["2932", "2910", "2931", "7112", "2920"],
        "Angajați 2023": [28000, 18000, 8500, 3500, 2550],
        "Angajați 2019": [23000, 16500, 7200, 2800, 2500],
        "Creștere": ["+21.7%", "+9.1%", "+18.1%", "+25.0%", "+2.0%"],
        "CA (mil EUR)": [4200, 5100, 1200, 450, 328]
    })

    col1, col2 = st.columns(2)

    with col1:
        # Pie chart angajați
        fig_pie = px.pie(
            subsector_data,
            values="Angajați 2023",
            names="Subsector",
            title="Distribuție Angajați pe Subsectoare",
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Bar chart creștere
        subsector_data["Creștere_num"] = [21.7, 9.1, 18.1, 25.0, 2.0]

        fig_bar = px.bar(
            subsector_data,
            x="Subsector",
            y="Creștere_num",
            title="Rata de Creștere 2019-2023 (%)",
            color="Creștere_num",
            color_continuous_scale="RdYlGn"
        )
        fig_bar.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.dataframe(subsector_data.drop(columns=["Creștere_num"]), hide_index=True, use_container_width=True)

with tab3:
    st.subheader("Regiunea Vest în Context Național și European")

    # Comparație RO vs UE
    comparison_metrics = st.multiselect(
        "Selectează indicatorii",
        ["Productivitate", "Salariu mediu", "Investiții R&D", "Pondere PIB"],
        default=["Productivitate", "Salariu mediu"]
    )

    # Sample data
    geo_data = pd.DataFrame({
        "Regiune": ["Regiunea Vest", "România", "UE-27", "Germania", "Cehia"],
        "Productivitate (€k/ang)": [185, 142, 245, 310, 195],
        "Salariu mediu (EUR)": [1450, 1200, 2800, 4200, 1650],
        "R&D (% CA)": [2.1, 1.5, 3.2, 5.8, 2.8],
        "Angajați sector": [60550, 185000, 2800000, 850000, 180000]
    })

    # Radar chart
    categories = ["Productivitate", "Salariu", "R&D", "Dimensiune"]

    fig_radar = go.Figure()

    # Normalizare pentru radar (0-100)
    vest_values = [75, 52, 66, 22]  # Valori normalizate
    ro_values = [58, 43, 47, 66]
    eu_values = [100, 100, 100, 100]

    fig_radar.add_trace(go.Scatterpolar(
        r=vest_values,
        theta=categories,
        fill='toself',
        name='Regiunea Vest',
        line_color='#1E3A5F'
    ))

    fig_radar.add_trace(go.Scatterpolar(
        r=ro_values,
        theta=categories,
        fill='toself',
        name='România',
        line_color='#E63946'
    ))

    fig_radar.add_trace(go.Scatterpolar(
        r=eu_values,
        theta=categories,
        fill='toself',
        name='Media UE',
        line_color='#457B9D',
        opacity=0.3
    ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title="Poziționare Competitivă (% din media UE)",
        height=500
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        st.plotly_chart(fig_radar, use_container_width=True)

    with col2:
        st.markdown("### Interpretare")
        st.markdown("""
        **Regiunea Vest:**
        - **Productivitate:** 75% din media UE
        - **Salarii:** 52% din media UE
        - **R&D:** 66% din media UE

        **Poziție competitivă:**
        - Avantaj de cost salarial
        - Productivitate în creștere
        - Potențial de creștere R&D
        """)

    st.dataframe(geo_data, hide_index=True, use_container_width=True)
