"""
Pagina Export Date - Exportă datele în diverse formate
"""

import streamlit as st
import pandas as pd
import io
import os
import sys
if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import require_auth
from styles import init_page_style, page_header, section_header, COLORS

st.set_page_config(page_title="Export Date", page_icon="📥", layout="wide")

# Verifică autentificarea
require_auth()

# Aplică stilurile moderne
init_page_style(st)

# Header pagină
st.markdown(page_header(
    "Export Date",
    "Descarcă datele statistice în diferite formate",
    "📥"
), unsafe_allow_html=True)

try:
    from db_utils import (
        export_all_data,
        get_salary_comparison,
        get_labor_market_data,
        get_industry_indices,
        get_all_indicators,
        get_counties,
        get_available_years
    )

    st.markdown("---")

    # Info
    st.info("""
    **Formate disponibile:**
    - **CSV** - Compatibil cu Excel, Google Sheets, R, Python
    - **Excel** - Format nativ Microsoft Excel (.xlsx)
    - **JSON** - Pentru aplicații web și API-uri
    """)

    # Statistici generale
    st.subheader("📊 Date Disponibile")

    col1, col2, col3 = st.columns(3)

    indicators_df = get_all_indicators()
    counties_df = get_counties()
    years = get_available_years()

    with col1:
        st.metric("Indicatori", len(indicators_df))

    with col2:
        st.metric("Județe", len(counties_df))

    with col3:
        if years:
            st.metric("Perioadă", f"{min(years)} - {max(years)}")

    st.markdown("---")

    # Export complet
    st.subheader("📦 Export Complet")

    st.write("Descarcă toate datele disponibile într-un singur fișier.")

    if st.button("🔄 Generează Export Complet", type="primary"):
        st.session_state["export_complete_generated"] = True

    if st.session_state.get("export_complete_generated", False):
        df_all = export_all_data()

        if not df_all.empty:
            st.success(f"✅ Export generat: {len(df_all)} înregistrări")

            # CSV
            csv_data = df_all.to_csv(index=False)
            st.download_button(
                label="📥 Descarcă CSV",
                data=csv_data,
                file_name="date_complete_regiunea_vest.csv",
                mime="text/csv",
                key="export_complete_csv"
            )

            # Excel
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df_all.to_excel(writer, index=False, sheet_name='Date')
            excel_data = excel_buffer.getvalue()

            st.download_button(
                label="📥 Descarcă Excel",
                data=excel_data,
                file_name="date_complete_regiunea_vest.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="export_complete_excel"
            )

            # JSON
            json_data = df_all.to_json(orient='records', force_ascii=False, indent=2)
            st.download_button(
                label="📥 Descarcă JSON",
                data=json_data,
                file_name="date_complete_regiunea_vest.json",
                mime="application/json",
                key="export_complete_json"
            )

            # Preview
            with st.expander("👁️ Previzualizare date"):
                st.dataframe(df_all.head(100), use_container_width=True, hide_index=True)
        else:
            st.warning("Nu există date pentru export.")

    st.markdown("---")

    # Export pe categorii
    st.subheader("📂 Export pe Categorii")

    tab1, tab2, tab3, tab4 = st.tabs(["💰 Salarii", "👷 Piața Muncii", "🏭 Industrie", "📋 Indicatori"])

    with tab1:
        st.write("Exportă datele despre salarii (brut și net)")

        year_filter = st.selectbox("Filtrează după an", [None] + years, format_func=lambda x: "Toți anii" if x is None else x, key="salary_year")

        if st.button("Generează export salarii"):
            st.session_state["export_salary_generated"] = True

        if st.session_state.get("export_salary_generated", False):
            df_salary = get_salary_comparison(year_filter)
            if not df_salary.empty:
                df_pivot = df_salary.pivot_table(
                    index=['county_name', 'year', 'quarter'],
                    columns='indicator_code',
                    values='value'
                ).reset_index()

                csv = df_pivot.to_csv(index=False)
                st.download_button(
                    label="📥 Descarcă CSV Salarii",
                    data=csv,
                    file_name="salarii_regiunea_vest.csv",
                    mime="text/csv",
                    key="export_salary_csv"
                )

                st.dataframe(df_pivot.head(20), use_container_width=True, hide_index=True)
            else:
                st.warning("Nu există date despre salarii.")

    with tab2:
        st.write("Exportă datele despre piața muncii (șomaj, angajați)")

        year_filter2 = st.selectbox("Filtrează după an", [None] + years, format_func=lambda x: "Toți anii" if x is None else x, key="labor_year")

        if st.button("Generează export piața muncii"):
            st.session_state["export_labor_generated"] = True

        if st.session_state.get("export_labor_generated", False):
            df_labor = get_labor_market_data(year_filter2)
            if not df_labor.empty:
                df_pivot = df_labor.pivot_table(
                    index=['county_name', 'year', 'quarter'],
                    columns='indicator_code',
                    values='value'
                ).reset_index()

                csv = df_pivot.to_csv(index=False)
                st.download_button(
                    label="📥 Descarcă CSV Piața Muncii",
                    data=csv,
                    file_name="piata_muncii_regiunea_vest.csv",
                    mime="text/csv",
                    key="export_labor_csv"
                )

                st.dataframe(df_pivot.head(20), use_container_width=True, hide_index=True)
            else:
                st.warning("Nu există date despre piața muncii.")

    with tab3:
        st.write("Exportă datele despre indicii industriali")

        year_filter3 = st.selectbox("Filtrează după an", [None] + years, format_func=lambda x: "Toți anii" if x is None else x, key="industry_year")

        if st.button("Generează export industrie"):
            st.session_state["export_industry_generated"] = True

        if st.session_state.get("export_industry_generated", False):
            df_industry = get_industry_indices(year_filter3)
            if not df_industry.empty:
                df_pivot = df_industry.pivot_table(
                    index=['county_name', 'year', 'quarter'],
                    columns='indicator_code',
                    values='value'
                ).reset_index()

                csv = df_pivot.to_csv(index=False)
                st.download_button(
                    label="📥 Descarcă CSV Industrie",
                    data=csv,
                    file_name="industrie_regiunea_vest.csv",
                    mime="text/csv",
                    key="export_industry_csv"
                )

                st.dataframe(df_pivot.head(20), use_container_width=True, hide_index=True)
            else:
                st.warning("Nu există date despre industrie.")

    with tab4:
        st.write("Lista tuturor indicatorilor disponibili")

        if not indicators_df.empty:
            df_display = indicators_df.copy()
            df_display.columns = ['Cod', 'Nume', 'Categorie', 'Unitate', 'Nr. Valori', 'An Min', 'An Max']

            csv = df_display.to_csv(index=False)
            st.download_button(
                label="📥 Descarcă Lista Indicatori",
                data=csv,
                file_name="lista_indicatori.csv",
                mime="text/csv"
            )

            st.dataframe(df_display, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Export personalizat
    st.subheader("🎯 Export Personalizat")

    st.write("Construiește un export personalizat selectând indicatorii și filtrele dorite.")

    col1, col2 = st.columns(2)

    with col1:
        selected_indicators = st.multiselect(
            "Selectează indicatorii",
            options=list(indicators_df['code']),
            format_func=lambda x: indicators_df[indicators_df['code'] == x]['name'].values[0]
        )

    with col2:
        selected_counties = st.multiselect(
            "Selectează județele",
            options=list(counties_df['code']),
            format_func=lambda x: counties_df[counties_df['code'] == x]['name'].values[0],
            default=list(counties_df['code'])
        )

    year_range = st.slider(
        "Selectează perioada",
        min_value=min(years) if years else 2023,
        max_value=max(years) if years else 2025,
        value=(min(years) if years else 2023, max(years) if years else 2025)
    )

    if st.button("🔄 Generează Export Personalizat", type="primary"):
        if selected_indicators:
            st.session_state["export_custom_generated"] = True
        else:
            st.warning("Selectează cel puțin un indicator.")

    if st.session_state.get("export_custom_generated", False) and selected_indicators:
        df_all = export_all_data()

        # Filtrare
        df_filtered = df_all[
            (df_all['cod_indicator'].isin(selected_indicators)) &
            (df_all['cod_judet'].isin(selected_counties)) &
            (df_all['an'] >= year_range[0]) &
            (df_all['an'] <= year_range[1])
        ]

        if not df_filtered.empty:
            st.success(f"✅ {len(df_filtered)} înregistrări selectate")

            csv = df_filtered.to_csv(index=False)
            st.download_button(
                label="📥 Descarcă Export Personalizat",
                data=csv,
                file_name="export_personalizat.csv",
                mime="text/csv",
                key="export_custom_csv"
            )

            st.dataframe(df_filtered, use_container_width=True, hide_index=True)
        else:
            st.warning("Nu există date pentru selecția făcută.")

except Exception as e:
    st.error(f"Eroare la încărcarea datelor: {str(e)}")
    st.info("Asigurați-vă că baza de date este configurată corect și conține date.")

# Footer
st.markdown("""
<div class="app-footer">
    <p style="margin: 0;">© 2025 Vest Policy Lab - Automotive Vest Analytics</p>
</div>
""", unsafe_allow_html=True)
