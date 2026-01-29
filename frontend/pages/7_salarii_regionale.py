"""
Pagina Salarii Regionale - Comparație salarii brute/nete pe județe
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

st.set_page_config(page_title="Salarii Regionale", page_icon="💰", layout="wide")

# Verifică autentificarea
require_auth()
show_user_info()

st.title("💰 Salarii Regionale")
st.markdown("Comparație câștiguri salariale medii brute și nete în Regiunea Vest")

try:
    from db_utils import get_salary_comparison, get_available_years

    # Filtre
    col1, col2 = st.columns([1, 3])

    with col1:
        years = get_available_years()
        selected_year = st.selectbox("Selectează anul", years if years else [2025, 2024, 2023])

    # Obține datele
    df = get_salary_comparison(selected_year)

    if df.empty:
        st.warning("Nu există date pentru anul selectat.")
    else:
        # Pivot pentru a avea brut și net pe coloane
        df_pivot = df.pivot_table(
            index=['county_name', 'county_code', 'year', 'quarter'],
            columns='indicator_code',
            values='value'
        ).reset_index()

        # Cele mai recente date per județ
        df_latest = df_pivot.sort_values(['year', 'quarter'], ascending=False).groupby('county_name').first().reset_index()

        st.markdown("---")

        # KPIs
        st.subheader("📊 Statistici Generale")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        with kpi1:
            if 'AVG_GROSS_SALARY' in df_latest.columns:
                avg_gross = df_latest['AVG_GROSS_SALARY'].mean()
                st.metric("Salariu Brut Mediu Regional", f"{avg_gross:,.0f} RON")

        with kpi2:
            if 'AVG_NET_SALARY' in df_latest.columns:
                avg_net = df_latest['AVG_NET_SALARY'].mean()
                st.metric("Salariu Net Mediu Regional", f"{avg_net:,.0f} RON")

        with kpi3:
            if 'AVG_GROSS_SALARY' in df_latest.columns:
                max_gross = df_latest.loc[df_latest['AVG_GROSS_SALARY'].idxmax()]
                st.metric("Cel mai mare salariu brut", f"{max_gross['AVG_GROSS_SALARY']:,.0f} RON", f"{max_gross['county_name']}")

        with kpi4:
            if 'AVG_GROSS_SALARY' in df_latest.columns:
                min_gross = df_latest.loc[df_latest['AVG_GROSS_SALARY'].idxmin()]
                st.metric("Cel mai mic salariu brut", f"{min_gross['AVG_GROSS_SALARY']:,.0f} RON", f"{min_gross['county_name']}")

        st.markdown("---")

        # Grafice
        chart1, chart2 = st.columns(2)

        with chart1:
            st.subheader("💵 Comparație Salarii pe Județe")

            if 'AVG_GROSS_SALARY' in df_latest.columns and 'AVG_NET_SALARY' in df_latest.columns:
                fig = go.Figure()

                fig.add_trace(go.Bar(
                    name='Salariu Brut',
                    x=df_latest['county_name'],
                    y=df_latest['AVG_GROSS_SALARY'],
                    marker_color='#1E3A5F',
                    text=df_latest['AVG_GROSS_SALARY'].apply(lambda x: f'{x:,.0f}'),
                    textposition='outside'
                ))

                fig.add_trace(go.Bar(
                    name='Salariu Net',
                    x=df_latest['county_name'],
                    y=df_latest['AVG_NET_SALARY'],
                    marker_color='#4CAF50',
                    text=df_latest['AVG_NET_SALARY'].apply(lambda x: f'{x:,.0f}'),
                    textposition='outside'
                ))

                fig.update_layout(
                    barmode='group',
                    xaxis_title="Județ",
                    yaxis_title="RON",
                    height=400,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02)
                )

                st.plotly_chart(fig, use_container_width=True)

        with chart2:
            st.subheader("📈 Evoluție Trimestrială")

            # Evoluție în timp
            df_evolution = df_pivot.sort_values(['year', 'quarter'])
            df_evolution['period'] = df_evolution['year'].astype(str) + ' T' + df_evolution['quarter'].astype(str)

            if 'AVG_GROSS_SALARY' in df_evolution.columns:
                fig2 = px.line(
                    df_evolution,
                    x='period',
                    y='AVG_GROSS_SALARY',
                    color='county_name',
                    markers=True,
                    title='Evoluție Salariu Brut'
                )

                fig2.update_layout(
                    xaxis_title="Perioadă",
                    yaxis_title="RON",
                    height=400,
                    legend_title="Județ"
                )

                st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

        # Tabel detaliat
        st.subheader("📋 Date Detaliate")

        df_display = df_pivot.copy()
        df_display.columns = ['Județ', 'Cod', 'An', 'Trimestru', 'Salariu Brut (RON)', 'Salariu Net (RON)']

        if 'Salariu Brut (RON)' in df_display.columns:
            df_display['Salariu Brut (RON)'] = df_display['Salariu Brut (RON)'].apply(lambda x: f'{x:,.0f}' if pd.notna(x) else '-')
        if 'Salariu Net (RON)' in df_display.columns:
            df_display['Salariu Net (RON)'] = df_display['Salariu Net (RON)'].apply(lambda x: f'{x:,.0f}' if pd.notna(x) else '-')

        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Download
        csv = df_pivot.to_csv(index=False)
        st.download_button(
            label="📥 Descarcă CSV",
            data=csv,
            file_name=f"salarii_regionale_{selected_year}.csv",
            mime="text/csv"
        )

except Exception as e:
    st.error(f"Eroare la încărcarea datelor: {str(e)}")
    st.info("Asigurați-vă că baza de date este configurată corect și conține date.")
