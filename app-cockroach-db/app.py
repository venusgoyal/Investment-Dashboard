"""
Investment Dashboard - Streamlit Application with CockroachDB (PostgreSQL)
"""
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime, date
import logging
import plotly.express as px
import plotly.graph_objects as go

from cockroach_service import (
    InvestmentService, 
    AuthenticationService,
    calculate_current_value, 
    calculate_profit_loss,
    calculate_return_percentage
)
from auth_pages import show_login_page, show_admin_page, show_profile_page

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function to convert numbers to words in Indian format
def number_to_words(num):
    """
    Convert a number to words in Indian format (with Lacs, Crores, etc.)
    Example: 3600000 -> "36 lacs"
    """
    ones = ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
    teens = ['ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 
             'sixteen', 'seventeen', 'eighteen', 'nineteen']
    tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety']
    
    def convert_below_1000(n):
        if n == 0:
            return ''
        elif n < 10:
            return ones[n]
        elif n < 20:
            return teens[n - 10]
        elif n < 100:
            return tens[n // 10] + (' ' + ones[n % 10] if n % 10 != 0 else '')
        else:
            return ones[n // 100] + ' hundred' + (' ' + convert_below_1000(n % 100) if n % 100 != 0 else '')
    
    if num == 0:
        return 'zero'
    
    num = int(num)
    if num < 0:
        return 'negative ' + number_to_words(-num)
    
    # Indian numbering system
    crore = num // 10000000
    lakh = (num % 10000000) // 100000
    thousand = (num % 100000) // 1000
    remainder = num % 1000
    
    parts = []
    
    if crore > 0:
        parts.append(convert_below_1000(crore) + ' crore,')
    if lakh > 0:
        parts.append(convert_below_1000(lakh) + ' lacs,')
    if thousand > 0:
        parts.append(convert_below_1000(thousand) + ' thousand,')
    if remainder > 0:
        parts.append(convert_below_1000(remainder))
    
    return ' '.join(parts) if parts else 'zero'

# Helper function to check if user is active
def is_user_active():
    """Check if current user is active (not awaiting admin approval)"""
    return getattr(st.session_state, 'is_active', True)

def show_inactive_user_message():
    """Display message for inactive users"""
    st.warning("""
    🔒 **Your Account is Awaiting Approval**
    
    Your account has been created but is not yet activated. An administrator needs to approve your account before you can access the investment management features.
    
    **Features available to you:**
    - 👤 View and manage your profile
    - 🔑 Change your password
    
    **Features locked (pending admin approval):**
    - 📊 Investment Dashboard
    - ➕ Create investments
    - 👁️ View investments
    - ✏️ Update investments
    - 🗑️ Delete investments
    
    Please contact an administrator to activate your account.
    """)

# CockroachDB Configuration from Streamlit Secrets
# For local development: credentials are read from .streamlit/secrets.toml
# For Streamlit Cloud: add secrets via the Streamlit Cloud console
try:
    # Try to get database_url directly
    COCKROACH_DB_URL = st.secrets["cockroachdb"]["database_url"]
except KeyError:
    try:
        # Fallback to individual parameters
        COCKROACH_DB_URL = None
        COCKROACH_CONFIG = {
            "host": st.secrets["cockroachdb"]["host"],
            "port": st.secrets["cockroachdb"]["port"],
            "user": st.secrets["cockroachdb"]["user"],
            "password": st.secrets["cockroachdb"]["password"],
            "database": st.secrets["cockroachdb"]["database"],
            "sslmode": st.secrets["cockroachdb"].get("sslmode", "verify-full")
        }
    except KeyError:
        # Configuration not found in secrets
        st.error("⚠️ CockroachDB credentials not found in secrets. Please configure them:")
        st.info("""
        **For local development:**
        - Create `.streamlit/secrets.toml` with your CockroachDB credentials
        
        **Option 1: Using database_url (recommended)**
        ```
        [cockroachdb]
        database_url = "postgresql://user:password@host:port/database?sslmode=verify-full"
        ```
        
        **Option 2: Using individual parameters**
        ```
        [cockroachdb]
        host = "your_host"
        port = 26257
        user = "your_user"
        password = "your_password"
        database = "defaultdb"
        sslmode = "verify-full"
        ```
        
        **For Streamlit Cloud:**
        - Go to your app's advanced settings
        - Add secrets in TOML format (same as above)
        """)
        st.stop()
else:
    COCKROACH_CONFIG = None

# Page configuration
st.set_page_config(
    page_title="Investment Dashboard - CockroachDB",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling - Modern Facebook-like design
st.markdown("""
    <style>
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        background-color: #f0f2f5;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
    }
    
    .main {
        background-color: #f0f2f5;
    }
    
    .stApp {
        background-color: #f0f2f5;
    }
    

    /* Card styling */
    .card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.1);
        transition: box-shadow 0.3s ease;
    }
    .card:hover {
        box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.15);
    }
    /* Real Estate and Mutual Fund Scenario sections - high contrast for both themes */
    .real-estate-section {
        background: #e3f0ff !important;
        border-left: 6px solid #2563eb !important;
        color: #102040 !important;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        padding: 1.5rem 1.5rem 1.2rem 1.5rem;
    }
    .mutual-fund-section {
        background: #fff7e6 !important;
        border-left: 6px solid #f59e42 !important;
        color: #4a2c00 !important;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        padding: 1.5rem 1.5rem 1.2rem 1.5rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    .metric-card-alt {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    .metric-card-alt2 {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    .metric-card-alt3 {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
    
    .metric-label {
        font-size: 14px;
        font-weight: 600;
        opacity: 0.9;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        margin: 10px 0;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 40px 30px;
        border-radius: 15px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .header-container h1 {
        font-size: 42px;
        margin-bottom: 10px;
        font-weight: 800;
    }
    
    .header-container p {
        font-size: 16px;
        opacity: 0.95;
    }
    
    /* Alert/Box styling */
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        color: #155724;
        padding: 15px 20px;
        border-radius: 8px;
        margin: 15px 0;
    }
    
    .error-box {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        color: #721c24;
        padding: 15px 20px;
        border-radius: 8px;
        margin: 15px 0;
    }
    
    .info-box {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        color: #0c5460;
        padding: 15px 20px;
        border-radius: 8px;
        margin: 15px 0;
    }
    
    /* Investment card */
    .investment-card {
        background: white;
        border-radius: 12px;
        padding: 25px;
        margin: 15px 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .investment-card:hover {
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
        transform: translateX(5px);
    }
    
    .investment-card-profit {
        border-left-color: #43e97b;
    }
    
    .investment-card-loss {
        border-left-color: #f5576c;
    }
    
    /* Table styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Input styling */
    .stNumberInput > div > input,
    .stDateInput > div > input,
    .stSelectbox > div > div,
    .stTextInput > div > input {
        border-radius: 8px !important;
        border: 2px solid #d0d0d0 !important;
        padding: 12px !important;
        font-size: 15px !important;
        background-color: #ffffff !important;
        color: #1f2937 !important;
    }
    
    .stNumberInput > div > input:focus,
    .stDateInput > div > input:focus,
    .stTextInput > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
        background-color: #f8f9fa !important;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Dropdown option styling - light theme */
    .stSelectbox [data-baseweb="select"] {
        background-color: #ffffff !important;
    }
    
    .stSelectbox [role="option"] {
        background-color: #ffffff !important;
        color: #1f2937 !important;
    }
    
    .stSelectbox [role="option"]:hover,
    .stSelectbox [role="option"][aria-selected="true"] {
        background-color: #e3f0ff !important;
        color: #102040 !important;
        font-weight: 600 !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 12px !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #e9ecef;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: white;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(to right, transparent, #e0e0e0, transparent);
        margin: 30px 0;
    }
    
    /* Subheader styling */
    h2, h3 {
        color: #1f2937;
        margin-top: 25px;
        margin-bottom: 15px;
        font-weight: 700;
    }
    
    /* Chart container */
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Input field styling */
    .stNumberInput > div > div > input {
        background-color: white !important;
        border: 2px solid #ddd !important;
        border-radius: 8px !important;
        color: #1f2937 !important;
    }
    
    .stNumberInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Dark theme support */
    @media (prefers-color-scheme: dark) {
        body {
            background-color: #0e1117;
            color: #e0e0e0;
        }
        .main {
            background-color: #0e1117;
        }
        .stApp {
            background-color: #0e1117;
        }
        /* Card styling for dark theme */
        .card {
            background-color: #161b22;
            color: #e0e0e0;
            border: 1px solid #30363d;
        }
        /* Real Estate and Mutual Fund Scenario sections - dark theme with colorful gradients */
        .real-estate-section {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
            border-left: 6px solid #00f2fe !important;
            color: white !important;
            box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);
        }
        .mutual-fund-section {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%) !important;
            border-left: 6px solid #38f9d7 !important;
            color: white !important;
            box-shadow: 0 4px 15px rgba(67, 233, 123, 0.4);
        }
        /* Chart container dark theme */
        .chart-container {
            background: #161b22;
            border: 1px solid #30363d;
            color: #e0e0e0;
        }
        /* Investment card dark theme */
        .investment-card {
            background: #161b22;
            border-left: 5px solid #667eea;
            border-right: 1px solid #30363d;
            border-top: 1px solid #30363d;
            border-bottom: 1px solid #30363d;
            color: #e0e0e0;
        }
        /* Input styling dark theme */
        .stNumberInput > div > div > input {
            background-color: #0d1117 !important;
            border: 2px solid #30363d !important;
            color: #e0e0e0 !important;
        }
        .stNumberInput > div > div > input:focus {
            border-color: #667eea !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3) !important;
            background-color: #161b22 !important;
        }
        .stDateInput > div > input,
        .stSelectbox > div > div,
        .stTextInput > div > input {
            background-color: #0d1117 !important;
            border: 2px solid #30363d !important;
            color: #e0e0e0 !important;
        }
        .stDateInput > div > input:focus,
        .stTextInput > div > input:focus {
            border-color: #667eea !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3) !important;
            background-color: #161b22 !important;
        }
        .stSelectbox > div > div:focus-within {
            border-color: #667eea !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3) !important;
        }
        /* Dropdown option styling - dark theme */
        .stSelectbox [data-baseweb="select"] {
            background-color: #0d1117 !important;
        }
        .stSelectbox [role="option"] {
            background-color: #161b22 !important;
            color: #e0e0e0 !important;
        }
        .stSelectbox [role="option"]:hover,
        .stSelectbox [role="option"][aria-selected="true"] {
            background-color: #4facfe !important;
            color: white !important;
            font-weight: 600 !important;
        }
        /* Expander dark theme */
        .streamlit-expanderHeader {
            background-color: #161b22;
            border: 1px solid #30363d;
            color: #e0e0e0;
        }
        .streamlit-expanderHeader:hover {
            background-color: #21262d;
        }
        /* Sidebar dark theme */
        .sidebar .sidebar-content {
            background-color: #161b22;
            border-right: 1px solid #30363d;
        }
        /* Text colors for dark theme */
        h2, h3, h4, h5, h6 {
            color: #e0e0e0 !important;
        }
        p {
            color: #c9d1d9 !important;
        }
        /* Alert/Box styling dark theme */
        .success-box {
            background-color: #0d3817;
            border-left: 4px solid #3fb950;
            color: #7ee787;
        }
        .error-box {
            background-color: #3d1f1a;
            border-left: 4px solid #da3633;
            color: #f85149;
        }
        .info-box {
            background-color: #0d1f2d;
            border-left: 4px solid #0969da;
            color: #79c0ff;
        }
        /* Divider dark theme */
        hr {
            background: linear-gradient(to right, transparent, #30363d, transparent);
        }
        /* Button styling dark theme */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
        }
        .stButton > button:hover {
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.8);
        }
        /* Metric cards remain colorful in dark theme */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .metric-card-alt {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        .metric-card-alt2 {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        .metric-card-alt3 {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }
        .metric-label {
            color: rgba(255, 255, 255, 0.9);
        }
        .metric-value {
            color: white;
        }
        /* Header dark theme */
        .header-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .header-container h1,
        .header-container p {
            color: white;
        }
    }
    
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'auth_service' not in st.session_state:
    try:
        if COCKROACH_DB_URL:
            st.session_state.auth_service = AuthenticationService(database_url=COCKROACH_DB_URL)
        else:
            st.session_state.auth_service = AuthenticationService(**COCKROACH_CONFIG)
    except Exception as e:
        st.error(f"Failed to initialize auth service: {str(e)}")
        logger.error(f"Auth service error: {e}")
        st.stop()

if 'service' not in st.session_state:
    try:
        if COCKROACH_DB_URL:
            st.session_state.service = InvestmentService(database_url=COCKROACH_DB_URL)
        else:
            st.session_state.service = InvestmentService(**COCKROACH_CONFIG)
    except Exception as e:
        st.error(f"Failed to connect to CockroachDB: {str(e)}")
        logger.error(f"Database connection error: {e}")
        st.stop()

if 'refresh_key' not in st.session_state:
    st.session_state.refresh_key = 0

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'user_id' not in st.session_state:
    st.session_state.user_id = None

if 'username' not in st.session_state:
    st.session_state.username = None

if 'role' not in st.session_state:
    st.session_state.role = None

if 'is_active' not in st.session_state:
    st.session_state.is_active = True

# Check authentication
if not st.session_state.authenticated:
    show_login_page(st.session_state.auth_service)
    st.stop()

# Modern header with custom HTML
st.markdown("""
    <div class="header-container">
        <h1>💼 Investment Dashboard</h1>
        <p>Smart Portfolio Management with CockroachDB - Real-Time Analytics</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/portfolio.png", width=50)
    
    # User info section
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, rgb(102, 126, 234) 0%, rgb(118, 75, 162) 100%); opacity: 0.9;" style='background: #f0f2f5; padding: 12px; border-radius: 8px; margin-bottom: 15px;'>
        <p style='margin: 0; font-weight: bold; color: #667eea;'>{st.session_state.username}</p>
        <p style='margin: 0; font-size: 12px; color: #666;'>{'👑 Admin' if st.session_state.role == 'admin' else '👤 User'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.title("Navigation")
    
    # Build menu options based on user role and active status
    if st.session_state.is_active:
        # Active users can access all investment features
        menu_options = ["📊 Dashboard", "➕ Create", "👁️ View All", "✏️ Update", "🗑️ Delete"]
        menu_icons = ["graph-up", "plus-circle", "eye", "pencil-square", "trash"]
        
        if st.session_state.role == "admin":
            menu_options.extend(["👨‍💼 Admin Panel", "👤 Profile", "🚪 Logout"])
            menu_icons.extend(["shield", "user", "door-open"])
        else:
            menu_options.extend(["👤 Profile", "🚪 Logout"])
            menu_icons.extend(["user", "door-open"])
    else:
        # Inactive users can only access Profile and Logout
        st.warning("""
        🔒 **Account Pending Activation**
        
        Your account is awaiting admin approval. You can only access your profile settings until your account is activated.
        """)
        menu_options = ["👤 Profile", "🚪 Logout"]
        menu_icons = ["user", "door-open"]
        
        if st.session_state.role == "admin":
            # Even admins have limited access if inactive (shouldn't happen, but just in case)
            menu_options = ["👨‍💼 Admin Panel", "👤 Profile", "🚪 Logout"]
            menu_icons = ["shield", "user", "door-open"]
    
    selected = option_menu(
        menu_title=None,
        options=menu_options,
        icons=menu_icons,
        menu_icon="cast",
        default_index=0,
    )

# Handle logout
if selected == "🚪 Logout":
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.role = None
    st.success("✅ Logged out successfully!")
    st.rerun()

# ==================== DASHBOARD PAGE ====================
if selected == "📊 Dashboard":
    if not is_user_active():
        show_inactive_user_message()
    else:
        try:
            investments = st.session_state.service.read_all_investments()
            
            if not investments:
                st.info("📭 No investments found. Create one to get started!")
            else:
                # Calculate metrics
                total_invested = 0
                total_current_value = 0
                total_profit_loss = 0
                
                for inv in investments:
                    amount = float(inv.get('investment_amount', 0))
                    annual_return = float(inv.get('annual_return_percentage', 0))
                    inv_date = inv.get('investment_date')
                    
                    # Handle date conversion
                    if inv_date:
                        if hasattr(inv_date, 'strftime'):
                            inv_date_str = inv_date.strftime('%Y-%m-%d')
                        else:
                            inv_date_str = str(inv_date)
                    else:
                        continue
                    
                    total_invested += amount
                    current_val = calculate_current_value(amount, annual_return, inv_date_str)
                    total_current_value += current_val
                    total_profit_loss += calculate_profit_loss(current_val, amount)
                
                # Display key metrics with custom gradient cards
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    invested_words = number_to_words(total_invested)
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">💰 Total Invested</div>
                            <div class="metric-value">₹{total_invested:,.2f}</div>
                            <div style="font-size: 12px; color: rgba(255,255,255,0.85); margin-top: 8px; text-transform: capitalize;">{invested_words}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    current_words = number_to_words(total_current_value)
                    st.markdown(f"""
                        <div class="metric-card metric-card-alt2">
                            <div class="metric-label">📈 Current Value</div>
                            <div class="metric-value">₹{total_current_value:,.2f}</div>
                            <div style="font-size: 12px; color: rgba(255,255,255,0.85); margin-top: 8px; text-transform: capitalize;">{current_words}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    profit_words = number_to_words(abs(total_profit_loss))
                    profit_color = "43e97b" if total_profit_loss >= 0 else "f5576c"
                    st.markdown(f"""
                        <div class="metric-card metric-card-alt3">
                            <div class="metric-label">📊 P/L Amount</div>
                            <div class="metric-value">₹{total_profit_loss:,.2f}</div>
                            <div style="font-size: 12px; color: rgba(255,255,255,0.85); margin-top: 8px; text-transform: capitalize;">{profit_words}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    roi = calculate_return_percentage(total_current_value, total_invested) if total_invested > 0 else 0
                    st.markdown(f"""
                        <div class="metric-card metric-card-alt">
                            <div class="metric-label">📉 ROI %</div>
                            <div class="metric-value">{roi:.2f}%</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Display overall investment segment (2x the current values for 50% partner)
                st.markdown("<h3 style='color: #1f2937; margin-top: 20px; margin-bottom: 15px;'>🌍 Overall Investment (100% Partnership)</h3>", unsafe_allow_html=True)
                
                overall_invested = total_invested * 2
                overall_current_value = total_current_value * 2
                overall_profit_loss = total_profit_loss * 2
                overall_roi = calculate_return_percentage(overall_current_value, overall_invested) if overall_invested > 0 else 0
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    overall_invested_words = number_to_words(overall_invested)
                    st.markdown(f"""
                        <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); opacity: 0.85;">
                            <div class="metric-label">💰 Total Invested</div>
                            <div class="metric-value">₹{overall_invested:,.2f}</div>
                            <div style="font-size: 12px; color: rgba(255,255,255,0.85); margin-top: 8px; text-transform: capitalize;">{overall_invested_words}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    overall_current_words = number_to_words(overall_current_value)
                    st.markdown(f"""
                        <div class="metric-card metric-card-alt2" style="opacity: 0.85;">
                            <div class="metric-label">📈 Current Value</div>
                            <div class="metric-value">₹{overall_current_value:,.2f}</div>
                            <div style="font-size: 12px; color: rgba(255,255,255,0.85); margin-top: 8px; text-transform: capitalize;">{overall_current_words}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    overall_profit_words = number_to_words(abs(overall_profit_loss))
                    st.markdown(f"""
                        <div class="metric-card metric-card-alt3" style="opacity: 0.85;">
                            <div class="metric-label">📊 P/L Amount</div>
                            <div class="metric-value">₹{overall_profit_loss:,.2f}</div>
                            <div style="font-size: 12px; color: rgba(255,255,255,0.85); margin-top: 8px; text-transform: capitalize;">{overall_profit_words}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                        <div class="metric-card metric-card-alt" style="opacity: 0.85;">
                            <div class="metric-label">📉 ROI %</div>
                            <div class="metric-value">{overall_roi:.2f}%</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # ===== REAL ESTATE INVESTMENT CALCULATOR =====
                st.markdown("<h3 style='color: #1f2937; margin-top: 30px; margin-bottom: 15px;'>🏠 Real Estate Investment Calculator</h3>", unsafe_allow_html=True)
                st.markdown("""
                <p style='color: #666; margin-bottom: 15px; font-size: 14px;'>
                Track the actual returns from real estate investment in the flat. Keep market price at ₹24,000/Sq Ft to see mutual fund baseline (16% annual return). Enter custom price to see real estate appreciation scenario.
                </p>
                """, unsafe_allow_html=True)
                
                # Real estate property details
                property_area_sqft = 3000  # Fixed property area
                original_price_per_sqft = 24000  # Fixed original price at purchase
                original_property_value = property_area_sqft * original_price_per_sqft
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Property Area", f"{property_area_sqft:,} Sq Ft")
                
                with col2:
                    st.metric("Original Purchase Price/Sq Ft", f"₹{original_price_per_sqft:,}")
                
                # Input field for current market price with heading
                st.markdown("<h4 style='color: #1f2937; margin-top: 20px; margin-bottom: 10px;'>💰 Enter Current Market Price per Sq Ft (₹)</h4>", unsafe_allow_html=True)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    current_price_per_sqft = st.number_input(
                        "Enter market price",
                        min_value=0.0,
                        value=float(original_price_per_sqft),
                        step=100.0,
                        format="%.0f",
                        help="Enter current market price per square foot. Keep at 24,000 for mutual fund scenario.",
                        label_visibility="collapsed"
                    )
                
                with col2:
                    if current_price_per_sqft != original_price_per_sqft:
                        price_change_percent = ((current_price_per_sqft - original_price_per_sqft) / original_price_per_sqft) * 100
                        change_color = "green" if price_change_percent > 0 else "red"
                        st.markdown(f"<p style='color: {change_color}; font-weight: bold; margin-top: 30px;'>{price_change_percent:+.2f}%</p>", unsafe_allow_html=True)
                
                # Display Real Estate vs Mutual Fund comparison
                st.markdown("<h4 style='color: #1f2937; margin-top: 25px; margin-bottom: 15px;'>📊 Scenario Comparison (Your Share - 50%)</h4>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); opacity: 0.9;" style="background: #f0f2f5; border-left: 4px solid #4facfe; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h5 style="color: #4facfe; margin-top: 0; margin-bottom: 10px;">📈 Mutual Fund Scenario (16% Annual Return)</h5>
                        <p style="margin: 8px 0; font-size: 14px; color: #666;">Invested: ₹{total_invested:,.2f}</p>
                        <p style="margin: 8px 0; font-size: 14px; color: #666;">Current Value: ₹{total_current_value:,.2f}</p>
                        <p style="margin: 8px 0; font-size: 14px; color: #666;">P/L: <span style="color: #43e97b;">₹{total_profit_loss:,.2f}</span></p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Only show real estate scenario if market price is different from original
                if current_price_per_sqft != original_price_per_sqft:
                    with col2:
                        # Calculate real estate profit based on property appreciation
                        # Profit = (Current Market Price - Original Price) × Property Area
                        property_profit = (current_price_per_sqft - original_price_per_sqft) * property_area_sqft
                        your_share_profit = property_profit / 2  # 50% partner
                        
                        profit_color = "#43e97b" if your_share_profit >= 0 else "#f5576c"
                        profit_color_bg = "#f0f2f5" if your_share_profit >= 0 else "#fff5f5"
                        border_color = "#43e97b" if your_share_profit >= 0 else "#f5576c"
                        
                        st.markdown(f"""
                        <div class="metric-card metric-card-alt2" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); opacity: 0.9;" style="background: {profit_color_bg}; border-left: 4px solid {border_color}; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                            <h5 style="color: {border_color}; margin-top: 0; margin-bottom: 10px;">🏠 Real Estate Scenario (Market Price)</h5>
                            <p style="margin: 8px 0; font-size: 14px; color: #666;">Invested: ₹{total_invested:,.2f}</p>
                            <p style="margin: 8px 0; font-size: 14px; color: #666;">Current Value: ₹{total_invested + your_share_profit:,.2f}</p>
                            <p style="margin: 8px 0; font-size: 14px; color: {border_color};"><strong>P/L: <span style="color: #43e97b;">₹{your_share_profit:,.2f}</span></strong></p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Show YOUR SHARE real estate metrics when custom market price is entered
                    st.markdown("<h4 style='color: #1f2937; margin-top: 25px; margin-bottom: 15px;'>👤 Your Share - Real Estate Investment (50%)</h4>", unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    your_share_invested_re = total_invested
                    your_share_current_value_re = your_share_invested_re + your_share_profit
                    your_share_roi = (your_share_profit / your_share_invested_re * 100) if your_share_invested_re > 0 else 0
                    
                    with col1:
                        st.markdown(f"""
                            <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); opacity: 0.9;">
                                <div class="metric-label">💰 Total Invested</div>
                                <div class="metric-value">₹{your_share_invested_re:,.2f}</div>
                                <div style="font-size: 11px; color: rgba(255,255,255,0.85); margin-top: 8px;">{number_to_words(your_share_invested_re)}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                            <div class="metric-card metric-card-alt2" style="opacity: 0.9;">
                                <div class="metric-label">📈 Current Value</div>
                                <div class="metric-value">₹{your_share_current_value_re:,.2f}</div>
                                <div style="font-size: 11px; color: rgba(255,255,255,0.85); margin-top: 8px;">{number_to_words(your_share_current_value_re)}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        profit_card_color = "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)" if your_share_profit >= 0 else "linear-gradient(135deg, #f5576c 0%, #f93b1d 100%)"
                        st.markdown(f"""
                            <div class="metric-card" style="background: {profit_card_color}; opacity: 0.9;">
                                <div class="metric-label">📊 Your P/L</div>
                                <div class="metric-value">₹{your_share_profit:,.2f}</div>
                                <div style="font-size: 11px; color: rgba(255,255,255,0.85); margin-top: 8px;">{number_to_words(abs(your_share_profit))}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(f"""
                            <div class="metric-card metric-card-alt" style="opacity: 0.9;">
                                <div class="metric-label">📉 ROI %</div>
                                <div class="metric-value">{your_share_roi:.2f}%</div>
                                <div style="font-size: 11px; color: rgba(255,255,255,0.85); margin-top: 8px;">Your 50% Share</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Show overall real estate metrics only when custom market price is entered
                    st.markdown("<h4 style='color: #1f2937; margin-top: 25px; margin-bottom: 15px;'>🌍 Overall Real Estate Investment (100% Partnership)</h4>", unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    overall_invested_re = total_invested * 2
                    overall_profit_re = property_profit  # Full property profit (both partners)
                    overall_current_value_re = overall_invested_re + overall_profit_re
                    
                    with col1:
                        st.markdown(f"""
                            <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); opacity: 0.9;">
                                <div class="metric-label">💰 Total Invested</div>
                                <div class="metric-value">₹{overall_invested_re:,.2f}</div>
                                <div style="font-size: 11px; color: rgba(255,255,255,0.85); margin-top: 8px;">{number_to_words(overall_invested_re)}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                            <div class="metric-card metric-card-alt2" style="opacity: 0.9;">
                                <div class="metric-label">📈 Current Value</div>
                                <div class="metric-value">₹{overall_current_value_re:,.2f}</div>
                                <div style="font-size: 11px; color: rgba(255,255,255,0.85); margin-top: 8px;">{number_to_words(overall_current_value_re)}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        profit_card_color = "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)" if overall_profit_re >= 0 else "linear-gradient(135deg, #f5576c 0%, #f93b1d 100%)"
                        st.markdown(f"""
                            <div class="metric-card" style="background: {profit_card_color}; opacity: 0.9;">
                                <div class="metric-label">📊 Total P/L</div>
                                <div class="metric-value">₹{overall_profit_re:,.2f}</div>
                                <div style="font-size: 11px; color: rgba(255,255,255,0.85); margin-top: 8px;">{number_to_words(abs(overall_profit_re))}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        re_roi = (overall_profit_re / overall_invested_re * 100) if overall_invested_re > 0 else 0
                        st.markdown(f"""
                            <div class="metric-card metric-card-alt" style="opacity: 0.9;">
                                <div class="metric-label">📉 ROI %</div>
                                <div class="metric-value">{re_roi:.2f}%</div>
                                <div style="font-size: 11px; color: rgba(255,255,255,0.85); margin-top: 8px;">Overall Partnership</div>
                            </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Prepare detailed data for charts
                chart_data = []
                for inv in investments:
                    inv_date = inv.get('investment_date')
                    if inv_date:
                        if hasattr(inv_date, 'strftime'):
                            inv_date_str = inv_date.strftime('%Y-%m-%d')
                        else:
                            inv_date_str = str(inv_date)
                        
                        amount = float(inv.get('investment_amount', 0))
                        annual_return = float(inv.get('annual_return_percentage', 0))
                        current_val = calculate_current_value(amount, annual_return, inv_date_str)
                        
                        chart_data.append({
                            'Date': inv_date_str,
                            'Invested': amount,
                            'Current': current_val,
                            'Return %': annual_return
                        })
                
                # Create visualizations
                st.markdown("<h2 style='color: #1f2937; margin-top: 30px;'>📊 Investment Analysis</h2>", unsafe_allow_html=True)
                
                # Create a single sunburst/circle chart showing Total Invested, Current Value, and P/L
                if chart_data:
                    # Prepare data for the circular chart
                    labels = ['Total Invested', 'Current Value', 'P/L Amount']
                    values = [total_invested, total_current_value, total_profit_loss]
                    colors = ['#667eea', '#4facfe', '#43e97b' if total_profit_loss >= 0 else '#f5576c']
                    
                    fig_circle = go.Figure(data=[go.Pie(
                        labels=labels,
                        values=[abs(v) for v in values],
                        hole=0.3,
                        marker=dict(colors=colors, line=dict(color='white', width=2)),
                        textposition='inside',
                        textinfo='label+percent',
                        hovertemplate='<b>%{label}</b><br>Amount: ₹%{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
                    )])
                    
                    fig_circle.update_layout(
                        title={
                            'text': "Investment Portfolio Breakdown",
                            'x': 0.5,
                            'xanchor': 'center',
                            'font': {'size': 18}
                        },
                        height=500,
                        showlegend=True,
                        font=dict(size=12),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    st.plotly_chart(fig_circle, use_container_width=True)
                
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.markdown("""
                    <h2 style='color: #1f2937; margin-bottom: 20px;'>📋 Investment Details</h2>
                    <p style='color: #666; margin-bottom: 20px;'>Complete list of all your investments</p>
                """, unsafe_allow_html=True)
                
                # Display investments table
                display_data = []
                for inv in investments:
                    inv_date = inv.get('investment_date')
                    if inv_date:
                        if hasattr(inv_date, 'strftime'):
                            inv_date_str = inv_date.strftime('%Y-%m-%d')
                        else:
                            inv_date_str = str(inv_date)
                        
                        amount = float(inv.get('investment_amount', 0))
                        annual_return = float(inv.get('annual_return_percentage', 0))
                        current_val = calculate_current_value(amount, annual_return, inv_date_str)
                        profit_loss = calculate_profit_loss(current_val, amount)
                        roi = calculate_return_percentage(current_val, amount)
                        
                        display_data.append({
                            'Amount': f"₹{amount:,.2f}",
                            'Date': inv_date_str,
                            'Annual Return %': f"{annual_return:.2f}%",
                            'Current Value': f"₹{current_val:,.2f}",
                            'P/L': f"₹{profit_loss:,.2f}",
                            'ROI %': f"{roi:.2f}%",
                            'Comments': inv.get('investment_comments', 'N/A')
                        })
                
                df = pd.DataFrame(display_data)
                st.dataframe(df, use_container_width=True)
        
        except Exception as e:
            st.error(f"❌ Error loading dashboard: {str(e)}")
            logger.error(f"Dashboard error: {e}")

# ==================== CREATE PAGE ====================
elif selected == "➕ Create":
    if not is_user_active():
        show_inactive_user_message()
    else:
        st.header("Create New Investment")
        
        with st.form("create_investment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                investment_amount = st.number_input(
                    "Investment Amount (₹)",
                    min_value=0.01,
                    step=100.0,
                    format="%.2f",
                    help="Enter the amount to invest"
                )
            
            with col2:
                investment_date = st.date_input(
                    "Investment Date",
                    value=date.today(),
                    help="Date when the investment was made"
                )
            
            annual_return_percentage = st.number_input(
                "Annual Return Percentage (%)",
                min_value=0.0,
                max_value=100.0,
                step=0.1,
                format="%.2f",
                help="Expected or actual annual return percentage"
            )
            
            investment_comments = st.text_area(
                "Investment Comments",
                placeholder="Add any notes or details about this investment...",
                height=100,
                help="Optional comments about the investment"
            )
            
            submitted = st.form_submit_button("✅ Create Investment", use_container_width=True)
            
            if submitted:
                try:
                    if investment_amount <= 0:
                        st.error("❌ Investment amount must be greater than 0!")
                    elif not investment_date:
                        st.error("❌ Please select an investment date!")
                    else:
                        investment = st.session_state.service.create_investment(
                            investment_amount=investment_amount,
                            investment_date=investment_date.strftime('%Y-%m-%d'),
                            annual_return_percentage=annual_return_percentage,
                            investment_comments=investment_comments
                        )
                        st.success(f"✅ Investment created successfully!")
                        st.balloons()
                        st.session_state.refresh_key += 1
                        st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error creating investment: {str(e)}")
                    logger.error(f"Create investment error: {e}")

# ==================== VIEW ALL PAGE ====================
elif selected == "👁️ View All":
    if not is_user_active():
        show_inactive_user_message()
    else:
        st.header("All Investments")
        
        try:
            investments = st.session_state.service.read_all_investments()
            
            if not investments:
                st.info("📭 No investments found. Create one to get started!")
            else:
                # Display investments in an expandable format
                for idx, inv in enumerate(investments, 1):
                    inv_date = inv.get('investment_date')
                    if inv_date:
                        if hasattr(inv_date, 'strftime'):
                            inv_date_str = inv_date.strftime('%Y-%m-%d')
                        else:
                            inv_date_str = str(inv_date)
                        
                        amount = float(inv.get('investment_amount', 0))
                        annual_return = float(inv.get('annual_return_percentage', 0))
                        current_val = calculate_current_value(amount, annual_return, inv_date_str)
                        profit_loss = calculate_profit_loss(current_val, amount)
                        roi = calculate_return_percentage(current_val, amount)
                        
                        with st.expander(f"💼 Investment {idx} - ₹{amount:,.2f} ({inv_date_str})", expanded=False):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Investment Amount", f"₹{amount:,.2f}")
                            with col2:
                                st.metric("Current Value", f"₹{current_val:,.2f}")
                            with col3:
                                st.metric("P/L", f"₹{profit_loss:,.2f}")
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Annual Return %", f"{annual_return:.2f}%")
                            with col2:
                                st.metric("ROI %", f"{roi:.2f}%")
                            with col3:
                                st.metric("Investment Date", inv_date_str)
                            
                            if inv.get('investment_comments'):
                                st.markdown(f"**Notes:** {inv.get('investment_comments')}")
        
        except Exception as e:
            st.error(f"❌ Error loading investments: {str(e)}")
            logger.error(f"View all error: {e}")


# ==================== UPDATE PAGE ====================
elif selected == "✏️ Update":
    if not is_user_active():
        show_inactive_user_message()
    else:
        st.header("Update Investment")
        
        try:
            investments = st.session_state.service.read_all_investments()
            
            if not investments:
                st.info("📭 No investments found to update!")
            else:
                # Create selection options
                investment_options = {}
                for inv in investments:
                    inv_date = inv.get('investment_date')
                    if inv_date:
                        if hasattr(inv_date, 'strftime'):
                            inv_date_str = inv_date.strftime('%Y-%m-%d')
                        else:
                            inv_date_str = str(inv_date)
                        amount = float(inv.get('investment_amount', 0))
                        investment_options[f"₹{amount:,.2f} - {inv_date_str}"] = inv['investment_id']
                
                selected_display = st.selectbox(
                    "Select an investment to update",
                    options=investment_options.keys(),
                    help="Choose which investment to modify"
                )
                
                if selected_display:
                    selected_id = investment_options[selected_display]
                    inv = st.session_state.service.read_investment(selected_id)
                    
                    if inv:
                        st.subheader("Update Investment Details")
                        
                        inv_date = inv.get('investment_date')
                        if inv_date and hasattr(inv_date, 'strftime'):
                            inv_date_str = inv_date.strftime('%Y-%m-%d')
                            inv_date_obj = inv_date
                        else:
                            inv_date_str = str(inv_date)
                            from datetime import datetime
                            inv_date_obj = datetime.strptime(inv_date_str, '%Y-%m-%d').date()
                        
                        with st.form("update_form"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                new_amount = st.number_input(
                                    "Investment Amount (₹)",
                                    min_value=0.01,
                                    value=float(inv.get('investment_amount', 0)),
                                    step=100.0,
                                    format="%.2f"
                                )
                            
                            with col2:
                                new_date = st.date_input(
                                    "Investment Date",
                                    value=inv_date_obj
                                )
                            
                            new_return = st.number_input(
                                "Annual Return Percentage (%)",
                                min_value=0.0,
                                max_value=100.0,
                                value=float(inv.get('annual_return_percentage', 0)),
                                step=0.1,
                                format="%.2f"
                            )
                            
                            new_comments = st.text_area(
                                "Investment Comments",
                                value=inv.get('investment_comments', ''),
                                height=100
                            )
                            
                            submit = st.form_submit_button("✅ Update Investment", use_container_width=True)
                            
                            if submit:
                                try:
                                    st.session_state.service.update_investment(
                                        investment_id=selected_id,
                                        investment_amount=new_amount,
                                        investment_date=new_date.strftime('%Y-%m-%d'),
                                        annual_return_percentage=new_return,
                                        investment_comments=new_comments
                                    )
                                    st.success("✅ Investment updated successfully!")
                                    st.session_state.refresh_key += 1
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error updating investment: {str(e)}")
        
        except Exception as e:
            st.error(f"❌ Error loading investments: {str(e)}")
            logger.error(f"Update page error: {e}")

# ==================== DELETE PAGE ====================
elif selected == "🗑️ Delete":
    if not is_user_active():
        show_inactive_user_message()
    else:
        st.header("Delete Investment")
        
        try:
            investments = st.session_state.service.read_all_investments()
            
            if not investments:
                st.info("📭 No investments found to delete!")
            else:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    investment_options = {}
                    for inv in investments:
                        inv_date = inv.get('investment_date')
                        if inv_date:
                            if hasattr(inv_date, 'strftime'):
                                inv_date_str = inv_date.strftime('%Y-%m-%d')
                            else:
                                inv_date_str = str(inv_date)
                            amount = float(inv.get('investment_amount', 0))
                            investment_options[f"₹{amount:,.2f} - {inv_date_str}"] = inv['investment_id']
                    
                    selected_display = st.selectbox(
                        "Select an investment to delete",
                        options=investment_options.keys(),
                        help="Choose which investment to remove"
                    )
                
                if selected_display:
                    selected_id = investment_options[selected_display]
                    inv = st.session_state.service.read_investment(selected_id)
                    
                    if inv:
                        st.warning(f"""
                        ⚠️ **Confirm Deletion**
                        
                        You are about to delete:
                        - **Amount:** ₹{inv.get('investment_amount', 0):,.2f}
                        - **Date:** {inv.get('investment_date')}
                        
                        This action cannot be undone!
                        """)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("🗑️ Confirm Delete", use_container_width=True, type="secondary"):
                                try:
                                    st.session_state.service.delete_investment(selected_id)
                                    st.success("✅ Investment deleted successfully!")
                                    st.session_state.refresh_key += 1
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error deleting investment: {str(e)}")
                        
                        with col2:
                            st.button("❌ Cancel", use_container_width=True, disabled=True)
        
        except Exception as e:
            st.error(f"❌ Error loading investments: {str(e)}")
            logger.error(f"Delete page error: {e}")

# ==================== ADMIN PANEL PAGE ====================
elif selected == "👨‍💼 Admin Panel":
    show_admin_page(st.session_state.auth_service)

# ==================== PROFILE PAGE ====================
elif selected == "👤 Profile":
    show_profile_page(st.session_state.auth_service)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
    Investment Dashboard v1.0 - CockroachDB Edition | Built with Streamlit & CockroachDB | Secure Authentication
    </div>
    """,
    unsafe_allow_html=True
)
