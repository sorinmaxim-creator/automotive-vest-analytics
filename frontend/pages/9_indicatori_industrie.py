"""
Pagina Indicatori Industrie - Producție industrială și cifră de afaceri
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
    chart_container_end, COLORS, get_plotly_layout_defaults, alert_box
)

st.set_page_config(page_title="Indicatori Industrie", page_icon="🏭", layout="wide")

# Verifică autentificarea
require_auth()

# Aplică stilurile moderne
init_page_style(st)

# Header pagină
st.markdown(page_header(
    "Indicatori Industrie",
    "Analiza indicilor de producție industrială și cifră de afaceri în Regiunea Vest",
    "🏭"
), unsafe_allow_html=True)

try:
    from db_utils import get_industry_indices, get_available_years

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
            key="industry_year_filter"
        )

    # Obține datele
    df = get_industry_indices(selected_year)

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

        # Info box
        st.markdown(alert_box(
            """<strong>Interpretare indicatori:</strong><br>
            • <strong>Indice > 100</strong>: Creștere față de perioada de referință<br>
            • <strong>Indice = 100</strong>: Fără modificare<br>
            • <strong>Indice < 100</strong>: Scădere față de perioada de referință""",
            "info"
        ), unsafe_allow_html=True)

        # KPIs Section
        st.markdown(section_header("Situația Curentă", "📊"), unsafe_allow_html=True)

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)

        with kpi1:
            if 'IND_PROD_INDEX' in df_latest.columns:
                avg_prod = df_latest['IND_PROD_INDEX'].mean()
                delta = avg_prod - 100
                st.metric("Indice Producție Mediu", f"{avg_prod:.1f}", f"{delta:+.1f} vs 100")

        with kpi2:
            if 'IND_TURNOVER_INDEX' in df_latest.columns:
                avg_turn = df_latest['IND_TURNOVER_INDEX'].mean()
                delta = avg_turn - 100
                st.metric("Indice CA Mediu", f"{avg_turn:.1f}", f"{delta:+.1f} vs 100")

        with kpi3:
            if 'IND_PROD_INDEX' in df_latest.columns:
                best_prod = df_latest.loc[df_latest['IND_PROD_INDEX'].idxmax()]
                st.metric("Lider Producție", f"{best_prod['IND_PROD_INDEX']:.1f}", f"{best_prod['county_name']}")

        with kpi4:
            if 'IND_TURNOVER_INDEX' in df_latest.columns:
                best_turn = df_latest.loc[df_latest['IND_TURNOVER_INDEX'].idxmax()]
                st.metric("Lider Cifră Afaceri", f"{best_turn['IND_TURNOVER_INDEX']:.1f}", f"{best_turn['county_name']}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Grafice principale
        st.markdown(section_header("Comparație Indici", "📈"), unsafe_allow_html=True)

        chart1, chart2 = st.columns(2)

        with chart1:
            st.markdown(chart_container("Indicele Producției Industriale", "📈"), unsafe_allow_html=True)

            if 'IND_PROD_INDEX' in df_latest.columns:
                df_sorted = df_latest.sort_values('IND_PROD_INDEX', ascending=True)
                colors = [COLORS['error'] if x < 100 else COLORS['secondary'] for x in df_sorted['IND_PROD_INDEX']]

                fig = go.Figure(go.Bar(
                    x=df_sorted['IND_PROD_INDEX'],
                    y=df_sorted['county_name'],
                    orientation='h',
                    marker_color=colors,
                    text=df_sorted['IND_PROD_INDEX'].apply(lambda x: f'{x:.1f}'),
                    textposition='outside'
                ))

                fig.add_vline(x=100, line_dash="dash", line_color="gray", annotation_text="Referință (100)")

                layout_defaults = get_plotly_layout_defaults()
                fig.update_layout(
                    xaxis_title="Indice",
                    yaxis_title="",
                    height=350,
                    **layout_defaults
                )

                st.plotly_chart(fig, use_container_width=True)

            st.markdown(chart_container_end(), unsafe_allow_html=True)

        with chart2:
            st.markdown(chart_container("Indicele Cifrei de Afaceri", "💰"), unsafe_allow_html=True)

            if 'IND_TURNOVER_INDEX' in df_latest.columns:
                df_sorted = df_latest.sort_values('IND_TURNOVER_INDEX', ascending=True)
                colors = [COLORS['error'] if x < 100 else COLORS['secondary'] for x in df_sorted['IND_TURNOVER_INDEX']]

                fig2 = go.Figure(go.Bar(
                    x=df_sorted['IND_TURNOVER_INDEX'],
                    y=df_sorted['county_name'],
                    orientation='h',
                    marker_color=colors,
                    text=df_sorted['IND_TURNOVER_INDEX'].apply(lambda x: f'{x:.1f}'),
                    textposition='outside'
                ))

                fig2.add_vline(x=100, line_dash="dash", line_color="gray", annotation_text="Referință (100)")

                layout_defaults = get_plotly_layout_defaults()
                fig2.update_layout(
                    xaxis_title="Indice",
                    yaxis_title="",
                    height=350,
                    **layout_defaults
                )

                st.plotly_chart(fig2, use_container_width=True)

            st.markdown(chart_container_end(), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Radar chart pentru comparație
        st.markdown(section_header("Comparație Județe", "🎯"), unsafe_allow_html=True)

        if 'IND_PROD_INDEX' in df_latest.columns and 'IND_TURNOVER_INDEX' in df_latest.columns:
            st.markdown(chart_container("Radar - Producție vs Cifră Afaceri", "🎯"), unsafe_allow_html=True)

            color_sequence = [COLORS['primary'], COLORS['primary_light'], COLORS['secondary'], COLORS['accent']]

            fig3 = go.Figure()

            for idx, (_, row) in enumerate(df_latest.iterrows()):
                fig3.add_trace(go.Scatterpolar(
                    r=[row['IND_PROD_INDEX'], row['IND_TURNOVER_INDEX'], row['IND_PROD_INDEX']],
                    theta=['Producție', 'Cifră Afaceri', 'Producție'],
                    fill='toself',
                    name=row['county_name'],
                    line=dict(color=color_sequence[idx % len(color_sequence)])
                ))

            fig3.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[50, 130])),
                height=450,
                legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter, sans-serif")
            )

            st.plotly_chart(fig3, use_container_width=True)
            st.markdown(chart_container_end(), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Evoluție în timp
        st.markdown(section_header("Evoluție Trimestrială", "📈"), unsafe_allow_html=True)

        df_evolution = df_pivot.sort_values(['year', 'quarter'])
        df_evolution['period'] = df_evolution['year'].astype(str) + ' T' + df_evolution['quarter'].astype(str)

        tab1, tab2 = st.tabs(["📈 Producție Industrială", "💰 Cifra de Afaceri"])

        layout_defaults = get_plotly_layout_defaults()
        color_sequence = [COLORS['primary'], COLORS['primary_light'], COLORS['secondary'], COLORS['accent']]

        with tab1:
            if 'IND_PROD_INDEX' in df_evolution.columns:
                fig4 = px.line(
                    df_evolution,
                    x='period',
                    y='IND_PROD_INDEX',
                    color='county_name',
                    markers=True,
                    color_discrete_sequence=color_sequence
                )
                fig4.add_hline(y=100, line_dash="dash", line_color="gray")
                fig4.update_layout(
                    xaxis_title="Perioadă",
                    yaxis_title="Indice Producție",
                    height=400,
                    legend_title="Județ",
                    **layout_defaults
                )
                st.plotly_chart(fig4, use_container_width=True)

        with tab2:
            if 'IND_TURNOVER_INDEX' in df_evolution.columns:
                fig5 = px.line(
                    df_evolution,
                    x='period',
                    y='IND_TURNOVER_INDEX',
                    color='county_name',
                    markers=True,
                    color_discrete_sequence=color_sequence
                )
                fig5.add_hline(y=100, line_dash="dash", line_color="gray")
                fig5.update_layout(
                    xaxis_title="Perioadă",
                    yaxis_title="Indice CA",
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
        if 'IND_PROD_INDEX' in df_display.columns:
            col_rename['IND_PROD_INDEX'] = 'Indice Producție'
        if 'IND_TURNOVER_INDEX' in df_display.columns:
            col_rename['IND_TURNOVER_INDEX'] = 'Indice CA'

        df_display = df_display.rename(columns=col_rename)

        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Download
        col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 2])
        with col_dl1:
            csv = df_pivot.to_csv(index=False)
            st.download_button(
                label="📥 Descarcă CSV",
                data=csv,
                file_name=f"indicatori_industrie_{selected_year}.csv",
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
