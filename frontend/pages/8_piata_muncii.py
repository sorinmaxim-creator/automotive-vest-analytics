"""
Pagina Piața Muncii - Analiză șomaj și angajați
Design modern și profesionist
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import sys
if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import require_auth
from styles import (
    init_page_style, page_header, section_header, chart_container,
    chart_container_end, COLORS, get_plotly_layout_defaults
)

st.set_page_config(page_title="Piața Muncii", page_icon="👷", layout="wide")

# Verifică autentificarea
require_auth()

# Aplică stilurile moderne
init_page_style(st)

# Header pagină
st.markdown(page_header(
    "Piața Muncii",
    "Analiză angajați, șomaj și dinamica pieței muncii în Regiunea Vest",
    "👷"
), unsafe_allow_html=True)

try:
    from db_utils import get_labor_market_data, get_available_years

    # Filtre în sidebar
    with st.sidebar:
        st.markdown("""
        <div class="menu-group">
            <div class="menu-group-title">🔧 Filtre</div>
        </div>
        """, unsafe_allow_html=True)

        years = get_available_years()
        selected_year = st.selectbox(
            "📅 Selectează anul",
            years if years else [2025, 2024, 2023],
            key="labor_year_filter"
        )

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

        # KPIs Section
        st.markdown(section_header("Indicatori Cheie Piața Muncii", "📊"), unsafe_allow_html=True)

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

        st.markdown("<br>", unsafe_allow_html=True)

        # Grafice principale
        st.markdown(section_header("Analiză pe Județe", "📈"), unsafe_allow_html=True)

        chart1, chart2 = st.columns(2)

        with chart1:
            st.markdown(chart_container("Rata Șomajului pe Județe", "📊"), unsafe_allow_html=True)

            if 'UNEMPLOYMENT_RATE' in df_latest.columns:
                fig = px.bar(
                    df_latest.sort_values('UNEMPLOYMENT_RATE', ascending=True),
                    x='UNEMPLOYMENT_RATE',
                    y='county_name',
                    orientation='h',
                    color='UNEMPLOYMENT_RATE',
                    color_continuous_scale=[[0, COLORS['secondary']], [0.5, COLORS['warning']], [1, COLORS['error']]],
                    text='UNEMPLOYMENT_RATE'
                )

                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')

                layout_defaults = get_plotly_layout_defaults()
                fig.update_layout(
                    xaxis_title="Rata Șomajului (%)",
                    yaxis_title="",
                    height=350,
                    showlegend=False,
                    coloraxis_showscale=False,
                    **layout_defaults
                )

                st.plotly_chart(fig, use_container_width=True)

            st.markdown(chart_container_end(), unsafe_allow_html=True)

        with chart2:
            st.markdown(chart_container("Efectiv Salariați pe Județe", "👥"), unsafe_allow_html=True)

            if 'EMPLOYEES_COUNT' in df_latest.columns:
                fig2 = px.pie(
                    df_latest,
                    values='EMPLOYEES_COUNT',
                    names='county_name',
                    hole=0.4,
                    color_discrete_sequence=[COLORS['primary'], COLORS['primary_light'], COLORS['secondary'], COLORS['accent']]
                )

                fig2.update_traces(textposition='inside', textinfo='percent+label')

                layout_defaults = get_plotly_layout_defaults()
                fig2.update_layout(
                    height=350,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
                    **{k: v for k, v in layout_defaults.items() if k not in ['xaxis', 'yaxis']}
                )

                st.plotly_chart(fig2, use_container_width=True)

            st.markdown(chart_container_end(), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Evoluție în timp
        st.markdown(section_header("Evoluție Trimestrială", "📈"), unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["📉 Rata Șomajului", "👤 Număr Șomeri", "👥 Efectiv Salariați"])

        df_evolution = df_pivot.sort_values(['year', 'quarter'])
        df_evolution['period'] = df_evolution['year'].astype(str) + ' T' + df_evolution['quarter'].astype(str)

        layout_defaults = get_plotly_layout_defaults()
        color_sequence = [COLORS['primary'], COLORS['primary_light'], COLORS['secondary'], COLORS['accent']]

        with tab1:
            if 'UNEMPLOYMENT_RATE' in df_evolution.columns:
                fig3 = px.line(
                    df_evolution,
                    x='period',
                    y='UNEMPLOYMENT_RATE',
                    color='county_name',
                    markers=True,
                    color_discrete_sequence=color_sequence
                )
                fig3.update_layout(
                    xaxis_title="Perioadă",
                    yaxis_title="Rata Șomajului (%)",
                    height=400,
                    legend_title="Județ",
                    **layout_defaults
                )
                st.plotly_chart(fig3, use_container_width=True)

        with tab2:
            if 'UNEMPLOYED_COUNT' in df_evolution.columns:
                fig4 = px.area(
                    df_evolution,
                    x='period',
                    y='UNEMPLOYED_COUNT',
                    color='county_name',
                    line_group='county_name',
                    color_discrete_sequence=color_sequence
                )
                fig4.update_layout(
                    xaxis_title="Perioadă",
                    yaxis_title="Număr Șomeri",
                    height=400,
                    legend_title="Județ",
                    **layout_defaults
                )
                st.plotly_chart(fig4, use_container_width=True)

        with tab3:
            if 'EMPLOYEES_COUNT' in df_evolution.columns:
                fig5 = px.bar(
                    df_evolution,
                    x='period',
                    y='EMPLOYEES_COUNT',
                    color='county_name',
                    barmode='group',
                    color_discrete_sequence=color_sequence
                )
                fig5.update_layout(
                    xaxis_title="Perioadă",
                    yaxis_title="Efectiv Salariați",
                    height=400,
                    legend_title="Județ",
                    **layout_defaults
                )
                st.plotly_chart(fig5, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Tabel detaliat
        st.markdown(section_header("Date Detaliate", "📋"), unsafe_allow_html=True)

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
        col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 2])
        with col_dl1:
            csv = df_pivot.to_csv(index=False)
            st.download_button(
                label="📥 Descarcă CSV",
                data=csv,
                file_name=f"piata_muncii_{selected_year}.csv",
                mime="text/csv",
                use_container_width=True
            )

except Exception as e:
    st.error(f"Eroare la încărcarea datelor: {str(e)}")
    st.info("Asigurați-vă că baza de date este configurată corect și conține date.")

# Footer
st.markdown(f"""
<div class="app-footer">
    <p style="margin: 0;">© 2025 Vest Policy Lab - Automotive Vest Analytics</p>
</div>
""", unsafe_allow_html=True)
