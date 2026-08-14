"""
Input validation for user data
"""
import pandas as pd
from typing import Optional

def validate_user_inputs(age: int, gender: str, height_feet: int, height_inches: int, weight: float) -> Optional[str]:
    """
    Validate user input fields
    
    Returns:
        Error message if validation fails, None if valid
    """
    # Age validation
    if not (18 <= age <= 70):
        return "Age must be between 18 and 70"
    
    # Gender validation
    if gender not in ["M", "F", "NA"]:
        return "Gender must be M, F, or NA"
    
    # Height validation
    total_inches = height_feet * 12 + height_inches
    if not (48 <= total_inches <= 96):  # 4ft to 8ft
        return "Height must be between 4 and 8 feet"
    
    # Weight validation
    if not (80 <= weight <= 400):
        return "Weight must be between 80 and 400 lbs (or 36-182 kg)"
    
    return None

def validate_csv_data(df: pd.DataFrame) -> Optional[str]:
    """
    Validate uploaded CSV data
    
    Args:
        df: DataFrame with metrics as rows, dates as columns
    
    Returns:
        Error message if validation fails, None if valid
    """
    required_metrics = [
        'Weight',
        'Skeletal Muscle Mass',
        'Percent Body Fat',
        'ECW/TBW',
        'Body Fat Mass',
        'Left Arm',
        'Right Arm',
        'Trunk',
        'Right Leg',
        'Left Leg'
    ]
    
    # Check if all required metrics are present
    missing = [m for m in required_metrics if m not in df.index]
    if missing:
        return f"Missing required metrics: {', '.join(missing)}"
    
    # Check minimum 3 time periods
    if len(df.columns) < 3:
        return f"Minimum 3 time periods required. You have {len(df.columns)}"
    
    # Check for numeric values
    try:
        df_numeric = df.astype(float)
    except ValueError:
        return "All values must be numeric"
    
    # Check for missing values
    if df_numeric.isnull().any().any():
        return "Dataset contains missing values"
    
    return None
