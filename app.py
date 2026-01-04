"""
Xərclər - Personal Expense Tracker
Built with Streamlit + Supabase
Date/Time is based on Azerbaijan Baku time (UTC+4)
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client
import os

# Page configuration
st.set_page_config(
    page_title="Xərclər - Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Azerbaijan Baku timezone
BAKU_TZ = pytz.timezone('Asia/Baku')

# Default categories
DEFAULT_CATEGORIES = [
    'Food & Dining', 'Transportation', 'Shopping', 'Entertainment',
    'Bills & Utilities', 'Healthcare', 'Education', 'Travel',
    'Groceries', 'Personal Care', 'Gifts', 'Geyim', 'Other'
]

# Custom CSS for beautiful dark theme with gold accents
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Sans+3:wght@300;400;500;600&display=swap');
    
    :root {
        --bg-primary: #0a0e17;
        --bg-card: #1a2332;
        --accent-gold: #d4a574;
        --accent-copper: #b87333;
        --text-primary: #f4f1eb;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0e17 0%, #111827 50%, #0a0e17 100%);
    }
    
    .main-header {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #e8c9a8, #b87333);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: 2px;
    }
    
    .subtitle {
        text-align: center;
        color: #9ca3af;
        font-size: 1.1rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }
    
    .baku-time {
        text-align: center;
        color: #d4a574;
        font-size: 1rem;
        padding: 0.5rem 1rem;
        background: rgba(26, 35, 50, 0.8);
        border-radius: 50px;
        display: inline-block;
        margin: 0 auto 2rem;
        border: 1px solid #2a3544;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #1a2332 0%, #111827 100%);
        border: 1px solid #2a3544;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        border-color: #d4a574;
        transform: translateY(-2px);
    }
    
    .stat-value {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        font-weight: 700;
        color: #d4a574;
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .expense-item {
        background: #0d1219;
        border: 1px solid #2a3544;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .expense-item:hover {
        border-color: #d4a574;
    }
    
    .category-badge {
        background: rgba(212, 165, 116, 0.15);
        color: #d4a574;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
    }
    
    div[data-testid="stMetricValue"] {
        font-family: 'Playfair Display', serif;
        color: #d4a574;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #d4a574, #b87333);
        color: #0a0e17;
        border: none;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(212, 165, 116, 0.3);
    }
    
    .stSelectbox > div > div {
        background: #0d1219;
        border-color: #2a3544;
    }
    
    .stTextInput > div > div > input {
        background: #0d1219;
        border-color: #2a3544;
        color: #f4f1eb;
    }
    
    .stNumberInput > div > div > input {
        background: #0d1219;
        border-color: #2a3544;
        color: #f4f1eb;
    }
    
    .stDateInput > div > div > input {
        background: #0d1219;
        border-color: #2a3544;
        color: #f4f1eb;
    }
    
    section[data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #2a3544;
    }
    
    .sidebar-header {
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        color: #d4a574;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def get_baku_now():
    """Get current datetime in Baku timezone"""
    return datetime.now(BAKU_TZ)


def get_baku_date():
    """Get current date in Baku timezone"""
    return get_baku_now().date()


@st.cache_resource
def init_supabase():
    """Initialize Supabase client"""
    url = st.secrets.get("SUPABASE_URL", os.environ.get("SUPABASE_URL", ""))
    key = st.secrets.get("SUPABASE_KEY", os.environ.get("SUPABASE_KEY", ""))
    
    if not url or not key:
        return None
    
    return create_client(url, key)


def create_tables_if_not_exist(supabase: Client):
    """
    Note: Tables should be created in Supabase dashboard with this SQL:
    
    CREATE TABLE IF NOT EXISTS expenses (
        id SERIAL PRIMARY KEY,
        description TEXT NOT NULL,
        category TEXT NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        date DATE NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    CREATE TABLE IF NOT EXISTS categories (
        id SERIAL PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
    );
    
    -- Insert default categories
    INSERT INTO categories (name) VALUES 
        ('Food & Dining'), ('Transportation'), ('Shopping'), ('Entertainment'),
        ('Bills & Utilities'), ('Healthcare'), ('Education'), ('Travel'),
        ('Groceries'), ('Personal Care'), ('Gifts'), ('Other')
    ON CONFLICT (name) DO NOTHING;
    """
    pass


def get_expenses(supabase: Client, start_date=None, end_date=None):
    """Fetch expenses from Supabase"""
    try:
        query = supabase.table('expenses').select('*')
        
        if start_date:
            query = query.gte('date', str(start_date))
        if end_date:
            query = query.lte('date', str(end_date))
        
        response = query.order('date', desc=True).order('id', desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching expenses: {e}")
        return []


def add_expense(supabase: Client, description: str, category: str, amount: float, date: str):
    """Add a new expense"""
    try:
        response = supabase.table('expenses').insert({
            'description': description,
            'category': category,
            'amount': amount,
            'date': date
        }).execute()
        return True
    except Exception as e:
        st.error(f"Error adding expense: {e}")
        return False


def delete_expense(supabase: Client, expense_id: int):
    """Delete an expense"""
    try:
        supabase.table('expenses').delete().eq('id', expense_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting expense: {e}")
        return False


def get_categories(supabase: Client):
    """Get all categories"""
    try:
        response = supabase.table('categories').select('name').order('name').execute()
        return [row['name'] for row in response.data]
    except:
        return DEFAULT_CATEGORIES


def calculate_summary(expenses, start_date, end_date):
    """Calculate summary statistics"""
    if not expenses:
        return {
            'total': 0,
            'count': 0,
            'average': 0,
            'by_category': [],
            'by_description': []
        }
    
    df = pd.DataFrame(expenses)
    df['amount'] = df['amount'].astype(float)
    
    # Filter by date range
    df['date'] = pd.to_datetime(df['date'])
    mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
    df = df[mask]
    
    if df.empty:
        return {
            'total': 0,
            'count': 0,
            'average': 0,
            'by_category': [],
            'by_description': []
        }
    
    total = df['amount'].sum()
    count = len(df)
    average = total / count if count > 0 else 0
    
    by_category = df.groupby('category').agg({
        'amount': 'sum',
        'id': 'count'
    }).rename(columns={'id': 'count'}).reset_index()
    by_category = by_category.sort_values('amount', ascending=False)
    
    by_description = df.groupby('description').agg({
        'amount': 'sum',
        'id': 'count'
    }).rename(columns={'id': 'count'}).reset_index()
    by_description = by_description.sort_values('amount', ascending=False)
    
    return {
        'total': total,
        'count': count,
        'average': average,
        'by_category': by_category.to_dict('records'),
        'by_description': by_description.to_dict('records')
    }


def main():
    # Header
    st.markdown('<h1 class="main-header">Xərclər</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Personal Expense Tracker</p>', unsafe_allow_html=True)
    
    # Display Baku time
    baku_now = get_baku_now()
    st.markdown(
        f'<div style="text-align: center;"><span class="baku-time">🕐 Baku: {baku_now.strftime("%Y-%m-%d %H:%M:%S")}</span></div>',
        unsafe_allow_html=True
    )
    
    # Initialize Supabase
    supabase = init_supabase()
    
    if supabase is None:
        st.warning("⚠️ Supabase not configured. Please set up your Supabase credentials.")
        st.info("""
        ### Setup Instructions:
        
        1. **Create a Supabase account** at [supabase.com](https://supabase.com)
        
        2. **Create a new project** and run this SQL in the SQL Editor:
        
        ```sql
        CREATE TABLE IF NOT EXISTS expenses (
            id SERIAL PRIMARY KEY,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            date DATE NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        );
        
        INSERT INTO categories (name) VALUES 
            ('Food & Dining'), ('Transportation'), ('Shopping'), ('Entertainment'),
            ('Bills & Utilities'), ('Healthcare'), ('Education'), ('Travel'),
            ('Groceries'), ('Personal Care'), ('Gifts'), ('Other')
        ON CONFLICT (name) DO NOTHING;
        ```
        
        3. **Get your credentials** from Project Settings → API:
           - Project URL
           - anon/public key
        
        4. **Create `.streamlit/secrets.toml`**:
        ```toml
        SUPABASE_URL = "your-project-url"
        SUPABASE_KEY = "your-anon-key"
        ```
        
        5. **For Streamlit Cloud deployment**, add these secrets in the app settings.
        """)
        
        # Demo mode with session state
        if 'demo_expenses' not in st.session_state:
            st.session_state.demo_expenses = []
        
        st.markdown("---")
        st.subheader("🎮 Demo Mode (data stored in session only)")
        demo_mode(None)
        return
    
    # Main app with Supabase
    demo_mode(supabase)


def demo_mode(supabase):
    """Main app logic - works with Supabase or demo mode"""
    
    # Sidebar for adding expenses
    with st.sidebar:
        st.markdown('<p class="sidebar-header">➕ Add Expense</p>', unsafe_allow_html=True)
        
        with st.form("add_expense_form", clear_on_submit=True):
            expense_date = st.date_input(
                "Date",
                value=get_baku_date(),
                format="YYYY-MM-DD"
            )
            
            description = st.text_input("Description", placeholder="What did you spend on?")
            
            if supabase:
                categories = get_categories(supabase)
            else:
                categories = DEFAULT_CATEGORIES
            
            category = st.selectbox("Category", options=categories)
            
            amount = st.number_input("Amount (₼)", min_value=0.0, step=0.01, format="%.2f")
            
            submitted = st.form_submit_button("Add Expense", use_container_width=True)
            
            if submitted:
                if description and amount > 0:
                    if supabase:
                        if add_expense(supabase, description, category, amount, str(expense_date)):
                            st.success("✅ Expense added!")
                            st.rerun()
                    else:
                        # Demo mode
                        new_id = len(st.session_state.demo_expenses) + 1
                        st.session_state.demo_expenses.insert(0, {
                            'id': new_id,
                            'description': description,
                            'category': category,
                            'amount': amount,
                            'date': str(expense_date)
                        })
                        st.success("✅ Expense added!")
                        st.rerun()
                else:
                    st.error("Please fill in all fields")
    
    # Main content area
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📋 Recent Expenses")
        
        if supabase:
            expenses = get_expenses(supabase)
        else:
            expenses = st.session_state.demo_expenses
        
        if not expenses:
            st.info("No expenses yet. Add your first expense!")
        else:
            for expense in expenses[:15]:
                with st.container():
                    c1, c2, c3 = st.columns([3, 1, 1])
                    with c1:
                        st.markdown(f"**{expense['description']}**")
                        st.markdown(f"<span class='category-badge'>{expense['category']}</span> · {expense['date']}", unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"**₼{float(expense['amount']):.2f}**")
                    with c3:
                        if st.button("🗑️", key=f"del_{expense['id']}"):
                            if supabase:
                                if delete_expense(supabase, expense['id']):
                                    st.rerun()
                            else:
                                st.session_state.demo_expenses = [
                                    e for e in st.session_state.demo_expenses 
                                    if e['id'] != expense['id']
                                ]
                                st.rerun()
                    st.markdown("---")
    
    with col2:
        st.subheader("📊 Summary & Analysis")
        
        # Time period selector
        period_options = {
            'Week': 7,
            'Month': 30,
            '3 Months': 90,
            '6 Months': 180,
            'Year': 365,
            'Custom': 0
        }
        
        selected_period = st.selectbox("Time Period", options=list(period_options.keys()))
        
        today = get_baku_date()
        
        if selected_period == 'Custom':
            date_col1, date_col2 = st.columns(2)
            with date_col1:
                start_date = st.date_input("Start Date", value=today - timedelta(days=30))
            with date_col2:
                end_date = st.date_input("End Date", value=today)
        else:
            days = period_options[selected_period]
            start_date = today - timedelta(days=days)
            end_date = today
        
        # Get and calculate summary
        if supabase:
            all_expenses = get_expenses(supabase, start_date, end_date)
        else:
            all_expenses = [
                e for e in st.session_state.demo_expenses
                if start_date <= datetime.strptime(e['date'], '%Y-%m-%d').date() <= end_date
            ]
        
        summary = calculate_summary(all_expenses, start_date, end_date)
        
        # Stats cards
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        
        with stat_col1:
            st.metric("Total Spent", f"₼{summary['total']:.2f}")
        with stat_col2:
            st.metric("Transactions", summary['count'])
        with stat_col3:
            st.metric("Average", f"₼{summary['average']:.2f}")
        
        # Charts
        if summary['by_category']:
            st.markdown("### By Category")
            
            cat_df = pd.DataFrame(summary['by_category'])
            
            fig = px.pie(
                cat_df, 
                values='amount', 
                names='category',
                color_discrete_sequence=px.colors.sequential.Oranges,
                hole=0.4
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#9ca3af',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5
                )
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Category table
            st.dataframe(
                cat_df.rename(columns={
                    'category': 'Category',
                    'amount': 'Total (₼)',
                    'count': 'Count'
                }),
                use_container_width=True,
                hide_index=True
            )
        
        if summary['by_description']:
            st.markdown("### By Description")
            
            desc_df = pd.DataFrame(summary['by_description']).head(10)
            
            fig = px.bar(
                desc_df,
                x='amount',
                y='description',
                orientation='h',
                color='amount',
                color_continuous_scale='Oranges'
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#9ca3af',
                showlegend=False,
                yaxis_title="",
                xaxis_title="Amount (₼)",
                coloraxis_showscale=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Export section
        st.markdown("### 📥 Export Data")
        
        export_col1, export_col2, export_col3 = st.columns(3)
        
        if all_expenses:
            df_export = pd.DataFrame(all_expenses)
            
            with export_col1:
                csv_all = df_export[['date', 'description', 'category', 'amount']].to_csv(index=False)
                st.download_button(
                    "📄 All Expenses",
                    csv_all,
                    f"expenses_{start_date}_to_{end_date}.csv",
                    "text/csv",
                    use_container_width=True
                )
            
            with export_col2:
                if summary['by_category']:
                    csv_cat = pd.DataFrame(summary['by_category']).to_csv(index=False)
                    st.download_button(
                        "📊 By Category",
                        csv_cat,
                        f"expenses_by_category_{start_date}_to_{end_date}.csv",
                        "text/csv",
                        use_container_width=True
                    )
            
            with export_col3:
                if summary['by_description']:
                    csv_desc = pd.DataFrame(summary['by_description']).to_csv(index=False)
                    st.download_button(
                        "📝 By Description",
                        csv_desc,
                        f"expenses_by_description_{start_date}_to_{end_date}.csv",
                        "text/csv",
                        use_container_width=True
                    )
        else:
            st.info("No data to export for the selected period.")


if __name__ == "__main__":
    main()

