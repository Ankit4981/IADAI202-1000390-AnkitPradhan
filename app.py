"""
LogiSight Analytics — Last-Mile Delivery Performance Dashboard
CRS Artificial Intelligence — Mathematics for AI-II (Formative Assessment-2)
Student: Ankit Pradhan | Roll Number: 1000390

Every number, chart and table is computed from data/Last_mile_Delivery_Data.csv.
Nothing is typed in from the design images.

UI notes
- Cards use st.container(key="card_...") and buttons use st.button(key="...").
  Streamlit turns each key into a stable CSS class (st-key-<key>), so the styling
  keeps working when Streamlit changes its internal HTML.
"""

import base64
import math
import re
import urllib.parse
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# ==============================================================================
# 1. SETUP & CONSTANTS
# ==============================================================================
st.set_page_config(
    page_title="LogiSight Analytics — Last-Mile Delivery Dashboard",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).parent
DATA_PATHS = [
    BASE_DIR / "data" / "Last_mile_Delivery_Data.csv",
    BASE_DIR / "Last_mile_Delivery_Data.csv",
]
ASSETS_DIR = BASE_DIR / "assets"

# Colours sampled from the Canva design
C_TEXT = "#0B3B38"
C_TITLE = "#00524C"
C_SB_1 = "#003B3C"
C_SB_2 = "#00635B"
C_PILL = "#DDFFF4"
C_PAGE = "#F8FDFD"
C_CARD_BORDER = "#B9DADC"
C_KPI_BG = "#F0FAF8"
C_KPI_BORDER = "#ADD7D9"
C_LATE_BG = "#FFF6F3"
C_LATE_BORDER = "#EEC9C2"
C_RED = "#E8221B"
C_GREEN = "#12A150"
C_MINT = "#DDF4EF"
C_ROW_ALT = "#EEF8F7"
C_GRID = "#E6EFEF"
FONT = "Roboto, 'Segoe UI', Arial, sans-serif"

WEATHER_ORDER = ["Sunny", "Cloudy", "Windy", "Fog", "Stormy", "Sandstorms"]
TRAFFIC_ORDER = ["Low", "Medium", "High", "Jam"]
AREA_ORDER = ["Metropolitan", "Urban", "Semi-Urban", "Other"]
AGE_ORDER = ["< 25", "25 – 40", "40+"]

TRAFFIC_COLORS = {"Low": "#BDEBD6", "Medium": "#34C08F", "High": "#0E7C66", "Jam": "#064E45"}
VEHICLE_COLORS = {"Van": "#0B8A74", "Scooter": "#10B981", "Motorcycle": "#2F7BF5", "Bicycle": "#94A3B8"}
AGE_COLORS = {"< 25": "#17BFA9", "25 – 40": "#5FD3E0", "40+": "#1F2A7A"}

NAV = [
    ("Delivery Analysis", "truck"),
    ("Agent Performance", "user"),
    ("Regional & Category", "bars"),
    ("Data Preparation", "table"),
    ("About Project", "book"),
]
FILTERS = [
    ("weather", "Weather Condition", "Weather"),
    ("traffic", "Traffic Density", "Traffic"),
    ("vehicle", "Vehicle Modality", "Vehicle"),
    ("area", "Geographic Area", "Area"),
    ("category", "Product Category", "Category"),
]

ICON_PATHS = {
    "truck": "<path d='M1 3h15v13H1z'/><path d='M16 8h4l3 3v5h-7z'/><circle cx='5.5' cy='18.5' r='2.5'/><circle cx='18.5' cy='18.5' r='2.5'/>",
    "user": "<circle cx='12' cy='8' r='4'/><path d='M4 21v-1a8 8 0 0 1 16 0v1'/>",
    "bars": "<path d='M5 20V11M10 20V5M15 20V13M20 20V9M2 21h21'/>",
    "table": "<rect x='3' y='3' width='18' height='18' rx='2'/><path d='M3 9h18M3 15h18M9 3v18M15 3v18'/>",
    "book": "<path d='M2 4h7a3 3 0 0 1 3 3v14a2 2 0 0 0-2-2H2z'/><path d='M22 4h-7a3 3 0 0 0-3 3v14a2 2 0 0 1 2-2h8z'/>",
    "filter": "<polygon points='22 3 2 3 10 12.5 10 19 14 21 14 12.5 22 3'/>",
    "timer": "<circle cx='12' cy='14' r='8'/><path d='M12 2v4M12 14v-4M9 2h6'/>",
    "alert": "<path d='M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z'/><path d='M12 9v4M12 17h.01'/>",
    "check": "<path d='M22 11.1V12a10 10 0 1 1-5.9-9.1'/><path d='M22 4L12 14l-3-3'/>",
    "home": "<path d='M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'/><path d='M9 22V12h6v10'/>",
    "reset": "<path d='M3 12a9 9 0 1 0 3-6.7L3 8'/><path d='M3 3v5h5'/>",
}


def svg(name: str, color: str, size: int = 20, width: float = 2) -> str:
    return (
        f"<svg width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' stroke='{color}' "
        f"stroke-width='{width}' stroke-linecap='round' stroke-linejoin='round'>{ICON_PATHS[name]}</svg>"
    )


def svg_uri(name: str, color: str) -> str:
    raw = svg(name, color, 24, 2).replace("<svg ", "<svg xmlns='http://www.w3.org/2000/svg' ", 1)
    return "url(\"data:image/svg+xml;utf8," + urllib.parse.quote(raw, safe="/:=' ") + "\")"


def clean_html(s: str) -> str:
    """Collapse whitespace so Streamlit's Markdown never treats indented HTML as code."""
    s = re.sub(r"<!--[\s\S]*?-->", "", s)
    s = re.sub(r">\s+<", "><", s)
    return " ".join(s.split()).strip()


def img_b64(*names: str) -> str:
    for n in names:
        p = ASSETS_DIR / n
        if p.exists():
            try:
                return base64.b64encode(p.read_bytes()).decode()
            except Exception:
                pass
    return ""


# ==============================================================================
# 2. CSS
# ==============================================================================
def inject_css(active_page: str):
    nav_css = ""
    for i, (label, icon) in enumerate(NAV):
        is_active = label == active_page
        nav_css += f"""
        .st-key-nav_{i} button::before {{
            content: ""; flex: none; width: 21px; height: 21px; margin-right: 16px;
            background: {svg_uri(icon, C_TITLE if is_active else "#FFFFFF")} center / contain no-repeat;
        }}"""
        if is_active:
            nav_css += f"""
        .st-key-nav_{i} button, .st-key-nav_{i} button:hover, .st-key-nav_{i} button:focus {{ background: {C_PILL} !important; color: {C_TITLE} !important; }}
        .st-key-nav_{i} button *, .st-key-nav_{i} button:hover * {{ color: {C_TITLE} !important; font-weight: 700 !important; }}"""

    EASE = "cubic-bezier(.2,.8,.2,1)"
    nav_motion = "".join(
        f'.st-key-nav_{i} {{ animation: lgSlideR .55s {0.15 + i * 0.08:.2f}s {EASE} both; }}\n    ' for i in range(len(NAV)))
    filter_motion = "".join(
        f'.st-key-frow_{k} {{ animation: lgSlideR .55s {0.65 + i * 0.08:.2f}s {EASE} both; }}\n    ' for i, (k, _, _) in enumerate(FILTERS))
    row_motion = "".join(
        f'.lg-js .lg-in :is(.lg-tbl tbody, .audit tbody, .audit) tr:nth-child({n}) {{ animation-delay: {0.15 + n * 0.07:.2f}s; }}\n    ' for n in range(1, 10))

    P = '.lg-js [data-testid="stPlotlyChart"].lg-in'
    cm = []
    # grouped / simple bars grow up from the baseline
    cm.append(f"{P} .barlayer .point path {{ transform-box: fill-box; transform-origin: 50% 100%; animation: lgGrow .9s {EASE} both; }}")
    cm.append(f"{P} .barlayer .point text {{ animation: lgFade .5s 1s both; }}")
    for t in range(1, 5):
        for p in range(1, 9):
            cm.append(f"{P} .barlayer .trace:nth-child({t}) .point:nth-child({p}) path {{ animation-delay: {0.1 + (t - 1) * 0.16 + (p - 1) * 0.06:.2f}s; }}")
    # scatter: points rise in per cohort, trendline draws itself
    cm.append(f"{P} .scatterlayer .trace .points {{ animation: lgPop .9s {EASE} both; }}")
    cm.append(f"{P} .scatterlayer .trace .js-line {{ stroke-dasharray: 3000; animation: lgDraw 1.4s .9s ease-out both; }}")
    for t in range(1, 5):
        cm.append(f"{P} .scatterlayer .trace:nth-child({t}) .points {{ animation-delay: {(t - 1) * 0.18:.2f}s; }}")
    # heatmap: tiles zoom in, numbers appear one after another
    cm.append(f"{P} .heatmaplayer image {{ transform-box: fill-box; transform-origin: 50% 50%; animation: lgZoom 1s {EASE} both; }}")
    cm.append(f"{P} .infolayer .annotation {{ animation: lgFade .5s both; }}")
    for n in range(1, 25):
        cm.append(f"{P} .infolayer .annotation:nth-child({n}) {{ animation-delay: {0.55 + n * 0.045:.2f}s; }}")
    cm.append(f"{P} .infolayer .legend {{ animation: lgFade .6s .6s both; }}")
    # boxplots grow from the bottom, left to right
    cm.append(f"{P} .boxlayer .trace {{ transform-box: fill-box; transform-origin: 50% 100%; animation: lgGrow .8s {EASE} both; }}")
    for n in range(1, 25):
        cm.append(f"{P} .boxlayer .trace:nth-child({n}) {{ animation-delay: {0.05 + n * 0.05:.2f}s; }}")
    chart_motion = "\n    ".join(cm)

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');

    html, body, .stApp {{ font-family: {FONT}; }}
    .stApp :is(p, div, label, button, input, td, th, h1, h2, h3, h4, li, a) {{ font-family: {FONT}; }}
    .stApp {{ background: {C_PAGE}; color: {C_TEXT}; }}

    /* Hide Streamlit chrome */
    [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer {{ display: none !important; }}
    header[data-testid="stHeader"] {{ background: transparent !important; }}
    .block-container {{ padding: 1rem 1.6rem 1.5rem 1.6rem !important; max-width: 100% !important; }}
    [data-testid="stHorizontalBlock"] {{ gap: 1rem !important; }}
    [data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"] {{ gap: 0.9rem; }}

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"][aria-expanded="false"] {{
        transform: none !important;
        margin-left: 0 !important;
        display: block !important;
        visibility: visible !important;
        width: 262px !important; min-width: 262px !important; max-width: 262px !important;
        background: linear-gradient(135deg, {C_SB_1} 0%, {C_SB_2} 100%) !important;
        border-right: 0 !important;
    }}
    section[data-testid="stSidebar"] > div {{ background: transparent !important; width: 262px !important; }}
    [data-testid="stSidebarHeader"] {{ padding: 0.4rem 0.6rem 0 0.6rem !important; min-height: 0 !important; height: auto !important; }}
    [data-testid="stSidebarUserContent"] {{ padding: 0 1rem 1rem 1rem !important; }}
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{ gap: 0.3rem; }}
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {{ gap: 0.4rem !important; align-items: center; }}

    /* Ensure sidebar toggle arrow is prominently visible if ever collapsed */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    button[data-testid="stSidebarCollapseButton"] {{
        display: flex !important;
        visibility: visible !important;
        background: #00524C !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        z-index: 999999 !important;
    }}
    [data-testid="stSidebarCollapsedControl"] svg,
    [data-testid="collapsedControl"] svg,
    button[data-testid="stSidebarCollapseButton"] svg {{
        fill: #FFFFFF !important;
        stroke: #FFFFFF !important;
    }}

    .brand {{ display: flex; align-items: flex-start; gap: 12px; margin: 0 0 14px 0; }}
    .brand-ic {{ width: 48px; height: 48px; border-radius: 13px; background: #11806F; display: flex;
                 align-items: center; justify-content: center; flex: none; box-shadow: 0 2px 6px rgba(0,0,0,.25); }}
    .brand-t {{ color: #fff; font-size: 21px; font-weight: 700; line-height: 1.12; }}
    .brand-s {{ color: #D7F0EA; font-size: 11.5px; line-height: 1.25; margin-top: 4px; }}
    .nav-h {{ color: #fff; font-weight: 700; font-size: 13px; letter-spacing: .03em; margin: 2px 0 6px 14px; }}
    .sb-sep {{ border-top: 1px solid #28AE9F; margin: 10px 0 12px 0; opacity: .75; }}
    .flt-h {{ display: flex; align-items: center; gap: 12px; color: #fff; font-weight: 700; font-size: 15px; margin: 0 0 8px 14px; }}
    .flt-l {{ color: #fff; font-size: 13px; line-height: 1.2; padding-left: 14px; }}

    /* Nav buttons */
    [class*="st-key-nav_"] button {{
        width: 100%; display: flex; justify-content: flex-start; align-items: center;
        background: transparent !important; border: 0 !important; box-shadow: none !important;
        border-radius: 10px; padding: 0.42rem 0.8rem; min-height: 0; color: #fff !important;
    }}
    [class*="st-key-nav_"] button > div {{ width: auto; flex: 1; justify-content: flex-start; }}
    [class*="st-key-nav_"] button :is(p, div) {{ color: #fff; font-size: 15px; font-weight: 400; text-align: left; margin: 0; white-space: nowrap; }}
    [class*="st-key-nav_"] button:hover {{ background: rgba(255,255,255,.10) !important; }}
    {nav_css}

    /* Filter selects (old + new Streamlit markup) */
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] {{ margin: 0; }}
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] :is([data-baseweb="select"] > div, [role="group"]) {{
        background: #F5FFFB !important; border: 0 !important; border-radius: 9px !important; min-height: 34px !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] :is(input, [data-baseweb="select"] *) {{
        color: {C_TEXT} !important; -webkit-text-fill-color: {C_TEXT} !important; font-size: 13px !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] svg {{ fill: {C_TEXT} !important; color: {C_TEXT} !important; }}

    /* Apply / Reset */
    .st-key-btn_apply button, .st-key-btn_reset button {{
        width: 100%; border-radius: 11px; min-height: 46px; font-weight: 500;
        display: flex; align-items: center; justify-content: center; gap: 10px; box-shadow: 0 1px 3px rgba(0,0,0,.2);
    }}
    .st-key-btn_apply button {{ background: #00A897 !important; border: 1px solid #2FCDBB !important; }}
    .st-key-btn_apply button :is(p, div) {{ color: #fff !important; font-size: 15px; font-weight: 500; margin: 0; }}
    .st-key-btn_reset button {{ background: #DDF7EF !important; border: 1px solid #BFE8DC !important; }}
    .st-key-btn_reset button :is(p, div) {{ color: {C_TITLE} !important; font-size: 15px; font-weight: 500; margin: 0; }}
    .st-key-btn_apply button::before {{ content: ""; width: 18px; height: 18px; background: {svg_uri("filter", "#FFFFFF")} center / contain no-repeat; }}
    .st-key-btn_reset button::before {{ content: ""; width: 18px; height: 18px; background: {svg_uri("reset", C_TITLE)} center / contain no-repeat; }}

    /* ---------- Header ---------- */
    .hdr {{ display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 14px; }}
    .hdr-t {{ font-size: 32px; font-weight: 700; color: {C_TITLE}; line-height: 1.1; }}
    .hdr-s {{ font-size: 16px; color: {C_TEXT}; margin-top: 6px; }}
    .hdr-banner {{ flex: 1; display: flex; justify-content: center; min-width: 0; }}
    .hdr-banner img {{ height: 58px; max-width: 100%; object-fit: contain; border-radius: 8px; }}
    .hdr-banner {{ align-self: center; }}
    .hdr-r {{ display: flex; align-items: center; gap: 12px; flex: none; }}
    .stu {{ background: #E4FAF3; border-radius: 10px; padding: 10px 16px; font-size: 12.5px; font-weight: 700;
            color: {C_TITLE}; line-height: 1.45; white-space: nowrap; }}
    .logo {{ height: 52px; background: #fff; border: 1px solid #E1EEEE; border-radius: 10px; padding: 3px 8px;
             display: flex; align-items: center; }}
    .logo img {{ max-height: 44px; width: auto; }}
    .logo b {{ color: {C_TITLE}; font-size: 14px; }}

    /* ---------- KPI cards ---------- */
    .kpi {{ display: flex; align-items: center; gap: 16px; background: {C_KPI_BG}; border: 1.5px solid {C_KPI_BORDER};
            border-radius: 16px; padding: 18px 20px; height: 118px; box-sizing: border-box; margin-bottom: 6px; }}
    .kpi.late {{ background: {C_LATE_BG}; border-color: {C_LATE_BORDER}; }}
    .kpi-ic {{ width: 46px; height: 46px; border-radius: 50%; background: #D9F6EA; display: flex;
               align-items: center; justify-content: center; flex: none; }}
    .kpi.late .kpi-ic {{ background: #FFE4DD; }}
    .kpi-t {{ font-size: 16px; font-weight: 700; color: {C_TEXT}; line-height: 1.2; }}
    .kpi-n {{ font-size: clamp(26px, 2.5vw, 38px); font-weight: 700; color: {C_TITLE}; line-height: 1.12; white-space: nowrap; }}
    .kpi-c {{ font-size: 12.5px; color: #3D5654; line-height: 1.25; }}

    /* ---------- Cards ---------- */
    [class*="st-key-card"] {{
        background: {C_PAGE}; border: 1.5px solid {C_CARD_BORDER}; border-radius: 18px;
        padding: 16px 20px 14px 20px; gap: 0.5rem; box-sizing: border-box; min-width: 0; max-width: 100%;
    }}
    [class*="st-key-card"] [data-testid="stElementContainer"], [class*="st-key-card"] .element-container {{ max-width: 100%; min-width: 0; }}
    [class*="st-key-card"] .js-plotly-plot, [class*="st-key-card"] .stPlotlyChart {{ max-width: 100%; }}
    [class*="st-key-card_in"] {{ background: #FBFEFE; border-radius: 16px; }}
    .ct {{ font-size: 17px; font-weight: 700; color: {C_TEXT}; line-height: 1.2; margin: 0 0 2px 0; }}
    .ct-big {{ font-size: 25px; font-weight: 700; color: {C_TEXT}; line-height: 1.15; }}
    .ct-sub {{ font-size: 14.5px; color: {C_TEXT}; margin-top: 4px; }}
    .note {{ font-size: 12px; color: #5B7270; margin-top: 2px; }}

    /* ---------- Tables ---------- */
    .lg-tbl {{ width: 100%; border-collapse: collapse; font-size: 14px; color: {C_TEXT}; }}
    .lg-tbl, .lg-tbl th, .lg-tbl td {{ border: 0 !important; }}
    .lg-tbl th {{ background: {C_MINT}; text-align: left; font-weight: 500; padding: 9px 14px; font-size: 13.5px; }}
    .lg-tbl td {{ padding: 9px 14px; background: transparent; }}
    .lg-tbl tbody tr:nth-child(even) td {{ background: {C_ROW_ALT}; }}
    .lg-tbl td:first-child {{ font-weight: 700; }}
    .lg-tbl.coh th, .lg-tbl.coh td {{ padding: 14px 12px; }}
    .lg-tbl.coh th {{ background: {C_MINT}; font-weight: 700; font-size: 13px; }}
    .lg-tbl.coh tbody tr:nth-child(even) td {{ background: transparent; }}
    .lg-tbl.coh td {{ border-bottom: 1px solid #E3EDED !important; }}
    .audit {{ width: 100%; border-collapse: collapse; font-size: 14.5px; color: {C_TEXT}; }}
    .audit, .audit td {{ border: 0 !important; }}
    .audit td {{ padding: 11px 14px; background: transparent; }}
    .audit tr:nth-child(odd) td {{ background: {C_ROW_ALT}; }}
    .audit td:last-child {{ text-align: right; font-weight: 700; }}
    .audit tr.tot td {{ background: #D5F3E8 !important; font-weight: 700; }}
    .formula {{ background: #DDF6EA; border-radius: 10px; padding: 12px 16px; font-weight: 700; font-size: 14px;
                color: {C_TEXT}; margin: 12px 0 14px 0; word-break: break-word; }}
    .blist {{ margin: 0; padding-left: 22px; font-size: 14.5px; line-height: 1.75; color: {C_TEXT}; }}
    .para {{ font-size: 15.5px; line-height: 1.6; color: {C_TEXT}; margin: 0; }}
    .dl-k {{ font-weight: 700; font-size: 15.5px; color: {C_TEXT}; margin-top: 16px; }}
    .dl-v {{ font-size: 15px; color: #3D5654; margin-top: 3px; }}
    .ic-row {{ display: flex; align-items: center; gap: 16px; margin-bottom: 10px; }}
    .ic-circ {{ width: 42px; height: 42px; border-radius: 50%; background: #D9F6EA; display: flex;
                align-items: center; justify-content: center; flex: none; }}

    /* ---------- Sidebar alignment ---------- */
    [data-testid="stSidebarContent"] {{ padding-left: 0 !important; padding-right: 0 !important; }}
    [data-testid="stSidebarUserContent"] {{ padding: 0 16px 20px 16px !important; }}
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{ gap: 0.35rem; }}
    .brand {{ margin: 0 0 14px 0; padding-left: 0; }}

    /* nav: identical rows, icon column and text column line up */
    .st-key-navwrap {{ display: flex; flex-direction: column; gap: 2px; }}
    [class*="st-key-nav_"], [class*="st-key-nav_"] > div, [class*="st-key-nav_"] [data-testid="stButton"] {{ width: 100% !important; }}
    [class*="st-key-nav_"] button {{
        width: 100% !important; height: 40px; min-height: 40px; padding: 0 14px !important;
        justify-content: flex-start !important; gap: 0; transition: background .25s ease, transform .25s ease;
    }}
    [class*="st-key-nav_"] button::before {{ margin-right: 14px !important; }}
    [class*="st-key-nav_"] button:hover {{ transform: translateX(3px); }}

    /* filters: label column + select column on one grid, vertically centred */
    [class*="st-key-frow_"], [class*="st-key-frow_"] > [data-testid="stLayoutWrapper"] {{ width: 100% !important; align-self: stretch; }}
    section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {{
        display: grid !important; grid-template-columns: 100px minmax(0, 1fr); column-gap: 6px;
        align-items: center; min-height: 40px; margin-bottom: 0;
    }}
    section[data-testid="stSidebar"] [data-testid="stColumn"] {{
        width: auto !important; min-width: 0 !important; flex: none !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stColumn"] [data-testid="stVerticalBlock"] {{ gap: 0; }}
    section[data-testid="stSidebar"] [data-testid="stSelectbox"],
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] > div {{ width: 100% !important; }}
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] :is([data-baseweb="select"] > div, [role="group"]) {{
        min-height: 36px !important; height: 36px !important; align-items: center !important; transition: box-shadow .2s ease;
    }}
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] :is([data-baseweb="select"] > div, [role="group"]):hover {{
        box-shadow: 0 0 0 2px rgba(47,205,187,.55);
    }}

    /* selected value sits in the vertical middle of its box */
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] input {{ height: 100% !important; line-height: 34px !important; padding-top: 0 !important; padding-bottom: 0 !important; }}
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] :is([role="group"], [data-baseweb="select"] > div) > * {{ align-self: center; }}
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div > div:first-child {{ display: flex; align-items: center; }}

    /* Apply / Reset: same width, same height, stacked */
    .st-key-btn_apply, .st-key-btn_reset, .st-key-btn_apply [data-testid="stButton"], .st-key-btn_reset [data-testid="stButton"] {{ width: 100% !important; }}
    .st-key-btn_apply button, .st-key-btn_reset button {{ width: 100% !important; height: 40px; min-height: 40px; transition: transform .2s ease, box-shadow .2s ease, filter .2s ease; }}
    .st-key-btn_apply button:hover, .st-key-btn_reset button:hover {{ transform: translateY(-2px); box-shadow: 0 6px 14px rgba(0,0,0,.25); filter: brightness(1.05); }}
    .st-key-btn_apply button:active, .st-key-btn_reset button:active {{ transform: translateY(0); }}
    .st-key-btn_apply {{ margin-top: 6px; }}

    /* ---------- Motion ---------- */
    @keyframes lgRise   {{ from {{ opacity: 0; transform: translateY(24px) scale(.97); }} to {{ opacity: 1; transform: none; }} }}
    @keyframes lgSlideR {{ from {{ opacity: 0; transform: translateX(-26px); }} to {{ opacity: 1; transform: none; }} }}
    @keyframes lgSlideL {{ from {{ opacity: 0; transform: translateX(-90px); }} to {{ opacity: 1; transform: none; }} }}
    @keyframes lgFade   {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    @keyframes lgGrow   {{ from {{ opacity: .15; transform: scaleY(0); }} to {{ opacity: 1; transform: scaleY(1); }} }}
    @keyframes lgPop    {{ from {{ opacity: 0; transform: translateY(26px); }} to {{ opacity: 1; transform: none; }} }}
    @keyframes lgZoom   {{ from {{ opacity: 0; transform: scale(.9); }} to {{ opacity: 1; transform: none; }} }}
    @keyframes lgDraw   {{ from {{ stroke-dashoffset: 3000; }} to {{ stroke-dashoffset: 0; }} }}
    @keyframes lgDrive  {{ 0%, 100% {{ transform: translateX(-2px); }} 50% {{ transform: translateX(2px); }} }}
    @keyframes lgPulse  {{ 0% {{ box-shadow: 0 0 0 0 rgba(232,34,27,.35); }} 70% {{ box-shadow: 0 0 0 12px rgba(232,34,27,0); }} 100% {{ box-shadow: 0 0 0 0 rgba(232,34,27,0); }} }}

    /* page-load sequence: sidebar, header, KPI cards */
    .brand {{ animation: lgSlideR .6s cubic-bezier(.2,.8,.2,1) both; }}
    .brand-ic svg {{ animation: lgDrive 3.2s ease-in-out infinite; }}
    .nav-h {{ animation: lgFade .6s .1s both; }}
    {nav_motion}
    .flt-h {{ animation: lgFade .6s .55s both; }}
    {filter_motion}
    .st-key-btn_apply {{ animation: lgSlideR .6s 1.0s cubic-bezier(.2,.8,.2,1) both; }}
    .st-key-btn_reset {{ animation: lgSlideR .6s 1.1s cubic-bezier(.2,.8,.2,1) both; }}
    .hdr-t {{ animation: lgSlideR .7s .1s cubic-bezier(.2,.8,.2,1) both; }}
    .hdr-s {{ animation: lgFade .8s .35s both; }}
    .hdr-banner > * {{ animation: lgFade 1s .2s both; }}
    .hdr-r {{ animation: lgFade .8s .5s both; }}
    .kpi {{ animation: lgRise .7s cubic-bezier(.2,.8,.2,1) both; }}
    [data-testid="stColumn"]:nth-of-type(1) .kpi {{ animation-delay: .25s; }}
    [data-testid="stColumn"]:nth-of-type(2) .kpi {{ animation-delay: .4s; }}
    [data-testid="stColumn"]:nth-of-type(3) .kpi {{ animation-delay: .55s; }}
    [data-testid="stColumn"]:nth-of-type(4) .kpi {{ animation-delay: .7s; }}
    .kpi.late .kpi-ic {{ animation: lgPulse 2.6s 1.6s infinite; }}

    /* animated truck scene in the header */
    .truck-scene {{ height: 64px; width: 100%; max-width: 560px; display: block; }}
    @keyframes lgFar   {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-520px); }} }}
    @keyframes lgNear  {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-520px); }} }}
    @keyframes lgRoad  {{ from {{ stroke-dashoffset: 0; }} to {{ stroke-dashoffset: -28; }} }}
    @keyframes lgSpin  {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
    @keyframes lgBounce {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-1.2px); }} }}
    @keyframes lgStreak {{ 0% {{ transform: translateX(14px); opacity: 0; }} 30% {{ opacity: .8; }} 100% {{ transform: translateX(-26px); opacity: 0; }} }}
    .ts-far  {{ animation: lgFar 26s linear infinite; }}
    .ts-near {{ animation: lgNear 9s linear infinite; }}
    .ts-road {{ animation: lgRoad .45s linear infinite; }}
    .ts-truck {{ animation: lgBounce .5s ease-in-out infinite; }}
    .ts-wheel {{ transform-box: fill-box; transform-origin: center; animation: lgSpin .7s linear infinite; }}
    .ts-streak {{ animation: lgStreak 1.1s linear infinite; }}
    .ts-streak.b {{ animation-delay: .35s; }}
    .ts-streak.c {{ animation-delay: .7s; }}

    /* photo-truck scene (uses assets/truck.png cut from banner.png). Truck drives LEFT, scenery moves RIGHT */
    .truck-scene2 {{ height: 108px; width: auto; max-width: 100%; display: block;
        -webkit-mask-image: linear-gradient(90deg, transparent 0, #000 14%, #000 86%, transparent 100%);
        mask-image: linear-gradient(90deg, transparent 0, #000 14%, #000 86%, transparent 100%); }}
    @keyframes lgFarR  {{ from {{ transform: translateX(0); }} to {{ transform: translateX(760px); }} }}
    @keyframes lgRoadR {{ from {{ stroke-dashoffset: 0; }} to {{ stroke-dashoffset: 36; }} }}
    @keyframes lgStreakR {{ 0% {{ transform: translateX(-6px); opacity: 0; }} 25% {{ opacity: .85; }} 100% {{ transform: translateX(46px); opacity: 0; }} }}
    @keyframes lgRock  {{ 0%, 100% {{ transform: translateY(0) rotate(0deg); }} 50% {{ transform: translateY(-1.6px) rotate(-.25deg); }} }}
    .t2-far   {{ animation: lgFarR 30s linear infinite; }}
    .t2-near  {{ animation: lgFarR 11s linear infinite; }}
    .t2-road  {{ animation: lgRoadR .5s linear infinite; }}
    .t2-truck {{ transform-box: fill-box; transform-origin: 50% 100%; animation: lgRock .55s ease-in-out infinite; }}
    .t2-wheel {{ transform-box: fill-box; transform-origin: center; animation: lgSpin .55s linear infinite; }}
    .t2-streak {{ animation: lgStreakR 1.2s linear infinite; }}
    .t2-streak.b {{ animation-delay: .4s; }}
    .t2-streak.c {{ animation-delay: .8s; }}

    /* banner: your banner artwork; the truck drives across it in a loop (right -> left) */
    .banner-scene {{ width: 100%; max-width: 660px; height: auto; display: block;
        -webkit-mask-image: linear-gradient(90deg, transparent 0, #000 4%, #000 96%, transparent 100%);
        mask-image: linear-gradient(90deg, transparent 0, #000 4%, #000 96%, transparent 100%); }}
    @keyframes lgDrive3 {{ 0% {{ transform: translateX(1390px); }} 82% {{ transform: translateX(-1730px); }} 100% {{ transform: translateX(-1730px); }} }}
    @keyframes lgSpinCCW {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(-360deg); }} }}
    @keyframes lgRock3 {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-3.5px); }} }}
    @keyframes lgDash3 {{ from {{ stroke-dashoffset: 0; }} to {{ stroke-dashoffset: -110; }} }}
    @keyframes lgStreak3 {{ 0% {{ transform: translateX(-10px); opacity: 0; }} 25% {{ opacity: .9; }} 100% {{ transform: translateX(120px); opacity: 0; }} }}
    .b-drive {{ animation: lgDrive3 8.5s linear -2.4s infinite; }}
    .b-rock  {{ animation: lgRock3 .5s ease-in-out infinite; }}
    .b-wheel {{ transform-box: fill-box; transform-origin: center; animation: lgSpinCCW .55s linear infinite; }}
    .b-dash  {{ animation: lgDash3 .9s linear infinite; }}
    .b-streak {{ animation: lgStreak3 1.1s linear infinite; }}
    .b-streak.b {{ animation-delay: .35s; }}
    .b-streak.c {{ animation-delay: .7s; }}

    /* hover feedback */
    [class*="st-key-card"] {{ transition: opacity .7s ease, transform .7s cubic-bezier(.2,.8,.2,1), box-shadow .3s ease; }}
    [class*="st-key-card"]:hover {{ box-shadow: 0 10px 28px rgba(0,82,76,.10); }}
    .kpi {{ transition: box-shadow .3s ease; }}
    .kpi:hover {{ box-shadow: 0 8px 22px rgba(0,82,76,.14); }}
    .lg-tbl tbody td {{ transition: background .2s ease; }}
    .lg-tbl tbody tr:hover td, .audit tr:hover td {{ background: #D5F3E8 !important; }}

    /* keep the page steady while Streamlit reruns (no grey flash) */
    [data-stale="true"] {{ opacity: 1 !important; transition: none !important; }}

    /* scroll reveal + chart reveal: only armed once the JS helper is running (html.lg-js) */
    .lg-js [class*="st-key-card"] {{ opacity: 0; transform: translateY(26px); }}
    .lg-js [class*="st-key-card"].lg-in {{ opacity: 1; transform: none; }}
    .lg-js [class*="st-key-card"]:not(.lg-in) :is(.lg-tbl, .audit) tbody tr, .lg-js [class*="st-key-card"]:not(.lg-in) .audit tr {{ opacity: 0; }}
    .lg-js [class*="st-key-card"].lg-in :is(.lg-tbl tbody tr, .audit tr) {{ animation: lgPop .55s cubic-bezier(.2,.8,.2,1) both; }}
    {row_motion}

    .lg-js [data-testid="stPlotlyChart"]:not(.lg-in) :is(.barlayer, .scatterlayer, .heatmaplayer, .boxlayer, .infolayer .annotation, .infolayer .legend) {{ opacity: 0; }}
    {chart_motion}

    @media (prefers-reduced-motion: reduce) {{
        *, *::before, *::after {{ animation: none !important; transition: none !important; }}
        .lg-js [class*="st-key-card"] {{ opacity: 1 !important; transform: none !important; }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ==============================================================================
# 3. DATA
# ==============================================================================
@st.cache_data(show_spinner=False)
def load_data():
    path = next((p for p in DATA_PATHS if p.exists()), None)
    if path is None:
        st.error("Dataset not found. Put Last_mile_Delivery_Data.csv in the data/ folder.")
        st.stop()

    df = pd.read_csv(path)
    raw_count = len(df)

    for c in ["Weather", "Traffic", "Vehicle", "Area", "Category"]:
        df[c] = df[c].astype("string").str.strip()
    df = df.replace({"": pd.NA, "NaN": pd.NA, "nan": pd.NA})

    spelling_fixed = int((df["Area"] == "Metropolitian").sum())
    df["Area"] = df["Area"].replace({"Metropolitian": "Metropolitan"})
    df["Vehicle"] = df["Vehicle"].str.title()
    df["Agent_Rating"] = pd.to_numeric(df["Agent_Rating"], errors="coerce")
    df["Agent_Age"] = pd.to_numeric(df["Agent_Age"], errors="coerce")
    df["Delivery_Time"] = pd.to_numeric(df["Delivery_Time"], errors="coerce")

    duplicates = int(df.duplicated(subset=["Order_ID"]).sum())
    raw_over40 = int((df["Agent_Age"] > 40).sum())          # agents aged 40+ in the raw file

    # Drop rows with missing Weather / Traffic / Rating, counted one step at a time
    step = df
    drops = {}
    for label, col in [("weather", "Weather"), ("traffic", "Traffic"), ("rating", "Agent_Rating")]:
        before = len(step)
        step = step.dropna(subset=[col])
        drops[label] = before - len(step)
    df = step.copy()

    rating_over_5 = int((df["Agent_Rating"] > 5).sum())
    clean_over40 = int((df["Agent_Age"] > 40).sum())         # agents aged 40+ still present after cleaning
    df["Agent_Age_Group"] = pd.cut(df["Agent_Age"], bins=[0, 24, 40, 200], labels=AGE_ORDER)

    mean_dt = float(df["Delivery_Time"].mean())
    std_dt = float(df["Delivery_Time"].std(ddof=0))
    thresh = mean_dt + std_dt
    df["Is_Late"] = df["Delivery_Time"] > thresh

    meta = dict(
        raw=raw_count, clean=len(df), duplicates=duplicates, drops=drops,
        spelling_fixed=spelling_fixed, rating_over_5=rating_over_5, raw_over40=raw_over40, clean_over40=clean_over40,
        mean=mean_dt, std=std_dt, thresh=thresh, late=int(df["Is_Late"].sum()),
    )
    meta["late_pct"] = meta["late"] / meta["clean"] * 100
    return df, meta


# ==============================================================================
# 4. CHARTS
# ==============================================================================
CFG = {"displayModeBar": False}


_CHART_N = [0]


def show(fig):
    """Draw a chart. The key includes the active filters, so changing a filter remounts the
    chart and its entrance animation plays again."""
    _CHART_N[0] += 1
    ss = st.session_state
    sig = "_".join(str(ss.get(f"f_{k}", "All")) for k, _, _ in FILTERS)
    key = f"pc_{ss.get('page', '')}_{_CHART_N[0]}_{sig}".replace(" ", "").replace("&", "")
    try:
        st.plotly_chart(fig, width="stretch", config=CFG, key=key)
    except TypeError:
        st.plotly_chart(fig, use_container_width=True, config=CFG, key=key)


def base_layout(height, **kw):
    lay = dict(
        height=height, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT, size=12, color=C_TEXT),
        hoverlabel=dict(bgcolor=C_SB_1, font=dict(color="#fff", family=FONT, size=12)),
    )
    lay.update(kw)
    return lay


def delay_chart(df, height=290):
    g = df.groupby(["Weather", "Traffic"], observed=True)["Delivery_Time"].mean().reset_index()
    weathers = [w for w in WEATHER_ORDER if w in set(g["Weather"])]
    fig = go.Figure()
    for t in TRAFFIC_ORDER:
        s = g[g["Traffic"] == t].set_index("Weather").reindex(weathers)
        fig.add_bar(
            x=weathers, y=s["Delivery_Time"].round(1), name=t, marker_color=TRAFFIC_COLORS[t],
            hovertemplate="%{x} · " + t + "<br>Avg: %{y:.1f} min<extra></extra>",
        )
    fig.update_layout(**base_layout(
        height, barmode="group", bargap=0.28, bargroupgap=0.04,
        legend=dict(orientation="h", x=1, xanchor="right", y=1.12, font=dict(size=12)),
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(showgrid=False, linecolor="#CFE0E0", tickfont=dict(size=12, color=C_TEXT)),
        yaxis=dict(title="Avg. Delivery Time (min)", gridcolor=C_GRID, rangemode="tozero", zeroline=False),
    ))
    return fig


def vehicle_chart(df, height=290):
    g = df.groupby("Vehicle", observed=True)["Delivery_Time"].agg(["mean", "count"]).reset_index().sort_values("mean")
    fig = go.Figure(go.Bar(
        x=g["Vehicle"], y=g["mean"].round(1), text=[f"{v:.1f}" for v in g["mean"]], textposition="outside",
        textfont=dict(size=14, color=C_TEXT, family=FONT), cliponaxis=False,
        marker_color=[VEHICLE_COLORS.get(v, "#64748B") for v in g["Vehicle"]],
        customdata=g["count"], hovertemplate="%{x}<br>Avg: %{y:.1f} min<br>Orders: %{customdata:,}<extra></extra>",
    ))
    fig.update_layout(**base_layout(
        height, margin=dict(l=10, r=10, t=28, b=10), bargap=0.12,
        xaxis=dict(showgrid=False, linecolor="#CFE0E0", tickfont=dict(size=13, color=C_TEXT)),
        yaxis=dict(gridcolor=C_GRID, rangemode="tozero", zeroline=False),
    ))
    return fig


def scatter_chart(df, height=290, sample=2500):
    d = df.dropna(subset=["Agent_Rating", "Delivery_Time"])
    d = d[d["Agent_Rating"] <= 5]
    fig = go.Figure()
    if len(d) >= 2:
        slope, icpt = np.polyfit(d["Agent_Rating"], d["Delivery_Time"], 1)
        samp = d.sample(sample, random_state=42) if len(d) > sample else d
        for grp in AGE_ORDER:
            s = samp[samp["Agent_Age_Group"] == grp]
            if len(s):
                fig.add_scatter(
                    x=s["Agent_Rating"], y=s["Delivery_Time"], mode="markers", name=grp,
                    marker=dict(size=5, color=AGE_COLORS[grp], opacity=0.55),
                    hovertemplate="Rating: %{x}<br>Time: %{y} min<extra>" + grp + "</extra>",
                )
        xs = np.array([d["Agent_Rating"].min(), d["Agent_Rating"].max()])
        fig.add_scatter(x=xs, y=slope * xs + icpt, mode="lines", name="OLS trend",
                        line=dict(color="#EF3B33", width=2), hoverinfo="skip", showlegend=False)
    fig.update_layout(**base_layout(
        height, margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(x=0.99, xanchor="right", y=0.99, yanchor="top", bgcolor="rgba(255,255,255,.7)", font=dict(size=12), itemsizing="constant"),
        xaxis=dict(title="Agent Rating", gridcolor=C_GRID, linecolor="#CFE0E0", zeroline=False, dtick=1),
        yaxis=dict(title="Delivery Time (min)", gridcolor=C_GRID, linecolor="#CFE0E0", zeroline=False),
    ))
    return fig


def heatmap_chart(df, height=290, compact=False):
    cols = [t for t in TRAFFIC_ORDER if t in set(df["Traffic"])]
    areas = [a for a in AREA_ORDER if a in set(df["Area"])] + sorted(set(df["Area"]) - set(AREA_ORDER))
    pv = df.pivot_table(index="Area", columns="Traffic", values="Delivery_Time", aggfunc="mean")
    pv = pv.reindex(index=areas, columns=cols)
    z = pv.values.astype(float)
    if np.isfinite(z).any():
        zmin, zmax = float(np.nanmin(z)), float(np.nanmax(z))
    else:
        zmin, zmax = 0.0, 1.0
    span = max(zmax - zmin, 1e-9)
    fig = go.Figure(go.Heatmap(
        z=z, x=cols, y=areas, xgap=3, ygap=3, zmin=zmin, zmax=zmax, hoverongaps=False,
        colorscale=[[0, "#E6F7EF"], [0.35, "#A9E8CB"], [0.65, "#3DBE8F"], [1, "#0B5B46"]],
        showscale=not compact,
        colorbar=dict(title=dict(text="Avg<br>Time<br>(min)", font=dict(size=11)), thickness=12, len=0.8, tickfont=dict(size=11)),
        hovertemplate="%{y} · %{x}<br>Avg: %{z:.1f} min<extra></extra>",
    ))
    ann = []
    for i, a in enumerate(areas):
        for j, c in enumerate(cols):
            v = z[i, j]
            if np.isfinite(v):
                dark = (v - zmin) / span > 0.6
                ann.append(dict(x=c, y=a, text=f"<b>{v:.1f}</b>", showarrow=False,
                                font=dict(size=11 if compact else 13, color="#fff" if dark else C_TEXT)))
            else:
                ann.append(dict(x=c, y=a, text="–", showarrow=False, font=dict(size=13, color="#8AA")))
    fig.update_layout(**base_layout(
        height, annotations=ann, margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(side="top", showgrid=False, tickangle=0, tickfont=dict(size=11 if compact else 13)),
        yaxis=dict(autorange="reversed", showgrid=False, automargin=True, tickfont=dict(size=11 if compact else 13, color=C_TEXT)),
    ))
    return fig


def box_chart(df, height=290):
    cats = sorted(df["Category"].dropna().unique())
    fig = go.Figure()
    for c in cats:
        fig.add_trace(go.Box(
            y=df.loc[df["Category"] == c, "Delivery_Time"], name=c, boxpoints=False,
            marker_color="#0E6B5C", line=dict(color="#0E6B5C", width=1.6), fillcolor="#CDEFE3",
            whiskerwidth=0.6, showlegend=False,
        ))
    fig.update_layout(**base_layout(
        height, margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, tickangle=-40 if len(cats) > 6 else 0, tickfont=dict(size=11), linecolor="#CFE0E0"),
        yaxis=dict(title="Delivery Time (min)", gridcolor=C_GRID, zeroline=False),
    ))
    return fig


# ==============================================================================
# 4b. MOTION HELPER (scroll reveal + KPI count-up)
# ==============================================================================
MOTION_JS = r"""
(function () {
  var host = window.parent && window.parent !== window ? window.parent : window;
  var doc = host.document;
  if (host.__lgMotion) return;
  host.__lgMotion = true;
  if (host.matchMedia && host.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var io = new host.IntersectionObserver(function (entries) {
    var i = 0;
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.style.transitionDelay = (i++ * 90) + 'ms';
      e.target.classList.add('lg-in');
      io.unobserve(e.target);
    });
  }, { threshold: 0.12 });

  function ease(t) { return 1 - Math.pow(1 - t, 3); }
  function fmt(v, d) { return v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d }); }

  function countUp(el) {
    var target = parseFloat(el.getAttribute('data-count'));
    if (isNaN(target) || el.getAttribute('data-lg-done') === String(target)) return;
    var node = el.firstChild;
    if (!node || node.nodeType !== 3) return;
    var from = parseFloat(el.getAttribute('data-lg-shown') || '0') || 0;
    var dec = parseInt(el.getAttribute('data-dec') || '0', 10);
    var suf = el.getAttribute('data-suf') || '';
    var delay = el.getAttribute('data-lg-shown') ? 0 : 450;
    el.setAttribute('data-lg-done', String(target));
    var t0 = null;
    function step(ts) {
      if (t0 === null) t0 = ts + delay;
      var p = Math.min(Math.max((ts - t0) / 1300, 0), 1);
      var v = from + (target - from) * ease(p);
      node.nodeValue = fmt(v, dec) + suf;
      if (p < 1) host.requestAnimationFrame(step); else el.setAttribute('data-lg-shown', String(target));
    }
    host.requestAnimationFrame(step);
  }

  function scan() {
    doc.querySelectorAll('[class*="st-key-card"]:not([data-lg-r]), [data-testid="stPlotlyChart"]:not([data-lg-r])')
      .forEach(function (el) { el.setAttribute('data-lg-r', '1'); io.observe(el); });
    doc.querySelectorAll('.kpi-n[data-count]').forEach(countUp);
  }

  var queued = false;
  new host.MutationObserver(function () {
    if (queued) return;
    queued = true;
    host.requestAnimationFrame(function () { queued = false; scan(); });
  }).observe(doc.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-count'] });

  scan();
  doc.documentElement.classList.add('lg-js');
})();
"""


def inject_motion():
    """Runs the small JS helper once per browser session (it guards against running twice)."""
    try:
        st.html(f"<script>{MOTION_JS}</script>", unsafe_allow_javascript=True)
    except TypeError:
        components.html(f"<script>{MOTION_JS}</script>", height=0)


# ==============================================================================
# 5. UI PIECES
# ==============================================================================
def truck_scene() -> str:
    """Animated delivery-truck scene (pure SVG + CSS): the truck bounces, wheels spin,
    and skyline / trees / road scroll past. No image file needed."""
    skyline = [(4, 22, 26), (30, 16, 38), (50, 26, 30), (80, 14, 44), (98, 24, 28), (126, 18, 36), (148, 28, 24),
               (180, 16, 40), (200, 22, 30), (226, 26, 22), (256, 14, 42), (274, 24, 32), (302, 18, 26),
               (324, 26, 38), (354, 16, 28), (374, 24, 44), (402, 20, 30), (426, 28, 24), (458, 16, 36), (478, 24, 28), (506, 10, 20)]
    trees = [30, 95, 150, 230, 300, 372, 440, 495]

    def far(dx):
        return "".join(f'<rect x="{x + dx}" y="{62 - h}" width="{w}" height="{h}" rx="2" fill="#CFE9E2"/>' for x, w, h in skyline)

    def near(dx):
        out = ""
        for x in trees:
            out += (f'<rect x="{x + dx - 1}" y="50" width="2.4" height="12" fill="#5E9C8C"/>'
                    f'<circle cx="{x + dx}" cy="46" r="7" fill="#7CCFB0"/><circle cx="{x + dx + 3}" cy="43" r="4.5" fill="#9BE0C6"/>')
        return out

    def wheel(cx):
        return (f'<g class="ts-wheel"><circle cx="{cx}" cy="57" r="7" fill="#0B3B38"/>'
                f'<circle cx="{cx}" cy="57" r="3.2" fill="#DDF4EF"/>'
                f'<path d="M{cx - 6} 57H{cx + 6}M{cx} 51V63" stroke="#DDF4EF" stroke-width="1.2"/></g>')

    return clean_html(f"""
    <svg class="truck-scene" viewBox="0 0 520 70" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Delivery truck driving">
      <g class="ts-far">{far(0)}{far(520)}</g>
      <g class="ts-near">{near(0)}{near(520)}</g>
      <line class="ts-road" x1="0" y1="66" x2="520" y2="66" stroke="#0E7C66" stroke-width="2" stroke-dasharray="14 14" opacity=".55"/>
      <line x1="0" y1="64.2" x2="520" y2="64.2" stroke="#9CCFC4" stroke-width="1.2"/>
      <g>
        <line class="ts-streak" x1="190" y1="30" x2="212" y2="30" stroke="#0E7C66" stroke-width="2" stroke-linecap="round"/>
        <line class="ts-streak b" x1="184" y1="40" x2="210" y2="40" stroke="#34C08F" stroke-width="2" stroke-linecap="round"/>
        <line class="ts-streak c" x1="192" y1="49" x2="212" y2="49" stroke="#0E7C66" stroke-width="2" stroke-linecap="round"/>
      </g>
      <g class="ts-truck">
        <rect x="215" y="14" width="86" height="38" rx="3" fill="#0B8A74"/>
        <rect x="215" y="14" width="86" height="6" rx="3" fill="#10B981"/>
        <text x="258" y="38" text-anchor="middle" font-family="Roboto, Arial, sans-serif" font-size="10" font-weight="700" fill="#FFFFFF">LogiSight</text>
        <path d="M301 22h20l13 15v15h-33z" fill="#10B981"/>
        <path d="M306 27h13l8 10h-21z" fill="#DDFFF4"/>
        <rect x="213" y="50" width="124" height="5" rx="2" fill="#064E45"/>
        <circle cx="333" cy="46" r="2" fill="#FDE68A"/>
        {wheel(236)}{wheel(272)}{wheel(321)}
      </g>
    </svg>""")


def truck_scene_photo(truck_b64: str) -> str:
    """Your own truck artwork (assets/truck.png, cut from banner.png) as a moving object:
    it rocks on the road, wheels spin, scenery scrolls past, speed lines trail behind."""
    W = 760
    buildings = [(10, 34, 52), (52, 26, 74), (86, 40, 46), (134, 30, 66), (172, 36, 40), (216, 28, 78), (252, 40, 50),
                 (300, 30, 62), (338, 38, 44), (384, 28, 70), (420, 42, 52), (470, 30, 80), (508, 36, 46),
                 (552, 28, 64), (588, 40, 54), (636, 30, 72), (674, 38, 44), (720, 28, 58)]
    trees = [(30, 1), (118, 0), (196, 1), (290, 0), (366, 1), (452, 0), (540, 1), (626, 0), (700, 1)]

    def far(dx):
        return "".join(f'<rect x="{x + dx}" y="{150 - h}" width="{w}" height="{h}" rx="8" fill="#E1F7F0"/>' for x, w, h in buildings)

    def near(dx):
        o = ""
        for x, kind in trees:
            X = x + dx
            if kind:   # lollipop tree
                o += (f'<rect x="{X - 1.5}" y="124" width="3" height="26" rx="1.5" fill="#0E6B5C"/>'
                      f'<rect x="{X - 13}" y="92" width="26" height="40" rx="13" fill="#8FE3CD"/>')
            else:      # bush
                o += (f'<circle cx="{X}" cy="140" r="10" fill="#7DDAC0"/><circle cx="{X + 11}" cy="136" r="13" fill="#6FD3B9"/>'
                      f'<circle cx="{X + 24}" cy="141" r="9" fill="#7DDAC0"/>')
        return o

    def wheel(cx, cy):
        dots = "".join(
            f'<circle cx="{cx + 14.2 * math.cos(k * 1.0472):.2f}" cy="{cy + 14.2 * math.sin(k * 1.0472):.2f}" r="1.7" fill="#5FE0C0"/>'
            for k in range(6))
        return f'<g class="t2-wheel">{dots}</g>'

    S = 0.475
    tx, ty = 205, 27
    wheels = "".join(wheel(tx + wx * S, ty + wy * S) for wx, wy in [(97, 212), (570, 212), (760, 212)])
    return clean_html(f"""
    <svg class="truck-scene2" viewBox="0 0 {W} 170" role="img" aria-label="LogiSight delivery truck driving">
      <g class="t2-far"><g transform="translate(-{W} 0)">{far(0)}</g>{far(0)}</g>
      <g class="t2-near"><g transform="translate(-{W} 0)">{near(0)}</g>{near(0)}</g>
      <rect x="0" y="146" width="{W}" height="8" fill="#CDF1E6" opacity=".7"/>
      <line x1="4" y1="150" x2="{W - 4}" y2="150" stroke="#06A68C" stroke-width="4" stroke-linecap="round"/>
      <line class="t2-road" x1="0" y1="161" x2="{W}" y2="161" stroke="#7FD8C2" stroke-width="2.4" stroke-dasharray="18 18" stroke-linecap="round"/>
      <g>
        <line class="t2-streak" x1="640" y1="70" x2="662" y2="70" stroke="#34C08F" stroke-width="2.4" stroke-linecap="round"/>
        <line class="t2-streak b" x1="648" y1="92" x2="676" y2="92" stroke="#0E7C66" stroke-width="2.4" stroke-linecap="round"/>
        <line class="t2-streak c" x1="640" y1="114" x2="660" y2="114" stroke="#34C08F" stroke-width="2.4" stroke-linecap="round"/>
      </g>
      <g class="t2-truck">
        <image href="data:image/png;base64,{truck_b64}" x="{tx}" y="{ty}" width="{903 * S:.1f}" height="{258 * S:.1f}"/>
        {wheels}
      </g>
    </svg>""")


def banner_scene(bg_b64: str, truck_b64: str) -> str:
    """Your banner artwork (assets/banner_bg.png = banner with the truck removed) with the
    truck (assets/truck.png) driving across it in an endless loop, wheels turning."""
    TX, TY = 797, 14                      # truck position in banner pixels (crop 2172 x 284)
    wheels = ""
    for wx, wy in [(97, 212), (570, 212), (760, 212)]:
        cx, cy = TX + wx, TY + wy
        dots = "".join(f'<circle cx="{cx + 30 * math.cos(k * math.pi / 3):.1f}" cy="{cy + 30 * math.sin(k * math.pi / 3):.1f}" r="3.8" fill="#5FE0C0"/>'
                       for k in range(6))
        wheels += f'<g class="b-wheel">{dots}</g>'
    return clean_html(f"""
    <svg class="banner-scene" viewBox="0 0 2172 284" role="img" aria-label="LogiSight truck driving along the road">
      <image href="data:image/png;base64,{bg_b64}" x="0" y="0" width="2172" height="284"/>
      <line class="b-dash" x1="0" y1="281" x2="2172" y2="281" stroke="#7FD8C2" stroke-width="5" stroke-dasharray="60 50" stroke-linecap="round" opacity=".8"/>
      <g class="b-drive"><g class="b-rock">
        <image href="data:image/png;base64,{truck_b64}" x="{TX}" y="{TY}" width="903" height="258"/>
        {wheels}
        <g>
          <line class="b-streak" x1="1716" y1="92" x2="1776" y2="92" stroke="#34C08F" stroke-width="6" stroke-linecap="round"/>
          <line class="b-streak b" x1="1724" y1="140" x2="1800" y2="140" stroke="#0E7C66" stroke-width="6" stroke-linecap="round"/>
          <line class="b-streak c" x1="1716" y1="188" x2="1766" y2="188" stroke="#34C08F" stroke-width="6" stroke-linecap="round"/>
        </g>
      </g></g>
    </svg>""")


def render_header():
    banner = img_b64("banner.png")
    wacp = img_b64("wacp.png", "wacp_design.png")
    viraj = img_b64("viraj.png", "viraj_design.png")
    wtag = f'<img src="data:image/png;base64,{wacp}" alt="WACP">' if wacp else "<b>WACP</b>"
    vtag = f'<img src="data:image/png;base64,{viraj}" alt="Viraj">' if viraj else "<b>VIRAJ</b>"
    truck_png, bg_png = img_b64("truck.png"), img_b64("banner_bg.png")
    if truck_png and bg_png:
        btag = banner_scene(bg_png, truck_png)            # your banner artwork, truck driving in a loop
    elif truck_png:
        btag = truck_scene_photo(truck_png)
    else:
        btag = truck_scene()                              # built-in vector truck if no assets
    st.markdown(clean_html(f"""
        <div class="hdr">
            <div><div class="hdr-t">LogiSight Analytics</div>
                 <div class="hdr-s">Last-Mile Delivery Performance Dashboard</div></div>
            <div class="hdr-banner">{btag}</div>
            <div class="hdr-r">
                <div class="stu">Ankit Pradhan – Roll: 1000390<br>Mathematics for AI-II (FA-2)</div>
                <div class="logo">{wtag}</div><div class="logo">{vtag}</div>
            </div>
        </div>"""), unsafe_allow_html=True)


def kpi_html(icon, icon_color, title, number, caption, late=False, count=None):
    # count = (value, decimals, suffix): the browser counts up to this value
    count_attr = ""
    if count is not None:
        v, dec, suf = count
        count_attr = f'data-count="{v:.6f}" data-dec="{dec}" data-suf="{suf}"'
    return clean_html(f"""
        <div class="kpi {'late' if late else ''}">
            <div class="kpi-ic">{svg(icon, icon_color, 22, 2)}</div>
            <div><div class="kpi-t">{title}</div>
                 <div class="kpi-n" {count_attr} style="color:{icon_color if icon in ('alert', 'check') else C_TITLE};">{number}</div>
                 <div class="kpi-c">{caption}</div></div>
        </div>""")


def render_kpis(f, meta, filtered):
    n = len(f)
    avg = f["Delivery_Time"].mean()
    late = int(f["Is_Late"].sum())
    late_pct = late / n * 100
    cols = st.columns(4)
    diff = avg - meta["mean"]
    avg_cap = "At fleet baseline" if not filtered else f"{diff:+.1f} min vs fleet baseline ({meta['mean']:.1f})"
    cols[0].markdown(kpi_html("truck", C_TITLE, "Total Deliveries", f"{n:,}",
                              f"Across {f['Category'].nunique()} categories &amp; {f['Area'].nunique()} areas",
                              count=(n, 0, "")), unsafe_allow_html=True)
    cols[1].markdown(kpi_html("timer", C_TITLE, "Avg. Delivery Time", f"{avg:.1f} min", avg_cap,
                              count=(avg, 1, " min")), unsafe_allow_html=True)
    cols[2].markdown(kpi_html("alert", C_RED, "Late Deliveries", f"{late_pct:.1f}%",
                              f"{late:,} orders exceeding {meta['thresh']:.1f} min", late=True,
                              count=(late_pct, 1, "%")), unsafe_allow_html=True)
    cols[3].markdown(kpi_html("check", C_GREEN, "On-Time Fulfillment", f"{100 - late_pct:.1f}%",
                              f"{n - late:,} orders within threshold",
                              count=(100 - late_pct, 1, "%")), unsafe_allow_html=True)


def title(text, sub=None, big=False):
    s = f'<div class="ct-sub">{sub}</div>' if sub else ""
    st.markdown(f'<div class="{"ct-big" if big else "ct"}">{text}</div>{s}', unsafe_allow_html=True)


def fleet_table(f):
    g = f.groupby("Vehicle", observed=True).agg(avg=("Delivery_Time", "mean"), n=("Order_ID", "count"),
                                                 late=("Is_Late", "sum")).reset_index().sort_values("avg")
    fastest = g["avg"].min()
    rows = "".join(
        f"<tr><td>{r.Vehicle}</td><td>{r.avg:.1f}</td><td>{int(r.n):,}</td><td>{int(r.late):,}</td>"
        f"<td>{r.late / r.n * 100:.1f}</td><td>{r.avg - fastest:.1f}</td></tr>" for r in g.itertuples())
    st.markdown(clean_html(f"""<table class="lg-tbl"><thead><tr><th>Vehicle Modality</th><th>Avg Delivery Time (min)</th>
        <th>Total Orders</th><th>Late Orders</th><th>Late Rate (%)</th><th>Delta vs Fastest (min)</th></tr></thead>
        <tbody>{rows}</tbody></table>"""), unsafe_allow_html=True)


def cohort_table(f):
    rows = ""
    for grp in AGE_ORDER:
        s = f[f["Agent_Age_Group"] == grp]
        if len(s):
            valid = s.loc[s["Agent_Rating"] <= 5, "Agent_Rating"]      # ratings above 5 are invalid on a 1-5 scale
            rating_txt = f"{valid.mean():.2f}" if len(valid) else "n/a*"
            rows += (f"<tr><td>{grp}</td><td>{len(s):,}</td><td>{rating_txt}</td>"
                     f"<td>{s['Delivery_Time'].mean():.1f}</td><td>{s['Is_Late'].mean() * 100:.1f}</td></tr>")
        else:
            rows += f"<tr><td>{grp}</td><td>0</td><td>–</td><td>–</td><td>–</td></tr>"
    st.markdown(clean_html(f"""<table class="lg-tbl coh"><thead><tr><th>Age Group</th><th>Orders</th><th>Avg Rating</th>
        <th>Avg Delivery Time (min)</th><th>Late Rate (%)</th></tr></thead><tbody>{rows}</tbody></table>"""),
        unsafe_allow_html=True)


# ==============================================================================
# 6. PAGES
# ==============================================================================
def page_delivery(f):
    c1, c2 = st.columns([1.55, 1])
    with c1:
        with st.container(key="card_delay"):
            title("Delay Analyzer: Weather &amp; Traffic Impact")
            show(delay_chart(f))
    with c2:
        with st.container(key="card_vehicle"):
            title("Vehicle Comparison: Avg. Delivery Time")
            show(vehicle_chart(f))

    c1, c2, c3 = st.columns([1.1, 1, 1.1])
    with c1:
        with st.container(key="card_scatter"):
            title("Agent Performance: Rating vs Delivery Time")
            show(scatter_chart(f, 270))
    with c2:
        with st.container(key="card_heat"):
            title("Area Heatmap: Avg Delivery Time (min)")
            show(heatmap_chart(f, 270, compact=True))
    with c3:
        with st.container(key="card_box"):
            title("Category Visualizer: Delivery Time Distribution")
            show(box_chart(f, 270))

    with st.container(key="card_fleet"):
        title("Fleet Modality Performance Breakdown")
        fleet_table(f)


def page_agent(f, meta):
    with st.container(key="card_outer_agent"):
        title("Agent Performance &amp; Workforce Distribution",
              "Correlation between agent ratings, delivery time, and age groups", big=True)
        c1, c2 = st.columns([1.35, 1])
        with c1:
            with st.container(key="card_in_scatter"):
                show(scatter_chart(f, 400, sample=4000))
                if meta["rating_over_5"]:
                    st.markdown(f'<div class="note">Records with Agent_Rating above 5 ({meta["rating_over_5"]}) are not plotted '
                                f"(invalid on a 1–5 scale). All other records are used for the trendline.</div>", unsafe_allow_html=True)
        with c2:
            with st.container(key="card_in_cohort"):
                title("Workforce Cohort Statistics")
                cohort_table(f)
                if meta["raw_over40"] and meta["clean_over40"] == 0:
                    st.markdown(f'<div class="note">* The raw file has {meta["raw_over40"]} orders by agents aged 40+, but each one '
                                f"had missing Weather/Traffic values, so cleaning removed them and no 40+ records remain.</div>",
                                unsafe_allow_html=True)


def page_regional(f):
    with st.container(key="card_outer_regional"):
        title("Geographic &amp; Product Line Logistics Analysis",
              "Cross-zonal delay heatmap and delivery time distribution across product categories", big=True)
        c1, c2 = st.columns(2)
        with c1:
            with st.container(key="card_in_heat"):
                title("Area Heatmap: Avg Delivery Time (min)")
                show(heatmap_chart(f, 340))
        with c2:
            with st.container(key="card_in_box"):
                title("Category Visualizer: Delivery Time Distribution")
                show(box_chart(f, 340))


def page_prep(meta):
    d = meta["drops"]
    with st.container(key="card_outer_prep"):
        title("Stage 4: Data Cleaning, Preparation &amp; Methodology",
              "Documented analytical audit trail per Formative Assessment-2 rubric guidelines", big=True)
        c1, c2 = st.columns(2)
        with c1:
            with st.container(key="card_in_formula"):
                title("Late Delivery Mathematical Formulation")
                st.markdown(clean_html(f"""
                    <p class="para" style="font-size:14.5px;">A delivery is formally classified as late when its fulfillment
                    duration exceeds one standard deviation above the mean:</p>
                    <div class="formula">Late_Threshold = Mean(Delivery_Time) + 1 × StdDev(Delivery_Time)</div>
                    <ul class="blist">
                      <li>Sample Size (N): {meta['clean']:,} clean deliveries</li>
                      <li>Fleet Mean (μ): {meta['mean']:.1f} minutes</li>
                      <li>Population StdDev (σ): {meta['std']:.2f} minutes</li>
                      <li>Calculated Threshold: {meta['thresh']:.1f} minutes</li>
                      <li>Total Late Deliveries: {meta['late']:,} ({meta['late_pct']:.1f}%)</li>
                    </ul><div style="height:10px"></div>"""), unsafe_allow_html=True)
        with c2:
            with st.container(key="card_in_audit"):
                title("Data Cleaning Audit Trail")
                st.markdown(clean_html(f"""
                    <table class="audit">
                      <tr><td>Raw Records Loaded:</td><td>{meta['raw']:,}</td></tr>
                      <tr><td>Duplicate Order IDs Found:</td><td>{meta['duplicates']:,}</td></tr>
                      <tr><td>Missing Weather Dropped:</td><td>-{d['weather']:,}</td></tr>
                      <tr><td>Further Missing Traffic Dropped:</td><td>-{d['traffic']:,}</td></tr>
                      <tr><td>Missing Rating Dropped:</td><td>-{d['rating']:,}</td></tr>
                      <tr><td>Area Spelling Corrected (Metropolitian):</td><td>{meta['spelling_fixed']:,}</td></tr>
                      <tr class="tot"><td>Clean Verified Records:</td><td>{meta['clean']:,} ({meta['clean'] / meta['raw'] * 100:.2f}%)</td></tr>
                    </table>"""), unsafe_allow_html=True)


def page_about():
    c1, c2 = st.columns(2)
    with c1:
        with st.container(key="card_about1"):
            st.markdown(clean_html(f"""
                <div class="ic-row"><div class="ic-circ">{svg('home', C_TITLE, 22)}</div><div class="ct-big">Project Overview</div></div>
                <div class="ct" style="font-size:20px;margin:14px 0 8px 0;">About LogiSight Analytics – FA-2 Project</div>
                <p class="para">This analytics platform fulfills all requirements of the FA-2 assignment brief: transforming the
                FA-1 design storyboard and data flow diagram into a fully responsive, real-time Streamlit analytics website.
                Every visual, KPI card, and table dynamically computes from the verified last-mile delivery dataset using
                Python, Pandas, and Plotly.</p><div style="height:10px"></div>"""), unsafe_allow_html=True)
    with c2:
        with st.container(key="card_about2"):
            st.markdown(clean_html(f"""
                <div class="ic-row"><div class="ic-circ">{svg('truck', C_TITLE, 22)}</div><div class="ct-big">Project Details</div></div>
                <div class="dl-k">Course:</div><div class="dl-v">Mathematics for AI-II (CRS-AI FA-2)</div>
                <div class="dl-k">Student:</div><div class="dl-v">Ankit Pradhan (Roll Number: 1000390)</div>
                <div class="dl-k">Corporate Role:</div><div class="dl-v">Senior Logistics Data Analyst at LogiSight Analytics Pvt. Ltd.</div>
                <div class="dl-k">Academic Partner:</div><div class="dl-v">Westcliff Academic Partner (WACP) &amp; Viraj International</div>
                <div style="height:14px"></div>"""), unsafe_allow_html=True)


# ==============================================================================
# 7. MAIN
# ==============================================================================
def main():
    df, meta = load_data()

    ss = st.session_state
    ss.setdefault("page", NAV[0][0])
    for key, _, _ in FILTERS:
        ss.setdefault(f"f_{key}", "All")

    def go_page(name):
        ss["page"] = name

    def apply_filters():
        for key, _, _ in FILTERS:
            ss[f"f_{key}"] = ss.get(f"w_{key}", "All")

    def reset_filters():
        for key, _, _ in FILTERS:
            ss[f"f_{key}"] = "All"
            ss[f"w_{key}"] = "All"

    _CHART_N[0] = 0
    inject_css(ss["page"])
    inject_motion()

    with st.sidebar:
        st.markdown(clean_html(f"""
            <div class="brand"><div class="brand-ic">{svg('truck', '#FFFFFF', 26)}</div>
            <div><div class="brand-t">LogiSight<br>Analytics</div>
            <div class="brand-s">Operational Intelligence System</div></div></div>
            <div class="nav-h">NAVIGATION</div>"""), unsafe_allow_html=True)

        with st.container(key="navwrap"):
            for i, (label, _) in enumerate(NAV):
                if _supports_width():
                    st.button(label, key=f"nav_{i}", on_click=go_page, args=(label,), width="stretch")
                else:
                    st.button(label, key=f"nav_{i}", on_click=go_page, args=(label,), use_container_width=True)

        st.markdown(clean_html(f"""<div class="sb-sep"></div>
            <div class="flt-h">{svg('filter', '#FFFFFF', 20)}<span>Global Filters</span></div>"""), unsafe_allow_html=True)

        for key, label, col in FILTERS:
            opts = ["All"] + sorted(df[col].dropna().unique().tolist())
            if col == "Traffic":
                opts = ["All"] + [t for t in TRAFFIC_ORDER if t in set(df[col])]
            if ss.get(f"w_{key}") not in opts:
                ss[f"w_{key}"] = ss[f"f_{key}"] if ss[f"f_{key}"] in opts else "All"
            with st.container(key=f"frow_{key}"):
                a, b = st.columns([1, 1.25])
                a.markdown(f'<div class="flt-l">{label}</div>', unsafe_allow_html=True)
                b.selectbox(label, opts, key=f"w_{key}", label_visibility="collapsed")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if _supports_width():
            st.button("Apply Filters", key="btn_apply", on_click=apply_filters, width="stretch")
            st.button("Reset", key="btn_reset", on_click=reset_filters, width="stretch")
        else:
            st.button("Apply Filters", key="btn_apply", on_click=apply_filters, use_container_width=True)
            st.button("Reset", key="btn_reset", on_click=reset_filters, use_container_width=True)

    # Apply committed filters
    f = df
    filtered = False
    for key, _, col in FILTERS:
        v = ss[f"f_{key}"]
        if v != "All":
            f = f[f[col] == v]
            filtered = True

    render_header()

    if len(f) == 0:
        st.warning("No delivery records match the current filters. Click Reset to restore the full dataset.")
        st.stop()

    render_kpis(f, meta, filtered)

    page = ss["page"]
    if page == "Delivery Analysis":
        page_delivery(f)
    elif page == "Agent Performance":
        page_agent(f, meta)
    elif page == "Regional & Category":
        page_regional(f)
    elif page == "Data Preparation":
        page_prep(meta)
    else:
        page_about()


def _supports_width() -> bool:
    """st.button(width=...) exists only in newer Streamlit; older versions use use_container_width."""
    import inspect
    return "width" in inspect.signature(st.button).parameters


if __name__ == "__main__":
    main()