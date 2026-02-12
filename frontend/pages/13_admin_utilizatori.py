"""
Pagina Administrare Utilizatori
Gestionare conturi, roluri și permisiuni
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys
if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import require_auth, require_role, get_current_user, hash_password
from styles import init_page_style, page_header, section_header, COLORS

st.set_page_config(page_title="Administrare Utilizatori", page_icon="👥", layout="wide")

# Verifică autentificarea
require_auth()

# Verifică dacă utilizatorul este admin
require_role("admin")

# Aplică stilurile moderne
init_page_style(st)

# Header pagină
st.markdown(page_header(
    "Administrare Utilizatori",
    "Gestionează conturile de utilizator, rolurile și permisiunile",
    "👥"
), unsafe_allow_html=True)

# Conectare la baza de date
try:
    from db_utils import get_db_connection
    USE_DATABASE = True
except ImportError:
    USE_DATABASE = False

def init_users_table():
    """Inițializează tabelul de utilizatori în baza de date"""
    if not USE_DATABASE:
        return False

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Creează tabelul dacă nu există
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(128) NOT NULL,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                role VARCHAR(20) DEFAULT 'viewer',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                created_by VARCHAR(50)
            )
        """)

        # Verifică dacă există admin implicit
        cur.execute("SELECT COUNT(*) FROM users WHERE username = 'sorin'")
        if cur.fetchone()[0] == 0:
            # Adaugă utilizatorul admin implicit
            cur.execute("""
                INSERT INTO users (username, password_hash, name, email, role, created_by)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                'sorin',
                hash_password('vestpolicylab17@'),
                'Sorin Maxim',
                'sorin@vestpolicylab.org',
                'admin',
                'system'
            ))

        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Eroare la inițializarea tabelului: {str(e)}")
        return False

def get_all_users():
    """Returnează toți utilizatorii din baza de date"""
    if not USE_DATABASE:
        # Returnează utilizatorii din dicționar (fallback)
        from auth import USERS
        users_list = []
        for username, data in USERS.items():
            users_list.append({
                'id': hash(username) % 10000,
                'username': username,
                'name': data.get('name', username),
                'email': data.get('email', ''),
                'role': data.get('role', 'viewer'),
                'is_active': True,
                'created_at': datetime.now(),
                'last_login': None
            })
        return pd.DataFrame(users_list)

    try:
        conn = get_db_connection()
        df = pd.read_sql("""
            SELECT id, username, name, email, role, is_active,
                   created_at, last_login, created_by
            FROM users
            ORDER BY created_at DESC
        """, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Eroare la citirea utilizatorilor: {str(e)}")
        return pd.DataFrame()

def add_user(username, password, name, email, role, created_by):
    """Adaugă un utilizator nou"""
    if not USE_DATABASE:
        st.warning("Funcție disponibilă doar cu baza de date activă.")
        return False

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO users (username, password_hash, name, email, role, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, hash_password(password), name, email, role, created_by))

        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Eroare la adăugarea utilizatorului: {str(e)}")
        return False

def update_user(user_id, name, email, role, is_active):
    """Actualizează un utilizator"""
    if not USE_DATABASE:
        st.warning("Funcție disponibilă doar cu baza de date activă.")
        return False

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE users
            SET name = %s, email = %s, role = %s, is_active = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (name, email, role, is_active, user_id))

        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Eroare la actualizarea utilizatorului: {str(e)}")
        return False

def reset_password(user_id, new_password):
    """Resetează parola unui utilizator"""
    if not USE_DATABASE:
        st.warning("Funcție disponibilă doar cu baza de date activă.")
        return False

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE users
            SET password_hash = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (hash_password(new_password), user_id))

        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Eroare la resetarea parolei: {str(e)}")
        return False

def delete_user(user_id, username):
    """Șterge un utilizator"""
    if not USE_DATABASE:
        st.warning("Funcție disponibilă doar cu baza de date activă.")
        return False

    # Nu permite ștergerea propriului cont
    current_user = get_current_user()
    if current_user and current_user['username'] == username:
        st.error("Nu poți șterge propriul cont!")
        return False

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))

        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Eroare la ștergerea utilizatorului: {str(e)}")
        return False

def get_user_stats():
    """Returnează statistici despre utilizatori"""
    if not USE_DATABASE:
        return {'total': 1, 'active': 1, 'admins': 1, 'editors': 0, 'viewers': 0}

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        stats = {}

        cur.execute("SELECT COUNT(*) FROM users")
        stats['total'] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM users WHERE is_active = TRUE")
        stats['active'] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        stats['admins'] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM users WHERE role = 'editor'")
        stats['editors'] = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM users WHERE role = 'viewer'")
        stats['viewers'] = cur.fetchone()[0]

        cur.close()
        conn.close()
        return stats
    except Exception as e:
        return {'total': 0, 'active': 0, 'admins': 0, 'editors': 0, 'viewers': 0}

# Inițializare tabel utilizatori
if USE_DATABASE:
    init_users_table()

# Info utilizator curent
current_user = get_current_user()
st.info(f"Conectat ca: **{current_user['name']}** (Rol: {current_user['role'].upper()})")

st.markdown("---")

# Statistici utilizatori
st.subheader("📊 Statistici Utilizatori")

stats = get_user_stats()
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Utilizatori", stats['total'])
with col2:
    st.metric("Activi", stats['active'])
with col3:
    st.metric("Administratori", stats['admins'])
with col4:
    st.metric("Editori", stats['editors'])
with col5:
    st.metric("Vizualizatori", stats['viewers'])

st.markdown("---")

# Tabs pentru diferite funcționalități
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Lista Utilizatori",
    "➕ Adaugă Utilizator",
    "🔐 Securitate",
    "📜 Jurnal Activități"
])

with tab1:
    st.subheader("Lista Utilizatorilor")

    # Filtre
    col_filter1, col_filter2, col_filter3 = st.columns(3)

    with col_filter1:
        filter_role = st.selectbox(
            "Filtrează după rol",
            ["Toți", "admin", "editor", "viewer"],
            key="filter_role"
        )

    with col_filter2:
        filter_status = st.selectbox(
            "Filtrează după status",
            ["Toți", "Activi", "Inactivi"],
            key="filter_status"
        )

    with col_filter3:
        search_term = st.text_input("Caută utilizator", placeholder="Nume sau email...")

    # Obține utilizatorii
    users_df = get_all_users()

    if not users_df.empty:
        # Aplică filtre
        if filter_role != "Toți":
            users_df = users_df[users_df['role'] == filter_role]

        if filter_status == "Activi":
            users_df = users_df[users_df['is_active'] == True]
        elif filter_status == "Inactivi":
            users_df = users_df[users_df['is_active'] == False]

        if search_term:
            mask = (
                users_df['name'].str.contains(search_term, case=False, na=False) |
                users_df['email'].str.contains(search_term, case=False, na=False) |
                users_df['username'].str.contains(search_term, case=False, na=False)
            )
            users_df = users_df[mask]

        st.markdown(f"**{len(users_df)}** utilizatori găsiți")

        # Afișare tabel cu acțiuni
        for idx, user in users_df.iterrows():
            with st.expander(f"👤 {user['name']} (@{user['username']}) - {user['role'].upper()}", expanded=False):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"""
                    - **Username:** {user['username']}
                    - **Email:** {user.get('email', 'N/A')}
                    - **Rol:** {user['role'].capitalize()}
                    - **Status:** {'✅ Activ' if user['is_active'] else '❌ Inactiv'}
                    - **Creat la:** {user['created_at'].strftime('%d.%m.%Y %H:%M') if pd.notna(user['created_at']) else 'N/A'}
                    - **Ultima autentificare:** {user['last_login'].strftime('%d.%m.%Y %H:%M') if pd.notna(user.get('last_login')) else 'Niciodată'}
                    """)

                with col2:
                    st.markdown("**Acțiuni:**")

                    # Formular editare
                    with st.form(f"edit_form_{user['id']}"):
                        new_name = st.text_input("Nume", value=user['name'], key=f"name_{user['id']}")
                        new_email = st.text_input("Email", value=user.get('email', ''), key=f"email_{user['id']}")
                        new_role = st.selectbox(
                            "Rol",
                            ["admin", "editor", "viewer"],
                            index=["admin", "editor", "viewer"].index(user['role']),
                            key=f"role_{user['id']}"
                        )
                        new_status = st.checkbox("Activ", value=user['is_active'], key=f"status_{user['id']}")

                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            if st.form_submit_button("💾 Salvează", use_container_width=True):
                                if update_user(user['id'], new_name, new_email, new_role, new_status):
                                    st.success("Utilizator actualizat!")
                                    st.rerun()

                    # Resetare parolă
                    with st.form(f"reset_pwd_{user['id']}"):
                        new_pwd = st.text_input("Parolă nouă", type="password", key=f"pwd_{user['id']}")
                        if st.form_submit_button("🔑 Resetează Parola", use_container_width=True):
                            if new_pwd:
                                if len(new_pwd) >= 8:
                                    if reset_password(user['id'], new_pwd):
                                        st.success("Parola a fost resetată!")
                                else:
                                    st.error("Parola trebuie să aibă minim 8 caractere!")
                            else:
                                st.warning("Introdu o parolă nouă!")

                    # Ștergere utilizator
                    if user['username'] != current_user['username']:
                        if st.button(f"🗑️ Șterge", key=f"delete_{user['id']}", type="secondary"):
                            st.session_state[f"confirm_delete_{user['id']}"] = True

                        if st.session_state.get(f"confirm_delete_{user['id']}", False):
                            st.warning(f"Sigur vrei să ștergi utilizatorul {user['username']}?")
                            col_confirm1, col_confirm2 = st.columns(2)
                            with col_confirm1:
                                if st.button("✅ Da", key=f"confirm_yes_{user['id']}"):
                                    if delete_user(user['id'], user['username']):
                                        st.success("Utilizator șters!")
                                        del st.session_state[f"confirm_delete_{user['id']}"]
                                        st.rerun()
                            with col_confirm2:
                                if st.button("❌ Nu", key=f"confirm_no_{user['id']}"):
                                    del st.session_state[f"confirm_delete_{user['id']}"]
                                    st.rerun()
    else:
        st.info("Nu există utilizatori înregistrați.")

with tab2:
    st.subheader("➕ Adaugă Utilizator Nou")

    with st.form("add_user_form"):
        col1, col2 = st.columns(2)

        with col1:
            new_username = st.text_input(
                "Username *",
                placeholder="utilizator123",
                help="Numele de utilizator pentru autentificare (fără spații)"
            )
            new_password = st.text_input(
                "Parolă *",
                type="password",
                help="Minim 8 caractere"
            )
            confirm_password = st.text_input(
                "Confirmă Parola *",
                type="password"
            )

        with col2:
            new_name = st.text_input(
                "Nume Complet *",
                placeholder="Ion Popescu"
            )
            new_email = st.text_input(
                "Email",
                placeholder="ion.popescu@example.com"
            )
            new_role = st.selectbox(
                "Rol *",
                ["viewer", "editor", "admin"],
                help="viewer: doar vizualizare | editor: poate modifica date | admin: acces complet"
            )

        st.markdown("---")

        # Descriere roluri
        st.markdown("""
        **Descriere Roluri:**
        - **Viewer (Vizualizator):** Poate vizualiza dashboard-uri și rapoarte, dar nu poate modifica date
        - **Editor:** Poate importa date, genera rapoarte și modifica informații
        - **Admin (Administrator):** Acces complet, inclusiv gestionarea utilizatorilor
        """)

        submitted = st.form_submit_button("➕ Creează Utilizator", type="primary", use_container_width=True)

        if submitted:
            # Validări
            errors = []

            if not new_username:
                errors.append("Username-ul este obligatoriu")
            elif len(new_username) < 3:
                errors.append("Username-ul trebuie să aibă minim 3 caractere")
            elif ' ' in new_username:
                errors.append("Username-ul nu poate conține spații")

            if not new_password:
                errors.append("Parola este obligatorie")
            elif len(new_password) < 8:
                errors.append("Parola trebuie să aibă minim 8 caractere")

            if new_password != confirm_password:
                errors.append("Parolele nu coincid")

            if not new_name:
                errors.append("Numele complet este obligatoriu")

            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                if add_user(new_username, new_password, new_name, new_email, new_role, current_user['username']):
                    st.success(f"✅ Utilizatorul '{new_username}' a fost creat cu succes!")
                    st.balloons()

with tab3:
    st.subheader("🔐 Setări de Securitate")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Politici Parole")

        st.markdown("""
        **Cerințe curente pentru parole:**
        - Minim 8 caractere
        - Se recomandă folosirea de litere mari, mici, cifre și simboluri
        """)

        st.markdown("---")

        st.markdown("### Schimbă Propria Parolă")

        with st.form("change_own_password"):
            current_pwd = st.text_input("Parola curentă", type="password")
            new_pwd = st.text_input("Parola nouă", type="password")
            confirm_new_pwd = st.text_input("Confirmă parola nouă", type="password")

            if st.form_submit_button("🔄 Schimbă Parola", use_container_width=True):
                if not current_pwd or not new_pwd or not confirm_new_pwd:
                    st.error("Completează toate câmpurile!")
                elif new_pwd != confirm_new_pwd:
                    st.error("Parolele noi nu coincid!")
                elif len(new_pwd) < 8:
                    st.error("Parola nouă trebuie să aibă minim 8 caractere!")
                else:
                    # Verifică parola curentă
                    from auth import verify_password
                    if verify_password(current_user['username'], current_pwd):
                        # Găsește ID-ul utilizatorului curent
                        users_df = get_all_users()
                        user_row = users_df[users_df['username'] == current_user['username']]
                        if not user_row.empty:
                            if reset_password(user_row.iloc[0]['id'], new_pwd):
                                st.success("Parola a fost schimbată cu succes!")
                    else:
                        st.error("Parola curentă este incorectă!")

    with col2:
        st.markdown("### Sesiuni Active")

        st.info("""
        Funcționalitatea de gestionare a sesiunilor active
        va fi disponibilă într-o versiune viitoare.
        """)

        st.markdown("---")

        st.markdown("### Acțiuni Rapide")

        if st.button("🔒 Dezactivează toți utilizatorii (excl. admini)", use_container_width=True):
            st.session_state["confirm_deactivate_all"] = True

        if st.session_state.get("confirm_deactivate_all", False):
            st.warning("Această acțiune va dezactiva toți utilizatorii care nu sunt administratori.")
            col_da, col_nu = st.columns(2)
            with col_da:
                if st.button("✅ Confirmă dezactivarea", key="confirm_deactivate_yes"):
                    st.info("Funcționalitate în dezvoltare")
                    st.session_state["confirm_deactivate_all"] = False
            with col_nu:
                if st.button("❌ Anulează", key="confirm_deactivate_no"):
                    st.session_state["confirm_deactivate_all"] = False
                    st.rerun()

        if st.button("📧 Trimite email resetare parolă tuturor", use_container_width=True):
            st.info("Funcționalitate în dezvoltare - necesită configurare SMTP")

with tab4:
    st.subheader("📜 Jurnal Activități")

    st.info("""
    Jurnalul de activități va înregistra:
    - Autentificări reușite și eșuate
    - Modificări ale conturilor de utilizator
    - Acțiuni importante în aplicație

    *Funcționalitate în dezvoltare*
    """)

    # Simulare jurnal
    activity_log = pd.DataFrame({
        "Data/Ora": [
            datetime.now().strftime("%d.%m.%Y %H:%M"),
            (datetime.now()).strftime("%d.%m.%Y %H:%M"),
        ],
        "Utilizator": ["sorin", "sorin"],
        "Acțiune": ["Autentificare reușită", "Acces pagină Admin"],
        "IP": ["N/A", "N/A"],
        "Detalii": ["Login din browser", "Vizualizare lista utilizatori"]
    })

    st.dataframe(activity_log, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.caption("⚠️ Modificările efectuate aici afectează securitatea aplicației. Procedează cu atenție.")
