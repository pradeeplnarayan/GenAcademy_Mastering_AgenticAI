"""
UI Styling and Components
Premium wellness app styling following Apple Health + Oura design principles
"""
import streamlit as st

def apply_custom_styling():
    """Apply custom CSS styling to the app"""
    st.markdown("""
    <style>
    /* Custom color palette */
    :root {
        --primary-green: #2d8f5f;
        --accent-amber: #d9a574;
        --accent-coral: #c47856;
        --bg-light: #fafaf8;
        --bg-dark: #1a1a1a;
        --text-primary: #1a1a1a;
        --text-secondary: #666666;
    }
    
    /* Main layout */
    .stMainBlockContainer {
        padding: 20px 40px;
        background: linear-gradient(135deg, #fafaf8 0%, #f5f5f3 100%);
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: #ffffff;
    }
    
    /* Metric boxes */
    .metric-box {
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        text-align: center;
        border: 1px solid #f0f0f0;
    }
    
    .metric-box.positive {
        border-left: 4px solid #2d8f5f;
    }
    
    .metric-box.attention {
        border-left: 4px solid #d9a574;
    }
    
    .metric-box.critical {
        border-left: 4px solid #c47856;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #1a1a1a;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 12px;
        color: #999;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-change {
        font-size: 14px;
        font-weight: 600;
        margin-top: 8px;
    }
    
    .metric-change.positive {
        color: #2d8f5f;
    }
    
    .metric-change.negative {
        color: #c47856;
    }
    
    /* Score cards */
    .score-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        border-left: 4px solid #2d8f5f;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    
    .score-card.attention {
        border-left-color: #d9a574;
    }
    
    .score-card.critical {
        border-left-color: #c47856;
    }
    
    .score-label {
        font-size: 14px;
        font-weight: 600;
        color: #1a1a1a;
    }
    
    .score-value {
        font-size: 14px;
        font-weight: 700;
        color: #2d8f5f;
        background: #f0f9f5;
        padding: 4px 12px;
        border-radius: 6px;
    }
    
    .score-value.attention {
        color: #d9a574;
        background: #fef5f0;
    }
    
    .score-value.critical {
        color: #c47856;
        background: #fef0ed;
    }
    
    /* Tabs */
    .stTabs [role="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 12px 20px;
        font-weight: 600;
        color: #666;
    }
    
    .stTabs [role="tab"][aria-selected="true"] {
        color: #2d8f5f;
        border-bottom: 3px solid #2d8f5f;
    }
    
    /* Input fields */
    .stNumberInput input, .stSelectbox select {
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        padding: 10px 12px;
    }
    
    .stNumberInput input:focus, .stSelectbox select:focus {
        border-color: #2d8f5f;
        box-shadow: 0 0 0 3px rgba(45, 143, 95, 0.1);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        padding: 10px 20px;
        border: none;
        background: #2d8f5f !important;
        color: white !important;
    }
    
    .stButton > button:hover {
        background: #1f6241 !important;
    }
    
    /* File uploader */
    .uploadedFile {
        border-radius: 8px;
        border: 2px dashed #2d8f5f;
    }
    
    /* Markdown styling */
    h1 {
        color: #1a1a1a;
        font-weight: 700;
        margin: 20px 0 10px 0;
    }
    
    h2 {
        color: #333;
        font-weight: 600;
        margin: 15px 0 8px 0;
    }
    
    h3 {
        color: #555;
        font-weight: 600;
        margin: 12px 0 6px 0;
    }
    
    p {
        color: #666;
        line-height: 1.6;
    }
    
    /* Success/Warning/Error messages */
    .stSuccess {
        background: #f0f9f5;
        border-left: 4px solid #2d8f5f;
        border-radius: 8px;
    }
    
    .stWarning {
        background: #fef5f0;
        border-left: 4px solid #d9a574;
        border-radius: 8px;
    }
    
    .stError {
        background: #fef0ed;
        border-left: 4px solid #c47856;
        border-radius: 8px;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        border-radius: 8px;
        background: #f5f5f3;
    }
    
    /* Plotly charts */
    .plotly-graph-div {
        border-radius: 12px;
    }
    
    /* Horizontal line */
    hr {
        border: none;
        border-top: 1px solid #e0e0e0;
        margin: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)

def render_metric_box(label: str, value: float, change: float, unit: str):
    """
    Render a metric display box
    
    Args:
        label: Metric label
        value: Current value
        change: Change from previous
        unit: Unit of measurement
    """
    change_sign = "↓" if change < 0 else "↑" if change > 0 else "→"
    change_color = "#2d8f5f" if change < 0 and label.startswith("Weight") else "#2d8f5f" if change > 0 else "#999"
    
    if unit == "ratio":
        value_str = f"{value:.3f}"
    elif unit == "%":
        value_str = f"{value:.1f}{unit}"
    else:
        value_str = f"{value:.1f} {unit}"
    
    change_str = f"{change_sign} {abs(change):.1f}" if change != 0 else f"→ 0"
    
    st.markdown(f"""
    <div style="background: white; border-radius: 16px; padding: 20px; 
                text-align: center; border: 1px solid #f0f0f0; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
        <div style="font-size: 11px; color: #999; text-transform: uppercase; 
                    letter-spacing: 1px; margin-bottom: 8px;">
            {label}
        </div>
        <div style="font-size: 28px; font-weight: 700; color: #1a1a1a;">
            {value_str}
        </div>
        <div style="font-size: 13px; color: {change_color}; font-weight: 600; 
                    margin-top: 8px;">
            {change_str}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_score_card(metric: str, score: float, status: str, emoji: str):
    """
    Render a score card
    
    Args:
        metric: Metric name
        score: Score out of 10
        status: Status label
        emoji: Emoji prefix
    """
    # Determine color based on score
    if score >= 7:
        color = "#2d8f5f"
        bg_color = "#f0f9f5"
        border_color = "#2d8f5f"
    elif score >= 5:
        color = "#d9a574"
        bg_color = "#fef5f0"
        border_color = "#d9a574"
    else:
        color = "#c47856"
        bg_color = "#fef0ed"
        border_color = "#c47856"
    
    st.markdown(f"""
    <div style="background: {bg_color}; border-left: 4px solid {border_color}; 
                border-radius: 12px; padding: 16px; margin: 12px 0; 
                display: flex; justify-content: space-between; align-items: center;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        <div>
            <div style="font-size: 14px; font-weight: 600; color: #1a1a1a;">
                {emoji} {metric}
            </div>
            <div style="font-size: 12px; color: #999; margin-top: 4px;">
                {status}
            </div>
        </div>
        <div style="font-size: 20px; font-weight: 700; color: {color};">
            {score:.1f}/10
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_dark_mode_toggle():
    """Render dark/light mode toggle"""
    col1, col2 = st.columns([0.8, 0.2])
    with col2:
        dark_mode = st.checkbox("🌙 Dark Mode", value=False)
    
    if dark_mode:
        st.markdown("""
        <style>
        .stMainBlockContainer {
            background: linear-gradient(135deg, #1a1a1a 0%, #222 100%);
            color: #f0f0f0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    return dark_mode
