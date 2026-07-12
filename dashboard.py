import os
import re
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="Sales Performance & Revenue Trends Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State for Theme Preferences
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

# ================= SIDEBAR THEME SWITCHER =================
st.sidebar.markdown("<h2 style='margin-top: 0; font-weight: 700;'>⚙️ Preferences</h2>", unsafe_allow_html=True)
st.session_state.dark_mode = True

# Theme Colors Definition based on theme selection
if st.session_state.dark_mode:
    COLOR_PRIMARY = "#F8FAFC"    # Slate 50
    COLOR_ACCENT = "#2DD4BF"     # Teal 400
    COLOR_SECONDARY = "#94A3B8"  # Slate 400
    COLOR_LIGHT = "#0F172A"      # Slate 900
    COLOR_BORDER = "#334155"     # Slate 700
    COLOR_SIDEBAR = "#1E293B"    # Slate 800
    COLOR_CARD_BG = "#1E293B"    # Slate 800
    COLOR_TEXT = "#E2E8F0"       # Slate 200
    
    # Status card colors
    COLOR_STATUS_DEFAULT_BG = "#1E3A8A"
    COLOR_STATUS_DEFAULT_BORDER = "#2563EB"
    COLOR_STATUS_DEFAULT_TEXT = "#DBEAFE"
    COLOR_STATUS_UPLOADED_BG = "#064E3B"
    COLOR_STATUS_UPLOADED_BORDER = "#059669"
    COLOR_STATUS_UPLOADED_TEXT = "#D1FAE5"
    
    CHART_PALETTE = ["#38BDF8", "#2DD4BF", "#60A5FA", "#FBBF24", "#F87171", "#A78BFA"]
    PLOTLY_TEXT_COLOR = "#94A3B8"
    PLOTLY_GRID_COLOR = "#334155"
else:
    COLOR_PRIMARY = "#0F172A"    # Slate 900
    COLOR_ACCENT = "#0D9488"     # Teal 600
    COLOR_SECONDARY = "#475569"  # Slate 600
    COLOR_LIGHT = "#F8FAFC"      # Slate 50
    COLOR_BORDER = "#E2E8F0"     # Slate 200
    COLOR_SIDEBAR = "#F1F5F9"    # Slate 100
    COLOR_CARD_BG = "#FFFFFF"    # Pure White
    COLOR_TEXT = "#1E293B"       # Slate 800
    
    # Status card colors
    COLOR_STATUS_DEFAULT_BG = "#EFF6FF"
    COLOR_STATUS_DEFAULT_BORDER = "#BFDBFE"
    COLOR_STATUS_DEFAULT_TEXT = "#1E40AF"
    COLOR_STATUS_UPLOADED_BG = "#ECFDF5"
    COLOR_STATUS_UPLOADED_BORDER = "#A7F3D0"
    COLOR_STATUS_UPLOADED_TEXT = "#065F46"
    
    CHART_PALETTE = ["#0F172A", "#0D9488", "#3B82F6", "#F59E0B", "#EF4444", "#8B5CF6"]
    PLOTLY_TEXT_COLOR = "#475569"
    PLOTLY_GRID_COLOR = "#F1F5F9"

# Custom CSS styling for premium look and feel
st.markdown(f"""
    <style>
    /* Main Background */
    .stApp {{
        background-color: {COLOR_LIGHT};
        color: {COLOR_TEXT};
    }}
    /* Sidebar Background */
    section[data-testid="stSidebar"] {{
        background-color: {COLOR_SIDEBAR} !important;
        border-right: 1px solid {COLOR_BORDER};
    }}
    /* Sidebar Header Colors */
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {{
        color: {COLOR_PRIMARY} !important;
    }}
    /* Sidebar text colors */
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] li, 
    section[data-testid="stSidebar"] span {{
        color: {COLOR_TEXT};
    }}
    /* Title and Header customization */
    h1 {{
        color: {COLOR_PRIMARY};
        font-weight: 800 !important;
        margin-bottom: 2px !important;
    }}
    h3 {{
        color: {COLOR_SECONDARY};
        font-weight: 600 !important;
    }}
    /* Metric container styling (styled into clean cards) */
    div[data-testid="stMetric"] {{
        background-color: {COLOR_CARD_BG};
        border: 1px solid {COLOR_BORDER};
        padding: 18px 22px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }}
    div[data-testid="stMetricValue"] {{
        font-size: 28px !important;
        font-weight: 700 !important;
        color: {COLOR_PRIMARY} !important;
    }}
    div[data-testid="stMetricLabel"] {{
        font-size: 14px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        color: {COLOR_SECONDARY} !important;
        font-weight: 600 !important;
    }}
    /* File uploader outer card and internal dropzone */
    div[data-testid="stFileUploader"] {{
        background-color: {COLOR_CARD_BG} !important;
        border: 1px solid {COLOR_BORDER} !important;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }}
    /* Upload dropzone - always dark with white text */
    div[data-testid="stFileUploaderDropzone"] {{
        border: 2px dashed {COLOR_ACCENT} !important;
        background-color: #1E293B !important;
        border-radius: 8px !important;
    }}
    div[data-testid="stFileUploaderDropzone"] span,
    div[data-testid="stFileUploaderDropzone"] small,
    div[data-testid="stFileUploaderDropzone"] p {{
        color: #FFFFFF !important;
        font-weight: 500 !important;
    }}
    /* Upload button - white text on dark */
    div[data-testid="stFileUploaderDropzone"] button {{
        background-color: {COLOR_ACCENT} !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 700 !important;
        padding: 8px 20px !important;
        border-radius: 6px !important;
    }}
    div[data-testid="stFileUploaderDropzone"] button span,
    div[data-testid="stFileUploaderDropzone"] button p,
    div[data-testid="stFileUploaderDropzone"] button small,
    div[data-testid="stFileUploaderDropzone"] button * {{
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }}
    /* Toggle - always dark background with white text */
    div[data-testid="stToggle"] {{
        background-color: #1E293B !important;
        border: 2px solid {COLOR_ACCENT} !important;
        padding: 12px 18px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.15);
        margin-bottom: 20px;
    }}
    div[data-testid="stToggle"] *,
    div[data-testid="stToggle"] p,
    div[data-testid="stToggle"] span,
    div[data-testid="stToggle"] label,
    div[data-testid="stToggle"] label span {{
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 15px !important;
    }}
    /* Upload icon color fix */
    div[data-testid="stFileUploaderDropzone"] svg {{
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
    }}
    /* File uploader status custom card */
    .status-card {{
        padding: 12px;
        border-radius: 8px;
        font-size: 13px;
        margin-bottom: 15px;
        line-height: 1.4;
    }}
    .status-default {{
        background-color: {COLOR_STATUS_DEFAULT_BG};
        border: 1px solid {COLOR_STATUS_DEFAULT_BORDER};
        color: {COLOR_STATUS_DEFAULT_TEXT};
    }}
    .status-uploaded {{
        background-color: {COLOR_STATUS_UPLOADED_BG};
        border: 1px solid {COLOR_STATUS_UPLOADED_BORDER};
        color: {COLOR_STATUS_UPLOADED_TEXT};
    }}
    </style>
""", unsafe_allow_html=True)

# Helper to extract digits for chronological sorting of periods/files
def get_period_sort_key(period_name):
    numbers = re.findall(r'\d+', str(period_name))
    if numbers:
        return int(numbers[0])
    return str(period_name)

# Helper function to validate and clean input DataFrames
def validate_and_clean_df(df):
    """
    Validates and cleans raw data from an Excel file.
    Returns: (cleaned_df, is_valid, error_message)
    """
    # Clean column headers
    df.columns = [str(col).strip() for col in df.columns]
    
    # Flexible column mapping to handle 'Revvenue' typo and casing issues gracefully
    column_mapping = {}
    for col in df.columns:
        col_lower = col.lower()
        if 'product' in col_lower:
            column_mapping[col] = 'Product'
        elif 'unit' in col_lower:
            column_mapping[col] = 'Units Sold'
        elif 'revvenue' in col_lower or 'revenue' in col_lower:
            column_mapping[col] = 'Revenue'
        elif 'region' in col_lower:
            column_mapping[col] = 'Region'
            
    df_renamed = df.rename(columns=column_mapping)
    
    # Check for missing essential columns
    required_cols = ['Product', 'Units Sold', 'Revenue', 'Region']
    missing_cols = [r_col for r_col in required_cols if r_col not in df_renamed.columns]
    
    if missing_cols:
        return None, False, f"Missing essential columns: {', '.join(missing_cols)}"
        
    try:
        # Create structured, typed DataFrame
        df_cleaned = pd.DataFrame()
        df_cleaned['Product'] = df_renamed['Product'].astype(str).str.strip()
        df_cleaned['Units Sold'] = pd.to_numeric(df_renamed['Units Sold'], errors='coerce').fillna(0).astype(int)
        df_cleaned['Revenue'] = pd.to_numeric(df_renamed['Revenue'], errors='coerce').fillna(0.0).astype(float)
        df_cleaned['Region'] = df_renamed['Region'].astype(str).str.strip()
        df_cleaned['Avg Price'] = df_cleaned['Revenue'] / df_cleaned['Units Sold'].replace(0, 1)
        
        # Eliminate empty rows
        df_cleaned = df_cleaned[df_cleaned['Product'] != 'nan']
        
        return df_cleaned, True, ""
    except Exception as e:
        return None, False, f"Type casting failed: {str(e)}"

# Cached data loading to support uploaded file objects
@st.cache_data
def process_data_sources(uploaded_files):
    dfs = []
    validation_reports = []
    
    if uploaded_files:
        # Process uploaded files dynamically
        for file_obj in uploaded_files:
            try:
                # Explicit File Type Validation
                if not file_obj.name.lower().endswith('.xlsx'):
                    validation_reports.append({
                        "file": file_obj.name,
                        "status": "❌ Invalid File Type",
                        "details": "Wrong file type. Only Excel files (.xlsx) are supported."
                    })
                    continue

                # Read the first sheet of the uploaded workbook
                df_raw = pd.read_excel(file_obj, sheet_name=0)
                source_name = file_obj.name.rsplit('.', 1)[0]
                
                cleaned_df, is_valid, err_msg = validate_and_clean_df(df_raw)
                if is_valid:
                    cleaned_df['Period'] = source_name
                    dfs.append(cleaned_df)
                    validation_reports.append({"file": file_obj.name, "status": "✅ Valid", "details": f"Loaded {len(cleaned_df)} rows successfully."})
                else:
                    validation_reports.append({"file": file_obj.name, "status": "❌ Invalid", "details": err_msg})
            except Exception as e:
                validation_reports.append({"file": file_obj.name, "status": "❌ Error", "details": f"Failed to parse Excel file: {str(e)}"})
    else:
        # Default fallback files
        default_files = ["sales_1.xlsx", "sales_2.xlsx", "sales_3.xlsx"]
        for i, file_name in enumerate(default_files, 1):
            if os.path.exists(file_name):
                try:
                    df_raw = pd.read_excel(file_name, sheet_name="Sales Data")
                    source_name = f"Period {i}"
                    cleaned_df, is_valid, _ = validate_and_clean_df(df_raw)
                    if is_valid:
                        cleaned_df['Period'] = source_name
                        dfs.append(cleaned_df)
                except Exception:
                    pass
                    
    combined_df = pd.DataFrame()
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df, validation_reports

# ================= SIDEBAR FILE UPLOADER =================
st.sidebar.markdown(f"<h2 style='color: {COLOR_PRIMARY}; font-weight: 700; margin-top: 15px;'>📥 Data Ingestion</h2>", unsafe_allow_html=True)

# Required format message
st.sidebar.markdown(
    f"""<div style='background-color: {COLOR_STATUS_DEFAULT_BG}; border: 1px solid {COLOR_STATUS_DEFAULT_BORDER}; 
    border-radius: 8px; padding: 10px; margin-bottom: 10px; font-size: 12px; color: {COLOR_STATUS_DEFAULT_TEXT};'>
    <b>📋 Required Format:</b><br>
    Excel file must have these columns:<br>
    • <b>Product</b> — product name<br>
    • <b>Units Sold</b> — quantity sold<br>
    • <b>Revenue</b> — sales amount<br>
    • <b>Region</b> — geographic area
    </div>""",
    unsafe_allow_html=True
)

# Drag-and-drop uploader for multiple Excel files
uploaded_files = st.sidebar.file_uploader(
    "Upload Excel Sales Files (.xlsx):",
    type=["xlsx"],
    accept_multiple_files=True,
    help="Upload one or more Excel spreadsheets. Standard columns: Product, Units sold, Revenue, and Region."
)

# Load and validate files with a loading spinner
with st.spinner("Processing and validating sales data..."):
    df_all, validation_reports = process_data_sources(uploaded_files)

# Show data source status
if uploaded_files:
    valid_count = sum(1 for r in validation_reports if "✅" in r['status'])
    st.sidebar.markdown(
        f"<div class='status-card status-uploaded'><b>✅ Active Dataset</b><br>Using {valid_count} valid uploaded spreadsheet(s).</div>",
        unsafe_allow_html=True
    )
    
    # Validation expander to show dynamic file validation feedback
    with st.sidebar.expander("🔍 File Validation Reports"):
        for report in validation_reports:
            st.markdown(f"**File:** `{report['file']}`")
            st.markdown(f"**Status:** {report['status']}")
            st.markdown(f"**Details:** {report['details']}")
            st.markdown("---")
else:
    st.sidebar.markdown(
        f"<div class='status-card status-default'><b>ℹ️ Demo Mode Active</b><br>Using default local files (sales_1, sales_2, sales_3). Upload your own Excel spreadsheets to explore custom datasets dynamically.</div>",
        unsafe_allow_html=True
    )

# Show prominent error messages in sidebar for incorrect file types or general validation failures
invalid_reports = [r for r in validation_reports if "❌" in r['status']]
if invalid_reports:
    for r in invalid_reports:
        if "Invalid File Type" in r['status']:
            st.sidebar.warning(f"😅 Oops! **{r['file']}** is not an Excel file. Please upload a **.xlsx** file only!")
        elif "Missing essential columns" in r['details']:
            st.sidebar.warning(f"🤔 Hmm! **{r['file']}** doesn't have the right columns. Make sure your file has: **Product, Units Sold, Revenue, Region**. Check the Required Format box above!")
        else:
            st.sidebar.warning(f"❌ Could not read **{r['file']}**. Please make sure it's a valid Excel file and try again!")

# ================= SIDEBAR FILTERS =================
st.sidebar.markdown(f"<h2 style='color: {COLOR_PRIMARY}; font-weight: 700; margin-top: 15px;'>🎛️ Dashboard Controls</h2>", unsafe_allow_html=True)
st.sidebar.markdown("Filter your data dynamically below:")

# Check if data is empty after loading
if df_all.empty:
    st.error("🚨 Critical Error: No data available. Please upload valid Excel sheets containing product sales details.")
    st.stop()

# 1. Period/File Filter
all_periods = sorted(df_all['Period'].unique(), key=get_period_sort_key)
selected_periods = st.sidebar.multiselect(
    "Select Datasets / Periods:",
    options=all_periods,
    default=all_periods,
    help="Select one or more uploaded file sources to aggregate"
)

# 2. Region Filter
all_regions = sorted(df_all['Region'].unique())
selected_regions = st.sidebar.multiselect(
    "Select Regions:",
    options=all_regions,
    default=all_regions,
    help="Filter by geographical regions"
)

# 3. Product Filter
all_products = sorted(df_all['Product'].unique())
selected_products = st.sidebar.multiselect(
    "Select Products:",
    options=all_products,
    default=all_products,
    help="Filter by specific items"
)

# Reset Button
if st.sidebar.button("🔄 Reset Filters", use_container_width=True):
    st.rerun()

# Apply Filters
df_filtered = df_all.copy()
if selected_periods:
    df_filtered = df_filtered[df_filtered['Period'].isin(selected_periods)]
if selected_regions:
    df_filtered = df_filtered[df_filtered['Region'].isin(selected_regions)]
if selected_products:
    df_filtered = df_filtered[df_filtered['Product'].isin(selected_products)]

# Empty State Check
if df_filtered.empty:
    st.warning("⚠️ No data matches your current filter combination. Please expand your filter selections in the sidebar.")
    st.stop()

# ================= MAIN HERO / HEADER =================
st.markdown("<h1>📊 Sales Performance & Revenue Trends</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='font-size: 16px; color: {COLOR_SECONDARY}; margin-bottom: 25px;'>Interactive analytical console presenting insights and financial results dynamically from your uploaded spreadsheets.</p>", unsafe_allow_html=True)

# ================= KPI METRIC CARDS =================
# Calculate KPIs
total_revenue = df_filtered['Revenue'].sum()
total_units = df_filtered['Units Sold'].sum()
avg_unit_price = total_revenue / total_units if total_units > 0 else 0

# Calculate growth for comparison dynamically from the earliest to the latest selected periods
sorted_filtered_periods = sorted(df_filtered['Period'].unique(), key=get_period_sort_key)
if len(sorted_filtered_periods) >= 2:
    first_period = sorted_filtered_periods[0]
    last_period = sorted_filtered_periods[-1]
    
    first_rev = df_filtered[df_filtered['Period'] == first_period]['Revenue'].sum()
    last_rev = df_filtered[df_filtered['Period'] == last_period]['Revenue'].sum()
    
    if first_rev > 0:
        overall_growth_pct = ((last_rev - first_rev) / first_rev) * 100
        delta_label = f"+{overall_growth_pct:.1f}% ({first_period} ➔ {last_period})" if overall_growth_pct >= 0 else f"{overall_growth_pct:.1f}% ({first_period} ➔ {last_period})"
    else:
        delta_label = None
else:
    delta_label = None

# Identify best performers
best_product_row = df_filtered.groupby('Product')['Revenue'].sum().idxmax()
best_product_rev = df_filtered.groupby('Product')['Revenue'].sum().max()
best_region_row = df_filtered.groupby('Region')['Revenue'].sum().idxmax()
best_region_rev = df_filtered.groupby('Region')['Revenue'].sum().max()

# Display KPIs in columns (4 beautifully styled summary cards)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Revenue",
        value=f"${total_revenue:,.2f}",
        delta=delta_label,
        help="Aggregated revenue from selected products, regions, and periods."
    )

with col2:
    st.metric(
        label="Total Units Sold",
        value=f"{total_units:,.0f}",
        help="Aggregated number of units sold across selections."
    )

with col3:
    st.metric(
        label="Average Selling Price (ASP)",
        value=f"${avg_unit_price:,.2f}",
        help="Calculated as Total Revenue divided by Total Units Sold."
    )

with col4:
    st.metric(
        label="Top Performer (Product)",
        value=best_product_row,
        delta=f"${best_product_rev:,.0f} Total",
        delta_color="normal",
        help="The product generating the highest total revenue in the filtered dataset."
    )


# ================= VISUALIZATIONS SECTION =================
st.markdown(f"<hr style='margin: 30px 0; border-color: {COLOR_BORDER};'>", unsafe_allow_html=True)

# ROW 1: Trend Line (Dual-Axis) & Region Donut
chart_col1, chart_col2 = st.columns([3, 2])

with chart_col1:
    st.markdown("### 📈 Revenue & Volume Growth Trend")
    # Aggregate by period
    trend_data = df_filtered.groupby('Period').agg({
        'Revenue': 'sum',
        'Units Sold': 'sum'
    }).reset_index()
    
    # Sort chronologically using our numeric sorting key helper
    trend_data['sort_key'] = trend_data['Period'].apply(get_period_sort_key)
    if trend_data['sort_key'].apply(lambda x: isinstance(x, int)).all():
        trend_data = trend_data.sort_values('sort_key')
    else:
        trend_data['sort_key_str'] = trend_data['sort_key'].astype(str)
        trend_data = trend_data.sort_values('sort_key_str')
        if 'sort_key_str' in trend_data.columns:
            trend_data = trend_data.drop(columns='sort_key_str')
    trend_data = trend_data.drop(columns='sort_key')
    
    if len(trend_data) > 1:
        # Create professional dual-axis chart matching standard reports
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Primary axis: Revenue (Solid line)
        fig_trend.add_trace(
            go.Scatter(
                x=trend_data['Period'],
                y=trend_data['Revenue'],
                name="Revenue ($)",
                line=dict(color=COLOR_PRIMARY, width=3),
                marker=dict(symbol="circle", size=8, color=COLOR_PRIMARY),
                hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>"
            ),
            secondary_y=False
        )
        
        # Secondary axis: Units Sold (Dashed line)
        fig_trend.add_trace(
            go.Scatter(
                x=trend_data['Period'],
                y=trend_data['Units Sold'],
                name="Units Sold",
                line=dict(color=COLOR_ACCENT, width=2.5, dash="dash"),
                marker=dict(symbol="square", size=8, color=COLOR_ACCENT),
                hovertemplate="<b>%{x}</b><br>Units Sold: %{y:,.0f}<extra></extra>"
            ),
            secondary_y=True
        )
        
        # Style layout
        fig_trend.update_layout(
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.05,
                xanchor="left",
                x=0.01,
                bgcolor="rgba(248, 250, 252, 0.8)" if not st.session_state.dark_mode else "rgba(15, 23, 42, 0.8)",
                bordercolor=COLOR_BORDER,
                borderwidth=1,
                font=dict(color=PLOTLY_TEXT_COLOR)
            ),
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=320,
            font=dict(color=PLOTLY_TEXT_COLOR)
        )
        
        fig_trend.update_xaxes(showgrid=False, linecolor=COLOR_BORDER, tickfont=dict(color=PLOTLY_TEXT_COLOR))
        fig_trend.update_yaxes(
            title_text="<b>Revenue ($)</b>",
            title_font=dict(size=11, color=COLOR_PRIMARY),
            gridcolor=PLOTLY_GRID_COLOR,
            tickformat="$~s",
            secondary_y=False,
            linecolor=COLOR_BORDER,
            tickfont=dict(color=PLOTLY_TEXT_COLOR)
        )
        fig_trend.update_yaxes(
            title_text="<b>Units Sold</b>",
            title_font=dict(size=11, color=COLOR_ACCENT),
            secondary_y=True,
            showgrid=False,
            linecolor=COLOR_BORDER,
            tickfont=dict(color=PLOTLY_TEXT_COLOR)
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        # Single period selected - display bar instead
        fig_single = px.bar(
            trend_data,
            x='Period',
            y='Revenue',
            text_auto='$,.2f',
            title="Selected Dataset Revenue",
            color_discrete_sequence=[COLOR_PRIMARY]
        )
        fig_single.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            height=320,
            margin=dict(l=20, r=20, t=40, b=20),
            font=dict(color=PLOTLY_TEXT_COLOR),
            xaxis=dict(linecolor=COLOR_BORDER, tickfont=dict(color=PLOTLY_TEXT_COLOR)),
            yaxis=dict(linecolor=COLOR_BORDER, gridcolor=PLOTLY_GRID_COLOR, tickformat="$~s", tickfont=dict(color=PLOTLY_TEXT_COLOR))
        )
        st.plotly_chart(fig_single, use_container_width=True)

with chart_col2:
    st.markdown("### 🗺️ Regional Contribution")
    region_data = df_filtered.groupby('Region')['Revenue'].sum().reset_index()
    
    fig_donut = px.pie(
        region_data,
        names='Region',
        values='Revenue',
        hole=0.45,
        color_discrete_sequence=CHART_PALETTE
    )
    
    fig_donut.update_layout(
        margin=dict(l=10, r=10, t=30, b=60),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(color=PLOTLY_TEXT_COLOR, size=11),
            itemwidth=80
        ),
        height=340,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=PLOTLY_TEXT_COLOR)
    )
    fig_donut.update_traces(
        textinfo="label+percent",
        textposition="inside",
        hoverinfo="label+value+percent",
        marker=dict(line=dict(color='white' if not st.session_state.dark_mode else COLOR_LIGHT, width=2))
    )
    
    st.plotly_chart(fig_donut, use_container_width=True)


# ROW 2: Product Breakdown Grouped Bar & Performance Table
chart_col3, chart_col4 = st.columns([3, 2])

with chart_col3:
    st.markdown("### 📦 Product Revenue Trend across Periods")
    # Group by Product and Period
    prod_period_data = df_filtered.groupby(['Product', 'Period'])['Revenue'].sum().reset_index()
    
    # Sort periods chronologically
    prod_period_data['sort_key'] = prod_period_data['Period'].apply(get_period_sort_key)
    if prod_period_data['sort_key'].apply(lambda x: isinstance(x, int)).all():
        prod_period_data = prod_period_data.sort_values(['Product', 'sort_key'])
    else:
        prod_period_data['sort_key_str'] = prod_period_data['sort_key'].astype(str)
        prod_period_data = prod_period_data.sort_values(['Product', 'sort_key_str'])
        if 'sort_key_str' in prod_period_data.columns:
            prod_period_data = prod_period_data.drop(columns='sort_key_str')
    prod_period_data = prod_period_data.drop(columns='sort_key')
    
    fig_prod_bar = px.bar(
        prod_period_data,
        x="Product",
        y="Revenue",
        color="Period",
        barmode="group",
        color_discrete_sequence=CHART_PALETTE
    )
    
    fig_prod_bar.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=350,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color=PLOTLY_TEXT_COLOR)),
        xaxis_title=None,
        yaxis_title="Revenue ($)",
        yaxis=dict(gridcolor=PLOTLY_GRID_COLOR, tickformat="$~s", linecolor=COLOR_BORDER, tickfont=dict(color=PLOTLY_TEXT_COLOR), title_font=dict(color=PLOTLY_TEXT_COLOR)),
        xaxis=dict(linecolor=COLOR_BORDER, tickfont=dict(color=PLOTLY_TEXT_COLOR)),
        font=dict(color=PLOTLY_TEXT_COLOR)
    )
    st.plotly_chart(fig_prod_bar, use_container_width=True)

with chart_col4:
    st.markdown("### 🎯 Performance Matrix")
    # Bubble/Scatter plot of units sold vs revenue by region/product
    scatter_data = df_filtered.groupby(['Product', 'Region']).agg({
        'Revenue': 'sum',
        'Units Sold': 'sum',
        'Avg Price': 'mean'
    }).reset_index()
    
    fig_scatter = px.scatter(
        scatter_data,
        x="Units Sold",
        y="Revenue",
        size="Avg Price",
        color="Region",
        hover_name="Product",
        color_discrete_sequence=CHART_PALETTE,
        size_max=30
    )
    
    fig_scatter.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=350,
        margin=dict(l=20, r=20, t=30, b=60),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(color=PLOTLY_TEXT_COLOR, size=11),
            title=None
        ),
        xaxis=dict(gridcolor=PLOTLY_GRID_COLOR, title="Units Sold", linecolor=COLOR_BORDER, tickfont=dict(color=PLOTLY_TEXT_COLOR), title_font=dict(color=PLOTLY_TEXT_COLOR)),
        yaxis=dict(gridcolor=PLOTLY_GRID_COLOR, title="Revenue ($)", tickformat="$~s", linecolor=COLOR_BORDER, tickfont=dict(color=PLOTLY_TEXT_COLOR), title_font=dict(color=PLOTLY_TEXT_COLOR)),
        font=dict(color=PLOTLY_TEXT_COLOR)
    )
    
    st.plotly_chart(fig_scatter, use_container_width=True)


# ================= ANALYTICAL PERFORMANCE TABLE =================
st.markdown(f"<hr style='margin: 30px 0; border-color: {COLOR_BORDER};'>", unsafe_allow_html=True)
st.markdown("### 📊 Consolidated Product Performance Summary")

# Group and calculate aggregated analytics
product_summary = df_filtered.groupby('Product').agg(
    total_units=('Units Sold', 'sum'),
    total_rev=('Revenue', 'sum')
).reset_index()

product_summary['Average Price per Unit'] = product_summary['total_rev'] / product_summary['total_units'].replace(0, 1)
total_filtered_rev = product_summary['total_rev'].sum()
product_summary['Revenue Contribution (%)'] = (product_summary['total_rev'] / total_filtered_rev) * 100

# Rename columns for presentation
product_summary.rename(columns={
    'Product': 'Product Name',
    'total_units': 'Units Sold',
    'total_rev': 'Total Revenue ($)'
}, inplace=True)

# Sort by Revenue descending
product_summary = product_summary.sort_values('Total Revenue ($)', ascending=False).reset_index(drop=True)

# Display styled DataFrame with numeric formatting
st.dataframe(
    product_summary.style.format({
        'Units Sold': '{:,.0f}',
        'Total Revenue ($)': '${:,.2f}',
        'Average Price per Unit': '${:,.2f}',
        'Revenue Contribution (%)': '{:.2f}%'
    }).background_gradient(subset=['Total Revenue ($)'], cmap='YlGnBu' if not st.session_state.dark_mode else 'Blues'),
    use_container_width=True,
    hide_index=True
)


# ================= DOWNLOAD REPORT BUTTON =================
st.markdown(f"<hr style='margin: 30px 0; border-color: {COLOR_BORDER};'>", unsafe_allow_html=True)
st.markdown("### 📥 Download Your Report")
col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    csv_full = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📊 Download Full Data as CSV",
        data=csv_full,
        file_name="sales_report.csv",
        mime="text/csv",
        use_container_width=True
    )
with col_dl2:
    summary_csv = product_summary.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📈 Download Product Summary as CSV",
        data=summary_csv,
        file_name="product_summary.csv",
        mime="text/csv",
        use_container_width=True
    )

# ================= DATA EXPLORER & EXPORT =================
st.markdown(f"<hr style='margin: 30px 0; border-color: {COLOR_BORDER};'>", unsafe_allow_html=True)
with st.expander("🔍 Filtered Raw Data Explorer & Export Tool"):
    st.markdown("Use this section to search the filtered datasets and export the raw tables to a CSV file.")
    
    # Search bar
    search_query = st.text_input("🔍 Quick Search (Product or Region name):", placeholder="e.g. EcoWidget, West...")
    
    df_search = df_filtered.copy()
    if search_query:
        df_search = df_search[
            df_search['Product'].str.contains(search_query, case=False, na=False) |
            df_search['Region'].str.contains(search_query, case=False, na=False)
        ]
        
    st.dataframe(df_search, use_container_width=True, hide_index=True)
    
    # Download Button
    csv = df_search.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_sales_data.csv",
        mime="text/csv",
        use_container_width=True
    )

# Footer credits
st.markdown(
    f"<p style='text-align: center; color: {COLOR_SECONDARY}; font-size: 12px; margin-top: 50px;'>Sales Analysis System v2.2 • Powered by Streamlit & Plotly</p>",
    unsafe_allow_html=True
)
