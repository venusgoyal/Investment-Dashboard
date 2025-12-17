"""
Investment Dashboard - Streamlit Application with MySQL
"""
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime, date
import logging
import plotly.express as px
import plotly.graph_objects as go

from mysql_service import (
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

# MySQL Configuration from Streamlit Secrets
# For local development: credentials are read from .streamlit/secrets.toml
# For Streamlit Cloud: add secrets via the Streamlit Cloud console
try:
    MYSQL_CONFIG = {
        "host": st.secrets["mysql"]["host"],
        "port": st.secrets["mysql"]["port"],
        "user": st.secrets["mysql"]["user"],
        "password": st.secrets["mysql"]["password"],
        "database": st.secrets["mysql"]["database"]
    }
except KeyError:
    # Fallback configuration for development (if secrets not configured)
    st.error("⚠️ MySQL credentials not found in secrets. Please configure them:")
    st.info("""
    **For local development:**
    - Create `.streamlit/secrets.toml` with your MySQL credentials
    
    **For Streamlit Cloud:**
    - Go to your app's advanced settings
    - Add secrets in TOML format:
    ```
    [mysql]
    host = "your_host"
    port = 3306
    user = "your_user"
    password = "your_password"
    database = "your_database"
    ```
    """)
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Investment Dashboard - MySQL",
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
        border: 2px solid #e0e0e0 !important;
        padding: 12px !important;
        font-size: 15px !important;
    }
    
    .stNumberInput > div > input:focus,
    .stDateInput > div > input:focus,
    .stTextInput > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
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
    
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'auth_service' not in st.session_state:
    try:
        st.session_state.auth_service = AuthenticationService(MYSQL_CONFIG)
    except Exception as e:
        st.error(f"Failed to initialize auth service: {str(e)}")
        st.stop()

if 'service' not in st.session_state:
    try:
        st.session_state.service = InvestmentService(**MYSQL_CONFIG)
    except Exception as e:
        st.error(f"Failed to connect to MySQL: {str(e)}")
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
        <p>Smart Portfolio Management with Real-Time Analytics</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/investment.png", width=50)
    
    # User info section
    st.markdown(f"""
    <div style='background: #f0f2f5; padding: 12px; border-radius: 8px; margin-bottom: 15px;'>
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
                    inv_date = inv.get('investment_date', '').strftime('%Y-%m-%d') if isinstance(inv.get('investment_date'), date) else inv.get('investment_date', '')
                    
                    total_invested += amount
                    
                    if inv_date:
                        current_val = calculate_current_value(amount, annual_return, inv_date)
                        total_current_value += current_val
                        total_profit_loss += calculate_profit_loss(current_val, amount)
                
                # Display key metrics with custom gradient cards
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-label">💰 Total Invested</div>
                            <div class="metric-value">₹{total_invested:,.0f}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div class="metric-card metric-card-alt">
                            <div class="metric-label">📈 Current Value</div>
                            <div class="metric-value">₹{total_current_value:,.0f}</div>
                            <div style="font-size: 14px; opacity: 0.9;">+₹{total_profit_loss:,.0f}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    overall_return = calculate_return_percentage(total_current_value, total_invested)
                    st.markdown(f"""
                        <div class="metric-card metric-card-alt2">
                            <div class="metric-label">📊 Overall Return</div>
                            <div class="metric-value">{overall_return:.2f}%</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                        <div class="metric-card metric-card-alt3">
                            <div class="metric-label">🎯 Total Holdings</div>
                            <div class="metric-value">{len(investments)}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Prepare detailed data for charts
                chart_data = []
                for inv in investments:
                    amount = float(inv.get('investment_amount', 0))
                    annual_return = float(inv.get('annual_return_percentage', 0))
                    inv_date = inv.get('investment_date', '')
                    if isinstance(inv_date, date):
                        inv_date_str = inv_date.strftime('%Y-%m-%d')
                    else:
                        inv_date_str = inv_date
                    
                    current_val = calculate_current_value(amount, annual_return, inv_date_str)
                    profit_loss = calculate_profit_loss(current_val, amount)
                    return_pct = calculate_return_percentage(current_val, amount)
                    
                    chart_data.append({
                        'id': inv.get('investment_id', '')[:8],
                        'amount': amount,
                        'current_value': current_val,
                        'profit_loss': profit_loss,
                        'return_pct': return_pct,
                        'annual_return': annual_return,
                        'date': inv_date_str
                    })
                
                # Create visualizations
                st.markdown("<h2 style='color: #1f2937; margin-top: 30px;'>📊 Investment Analysis</h2>", unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                # Chart 1: Portfolio Composition (Pie Chart)
                with col1:
                    st.markdown("""
                        <div class="chart-container">
                            <h3 style='margin: 0 0 10px 0; color: #667eea;'>💎 Portfolio Composition</h3>
                            <p style='color: #666; margin: 0 0 15px 0; font-size: 13px;'>Distribution by invested amount</p>
                        </div>
                    """, unsafe_allow_html=True)
                    pie_df = pd.DataFrame({
                        'Investment': [f"Inv {i+1}" for i in range(len(chart_data))],
                        'Amount': [item['amount'] for item in chart_data]
                    })
                    
                    fig_pie = px.pie(
                        pie_df,
                        values='Amount',
                        names='Investment',
                        hole=0.3,
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig_pie.update_layout(height=400, showlegend=True)
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                # Chart 2: Current Value vs Invested (Bar Chart)
                with col2:
                    st.markdown("""
                        <div class="chart-container">
                            <h3 style='margin: 0 0 10px 0; color: #667eea;'>📊 Value Comparison</h3>
                            <p style='color: #666; margin: 0 0 15px 0; font-size: 13px;'>Investment vs current value</p>
                        </div>
                    """, unsafe_allow_html=True)
                    bar_df = pd.DataFrame({
                        'Investment': [f"Inv {i+1}" for i in range(len(chart_data))],
                        'Invested': [item['amount'] for item in chart_data],
                        'Current Value': [item['current_value'] for item in chart_data]
                    })
                    
                    fig_bar = px.bar(
                        bar_df,
                        x='Investment',
                        y=['Invested', 'Current Value'],
                        barmode='group',
                        color_discrete_map={'Invested': '#636EFA', 'Current Value': '#00CC96'}
                    )
                    fig_bar.update_layout(height=400, showlegend=True)
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                # Chart 3: Profit/Loss Distribution
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                        <div class="chart-container">
                            <h3 style='margin: 0 0 10px 0; color: #667eea;'>💵 Profit/Loss Analysis</h3>
                            <p style='color: #666; margin: 0 0 15px 0; font-size: 13px;'>Gains and losses per investment</p>
                        </div>
                    """, unsafe_allow_html=True)
                    profit_df = pd.DataFrame({
                        'Investment': [f"Inv {i+1}" for i in range(len(chart_data))],
                        'Profit/Loss': [item['profit_loss'] for item in chart_data],
                        'Color': ['green' if x > 0 else 'red' for x in [item['profit_loss'] for item in chart_data]]
                    })
                    
                    fig_profit = px.bar(
                        profit_df,
                        x='Investment',
                        y='Profit/Loss',
                        color='Color',
                        color_discrete_map={'green': '#00CC96', 'red': '#EF553B'}
                    )
                    fig_profit.add_hline(y=0, line_dash="dash", line_color="gray")
                    fig_profit.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig_profit, use_container_width=True)
                
                # Chart 4: Return Percentage Comparison
                with col2:
                    st.markdown("""
                        <div class="chart-container">
                            <h3 style='margin: 0 0 10px 0; color: #667eea;'>📈 Return % Overview</h3>
                            <p style='color: #666; margin: 0 0 15px 0; font-size: 13px;'>Performance comparison</p>
                        </div>
                    """, unsafe_allow_html=True)
                    return_df = pd.DataFrame({
                        'Investment': [f"Inv {i+1}" for i in range(len(chart_data))],
                        'Return %': [item['return_pct'] for item in chart_data]
                    })
                    
                    fig_return = px.bar(
                        return_df,
                        x='Investment',
                        y='Return %',
                        color='Return %',
                        color_continuous_scale='RdYlGn'
                    )
                    fig_return.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig_return, use_container_width=True)
                
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.markdown("""
                    <h2 style='color: #1f2937; margin-bottom: 20px;'>📋 Investment Details</h2>
                    <p style='color: #666; margin-bottom: 20px;'>Complete list of all your investments</p>
                """, unsafe_allow_html=True)
                
                # Display investments table
                display_data = []
                for inv in investments:
                    amount = float(inv.get('investment_amount', 0))
                    annual_return = float(inv.get('annual_return_percentage', 0))
                    inv_date = inv.get('investment_date', '')
                    if isinstance(inv_date, date):
                        inv_date = inv_date.strftime('%Y-%m-%d')
                    
                    current_val = calculate_current_value(amount, annual_return, inv_date)
                    profit_loss = calculate_profit_loss(current_val, amount)
                    return_pct = calculate_return_percentage(current_val, amount)
                    
                    # Calculate days passed
                    inv_date_obj = datetime.strptime(inv_date, '%Y-%m-%d').date()
                    days_passed = (date.today() - inv_date_obj).days
                    
                    # Current date
                    current_date = datetime.now().strftime('%Y-%m-%d')
                    
                    display_data.append({
                        'Investment ID': inv.get('investment_id', '')[:8] + '...',
                        'Amount': f"₹{amount:,.2f}",
                        'Date': inv_date,
                        'Days Passed': days_passed,
                        'Current Date': current_date,
                        'Annual Return %': f"{annual_return:.2f}%",
                        'Current Value': f"₹{current_val:,.2f}",
                        'Profit/Loss': f"₹{profit_loss:,.2f}",
                        'Return %': f"{return_pct:.2f}%",
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
                    # Convert date to string
                    inv_date_str = investment_date.strftime("%Y-%m-%d")
                    
                    # Create investment
                    result = st.session_state.service.create_investment(
                        investment_amount=investment_amount,
                        investment_date=inv_date_str,
                        annual_return_percentage=annual_return_percentage,
                        investment_comments=investment_comments
                    )
                    
                    st.success(f"✅ Investment created successfully!")
                    st.info(f"Investment ID: `{result['investment_id']}`")
                    
                    # Display created investment details
                    current_val = calculate_current_value(
                        investment_amount, 
                        annual_return_percentage, 
                        inv_date_str
                    )
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Amount", f"₹{investment_amount:,.2f}")
                    with col2:
                        st.metric("Current Value", f"₹{current_val:,.2f}")
                    with col3:
                        profit_loss = calculate_profit_loss(current_val, investment_amount)
                        st.metric("Profit/Loss", f"₹{profit_loss:,.2f}")
                    
                    st.balloons()
                    st.session_state.refresh_key += 1
                    
                except Exception as e:
                    st.error(f"❌ Error creating investment: {str(e)}")
                    logger.error(f"Create error: {e}")

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
                # Display investments
                for idx, inv in enumerate(investments, 1):
                    with st.expander(
                        f"📈 Investment #{idx} - {inv.get('investment_date', 'N/A')}", 
                        expanded=False
                    ):
                        col1, col2, col3 = st.columns(3)
                        
                        amount = float(inv.get('investment_amount', 0))
                        annual_return = float(inv.get('annual_return_percentage', 0))
                        inv_date = inv.get('investment_date', '')
                        if isinstance(inv_date, date):
                            inv_date = inv_date.strftime('%Y-%m-%d')
                        
                        current_val = calculate_current_value(amount, annual_return, inv_date)
                        profit_loss = calculate_profit_loss(current_val, amount)
                        return_pct = calculate_return_percentage(current_val, amount)
                        
                        with col1:
                            st.metric("Investment Amount", f"₹{amount:,.2f}")
                        with col2:
                            st.metric("Current Value", f"₹{current_val:,.2f}")
                        with col3:
                            st.metric("Profit/Loss", f"₹{profit_loss:,.2f}")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Annual Return %", f"{annual_return:.2f}%")
                        with col2:
                            st.metric("Return %", f"{return_pct:.2f}%")
                        with col3:
                            st.metric("Investment Date", inv_date)
                        
                        # New fields: Current Date and Days Passed
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            current_date = datetime.now().strftime('%Y-%m-%d')
                            st.metric("Current Date", current_date)
                        with col2:
                            inv_date_obj = datetime.strptime(inv_date, '%Y-%m-%d').date()
                            days_passed = (date.today() - inv_date_obj).days
                            st.metric("Days Passed", f"{days_passed} days")
                        with col3:
                            st.write("")  # Empty column for alignment
                        
                        # Display comments if available
                        comments = inv.get('investment_comments', '')
                        if comments:
                            st.info(f"💬 **Comments:** {comments}")
                        
                        # Add a mini visualization for this investment
                        col1, col2 = st.columns(2)
                        
                        # Pie chart for this investment
                        with col1:
                            fig_mini_pie = go.Figure(data=[go.Pie(
                                labels=['Initial Investment', 'Profit'],
                                values=[amount, max(profit_loss, 0)],
                                marker=dict(colors=['#636EFA', '#00CC96'])
                            )])
                            fig_mini_pie.update_layout(height=250, showlegend=True)
                            st.plotly_chart(fig_mini_pie, use_container_width=True)
                        
                        # Bar chart for comparison
                        with col2:
                            fig_mini_bar = go.Figure(data=[
                                go.Bar(x=['Investment', 'Current Value'], y=[amount, current_val], marker_color=['#636EFA', '#00CC96'])
                            ])
                            fig_mini_bar.update_layout(height=250, showlegend=False)
                            st.plotly_chart(fig_mini_bar, use_container_width=True)
                        
                        st.info(f"**ID:** `{inv.get('investment_id')}`")
                
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
                    inv_date = inv.get('investment_date', '')
                    if isinstance(inv_date, date):
                        inv_date = inv_date.strftime('%Y-%m-%d')
                    amount = float(inv.get('investment_amount', 0))
                    display_key = f"{inv_date} - ₹{amount:,.2f}"
                    investment_options[display_key] = inv.get('investment_id')
                
                selected_display = st.selectbox(
                    "Select an investment to update",
                    options=investment_options.keys(),
                    help="Choose which investment to modify"
                )
                
                if selected_display:
                    selected_id = investment_options[selected_display]
                    selected_investment = st.session_state.service.read_investment(selected_id)
                    
                    if selected_investment:
                        st.info(f"Selected Investment ID: `{selected_id}`")
                        
                        with st.form("update_investment_form"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                new_amount = st.number_input(
                                    "New Investment Amount (₹)",
                                    value=float(selected_investment.get('investment_amount', 0)),
                                    min_value=0.01,
                                    step=100.0,
                                    format="%.2f"
                                )
                            
                            with col2:
                                inv_date_obj = selected_investment.get('investment_date')
                                if isinstance(inv_date_obj, date):
                                    inv_date_obj = inv_date_obj
                                else:
                                    inv_date_obj = datetime.strptime(str(inv_date_obj), "%Y-%m-%d").date()
                                new_date = st.date_input(
                                    "New Investment Date",
                                    value=inv_date_obj
                                )
                            
                            new_return_pct = st.number_input(
                                "New Annual Return Percentage (%)",
                                value=float(selected_investment.get('annual_return_percentage', 0)),
                                min_value=0.0,
                                max_value=100.0,
                                step=0.1,
                                format="%.2f"
                            )
                            
                            new_comments = st.text_area(
                                "Investment Comments",
                                value=selected_investment.get('investment_comments', ''),
                                placeholder="Add any notes or details about this investment...",
                                height=100,
                                help="Optional comments about the investment"
                            )
                            
                            submitted = st.form_submit_button("✅ Update Investment", use_container_width=True)
                            
                            if submitted:
                                try:
                                    new_date_str = new_date.strftime("%Y-%m-%d")
                                    
                                    result = st.session_state.service.update_investment(
                                        investment_id=selected_id,
                                        investment_amount=new_amount,
                                        investment_date=new_date_str,
                                        annual_return_percentage=new_return_pct,
                                        investment_comments=new_comments
                                    )
                                    
                                    if result:
                                        st.success("✅ Investment updated successfully!")
                                        
                                        current_val = calculate_current_value(
                                            new_amount, 
                                            new_return_pct, 
                                            new_date_str
                                        )
                                        
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            st.metric("New Amount", f"₹{new_amount:,.2f}")
                                        with col2:
                                            st.metric("New Current Value", f"₹{current_val:,.2f}")
                                        with col3:
                                            st.metric("Annual Return", f"{new_return_pct:.2f}%")
                                        
                                        # Display new fields
                                        col1, col2, col3 = st.columns(3)
                                        with col1:
                                            current_date = datetime.now().strftime('%Y-%m-%d')
                                            st.metric("Current Date", current_date)
                                        with col2:
                                            new_date_obj = datetime.strptime(new_date_str, '%Y-%m-%d').date()
                                            days_passed = (date.today() - new_date_obj).days
                                            st.metric("Days Passed", f"{days_passed} days")
                                        with col3:
                                            st.write("")  # Empty column for alignment
                                        
                                        # Display comments if available
                                        if new_comments:
                                            st.info(f"💬 **Comments:** {new_comments}")
                                        
                                        st.session_state.refresh_key += 1
                                    else:
                                        st.error("❌ Investment not found")
                                        
                                except Exception as e:
                                    st.error(f"❌ Error updating investment: {str(e)}")
                                    logger.error(f"Update error: {e}")
        
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
                    # Create selection options
                    investment_options = {}
                    for inv in investments:
                        inv_date = inv.get('investment_date', '')
                        if isinstance(inv_date, date):
                            inv_date = inv_date.strftime('%Y-%m-%d')
                        amount = float(inv.get('investment_amount', 0))
                        display_key = f"{inv_date} - ₹{amount:,.2f}"
                        investment_options[display_key] = inv.get('investment_id')
                    
                    selected_display = st.selectbox(
                        "Select an investment to delete",
                        options=investment_options.keys(),
                        help="⚠️ This action cannot be undone!"
                    )
                
                if selected_display:
                    selected_id = investment_options[selected_display]
                    selected_investment = st.session_state.service.read_investment(selected_id)
                    
                    if selected_investment:
                        st.warning(f"⚠️ You are about to delete investment: `{selected_id}`")
                        
                        # Display investment details
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(
                                "Amount",
                                f"₹{float(selected_investment.get('investment_amount', 0)):,.2f}"
                            )
                        with col2:
                            inv_date = selected_investment.get('investment_date', '')
                            if isinstance(inv_date, date):
                                inv_date = inv_date.strftime('%Y-%m-%d')
                            st.metric("Date", inv_date)
                        with col3:
                            st.metric(
                                "Annual Return %",
                                f"{float(selected_investment.get('annual_return_percentage', 0)):.2f}%"
                            )
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("🗑️ Delete Investment", use_container_width=True):
                                try:
                                    if st.session_state.service.delete_investment(selected_id):
                                        st.success("✅ Investment deleted successfully!")
                                        st.session_state.refresh_key += 1
                                        import time
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("❌ Investment not found")
                                        
                                except Exception as e:
                                    st.error(f"❌ Error deleting investment: {str(e)}")
                                    logger.error(f"Delete error: {e}")
                        
                        with col2:
                            if st.button("❌ Cancel", use_container_width=True):
                                st.info("Delete operation cancelled")
        
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
    Investment Dashboard v1.0 - MySQL Edition | Built with Streamlit & MySQL | Secure Authentication
    </div>
    """,
    unsafe_allow_html=True
)
