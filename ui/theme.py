"""
Enterprise UI Theme System
Professional design palette and styling for GigShield AI
"""
import streamlit as st
from config.settings import COLORS


def apply_custom_theme():
    """Apply custom enterprise theme to Streamlit app."""
    
    # Custom CSS for professional styling
    st.markdown(f"""
    <style>
        /* Primary Colors */
        :root {{
            --primary: {COLORS['primary']};
            --secondary: {COLORS['secondary']};
            --accent: {COLORS['accent']};
            --success: {COLORS['success']};
            --warning: {COLORS['warning']};
            --error: {COLORS['error']};
            --background: {COLORS['background']};
            --surface: {COLORS['surface']};
            --text-primary: {COLORS['text_primary']};
            --text-secondary: {COLORS['text_secondary']};
        }}

        /* Main App Styling */
        .main {{
            background-color: {COLORS['background']};
            color: {COLORS['text_primary']};
        }}

        /* Headers */
        h1 {{
            color: {COLORS['primary']};
            font-weight: 700;
            margin-bottom: 1.5rem;
            border-bottom: 3px solid {COLORS['accent']};
            padding-bottom: 0.5rem;
        }}

        h2 {{
            color: {COLORS['primary']};
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }}

        h3 {{
            color: {COLORS['secondary']};
            font-weight: 600;
            margin-top: 1rem;
        }}

        /* Cards & Containers */
        .card {{
            background-color: {COLORS['surface']};
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid #e5e7eb;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }}

        /* Sidebar */
        .css-1lcbmhc {{
            background-color: {COLORS['surface']};
        }}

        /* Buttons */
        .stButton > button {{
            background-color: {COLORS['primary']};
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
        }}

        .stButton > button:hover {{
            background-color: {COLORS['secondary']};
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}

        /* Input Fields */
        .stTextInput, .stNumberInput, .stSelectbox, .stSlider {{
            border-radius: 8px;
        }}

        /* Metrics Display */
        .metric-container {{
            background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 1rem;
        }}

        .metric-value {{
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0.5rem 0;
        }}

        .metric-label {{
            font-size: 0.9rem;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* Status Badges */
        .badge {{
            display: inline-block;
            padding: 0.4rem 0.8rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin: 0.25rem;
        }}

        .badge-success {{
            background-color: #d1fae5;
            color: #065f46;
        }}

        .badge-warning {{
            background-color: #fef3c7;
            color: #92400e;
        }}

        .badge-error {{
            background-color: #fee2e2;
            color: #741c21;
        }}

        .badge-info {{
            background-color: #dbeafe;
            color: #1e40af;
        }}

        /* Tables */
        table {{
            border-collapse: collapse;
            width: 100%;
            font-size: 0.9rem;
        }}

        thead {{
            background-color: {COLORS['primary']};
            color: white;
        }}

        tbody tr {{
            border-bottom: 1px solid #e5e7eb;
        }}

        tbody tr:hover {{
            background-color: {COLORS['background']};
        }}

        td, th {{
            padding: 0.75rem;
            text-align: left;
        }}

        /* Alert Boxes */
        .alert {{
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1rem;
            border-left: 4px solid;
        }}

        .alert-success {{
            background-color: #f0fdf4;
            border-left-color: {COLORS['success']};
            color: #166534;
        }}

        .alert-warning {{
            background-color: #fffbeb;
            border-left-color: {COLORS['warning']};
            color: #78350f;
        }}

        .alert-error {{
            background-color: #fef2f2;
            border-left-color: {COLORS['error']};
            color: #7f1d1d;
        }}

        .alert-info {{
            background-color: #f0f9ff;
            border-left-color: {COLORS['accent']};
            color: #0c2d48;
        }}

        /* Dividers */
        hr {{
            border: none;
            border-top: 2px solid {COLORS['accent']};
            margin: 2rem 0;
            opacity: 0.3;
        }}

        /* Footer */
        .footer {{
            text-align: center;
            color: {COLORS['text_secondary']};
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #e5e7eb;
            font-size: 0.85rem;
        }}
    </style>
    """, unsafe_allow_html=True)


def get_color(color_name: str) -> str:
    """
    Get color by name.

    Args:
        color_name: Color name

    Returns:
        HEX color code
    """
    return COLORS.get(color_name, COLORS['primary'])


def style_metric_card(label: str, value: str, delta: str = None,
                      help_text: str = None) -> None:
    """
    Display a styled metric card.

    Args:
        label: Metric label
        value: Metric value
        delta: Optional change indicator
        help_text: Optional tooltip text
    """
    with st.container():
        col1, col2 = st.columns([3, 1]) if help_text else (st.columns([1]), None)

        st.markdown(f"""
        <div class="card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            {f'<div style="font-size: 0.85rem; color: {COLORS["text_secondary"]};">{delta}</div>' if delta else ''}
        </div>
        """, unsafe_allow_html=True)


def success_box(title: str, message: str) -> None:
    """Display success alert box."""
    st.markdown(f"""
    <div class="alert alert-success">
        <strong>{title}</strong><br>
        {message}
    </div>
    """, unsafe_allow_html=True)


def warning_box(title: str, message: str) -> None:
    """Display warning alert box."""
    st.markdown(f"""
    <div class="alert alert-warning">
        <strong>⚠️ {title}</strong><br>
        {message}
    </div>
    """, unsafe_allow_html=True)


def error_box(title: str, message: str) -> None:
    """Display error alert box."""
    st.markdown(f"""
    <div class="alert alert-error">
        <strong>❌ {title}</strong><br>
        {message}
    </div>
    """, unsafe_allow_html=True)


def info_box(title: str, message: str) -> None:
    """Display info alert box."""
    st.markdown(f"""
    <div class="alert alert-info">
        <strong>ℹ️ {title}</strong><br>
        {message}
    </div>
    """, unsafe_allow_html=True)


def badge(text: str, badge_type: str = "info") -> None:
    """
    Display a styled badge.

    Args:
        text: Badge text
        badge_type: Type of badge (success, warning, error, info)
    """
    st.markdown(f'<span class="badge badge-{badge_type}">{text}</span>',
                unsafe_allow_html=True)
