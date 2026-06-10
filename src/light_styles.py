import streamlit as st

from src.light_config import APP_BG, APP_BG_2, TEXT_LIGHT, TEXT_MUTED, NEON, CYAN, BLUE


def apply_light_styles():
    """Apply the standalone light dashboard CSS design."""
    st.markdown(
        f"""
<style>
    /* =========================
       Global app background
       ========================= */
    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background:
            radial-gradient(circle at top left, rgba(37, 99, 235, 0.10), transparent 30%),
            radial-gradient(circle at top right, rgba(92, 184, 92, 0.10), transparent 28%),
            linear-gradient(180deg, #F8FAFF 0%, #EEF4FF 100%) !important;
        color: {TEXT_LIGHT} !important;
    }}

    [data-testid="stHeader"] {{
        background: transparent !important;
    }}

    .block-container {{
        padding-top: 2.7rem !important;
        padding-bottom: 2rem !important;
        max-width: 95%;
    }}

    /* =========================
       Sidebar
       ========================= */
    section[data-testid="stSidebar"] {{
        background:
            radial-gradient(circle at top, rgba(37, 99, 235, 0.08), transparent 24%),
            linear-gradient(180deg, #FFFFFF 0%, #F5F9FF 100%) !important;
        border-right: 1px solid rgba(37, 99, 235, 0.10);
        padding-top: 0.8rem;
        box-shadow: 10px 0 35px rgba(15, 23, 42, 0.05);
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {{
        color: {TEXT_LIGHT} !important;
    }}

    .sidebar-hero {{
        display: flex;
        align-items: center;
        gap: 12px;
        background: linear-gradient(135deg, #FFFFFF 0%, #EAF2FF 100%);
        border: 1px solid rgba(37, 99, 235, 0.14);
        border-radius: 22px;
        padding: 16px 14px;
        margin-bottom: 20px;
        box-shadow: 0 16px 34px rgba(37, 99, 235, 0.08);
    }}

    .sidebar-hero-icon {{
        width: 46px;
        height: 46px;
        min-width: 46px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 16px;
        background: linear-gradient(135deg, {BLUE} 0%, {CYAN} 100%);
        font-size: 24px;
        box-shadow: 0 10px 24px rgba(37, 99, 235, 0.18);
    }}

    .sidebar-hero-title {{
        color: {BLUE};
        font-size: 22px;
        font-weight: 900;
        line-height: 1.2;
        margin-bottom: 4px;
    }}

    .sidebar-hero-subtitle {{
        color: {TEXT_MUTED};
        font-size: 14px;
        line-height: 1.4;
        font-weight: 550;
    }}

    section[data-testid="stSidebar"] div[data-testid="stExpander"] {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        margin-bottom: 14px !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stExpander"] summary {{
        background: linear-gradient(90deg, #FFFFFF 0%, #F4F8FF 100%) !important;
        color: {TEXT_LIGHT} !important;
        border-radius: 16px !important;
        padding: 13px 14px !important;
        border: 1px solid rgba(37, 99, 235, 0.14) !important;
        font-weight: 850 !important;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
        transition: all 0.2s ease;
    }}

    section[data-testid="stSidebar"] div[data-testid="stExpander"] summary:hover {{
        transform: translateY(-1px);
        border-color: {BLUE} !important;
        box-shadow: 0 12px 26px rgba(37, 99, 235, 0.10);
    }}

    section[data-testid="stSidebar"] div[data-testid="stExpander"] summary * {{
        color: {TEXT_LIGHT} !important;
        font-size: 16px !important;
        font-weight: 850 !important;
    }}

    section[data-testid="stSidebar"] label {{
        font-size: 15px !important;
        font-weight: 800 !important;
        color: #3D5875 !important;
        margin-bottom: 6px !important;
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
        background: #FFFFFF !important;
        border: 1px solid rgba(37, 99, 235, 0.18) !important;
        border-radius: 14px !important;
        min-height: 48px !important;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover {{
        border-color: {BLUE} !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.08);
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] span,
    section[data-testid="stSidebar"] div[data-baseweb="select"] div {{
        color: {TEXT_LIGHT} !important;
        font-size: 15px !important;
        font-weight: 750 !important;
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] svg {{
        fill: {BLUE} !important;
        color: {BLUE} !important;
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] input {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        color: {TEXT_LIGHT} !important;
        font-size: 15px !important;
        font-weight: 750 !important;
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] input::placeholder {{
        color: #7D92AA !important;
        opacity: 1 !important;
        font-weight: 650 !important;
    }}

    section[data-testid="stSidebar"] [data-baseweb="tag"] {{
        background: linear-gradient(135deg, #DBEAFE 0%, #DDF8F2 100%) !important;
        border: 1px solid rgba(37, 99, 235, 0.18) !important;
        border-radius: 999px !important;
        color: {TEXT_LIGHT} !important;
        font-weight: 850 !important;
    }}

    section[data-testid="stSidebar"] [data-baseweb="tag"] span {{
        color: {TEXT_LIGHT} !important;
        font-size: 14px !important;
        font-weight: 850 !important;
    }}

    section[data-testid="stSidebar"] [data-baseweb="tag"] svg {{
        fill: {BLUE} !important;
        color: {BLUE} !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stTextInput"] input {{
        background: #FFFFFF !important;
        color: {TEXT_LIGHT} !important;
        border: 1px solid rgba(37, 99, 235, 0.18) !important;
        border-radius: 14px !important;
        min-height: 44px !important;
        font-size: 15px !important;
        font-weight: 750 !important;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05) !important;
        padding-left: 12px !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stTextInput"] input::placeholder {{
        color: #7D92AA !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stSlider"] span {{
        color: {TEXT_LIGHT} !important;
        font-size: 15px !important;
        font-weight: 750 !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stSlider"] div[role="slider"] {{
        background: linear-gradient(135deg, {BLUE} 0%, {CYAN} 100%) !important;
        border: 3px solid #FFFFFF !important;
        box-shadow: 0 0 0 4px rgba(37,99,235,0.14), 0 8px 18px rgba(37,99,235,0.16);
    }}

    /* =========================
       Hero section
       ========================= */
    .dashboard-hero {{
        background:
            radial-gradient(circle at top left, rgba(37,99,235,0.08), transparent 28%),
            radial-gradient(circle at top right, rgba(92,184,92,0.10), transparent 30%),
            linear-gradient(135deg, #FFFFFF 0%, #F6FAFF 100%);
        border: 1px solid rgba(37, 99, 235, 0.10);
        border-radius: 28px;
        padding: 34px 26px 30px 26px;
        margin-top: 0.5rem;
        margin-bottom: 1.6rem;
        text-align: center;
        box-shadow: 0 18px 40px rgba(37, 99, 235, 0.08);
    }}

    .dashboard-badge {{
        display: inline-block;
        color: {BLUE};
        background: rgba(37,99,235,0.08);
        border: 1px solid rgba(37,99,235,0.16);
        padding: 7px 13px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 850;
        margin-bottom: 14px;
    }}

    .dashboard-title {{
        font-size: 2.65rem;
        font-weight: 900;
        color: {TEXT_LIGHT};
        line-height: 1.12;
        margin: 0 0 10px 0;
        letter-spacing: 0.2px;
        text-align: center;
    }}

    .dashboard-title span {{
        color: {NEON};
    }}

    .dashboard-subtitle {{
        font-size: 1.1rem;
        color: #5F738E;
        margin: 0;
        text-align: center;
        font-weight: 600;
        line-height: 1.55;
    }}

    /* =========================
       KPI cards
       ========================= */
    .kpi-card {{
        background: linear-gradient(180deg, #FFFFFF 0%, #F9FBFF 100%);
        border: 1px solid rgba(37, 99, 235, 0.10);
        border-left: 6px solid {BLUE};
        padding: 20px 22px;
        min-height: 112px;
        border-radius: 20px;
        box-shadow: 0 14px 30px rgba(15, 23, 42, 0.06);
        text-align: center;
    }}

    .kpi-label {{
        font-size: 14px;
        color: #5B7190;
        margin-bottom: 10px;
        font-weight: 850;
    }}

    .kpi-value {{
        font-size: 36px;
        line-height: 1;
        font-weight: 900;
        color: {TEXT_LIGHT};
    }}

    .kpi-change {{
        font-size: 13px;
        color: {NEON};
        margin-top: 10px;
        font-weight: 850;
    }}

    /* =========================
       Headings and text
       ========================= */
    h1 {{
        color: {TEXT_LIGHT} !important;
        font-size: 2.4rem !important;
        font-weight: 900 !important;
        text-align: center;
    }}

    h2 {{
        color: {TEXT_LIGHT} !important;
        font-size: 2rem !important;
        font-weight: 850 !important;
        text-align: center;
    }}

    h3 {{
        color: {TEXT_LIGHT} !important;
        font-size: 1.75rem !important;
        font-weight: 850 !important;
        text-align: center;
    }}

    p, li, span {{
        color: {TEXT_LIGHT};
    }}

    .stMarkdown p,
    div[data-testid="stMarkdownContainer"] p {{
        color: #415A76 !important;
        font-size: 18px !important;
        line-height: 1.65 !important;
        font-weight: 550 !important;
    }}

    div[data-testid="stCaptionContainer"],
    .stCaption {{
        color: #5D7490 !important;
        font-size: 16px !important;
        line-height: 1.55 !important;
        font-weight: 550 !important;
    }}

    /* =========================
       Main page input readability
       ========================= */
    div[data-testid="stSelectbox"] label,
    div[data-testid="stSlider"] label,
    div[data-testid="stCheckbox"] label,
    div[data-testid="stMultiSelect"] label,
    div[data-testid="stTextInput"] label {{
        color: {TEXT_LIGHT} !important;
        font-size: 19px !important;
        font-weight: 850 !important;
    }}

    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {{
        background: #FFFFFF !important;
        border: 1px solid rgba(37, 99, 235, 0.16) !important;
        border-radius: 14px !important;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
    }}

    div[data-testid="stSelectbox"] div[data-baseweb="select"] span,
    div[data-testid="stMultiSelect"] div[data-baseweb="select"] span {{
        color: {TEXT_LIGHT} !important;
        font-size: 17px !important;
        font-weight: 750 !important;
    }}

    div[data-testid="stSlider"] span {{
        color: #405873 !important;
        font-size: 17px !important;
        font-weight: 750 !important;
    }}

    div[data-testid="stCheckbox"] p {{
        color: #415A76 !important;
        font-size: 17px !important;
        font-weight: 650 !important;
    }}

    /* =========================
       Info / warning / success boxes
       ========================= */
    div[data-testid="stAlert"] {{
        border-radius: 16px !important;
        border: 1px solid rgba(37, 99, 235, 0.10) !important;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
    }}

    div[data-testid="stAlert"] p {{
        font-size: 18px !important;
        line-height: 1.6 !important;
        font-weight: 650 !important;
    }}

    /* =========================
       Metrics
       ========================= */
    div[data-testid="stMetric"] {{
        background: linear-gradient(180deg, #FFFFFF 0%, #F8FBFF 100%);
        border: 1px solid rgba(37, 99, 235, 0.10);
        border-radius: 18px;
        padding: 14px 16px;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
    }}

    div[data-testid="stMetric"] label {{
        color: #60758F !important;
        font-size: 16px !important;
        font-weight: 750 !important;
    }}

    div[data-testid="stMetricValue"] {{
        color: {TEXT_LIGHT} !important;
        font-size: 2rem !important;
        font-weight: 900 !important;
    }}

    /* =========================
       DataFrame
       ========================= */
    div[data-testid="stDataFrame"] {{
        border: 1px solid rgba(37, 99, 235, 0.10);
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
        margin-left: auto;
        margin-right: auto;
        background: #FFFFFF;
    }}

    div[data-testid="stDataFrame"] * {{
        font-size: 15px !important;
    }}

    /* =========================
       Tabs
       ========================= */
    button[role="tab"] {{
        background: #FFFFFF !important;
        border: 1px solid rgba(37, 99, 235, 0.12) !important;
        border-radius: 12px 12px 0 0 !important;
        color: #506884 !important;
        font-size: 17px !important;
        font-weight: 850 !important;
        padding: 12px 18px !important;
        margin-right: 6px !important;
        transition: all 0.2s ease !important;
    }}

    button[role="tab"]:hover {{
        color: {BLUE} !important;
        background: #F7FAFF !important;
    }}

    button[role="tab"][aria-selected="true"] {{
        color: {BLUE} !important;
        background: #FFFFFF !important;
        border-bottom: 2px solid {BLUE} !important;
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.06);
    }}

    /* =========================
       Radio navigation pills
       ========================= */
    [data-testid="column"] {{
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }}

    div[role="radiogroup"] {{
        justify-content: center;
        gap: 12px;
        margin-top: 20px;
        margin-bottom: 24px;
        flex-wrap: wrap;
    }}

    div[role="radiogroup"] label {{
        background: #FFFFFF;
        border: 1px solid rgba(37,99,235,0.14);
        padding: 10px 19px;
        border-radius: 999px;
        color: {TEXT_LIGHT} !important;
        transition: all 0.2s ease;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
    }}

    div[role="radiogroup"] label:hover {{
        border-color: {BLUE};
        box-shadow: 0 12px 26px rgba(37,99,235,0.10);
        transform: translateY(-1px);
    }}

    div[role="radiogroup"] label * {{
        color: {TEXT_LIGHT} !important;
        font-size: 16px !important;
        font-weight: 750 !important;
    }}

    div[role="radiogroup"] label:has(input:checked) {{
        background: linear-gradient(135deg, #FFFFFF 0%, #EEF5FF 100%) !important;
        border: 1px solid rgba(37,99,235,0.32) !important;
        box-shadow: 0 12px 26px rgba(37,99,235,0.12) !important;
    }}

    /* =========================
       Horizontal rule
       ========================= */
    hr {{
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(37,99,235,0.16), transparent);
        margin: 1.2rem 0;
    }}
</style>
""",
        unsafe_allow_html=True
    )