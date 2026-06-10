import streamlit as st

from src.config import APP_BG, APP_BG_2, TEXT_LIGHT, TEXT_MUTED, NEON, CYAN


def apply_styles():
    """Apply the dashboard CSS design."""
    st.markdown(
        f"""
<style>
    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background:
            radial-gradient(circle at top left, rgba(34, 211, 238, 0.14), transparent 34%),
            radial-gradient(circle at top right, rgba(183, 255, 60, 0.08), transparent 30%),
            linear-gradient(180deg, {APP_BG} 0%, {APP_BG_2} 100%) !important;
        color: {TEXT_LIGHT} !important;
    }}

    [data-testid="stHeader"] {{
        background: transparent !important;
    }}

    .block-container {{
        padding-top: 3rem !important;
        padding-bottom: 2rem !important;
        max-width: 94%;
    }}

    section[data-testid="stSidebar"] {{
        background:
            radial-gradient(circle at top, rgba(183, 255, 60, 0.10), transparent 22%),
            linear-gradient(180deg, #030A16 0%, #071426 100%) !important;
        border-right: 1px solid rgba(183, 255, 60, 0.12);
        padding-top: 0.8rem;
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {{
        color: #EAF2FF !important;
    }}

    .sidebar-hero {{
        display: flex;
        align-items: center;
        gap: 12px;
        background: linear-gradient(135deg, rgba(15, 27, 45, 0.98) 0%, rgba(6, 17, 31, 0.98) 100%);
        border: 1px solid rgba(183, 255, 60, 0.28);
        border-radius: 18px;
        padding: 16px 14px;
        margin-bottom: 20px;
        box-shadow: 0 16px 36px rgba(0,0,0,0.30);
    }}

    .sidebar-hero-icon {{
        width: 46px;
        height: 46px;
        min-width: 46px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 14px;
        background: linear-gradient(135deg, {NEON} 0%, {CYAN} 100%);
        font-size: 24px;
        box-shadow: 0 0 22px rgba(183, 255, 60, 0.28);
    }}

    .sidebar-hero-title {{
        color: {NEON};
        font-size: 20px;
        font-weight: 900;
        line-height: 1.2;
        margin-bottom: 4px;
    }}

    .sidebar-hero-subtitle {{
        color: #BFD4EA;
        font-size: 12px;
        line-height: 1.4;
    }}

    section[data-testid="stSidebar"] div[data-testid="stExpander"] {{
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        margin-bottom: 14px !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stExpander"] summary {{
        background: linear-gradient(90deg, #0B1728 0%, #101E33 100%) !important;
        color: #F8FAFC !important;
        border-radius: 16px !important;
        padding: 12px 14px !important;
        border: 1px solid rgba(183, 255, 60, 0.16) !important;
        font-weight: 800 !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.20);
        transition: all 0.2s ease;
    }}

    section[data-testid="stSidebar"] div[data-testid="stExpander"] summary:hover {{
        transform: translateY(-1px);
        border-color: {NEON} !important;
        box-shadow: 0 0 18px rgba(183,255,60,0.14);
    }}

    section[data-testid="stSidebar"] div[data-testid="stExpander"] summary * {{
        color: #F8FAFC !important;
    }}

    section[data-testid="stSidebar"] label {{
        font-size: 13px !important;
        font-weight: 800 !important;
        color: #EAF2FF !important;
        margin-bottom: 6px !important;
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
        background: linear-gradient(180deg, #071426 0%, #0B1728 100%) !important;
        border: 1px solid rgba(56, 189, 248, 0.28) !important;
        border-radius: 14px !important;
        min-height: 48px !important;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02), 0 8px 20px rgba(0,0,0,0.16);
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover {{
        border-color: {NEON} !important;
        box-shadow: 0 0 0 3px rgba(183,255,60,0.10);
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] span,
    section[data-testid="stSidebar"] div[data-baseweb="select"] div {{
        color: #EAF2FF !important;
        font-weight: 800 !important;
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] svg {{
        fill: {NEON} !important;
        color: {NEON} !important;
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] input {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        color: #EAF2FF !important;
        font-weight: 800 !important;
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] input::placeholder {{
        color: #BFD4EA !important;
        opacity: 1 !important;
        font-weight: 700 !important;
    }}

    section[data-testid="stSidebar"] [data-baseweb="tag"] {{
        background: linear-gradient(135deg, #0F2742 0%, #123B5A 100%) !important;
        border: 1px solid rgba(56, 189, 248, 0.45) !important;
        border-radius: 999px !important;
        color: #EAF2FF !important;
        font-weight: 800 !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.12);
    }}

    section[data-testid="stSidebar"] [data-baseweb="tag"] span {{
        color: #EAF2FF !important;
        font-weight: 800 !important;
    }}

    section[data-testid="stSidebar"] [data-baseweb="tag"] svg {{
        fill: #38BDF8 !important;
        color: #38BDF8 !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stTextInput"] input {{
        background: linear-gradient(180deg, #071426 0%, #0B1728 100%) !important;
        color: #EAF2FF !important;
        border: 1px solid rgba(56, 189, 248, 0.18) !important;
        border-radius: 14px !important;
        min-height: 44px !important;
        font-weight: 800 !important;
        box-shadow: 0 8px 20px rgba(0,0,0,0.16) !important;
        padding-left: 12px !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stTextInput"] input::placeholder {{
        color: #BFD4EA !important;
        opacity: 1 !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stSlider"] span {{
        color: #EAF2FF !important;
        font-weight: 800 !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stSlider"] div[role="slider"] {{
        background: linear-gradient(135deg, {NEON} 0%, #7DD321 100%) !important;
        border: 3px solid #F8FAFC !important;
        box-shadow: 0 0 0 4px rgba(183,255,60,0.18), 0 0 18px rgba(183,255,60,0.20);
    }}

    .dashboard-hero {{
        background:
            radial-gradient(circle at top left, rgba(183,255,60,0.10), transparent 28%),
            radial-gradient(circle at top right, rgba(56,189,248,0.12), transparent 30%),
            linear-gradient(135deg, rgba(11,23,40,0.96) 0%, rgba(6,17,31,0.96) 100%);
        border: 1px solid rgba(183, 255, 60, 0.18);
        border-radius: 24px;
        padding: 34px 26px 30px 26px;
        margin-top: 0.5rem;
        margin-bottom: 1.8rem;
        text-align: center;
        box-shadow: 0 18px 46px rgba(0,0,0,0.28);
    }}

    .dashboard-badge {{
        display: inline-block;
        color: {NEON};
        background: rgba(183,255,60,0.08);
        border: 1px solid rgba(183,255,60,0.22);
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 800;
        margin-bottom: 14px;
    }}

    .dashboard-title {{
        font-size: 2.5rem;
        font-weight: 900;
        color: {TEXT_LIGHT};
        line-height: 1.12;
        margin: 0 0 10px 0;
        letter-spacing: 0.3px;
        text-align: center;
    }}

    .dashboard-title span {{
        color: {NEON};
    }}

    .dashboard-subtitle {{
        font-size: 1rem;
        color: #BFD4EA;
        margin: 0;
        text-align: center;
    }}

    .kpi-card {{
        background: linear-gradient(180deg, rgba(15, 27, 45, 0.98) 0%, rgba(11, 23, 40, 0.98) 100%);
        border: 1px solid rgba(183, 255, 60, 0.16);
        border-left: 6px solid {NEON};
        padding: 20px 22px;
        min-height: 112px;
        border-radius: 18px;
        box-shadow: 0 14px 32px rgba(0,0,0,0.25);
        text-align: center;
    }}

    .kpi-label {{
        font-size: 13px;
        color: #BFD4EA;
        margin-bottom: 10px;
        font-weight: 800;
    }}

    .kpi-value {{
        font-size: 34px;
        line-height: 1;
        font-weight: 900;
        color: #F8FAFC;
    }}

    .kpi-change {{
        font-size: 12px;
        color: {NEON};
        margin-top: 10px;
        font-weight: 800;
    }}

    h1, h2, h3 {{
        color: {TEXT_LIGHT} !important;
        font-weight: 800;
        text-align: center;
    }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid rgba(56, 189, 248, 0.14);
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 10px 28px rgba(0,0,0,0.18);
        margin-left: auto;
        margin-right: auto;
    }}

    [data-testid="column"] {{
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }}

    div[role="radiogroup"] {{
        justify-content: center;
        gap: 14px;
        margin-top: 22px;
        margin-bottom: 24px;
    }}

    div[role="radiogroup"] label {{
        background: linear-gradient(180deg, #0B1728 0%, #071426 100%);
        border: 1px solid rgba(183,255,60,0.16);
        padding: 9px 18px;
        border-radius: 999px;
        color: #F8FAFC !important;
        transition: all 0.2s ease;
    }}

    div[role="radiogroup"] label:hover {{
        border-color: {NEON};
        box-shadow: 0 0 16px rgba(183,255,60,0.12);
        transform: translateY(-1px);
    }}

    div[role="radiogroup"] label * {{
        color: #F8FAFC !important;
        font-weight: 800 !important;
    }}

    /* =========================
       Main page readability fixes
       ========================= */

    div[data-testid="stSelectbox"] label,
    div[data-testid="stSlider"] label,
    div[data-testid="stCheckbox"] label,
    div[data-testid="stMultiSelect"] label,
    div[data-testid="stTextInput"] label {{
        color: #EAF2FF !important;
        font-weight: 800 !important;
    }}

    div[data-testid="stMarkdownContainer"] p {{
        color: #D4E2F5 !important;
        font-weight: 600 !important;
    }}

    div[data-testid="stCheckbox"] p {{
        color: #D4E2F5 !important;
        font-weight: 700 !important;
    }}

    div[data-testid="stSlider"] span {{
        color: #EAF2FF !important;
        font-weight: 800 !important;
    }}

    div[data-testid="stSelectbox"] div[data-baseweb="select"] span {{
        color: #071426 !important;
        font-weight: 800 !important;
    }}

    .stMarkdown,
    .stText {{
        color: #D4E2F5 !important;
    }}
</style>
""",
        unsafe_allow_html=True
    )