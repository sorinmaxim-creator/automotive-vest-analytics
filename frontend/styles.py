"""
Stiluri CSS globale pentru aplicație
Design modern și profesionist
"""

# Paleta de culori
COLORS = {
    "primary": "#1a365d",      # Albastru închis
    "primary_light": "#2c5282",
    "secondary": "#38a169",    # Verde
    "accent": "#ed8936",       # Portocaliu
    "background": "#f7fafc",
    "surface": "#ffffff",
    "text": "#2d3748",
    "text_light": "#718096",
    "border": "#e2e8f0",
    "success": "#48bb78",
    "warning": "#ecc94b",
    "error": "#f56565",
}

def get_main_css():
    """Returnează CSS-ul principal pentru aplicație"""
    return f"""
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* Global Styles */
        .stApp {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}

        /* Main container */
        .main .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }}

        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%);
            padding-top: 0;
        }}

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
            color: white;
        }}

        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stMultiSelect label {{
            color: rgba(255,255,255,0.9) !important;
        }}

        /* Sidebar navigation items */
        [data-testid="stSidebarNav"] {{
            padding-top: 1rem;
        }}

        [data-testid="stSidebarNav"] > ul {{
            padding-left: 0;
        }}

        [data-testid="stSidebarNav"] li {{
            margin-bottom: 0.25rem;
        }}

        [data-testid="stSidebarNav"] a {{
            color: rgba(255,255,255,0.85) !important;
            padding: 0.6rem 1rem;
            border-radius: 8px;
            transition: all 0.2s ease;
            font-weight: 500;
        }}

        [data-testid="stSidebarNav"] a:hover {{
            background: rgba(255,255,255,0.15);
            color: white !important;
        }}

        [data-testid="stSidebarNav"] a[aria-selected="true"] {{
            background: rgba(255,255,255,0.2);
            color: white !important;
            font-weight: 600;
        }}

        /* Page header styling */
        .page-header {{
            background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%);
            padding: 2rem 2.5rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            color: white;
            box-shadow: 0 4px 20px rgba(26, 54, 93, 0.15);
        }}

        .page-header h1 {{
            margin: 0;
            font-size: 2rem;
            font-weight: 700;
            color: white;
        }}

        .page-header p {{
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
            font-size: 1.1rem;
        }}

        /* Card styling */
        .metric-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            border: 1px solid {COLORS['border']};
            transition: all 0.2s ease;
        }}

        .metric-card:hover {{
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}

        /* Metrics styling */
        [data-testid="stMetric"] {{
            background: white;
            padding: 1.25rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            border: 1px solid {COLORS['border']};
        }}

        [data-testid="stMetricLabel"] {{
            font-weight: 600;
            color: {COLORS['text_light']};
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        [data-testid="stMetricValue"] {{
            font-weight: 700;
            color: {COLORS['primary']};
            font-size: 1.75rem;
        }}

        [data-testid="stMetricDelta"] {{
            font-weight: 600;
        }}

        /* Buttons */
        .stButton > button {{
            border-radius: 8px;
            padding: 0.5rem 1.5rem;
            font-weight: 600;
            transition: all 0.2s ease;
            border: none;
        }}

        .stButton > button[kind="primary"] {{
            background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%);
            color: white;
        }}

        .stButton > button[kind="primary"]:hover {{
            box-shadow: 0 4px 12px rgba(26, 54, 93, 0.3);
            transform: translateY(-1px);
        }}

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.5rem;
            background: {COLORS['background']};
            padding: 0.5rem;
            border-radius: 12px;
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            color: {COLORS['text']};
        }}

        .stTabs [aria-selected="true"] {{
            background: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            color: {COLORS['primary']};
        }}

        /* DataFrames */
        .stDataFrame {{
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid {COLORS['border']};
        }}

        /* Expanders */
        .streamlit-expanderHeader {{
            background: {COLORS['background']};
            border-radius: 8px;
            font-weight: 600;
        }}

        /* Select boxes */
        .stSelectbox > div > div {{
            border-radius: 8px;
            border-color: {COLORS['border']};
        }}

        /* Text inputs */
        .stTextInput > div > div > input {{
            border-radius: 8px;
            border-color: {COLORS['border']};
        }}

        /* Alerts/Info boxes */
        .stAlert {{
            border-radius: 12px;
            border: none;
        }}

        /* Charts container */
        .chart-container {{
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            border: 1px solid {COLORS['border']};
            margin-bottom: 1rem;
        }}

        /* Section headers */
        .section-header {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid {COLORS['border']};
            margin-bottom: 1.5rem;
        }}

        .section-header h3 {{
            margin: 0;
            color: {COLORS['primary']};
            font-weight: 600;
        }}

        /* Info cards */
        .info-card {{
            background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1rem;
        }}

        .info-card h4 {{
            margin: 0 0 0.5rem 0;
            font-weight: 600;
        }}

        .info-card p {{
            margin: 0;
            opacity: 0.9;
        }}

        /* User info in sidebar */
        .user-info {{
            background: rgba(255,255,255,0.1);
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        }}

        .user-info-name {{
            font-weight: 600;
            font-size: 1rem;
            color: white;
        }}

        .user-info-role {{
            font-size: 0.8rem;
            color: rgba(255,255,255,0.7);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        /* Logo container */
        .logo-container {{
            padding: 1.5rem 1rem;
            text-align: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 1rem;
        }}

        .logo-text {{
            font-size: 1.5rem;
            font-weight: 700;
            color: white;
            margin: 0;
        }}

        .logo-subtitle {{
            font-size: 0.75rem;
            color: rgba(255,255,255,0.7);
            margin-top: 0.25rem;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}

        /* Menu group */
        .menu-group {{
            margin-bottom: 1.5rem;
        }}

        .menu-group-title {{
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: rgba(255,255,255,0.5);
            padding: 0 1rem;
            margin-bottom: 0.5rem;
        }}

        /* Stats row */
        .stats-row {{
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
        }}

        /* Footer */
        .app-footer {{
            text-align: center;
            padding: 2rem 0;
            color: {COLORS['text_light']};
            font-size: 0.85rem;
            border-top: 1px solid {COLORS['border']};
            margin-top: 3rem;
        }}

        /* Responsive adjustments */
        @media (max-width: 768px) {{
            .page-header {{
                padding: 1.5rem;
            }}
            .page-header h1 {{
                font-size: 1.5rem;
            }}
        }}
    </style>
    """


def get_sidebar_css():
    """CSS specific pentru sidebar"""
    return f"""
    <style>
        /* Sidebar custom navigation */
        .sidebar-nav {{
            padding: 0 0.5rem;
        }}

        .nav-item {{
            display: flex;
            align-items: center;
            padding: 0.75rem 1rem;
            color: rgba(255,255,255,0.85);
            text-decoration: none;
            border-radius: 8px;
            margin-bottom: 0.25rem;
            transition: all 0.2s ease;
            font-weight: 500;
        }}

        .nav-item:hover {{
            background: rgba(255,255,255,0.15);
            color: white;
        }}

        .nav-item.active {{
            background: rgba(255,255,255,0.2);
            color: white;
        }}

        .nav-icon {{
            margin-right: 0.75rem;
            font-size: 1.1rem;
        }}

        .nav-divider {{
            height: 1px;
            background: rgba(255,255,255,0.1);
            margin: 1rem 0;
        }}
    </style>
    """


def page_header(title, subtitle=None, icon=None):
    """Generează un header de pagină stilizat"""
    icon_html = f'<span style="font-size: 2.5rem; margin-right: 1rem;">{icon}</span>' if icon else ''
    subtitle_html = f'<p>{subtitle}</p>' if subtitle else ''

    return f"""
    <div class="page-header">
        <div style="display: flex; align-items: center;">
            {icon_html}
            <div>
                <h1>{title}</h1>
                {subtitle_html}
            </div>
        </div>
    </div>
    """


def section_header(title, icon=None):
    """Generează un header de secțiune"""
    icon_html = f'<span style="font-size: 1.5rem;">{icon}</span>' if icon else ''
    return f"""
    <div class="section-header">
        {icon_html}
        <h3>{title}</h3>
    </div>
    """


def info_card(title, content, icon=None):
    """Generează un card informativ"""
    icon_html = f'<span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>' if icon else ''
    return f"""
    <div class="info-card">
        <h4>{icon_html}{title}</h4>
        <p>{content}</p>
    </div>
    """


def init_page_style(st_module):
    """
    Inițializează stilurile pentru o pagină.
    Aplică CSS-ul global și sidebar-ul stilizat.

    Utilizare:
        from styles import init_page_style
        init_page_style(st)
    """
    st_module.markdown(get_main_css(), unsafe_allow_html=True)
    st_module.markdown(get_sidebar_css(), unsafe_allow_html=True)


def chart_container(title, icon=None):
    """Generează containerul pentru grafice cu stil uniform"""
    icon_html = f'{icon} ' if icon else ''
    return f"""
    <div class="chart-container">
        <h4 style="margin: 0 0 1rem 0; color: {COLORS['primary']};">{icon_html}{title}</h4>
    """


def chart_container_end():
    """Închide containerul pentru grafice"""
    return "</div>"


def alert_box(message, alert_type="info", icon=None):
    """
    Generează un box de alertă stilizat.
    alert_type: info, success, warning, error
    """
    colors_map = {
        "info": (COLORS['primary'], COLORS['primary'] + "15"),
        "success": (COLORS['success'], COLORS['success'] + "15"),
        "warning": (COLORS['warning'], COLORS['warning'] + "15"),
        "error": (COLORS['error'], COLORS['error'] + "15")
    }
    border_color, bg_color = colors_map.get(alert_type, colors_map["info"])
    icon_html = f'<span style="margin-right: 0.5rem;">{icon}</span>' if icon else ''

    return f"""
    <div style="background: {bg_color}; padding: 1rem 1.5rem; border-radius: 12px;
                border-left: 4px solid {border_color}; margin-bottom: 1rem;">
        {icon_html}{message}
    </div>
    """


def get_plotly_layout_defaults():
    """Returnează setările implicite pentru layout-ul Plotly"""
    return {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {'family': 'Inter, sans-serif'},
        'xaxis': {'gridcolor': '#e2e8f0'},
        'yaxis': {'gridcolor': '#e2e8f0'},
        'margin': {'l': 20, 'r': 20, 't': 20, 'b': 40}
    }
