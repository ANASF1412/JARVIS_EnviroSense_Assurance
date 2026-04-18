import streamlit as st
import json

def get_theme_palette(theme_mode="dark"):
    if theme_mode == "dark":
        return {
            "background": "#0e1117",
            "surface": "#1e2127",
            "border": "#31353f",
            "text_primary": "#f8f9fa",
            "text_secondary": "#abb2bf",
            "success": "#22c55e",
            "warning": "#f59e0b",
            "error": "#ef4444",
            "accent": "#4f46e5"
        }
    else:
        return {
            "background": "#f8f9fa",
            "surface": "#ffffff",
            "border": "#e5e7eb",
            "text_primary": "#111827",
            "text_secondary": "#6b7280",
            "success": "#16a34a",
            "warning": "#d97706",
            "error": "#dc2626",
            "accent": "#4338ca"
        }

def inject_theme_css(theme_mode="dark"):
    """Inject fully defined theme CSS based on light/dark mode."""
    colors = get_theme_palette(theme_mode)

    st.markdown(f"""
<style>
/* Base Streamlit App Level Variables (Trying to override generic elements) */
:root {{
    --primary: {colors['accent']};
    --background: {colors['background']};
    --surface: {colors['surface']};
    --border: {colors['border']};
    --text-primary: {colors['text_primary']};
    --text-secondary: {colors['text_secondary']};
    --success: {colors['success']};
    --warning: {colors['warning']};
    --danger: {colors['error']};
}}

/* App Containers */
.stApp, .main {{
    background-color: var(--background) !important;
    color: var(--text-primary) !important;
}}

/* Sidebar styling to match theme */
[data-testid="stSidebar"] {{
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}}

/* Typography overrides */
h1, h2, h3, h4, h5, p, span, div {{
    color: var(--text-primary);
}}

.stMarkdown p, .stMarkdown span {{
    color: var(--text-primary) !important;
}}

/* Fixed Metric Cards */
.theme-card {{
    background-color: var(--surface);
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid var(--border);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}}

.theme-card-label {{
    font-size: 0.85rem;
    text-transform: uppercase;
    font-weight: 600;
    color: var(--text-secondary);
    letter-spacing: 0.5px;
}}

.theme-card-value {{
    font-size: 2.2rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.1;
}}

.theme-card-subtext {{
    font-size: 0.85rem;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 5px;
}}

/* Buttons & UI Controls */
div.stButton > button {{
    background-color: var(--surface) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    transition: all 0.2s ease;
}}

div.stButton > button:hover {{
    border-color: var(--primary) !important;
    color: var(--primary) !important;
}}

div.stButton > button[data-testid="baseButton-primary"] {{
    background-color: var(--primary) !important;
    color: white !important;
    border: none !important;
}}

/* Old Card Backward compatibility */
.card {{
    background-color: var(--surface);
    border-radius: 12px;
    padding: 1.5rem;
    border: 1px solid var(--border);
    margin-bottom: 1rem;
}}
.metric-label {{ font-size: 0.9rem; color: var(--text-secondary); text-transform: uppercase; }}
.metric-value {{ font-size: 2rem; font-weight: bold; color: var(--text-primary); }}

/* Extracted explicit styles from Streamlit components to fix standard white boxes */
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{
    color: var(--text-primary) !important;
}}
[data-testid="stMetric"] {{
    background-color: var(--surface) !important;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
}}

/* Force Input Backgrounds and Text Colors */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > input,
div[data-baseweb="textarea"] > textarea,
div[data-testid="stChatInput"] textarea {{
    background-color: var(--background) !important;
    color: var(--text-primary) !important;
    border-color: var(--border) !important;
}}

div[data-baseweb="select"] ul {{
    background-color: var(--surface) !important;
    color: var(--text-primary) !important;
}}

div[data-baseweb="select"] li {{
    color: var(--text-primary) !important;
    background-color: var(--surface) !important;
}}

/* Streamlit expander and messages */
details[data-testid="stExpanderDetails"], details[data-testid="stExpanderDetails"] summary {{
    background-color: var(--surface) !important;
    color: var(--text-primary) !important;
}}

div[data-testid="stChatMessage"] {{
    background-color: var(--surface) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px;
}}

/* Status Badges */
.badge {{
    display: inline-block;
    padding: 0.4rem 0.8rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    margin: 0.25rem;
    background-color: var(--surface);
    border: 1px solid var(--border);
    color: var(--text-primary);
}}
.badge-success {{ color: var(--success); border-color: var(--success); }}
.badge-warning {{ color: var(--warning); border-color: var(--warning); }}
.badge-error {{ color: var(--danger); border-color: var(--danger); }}
.badge-info {{ color: var(--primary); border-color: var(--primary); }}

/* Alerts */
.alert {{
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    border-left: 4px solid;
    background-color: var(--surface);
    color: var(--text-primary);
}}
.alert-success {{ border-left-color: var(--success); }}
.alert-warning {{ border-left-color: var(--warning); }}
.alert-error {{ border-left-color: var(--danger); }}
.alert-info {{ border-left-color: var(--primary); }}

hr {{ border-top: 1px solid var(--border); opacity: 0.5; }}
</style>
    """, unsafe_allow_html=True)


def style_metric_card(label: str, value: str, delta: str = None, help_text: str = None, text_color: str = None) -> None:
    """Enhanced customizable metric card integrating seamlessly with Light/Dark Mode."""
    c_color = f"color: {text_color};" if text_color else ""
    card_html = f'<div class="theme-card"><div class="theme-card-label">{label}</div><div class="theme-card-value" style="{c_color}">{value}</div>'
    if delta:
        card_html += f'<div class="theme-card-subtext">{delta}</div>'
    card_html += '</div>'
    st.markdown(card_html, unsafe_allow_html=True)

def success_box(title: str, message: str) -> None:
    st.markdown(f'<div class="alert alert-success"><strong>{title}</strong><br>{message}</div>', unsafe_allow_html=True)

def warning_box(title: str, message: str) -> None:
    st.markdown(f'<div class="alert alert-warning"><strong>⚠️ {title}</strong><br>{message}</div>', unsafe_allow_html=True)

def error_box(title: str, message: str) -> None:
    st.markdown(f'<div class="alert alert-error"><strong>❌ {title}</strong><br>{message}</div>', unsafe_allow_html=True)

def info_box(title: str, message: str) -> None:
    st.markdown(f'<div class="alert alert-info"><strong>ℹ️ {title}</strong><br>{message}</div>', unsafe_allow_html=True)

def badge(text: str, badge_type: str = "info") -> None:
    st.markdown(f'<span class="badge badge-{badge_type}">{text}</span>', unsafe_allow_html=True)

def apply_custom_theme():
    # Backward compatibility wrap
    if "theme_mode" not in st.session_state:
        st.session_state["theme_mode"] = "dark"
    inject_theme_css(st.session_state["theme_mode"])
