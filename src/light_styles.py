import streamlit as st

from src.light_config import APP_BG, APP_BG_2, TEXT_LIGHT, TEXT_MUTED, NEON, CYAN, BLUE


def apply_light_styles():
    """Apply the standalone light dashboard CSS design."""
    st.markdown(
        f"""
<style>
    html, body, [data-testid="stAppViewContainer"], .stApp {{
        background:
            radial-gradient(circle at top left, rgba(37, 99, 235, 0.12), transparent 30%),
            radial-gradient(circle at top right, rgba(92, 184, 92, 0.13), transparent 28%),
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
            radial-gradient(circle at top, rgba(37, 99, 235, 0.12), transparent 24%),
            linear-gradient(180deg, #FFFFFF 0%, #F1F7FF 100%) !important;
        border-right: 1px solid rgba(37, 99, 235, 0.12);
        padding-top: 0.8rem;
        box-shadow: 10px 0 35px rgba(15, 23, 42, 0.06);
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
        border: 1px solid rgba(37, 99, 235, 0.16);
        border-radius: 22px;
        padding: 16px 14px;
        margin-bottom: 20px;
        box-shadow: 0 18px 36px rgba(37, 99, 235, 0.10);
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
        box-shadow: 0 10px 24px rgba(37, 99, 235, 0.24);
    }}

    .sidebar-hero-title {{
        color: {BLUE};
        font-size: 20px;
        font-weight: 900;
        line-height: 1.2;
        margin-bottom: 4px;
    }}

    .sidebar-hero-subtitle {{
        color: {TEXT_MUTED};
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
        background: linear-gradient(90deg, #FFFFFF 0%, #F1F7FF 100%) !important;
        color: {TEXT_LIGHT} !important;
        border-radius: 16px !important;
        padding: 12px 14px !important;
        border: 1px solid rgba(37, 99, 235, 0.16) !important;
        font-weight: 800 !important;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
        transition: all 0.2s ease;
    }}

    section[data-testid="stSidebar"] div[data-testid="stExpander"] summary:hover {{
        transform: translateY(-1px);
        border-color: {BLUE} !important;
        box-shadow: 0 10px 24px rgba(37, 99, 235, 0.13);
    }}

    section[data-testid="stSidebar"] div[data-testid="stExpander"] summary * {{
        color: {TEXT_LIGHT} !important;
    }}

    section[data-testid="stSidebar"] label {{
        font-size: 13px !important;
        font-weight: 700 !important;
        color: {TEXT_MUTED} !important;
        margin-bottom: 6px !important;
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
        background: #FFFFFF !important;
        border: 1px solid rgba(37, 99, 235, 0.22) !important;
        border-radius: 14px !important;
        min-height: 48px !important;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover {{
        border-color: {BLUE} !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.10);
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] span {{
        color: {TEXT_LIGHT} !important;
        font-weight: 700 !important;
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
        font-weight: 700 !important;
    }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] input::placeholder {{
        color: #8799AE !important;
        opacity: 1 !important;
    }}

    section[data-testid="stSidebar"] [data-baseweb="tag"] {{
        background: linear-gradient(135deg, #DBEAFE 0%, #CCFBF1 100%) !important;
        border: 1px solid rgba(37, 99, 235, 0.22) !important;
        border-radius: 999px !important;
        color: {TEXT_LIGHT} !important;
        font-weight: 800 !important;
    }}

    section[data-testid="stSidebar"] [data-baseweb="tag"] span {{
        color: {TEXT_LIGHT} !important;
        font-weight: 800 !important;
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
        font-weight: 700 !important;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06) !important;
        padding-left: 12px !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stTextInput"] input::placeholder {{
        color: #8799AE !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stSlider"] span {{
        color: {TEXT_LIGHT} !important;
        font-weight: 700 !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stSlider"] div[role="slider"] {{
        background: linear-gradient(135deg, {BLUE} 0%, {CYAN} 100%) !important;
        border: 3px solid #FFFFFF !important;
        box-shadow: 0 0 0 4px rgba(37,99,235,0.16), 0 8px 18px rgba(37,99,235,0.18);
    }}

    .dashboard-hero {{
        background:
            radial-gradient(circle at top left, rgba(37,99,235,0.10), transparent 28%),
            radial-gradient(circle at top right, rgba(92,184,92,0.16), transparent 30%),
            linear-gradient(135deg, #FFFFFF 0%, #F1F7FF 100%);
        border: 1px solid rgba(37, 99, 235, 0.12);
        border-radius: 28px;
        padding: 34px 26px 30px 26px;
        margin-top: 0.5rem;
        margin-bottom: 1.8rem;
        text-align: center;
        box-shadow: 0 22px 48px rgba(37, 99, 235, 0.10);
    }}

    .dashboard-badge {{
        display: inline-block;
        color: {BLUE};
        background: rgba(37,99,235,0.08);
        border: 1px solid rgba(37,99,235,0.18);
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
        color: {TEXT_MUTED};
        margin: 0;
        text-align: center;
    }}

    .kpi-card {{
        background: linear-gradient(180deg, #FFFFFF 0%, #F8FBFF 100%);
        border: 1px solid rgba(37, 99, 235, 0.12);
        border-left: 6px solid {BLUE};
        padding: 20px 22px;
        min-height: 112px;
        border-radius: 20px;
        box-shadow: 0 16px 34px rgba(15, 23, 42, 0.07);
        text-align: center;
    }}

    .kpi-label {{
        font-size: 13px;
        color: {TEXT_MUTED};
        margin-bottom: 10px;
        font-weight: 800;
    }}

    .kpi-value {{
        font-size: 34px;
        line-height: 1;
        font-weight: 900;
        color: {TEXT_LIGHT};
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
        border: 1px solid rgba(37, 99, 235, 0.12);
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
        margin-left: auto;
        margin-right: auto;
        background: #FFFFFF;
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
        background: #FFFFFF;
        border: 1px solid rgba(37,99,235,0.16);
        padding: 9px 18px;
        border-radius: 999px;
        color: {TEXT_LIGHT} !important;
        transition: all 0.2s ease;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
    }}

    div[role="radiogroup"] label:hover {{
        border-color: {BLUE};
        box-shadow: 0 12px 26px rgba(37,99,235,0.12);
        transform: translateY(-1px);
    }}

    div[role="radiogroup"] label * {{
        color: {TEXT_LIGHT} !important;
    }}
</style>
""",
        unsafe_allow_html=True
    )
