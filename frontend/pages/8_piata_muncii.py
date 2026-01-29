"""
Pagina Piața Muncii - Analiză șomaj și angajați
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import sys
if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import require_auth, show_user_info

st.set_page_config(page_title="Piața Muncii", page_icon="👷", layout="wide")

# Verifică autentificarea
require_auth()
show_user_info()

st.title("👷 Piața Muncii")
st.markdown("Analiză angajați, șomaj și dinamica pieței muncii în Regiunea Vest")

try:
    from db_utils import get_labor_market_data, get_available_years

    # Filtre
    col1, col2 = st.columns([1, 3])

    with col1:
        years = get_available_years()
        selected_year = st.selectbox("Selectează anul", years if years else [2025, 2024, 2023])

    # Obține datele
    df = get_labor_market_data(selected_year)

    if df.empty:
        st.warning("Nu există date pentru anul selectat.")
    else:
        # Pivot pentru a avea indicatorii pe coloane
        df_pivot = df.pivot_table(
            index=['county_name', 'county_code', 'year', 'quarter'],
            columns='indicator_code',
            values='value'
        ).reset_index()

        # Cele mai recente date per județ
        df_latest = df_pivot.sort_values(['year', 'quarter'], ascending=False).groupby('county_name').first().reset_index()

        st.markdown("---")

        # KPIs
        st.subheader("📊 Indicatori Cheie Piața Muncii")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        with kpi1:
            if 'EMPLOYEES_COUNT' in df_latest.columns:
                total_emp = df_latest['EMPLOYEES_COUNT'].sum()
                st.metric("Total Salariați Regiune", f"{total_emp:,.0f}")

        with kpi2:
            if 'UNEMPLOYED_COUNT' in df_latest.columns:
                total_unemp = df_latest['UNEMPLOYED_COUNT'].sum()
                st.metric("Total Șomeri Regiune", f"{total_unemp:,.0f}")

        with kpi3:
            if 'UNEMPLOYMENT_RATE' in df_latest.columns:
                avg_rate = df_latest['UNEMPLOYMENT_RATE'].mean()
                st.metric("Rata Șomajului Medie", f"{avg_rate:.1f}%")

        with kpi4:
            if 'UNEMPLOYMENT_RATE' in df_latest.columns:
                min_rate = df_latest.loc[df_latest['UNEMPLOYMENT_RATE'].idxmin()]
                st.metric("Cea mai mică rată", f"{min_rate['UNEMPLOYMENT_RATE']:.1f}%", f"{min_rate['county_name']}")

        st.markdown("---")

        # Grafice principale
        chart1, chart2 = st.columns(2)

        with chart1:
            st.subheader("📊 Rata Șomajului pe Județe")

            if 'UNEMPLOYMENT_RATE' in df_latest.columns:
                fig = px.bar(
                    df_latest.sort_values('UNEMPLOYMENT_RATE', ascending=True),
                    x='UNEMPLOYMENT_RATE',
                    y='county_name',
                    orientation='h',
                    color='UNEMPLOYMENT_RATE',
                    color_continuous_scale='RdYlGn_r',
                    text='UNEMPLOYMENT_RATE'
                )

                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                fig.update_layout(
                    xaxis_title="Rata Șomajului (%)",
                    yaxis_title="",
                    height=350,
                    showlegend=False
                )

                st.plotly_chart(fig, use_container_width=True)

        with chart2:
            st.subheader("👥 Efectiv Salariați pe Județe")

            if 'EMPLOYEES_COUNT' in df_latest.columns:
                fig2 = px.pie(
                    df_latest,
                    values='EMPLOYEES_COUNT',
                    names='county_name',
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set2
                )

                fig2.update_traces(textposition='inside', textinfo='percent+label')
                fig2.update_layout(height=350)

                st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

        # Evoluție în timp
        st.subheader("📈 Evoluție Trimestrială")

        tab1, tab2, tab3 = st.tabs(["Rata Șomajului", "Număr Șomeri", "Efectiv Salariați"])

        df_evolution = df_pivot.sort_values(['year', 'quarter'])
        df_evolution['period'] = df_evolution['year'].astype(str) + ' T' + df_evolution['quarter'].astype(str)

        with tab1:
            if 'UNEMPLOYMENT_RATE' in df_evolution.columns:
                fig3 = px.line(
                    df_evolution,
                    x='period',
                    y='UNEMPLOYMENT_RATE',
                    color='county_name',
                    markers=True
                )
                fig3.update_layout(
                    xaxis_title="Perioadă",
                    yaxis_title="Rata Șomajului (%)",
                    height=400,
                    legend_title="Județ"
                )
                st.plotly_chart(fig3, use_container_width=True)

        with tab2:
            if 'UNEMPLOYED_COUNT' in df_evolution.columns:
                fig4 = px.area(
                    df_evolution,
                    x='period',
                    y='UNEMPLOYED_COUNT',
                    color='county_name',
                    line_group='county_name'
                )
                fig4.update_layout(
                    xaxis_title="Perioadă",
                    yaxis_title="Număr Șomeri",
                    height=400,
                    legend_title="Județ"
                )
                st.plotly_chart(fig4, use_container_width=True)

        with tab3:
            if 'EMPLOYEES_COUNT' in df_evolution.columns:
                fig5 = px.bar(
                    df_evolution,
                    x='period',
                    y='EMPLOYEES_COUNT',
                    color='county_name',
                    barmode='group'
                )
                fig5.update_layout(
                    xaxis_title="Perioadă",
                    yaxis_title="Efectiv Salariați",
                    height=400,
                    legend_title="Județ"
                )
                st.plotly_chart(fig5, use_container_width=True)

        st.markdown("---")

        # Tabel detaliat
        st.subheader("📋 Date Detaliate")

        df_display = df_pivot.copy()
        col_rename = {
            'county_name': 'Județ',
            'county_code': 'Cod',
            'year': 'An',
            'quarter': 'Trimestru'
        }
        if 'EMPLOYEES_COUNT' in df_display.columns:
            col_rename['EMPLOYEES_COUNT'] = 'Salariați'
        if 'UNEMPLOYED_COUNT' in df_display.columns:
            col_rename['UNEMPLOYED_COUNT'] = 'Șomeri'
        if 'UNEMPLOYMENT_RATE' in df_display.columns:
            col_rename['UNEMPLOYMENT_RATE'] = 'Rata Șomaj (%)'

        df_display = df_display.rename(columns=col_rename)

        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Download
        csv = df_pivot.to_csv(index=False)
        st.download_button(
            label="📥 Descarcă CSV",
            data=csv,
            file_name=f"piata_muncii_{selected_year}.csv",
            mime="text/csv"
        )

except Exception as e:
    st.error(f"Eroare la încărcarea datelor: {str(e)}")
    st.info("Asigurați-vă că baza de date este configurată corect și conține date.")
