"""
Investment Dashboard - Streamlit Application with Oracle CRUD Operations
"""
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime, date
import logging
import os

from oracle_service import (
    InvestmentService, 
    calculate_current_value, 
    calculate_profit_loss,
    calculate_return_percentage
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Investment Dashboard - Oracle",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 12px;
        border-radius: 4px;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 12px;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'service' not in st.session_state:
    try:
        st.session_state.service = InvestmentService(
            db_user=os.getenv('ORACLE_USER', 'system'),
            db_password=os.getenv('ORACLE_PASSWORD', 'oracle'),
            db_host=os.getenv('ORACLE_HOST', 'localhost'),
            db_port=int(os.getenv('ORACLE_PORT', '1521')),
            db_service=os.getenv('ORACLE_SERVICE', 'XEPDB1')
        )
    except Exception as e:
        st.error(f"❌ Database connection failed: {str(e)}")
        st.info("Please ensure Oracle Database is running and credentials are correct.")
        st.stop()

if 'refresh_key' not in st.session_state:
    st.session_state.refresh_key = 0

# Main title
st.title("💼 Investment Dashboard - Oracle")
st.markdown("---")

# Sidebar navigation
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/investment.png", width=50)
    st.title("Navigation")
    
    selected = option_menu(
        menu_title=None,
        options=["📊 Dashboard", "➕ Create", "👁️ View All", "✏️ Update", "🗑️ Delete"],
        icons=["graph-up", "plus-circle", "eye", "pencil-square", "trash"],
        menu_icon="cast",
        default_index=0,
    )
    
    st.markdown("---")
    st.caption("Oracle Database")
    st.caption("Investment Dashboard v2.0")

# ==================== DASHBOARD PAGE ====================
if selected == "📊 Dashboard":
    st.header("Dashboard Overview")
    
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
                amount = inv['investment_amount']
                annual_return = inv['annual_return_percentage']
                inv_date = inv['investment_date']
                
                total_invested += amount
                
                if inv_date:
                    current_val = calculate_current_value(amount, annual_return, inv_date)
                    total_current_value += current_val
                    total_profit_loss += calculate_profit_loss(current_val, amount)
            
            # Display key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Total Invested",
                    value=f"₹{total_invested:,.2f}",
                    delta=None
                )
            
            with col2:
                st.metric(
                    label="Current Value",
                    value=f"₹{total_current_value:,.2f}",
                    delta=f"₹{total_profit_loss:,.2f}"
                )
            
            with col3:
                overall_return = calculate_return_percentage(total_current_value, total_invested)
                st.metric(
                    label="Overall Return %",
                    value=f"{overall_return:.2f}%",
                    delta=None
                )
            
            with col4:
                st.metric(
                    label="Total Investments",
                    value=len(investments),
                    delta=None
                )
            
            st.markdown("---")
            
            # Display investments table
            st.subheader("All Investments")
            
            # Prepare data for display
            display_data = []
            for inv in investments:
                amount = inv['investment_amount']
                annual_return = inv['annual_return_percentage']
                inv_date = inv['investment_date']
                
                current_val = calculate_current_value(amount, annual_return, inv_date)
                profit_loss = calculate_profit_loss(current_val, amount)
                return_pct = calculate_return_percentage(current_val, amount)
                
                display_data.append({
                    'Investment ID': inv['investment_id'][:8] + '...',
                    'Amount': f"₹{amount:,.2f}",
                    'Date': inv_date,
                    'Annual Return %': f"{annual_return:.2f}%",
                    'Current Value': f"₹{current_val:,.2f}",
                    'Profit/Loss': f"₹{profit_loss:,.2f}",
                    'Return %': f"{return_pct:.2f}%"
                })
            
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True)
            
    except Exception as e:
        st.error(f"❌ Error loading dashboard: {str(e)}")
        logger.error(f"Dashboard error: {e}")

# ==================== CREATE PAGE ====================
elif selected == "➕ Create":
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
        
        submitted = st.form_submit_button("✅ Create Investment", use_container_width=True)
        
        if submitted:
            try:
                # Convert date to string
                inv_date_str = investment_date.strftime("%Y-%m-%d")
                
                # Create investment
                result = st.session_state.service.create_investment(
                    investment_amount=investment_amount,
                    investment_date=inv_date_str,
                    annual_return_percentage=annual_return_percentage
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
    st.header("All Investments")
    
    try:
        investments = st.session_state.service.read_all_investments()
        
        if not investments:
            st.info("📭 No investments found. Create one to get started!")
        else:
            # Display investments
            for idx, inv in enumerate(investments, 1):
                with st.expander(
                    f"📈 Investment #{idx} - {inv['investment_date']}", 
                    expanded=False
                ):
                    col1, col2, col3 = st.columns(3)
                    
                    amount = inv['investment_amount']
                    annual_return = inv['annual_return_percentage']
                    inv_date = inv['investment_date']
                    
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
                    
                    st.info(f"**ID:** `{inv['investment_id']}`")
            
    except Exception as e:
        st.error(f"❌ Error loading investments: {str(e)}")
        logger.error(f"View all error: {e}")

# ==================== UPDATE PAGE ====================
elif selected == "✏️ Update":
    st.header("Update Investment")
    
    try:
        investments = st.session_state.service.read_all_investments()
        
        if not investments:
            st.info("📭 No investments found to update!")
        else:
            # Create selection options
            investment_options = {
                f"{inv['investment_date']} - ₹{inv['investment_amount']:,.2f}": 
                inv['investment_id'] 
                for inv in investments
            }
            
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
                                value=selected_investment['investment_amount'],
                                min_value=0.01,
                                step=100.0,
                                format="%.2f"
                            )
                        
                        with col2:
                            inv_date_obj = datetime.strptime(
                                selected_investment['investment_date'], 
                                "%Y-%m-%d"
                            ).date()
                            new_date = st.date_input(
                                "New Investment Date",
                                value=inv_date_obj
                            )
                        
                        new_return_pct = st.number_input(
                            "New Annual Return Percentage (%)",
                            value=selected_investment['annual_return_percentage'],
                            min_value=0.0,
                            max_value=100.0,
                            step=0.1,
                            format="%.2f"
                        )
                        
                        submitted = st.form_submit_button("✅ Update Investment", use_container_width=True)
                        
                        if submitted:
                            try:
                                new_date_str = new_date.strftime("%Y-%m-%d")
                                
                                result = st.session_state.service.update_investment(
                                    investment_id=selected_id,
                                    investment_amount=new_amount,
                                    investment_date=new_date_str,
                                    annual_return_percentage=new_return_pct
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
    st.header("Delete Investment")
    
    try:
        investments = st.session_state.service.read_all_investments()
        
        if not investments:
            st.info("📭 No investments found to delete!")
        else:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Create selection options
                investment_options = {
                    f"{inv['investment_date']} - ₹{inv['investment_amount']:,.2f}": 
                    inv['investment_id'] 
                    for inv in investments
                }
                
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
                            f"₹{selected_investment['investment_amount']:,.2f}"
                        )
                    with col2:
                        st.metric("Date", selected_investment['investment_date'])
                    with col3:
                        st.metric(
                            "Annual Return %",
                            f"{selected_investment['annual_return_percentage']:.2f}%"
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

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray; font-size: 12px;'>
    Investment Dashboard v2.0 - Oracle Edition | Built with Streamlit & Oracle Database
    </div>
    """,
    unsafe_allow_html=True
)
