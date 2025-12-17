"""
Authentication and Admin Pages Module
"""
import streamlit as st
from datetime import datetime
import pandas as pd
from mysql_service import AuthenticationService


def show_login_page(auth_service: AuthenticationService):
    """Display login/register page"""
    
    st.markdown("""
        <style>
        .login-container {
            max-width: 450px;
            margin: 50px auto;
        }
        .login-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }
        .login-header h1 {
            margin: 0;
            font-size: 36px;
            margin-bottom: 10px;
        }
        .login-header p {
            margin: 0;
            opacity: 0.9;
            font-size: 14px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div class="login-header">
                <h1>💼 Investment Dashboard</h1>
                <p>Secure Access</p>
            </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
        
        # LOGIN TAB
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submit = st.form_submit_button("🔓 Login", use_container_width=True)
                
                if submit:
                    if username and password:
                        try:
                            # Check user status for better feedback
                            status = auth_service.check_user_status(username, password)
                            
                            if not status['exists']:
                                st.error("❌ Invalid username or password!")
                            elif not status['password_correct']:
                                st.error("❌ Invalid username or password!")
                            elif not status['is_active']:
                                st.error("🔒 Your account is awaiting admin approval!\n\n**Please wait for an administrator to activate your account before you can login.**")
                            else:
                                # Authenticate and login
                                user = auth_service.authenticate_user(username, password)
                                if user:
                                    st.session_state.authenticated = True
                                    st.session_state.user_id = user['user_id']
                                    st.session_state.username = user['username']
                                    st.session_state.email = user['email']
                                    st.session_state.full_name = user['full_name']
                                    st.session_state.role = user['role']
                                    st.session_state.is_active = user['is_active']
                                    st.success(f"✅ Welcome, {user['full_name']}!")
                                    st.rerun()
                                else:
                                    st.error("❌ Invalid username or password!")
                        except Exception as e:
                            st.error(f"❌ Login error: {str(e)}")
                    else:
                        st.warning("⚠️ Please enter username and password")
        
        # REGISTER TAB
        with tab2:
            with st.form("register_form"):
                st.info("📝 Create a new account")
                
                reg_username = st.text_input("Username", placeholder="Choose a username", key="reg_username")
                reg_email = st.text_input("Email", placeholder="Enter your email", key="reg_email")
                reg_full_name = st.text_input("Full Name", placeholder="Enter your full name", key="reg_full_name")
                reg_password = st.text_input("Password", type="password", placeholder="Create a password", key="reg_password")
                reg_confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm password", key="reg_confirm_pwd")
                
                submit_reg = st.form_submit_button("📝 Register", use_container_width=True)
                
                if submit_reg:
                    if not all([reg_username, reg_email, reg_full_name, reg_password, reg_confirm_password]):
                        st.warning("⚠️ Please fill all fields")
                    elif reg_password != reg_confirm_password:
                        st.error("❌ Passwords do not match!")
                    elif len(reg_password) < 6:
                        st.error("❌ Password must be at least 6 characters long!")
                    else:
                        try:
                            # Check if user already exists
                            existing_user = auth_service.get_user_by_username(reg_username)
                            if existing_user:
                                st.error("❌ Username already exists!")
                            else:
                                user = auth_service.register_user(
                                    username=reg_username,
                                    email=reg_email,
                                    password=reg_password,
                                    full_name=reg_full_name,
                                    role="user"
                                )
                                st.success("✅ Registration successful!")
                                st.info("""
                                **⏳ Account Pending Activation**
                                
                                Your account has been created but needs admin approval before you can access the investment pages.
                                
                                **An administrator will review your account and activate it shortly.**
                                
                                Once activated, you will be able to:
                                - 📊 View the Investment Dashboard
                                - ➕ Create new investments
                                - 👁️ View all investments
                                - ✏️ Update investments
                                - 🗑️ Delete investments
                                
                                Please check back later or contact an administrator.
                                """)
                        except Exception as e:
                            st.error(f"❌ Registration error: {str(e)}")


def show_admin_page(auth_service: AuthenticationService):
    """Display admin dashboard and user management"""
    
    if st.session_state.role != "admin":
        st.error("❌ You don't have permission to access this page!")
        return
    
    st.header("👨‍💼 Admin Panel")
    
    tab1, tab2 = st.tabs(["👥 User Management", "📊 Statistics"])
    
    # USER MANAGEMENT TAB
    with tab1:
        st.subheader("Manage Users")
        
        try:
            users = auth_service.get_all_users()
            
            if not users:
                st.info("📭 No users found")
            else:
                # Display users table
                display_users = []
                for user in users:
                    status = "🟢 Active" if user['is_active'] else "🔴 Inactive"
                    display_users.append({
                        'Username': user['username'],
                        'Email': user['email'],
                        'Full Name': user['full_name'] or 'N/A',
                        'Role': user['role'].upper(),
                        'Status': status,
                        'Created': user['created_at'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(user['created_at'], datetime) else user['created_at']
                    })
                
                df = pd.DataFrame(display_users)
                st.dataframe(df, use_container_width=True)
                
                st.markdown("---")
                
                # User management options
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Modify User Role")
                    selected_user = st.selectbox(
                        "Select user",
                        options=[u['username'] for u in users],
                        help="Choose a user to modify"
                    )
                    
                    if selected_user:
                        user_obj = next((u for u in users if u['username'] == selected_user), None)
                        if user_obj:
                            new_role = st.radio(
                                "Select new role",
                                options=['user', 'admin'],
                                index=0 if user_obj['role'] == 'user' else 1
                            )
                            
                            if st.button("✅ Update Role", use_container_width=True):
                                try:
                                    auth_service.update_user_role(user_obj['user_id'], new_role)
                                    st.success(f"✅ Role updated for {selected_user}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error: {str(e)}")
                
                with col2:
                    st.subheader("User Actions")
                    action_user = st.selectbox(
                        "Select user for action",
                        options=[u['username'] for u in users],
                        help="Choose a user to manage",
                        key="action_user"
                    )
                    
                    if action_user:
                        user_obj = next((u for u in users if u['username'] == action_user), None)
                        if user_obj:
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                if st.button("🔓 Toggle Status", use_container_width=True):
                                    try:
                                        auth_service.toggle_user_status(user_obj['user_id'])
                                        new_status = "activated" if not user_obj['is_active'] else "deactivated"
                                        st.success(f"✅ User {new_status}: {action_user}")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Error: {str(e)}")
                            
                            with col_b:
                                if user_obj['user_id'] != st.session_state.user_id:
                                    if st.button("🗑️ Delete User", use_container_width=True):
                                        try:
                                            auth_service.delete_user(user_obj['user_id'])
                                            st.success(f"✅ User deleted: {action_user}")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ Error: {str(e)}")
                                else:
                                    st.warning("⚠️ You cannot delete your own account!")
        
        except Exception as e:
            st.error(f"❌ Error loading users: {str(e)}")
    
    # STATISTICS TAB
    with tab2:
        st.subheader("System Statistics")
        
        try:
            users = auth_service.get_all_users()
            
            col1, col2, col3, col4 = st.columns(4)
            
            total_users = len(users)
            active_users = len([u for u in users if u['is_active']])
            admin_users = len([u for u in users if u['role'] == 'admin'])
            inactive_users = total_users - active_users
            
            with col1:
                st.markdown("""
                    <div class="metric-card">
                        <div class="metric-label">👥 Total Users</div>
                        <div class="metric-value" style="font-size: 28px;">{}</div>
                    </div>
                """.format(total_users), unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                    <div class="metric-card metric-card-alt3">
                        <div class="metric-label">🟢 Active</div>
                        <div class="metric-value" style="font-size: 28px;">{}</div>
                    </div>
                """.format(active_users), unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                    <div class="metric-card metric-card-alt">
                        <div class="metric-label">👑 Admins</div>
                        <div class="metric-value" style="font-size: 28px;">{}</div>
                    </div>
                """.format(admin_users), unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                    <div class="metric-card metric-card-alt2">
                        <div class="metric-label">🔴 Inactive</div>
                        <div class="metric-value" style="font-size: 28px;">{}</div>
                    </div>
                """.format(inactive_users), unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Users by role chart
            role_data = {
                'Admin': admin_users,
                'User': total_users - admin_users
            }
            
            import plotly.express as px
            fig_roles = px.pie(
                values=list(role_data.values()),
                names=list(role_data.keys()),
                hole=0.3,
                color_discrete_map={'Admin': '#667eea', 'User': '#764ba2'}
            )
            fig_roles.update_layout(height=400)
            st.plotly_chart(fig_roles, use_container_width=True)
        
        except Exception as e:
            st.error(f"❌ Error loading statistics: {str(e)}")


def show_profile_page(auth_service: AuthenticationService):
    """Display user profile page"""
    
    st.header("👤 My Profile")
    
    try:
        user = auth_service.get_user_by_id(st.session_state.user_id)
        
        if not user:
            st.error("❌ User not found")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Profile Information")
            st.info(f"**Username:** {user['username']}")
            st.info(f"**Email:** {user['email']}")
            st.info(f"**Full Name:** {user['full_name'] or 'Not set'}")
            st.info(f"**Role:** {user['role'].upper()}")
            st.info(f"**Status:** {'🟢 Active' if user['is_active'] else '🔴 Inactive'}")
            st.info(f"**Member Since:** {user['created_at'].strftime('%Y-%m-%d %H:%M:%S') if isinstance(user['created_at'], datetime) else user['created_at']}")
        
        with col2:
            st.subheader("🔐 Security")
            
            with st.form("change_password_form"):
                current_password = st.text_input("Current Password", type="password")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                
                submit = st.form_submit_button("✅ Change Password", use_container_width=True)
                
                if submit:
                    if not all([current_password, new_password, confirm_password]):
                        st.warning("⚠️ Please fill all fields")
                    elif new_password != confirm_password:
                        st.error("❌ New passwords do not match!")
                    elif len(new_password) < 6:
                        st.error("❌ Password must be at least 6 characters long!")
                    else:
                        try:
                            if auth_service.change_password(st.session_state.user_id, current_password, new_password):
                                st.success("✅ Password changed successfully!")
                            else:
                                st.error("❌ Current password is incorrect!")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error loading profile: {str(e)}")
