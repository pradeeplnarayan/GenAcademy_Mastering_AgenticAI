"""
Body Composition Analysis Module
Calculates and analyzes body composition metrics over time
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from typing import Dict, List, Tuple

class BodyCompositionAnalyzer:
    """Analyzes body composition data and generates insights"""
    
    # Status thresholds
    THRESHOLDS = {
        'muscle_symmetry_excellent': 0.98,
        'muscle_symmetry_good': 0.95,
        'strength_plateau_threshold': 0.5,  # % change
        'visceral_fat_target': 100,  # ml
        'body_fat_pct_excellent_male': 15,
        'body_fat_pct_excellent_female': 22,
        'weight_change_rate': 1,  # lbs per week target
    }
    
    def __init__(self, age: int, gender: str, height_cm: float, weight_kg: float, composition_data: pd.DataFrame):
        """
        Initialize analyzer with user profile and composition data
        
        Args:
            age: User age (18-70)
            gender: 'M', 'F', or 'NA'
            height_cm: Height in centimeters
            weight_kg: Current weight in kg
            composition_data: DataFrame with metrics as rows, dates as columns
        """
        self.age = age
        self.gender = gender
        self.height_cm = height_cm
        self.weight_kg = weight_kg
        self.composition_data = composition_data
        
        # Parse data
        self.dates = [pd.to_datetime(col) for col in composition_data.columns]
        self.dates_sorted = sorted(self.dates)
        
        # Sort dataframe by dates
        sorted_cols = sorted(composition_data.columns, key=lambda x: pd.to_datetime(x))
        self.composition_data = composition_data[sorted_cols]
    
    def get_metric(self, metric_name: str) -> List[float]:
        """Get metric values over time"""
        if metric_name in self.composition_data.index:
            return self.composition_data.loc[metric_name].values.tolist()
        return []
    
    def calculate_trend(self, metric_values: List[float]) -> Dict:
        """Calculate trend for a metric"""
        if len(metric_values) < 2:
            return {'direction': 'neutral', 'change': 0, 'pct_change': 0}
        
        first = metric_values[0]
        last = metric_values[-1]
        change = last - first
        pct_change = (change / abs(first)) * 100 if first != 0 else 0
        
        return {
            'change': change,
            'pct_change': pct_change,
            'direction': 'up' if change > 0 else 'down' if change < 0 else 'neutral'
        }
    
    def calculate_symmetry(self, left: float, right: float) -> float:
        """Calculate symmetry percentage (0-100)"""
        if max(left, right) == 0:
            return 100.0
        return (1 - abs(left - right) / max(left, right)) * 100
    
    def get_bmi(self) -> float:
        """Calculate BMI"""
        height_m = self.height_cm / 100
        return self.weight_kg / (height_m ** 2)
    
    def estimate_visceral_fat(self, body_fat_pct: float) -> float:
        """Estimate visceral fat based on body fat percentage"""
        # Simplified estimation: visceral fat is roughly 10-15% of total body fat
        total_fat_kg = self.weight_kg * (body_fat_pct / 100)
        visceral_ratio = 0.12  # Average ratio
        return total_fat_kg * visceral_ratio
    
    def generate_analysis(self) -> Dict:
        """Generate comprehensive analysis"""
        
        # Extract metrics
        weights = self.get_metric('Weight')
        muscles = self.get_metric('Skeletal Muscle Mass')
        fat_pcts = self.get_metric('Percent Body Fat')
        ecw_tbw = self.get_metric('ECW/TBW')
        fat_masses = self.get_metric('Body Fat Mass')
        left_arms = self.get_metric('Left Arm')
        right_arms = self.get_metric('Right Arm')
        trunks = self.get_metric('Trunk')
        left_legs = self.get_metric('Left Leg')
        right_legs = self.get_metric('Right Leg')
        
        # Convert dates to strings for display
        date_strings = [d.strftime('%b %Y') for d in self.dates_sorted]
        
        # Calculate trends
        weight_trend = self.calculate_trend(weights)
        muscle_trend = self.calculate_trend(muscles)
        fat_pct_trend = self.calculate_trend(fat_pcts)
        ecw_tbw_trend = self.calculate_trend(ecw_tbw)
        
        # Latest values
        latest_weight = weights[-1] if weights else 0
        latest_muscle = muscles[-1] if muscles else 0
        latest_fat_pct = fat_pcts[-1] if fat_pcts else 0
        latest_ecw_tbw = ecw_tbw[-1] if ecw_tbw else 0
        latest_fat_mass = fat_masses[-1] if fat_masses else 0
        
        # Symmetry analysis
        muscle_symmetry = self.calculate_symmetry(
            left_arms[-1] if left_arms else 0,
            right_arms[-1] if right_arms else 0
        )
        
        # Segment values
        segments = {
            'left_arm': left_arms[-1] if left_arms else 0,
            'right_arm': right_arms[-1] if right_arms else 0,
            'trunk': trunks[-1] if trunks else 0,
            'left_leg': left_legs[-1] if left_legs else 0,
            'right_leg': right_legs[-1] if right_legs else 0,
        }
        
        # Score calculations (0-10 scale)
        muscle_score = min(10, (latest_muscle / (self.weight_kg * 0.35)) * 10) if latest_muscle > 0 else 5
        symmetry_score = (muscle_symmetry / 100) * 10
        strength_score = min(10, 5 + (muscle_trend['pct_change'] / 2))
        weight_score = 10 if weight_trend['change'] <= -1 else 8 if weight_trend['change'] <= 0 else 6 if weight_trend['change'] <= 2 else 4
        fat_score = 10 if latest_fat_pct < 20 else 8 if latest_fat_pct < 25 else 6 if latest_fat_pct < 30 else 3
        visceral_score = 10 if latest_fat_pct < 20 else 7 if latest_fat_pct < 28 else 4
        trunk_fat_score = 10 if (trunks[-1] / latest_muscle) < 0.4 else 6 if (trunks[-1] / latest_muscle) < 0.5 else 3
        
        # Overall score (weighted average)
        overall_score = (
            muscle_score * 0.15 +
            symmetry_score * 0.10 +
            strength_score * 0.15 +
            weight_score * 0.15 +
            fat_score * 0.20 +
            visceral_score * 0.15 +
            trunk_fat_score * 0.10
        )
        overall_score = min(10, max(0, overall_score))
        
        # Status labels
        def get_status(score):
            if score >= 8.5:
                return "Excellent"
            elif score >= 7:
                return "Good"
            elif score >= 5.5:
                return "Working"
            elif score >= 3:
                return "Area to Improve"
            else:
                return "Needs to come down"
        
        # Biggest win
        wins = []
        if weight_trend['change'] < -1:
            wins.append(('🏆 Weight Loss', f"↓ {abs(weight_trend['change']):.1f} lb", abs(weight_trend['change'])))
        if muscle_trend['change'] > 0.5:
            wins.append(('💪 Muscle Gain', f"↑ {muscle_trend['change']:.1f} lb", muscle_trend['change']))
        if symmetry_score >= 8:
            wins.append(('⚖️ Symmetry', f"{muscle_symmetry:.1f}% balanced", muscle_symmetry))
        
        biggest_win = wins[0] if wins else ('📈 Starting', 'Beginning your journey', 0)
        biggest_win = {
            'emoji': biggest_win[0].split()[0],
            'title': biggest_win[0],
            'value': biggest_win[1]
        }
        
        # Working scores (score >= 7)
        working = []
        if muscle_score >= 7:
            working.append({'metric': 'Muscle', 'score': muscle_score, 'status': get_status(muscle_score)})
        if symmetry_score >= 7:
            working.append({'metric': 'Muscle symmetry', 'score': symmetry_score, 'status': get_status(symmetry_score)})
        if strength_score >= 7:
            working.append({'metric': 'Strength training', 'score': strength_score, 'status': get_status(strength_score)})
        if weight_score >= 7:
            working.append({'metric': 'Weight', 'score': weight_score, 'status': get_status(weight_score)})
        
        # Needs attention (5 <= score < 7)
        needs_attention = []
        if 5 <= fat_score < 7:
            needs_attention.append({'metric': 'Total fat', 'score': fat_score, 'status': get_status(fat_score)})
        if 5 <= visceral_score < 7:
            needs_attention.append({'metric': 'Visceral fat', 'score': visceral_score, 'status': get_status(visceral_score)})
        if 5 <= trunk_fat_score < 7:
            needs_attention.append({'metric': 'Trunk/abdominal fat', 'score': trunk_fat_score, 'status': get_status(trunk_fat_score)})
        if 5 <= strength_score < 7:
            needs_attention.append({'metric': 'Strength plateau', 'score': strength_score, 'status': get_status(strength_score)})
        
        # Coach's take
        if overall_score >= 7:
            coach_positive = "You're building solid foundation. Consistency is your superpower—keep the momentum going!"
        elif overall_score >= 5:
            coach_positive = "Good progress visible. Focus on refining your approach for faster results."
        else:
            coach_positive = "You're on the journey. Small wins compound into big results."
        
        # Biggest opportunity
        if fat_score < 5 or visceral_score < 5:
            opportunity = "Make fat loss more consistent while protecting muscle. Prioritize protein intake and resistance training."
        elif weight_score < 5:
            opportunity = "Weight trending up. Review nutrition and increase daily activity."
        elif strength_score < 5:
            opportunity = "Strength plateau detected. Time to change training stimulus—increase intensity or volume."
        else:
            opportunity = "All systems working well. Time for a deliberate fat-loss phase if desired."
        
        # Overall message
        if overall_score >= 8:
            overall_msg = "Excellent progress — you're crushing it! 🚀"
        elif overall_score >= 6:
            overall_msg = "Good progress — keep going! 💪"
        else:
            overall_msg = "Building your foundation — stay consistent! 📈"
        
        return {
            'overall_score': overall_score,
            'overall_message': overall_msg,
            'dates': date_strings,
            'weights': weights,
            'muscles': muscles,
            'fat_pcts': fat_pcts,
            'ecw_tbw': ecw_tbw,
            'latest_weight': latest_weight,
            'weight_change': weight_trend['change'],
            'latest_muscle': latest_muscle,
            'muscle_change': muscle_trend['change'],
            'latest_fat_pct': latest_fat_pct,
            'fat_pct_change': fat_pct_trend['change'],
            'latest_ecw_tbw': latest_ecw_tbw,
            'ecw_tbw_change': ecw_tbw_trend['change'],
            'biggest_win': biggest_win,
            'segments': segments,
            'working_scores': working,
            'needs_attention_scores': needs_attention,
            'coach_take_positive': coach_positive,
            'biggest_opportunity': opportunity,
        }
    
    def plot_trend(self, metric_type: str, dates: List[str], values: List[float]) -> go.Figure:
        """Create trend chart for a metric"""
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            mode='lines+markers',
            name=metric_type.capitalize(),
            line=dict(color='#2d8f5f', width=3),
            marker=dict(size=8, color='#2d8f5f'),
            fill='tozeroy',
            fillcolor='rgba(45, 143, 95, 0.1)'
        ))
        
        # Add trend line
        if len(values) > 1:
            z = np.polyfit(range(len(values)), values, 1)
            p = np.poly1d(z)
            trendline = p(range(len(values)))
            fig.add_trace(go.Scatter(
                x=dates,
                y=trendline,
                mode='lines',
                name='Trend',
                line=dict(color='#d9a574', width=2, dash='dash')
            ))
        
        fig.update_layout(
            template='plotly_white',
            hovermode='x unified',
            height=300,
            margin=dict(l=40, r=40, t=40, b=40),
            xaxis_title="",
            yaxis_title="Value",
            showlegend=True,
        )
        
        return fig
