"""
Pagina Salarii Regionale - Comparație salarii brute/nete pe județe
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

st.set_page_config(page_title="Salarii Regionale", page_icon="💰", layout="wide")

# Verifică autentificarea
require_auth()

# Aplică stilurile moderne
init_page_style(st)

# Header pagină
st.markdown(page_header(
    "Salarii Regionale",
    "Comparație câștiguri salariale medii brute și nete în Regiunea Vest",
    "💰"
), unsafe_allow_html=True)

try:
    from db_utils import get_salary_comparison, get_available_years

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
            key="salary_year_filter"
        )

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

        # KPIs Section
        st.markdown(section_header("Statistici Generale", "📊"), unsafe_allow_html=True)

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

        st.markdown("<br>", unsafe_allow_html=True)

        # Grafice
        st.markdown(section_header("Analiză Grafică", "📈"), unsafe_allow_html=True)

        chart1, chart2 = st.columns(2)

        with chart1:
            st.markdown(chart_container("Comparație Salarii pe Județe", "💵"), unsafe_allow_html=True)

            if 'AVG_GROSS_SALARY' in df_latest.columns and 'AVG_NET_SALARY' in df_latest.columns:
                fig = go.Figure()

                fig.add_trace(go.Bar(
                    name='Salariu Brut',
                    x=df_latest['county_name'],
                    y=df_latest['AVG_GROSS_SALARY'],
                    marker_color=COLORS['primary'],
                    text=df_latest['AVG_GROSS_SALARY'].apply(lambda x: f'{x:,.0f}'),
                    textposition='outside'
                ))

                fig.add_trace(go.Bar(
                    name='Salariu Net',
                    x=df_latest['county_name'],
                    y=df_latest['AVG_NET_SALARY'],
                    marker_color=COLORS['secondary'],
                    text=df_latest['AVG_NET_SALARY'].apply(lambda x: f'{x:,.0f}'),
                    textposition='outside'
                ))

                layout_defaults = get_plotly_layout_defaults()
                fig.update_layout(
                    barmode='group',
                    xaxis_title="Județ",
                    yaxis_title="RON",
                    height=380,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    **layout_defaults
                )

                st.plotly_chart(fig, use_container_width=True)

            st.markdown(chart_container_end(), unsafe_allow_html=True)

        with chart2:
            st.markdown(chart_container("Evoluție Trimestrială", "📈"), unsafe_allow_html=True)

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
                    color_discrete_sequence=[COLORS['primary'], COLORS['primary_light'], COLORS['secondary'], COLORS['accent']]
                )

                layout_defaults = get_plotly_layout_defaults()
                fig2.update_layout(
                    xaxis_title="Perioadă",
                    yaxis_title="RON",
                    height=380,
                    legend_title="Județ",
                    **layout_defaults
                )

                st.plotly_chart(fig2, use_container_width=True)

            st.markdown(chart_container_end(), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Tabel detaliat
        st.markdown(section_header("Date Detaliate", "📋"), unsafe_allow_html=True)

        df_display = df_pivot.copy()
        df_display.columns = ['Județ', 'Cod', 'An', 'Trimestru', 'Salariu Brut (RON)', 'Salariu Net (RON)']

        if 'Salariu Brut (RON)' in df_display.columns:
            df_display['Salariu Brut (RON)'] = df_display['Salariu Brut (RON)'].apply(lambda x: f'{x:,.0f}' if pd.notna(x) else '-')
        if 'Salariu Net (RON)' in df_display.columns:
            df_display['Salariu Net (RON)'] = df_display['Salariu Net (RON)'].apply(lambda x: f'{x:,.0f}' if pd.notna(x) else '-')

        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Download
        col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 2])
        with col_dl1:
            csv = df_pivot.to_csv(index=False)
            st.download_button(
                label="📥 Descarcă CSV",
                data=csv,
                file_name=f"salarii_regionale_{selected_year}.csv",
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
