"""
Lyns Real Estate CRM - Complete Business Version
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import hashlib
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.set_page_config(page_title="Lyns Real Estate CRM", page_icon="🏠", layout="wide")

st.markdown("""
    <style>
    .main-header {font-size: 2.5rem; font-weight: bold; color: #1f77b4; margin-bottom: 1rem;}
    .metric-card {background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #1f77b4;}
    </style>
""", unsafe_allow_html=True)


# Google Sheets Integration
def init_google_sheets():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        
        # Check if running on Streamlit Cloud (secrets available) or locally
        if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
            # Running on Streamlit Cloud - use secrets
            creds_dict = dict(st.secrets['gcp_service_account'])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            
            config = {
                'users_sheet_id': st.secrets['sheets']['users_sheet_id'],
                'clients_sheet_id': st.secrets['sheets']['clients_sheet_id'],
                'listings_sheet_id': st.secrets['sheets']['listings_sheet_id'],
                'deals_sheet_id': st.secrets['sheets']['deals_sheet_id']
            }
        else:
            # Running locally - use files
            creds = ServiceAccountCredentials.from_json_keyfile_name('google_credentials.json', scope)
            client = gspread.authorize(creds)
            
            with open('sheets_config.json', 'r') as f:
                config = json.load(f)
        
        return client, config
    except Exception as e:
        st.error(f"Google Sheets connection error: {e}")
        return None, None


def send_email_notification(to_email, subject, body):
    try:
        # Check if email settings are configured
        if not hasattr(st, 'secrets') or 'email' not in st.secrets:
            return False
        
        smtp_server = st.secrets['email']['smtp_server']
        smtp_port = st.secrets['email']['smtp_port']
        sender_email = st.secrets['email']['sender_email']
        sender_password = st.secrets['email']['sender_password']
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        st.error(f"Email notification failed: {e}")
        return False

def load_from_sheets(client, sheet_id, sheet_name="Sheet1"):
    try:
        sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
        data = sheet.get_all_records()
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def save_to_sheets(client, sheet_id, df, sheet_name="Sheet1"):
    try:
        sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
        sheet.clear()
        if not df.empty:
            sheet.update([df.columns.values.tolist()] + df.values.tolist())
        return True
    except Exception as e:
        st.error(f"Error saving to sheets: {e}")
        return False

LOCATIONS = ["Sakinaka", "Chandivali", "Marol", "JB Nagar", "Chakala", "Kurla", "Powai", 
             "Andheri-Kurla Road", "Andheri East", "Andheri West", "Ghatkopar", "Vikhroli", 
             "Bhandup", "Mulund", "Other"]

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_data():
    # Initialize Google Sheets connection
    if 'gs_client' not in st.session_state:
        client, config = init_google_sheets()
        st.session_state.gs_client = client
        st.session_state.gs_config = config
    
    client = st.session_state.gs_client
    config = st.session_state.gs_config
    
    if client and config:
        # Load Users from Google Sheets
        if 'users' not in st.session_state:
            users_df = load_from_sheets(client, config['users_sheet_id'])
            if users_df.empty:
                # Create default admin if sheet is empty
                st.session_state.users = pd.DataFrame([{
                    'Username': 'admin',
                    'Password': hash_password('lyns2024'),
                    'Role': 'Admin',
                    'Full_Name': 'Lyndon',
                    'Email': 'lyndon@lynsrealestate.com',
                    'Status': 'Active'
                }])
                save_to_sheets(client, config['users_sheet_id'], st.session_state.users)
            else:
                st.session_state.users = users_df
        
        # Load Clients
        if 'clients' not in st.session_state:
            clients_df = load_from_sheets(client, config['clients_sheet_id'])
            if clients_df.empty:
                st.session_state.clients = pd.DataFrame(columns=[
                    'Client_ID', 'Client_Name', 'Contact_Number', 'Email', 'Client_Type', 'Property_Category', 
                    'Property_Type', 'Furnishing_Status', 'Budget_Min', 'Budget_Max', 'Budget_Currency', 
                    'Location_Preference', 'BHK_Requirement', 'Requirements_Notes', 'Possession_Date', 
                    'Status', 'Assigned_To', 'Date_Registered', 'Source', 'Priority'
                ])
            else:
                st.session_state.clients = clients_df
        
        # Load Listings
        if 'listings' not in st.session_state:
            listings_df = load_from_sheets(client, config['listings_sheet_id'])
            if listings_df.empty:
                st.session_state.listings = pd.DataFrame(columns=[
                    'Listing_ID', 'Property_Address', 'Location', 'Property_Category', 'Property_Type', 
                    'Furnishing_Status', 'BHK', 'Price', 'Price_Currency', 'Area_SqFt', 'Broker_Name', 
                    'Broker_Contact', 'Amenities', 'Listing_Status', 'Date_Added', 'Visible_To_Partner', 
                    'Notes', 'Assigned_To', 'Shown_To_Clients'
                ])
            else:
                st.session_state.listings = listings_df
        
        # Load Deals
        if 'deals' not in st.session_state:
            deals_df = load_from_sheets(client, config['deals_sheet_id'])
            if deals_df.empty:
                st.session_state.deals = pd.DataFrame(columns=[
                    'Deal_ID', 'Client_ID', 'Listing_ID', 'Brokerage_From_Owner', 'Brokerage_From_Client', 
                    'Total_Brokerage', 'Number_Of_Brokers', 'Your_Share', 'Partner_Share', 'Partner_Name', 
                    'Deal_Date', 'Payment_Status', 'Notes'
                ])
            else:
                st.session_state.deals = deals_df
    else:
        st.error("⚠️ Google Sheets not connected. Running in memory-only mode.")
        # Fallback to in-memory mode
        if 'users' not in st.session_state:
            st.session_state.users = pd.DataFrame([{
                'Username': 'admin',
                'Password': hash_password('lyns2024'),
                'Role': 'Admin',
                'Full_Name': 'Lyndon',
                'Email': 'lynsrealestateagency@gmail.com',
                'Status': 'Active'
            }])
        if 'clients' not in st.session_state:
            st.session_state.clients = pd.DataFrame(columns=[
                'Client_ID', 'Client_Name', 'Contact_Number', 'Email', 'Client_Type', 'Property_Category', 
                'Property_Type', 'Furnishing_Status', 'Budget_Min', 'Budget_Max', 'Budget_Currency', 
                'Location_Preference', 'BHK_Requirement', 'Requirements_Notes', 'Possession_Date', 
                'Status', 'Assigned_To', 'Date_Registered', 'Source', 'Priority'
            ])
        if 'listings' not in st.session_state:
            st.session_state.listings = pd.DataFrame(columns=[
                'Listing_ID', 'Property_Address', 'Location', 'Property_Category', 'Property_Type', 
                'Furnishing_Status', 'BHK', 'Price', 'Price_Currency', 'Area_SqFt', 'Broker_Name', 
                'Broker_Contact', 'Amenities', 'Listing_Status', 'Date_Added', 'Visible_To_Partner', 
                'Notes', 'Assigned_To', 'Shown_To_Clients'
            ])
        if 'deals' not in st.session_state:
            st.session_state.deals = pd.DataFrame(columns=[
                    'Deal_ID', 'Client_ID', 'Listing_ID', 'Brokerage_From_Owner', 'Brokerage_From_Client', 
                    'Total_Brokerage', 'Number_Of_Brokers', 'Your_Share', 'Partner_Share', 'Partner_Name', 
                    'Deal_Date', 'Payment_Status', 'Notes'
                ])

def add_user(username, password, role, full_name, email):
    new_user = pd.DataFrame([{
        'Username': username,
        'Password': hash_password(password),
        'Role': role,
        'Full_Name': full_name,
        'Email': email,
        'Status': 'Active'
    }])
    st.session_state.users = pd.concat([st.session_state.users, new_user], ignore_index=True)
    # Save to Google Sheets
    if st.session_state.gs_client and st.session_state.gs_config:
        save_to_sheets(st.session_state.gs_client, st.session_state.gs_config['users_sheet_id'], st.session_state.users)

def authenticate(username, password):
    users = st.session_state.users
    user = users[users['Username'] == username]
    if not user.empty:
        if user['Status'].values[0] == 'Inactive':
            return False, None, None  # User is disabled
        if user['Password'].values[0] == hash_password(password):
            return True, user['Role'].values[0], user['Full_Name'].values[0]
    return False, None, None

def add_client(client_data):
    client_id = f"C{len(st.session_state.clients) + 1:04d}"
    new_row = pd.DataFrame([{
        'Client_ID': client_id, 'Client_Name': client_data['name'], 
        'Contact_Number': client_data['contact'], 'Email': client_data['email'],
        'Client_Type': client_data['client_type'], 'Property_Category': client_data['property_category'],
        'Property_Type': client_data['property_type'], 
        'Furnishing_Status': client_data.get('furnishing_status', 'N/A'),
        'Budget_Min': client_data['budget_min'], 'Budget_Max': client_data['budget_max'], 
        'Budget_Currency': client_data['budget_currency'], 'Location_Preference': client_data['location'], 
        'BHK_Requirement': client_data['bhk'], 'Requirements_Notes': client_data['requirements'], 
        'Possession_Date': client_data.get('possession_date', ''), 'Status': 'New Lead', 
        'Assigned_To': client_data['assigned_to'], 'Date_Registered': datetime.now().strftime('%Y-%m-%d'),
        'Source': client_data['source'], 'Priority': client_data['priority']
    }])
    st.session_state.clients = pd.concat([st.session_state.clients, new_row], ignore_index=True)
    # Save to Google Sheets
    if st.session_state.gs_client and st.session_state.gs_config:
        save_to_sheets(st.session_state.gs_client, st.session_state.gs_config['clients_sheet_id'], st.session_state.clients)
    
    # Send email notification if assigned to a partner
    if client_data['assigned_to'] != 'Unassigned' and client_data['assigned_to'] != 'Admin':
        # Find partner email
        partner = st.session_state.users[st.session_state.users['Full_Name'] == client_data['assigned_to']]
        if not partner.empty:
            partner_email = partner.iloc[0]['Email']
            subject = f"New Client Assigned: {client_data['name']}"
            body = f"""
            <html>
            <body>
            <h2>New Client Assigned to You</h2>
            <p>Hi {client_data['assigned_to']},</p>
            <p>A new client has been assigned to you:</p>
            <ul>
            <li><strong>Client Name:</strong> {client_data['name']}</li>
            <li><strong>Contact:</strong> {client_data['contact']}</li>
            <li><strong>Type:</strong> {client_data['client_type']}</li>
            <li><strong>Property:</strong> {client_data['property_category']} - {client_data['property_type']}</li>
            <li><strong>Budget:</strong> {client_data['budget_currency']} {client_data['budget_min']} - {client_data['budget_max']}</li>
            <li><strong>Location:</strong> {client_data['location']}</li>
            </ul>
            <p>Please follow up with the client.</p>
            <p><strong>Client ID:</strong> {client_id}</p>
            </body>
            </html>
            """
            send_email_notification(partner_email, subject, body)
    return client_id

def add_listing(listing_data):
    listing_id = f"L{len(st.session_state.listings) + 1:04d}"
    new_row = pd.DataFrame([{
        'Listing_ID': listing_id, 'Property_Address': listing_data['address'], 
        'Location': listing_data['location'], 'Property_Category': listing_data['property_category'], 
        'Property_Type': listing_data['property_type'],
        'Furnishing_Status': listing_data.get('furnishing_status', 'N/A'),
        'BHK': listing_data['bhk'], 'Price': listing_data['price'], 
        'Price_Currency': listing_data['price_currency'], 'Area_SqFt': listing_data['area'], 
        'Broker_Name': listing_data['broker_name'], 'Broker_Contact': listing_data['broker_contact'], 
        'Amenities': listing_data['amenities'], 'Listing_Status': 'Available',
        'Date_Added': datetime.now().strftime('%Y-%m-%d'),
        'Visible_To_Partner': listing_data['visible_to_partner'], 'Notes': listing_data['notes'],
        'Assigned_To': listing_data.get('assigned_to', 'Unassigned'), 'Shown_To_Clients': ''
    }])
    st.session_state.listings = pd.concat([st.session_state.listings, new_row], ignore_index=True)
    # Save to Google Sheets
    if st.session_state.gs_client and st.session_state.gs_config:
        save_to_sheets(st.session_state.gs_client, st.session_state.gs_config['listings_sheet_id'], st.session_state.listings)
    return listing_id

def add_deal(deal_data):
    deal_id = f"D{len(st.session_state.deals) + 1:04d}"
    
    # Calculate: Total = Owner + Client
    total_brokerage = deal_data['brokerage_owner'] + deal_data['brokerage_client']
    
    # Divide by number of brokers, then 90/10 split
    num_brokers = deal_data['num_brokers']
    brokerage_per_broker = total_brokerage / num_brokers
    your_share = brokerage_per_broker * 0.90
    partner_share = brokerage_per_broker * 0.10
    
    new_deal = pd.DataFrame([{
        'Deal_ID': deal_id,
        'Client_ID': deal_data['client_id'],
        'Listing_ID': deal_data['listing_id'],
        'Brokerage_From_Owner': deal_data['brokerage_owner'],
        'Brokerage_From_Client': deal_data['brokerage_client'],
        'Total_Brokerage': total_brokerage,
        'Number_Of_Brokers': num_brokers,
        'Your_Share': your_share,
        'Partner_Share': partner_share,
        'Partner_Name': deal_data['partner_name'],
        'Deal_Date': datetime.now().strftime('%Y-%m-%d'),
        'Payment_Status': 'Pending',
        'Notes': deal_data.get('notes', '')
    }])
    st.session_state.deals = pd.concat([st.session_state.deals, new_deal], ignore_index=True)
    # Save to Google Sheets
    if st.session_state.gs_client and st.session_state.gs_config:
        save_to_sheets(st.session_state.gs_client, st.session_state.gs_config['deals_sheet_id'], st.session_state.deals)
    return deal_id

def delete_client(client_id):
    st.session_state.clients = st.session_state.clients[st.session_state.clients['Client_ID'] != client_id]
    # Save to Google Sheets
    if st.session_state.gs_client and st.session_state.gs_config:
        save_to_sheets(st.session_state.gs_client, st.session_state.gs_config['clients_sheet_id'], st.session_state.clients)

def delete_listing(listing_id):
    st.session_state.listings = st.session_state.listings[st.session_state.listings['Listing_ID'] != listing_id]
    # Save to Google Sheets
    if st.session_state.gs_client and st.session_state.gs_config:
        save_to_sheets(st.session_state.gs_client, st.session_state.gs_config['listings_sheet_id'], st.session_state.listings)

def update_client_status(client_id, new_status):
    st.session_state.clients.loc[st.session_state.clients['Client_ID'] == client_id, 'Status'] = new_status
    # Save to Google Sheets
    if st.session_state.gs_client and st.session_state.gs_config:
        save_to_sheets(st.session_state.gs_client, st.session_state.gs_config['clients_sheet_id'], st.session_state.clients)

def update_listing_status(listing_id, new_status, shown_to_clients=''):
    st.session_state.listings.loc[st.session_state.listings['Listing_ID'] == listing_id, 'Listing_Status'] = new_status
    if shown_to_clients:
        st.session_state.listings.loc[st.session_state.listings['Listing_ID'] == listing_id, 'Shown_To_Clients'] = shown_to_clients
    # Save to Google Sheets
    if st.session_state.gs_client and st.session_state.gs_config:
        save_to_sheets(st.session_state.gs_client, st.session_state.gs_config['listings_sheet_id'], st.session_state.listings)

def initialize_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None
    if 'username' not in st.session_state:
        st.session_state.username = None

def login_page():
    st.markdown('<div class="main-header">🏠 Lyns Real Estate CRM</div>', unsafe_allow_html=True)
    st.markdown("### Please login to continue")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            success, role, full_name = authenticate(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.user_role = role
                st.session_state.user_name = full_name
                st.session_state.username = username
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

def logout():
    st.session_state.logged_in = False
    st.rerun()


def admin_dashboard():
    st.sidebar.markdown(f"### 👤 {st.session_state.user_name}")
    st.sidebar.markdown(f"**Role:** {st.session_state.user_role}")
    menu = st.sidebar.radio("Navigation", 
        ["📊 Dashboard", "👥 Clients", "🏢 Listings", "💰 Deals", "👤 Users", "📈 Reports"])
    if st.sidebar.button("🚪 Logout"):
        logout()
    
    if menu == "📊 Dashboard":
        show_admin_dashboard()
    elif menu == "👥 Clients":
        show_clients_page(True)
    elif menu == "🏢 Listings":
        show_listings_page(True)
    elif menu == "💰 Deals":
        show_deals_page()
    elif menu == "👤 Users":
        show_users_page()
    else:
        show_reports()

def show_admin_dashboard():
    st.markdown('<div class="main-header">📊 Admin Dashboard</div>', unsafe_allow_html=True)
    
    clients_df = st.session_state.clients
    listings_df = st.session_state.listings
    deals_df = st.session_state.deals
    
    # Summary Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><h3>{len(clients_df)}</h3><p>Total Clients</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h3>{len(listings_df)}</h3><p>Total Listings</p></div>', unsafe_allow_html=True)
    with col3:
        deals_closed = len(deals_df)
        st.markdown(f'<div class="metric-card"><h3>{deals_closed}</h3><p>Deals Closed</p></div>', unsafe_allow_html=True)
    with col4:
        total_brokerage = deals_df['Total_Brokerage'].sum() if not deals_df.empty else 0
        st.markdown(f'<div class="metric-card"><h3>₹{total_brokerage:,.0f}</h3><p>Total Brokerage</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Status Breakdown
    if not clients_df.empty:
        st.subheader("📊 Client Status Breakdown")
        col1, col2 = st.columns(2)
        with col1:
            status_counts = clients_df['Status'].value_counts()
            for status, count in status_counts.items():
                st.metric(status, count)
        with col2:
            st.bar_chart(status_counts)
    
    st.markdown("---")
    
    # Recent Activity
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📋 Recent Clients")
        if not clients_df.empty:
            st.dataframe(clients_df.tail(5), use_container_width=True, hide_index=True)
        else:
            st.info("No clients yet")
    
    with col2:
        st.subheader("💰 Recent Deals")
        if not deals_df.empty:
            st.dataframe(deals_df.tail(5), use_container_width=True, hide_index=True)
        else:
            st.info("No deals yet")


def show_clients_page(is_admin):
    st.markdown('<div class="main-header">👥 Clients</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 View & Manage", "➕ Add New"])
    
    with tab1:
        if not st.session_state.clients.empty:
            st.dataframe(st.session_state.clients, use_container_width=True, hide_index=True)
            
            if is_admin:
                st.markdown("### 🗑️ Delete Client")
                del_client = st.selectbox("Select client to delete", 
                                         st.session_state.clients['Client_Name'].tolist())
                if st.button("🗑️ Delete Selected Client", type="secondary"):
                    client_id = st.session_state.clients[st.session_state.clients['Client_Name'] == del_client]['Client_ID'].values[0]
                    delete_client(client_id)
                    st.success(f"✅ Deleted: {del_client}")
                    st.rerun()
        else:
            st.info("No clients yet!")
    
    with tab2:
        if is_admin:
            show_add_client_form()
        else:
            st.warning("Admin only")

def show_add_client_form():
    st.subheader("Add New Client")
    client_type_temp = st.selectbox("Client Type *", ["Sale", "Rental"], key="temp_ct")
    property_category_temp = st.selectbox("Property Category *", ["Residential", "Commercial"], key="temp_pc")
    
    with st.form("client_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Client Name *")
            contact = st.text_input("Contact *")
            email = st.text_input("Email")
        with col2:
            client_type = client_type_temp
            property_category = property_category_temp
            if property_category == "Residential":
                property_type = st.selectbox("Property Type *", 
                    ["Apartment", "Villa", "Independent House", "Penthouse", "Studio"])
            else:
                property_type = st.selectbox("Property Type *", 
                    ["Office Space", "Warehouse", "Shop/Showroom", "Land/Plot", "Industrial Unit", "Co-working Space"])
        
        furnishing_status = None
        if property_category == "Residential":
            furnishing_status = st.selectbox("Furnishing *", ["Furnished", "Semi-Furnished", "Unfurnished"])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            currency = st.selectbox("Currency *", ["₹ Rupees", "₹ Lakhs", "₹ Crores"])
        with col2:
            if currency == "₹ Rupees":
                bmin = st.number_input("Min *", 10000, 500000000, 500000, 10000)
            elif currency == "₹ Lakhs":
                bmin = st.number_input("Min (L) *", 0.1, 5000.0, 50.0, 5.0)
            else:
                bmin = st.number_input("Min (Cr) *", 0.01, 50.0, 1.0, 0.5)
        with col3:
            if currency == "₹ Rupees":
                bmax = st.number_input("Max *", 10000, 500000000, 1000000, 10000)
            elif currency == "₹ Lakhs":
                bmax = st.number_input("Max (L) *", 0.1, 5000.0, 80.0, 5.0)
            else:
                bmax = st.number_input("Max (Cr) *", 0.01, 50.0, 2.0, 0.5)
        
        location = st.multiselect("Location *", LOCATIONS)
        location_str = ", ".join(location) if location else ""
        
        if property_category == "Residential":
            bhk = st.selectbox("BHK *", ["Studio", "1 BHK", "2 BHK", "3 BHK", "4 BHK", "5+ BHK"])
        else:
            bhk = st.text_input("Size", "e.g., 2000 sq ft")
        
        requirements = st.text_area("Requirements")
        
        poss_date = None
        if client_type == "Rental":
            st.markdown("### 📅 Rental Details")
            poss_date = st.date_input("Possession Date *", min_value=date.today())
        
        # Get list of partners for assignment
        partners = st.session_state.users[st.session_state.users['Role'] == 'Partner']['Full_Name'].tolist()
        assign_options = ["Unassigned", "Admin"] + partners
        
        col1, col2, col3 = st.columns(3)
        with col1:
            source = st.selectbox("Source *", ["SquareYards", "Referral", "Direct", "Website", "Other"])
        with col2:
            assigned = st.selectbox("Assign To", assign_options)
        with col3:
            priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        
        if st.form_submit_button("✅ Add Client", use_container_width=True):
            if name and contact and location_str:
                data = {
                    'name': name, 'contact': contact, 'email': email, 'client_type': client_type,
                    'property_category': property_category, 'property_type': property_type,
                    'furnishing_status': furnishing_status if furnishing_status else 'N/A',
                    'budget_min': bmin, 'budget_max': bmax, 'budget_currency': currency,
                    'location': location_str, 'bhk': bhk, 'requirements': requirements,
                    'possession_date': poss_date.strftime('%Y-%m-%d') if poss_date else '',
                    'assigned_to': assigned, 'source': source, 'priority': priority
                }
                cid = add_client(data)
                st.success(f"✅ Client added! ID: {cid}")
                st.balloons()
            else:
                st.error("❌ Fill required fields")


def show_listings_page(is_admin):
    st.markdown('<div class="main-header">🏢 Independent Listings</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["📋 View & Manage", "➕ Add New"])
    
    with tab1:
        if not st.session_state.listings.empty:
            st.dataframe(st.session_state.listings, use_container_width=True, hide_index=True)
            
            if is_admin:
                st.markdown("### 🗑️ Delete Listing")
                del_listing = st.selectbox("Select listing to delete", 
                                          st.session_state.listings['Property_Address'].tolist())
                if st.button("🗑️ Delete Selected Listing", type="secondary"):
                    listing_id = st.session_state.listings[st.session_state.listings['Property_Address'] == del_listing]['Listing_ID'].values[0]
                    delete_listing(listing_id)
                    st.success(f"✅ Deleted: {del_listing}")
                    st.rerun()
        else:
            st.info("No listings yet!")
    
    with tab2:
        if is_admin:
            show_add_listing_form()
        else:
            st.warning("Admin only")

def show_add_listing_form():
    st.subheader("Add New Listing (Independent)")
    cat_temp = st.selectbox("Property Category *", ["Residential", "Commercial"], key="temp_lc")
    
    with st.form("listing_form"):
        col1, col2 = st.columns(2)
        with col1:
            cat = cat_temp
            if cat == "Residential":
                ptype = st.selectbox("Type *", ["Apartment", "Villa", "House", "Penthouse", "Studio"])
            else:
                ptype = st.selectbox("Type *", ["Office Space", "Warehouse", "Shop/Showroom", "Land/Plot", "Industrial Unit", "Co-working Space"])
        with col2:
            addr = st.text_input("Address *")
            loc = st.selectbox("Location *", LOCATIONS)
        
        furn = None
        if cat == "Residential":
            furn = st.selectbox("Furnishing *", ["Furnished", "Semi-Furnished", "Unfurnished"])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            bhk = st.text_input("BHK/Size *")
        with col2:
            curr = st.selectbox("Currency", ["₹ Rupees", "₹ Lakhs", "₹ Crores"])
        with col3:
            if curr == "₹ Rupees":
                pr = st.number_input("Price *", 10000, 500000000, 5000000, 10000)
            elif curr == "₹ Lakhs":
                pr = st.number_input("Price (L) *", 0.1, 5000.0, 95.0, 5.0)
            else:
                pr = st.number_input("Price (Cr) *", 0.01, 50.0, 1.5, 0.1)
        
        area = st.number_input("Area (sq ft) *", 100, 100000, 850, 50)
        amen = st.text_area("Amenities")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            bname = st.text_input("Broker Name *")
        with col2:
            bcontact = st.text_input("Broker Contact *")
        with col3:
            vis = st.selectbox("Visible to Partner? *", ["Yes", "No"])
        
        partners = st.session_state.users[st.session_state.users['Role'] == 'Partner']['Full_Name'].tolist()
        assign_options = ["Unassigned", "Admin"] + partners
        assigned = st.selectbox("Assign To", assign_options)
        notes = st.text_area("Notes")
        
        if st.form_submit_button("✅ Add Listing", use_container_width=True):
            if addr and loc and bname and bcontact and bhk:
                ldata = {
                    'address': addr, 'location': loc, 'property_category': cat,
                    'property_type': ptype, 'furnishing_status': furn if furn else 'N/A',
                    'bhk': bhk, 'price': pr, 'price_currency': curr, 'area': area,
                    'broker_name': bname, 'broker_contact': bcontact, 'amenities': amen,
                    'visible_to_partner': vis, 'notes': notes, 'assigned_to': assigned
                }
                lid = add_listing(ldata)
                st.success(f"✅ Listing added! ID: {lid}")
                st.balloons()
            else:
                st.error("❌ Fill required fields")

def show_deals_page():
    st.markdown('<div class="main-header">💰 Deals & Commission</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 View Deals", "➕ Close New Deal"])
    
    with tab1:
        if not st.session_state.deals.empty:
            st.dataframe(st.session_state.deals, use_container_width=True, hide_index=True)
            
            st.markdown("### 🗑️ Delete Deal")
            del_deal = st.selectbox("Select deal to delete", 
                                   st.session_state.deals['Deal_ID'].tolist(),
                                   key="del_deal_select")
            if st.button("🗑️ Delete Selected Deal", type="secondary"):
                delete_deal(del_deal)
                st.success(f"✅ Deleted deal: {del_deal}")
                st.rerun()
            
            # Commission Summary
            st.markdown("### 💰 Commission Summary")
            total_brokerage = st.session_state.deals['Total_Brokerage'].sum()
            your_total = st.session_state.deals['Your_Share'].sum()
            partner_total = st.session_state.deals['Partner_Share'].sum()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Brokerage", f"₹{total_brokerage:,.0f}")
            with col2:
                st.metric("Your Share (90%)", f"₹{your_total:,.0f}")
            with col3:
                st.metric("Partners Share (10%)", f"₹{partner_total:,.0f}")
        else:
            st.info("No deals closed yet")
    
    with tab2:
        show_close_deal_form()

def show_close_deal_form():
    st.subheader("Close New Deal (Admin Only)")
    
    if st.session_state.clients.empty:
        st.warning("⚠️ Add clients first")
        return
    
    # Client selection
    client_opts = {f"{r['Client_Name']} ({r['Client_ID']})": r['Client_ID'] 
                  for _, r in st.session_state.clients.iterrows()}
    selected_client = st.selectbox("Client *", list(client_opts.keys()))
    
    # Listing selection (optional)
    listing_opts = {"No specific listing": "N/A"}
    if not st.session_state.listings.empty:
        listing_opts.update({f"{r['Property_Address']} ({r['Listing_ID']})": r['Listing_ID'] 
                            for _, r in st.session_state.listings.iterrows()})
    selected_listing = st.selectbox("Property Listing (Optional)", list(listing_opts.keys()))
    
    st.markdown("### 💰 Brokerage Details")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        brokerage_owner = st.number_input("Brokerage from Owner (₹) *", min_value=0, value=25000, step=1000, key="brk_owner")
    with col2:
        brokerage_client = st.number_input("Brokerage from Client (₹) *", min_value=0, value=25000, step=1000, key="brk_client")
    with col3:
        num_brokers = st.number_input("Number of Brokers in Deal *", min_value=1, max_value=10, value=1, step=1, key="num_brk")
    
    # Live calculation
    total_brokerage = brokerage_owner + brokerage_client
    brokerage_per_broker = total_brokerage / num_brokers
    your_share = brokerage_per_broker * 0.90
    partner_share = brokerage_per_broker * 0.10
    
    st.markdown("### 📊 Commission Breakdown")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Brokerage", f"₹{total_brokerage:,.0f}")
    with col2:
        st.metric("Per Broker", f"₹{brokerage_per_broker:,.0f}")
    with col3:
        st.metric("Your Share (90%)", f"₹{your_share:,.0f}")
    with col4:
        st.metric("Partner Share (10%)", f"₹{partner_share:,.0f}")
    
    # Partner selection
    partners = st.session_state.users[st.session_state.users['Role'] == 'Partner']['Full_Name'].tolist()
    partner_name = st.selectbox("Partner who worked on this *", partners if partners else ["No partners"])
    
    notes = st.text_area("Deal Notes")
    
    if st.button("✅ Close Deal", use_container_width=True, type="primary"):
        if partner_name and partner_name != "No partners":
            deal_data = {
                'client_id': client_opts[selected_client],
                'listing_id': listing_opts[selected_listing],
                'brokerage_owner': brokerage_owner,
                'brokerage_client': brokerage_client,
                'num_brokers': num_brokers,
                'partner_name': partner_name,
                'notes': notes
            }
            deal_id = add_deal(deal_data)
            
            # Update client status
            update_client_status(client_opts[selected_client], 'Deal Closed')
            
            st.success(f"✅ Deal closed! ID: {deal_id}")
            st.balloons()
        else:
            st.error("❌ Select a partner")

def show_users_page():
    st.markdown('<div class="main-header">👤 User Management</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 View Users", "➕ Add New User", "✏️ Edit User"])
    
    with tab1:
        st.subheader("Current Users")
        users_display = st.session_state.users[['Username', 'Full_Name', 'Email', 'Role', 'Status']].copy()
        st.dataframe(users_display, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("### 🔄 Enable/Disable User")
        
        non_admin_users = st.session_state.users[st.session_state.users['Username'] != 'admin']
        if not non_admin_users.empty:
            user_to_toggle = st.selectbox("Select User", non_admin_users['Username'].tolist(), key="toggle_user")
            current_status = st.session_state.users[st.session_state.users['Username'] == user_to_toggle]['Status'].values[0]
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"Current Status: **{current_status}**")
            with col2:
                if current_status == 'Active':
                    if st.button("🚫 Disable User", type="secondary"):
                        st.session_state.users.loc[st.session_state.users['Username'] == user_to_toggle, 'Status'] = 'Inactive'
                        if st.session_state.gs_client and st.session_state.gs_config:
                            save_to_sheets(st.session_state.gs_client, st.session_state.gs_config['users_sheet_id'], st.session_state.users)
                        st.success(f"✅ User {user_to_toggle} disabled")
                        st.rerun()
                else:
                    if st.button("✅ Enable User", type="primary"):
                        st.session_state.users.loc[st.session_state.users['Username'] == user_to_toggle, 'Status'] = 'Active'
                        if st.session_state.gs_client and st.session_state.gs_config:
                            save_to_sheets(st.session_state.gs_client, st.session_state.gs_config['users_sheet_id'], st.session_state.users)
                        st.success(f"✅ User {user_to_toggle} enabled")
                        st.rerun()
        else:
            st.info("No users to manage (Admin cannot be disabled)")
        
        st.markdown("---")
        st.markdown("### 🗑️ Delete User")
        
        if not non_admin_users.empty:
            user_to_delete = st.selectbox("Select User to Delete", non_admin_users['Username'].tolist(), key="delete_user_select")
            st.warning("⚠️ This action cannot be undone!")
            if st.button("🗑️ Delete User Permanently", type="secondary"):
                delete_user(user_to_delete)
                st.success(f"✅ User {user_to_delete} deleted permanently")
                st.rerun()
        else:
            st.info("No users to delete")
    
    with tab2:
        st.subheader("Add New User")
        with st.form("user_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_username = st.text_input("Username *")
                new_fullname = st.text_input("Full Name *")
                new_email = st.text_input("Email *")
            with col2:
                new_password = st.text_input("Password *", type="password")
                confirm_password = st.text_input("Confirm Password *", type="password")
            
            new_role = st.selectbox("Role *", ["Partner", "Admin"])
            
            if st.form_submit_button("✅ Create User", use_container_width=True):
                if not new_username or not new_password or not new_fullname or not new_email:
                    st.error("❌ Fill all required fields")
                elif new_password != confirm_password:
                    st.error("❌ Passwords don't match")
                elif new_username in st.session_state.users['Username'].values:
                    st.error("❌ Username already exists")
                else:
                    add_user(new_username, new_password, new_role, new_fullname, new_email)
                    st.success(f"✅ User created: {new_username} ({new_role})")
                    st.balloons()
    
    with tab3:
        st.subheader("Edit User Details")
        
        edit_user = st.selectbox("Select User to Edit", st.session_state.users['Username'].tolist(), key="edit_user_select")
        user_data = st.session_state.users[st.session_state.users['Username'] == edit_user].iloc[0]
        
        with st.form("edit_user_form"):
            st.info(f"Editing: **{edit_user}**")
            
            col1, col2 = st.columns(2)
            with col1:
                edit_fullname = st.text_input("Full Name *", value=user_data['Full_Name'])
                edit_email = st.text_input("Email *", value=user_data['Email'])
                edit_role = st.selectbox("Role *", ["Partner", "Admin"], 
                                        index=0 if user_data['Role'] == 'Partner' else 1)
            with col2:
                edit_password = st.text_input("New Password (leave blank to keep current)", type="password")
                confirm_edit_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("✅ Update User", use_container_width=True):
                if not edit_fullname or not edit_email:
                    st.error("❌ Full name and email are required")
                elif edit_password and edit_password != confirm_edit_password:
                    st.error("❌ Passwords don't match")
                else:
                    st.session_state.users.loc[st.session_state.users['Username'] == edit_user, 'Full_Name'] = edit_fullname
                    st.session_state.users.loc[st.session_state.users['Username'] == edit_user, 'Role'] = edit_role
                    st.session_state.users.loc[st.session_state.users['Username'] == edit_user, 'Email'] = edit_email
                    
                    # Save to Google Sheets
                    if st.session_state.gs_client and st.session_state.gs_config:
                        save_to_sheets(st.session_state.gs_client, st.session_state.gs_config['users_sheet_id'], st.session_state.users)
                    
                    if edit_password:
                        st.session_state.users.loc[st.session_state.users['Username'] == edit_user, 'Password'] = hash_password(edit_password)
                        st.success(f"✅ Updated {edit_user} (including password)")
                    else:
                        st.success(f"✅ Updated {edit_user}")
                    st.balloons()
                    st.rerun()


def show_reports():
    st.markdown('<div class="main-header">📈 Reports & Analytics</div>', unsafe_allow_html=True)
    
    clients_df = st.session_state.clients
    listings_df = st.session_state.listings
    deals_df = st.session_state.deals
    
    if not clients_df.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Client Type Distribution")
            st.bar_chart(clients_df['Client_Type'].value_counts())
        with col2:
            st.subheader("Property Category")
            st.bar_chart(clients_df['Property_Category'].value_counts())
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Priority Levels")
            st.bar_chart(clients_df['Priority'].value_counts())
        with col2:
            st.subheader("Assignment Status")
            st.bar_chart(clients_df['Assigned_To'].value_counts())
        
        st.markdown("---")
        
        st.subheader("Client Status Pipeline")
        st.bar_chart(clients_df['Status'].value_counts())
    else:
        st.info("📊 No data yet! Add clients to see reports.")


def partner_dashboard():
    st.sidebar.markdown(f"### 👤 {st.session_state.user_name}")
    st.sidebar.markdown(f"**Role:** {st.session_state.user_role}")
    menu = st.sidebar.radio("Navigation", ["📊 Dashboard", "👥 My Clients", "🏢 My Listings"])
    if st.sidebar.button("🚪 Logout"):
        logout()
    
    if menu == "📊 Dashboard":
        show_partner_dashboard_home()
    elif menu == "👥 My Clients":
        show_partner_clients()
    else:
        show_partner_listings()

def show_partner_dashboard_home():
    st.markdown('<div class="main-header">📊 Partner Dashboard</div>', unsafe_allow_html=True)
    
    partner_name = st.session_state.user_name
    my_clients = st.session_state.clients[st.session_state.clients['Assigned_To'].str.contains(partner_name, case=False, na=False)]
    my_listings = st.session_state.listings[
        (st.session_state.listings['Assigned_To'].str.contains(partner_name, case=False, na=False)) & 
        (st.session_state.listings['Visible_To_Partner'] == 'Yes')
    ]
    my_deals = st.session_state.deals[st.session_state.deals['Partner_Name'].str.contains(partner_name, case=False, na=False)]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card"><h3>{len(my_clients)}</h3><p>My Clients</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h3>{len(my_listings)}</h3><p>My Listings</p></div>', unsafe_allow_html=True)
    with col3:
        my_commission = my_deals['Partner_Share'].sum() if not my_deals.empty else 0
        st.markdown(f'<div class="metric-card"><h3>₹{my_commission:,.0f}</h3><p>My Commission</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Status breakdown
    if not my_clients.empty:
        st.subheader("📊 My Client Status")
        status_counts = my_clients['Status'].value_counts()
        col1, col2 = st.columns(2)
        with col1:
            for status, count in status_counts.items():
                st.metric(status, count)
        with col2:
            st.bar_chart(status_counts)
    
    st.markdown("---")
    
    if not my_clients.empty:
        st.subheader("👥 Recent Clients")
        st.dataframe(my_clients.tail(5), use_container_width=True, hide_index=True)

def show_partner_clients():
    st.markdown('<div class="main-header">👥 My Clients</div>', unsafe_allow_html=True)
    
    partner_name = st.session_state.user_name
    my_clients = st.session_state.clients[st.session_state.clients['Assigned_To'].str.contains(partner_name, case=False, na=False)]
    
    if not my_clients.empty:
        st.dataframe(my_clients, use_container_width=True, hide_index=True)
        
        st.markdown("### ✏️ Update Client Status")
        client_to_update = st.selectbox("Select Client", my_clients['Client_Name'].tolist())
        new_status = st.selectbox("New Status", 
            ["New Lead", "Contacted", "Site Visit Scheduled", "Site Visit Done", "Interested", 
             "Negotiation", "Deal in Progress", "On Hold", "Not Interested"])
        
        if st.button("✅ Update Status"):
            client_id = my_clients[my_clients['Client_Name'] == client_to_update]['Client_ID'].values[0]
            update_client_status(client_id, new_status)
            st.success(f"✅ Updated {client_to_update} to: {new_status}")
            st.rerun()
    else:
        st.info("📭 No clients assigned yet")

def show_partner_listings():
    st.markdown('<div class="main-header">🏢 My Listings</div>', unsafe_allow_html=True)
    
    partner_name = st.session_state.user_name
    my_clients = st.session_state.clients[st.session_state.clients['Assigned_To'].str.contains(partner_name, case=False, na=False)]
    my_listings = st.session_state.listings[
        (st.session_state.listings['Assigned_To'].str.contains(partner_name, case=False, na=False)) & 
        (st.session_state.listings['Visible_To_Partner'] == 'Yes')
    ]
    
    if not my_listings.empty:
        for idx, listing in my_listings.iterrows():
            with st.expander(f"🏢 {listing['Property_Address']} - {listing['Location']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Type:** {listing['Property_Type']}")
                    st.write(f"**BHK/Size:** {listing['BHK']}")
                    st.write(f"**Price:** {listing['Price_Currency']} {listing['Price']}")
                with col2:
                    st.write(f"**Area:** {listing['Area_SqFt']} sq ft")
                    st.write(f"**Furnishing:** {listing['Furnishing_Status']}")
                    st.write(f"**Status:** {listing['Listing_Status']}")
                with col3:
                    st.write(f"**Broker:** {listing['Broker_Name']}")
                    st.write(f"**Contact:** {listing['Broker_Contact']}")
                
                st.write(f"**Amenities:** {listing['Amenities']}")
                
                if listing.get('Shown_To_Clients'):
                    st.info(f"👥 Previously shown to: {listing['Shown_To_Clients']}")
                
                st.markdown("### ✏️ Update Listing Status")
                new_status = st.selectbox(
                    "Status", 
                    ["Available", "Shown to Client", "Client Interested", "Under Negotiation", "Not Available"],
                    key=f"status_{listing['Listing_ID']}"
                )
                
                shown_to_clients = ''
                if new_status == "Shown to Client" and not my_clients.empty:
                    selected_clients = st.multiselect(
                        "Which clients did you show this to?",
                        my_clients['Client_Name'].tolist(),
                        key=f"clients_{listing['Listing_ID']}"
                    )
                    shown_to_clients = ", ".join(selected_clients) if selected_clients else ''
                
                if st.button("✅ Update", key=f"btn_{listing['Listing_ID']}"):
                    update_listing_status(listing['Listing_ID'], new_status, shown_to_clients)
                    st.success(f"✅ Updated!")
                    if shown_to_clients:
                        st.success(f"📝 Recorded: Shown to {shown_to_clients}")
                    st.rerun()
    else:
        st.info("📭 No listings assigned yet")

def main():
    initialize_session_state()
    initialize_data()
    if not st.session_state.logged_in:
        login_page()
    elif st.session_state.user_role == "Admin":
        admin_dashboard()
    else:
        partner_dashboard()

if __name__ == "__main__":
    main()





























