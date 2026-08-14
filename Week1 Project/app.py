"""
Body Composition Dashboard - Main Streamlit App
AI-powered analysis for body composition metrics and fitness tracking
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from io import StringIO

from analysis import BodyCompositionAnalyzer
from validators import validate_user_inputs, validate_csv_data
from styles import apply_custom_styling, render_score_card, render_metric_box

# Page config
st.set_page_config(
    page_title="Body Composition Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
apply_custom_styling()

# Session state initialization
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

# Header with story
def render_hero_section():
    """Render the compelling hero section - tells story in 5 seconds"""
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px;">
        <h1 style="font-size: 48px; font-weight: 700; margin-bottom: 10px; color: #1a1a1a;">
            📊 YOUR BODY COMPOSITION
        </h1>
        <h2 style="font-size: 28px; color: #666; margin-bottom: 30px; font-weight: 400;">
            Progress Dashboard
        </h2>
        <p style="font-size: 18px; color: #888; max-width: 600px; margin: 0 auto;">
            Track your fitness journey with AI-powered insights. See what's working, 
            what needs attention, and celebrate your wins.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar for input
with st.sidebar:
    st.title("📋 Your Profile")
    
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=18, max_value=70, value=30, step=1)
    with col2:
        gender = st.selectbox("Gender", ["M", "F", "NA"], index=0)
    
    # Height input (feet and inches)
    col1, col2 = st.columns(2)
    with col1:
        height_feet = st.number_input("Height (Feet)", min_value=4, max_value=7, value=5, step=1)
    with col2:
        height_inches = st.number_input("Inches", min_value=0, max_value=11, value=10, step=1)
    
    height_inches_total = height_feet * 12 + height_inches
    
    # Weight input
    col1, col2 = st.columns(2)
    with col1:
        weight_unit = st.radio("Weight Unit", ["lb", "kg"], horizontal=True, index=0)
    with col2:
        if weight_unit == "lb":
            weight = st.number_input("Weight (lb)", min_value=80.0, max_value=400.0, value=180.0, step=0.1)
            weight_kg = weight * 0.453592
        else:
            weight = st.number_input("Weight (kg)", min_value=36.0, max_value=182.0, value=82.0, step=0.1)
            weight_kg = weight
            weight = weight / 0.453592
    
    st.markdown("---")
    st.title("📤 Upload Data")
    
    uploaded_file = st.file_uploader(
        "Upload InBody CSV",
        type="csv",
        help="CSV with composition data: Weight, Skeletal Muscle Mass, Percent Body Fat, ECW/TBW, Body Fat Mass, Left Arm, Right Arm, Trunk, Right Leg, Left Leg (as rows, dates as columns)"
    )
    
    if st.button("🔍 Analyze", use_container_width=True, type="primary"):
        if uploaded_file is not None:
            try:
                # Read and validate CSV
                df = pd.read_csv(uploaded_file, index_col=0)
                
                validation_errors = validate_csv_data(df)
                if validation_errors:
                    st.error(f"CSV Validation Error: {validation_errors}")
                else:
                    # Create analyzer
                    analyzer = BodyCompositionAnalyzer(
                        age=age,
                        gender=gender,
                        height_cm=height_inches_total * 2.54,
                        weight_kg=weight_kg,
                        composition_data=df
                    )
                    
                    st.session_state.analyzer = analyzer
                    st.session_state.analysis_complete = True
                    st.success("✅ Analysis complete! Scroll down to see results.")
                    
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
        else:
            st.warning("Please upload a CSV file first.")

# Main content area
if st.session_state.analysis_complete and st.session_state.analyzer:
    analyzer = st.session_state.analyzer
    results = analyzer.generate_analysis()
    
    # Hero section with overall score
    render_hero_section()
    
    # Overall score card
    overall_score = results['overall_score']
    score_color = "#2d8f5f" if overall_score >= 7 else "#d9a574" if overall_score >= 5 else "#c47856"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {score_color}15 0%, {score_color}05 100%); 
                border: 2px solid {score_color}; border-radius: 16px; padding: 30px; 
                text-align: center; margin: 20px 0;">
        <div style="font-size: 48px; font-weight: 700; color: {score_color};">
            ⭐ {overall_score:.1f} / 10
        </div>
        <div style="font-size: 18px; color: #666; margin-top: 10px;">
            {results['overall_message']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics
    st.markdown("### 📈 Key Metrics")
    
    metrics_cols = st.columns(4)
    metrics_data = [
        ("Weight", results['latest_weight'], results['weight_change'], "lb"),
        ("Muscle Mass", results['latest_muscle'], results['muscle_change'], "lb"),
        ("Body Fat %", results['latest_fat_pct'], results['fat_pct_change'], "%"),
        ("ECW/TBW", results['latest_ecw_tbw'], results['ecw_tbw_change'], "ratio"),
    ]
    
    for i, (label, value, change, unit) in enumerate(metrics_data):
        with metrics_cols[i]:
            render_metric_box(label, value, change, unit)
    
    # Biggest win section
    st.markdown("### 🏆 Your Biggest Win")
    biggest_win = results['biggest_win']
    st.markdown(f"""
    <div style="background: #f0f9f5; border-left: 4px solid #2d8f5f; padding: 20px; 
                border-radius: 8px; margin: 20px 0;">
        <div style="font-size: 24px; font-weight: 600; color: #2d8f5f;">
            {biggest_win['emoji']} {biggest_win['title']}
        </div>
        <div style="font-size: 16px; color: #666; margin-top: 8px;">
            {biggest_win['value']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Your Journey", "✅ What's Working", "⚠️ Needs Attention", "🎯 Segmental Analysis"]
    )
    
    with tab1:
        st.markdown("### Your Journey Over Time")
        
        cols = st.columns(3)
        
        with cols[0]:
            st.markdown("#### Weight Trend")
            fig = analyzer.plot_trend('weight', results['dates'], results['weights'])
            st.plotly_chart(fig, use_container_width=True)
        
        with cols[1]:
            st.markdown("#### Muscle Mass Trend")
            fig = analyzer.plot_trend('muscle', results['dates'], results['muscles'])
            st.plotly_chart(fig, use_container_width=True)
        
        with cols[2]:
            st.markdown("#### Body Fat % Trend")
            fig = analyzer.plot_trend('fat', results['dates'], results['fat_pcts'])
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### 🟢 What's Working")
        working_scores = results['working_scores']
        
        for item in working_scores:
            render_score_card(item['metric'], item['score'], item['status'], "✅")
        
        if results['coach_take_positive']:
            st.markdown(f"""
            <div style="background: #f0f9f5; padding: 20px; border-radius: 12px; 
                        border-left: 4px solid #2d8f5f; margin-top: 20px;">
                <div style="font-size: 18px; font-weight: 600; color: #2d8f5f; margin-bottom: 10px;">
                    💬 Coach's Take
                </div>
                <div style="font-size: 16px; color: #333;">
                    {results['coach_take_positive']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 🟡 Needs Attention")
        needs_attention = results['needs_attention_scores']
        
        for item in needs_attention:
            render_score_card(item['metric'], item['score'], item['status'], "⚠️")
        
        # Biggest opportunity
        opportunity = results['biggest_opportunity']
        st.markdown(f"""
        <div style="background: #fef5f0; padding: 20px; border-radius: 12px; 
                    border-left: 4px solid #d9a574; margin-top: 20px;">
            <div style="font-size: 18px; font-weight: 600; color: #d9a574; margin-bottom: 10px;">
                🔴 Biggest Opportunity
            </div>
            <div style="font-size: 16px; color: #333;">
                {opportunity}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### 📍 Segmental Analysis")
        
        # Body segment visualization
        segments = results['segments']
        
        cols = st.columns(3)
        segment_labels = ['Left Arm', 'Trunk', 'Right Arm', 'Left Leg', 'Right Leg']
        segment_values = [
            segments.get('left_arm', 0),
            segments.get('trunk', 0),
            segments.get('right_arm', 0),
            segments.get('left_leg', 0),
            segments.get('right_leg', 0),
        ]
        
        # Symmetry analysis
        left_arm = segments.get('left_arm', 0)
        right_arm = segments.get('right_arm', 0)
        left_leg = segments.get('left_leg', 0)
        right_leg = segments.get('right_leg', 0)
        
        arm_symmetry = (1 - abs(left_arm - right_arm) / max(left_arm, right_arm, 0.1)) * 100 if max(left_arm, right_arm) > 0 else 0
        leg_symmetry = (1 - abs(left_leg - right_leg) / max(left_leg, right_leg, 0.1)) * 100 if max(left_leg, right_leg) > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🦾 Arm Symmetry", f"{arm_symmetry:.1f}%", "Balanced" if arm_symmetry > 95 else "Needs work")
        with col2:
            st.metric("🦵 Leg Symmetry", f"{leg_symmetry:.1f}%", "Balanced" if leg_symmetry > 95 else "Needs work")
        
        # Segment breakdown chart
        fig = go.Figure(data=[
            go.Bar(
                y=segment_labels[:3],
                x=segment_values[:3],
                orientation='h',
                marker_color='#2d8f5f',
                name='Upper Body'
            ),
            go.Bar(
                y=segment_labels[3:],
                x=segment_values[3:],
                orientation='h',
                marker_color='#7ba67b',
                name='Lower Body'
            )
        ])
        fig.update_layout(
            barmode='group',
            title="Muscle Mass by Segment",
            xaxis_title="Muscle Mass (kg)",
            yaxis_title="Body Segment",
            template="plotly_white",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

else:
    render_hero_section()
    st.info("👈 **Get started:** Fill in your profile on the left sidebar and upload your InBody CSV data to begin your analysis.")
    
    # Show sample CSV format
    with st.expander("📋 See Sample CSV Format"):
        sample_csv = """Metric,2025-08-01,2025-09-01,2025-10-01
Weight,180.5,177.2,175.8
Skeletal Muscle Mass,68.5,68.9,69.2
Percent Body Fat,28.5,27.1,26.4
ECW/TBW,0.389,0.385,0.380
Body Fat Mass,51.4,48.0,46.4
Left Arm,6.2,6.3,6.4
Right Arm,6.1,6.2,6.3
Trunk,25.3,25.6,25.9
Right Leg,12.8,13.1,13.4
Left Leg,12.9,13.2,13.5"""
        st.code(sample_csv, language="csv")

# Footer with instructions
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; font-size: 12px; padding: 20px;">
    <p>💪 This dashboard provides personalized body composition insights.</p>
    <p><em>Disclaimer: Not medical advice. Consult with healthcare provider for medical guidance.</em></p>
</div>
""", unsafe_allow_html=True)
