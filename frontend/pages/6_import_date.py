"""
Pagina Import Date - Upload documente
Suport pentru PDF, CSV, Excel
Import din folder server sau upload fișiere
"""

import streamlit as st
import pandas as pd
import io
import re
import os
from pathlib import Path
import sys
if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import require_auth, show_user_info

st.set_page_config(page_title="Import Date", page_icon="📤", layout="wide")

# Verifică autentificarea
require_auth()
show_user_info()

st.title("📤 Import Date")
st.markdown("Încarcă documente pentru a extrage și importa date în sistem")

# Folder implicit pentru import de pe server
DEFAULT_IMPORT_FOLDER = os.environ.get("IMPORT_FOLDER", "/app/data/import")
ALLOWED_EXTENSIONS = {".pdf", ".csv", ".xlsx", ".xls"}

# Formate acceptate
ALLOWED_FORMATS = {
    "pdf": "application/pdf",
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xls": "application/vnd.ms-excel"
}

def extract_text_from_pdf(uploaded_file):
    """Extrage text din fișier PDF"""
    try:
        import pdfplumber

        text_content = []
        tables = []

        with pdfplumber.open(uploaded_file) as pdf:
            for i, page in enumerate(pdf.pages):
                # Extrage text
                page_text = page.extract_text()
                if page_text:
                    text_content.append(f"--- Pagina {i+1} ---\n{page_text}")

                # Extrage tabele
                page_tables = page.extract_tables()
                for table in page_tables:
                    if table:
                        tables.append(table)

        return {
            "text": "\n\n".join(text_content),
            "tables": tables,
            "num_pages": len(pdf.pages) if 'pdf' in dir() else 0
        }
    except ImportError:
        st.error("Biblioteca pdfplumber nu este instalată. Rulează: pip install pdfplumber")
        return None
    except Exception as e:
        st.error(f"Eroare la citirea PDF-ului: {str(e)}")
        return None

def extract_numbers_from_text(text):
    """Extrage numere din text"""
    # Pattern pentru numere (inclusiv cu virgulă/punct pentru decimale)
    numbers = re.findall(r'\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?\b', text)

    # Curăță și convertește
    cleaned_numbers = []
    for num in numbers:
        # Înlocuiește formatul european (1.234,56) cu format standard
        if ',' in num and '.' in num:
            if num.rindex(',') > num.rindex('.'):
                num = num.replace('.', '').replace(',', '.')
            else:
                num = num.replace(',', '')
        elif ',' in num:
            num = num.replace(',', '.')

        try:
            cleaned_numbers.append(float(num))
        except ValueError:
            continue

    return cleaned_numbers

def process_csv(uploaded_file):
    """Procesează fișier CSV"""
    try:
        df = pd.read_csv(uploaded_file)
        return df
    except Exception as e:
        st.error(f"Eroare la citirea CSV: {str(e)}")
        return None

def process_excel(uploaded_file):
    """Procesează fișier Excel"""
    try:
        df = pd.read_excel(uploaded_file)
        return df
    except Exception as e:
        st.error(f"Eroare la citirea Excel: {str(e)}")
        return None

def scan_folder(folder_path, recursive=False):
    """Scanează un folder și returnează lista de fișiere compatibile"""
    files_found = []
    folder = Path(folder_path)

    if not folder.exists():
        return [], f"Folderul '{folder_path}' nu există"

    if not folder.is_dir():
        return [], f"'{folder_path}' nu este un folder"

    try:
        if recursive:
            for file_path in folder.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in ALLOWED_EXTENSIONS:
                    files_found.append(file_path)
        else:
            for file_path in folder.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in ALLOWED_EXTENSIONS:
                    files_found.append(file_path)

        return sorted(files_found, key=lambda x: x.name), None
    except PermissionError:
        return [], f"Nu ai permisiuni pentru a accesa '{folder_path}'"
    except Exception as e:
        return [], f"Eroare la scanarea folderului: {str(e)}"

def process_file_from_path(file_path):
    """Procesează un fișier de pe disk după path"""
    extension = file_path.suffix.lower()

    try:
        if extension == ".pdf":
            with open(file_path, "rb") as f:
                return extract_text_from_pdf(f), "pdf"
        elif extension == ".csv":
            df = pd.read_csv(file_path)
            return df, "csv"
        elif extension in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path)
            return df, "excel"
    except Exception as e:
        st.error(f"Eroare la procesarea {file_path.name}: {str(e)}")
        return None, None

def get_file_size_str(file_path):
    """Returnează dimensiunea fișierului formatată"""
    size = file_path.stat().st_size
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / (1024 * 1024):.1f} MB"

# Tabs pentru diferite moduri de import
tab1, tab2, tab3 = st.tabs(["📁 Upload Fișier", "🗂️ Import din Folder Server", "📋 Istoric Import"])

with tab1:
    st.subheader("Încarcă Document")

    # Info despre formate acceptate
    st.info("""
    **Formate acceptate:**
    - **PDF** (.pdf) - Extrage text și tabele din documente PDF
    - **CSV** (.csv) - Import date tabelare
    - **Excel** (.xlsx, .xls) - Import date din foi de calcul
    """)

    # Upload widget
    uploaded_files = st.file_uploader(
        "Trage fișierele aici sau click pentru a le selecta",
        type=["pdf", "csv", "xlsx", "xls"],
        help="Formate acceptate: PDF, CSV, Excel",
        accept_multiple_files=True
    )

    if uploaded_files:
        st.markdown(f"### 📄 Fișiere încărcate ({len(uploaded_files)})")
        
        # Batch actions
        if len(uploaded_files) > 1:
            if st.button("💾 Importă TOATE datele", type="primary", key="batch_import"):
                st.success(f"Toate cele {len(uploaded_files)} fișiere au fost importate cu succes!")
                st.balloons()
            st.markdown("---")

        for uploaded_file in uploaded_files:
            file_extension = uploaded_file.name.split(".")[-1].lower()
            
            with st.expander(f"🔍 Detalii: {uploaded_file.name}", expanded=(len(uploaded_files) == 1)):
                st.info(f"Mărime: {uploaded_file.size / 1024:.1f} KB | Tip: {file_extension.upper()}")

                # Procesare în funcție de tip
                if file_extension == "pdf":
                    st.subheader("📄 Conținut PDF")

                    with st.spinner(f"Se procesează {uploaded_file.name}..."):
                        result = extract_text_from_pdf(uploaded_file)

                    if result:
                        col1, col2 = st.columns([2, 1])

                        with col1:
                            st.markdown("### Text Extras")
                            st.text_area(
                                f"Conținut text - {uploaded_file.name}",
                                value=result["text"],
                                height=200,
                                disabled=True,
                                key=f"text_{uploaded_file.name}"
                            )

                        with col2:
                            st.markdown("### Statistici")
                            st.metric("Pagini", result.get("num_pages", "N/A"))
                            st.metric("Caractere", len(result["text"]))
                            
                            # Extrage numere
                            numbers = extract_numbers_from_text(result["text"])
                            st.metric("Numere găsite", len(numbers))

                        # Tabele extrase
                        if result["tables"]:
                            st.markdown("### Tabele Extrase")
                            for i, table in enumerate(result["tables"]):
                                try:
                                    df = pd.DataFrame(table[1:], columns=table[0] if table[0] else None)
                                    st.dataframe(df, use_container_width=True, key=f"table_{uploaded_file.name}_{i}")
                                except Exception:
                                    st.write(table)

                        if st.button(f"💾 Salvează datele din {uploaded_file.name}", key=f"save_{uploaded_file.name}"):
                            st.success(f"Datele din {uploaded_file.name} au fost salvate!")

                elif file_extension == "csv":
                    st.subheader("📊 Conținut CSV")
                    df = process_csv(uploaded_file)
                    if df is not None:
                        st.dataframe(df, use_container_width=True, key=f"df_{uploaded_file.name}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Rânduri", len(df))
                        with col2:
                            st.metric("Coloane", len(df.columns))

                        if st.button(f"💾 Importă {uploaded_file.name}", key=f"import_{uploaded_file.name}"):
                            st.success(f"Datele din {uploaded_file.name} au fost importate!")

                elif file_extension in ["xlsx", "xls"]:
                    st.subheader("📊 Conținut Excel")
                    df = process_excel(uploaded_file)
                    if df is not None:
                        st.dataframe(df, use_container_width=True, key=f"df_{uploaded_file.name}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Rânduri", len(df))
                        with col2:
                            st.metric("Coloane", len(df.columns))

                        if st.button(f"💾 Importă {uploaded_file.name}", key=f"import_{uploaded_file.name}"):
                            st.success(f"Datele din {uploaded_file.name} au fost importate!")

with tab2:
    st.subheader("🗂️ Import din Folder Server")

    st.info("""
    **Import fișiere direct de pe server**

    Specifică un folder de pe server pentru a importa toate fișierele compatibile.
    Formate acceptate: PDF, CSV, Excel (.xlsx, .xls)
    """)

    col1, col2 = st.columns([3, 1])

    with col1:
        folder_path = st.text_input(
            "📂 Calea către folder",
            value=DEFAULT_IMPORT_FOLDER,
            help="Introdu calea completă către folderul de pe server",
            placeholder="/app/data/import"
        )

    with col2:
        recursive = st.checkbox("🔄 Recursiv", value=False, help="Scanează și subfolderele")

    if st.button("🔍 Scanează Folder", type="primary"):
        if folder_path:
            with st.spinner(f"Se scanează {folder_path}..."):
                files, error = scan_folder(folder_path, recursive)

            if error:
                st.error(error)
            elif not files:
                st.warning(f"Nu s-au găsit fișiere compatibile în '{folder_path}'")
            else:
                st.session_state["scanned_files"] = files
                st.session_state["scanned_folder"] = folder_path
                st.success(f"S-au găsit {len(files)} fișiere compatibile!")

    # Afișare fișiere găsite
    if "scanned_files" in st.session_state and st.session_state["scanned_files"]:
        files = st.session_state["scanned_files"]
        folder = st.session_state.get("scanned_folder", "")

        st.markdown(f"### 📄 Fișiere găsite în `{folder}` ({len(files)})")

        # Tabel cu fișierele găsite
        files_data = []
        for f in files:
            files_data.append({
                "Nume": f.name,
                "Tip": f.suffix.upper().replace(".", ""),
                "Dimensiune": get_file_size_str(f),
                "Cale": str(f.parent)
            })

        files_df = pd.DataFrame(files_data)
        st.dataframe(files_df, use_container_width=True, hide_index=True)

        # Selectare fișiere pentru import
        st.markdown("### Selectează fișierele pentru import")

        select_all = st.checkbox("✅ Selectează toate", value=True)

        selected_files = []
        if not select_all:
            selected_names = st.multiselect(
                "Alege fișierele",
                options=[f.name for f in files],
                default=[f.name for f in files]
            )
            selected_files = [f for f in files if f.name in selected_names]
        else:
            selected_files = files

        st.markdown(f"**{len(selected_files)}** fișiere selectate pentru import")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("👁️ Previzualizează", disabled=len(selected_files) == 0):
                st.session_state["preview_files"] = selected_files

        with col2:
            if st.button("💾 Importă Selectate", type="primary", disabled=len(selected_files) == 0):
                progress_bar = st.progress(0)
                status_text = st.empty()

                imported_count = 0
                errors = []

                for i, file_path in enumerate(selected_files):
                    status_text.text(f"Se procesează: {file_path.name}")
                    progress_bar.progress((i + 1) / len(selected_files))

                    result, file_type = process_file_from_path(file_path)
                    if result is not None:
                        imported_count += 1
                    else:
                        errors.append(file_path.name)

                progress_bar.empty()
                status_text.empty()

                if imported_count > 0:
                    st.success(f"✅ S-au importat cu succes {imported_count} fișiere!")

                if errors:
                    st.warning(f"⚠️ Nu s-au putut procesa: {', '.join(errors)}")

                st.balloons()

        # Previzualizare fișiere
        if "preview_files" in st.session_state and st.session_state["preview_files"]:
            st.markdown("---")
            st.markdown("### 👁️ Previzualizare")

            for file_path in st.session_state["preview_files"][:5]:  # Limită la 5 pentru performanță
                with st.expander(f"📄 {file_path.name}", expanded=False):
                    result, file_type = process_file_from_path(file_path)

                    if result is None:
                        st.error("Nu s-a putut procesa fișierul")
                        continue

                    if file_type == "pdf":
                        if result.get("text"):
                            st.text_area("Text extras", result["text"][:2000] + "..." if len(result["text"]) > 2000 else result["text"], height=150, disabled=True)
                        if result.get("tables"):
                            st.write(f"Tabele găsite: {len(result['tables'])}")
                    elif file_type in ["csv", "excel"]:
                        st.dataframe(result.head(10), use_container_width=True)
                        st.caption(f"Afișate primele 10 rânduri din {len(result)}")

            if len(st.session_state["preview_files"]) > 5:
                st.info(f"Se afișează previzualizare pentru primele 5 fișiere din {len(st.session_state['preview_files'])}")

with tab3:
    st.subheader("Istoric Import")

    # Istoric simulat
    history_data = pd.DataFrame({
        "Data": ["2024-01-20", "2024-01-18", "2024-01-15", "2024-01-10"],
        "Fișier": ["raport_q4.pdf", "date_angajati.csv", "export_eurostat.xlsx", "analiza_sector.pdf"],
        "Tip": ["PDF", "CSV", "Excel", "PDF"],
        "Dimensiune": ["2.4 MB", "156 KB", "890 KB", "1.8 MB"],
        "Status": ["✅ Procesat", "✅ Importat", "✅ Importat", "✅ Procesat"]
    })

    st.dataframe(history_data, use_container_width=True, hide_index=True)
