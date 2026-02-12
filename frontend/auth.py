"""
Modul de autentificare pentru aplicație
Suportă atât dicționar local cât și baza de date
"""

import streamlit as st
import bcrypt
import os
from datetime import datetime

# Configurare utilizatori din variabile de mediu
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "sorin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "vestpolicylab17@")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "sorin@vestpolicylab.org")

# Utilizatori fallback (când baza de date nu e disponibilă)
# Parolele în acest dicționar ar trebui să fie de asemenea hash-uite dacă sunt stocate permanent, 
# dar aici le calculăm la runtime din variabile de mediu pentru securitate.
USERS = {
    ADMIN_USERNAME: {
        "password_hash": None, # Va fi populat la nevoie sau verificat direct
        "name": "Sorin Maxim",
        "role": "admin",
        "email": ADMIN_EMAIL
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
        print(f"Eroare init users table: {e}")
        return False

def hash_password(password: str) -> str:
    """Generează hash Bcrypt pentru parolă"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode('utf-8')

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
                # Verificare hash cu bcrypt
                try:
                    return bcrypt.checkpw(password.encode(), stored_hash.encode())
                except ValueError:
                    # Fallback în caz că hash-ul vechi e SHA256 (pentru migrare)
                    import hashlib
                    old_hash = hashlib.sha256(password.encode()).hexdigest()
                    if stored_hash == old_hash:
                        # Re-hash cu bcrypt pentru viitor
                        # update_password_hash(username, password)
                        return True
                    return False
            return False
        except Exception as e:
            print(f"Eroare verificare parolă DB: {e}")
            # Fallback la dicționar
            pass

    # Fallback: verifică direct cu parola din variabile de mediu
    if username == ADMIN_USERNAME and ADMIN_PASSWORD:
        return password == ADMIN_PASSWORD
    return False

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

def register_user(username: str, password: str, name: str, email: str = "") -> tuple:
    """Înregistrează un utilizator nou. Returnează (succes, mesaj)."""
    # Validări
    if not username or len(username) < 3:
        return False, "Username-ul trebuie să aibă minim 3 caractere"
    if ' ' in username:
        return False, "Username-ul nu poate conține spații"
    if not password or len(password) < 8:
        return False, "Parola trebuie să aibă minim 8 caractere"
    if not name:
        return False, "Numele complet este obligatoriu"

    conn = _get_db_connection()
    if not conn:
        return False, "Înregistrarea nu este disponibilă momentan (baza de date indisponibilă)"

    try:
        cur = conn.cursor()

        # Verifică dacă username-ul există deja
        cur.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
        if cur.fetchone()[0] > 0:
            cur.close()
            conn.close()
            return False, "Acest username este deja folosit"

        # Inserează utilizatorul nou cu rol viewer
        cur.execute("""
            INSERT INTO users (username, password_hash, name, email, role, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, hash_password(password), name, email, 'viewer', 'self-register'))

        conn.commit()
        cur.close()
        conn.close()
        return True, "Cont creat cu succes! Te poți autentifica acum."
    except Exception as e:
        print(f"Eroare înregistrare utilizator: {e}")
        return False, "Eroare la crearea contului. Încearcă din nou."


def login_form():
    """Afișează formularul de login cu două secțiuni: Autentificare și Înregistrare"""
    st.markdown("""
    <style>
    .auth-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        height: 100%;
    }
    .auth-card-login {
        border-top: 4px solid #1a365d;
    }
    .auth-card-register {
        border-top: 4px solid #38a169;
    }
    .auth-card-title {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .auth-card-title-login { color: #1a365d; }
    .auth-card-title-register { color: #38a169; }
    .auth-card-desc {
        color: #718096;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    col_login, col_sep, col_register = st.columns([5, 1, 5])

    # ── Coloana stânga: AM DEJA CONT ──
    with col_login:
        st.markdown("""
        <div class="auth-card auth-card-login">
            <div class="auth-card-title auth-card-title-login">🔐 Am deja cont</div>
            <div class="auth-card-desc">Introdu datele tale de autentificare</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("👤 Utilizator", placeholder="Introdu numele de utilizator")
            password = st.text_input("🔑 Parolă", type="password", placeholder="Introdu parola")

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

    # ── Separator vizual ──
    with col_sep:
        st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center;
                    justify-content: center; height: 100%; min-height: 300px;">
            <div style="width: 2px; flex: 1; background: linear-gradient(to bottom, transparent, #cbd5e0, transparent);"></div>
            <div style="padding: 0.75rem 0; color: #a0aec0; font-weight: 600; font-size: 0.85rem;">SAU</div>
            <div style="width: 2px; flex: 1; background: linear-gradient(to bottom, transparent, #cbd5e0, transparent);"></div>
        </div>
        """, unsafe_allow_html=True)

    # ── Coloana dreapta: SUNT UTILIZATOR NOU ──
    with col_register:
        st.markdown("""
        <div class="auth-card auth-card-register">
            <div class="auth-card-title auth-card-title-register">📝 Sunt utilizator nou</div>
            <div class="auth-card-desc">Creează-ți un cont gratuit (doar vizualizare)</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("register_form"):
            reg_username = st.text_input(
                "👤 Username",
                placeholder="Alege un username (min. 3 caractere)"
            )
            reg_name = st.text_input(
                "📛 Nume Complet",
                placeholder="Ex: Ion Popescu"
            )
            reg_email = st.text_input(
                "📧 Email (opțional)",
                placeholder="Ex: ion.popescu@example.com"
            )
            reg_password = st.text_input(
                "🔑 Parolă",
                type="password",
                placeholder="Minim 8 caractere"
            )
            reg_confirm = st.text_input(
                "🔑 Confirmă Parola",
                type="password",
                placeholder="Repetă parola"
            )

            submit_reg = st.form_submit_button("📝 Creează Cont", type="primary", use_container_width=True)

            if submit_reg:
                if reg_password != reg_confirm:
                    st.error("❌ Parolele nu coincid!")
                else:
                    success, message = register_user(reg_username, reg_password, reg_name, reg_email)
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")

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
