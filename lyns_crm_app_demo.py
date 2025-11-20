import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Lyns Real Estate CRM", page_icon="🏠", layout="wide")

st.markdown('<h1 style="color: #1f77b4;">🏠 Lyns Real Estate CRM</h1>', unsafe_allow_html=True)

# Simple login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("### Please Login")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        user_role = st.selectbox("Select Your Role", ["Admin (Lyndon)", "Partner A"])
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            if password == "lyns2024":
                st.session_state.logged_in = True
                st.session_state.user_role = "Admin" if "Admin" in user_role else "Partner"
                st.session_state.user_name = user_role.split("(")[0].strip()
                st.rerun()
            else:
                st.error("Invalid password")
        st.info("Demo password: lyns2024")
else:
    st.sidebar.markdown(f"### 👤 Welcome, {st.session_state.user_name}!")
    st.sidebar.markdown(f"**Role:** {st.session_state.user_role}")
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.success("✅ You're logged in! This is a demo version of Lyns Real Estate CRM")
    
    st.markdown("### 📊 Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Clients", "0", "Demo Mode")
    with col2:
        st.metric("Total Listings", "0", "Demo Mode")
    with col3:
        st.metric("Deals Closed", "0", "Demo Mode")
    with col4:
        st.metric("Commission", "₹0", "Demo Mode")
    
    st.info("🚧 This is a simplified demo. Full version with Google Sheets will be configured next!")
    
    st.markdown("### Next Steps:")
    st.write("1. ✅ Installation complete - You're seeing this!")
    st.write("2. 📋 Next: Set up Google Sheets for data storage")
    st.write("3. 🚀 Then: Start adding real clients and listings")
