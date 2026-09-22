import pandas as pd
import streamlit as st
from pathlib import Path

# Complete mapping of 51 CDC natality geographies to 2-letter postal abbreviations
STATE_ABBREVIATIONS = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'District of Columbia': 'DC',
    'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL',
    'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA',
    'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN',
    'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR',
    'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
    'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA',
    'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}

# Strict chronological calendar month order
MONTH_ORDER = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

EXPECTED_COLUMNS = [
    'State of Residence', 'Month', 'Month Code', 'Year Code', 'Sex of Infant', 'Births'
]
EXPECTED_ROWS = 1224
EXPECTED_TOTAL_BIRTHS = 3604640

@st.cache_data
def load_and_validate_data(data_path=None) -> pd.DataFrame:
    """
    Loads provisional 2025 CDC Natality Excel dataset, conducts data-quality validation checks,
    attaches 2-letter state postal abbreviations, and enforces categorical month ordering.
    """
    if data_path is None:
        # Default path relative to this module for local & Streamlit Cloud compatibility
        base_dir = Path(__file__).resolve().parent.parent
        data_path = base_dir / "Data" / "Provisional_Natality_2025_CDC.xlsx"

    if not Path(data_path).exists():
        raise FileNotFoundError(f"Dataset file not found at: {data_path}")

    # Read Excel file (sheet index 0)
    df = pd.read_excel(data_path, sheet_name=0)

    # 1. Validate Columns
    missing_cols = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Dataset validation failed: missing expected columns {missing_cols}")

    # 2. Validate Row Count
    if len(df) != EXPECTED_ROWS:
        raise ValueError(f"Dataset validation failed: expected {EXPECTED_ROWS} rows, got {len(df)}")

    # 3. Validate Total Birth Count
    total_births = df['Births'].sum()
    if total_births != EXPECTED_TOTAL_BIRTHS:
        raise ValueError(
            f"Dataset validation failed: expected total births {EXPECTED_TOTAL_BIRTHS:,}, got {total_births:,}"
        )

    # 4. Check missing values
    if df.isnull().sum().sum() > 0:
        raise ValueError("Dataset validation failed: unexpected missing values found.")

    # Attach State Code abbreviation for choropleth mapping
    df['State Code'] = df['State of Residence'].map(STATE_ABBREVIATIONS)
    unmapped_states = df[df['State Code'].isnull()]['State of Residence'].unique()
    if len(unmapped_states) > 0:
        raise ValueError(f"Failed to map state abbreviations for: {unmapped_states}")

    # Set categorical month ordering
    df['Month'] = pd.Categorical(df['Month'], categories=MONTH_ORDER, ordered=True)

    return df


def filter_dataset(df: pd.DataFrame, selected_states=None, selected_months=None, selected_sex="All") -> pd.DataFrame:
    """
    Filters dataframe by selected states, months, and infant sex category.
    """
    filtered = df.copy()

    if selected_states:
        filtered = filtered[filtered['State of Residence'].isin(selected_states)]

    if selected_months:
        filtered = filtered[filtered['Month'].isin(selected_months)]

    if selected_sex and selected_sex != "All":
        filtered = filtered[filtered['Sex of Infant'] == selected_sex]

    return filtered
