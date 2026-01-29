"""
Pagina Hărți Interactive
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import folium
from streamlit_folium import st_folium
import sys
import os
if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import require_auth, show_user_info

st.set_page_config(page_title="Hărți", page_icon="🗺️", layout="wide")

# Verifică autentificarea
require_auth()
show_user_info()

st.title("🗺️ Hărți Interactive")
st.markdown("Vizualizare geografică a sectorului automotive")

# Selectare indicator pentru colorare
indicator = st.selectbox(
    "Colorare hartă după:",
    ["Număr angajați", "Cifră de afaceri", "Productivitate", "Număr firme", "Concentrare (HHI)"]
)

year = st.slider("An", 2015, 2023, 2023)

# Date coordonate județe
county_coords = {
    "Timiș": {"lat": 45.7489, "lon": 21.2087, "employees": 33200, "turnover": 6474,
              "productivity": 195, "companies": 245, "color": "#1E3A5F"},
    "Arad": {"lat": 46.1866, "lon": 21.3123, "employees": 21500, "turnover": 3870,
             "productivity": 180, "companies": 142, "color": "#2E5A8F"},
    "Hunedoara": {"lat": 45.7500, "lon": 22.9000, "employees": 4600, "turnover": 759,
                  "productivity": 165, "companies": 48, "color": "#4E7ABF"},
    "Caraș-Severin": {"lat": 45.0833, "lon": 21.8833, "employees": 1250, "turnover": 175,
                      "productivity": 140, "companies": 13, "color": "#7E9ACF"}
}

# Tabs pentru diferite vizualizări
tab1, tab2, tab3 = st.tabs(["🗺️ Hartă Interactivă", "📊 Choropleth", "📍 Clustere"])

with tab1:
    st.subheader("Hartă Regiunii Vest")

    # Creare hartă Folium
    m = folium.Map(
        location=[45.5, 21.8],
        zoom_start=8,
        tiles="cartodbpositron"
    )

    # Adăugare markere pentru fiecare județ
    for county, data in county_coords.items():
        # Dimensiune marker bazată pe angajați
        radius = data["employees"] / 2000

        popup_html = f"""
        <div style="width: 200px;">
            <h4 style="color: #1E3A5F;">{county}</h4>
            <hr>
            <b>Angajați:</b> {data['employees']:,}<br>
            <b>CA:</b> €{data['turnover']} mil<br>
            <b>Productivitate:</b> €{data['productivity']}k<br>
            <b>Nr. Firme:</b> {data['companies']}<br>
        </div>
        """

        folium.CircleMarker(
            location=[data["lat"], data["lon"]],
            radius=radius,
            popup=folium.Popup(popup_html, max_width=250),
            color=data["color"],
            fill=True,
            fill_color=data["color"],
            fill_opacity=0.7,
            tooltip=f"{county}: {data['employees']:,} angajați"
        ).add_to(m)

        # Label pentru județ
        folium.Marker(
            location=[data["lat"], data["lon"]],
            icon=folium.DivIcon(
                html=f'<div style="font-size: 10px; font-weight: bold; color: #333;">{county}</div>'
            )
        ).add_to(m)

    # Afișare hartă
    st_folium(m, width=None, height=500)

    # Legendă
    st.markdown("""
    **Legendă:** Dimensiunea cercului reprezintă numărul de angajați.
    Click pe marker pentru detalii.
    """)

with tab2:
    st.subheader("Distribuție Geografică - Choropleth")

    # Simulare choropleth cu Plotly
    df_counties = pd.DataFrame([
        {"Județ": k, "Lat": v["lat"], "Lon": v["lon"],
         "Angajați": v["employees"], "CA": v["turnover"],
         "Productivitate": v["productivity"]}
        for k, v in county_coords.items()
    ])

    # Bubble map
    fig = px.scatter_mapbox(
        df_counties,
        lat="Lat",
        lon="Lon",
        size="Angajați",
        color="Productivitate",
        hover_name="Județ",
        hover_data={"Angajați": True, "CA": True, "Productivitate": True, "Lat": False, "Lon": False},
        color_continuous_scale="RdYlGn",
        size_max=50,
        zoom=7,
        center={"lat": 45.5, "lon": 21.8}
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        height=500,
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tabel cu date
    st.markdown("### Date pe Județe")
    st.dataframe(df_counties, hide_index=True, use_container_width=True)

with tab3:
    st.subheader("Clustere Industriale")

    st.markdown("""
    ### Principalele Clustere Automotive

    Regiunea Vest găzduiește mai multe zone cu concentrare ridicată de activități automotive:
    """)

    clusters = [
        {
            "name": "Timișoara - Hub Principal",
            "description": "Cel mai mare cluster, cu Continental, Hella, Dräxlmaier",
            "employees": 25000,
            "companies": 180,
            "specialization": "Componente electronice, software automotive"
        },
        {
            "name": "Arad - Zona Industrială Vest",
            "description": "Cluster secundar cu Yazaki, Mahle, Adient",
            "employees": 15000,
            "companies": 95,
            "specialization": "Cablaje, componente interioare"
        },
        {
            "name": "Arad - Zona Curtici",
            "description": "Zonă în dezvoltare cu acces transfrontalier",
            "employees": 4500,
            "companies": 35,
            "specialization": "Logistică, subansamble"
        }
    ]

    for cluster in clusters:
        with st.expander(f"📍 {cluster['name']}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Angajați", f"{cluster['employees']:,}")
            with col2:
                st.metric("Companii", cluster['companies'])
            with col3:
                st.metric("Tip", cluster['specialization'][:20] + "...")

            st.markdown(f"**Descriere:** {cluster['description']}")
            st.markdown(f"**Specializare:** {cluster['specialization']}")

    # Heatmap simplificat
    st.markdown("### Densitate Activitate Automotive")

    heatmap_data = pd.DataFrame({
        "Zonă": ["Timișoara Nord", "Timișoara Sud", "Arad Vest", "Arad Centru",
                 "Hunedoara", "Deva", "Reșița", "Caransebeș"],
        "Intensitate": [95, 78, 85, 62, 35, 28, 15, 8],
        "Tip": ["Hub", "Hub", "Cluster", "Cluster", "Dispersat", "Dispersat", "Izolat", "Izolat"]
    })

    fig_heat = px.bar(
        heatmap_data,
        x="Zonă",
        y="Intensitate",
        color="Tip",
        title="Intensitate Activitate Automotive pe Zone",
        color_discrete_map={"Hub": "#1E3A5F", "Cluster": "#457B9D", "Dispersat": "#A8DADC", "Izolat": "#F1FAEE"}
    )

    fig_heat.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_heat, use_container_width=True)
