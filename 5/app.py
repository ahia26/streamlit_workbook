import streamlit as st
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text
import hashlib
import os
from dotenv import load_dotenv
import time
import base64
from datetime import datetime

# Set page configuration immediately
st.set_page_config(
    page_title="Inventory Manager Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for improved design
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem !important;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f0f0f0;
    }
    .sub-header {
        font-size: 1.8rem !important;
        color: #333;
        margin-top: 1rem;
        margin-bottom: 1rem;
        padding-left: 0.5rem;
        border-left: 4px solid #1E88E5;
    }
    .info-box {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1E88E5;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #E8F5E9;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4CAF50;
        margin-bottom: 1rem;
    }
    .error-box {
        background-color: #FFEBEE;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #F44336;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        border-radius: 0.3rem;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #1976D2;
    }
    [data-testid="stForm"] {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    div[data-testid="stDataFrame"] {
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #f0f0f0;
        color: #888;
        font-size: 0.8rem;
    }
    .logout-btn {
        float: right;
    }
    .welcome-header {
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# Database configuration
DB_USER = os.getenv("DB_USER", "root1")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "streamlit_demo")

# Create database connection
@st.cache_resource
def init_connection():
    try:
        connection_string = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        show_error(f"Database connection error: {e}")
        return None

# Initialize database schema if needed
def initialize_database():
    engine = init_connection()
    if engine is None:
        return False
    
    # Create users table if it doesn't exist
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(64) NOT NULL,
        is_admin BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Create products table if it doesn't exist
    create_products_table = """
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        category VARCHAR(50),
        price DECIMAL(10, 2) NOT NULL,
        inventory INT DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );
    """
    
    try:
        with engine.begin() as conn:
            # Create tables
            conn.execute(text(create_users_table))
            conn.execute(text(create_products_table))
            
            # Check if admin user exists
            result = conn.execute(text("SELECT COUNT(*) FROM users WHERE is_admin = TRUE"))
            admin_exists = result.scalar()
            
            # Add admin user if none exists
            if not admin_exists:
                admin_password_hash = hash_password("admin123")
                conn.execute(text(
                    "INSERT INTO users (username, password_hash, is_admin) VALUES ('admin', :password_hash, TRUE)"
                ), {"password_hash": admin_password_hash})
                
                # Add sample products
                sample_products = [
                    ("MacBook Pro", "Electronics", 1999.99, 15),
                    ("Espresso Machine", "Appliances", 389.99, 8),
                    ("Ergonomic Chair", "Furniture", 249.99, 12),
                    ("iPhone 13", "Electronics", 899.99, 25),
                    ("Noise-Cancelling Headphones", "Electronics", 299.99, 18),
                    ("Standing Desk", "Furniture", 499.99, 7),
                    ("Smart Watch", "Electronics", 349.99, 20),
                    ("Air Purifier", "Appliances", 179.99, 15),
                    ("Bluetooth Speaker", "Electronics", 89.99, 30),
                    ("Robotic Vacuum", "Appliances", 279.99, 10)
                ]
                
                for product in sample_products:
                    conn.execute(text(
                        "INSERT INTO products (name, category, price, inventory) VALUES (:name, :category, :price, :inventory)"
                    ), {"name": product[0], "category": product[1], "price": product[2], "inventory": product[3]})
        
        return True
    except Exception as e:
        show_error(f"Database initialization error: {e}")
        return False

# Execute query with caching for read-only queries
@st.cache_data(ttl=60)
def run_query(query, params=None):
    engine = init_connection()
    if engine is None:
        return None
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            return pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as e:
        # If table doesn't exist, try to initialize database
        if "doesn't exist" in str(e):
            with st.spinner("Setting up database..."):
                if initialize_database():
                    # Try the query again after initialization
                    with engine.connect() as conn:
                        result = conn.execute(text(query), params or {})
                        return pd.DataFrame(result.fetchall(), columns=result.keys())
                else:
                    show_error(f"Query execution error: {e}")
                    return None
        else:
            show_error(f"Query execution error: {e}")
            return None

# Execute query without caching for write operations
def execute_query(query, params=None):
    engine = init_connection()
    if engine is None:
        return False
    
    try:
        with engine.begin() as conn:
            conn.execute(text(query), params or {})
            return True
    except Exception as e:
        # If table doesn't exist, try to initialize database
        if "doesn't exist" in str(e):
            with st.spinner("Setting up database..."):
                if initialize_database():
                    # Try the query again after initialization
                    with engine.begin() as conn:
                        conn.execute(text(query), params or {})
                        return True
                else:
                    show_error(f"Query execution error: {e}")
                    return False
        else:
            show_error(f"Query execution error: {e}")
            return False

# Hash password for secure storage
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Verify password
def verify_password(username, password):
    hashed_password = hash_password(password)
    query = "SELECT * FROM users WHERE username = :username AND password_hash = :password_hash"
    result = run_query(query, {"username": username, "password_hash": hashed_password})
    return not result.empty if result is not None else False

# Custom notification functions
def show_info(message):
    st.markdown(f'<div class="info-box">{message}</div>', unsafe_allow_html=True)

def show_success(message):
    st.markdown(f'<div class="success-box">{message}</div>', unsafe_allow_html=True)

def show_error(message):
    st.markdown(f'<div class="error-box">{message}</div>', unsafe_allow_html=True)

# Loading animation
def show_loading_animation():
    with st.spinner('Processing...'):
        time.sleep(0.5)

# User authentication system
def login_page():
    # Add a logo or banner image
    st.markdown('<h1 class="main-header">📊 Inventory Manager Pro</h1>', unsafe_allow_html=True)
    
    # Create a clean login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<h2 class="sub-header">Sign In</h2>', unsafe_allow_html=True)
        #show_info("Default login: username = <b>admin</b>, password = <b>admin123</b>")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns(2)
            with col1:
                submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                show_loading_animation()
                if verify_password(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.login_time = datetime.now().strftime("%H:%M:%S")
                    st.rerun()
                else:
                    show_error("Invalid username or password")
    
    # Add footer
    st.markdown('<div class="footer">© 2025 Inventory Manager Pro. All rights reserved.</div>', unsafe_allow_html=True)

# Dashboard metrics
def get_dashboard_metrics():
    metrics = {}
    
    # Total products
    query = "SELECT COUNT(*) as total FROM products"
    result = run_query(query)
    metrics['total_products'] = result['total'].iloc[0] if result is not None and not result.empty else 0
    
    # Total inventory value
    query = "SELECT SUM(price * inventory) as value FROM products"
    result = run_query(query)
    metrics['total_value'] = result['value'].iloc[0] if result is not None and not result.empty else 0
    
    # Low stock products (less than 10)
    query = "SELECT COUNT(*) as low_stock FROM products WHERE inventory < 10"
    result = run_query(query)
    metrics['low_stock'] = result['low_stock'].iloc[0] if result is not None and not result.empty else 0
    
    # Category distribution
    query = "SELECT category, COUNT(*) as count FROM products GROUP BY category"
    metrics['categories'] = run_query(query)
    
    return metrics

# Product management page
def product_management():
    # Header with logout button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<h1 class="main-header">📊 Inventory Manager Pro</h1>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Welcome message with username and login time
    st.markdown(f'<h3 class="welcome-header">Welcome, {st.session_state.username}! | Login time: {st.session_state.login_time}</h3>', unsafe_allow_html=True)
    
    # Dashboard
    st.markdown('<h2 class="sub-header">Dashboard</h2>', unsafe_allow_html=True)
    metrics = get_dashboard_metrics()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Products", metrics['total_products'])
    with col2:
        st.metric("Inventory Value", f"${metrics['total_value']:,.2f}")
    with col3:
        st.metric("Low Stock Items", metrics['low_stock'])
    
    # Tabs for different sections
    tab1, tab2 = st.tabs(["📋 Product Inventory", "➕ Add New Product"])
    
    # Tab 1: Product Inventory
    with tab1:
        st.markdown('<h2 class="sub-header">Product Inventory</h2>', unsafe_allow_html=True)
        
        # Filter options in a nice form
        with st.expander("🔍 Filter Options", expanded=True):
            col1, col2 = st.columns(2)
            
            # Default category to "All" in case query fails
            selected_category = "All"
            
            with col1:
                categories = run_query("SELECT DISTINCT category FROM products")
                if categories is not None and not categories.empty:
                    category_list = ["All"] + categories["category"].tolist()
                    selected_category = st.selectbox("Category", category_list)
            
            with col2:
                price_range = st.slider(
                    "Price Range ($)", 
                    min_value=0.0, 
                    max_value=2000.0, 
                    value=(0.0, 2000.0),
                    step=10.0
                )
                
            # Sort options
            sort_col, sort_dir = st.columns(2)
            with sort_col:
                sort_by = st.selectbox("Sort by", ["id", "name", "price", "inventory", "category"])
            with sort_dir:
                sort_direction = st.selectbox("Order", ["Ascending", "Descending"])
        
        # Build query based on filters
        query = "SELECT * FROM products WHERE 1=1"
        params = {}
        
        if selected_category != "All":
            query += " AND category = :category"
            params["category"] = selected_category
        
        query += " AND price BETWEEN :min_price AND :max_price"
        params["min_price"] = price_range[0]
        params["max_price"] = price_range[1]
        
        # Add sorting
        sort_direction_sql = "DESC" if sort_direction == "Descending" else "ASC"
        query += f" ORDER BY {sort_by} {sort_direction_sql}"
        
        # Display filtered products
        products = run_query(query, params)
        if products is not None and not products.empty:
            # Format price with dollar sign
            products['price'] = products['price'].apply(lambda x: f"${x:,.2f}")
            
            # Add styling to highlight low inventory
            def highlight_low_inventory(val):
                try:
                    inventory = int(val)
                    if inventory < 10:
                        return 'background-color: #FFEBEE'
                    else:
                        return ''
                except:
                    return ''
            
            # Apply styling and display
            st.dataframe(
                products, 
                column_config={
                    "id": "ID",
                    "name": "Product Name",
                    "category": "Category",
                    "price": "Price",
                    "inventory": "In Stock",
                    "created_at": "Created",
                    "updated_at": "Updated"
                },
                height=400,
                use_container_width=True
            )
        else:
            show_info("No products found with the current filters.")
    
    # Tab 2: Add New Product
    with tab2:
        st.markdown('<h2 class="sub-header">Add New Product</h2>', unsafe_allow_html=True)
        
        with st.form("new_product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Product Name", placeholder="Enter product name")
                
                # Get existing categories for dropdown
                categories = run_query("SELECT DISTINCT category FROM products")
                if categories is not None and not categories.empty:
                    category_list = categories["category"].tolist()
                    category = st.selectbox("Category", ["Select category..."] + category_list)
                    if category == "Select category...":
                        category = st.text_input("Or enter a new category", placeholder="Enter category name")
                else:
                    category = st.text_input("Category", placeholder="Enter category")
            
            with col2:
                price = st.number_input("Price ($)", min_value=0.01, step=0.01, format="%.2f")
                inventory = st.number_input("Initial Inventory", min_value=0, step=1)
            
            submit = st.form_submit_button("Add Product", use_container_width=True)
            
            if submit:
                if name and category and price > 0:
                    with st.spinner("Adding product..."):
                        insert_query = """
                        INSERT INTO products (name, category, price, inventory) 
                        VALUES (:name, :category, :price, :inventory)
                        """
                        if execute_query(insert_query, {
                            "name": name, 
                            "category": category, 
                            "price": price, 
                            "inventory": inventory
                        }):
                            show_success("Product added successfully!")
                            # Clear cache to reflect new data
                            st.cache_data.clear()
                            time.sleep(1)
                            st.rerun()
                else:
                    show_error("Please fill all required fields")
    
    # Add footer
    st.markdown('<div class="footer">© 2025 Inventory Manager Pro. All rights reserved.</div>', unsafe_allow_html=True)

# Main app
def main():
    # Initialize session state for authentication
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "login_time" not in st.session_state:
        st.session_state.login_time = None
    
    # Display appropriate page based on authentication status
    if not st.session_state.authenticated:
        login_page()
    else:
        product_management()

if __name__ == "__main__":
    main()