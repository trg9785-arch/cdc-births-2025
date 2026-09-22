# CDC Provisional Natality 2025 Streamlit Dashboard

An interactive web application designed for undergraduate business analytics students to explore provisional 2025 natality data from the Centers for Disease Control and Prevention (CDC).

## Project Overview

This application provides a comprehensive interactive dashboard for analyzing geographic, monthly, and biological sex differences in U.S. birth counts.

### Key Features
- **Educational Header & Data Integrity Warnings**: Explicitly highlights that figures represent **birth counts, not birth rates**.
- **Interactive Sidebar Controls**: Multi-select filters for state/geography, calendar month, and infant sex, complete with "Select All", "Clear All", and "Reset Filters" controls.
- **Dynamic KPI Cards**: Displays total birth volume, state counts, monthly averages, peak geography, and peak month.
- **5 Comprehensive Content Tabs**:
  1. **Overview**: US Choropleth map & monthly national birth trends.
  2. **Geographic Analysis**: State volume ranking, Top N vs. Bottom N comparison, and State vs. Month matrix heatmap.
  3. **Monthly & Sex Analysis**: Infant sex distribution donut chart, line trends, and biological secondary sex ratio analysis.
  4. **Data Table & Download**: Interactive `st.dataframe` with CSV export capability.
  5. **About the Data**: Methodology documentation, data-quality notes, and classroom discussion questions for students.

---

## Technical Architecture

```text
cdc-births-2025/
├── Data/
│   └── Provisional_Natality_2025_CDC.xlsx  # Original CDC natality dataset (1,224 rows, 3.6M births)
├── utils/
│   ├── __init__.py
│   ├── data_loader.py                      # Data validation, caching, state postal mapping, filtering
│   └── charts.py                           # Plotly graph builders with accessible color schemes & zero-based axes
├── app.py                                  # Main Streamlit dashboard application
├── requirements.txt                        # Python dependencies
└── README.md                               # Project documentation
```

---

## Setup and Running Locally

### Prerequisites
- Python 3.9+ installed

### Running the App
From the project directory:

```bash
# Using standard Python / Anaconda environment
python -m streamlit run app.py
```

Or using the Anaconda environment directly:
```bash
"C:\Users\trg97\anaconda3\python.exe" -m streamlit run app.py
```

The Streamlit web application will launch locally at `http://localhost:8501`.
