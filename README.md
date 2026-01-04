# Xərclər - Personal Expense Tracker

A beautiful expense tracking application with Azerbaijan Baku timezone support, built with Streamlit and Supabase.

## Features

- **Daily Expense Tracking**: Add expenses with description, category, and amount
- **Baku Time**: All dates are based on Azerbaijan Baku time (UTC+4)
- **Cloud Storage**: Data stored securely in Supabase (PostgreSQL)
- **Categories**: Pre-defined categories for organizing expenses
- **Summary & Analysis**:
  - View summaries for different time periods (Week, Month, 3 Months, 6 Months, Year)
  - Custom date range selection
  - Interactive pie chart for category breakdown
  - Bar chart for description analysis
- **CSV Export**: Export your data in three formats:
  - All expenses (raw data)
  - Grouped by category
  - Grouped by description

## Quick Start

### 1. Clone and Install

```bash
cd expenses-app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set Up Supabase (Free Cloud Database)

1. **Create a Supabase account** at [supabase.com](https://supabase.com) (it's free!)

2. **Create a new project** and wait for it to initialize

3. **Run this SQL** in the SQL Editor (left sidebar → SQL Editor):

```sql
-- Create expenses table
CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create categories table
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

-- Enable Row Level Security (optional but recommended)
ALTER TABLE expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;

-- Allow all operations for now (you can restrict this later)
CREATE POLICY "Allow all" ON expenses FOR ALL USING (true);
CREATE POLICY "Allow all" ON categories FOR ALL USING (true);
```

4. **Get your credentials** from Project Settings → API:
   - Copy **Project URL**
   - Copy **anon/public** key

### 3. Configure Secrets

Create `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_KEY = "your-anon-public-key"
```

### 4. Run the App

```bash
streamlit run app.py
```

The app will open at http://localhost:8501

## Deploy to Streamlit Cloud (Free)

1. Push your code to GitHub (don't include `secrets.toml`!)

2. Go to [share.streamlit.io](https://share.streamlit.io)

3. Connect your GitHub repository

4. Add your secrets in the app settings:
   - Click "Advanced settings"
   - Add your `SUPABASE_URL` and `SUPABASE_KEY`

5. Deploy! 🚀

## Project Structure

```
expenses-app/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── .streamlit/
    └── secrets.toml       # Your Supabase credentials (don't commit!)
```

## Tech Stack

- **Frontend**: Streamlit
- **Database**: Supabase (PostgreSQL)
- **Charts**: Plotly
- **Data Processing**: Pandas
- **Timezone**: pytz for Baku timezone handling

## Currency

The app uses Azerbaijan Manat (₼ / AZN) as the default currency.

## Demo Mode

If Supabase is not configured, the app runs in demo mode where data is stored temporarily in the session. This is great for testing but data will be lost when you close the browser.
