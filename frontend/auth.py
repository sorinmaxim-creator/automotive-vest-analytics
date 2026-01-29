"""
Modul de autentificare pentru aplicație
Suportă atât dicționar local cât și baza de date
"""

import streamlit as st
import hashlib
import os
from datetime import datetime

# Configurare utilizatori fallback (când baza de date nu e disponibilă)
USERS = {
    "sorin": {
        "password_hash": hashlib.sha256("vestpolicylab17@".encode()).hexdigest(),
        "name": "Sorin Maxim",
        "role": "admin",
        "email": "sorin@vestpolicylab.org"
    }
}

# Flag pentru a detecta dacă baza de date e disponibilă
USE_DATABASE = False

def _get_db_connection():
    """Încearcă să obțină o conexiune la baza de date"""
    global USE_DATABASE
    try:
        from db_utils import get_db_connection
        conn = get_db_connection()
        USE_DATABASE = True
        return conn
    except Exception:
        USE_DATABASE = False
        return None

def _init_users_table():
    """Inițializează tabelul de utilizatori dacă nu există"""
    conn = _get_db_connection()
    if not conn:
        return False

    try:
        cur = conn.cursor()

        # Creează tabelul dacă nu există
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(64) NOT NULL,
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
        print(f"Eroare init users table: {e}")
        return False

def hash_password(password: str) -> str:
    """Generează hash SHA256 pentru parolă"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(username: str, password: str) -> bool:
    """Verifică dacă parola este corectă"""
    # Încearcă mai întâi din baza de date
    conn = _get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT password_hash, is_active FROM users
                WHERE username = %s
            """, (username,))
            result = cur.fetchone()
            cur.close()
            conn.close()

            if result:
                stored_hash, is_active = result
                if not is_active:
                    return False
                return stored_hash == hash_password(password)
            return False
        except Exception as e:
            print(f"Eroare verificare parolă DB: {e}")
            # Fallback la dicționar
            pass

    # Fallback: verifică în dicționar
    if username not in USERS:
        return False
    return USERS[username]["password_hash"] == hash_password(password)

def get_user_info(username: str) -> dict:
    """Returnează informațiile utilizatorului"""
    # Încearcă mai întâi din baza de date
    conn = _get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT username, name, email, role FROM users
                WHERE username = %s AND is_active = TRUE
            """, (username,))
            result = cur.fetchone()
            cur.close()
            conn.close()

            if result:
                return {
                    "username": result[0],
                    "name": result[1],
                    "email": result[2] or "",
                    "role": result[3]
                }
        except Exception as e:
            print(f"Eroare get user info DB: {e}")
            pass

    # Fallback: verifică în dicționar
    if username in USERS:
        return {
            "username": username,
            "name": USERS[username]["name"],
            "role": USERS[username]["role"],
            "email": USERS[username].get("email", "")
        }
    return None

def update_last_login(username: str):
    """Actualizează data ultimei autentificări"""
    conn = _get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE username = %s
            """, (username,))
            conn.commit()
            cur.close()
            conn.close()
        except Exception:
            pass

def login_form():
    """Afișează formularul de login"""
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: #f8f9fa;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### 🔐 Autentificare")
        st.markdown("---")

        with st.form("login_form"):
            username = st.text_input("👤 Utilizator", placeholder="Introdu numele de utilizator")
            password = st.text_input("🔑 Parolă", type="password", placeholder="Introdu parola")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit = st.form_submit_button("🔓 Autentificare", type="primary", use_container_width=True)

            if submit:
                if username and password:
                    if verify_password(username, password):
                        st.session_state["authenticated"] = True
                        st.session_state["user"] = get_user_info(username)
                        update_last_login(username)
                        st.success("✅ Autentificare reușită!")
                        st.rerun()
                    else:
                        st.error("❌ Utilizator sau parolă incorectă!")
                else:
                    st.warning("⚠️ Completează toate câmpurile!")

        st.markdown("---")
        st.caption("© 2025 Vest Policy Lab - Regiunea Vest Analytics")

def logout():
    """Deconectare utilizator"""
    if "authenticated" in st.session_state:
        del st.session_state["authenticated"]
    if "user" in st.session_state:
        del st.session_state["user"]
    if "_user_info_shown" in st.session_state:
        del st.session_state["_user_info_shown"]

def is_authenticated() -> bool:
    """Verifică dacă utilizatorul este autentificat"""
    return st.session_state.get("authenticated", False)

def get_current_user() -> dict:
    """Returnează utilizatorul curent"""
    return st.session_state.get("user", None)

def require_auth():
    """Decorator/funcție pentru a proteja o pagină"""
    # Inițializează tabelul de utilizatori la prima utilizare
    _init_users_table()

    if not is_authenticated():
        st.title("🏭 Automotive Vest Analytics")
        st.markdown("### Platformă de analiză a sectorului automotive din Regiunea Vest")
        st.markdown("---")
        login_form()
        st.stop()

def show_user_info():
    """Afișează informații despre utilizatorul curent în sidebar"""
    # Evită afișarea multiplă a informațiilor utilizatorului
    if st.session_state.get("_user_info_shown", False):
        return

    user = get_current_user()
    if user:
        st.session_state["_user_info_shown"] = True
        with st.sidebar:
            st.markdown("---")
            st.markdown(f"👤 **{user['name']}**")
            st.caption(f"Rol: {user['role'].capitalize()}")

            if st.button("🚪 Deconectare", use_container_width=True, key="sidebar_logout_btn"):
                logout()
                st.rerun()

def check_role(required_role: str) -> bool:
    """Verifică dacă utilizatorul are rolul necesar"""
    user = get_current_user()
    if not user:
        return False

    role_hierarchy = {"viewer": 1, "editor": 2, "admin": 3}
    user_level = role_hierarchy.get(user["role"], 0)
    required_level = role_hierarchy.get(required_role, 0)

    return user_level >= required_level

def require_role(required_role: str):
    """Verifică rolul și oprește execuția dacă nu are permisiuni"""
    if not check_role(required_role):
        st.error(f"❌ Nu ai permisiuni pentru această pagină. Rol necesar: {required_role}")
        st.stop()
