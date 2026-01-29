"""
Pagina Rapoarte și Export
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os
import sys
if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import require_auth, show_user_info

st.set_page_config(page_title="Rapoarte", page_icon="📄", layout="wide")

# Verifică autentificarea
require_auth()
show_user_info()

st.title("📄 Rapoarte și Export")
st.markdown("Generare rapoarte și export date")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Generare Raport", "📥 Export Date", "📋 Rapoarte Salvate"])

with tab1:
    st.subheader("Generare Raport Personalizat")

    col1, col2 = st.columns(2)

    with col1:
        report_type = st.selectbox(
            "Tip raport",
            [
                "Raport Trimestrial Sumar",
                "Raport Anual Complet",
                "Comparație Județe",
                "Analiză Tendințe",
                "Dashboard KPI",
                "Raport Personalizat"
            ]
        )

        report_title = st.text_input(
            "Titlu raport",
            value=f"Raport Automotive Vest - {datetime.now().strftime('%B %Y')}"
        )

        year = st.selectbox("An de referință", range(2023, 2009, -1))

    with col2:
        counties = st.multiselect(
            "Județe incluse",
            ["Timiș", "Arad", "Hunedoara", "Caraș-Severin"],
            default=["Timiș", "Arad", "Hunedoara", "Caraș-Severin"]
        )

        indicators = st.multiselect(
            "Indicatori incluși",
            [
                "Număr angajați",
                "Cifră de afaceri",
                "Export",
                "Productivitate",
                "Număr firme",
                "Investiții",
                "R&D"
            ],
            default=["Număr angajați", "Cifră de afaceri", "Export"]
        )

        include_charts = st.checkbox("Include grafice", value=True)
        include_map = st.checkbox("Include hartă", value=True)
        include_forecast = st.checkbox("Include proiecții", value=False)

    st.markdown("---")

    # Preview
    st.subheader("Preview Raport")

    with st.expander("Vezi structura raportului", expanded=True):
        st.markdown(f"""
        ## {report_title}

        **Data generării:** {datetime.now().strftime('%d %B %Y, %H:%M')}

        **Parametri:**
        - Tip: {report_type}
        - An: {year}
        - Județe: {', '.join(counties)}

        ---

        ### 1. Sumar Executiv
        Acest raport prezintă situația sectorului automotive din Regiunea Vest
        pentru anul {year}, cu focus pe indicatorii selectați.

        ### 2. Indicatori Cheie
        {''.join([f'- {ind}' + chr(10) for ind in indicators])}

        ### 3. Analiză pe Județe
        {'Grafice comparative între județe' if include_charts else 'Tabel comparativ'}

        {'### 4. Hartă Distribuție' if include_map else ''}
        {'Vizualizare geografică a indicatorilor' if include_map else ''}

        {'### 5. Proiecții 2024-2030' if include_forecast else ''}
        {'Scenarii de evoluție (optimist, bază, pesimist)' if include_forecast else ''}

        ### {'6' if include_forecast else '4' if not include_map else '5'}. Concluzii și Recomandări

        ---
        *Raport generat automat de Automotive Vest Analytics*
        """)

    col_btn1, col_btn2, col_btn3 = st.columns(3)

    with col_btn1:
        if st.button("📄 Generează PDF", type="primary", use_container_width=True):
            with st.spinner("Se generează raportul PDF..."):
                import time
                time.sleep(2)
                st.success("Raport PDF generat cu succes!")
                st.download_button(
                    "⬇️ Descarcă PDF",
                    data=b"PDF content placeholder",
                    file_name=f"raport_automotive_{year}.pdf",
                    mime="application/pdf"
                )

    with col_btn2:
        if st.button("📊 Generează DOCX", use_container_width=True):
            st.info("Funcționalitate în dezvoltare")

    with col_btn3:
        if st.button("📑 Generează PPTX", use_container_width=True):
            st.info("Funcționalitate în dezvoltare")

with tab2:
    st.subheader("Export Date")

    export_format = st.radio(
        "Format export",
        ["Excel (.xlsx)", "CSV", "JSON"],
        horizontal=True
    )

    col1, col2 = st.columns(2)

    with col1:
        export_indicators = st.multiselect(
            "Indicatori de exportat",
            [
                "TOTAL_EMPLOYEES",
                "TOTAL_TURNOVER",
                "TOTAL_EXPORTS",
                "PRODUCTIVITY",
                "TOTAL_COMPANIES",
                "AVG_SALARY",
                "RD_EXPENDITURE"
            ],
            default=["TOTAL_EMPLOYEES", "TOTAL_TURNOVER"]
        )

    with col2:
        export_years = st.slider(
            "Perioada",
            min_value=2010,
            max_value=2023,
            value=(2019, 2023)
        )

        export_level = st.selectbox(
            "Nivel agregare",
            ["Regional", "Pe județe", "Ambele"]
        )

    # Generare date pentru export
    if st.button("Pregătește datele pentru export"):
        # Sample data
        years = list(range(export_years[0], export_years[1] + 1))

        if export_level == "Pe județe":
            data_rows = []
            for year in years:
                for county in ["Timiș", "Arad", "Hunedoara", "Caraș-Severin"]:
                    row = {"An": year, "Județ": county}
                    if "TOTAL_EMPLOYEES" in export_indicators:
                        row["Angajați"] = 30000 + year * 100 + (hash(county) % 10000)
                    if "TOTAL_TURNOVER" in export_indicators:
                        row["CA (mil EUR)"] = 2000 + year * 50 + (hash(county) % 3000)
                    data_rows.append(row)
            export_df = pd.DataFrame(data_rows)
        else:
            data_rows = []
            for year in years:
                row = {"An": year, "Regiune": "Vest"}
                if "TOTAL_EMPLOYEES" in export_indicators:
                    row["Angajați"] = 50000 + (year - 2010) * 1500
                if "TOTAL_TURNOVER" in export_indicators:
                    row["CA (mil EUR)"] = 7000 + (year - 2010) * 500
                data_rows.append(row)
            export_df = pd.DataFrame(data_rows)

        st.dataframe(export_df, use_container_width=True)

        # Export buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            # Excel
            buffer = io.BytesIO()
            export_df.to_excel(buffer, index=False, engine='openpyxl')
            buffer.seek(0)

            st.download_button(
                "⬇️ Descarcă Excel",
                data=buffer,
                file_name=f"automotive_vest_{export_years[0]}_{export_years[1]}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with col2:
            # CSV
            csv_data = export_df.to_csv(index=False)
            st.download_button(
                "⬇️ Descarcă CSV",
                data=csv_data,
                file_name=f"automotive_vest_{export_years[0]}_{export_years[1]}.csv",
                mime="text/csv"
            )

        with col3:
            # JSON
            json_data = export_df.to_json(orient="records", indent=2)
            st.download_button(
                "⬇️ Descarcă JSON",
                data=json_data,
                file_name=f"automotive_vest_{export_years[0]}_{export_years[1]}.json",
                mime="application/json"
            )

with tab3:
    st.subheader("Rapoarte Generate Anterior")

    # Lista de rapoarte simulate
    saved_reports = pd.DataFrame({
        "Data": ["2024-01-15", "2024-01-10", "2023-12-20", "2023-12-01", "2023-11-15"],
        "Tip": ["Trimestrial", "KPI Dashboard", "Anual Complet", "Comparație", "Tendințe"],
        "Titlu": [
            "Raport Q4 2023",
            "Dashboard KPI Ianuarie",
            "Raport Anual 2023",
            "Comparație Județe Q3",
            "Analiză Tendințe 2019-2023"
        ],
        "Format": ["PDF", "PDF", "PDF", "XLSX", "PDF"],
        "Dimensiune": ["2.4 MB", "1.8 MB", "5.2 MB", "0.8 MB", "3.1 MB"]
    })

    # Afișare tabel cu acțiuni
    for idx, row in saved_reports.iterrows():
        col1, col2, col3, col4, col5 = st.columns([2, 1, 3, 1, 2])

        with col1:
            st.text(row["Data"])
        with col2:
            st.text(row["Tip"])
        with col3:
            st.text(row["Titlu"])
        with col4:
            st.text(row["Format"])
        with col5:
            if st.button("⬇️ Descarcă", key=f"download_{idx}"):
                st.info("Download simulat")

    st.markdown("---")

    # Programare rapoarte automate
    st.subheader("Rapoarte Programate")

    with st.expander("Configurare rapoarte automate"):
        st.markdown("""
        Configurează generarea automată de rapoarte pe bază de programare:
        """)

        auto_type = st.selectbox(
            "Tip raport automat",
            ["Raport Trimestrial", "Dashboard Lunar", "Alertă Indicatori"]
        )

        frequency = st.selectbox(
            "Frecvență",
            ["Lunar", "Trimestrial", "Săptămânal"]
        )

        recipients = st.text_input(
            "Destinatari email (separați prin virgulă)",
            "admin@example.com"
        )

        if st.button("Salvează programare"):
            st.success(f"Raport programat: {auto_type} - {frequency}")
