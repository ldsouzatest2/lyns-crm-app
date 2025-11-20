"""
Lyns Real Estate CRM - Streamlit Application
A complete CRM system for managing clients, property listings, site visits, and deals
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import json

# Page configuration
st.set_page_config(
    page_title="Lyns Real Estate CRM",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== DATA STORAGE (In-Memory for Demo) ====================

# Initialize session state for data storage
def initialize_data():
    if 'clients' not in st.session_state:
        st.session_state.clients = pd.DataFrame(columns=[
            'Client_ID', 'Client_Name', 'Contact_Number', 'Email', 'Budget_Min', 
            'Budget_Max', 'Location_Preference', 'BHK_Requirement', 'Requirements_Notes',
            'Status', 'Assigned_To', 'Date_Registered', 'Source', 'Priority'
        ])
    
    if 'listings' not in st.session_state:
        st.session_state.listings = pd.DataFrame(columns=[
            'Listing_ID', 'Client_ID', 'Property_Address', 'Location', 'BHK', 'Price',
            'Area_SqFt', 'Broker_Name', 'Broker_Contact', 'Amenities', 'Listing_Status',
            'Date_Added', 'Visible_To_Partner', 'Notes'
        ])
    
    if 'site_visits' not in st.session_state:
        st.session_state.site_visits = pd.DataFrame(columns=[
            'Visit_ID', 'Client_ID', 'Listing_ID', 'Partner_Name', 'Visit_Date',
            'Visit_Time', 'Client_Reaction', 'Client_Feedback', 'Next_Steps',
            'Follow_Up_Date', 'Status'
        ])
    
    if 'deals' not in st.session_state:
        st.session_state.deals = pd.DataFrame(columns=[
            'Deal_ID', 'Client_ID', 'Listing_ID', 'Deal_Stage', 'Negotiated_Price',
            'Token_Amount', 'Final_Price', 'Close_Date', 'Commission_Total',
            'Your_Share', 'Partner_Share', 'Payment_Status', 'Payment_Date', 'Notes'
        ])

def add_client(client_data):
    client_id = f"C{len(st.session_state.clients) + 1:04d}"
    new_row = pd.DataFrame([{
        'Client_ID': client_id,
        'Client_Name': client_data['name'],
        'Contact_Number': client_data['contact'],
        'Email': client_data['email'],
        'Budget_Min': client_data['budget_min'],
        'Budget_Max': client_data['budget_max'],
        'Location_Preference': client_data['location'],
        'BHK_Requirement': client_data['bhk'],
        'Requirements_Notes': client_data['requirements'],
        'Status': 'Active',
        'Assigned_To': client_data['assigned_to'],
        'Date_Registered': datetime.now().strftime('%Y-%m-%d'),
        'Source': client_data['source'],
        'Priority': client_data['priority']
    }])
    st.session_state.clients = pd.concat([st.session_state.clients, new_row], ignore_index=True)
    return client_id

def add_listing(listing_data):
    listing_id = f"L{len(st.session_state.listings) + 1:04d}"
    new_row = pd.DataFrame([{
        'Listing_ID': listing_id,
        'Client_ID': listing_data['client_id'],
        'Property_Address': listing_data['address'],
        'Location': listing_data['location'],
        'BHK': listing_data['bhk'],
        'Price': listing_data['price'],
        'Area_SqFt': listing_data['area'],
        'Broker_Name': listing_data['broker_name'],
        'Broker_Contact': listing_data['broker_contact'],
        'Amenities': listing_data['amenities'],
        'Listing_Status': 'Available',
        'Date_Added': datetime.now().strftime('%Y-%m-%d'),
        'Visible_To_Partner': listing_data['visible_to_partner'],
        'Notes': listing_data['notes']
    }])
    st.session_state.listings = pd.concat([st.session_state.listings, new_row], ignore_index=True)
    return listing_id


# ==================== AUTHENTICATION & SESSION STATE ====================

def initialize_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None

def login_page():
    st.markdown('<div class="main-header">🏠 Lyns Real Estate CRM</div>', unsafe_allow_html=True)
    st.markdown("### Please login to continue")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        user_role = st.selectbox(
            "Select Your Role",
            ["Admin (Lyndon)", "Partner A"],
            key="role_select"
        )
        
        password = st.text_input("Password", type="password", key="password_input")
        
        if st.button("Login", use_container_width=True):
            if password == "lyns2024":
                st.session_state.logged_in = True
                st.session_state.user_role = "Admin" if "Admin" in user_role else "Partner"
                st.session_state.user_name = user_role.split("(")[0].strip()
                st.rerun()
            else:
                st.error("❌ Invalid password")
        
        st.info("💡 Demo password: lyns2024")
        st.warning("⚠️ Running in DEMO MODE - Data stored in memory only (will reset when you refresh)")

def logout():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_name = None
    st.rerun()


# ==================== ADMIN DASHBOARD ====================

def admin_dashboard():
    st.sidebar.markdown(f"### 👤 Welcome, {st.session_state.user_name}!")
    st.sidebar.markdown(f"**Role:** {st.session_state.user_role}")
    
    menu = st.sidebar.radio(
        "Navigation",
        ["📊 Dashboard", "👥 Clients", "🏢 Listings", "📈 Reports"],
        key="admin_menu"
    )
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
    
    if menu == "📊 Dashboard":
        show_admin_dashboard_home()
    elif menu == "👥 Clients":
        show_clients_page(is_admin=True)
    elif menu == "🏢 Listings":
        show_listings_page(is_admin=True)
    elif menu == "📈 Reports":
        show_reports_page()

def show_admin_dashboard_home():
    st.markdown('<div class="main-header">📊 Admin Dashboard</div>', unsafe_allow_html=True)
    
    clients_df = st.session_state.clients
    listings_df = st.session_state.listings
    deals_df = st.session_state.deals
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_clients = len(clients_df)
        active_clients = len(clients_df[clients_df['Status'] == 'Active']) if not clients_df.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_clients}</h3>
            <p>Total Clients</p>
            <small>{active_clients} Active</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_listings = len(listings_df)
        available_listings = len(listings_df[listings_df['Listing_Status'] == 'Available']) if not listings_df.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_listings}</h3>
            <p>Total Listings</p>
            <small>{available_listings} Available</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        deals_closed = len(deals_df[deals_df['Deal_Stage'] == 'Deal Closed']) if not deals_df.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>{deals_closed}</h3>
            <p>Deals Closed</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        total_commission = deals_df['Commission_Total'].sum() if not deals_df.empty and 'Commission_Total' in deals_df.columns else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>₹{total_commission:,.0f}</h3>
            <p>Total Commission</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Recent Clients")
        if not clients_df.empty:
            recent_clients = clients_df.sort_values('Date_Registered', ascending=False).head(5)
            st.dataframe(
                recent_clients[['Client_Name', 'BHK_Requirement', 'Status', 'Assigned_To']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No clients yet. Add your first client!")
    
    with col2:
        st.subheader("🎯 Priority Clients")
        if not clients_df.empty:
            priority_clients = clients_df[clients_df['Priority'] == 'High'].head(5)
            if not priority_clients.empty:
                st.dataframe(
                    priority_clients[['Client_Name', 'Location_Preference', 'Status']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No high priority clients")
        else:
            st.info("No clients yet")


# ==================== CLIENTS PAGE ====================

def show_clients_page(is_admin=True):
    st.markdown('<div class="main-header">👥 Client Management</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 View Clients", "➕ Add New Client"])
    
    with tab1:
        clients_df = st.session_state.clients
        
        if not clients_df.empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.multiselect(
                    "Status",
                    options=clients_df['Status'].unique() if 'Status' in clients_df.columns else [],
                    default=None
                )
            
            with col2:
                assigned_filter = st.multiselect(
                    "Assigned To",
                    options=clients_df['Assigned_To'].unique() if 'Assigned_To' in clients_df.columns else [],
                    default=None
                )
            
            with col3:
                priority_filter = st.multiselect(
                    "Priority",
                    options=clients_df['Priority'].unique() if 'Priority' in clients_df.columns else [],
                    default=None
                )
            
            filtered_df = clients_df.copy()
            if status_filter:
                filtered_df = filtered_df[filtered_df['Status'].isin(status_filter)]
            if assigned_filter:
                filtered_df = filtered_df[filtered_df['Assigned_To'].isin(assigned_filter)]
            if priority_filter:
                filtered_df = filtered_df[filtered_df['Priority'].isin(priority_filter)]
            
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
            
            if not filtered_df.empty:
                st.markdown("### Client Details")
                selected_client = st.selectbox(
                    "Select a client to view details",
                    options=filtered_df['Client_Name'].tolist()
                )
                
                if selected_client:
                    client_data = filtered_df[filtered_df['Client_Name'] == selected_client].iloc[0]
                    show_client_details(client_data, is_admin)
        else:
            st.info("📭 No clients found. Add your first client using the 'Add New Client' tab!")
    
    with tab2:
        if is_admin:
            show_add_client_form()
        else:
            st.warning("⚠️ Only Admin can add new clients")

def show_add_client_form():
    st.subheader("Add New Client")
    
    with st.form("add_client_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Client Name *", placeholder="e.g., Rajesh Kumar")
            contact = st.text_input("Contact Number *", placeholder="e.g., +91 98765 43210")
            email = st.text_input("Email", placeholder="e.g., rajesh@email.com")
            
        with col2:
            budget_min = st.number_input("Budget Min (Lakhs) *", min_value=10, max_value=1000, value=80, step=5)
            budget_max = st.number_input("Budget Max (Lakhs) *", min_value=10, max_value=1000, value=100, step=5)
            bhk = st.selectbox("BHK Requirement *", ["1 BHK", "2 BHK", "3 BHK", "4 BHK", "5+ BHK"])
        
        location = st.text_input("Location Preference *", placeholder="e.g., Marol, Andheri East")
        requirements = st.text_area("Requirements & Notes", placeholder="e.g., Vegetarian family, good ventilation, parking mandatory")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            source = st.selectbox("Source *", ["SquareYards", "Referral", "Direct", "Website", "Other"])
        
        with col2:
            assigned_to = st.selectbox("Assign To", ["Unassigned", "Partner A", "Admin"])
        
        with col3:
            priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        
        submitted = st.form_submit_button("Add Client", use_container_width=True)
        
        if submitted:
            if name and contact and budget_min and budget_max and location and bhk:
                client_data = {
                    'name': name,
                    'contact': contact,
                    'email': email,
                    'budget_min': budget_min,
                    'budget_max': budget_max,
                    'location': location,
                    'bhk': bhk,
                    'requirements': requirements,
                    'assigned_to': assigned_to,
                    'source': source,
                    'priority': priority
                }
                
                client_id = add_client(client_data)
                st.success(f"✅ Client added successfully! Client ID: {client_id}")
                st.balloons()
            else:
                st.error("❌ Please fill all required fields marked with *")

def show_client_details(client_data, is_admin):
    with st.expander(f"📋 {client_data['Client_Name']} - Details", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Client ID:** {client_data['Client_ID']}")
            st.write(f"**Contact:** {client_data['Contact_Number']}")
            st.write(f"**Email:** {client_data.get('Email', 'N/A')}")
        
        with col2:
            st.write(f"**Budget:** ₹{client_data['Budget_Min']}L - ₹{client_data['Budget_Max']}L")
            st.write(f"**Location:** {client_data['Location_Preference']}")
            st.write(f"**BHK:** {client_data['BHK_Requirement']}")
        
        with col3:
            st.write(f"**Status:** {client_data['Status']}")
            st.write(f"**Assigned To:** {client_data['Assigned_To']}")
            st.write(f"**Priority:** {client_data['Priority']}")
        
        st.write(f"**Requirements:** {client_data.get('Requirements_Notes', 'N/A')}")
        
        listings_df = st.session_state.listings
        if not listings_df.empty:
            client_listings = listings_df[listings_df['Client_ID'] == client_data['Client_ID']]
            
            if not client_listings.empty:
                st.markdown("#### 🏢 Property Listings")
                for idx, listing in client_listings.iterrows():
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                    
                    with col1:
                        st.write(f"**{listing['Property_Address']}**")
                        st.caption(f"{listing['BHK']} | {listing['Area_SqFt']} sq ft")
                    
                    with col2:
                        st.write(f"**₹{listing['Price']}L**")
                        st.caption(f"Status: {listing['Listing_Status']}")
                    
                    with col3:
                        st.write(f"**Broker:** {listing['Broker_Name']}")
                        st.caption(f"{listing['Broker_Contact']}")
                    
                    with col4:
                        visible = "✅ Yes" if listing['Visible_To_Partner'] == 'Yes' else "❌ No"
                        st.write(f"**Partner Access:** {visible}")
                    
                    st.markdown("---")
            else:
                st.info("No listings added for this client yet")


# ==================== LISTINGS PAGE ====================

def show_listings_page(is_admin=True):
    st.markdown('<div class="main-header">🏢 Property Listings</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📋 View Listings", "➕ Add New Listing"])
    
    with tab1:
        listings_df = st.session_state.listings
        
        if not listings_df.empty:
            clients_df = st.session_state.clients
            
            if not clients_df.empty:
                listings_display = listings_df.merge(
                    clients_df[['Client_ID', 'Client_Name']], 
                    on='Client_ID', 
                    how='left'
                )
            else:
                listings_display = listings_df
            
            st.dataframe(listings_display, use_container_width=True, hide_index=True)
        else:
            st.info("📭 No listings found. Add your first listing using the 'Add New Listing' tab!")
    
    with tab2:
        if is_admin:
            show_add_listing_form()
        else:
            st.warning("⚠️ Only Admin can add new listings")

def show_add_listing_form():
    st.subheader("Add New Property Listing")
    
    clients_df = st.session_state.clients
    
    if clients_df.empty:
        st.warning("⚠️ Please add clients first before adding listings")
        return
    
    client_options = {f"{row['Client_Name']} ({row['Client_ID']})": row['Client_ID'] 
                     for _, row in clients_df.iterrows()}
    
    with st.form("add_listing_form"):
        selected_client = st.selectbox("Select Client *", options=list(client_options.keys()))
        
        col1, col2 = st.columns(2)
        
        with col1:
            address = st.text_input("Property Address *", placeholder="e.g., 2 BHK, Marol Pipeline Road")
            location = st.text_input("Location *", placeholder="e.g., Marol, Andheri East")
            bhk = st.selectbox("BHK *", ["1 BHK", "2 BHK", "3 BHK", "4 BHK", "5+ BHK"])
        
        with col2:
            price = st.number_input("Price (Lakhs) *", min_value=10, max_value=1000, value=95, step=5)
            area = st.number_input("Area (Sq Ft) *", min_value=200, max_value=5000, value=850, step=50)
            
        amenities = st.text_area("Amenities", placeholder="e.g., East facing, covered parking, 5th floor")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            broker_name = st.text_input("Broker Name *", placeholder="e.g., Ramesh Patil")
        
        with col2:
            broker_contact = st.text_input("Broker Contact *", placeholder="e.g., +91 99999 88888")
        
        with col3:
            visible_to_partner = st.selectbox("Visible to Partner? *", ["Yes", "No"])
        
        notes = st.text_area("Internal Notes", placeholder="Notes for internal use only")
        
        submitted = st.form_submit_button("Add Listing", use_container_width=True)
        
        if submitted:
            if address and location and bhk and price and broker_name and broker_contact:
                listing_data = {
                    'client_id': client_options[selected_client],
                    'address': address,
                    'location': location,
                    'bhk': bhk,
                    'price': price,
                    'area': area,
                    'broker_name': broker_name,
                    'broker_contact': broker_contact,
                    'amenities': amenities,
                    'visible_to_partner': visible_to_partner,
                    'notes': notes
                }
                
                listing_id = add_listing(listing_data)
                st.success(f"✅ Listing added successfully! Listing ID: {listing_id}")
                st.balloons()
            else:
                st.error("❌ Please fill all required fields marked with *")


# ==================== PARTNER DASHBOARD ====================

def partner_dashboard():
    st.sidebar.markdown(f"### 👤 Welcome, {st.session_state.user_name}!")
    st.sidebar.markdown(f"**Role:** {st.session_state.user_role}")
    
    menu = st.sidebar.radio(
        "Navigation",
        ["📊 My Dashboard", "👥 My Clients", "🏢 Property Listings"],
        key="partner_menu"
    )
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        logout()
    
    if menu == "📊 My Dashboard":
        show_partner_dashboard_home()
    elif menu == "👥 My Clients":
        show_partner_clients()
    elif menu == "🏢 Property Listings":
        show_partner_listings()

def show_partner_dashboard_home():
    st.markdown('<div class="main-header">📊 My Dashboard</div>', unsafe_allow_html=True)
    
    clients_df = st.session_state.clients
    partner_name = st.session_state.user_name
    
    my_clients = clients_df[clients_df['Assigned_To'].str.contains(partner_name, case=False, na=False)]
    
    if not my_clients.empty:
        client_ids = my_clients['Client_ID'].tolist()
        listings_df = st.session_state.listings
        my_listings = listings_df[
            (listings_df['Client_ID'].isin(client_ids)) & 
            (listings_df['Visible_To_Partner'] == 'Yes')
        ]
    else:
        my_listings = pd.DataFrame()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(my_clients)}</h3>
            <p>My Assigned Clients</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(my_listings)}</h3>
            <p>Properties to Show</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>0</h3>
            <p>Site Visits This Week</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("👥 My Assigned Clients")
    if not my_clients.empty:
        st.dataframe(
            my_clients[['Client_Name', 'Budget_Min', 'Budget_Max', 'Location_Preference', 'BHK_Requirement', 'Status']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("📭 No clients assigned to you yet")

def show_partner_clients():
    st.markdown('<div class="main-header">👥 My Clients</div>', unsafe_allow_html=True)
    
    clients_df = st.session_state.clients
    partner_name = st.session_state.user_name
    
    my_clients = clients_df[clients_df['Assigned_To'].str.contains(partner_name, case=False, na=False)]
    
    if not my_clients.empty:
        st.dataframe(my_clients, use_container_width=True, hide_index=True)
        
        st.markdown("### Client Details")
        selected_client = st.selectbox(
            "Select a client to view details",
            options=my_clients['Client_Name'].tolist()
        )
        
        if selected_client:
            client_data = my_clients[my_clients['Client_Name'] == selected_client].iloc[0]
            show_client_details(client_data, is_admin=False)
    else:
        st.info("📭 No clients assigned to you yet. Please contact admin.")

def show_partner_listings():
    st.markdown('<div class="main-header">🏢 Property Listings</div>', unsafe_allow_html=True)
    
    clients_df = st.session_state.clients
    partner_name = st.session_state.user_name
    my_clients = clients_df[clients_df['Assigned_To'].str.contains(partner_name, case=False, na=False)]
    
    if not my_clients.empty:
        client_ids = my_clients['Client_ID'].tolist()
        
        listings_df = st.session_state.listings
        my_listings = listings_df[
            (listings_df['Client_ID'].isin(client_ids)) & 
            (listings_df['Visible_To_Partner'] == 'Yes')
        ]
        
        if not my_listings.empty:
            listings_display = my_listings.merge(
                my_clients[['Client_ID', 'Client_Name']], 
                on='Client_ID', 
                how='left'
            )
            
            st.dataframe(
                listings_display[['Client_Name', 'Property_Address', 'Location', 'BHK', 'Price', 
                                'Broker_Name', 'Broker_Contact', 'Listing_Status']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("📭 No properties available to show yet")
    else:
        st.info("📭 No clients assigned to you yet")

def show_reports_page():
    st.markdown('<div class="main-header">📈 Reports & Analytics</div>', unsafe_allow_html=True)
    st.info("🚧 Reports coming soon! This will include performance metrics, conversion rates, and revenue analytics.")

# ==================== MAIN APPLICATION ====================

def main():
    initialize_session_state()
    initialize_data()
    
    if not st.session_state.logged_in:
        login_page()
        return
    
    if st.session_state.user_role == "Admin":
        admin_dashboard()
    else:
        partner_dashboard()

if __name__ == "__main__":
    main()

