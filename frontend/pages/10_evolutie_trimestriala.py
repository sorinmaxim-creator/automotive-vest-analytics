"""
Pagina Evoluție Trimestrială - Tendințe pe trimestre
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

st.set_page_config(page_title="Evoluție Trimestrială", page_icon="📅", layout="wide")

# Verifică autentificarea
require_auth()
show_user_info()

st.title("📅 Evoluție Trimestrială")
st.markdown("Analiză detaliată a tendințelor pe trimestre pentru toți indicatorii")

try:
    from db_utils import get_quarterly_evolution, get_all_indicators, get_counties

    # Obține lista de indicatori și județe
    indicators_df = get_all_indicators()
    counties_df = get_counties()

    # Filtre
    col1, col2 = st.columns(2)

    with col1:
        indicator_options = dict(zip(indicators_df['name'], indicators_df['code']))
        selected_indicator_name = st.selectbox("Selectează indicatorul", list(indicator_options.keys()))
        selected_indicator = indicator_options[selected_indicator_name]

    with col2:
        county_options = {"Toate județele": None}
        county_options.update(dict(zip(counties_df['name'], counties_df['code'])))
        selected_county_name = st.selectbox("Selectează județul", list(county_options.keys()))
        selected_county = county_options[selected_county_name]

    # Obține datele
    df = get_quarterly_evolution(selected_indicator, selected_county)

    if df.empty:
        st.warning("Nu există date pentru selecția făcută.")
    else:
        st.markdown("---")

        # Statistici
        st.subheader("📊 Statistici")

        stats1, stats2, stats3, stats4 = st.columns(4)

        with stats1:
            st.metric("Valoare Minimă", f"{df['value'].min():,.1f}")

        with stats2:
            st.metric("Valoare Maximă", f"{df['value'].max():,.1f}")

        with stats3:
            st.metric("Medie", f"{df['value'].mean():,.1f}")

        with stats4:
            # Calculează variația
            if len(df) > 1:
                first_val = df.iloc[0]['value']
                last_val = df.iloc[-1]['value']
                variation = ((last_val - first_val) / first_val) * 100 if first_val != 0 else 0
                st.metric("Variație totală", f"{variation:+.1f}%")
            else:
                st.metric("Variație totală", "N/A")

        st.markdown("---")

        # Grafic principal
        st.subheader(f"📈 Evoluție: {selected_indicator_name}")

        if selected_county:
            # Grafic pentru un singur județ
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df['period'],
                y=df['value'],
                mode='lines+markers',
                name=selected_county_name,
                line=dict(width=3, color='#1E3A5F'),
                marker=dict(size=10)
            ))

            # Adaugă trend line
            if len(df) > 2:
                z = pd.np.polyfit(range(len(df)), df['value'], 1) if hasattr(pd, 'np') else None
                if z is not None:
                    p = pd.np.poly1d(z)
                    fig.add_trace(go.Scatter(
                        x=df['period'],
                        y=p(range(len(df))),
                        mode='lines',
                        name='Trend',
                        line=dict(dash='dash', color='#E63946')
                    ))

            fig.update_layout(
                xaxis_title="Perioadă",
                yaxis_title="Valoare",
                height=450,
                hovermode='x unified'
            )

        else:
            # Grafic pentru toate județele
            fig = px.line(
                df,
                x='period',
                y='value',
                color='county_name',
                markers=True,
                line_shape='linear'
            )

            fig.update_layout(
                xaxis_title="Perioadă",
                yaxis_title="Valoare",
                height=450,
                legend_title="Județ",
                hovermode='x unified'
            )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Comparație pe trimestre
        st.subheader("🔄 Comparație pe Trimestre")

        # Pivot pentru comparație
        df_quarter = df.copy()
        df_quarter['quarter_label'] = 'T' + df_quarter['quarter'].astype(str)

        if not selected_county:
            # Heatmap pentru toate județele
            df_heatmap = df_quarter.pivot_table(
                index='county_name',
                columns='period',
                values='value',
                aggfunc='mean'
            )

            fig2 = px.imshow(
                df_heatmap,
                labels=dict(x="Perioadă", y="Județ", color="Valoare"),
                color_continuous_scale="RdYlGn",
                aspect="auto"
            )

            fig2.update_layout(height=300)
            st.plotly_chart(fig2, use_container_width=True)

        # Box plot pentru distribuție
        st.subheader("📦 Distribuție pe Trimestre")

        fig3 = px.box(
            df_quarter,
            x='quarter_label',
            y='value',
            color='quarter_label',
            points='all'
        )

        fig3.update_layout(
            xaxis_title="Trimestru",
            yaxis_title="Valoare",
            height=350,
            showlegend=False
        )

        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("---")

        # Variații trimestriale
        st.subheader("📊 Variații Trimestriale")

        # Calculează variațiile
        if not selected_county:
            for county in df['county_name'].unique():
                county_data = df[df['county_name'] == county].sort_values('period')
                if len(county_data) > 1:
                    county_data['variation'] = county_data['value'].pct_change() * 100
                    df.loc[df['county_name'] == county, 'variation'] = county_data['variation'].values
        else:
            df = df.sort_values('period')
            df['variation'] = df['value'].pct_change() * 100

        if 'variation' in df.columns:
            df_var = df.dropna(subset=['variation'])

            if not df_var.empty:
                fig4 = px.bar(
                    df_var,
                    x='period',
                    y='variation',
                    color='county_name' if not selected_county else None,
                    barmode='group',
                    color_discrete_sequence=px.colors.qualitative.Set2
                )

                fig4.add_hline(y=0, line_dash="dash", line_color="gray")

                fig4.update_layout(
                    xaxis_title="Perioadă",
                    yaxis_title="Variație (%)",
                    height=350,
                    legend_title="Județ" if not selected_county else None
                )

                st.plotly_chart(fig4, use_container_width=True)

        st.markdown("---")

        # Tabel detaliat
        st.subheader("📋 Date Detaliate")

        df_display = df[['county_name', 'year', 'quarter', 'period', 'value']].copy()
        df_display.columns = ['Județ', 'An', 'Trimestru', 'Perioadă', 'Valoare']

        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # Download
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Descarcă CSV",
            data=csv,
            file_name=f"evolutie_{selected_indicator}.csv",
            mime="text/csv"
        )

except Exception as e:
    st.error(f"Eroare la încărcarea datelor: {str(e)}")
    st.info("Asigurați-vă că baza de date este configurată corect și conține date.")
