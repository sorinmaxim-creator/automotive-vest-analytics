"""
Pagina de Login
"""

import streamlit as st
import os
import sys
if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import login_form, is_authenticated, logout

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered")

if is_authenticated():
    st.title("✅ Ești deja autentificat")
    st.info("Navighează la alte pagini din meniul din stânga.")

    if st.button("🚪 Deconectare"):
        logout()
        st.rerun()
else:
    st.title("🏭 Automotive Vest Analytics")
    st.markdown("### Platformă de analiză a sectorului automotive din Regiunea Vest")
    st.markdown("---")
    login_form()
