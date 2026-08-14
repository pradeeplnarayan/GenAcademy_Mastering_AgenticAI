# Body Composition Analysis Dashboard

AI-powered body composition analysis dashboard built with Streamlit.

## Features

- 📊 **Comprehensive Analysis** - Analyzes body composition metrics over time
- 🎯 **Personalized Insights** - AI-powered recommendations based on your data
- 📈 **Visual Trends** - Track progress with interactive charts
- 💪 **Segmental Analysis** - Muscle symmetry and distribution analysis
- 🎨 **Premium Design** - Modern wellness app styling (Apple Health + Oura inspired)

## Quick Start

### Prerequisites

- Python 3.9+
- Uv (Python package manager)

### Installation

1. Clone or navigate to the project directory:
```bash
cd "Week 1 Project"
```

2. Install dependencies using Uv:
```bash
uv sync
```

### Running the App

Start the Streamlit development server:

```bash
uv run streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

### 1. Enter Your Profile
- Age (18-70)
- Gender (M/F/NA)
- Height (Feet & Inches)
- Weight (lb or kg)

### 2. Upload Your Data
- Prepare a CSV file with InBody composition data
- Required metrics (rows):
  - Weight
  - Skeletal Muscle Mass
  - Percent Body Fat
  - ECW/TBW
  - Body Fat Mass
  - Left Arm, Right Arm
  - Trunk
  - Right Leg, Left Leg
- Columns should be dates (minimum 3 time periods)

### 3. View Results
- Overall score and message
- Key metrics with trends
- Biggest wins
- Four analysis tabs:
  - 📊 Your Journey (trends over time)
  - ✅ What's Working (positive metrics)
  - ⚠️ Needs Attention (areas to improve)
  - 🎯 Segmental Analysis (muscle distribution)

## CSV Format

```
Metric,2025-08-01,2025-09-01,2025-10-01
Weight,180.5,177.2,175.8
Skeletal Muscle Mass,68.5,68.9,69.2
Percent Body Fat,28.5,27.1,26.4
ECW/TBW,0.389,0.385,0.380
Body Fat Mass,51.4,48.0,46.4
Left Arm,6.2,6.3,6.4
Right Arm,6.1,6.2,6.3
Trunk,25.3,25.6,25.9
Right Leg,12.8,13.1,13.4
Left Leg,12.9,13.2,13.5
```

## Color Palette

- **Primary Green**: #2d8f5f (Positive indicators)
- **Accent Amber**: #d9a574 (Attention/Needs work)
- **Accent Coral**: #c47856 (Critical/Action needed)
- **Background**: Off-white/Light gray (#fafaf8)
- **Text**: Deep charcoal (#1a1a1a)

## Status Levels

- **Excellent** (8.5-10): Optimal performance
- **Good** (7-8.5): Strong progress
- **Working** (5.5-7): On track
- **Area to Improve** (3-5.5): Needs attention
- **Needs to come down** (0-3): Critical action needed

## Project Structure

```
Week 1 Project/
├── app.py              # Main Streamlit application
├── analysis.py         # Body composition analysis engine
├── validators.py       # Input validation logic
├── styles.py           # UI styling and components
├── __about__.py        # Version info
├── pyproject.toml      # Uv/pip dependencies
├── sample_data.csv     # Example CSV data
└── README.md           # This file
```

## Development

Install development dependencies:
```bash
uv sync --extra dev
```

Run code quality checks:
```bash
uv run black .
uv run ruff check .
```

## Disclaimer

This dashboard provides personalized body composition insights for fitness tracking purposes only. It is not medical advice. Always consult with a healthcare provider for medical guidance or concerns.

## License

MIT License - See LICENSE file for details
