"""
Pagina Analiză Județ - Dashboard detaliat per județ
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import os
import sys
if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import require_auth, show_user_info

st.set_page_config(page_title="Analiză Județ", page_icon="🗺️", layout="wide")

# Verifică autentificarea
require_auth()
show_user_info()

st.title("🗺️ Analiză Județ")
st.markdown("Dashboard detaliat cu toți indicatorii pentru un județ selectat")

try:
    from db_utils import get_county_details, get_counties, get_available_years

    # Obține lista de județe
    counties_df = get_counties()

    # Selector județ
    col1, col2 = st.columns([1, 3])

    with col1:
        county_options = dict(zip(counties_df['name'], counties_df['code']))
        selected_county_name = st.selectbox("🏛️ Selectează județul", list(county_options.keys()))
        selected_county = county_options[selected_county_name]

    # Obține datele pentru județ
    df = get_county_details(selected_county)

    if df.empty:
        st.warning("Nu există date pentru județul selectat.")
    else:
        st.markdown("---")

        # Header cu info județ
        county_info = counties_df[counties_df['code'] == selected_county].iloc[0]

        st.header(f"📍 {selected_county_name}")

        # Cele mai recente date per indicator
        df_latest = df.sort_values(['year', 'quarter'], ascending=False).groupby('indicator_code').first().reset_index()

        # KPIs principale
        st.subheader("📊 Indicatori Cheie (Ultimele Date)")

        kpi_cols = st.columns(4)

        kpi_mapping = {
            'AVG_GROSS_SALARY': ('💰 Salariu Brut', 'RON'),
            'AVG_NET_SALARY': ('💵 Salariu Net', 'RON'),
            'UNEMPLOYMENT_RATE': ('📉 Rata Șomaj', '%'),
            'IND_PROD_INDEX': ('🏭 Indice Producție', 'indice')
        }

        kpi_idx = 0
        for code, (label, unit_label) in kpi_mapping.items():
            if code in df_latest['indicator_code'].values:
                row = df_latest[df_latest['indicator_code'] == code].iloc[0]
                with kpi_cols[kpi_idx % 4]:
                    if unit_label == 'RON':
                        st.metric(label, f"{row['value']:,.0f} {unit_label}")
                    elif unit_label == '%':
                        st.metric(label, f"{row['value']:.1f}{unit_label}")
                    else:
                        st.metric(label, f"{row['value']:.1f}")
                    st.caption(f"T{row['quarter']}/{row['year']}")
                kpi_idx += 1

        st.markdown("---")

        # Secțiune Salarii
        st.subheader("💰 Câștiguri Salariale")

        salary_codes = ['AVG_GROSS_SALARY', 'AVG_NET_SALARY']
        df_salary = df[df['indicator_code'].isin(salary_codes)].copy()

        if not df_salary.empty:
            df_salary['period'] = df_salary['year'].astype(str) + ' T' + df_salary['quarter'].astype(str)
            df_salary = df_salary.sort_values(['year', 'quarter'])

            fig_salary = px.line(
                df_salary,
                x='period',
                y='value',
                color='indicator_name',
                markers=True,
                color_discrete_map={
                    'Câștigul salarial mediu brut': '#1E3A5F',
                    'Câștigul salarial mediu net': '#4CAF50'
                }
            )

            fig_salary.update_layout(
                xaxis_title="Perioadă",
                yaxis_title="RON",
                height=350,
                legend_title="Indicator",
                legend=dict(orientation="h", yanchor="bottom", y=1.02)
            )

            st.plotly_chart(fig_salary, use_container_width=True)
        else:
            st.info("Nu există date despre salarii pentru acest județ.")

        st.markdown("---")

        # Secțiune Piața Muncii
        st.subheader("👷 Piața Muncii")

        col_labor1, col_labor2 = st.columns(2)

        with col_labor1:
            # Rata șomajului
            df_unemp = df[df['indicator_code'] == 'UNEMPLOYMENT_RATE'].copy()
            if not df_unemp.empty:
                df_unemp['period'] = df_unemp['year'].astype(str) + ' T' + df_unemp['quarter'].astype(str)
                df_unemp = df_unemp.sort_values(['year', 'quarter'])

                fig_unemp = go.Figure()

                fig_unemp.add_trace(go.Scatter(
                    x=df_unemp['period'],
                    y=df_unemp['value'],
                    mode='lines+markers+text',
                    text=df_unemp['value'].apply(lambda x: f'{x:.1f}%'),
                    textposition='top center',
                    line=dict(color='#E63946', width=2),
                    marker=dict(size=8)
                ))

                fig_unemp.update_layout(
                    title="Rata Șomajului",
                    xaxis_title="Perioadă",
                    yaxis_title="%",
                    height=300
                )

                st.plotly_chart(fig_unemp, use_container_width=True)

        with col_labor2:
            # Număr șomeri
            df_unemp_count = df[df['indicator_code'] == 'UNEMPLOYED_COUNT'].copy()
            if not df_unemp_count.empty:
                df_unemp_count['period'] = df_unemp_count['year'].astype(str) + ' T' + df_unemp_count['quarter'].astype(str)
                df_unemp_count = df_unemp_count.sort_values(['year', 'quarter'])

                fig_unemp_count = px.bar(
                    df_unemp_count,
                    x='period',
                    y='value',
                    color='value',
                    color_continuous_scale='Reds'
                )

                fig_unemp_count.update_layout(
                    title="Număr Șomeri",
                    xaxis_title="Perioadă",
                    yaxis_title="Persoane",
                    height=300,
                    showlegend=False
                )

                st.plotly_chart(fig_unemp_count, use_container_width=True)

        st.markdown("---")

        # Secțiune Indicatori Industriali
        st.subheader("🏭 Indicatori Industriali")

        industry_codes = ['IND_PROD_INDEX', 'IND_TURNOVER_INDEX']
        df_industry = df[df['indicator_code'].isin(industry_codes)].copy()

        if not df_industry.empty:
            df_industry['period'] = df_industry['year'].astype(str) + ' T' + df_industry['quarter'].astype(str)
            df_industry = df_industry.sort_values(['year', 'quarter'])

            fig_industry = go.Figure()

            for code in industry_codes:
                df_code = df_industry[df_industry['indicator_code'] == code]
                if not df_code.empty:
                    name = df_code.iloc[0]['indicator_name']
                    fig_industry.add_trace(go.Scatter(
                        x=df_code['period'],
                        y=df_code['value'],
                        mode='lines+markers',
                        name=name
                    ))

            fig_industry.add_hline(y=100, line_dash="dash", line_color="gray", annotation_text="Referință (100)")

            fig_industry.update_layout(
                xaxis_title="Perioadă",
                yaxis_title="Indice",
                height=350,
                legend=dict(orientation="h", yanchor="bottom", y=1.02)
            )

            st.plotly_chart(fig_industry, use_container_width=True)
        else:
            st.info("Nu există date despre indicatori industriali pentru acest județ.")

        st.markdown("---")

        # Tabel rezumat
        st.subheader("📋 Toate Datele")

        df_display = df[['indicator_name', 'year', 'quarter', 'value', 'unit']].copy()
        df_display.columns = ['Indicator', 'An', 'Trimestru', 'Valoare', 'Unitate']

        # Formatare valori
        df_display['Valoare'] = df_display.apply(
            lambda row: f"{row['Valoare']:,.0f}" if row['Unitate'] in ['numar', 'ron'] else f"{row['Valoare']:.1f}",
            axis=1
        )

        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Download
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Descarcă toate datele",
            data=csv,
            file_name=f"date_{selected_county_name.lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )

except Exception as e:
    st.error(f"Eroare la încărcarea datelor: {str(e)}")
    st.info("Asigurați-vă că baza de date este configurată corect și conține date.")
