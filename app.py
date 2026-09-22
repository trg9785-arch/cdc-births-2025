import os
import sys
from pathlib import Path
import streamlit as st
import pandas as pd

# Ensure project root is in sys.path for relative imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.data_loader import (
    load_and_validate_data,
    filter_dataset,
    STATE_ABBREVIATIONS,
    MONTH_ORDER,
    EXPECTED_TOTAL_BIRTHS
)
from utils.charts import (
    plot_monthly_trend,
    plot_sex_comparison,
    plot_state_ranking,
    plot_choropleth_map,
    plot_state_month_heatmap,
    plot_top_bottom_comparison
)

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="CDC Provisional Natality Dashboard (2025)",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished educational UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1rem;
    }
    .kpi-card {
        background-color: #F8FAFC;
        border-left: 4px solid #2B547E;
        padding: 1rem;
        border-radius: 0.375rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: #0F172A;
        margin-top: 0.2rem;
    }
    .kpi-sub {
        font-size: 0.8rem;
        color: #64748B;
        margin-top: 0.1rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state(all_states, all_months):
    """Initializes session state defaults for sidebar filter controls."""
    if "selected_states" not in st.session_state:
        st.session_state.selected_states = list(all_states)
    if "selected_months" not in st.session_state:
        st.session_state.selected_months = list(all_months)
    if "selected_sex" not in st.session_state:
        st.session_state.selected_sex = "All"


def main():
    # Load dataset with cached validation
    try:
        df = load_and_validate_data()
    except Exception as e:
        st.error(f"❌ Data Initialization Error: {e}")
        st.stop()

    all_states = sorted(df['State of Residence'].unique().tolist())
    all_months = MONTH_ORDER

    initialize_session_state(all_states, all_months)

    # ---------------------------------------------------------
    # 1. HEADER & EDUCATIONAL BANNERS
    # ---------------------------------------------------------
    st.markdown('<div class="main-header">👶 CDC Provisional Natality Dashboard (2025)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">An interactive business analytics tool for exploring provisional U.S. birth counts across geographies, months, and infant sexes.</div>',
        unsafe_allow_html=True
    )

    st.info(
        "📌 **Analytical Note for Students**: Figures reported in this dataset represent **raw provisional birth counts** "
        "collected by the Centers for Disease Control and Prevention (CDC / NCHS). "
        "**These figures are counts, not birth rates.** Birth rates require total underlying population denominators, "
        "which are not present in raw natality counts."
    )

    # ---------------------------------------------------------
    # 2. SIDEBAR FILTERS
    # ---------------------------------------------------------
    st.sidebar.header("🔍 Filter Controls")

    # State Selection Convenience Controls
    st.sidebar.subheader("Geographies")
    col_st1, col_st2 = st.sidebar.columns(2)
    if col_st1.button("Select All States", use_container_width=True):
        st.session_state.selected_states = list(all_states)
    if col_st2.button("Clear States", use_container_width=True):
        st.session_state.selected_states = []

    st.session_state.selected_states = st.sidebar.multiselect(
        "Select State(s) / Geography:",
        options=all_states,
        default=st.session_state.selected_states,
        help="Select one or more of the 50 US States + District of Columbia"
    )

    # Month Selection Convenience Controls
    st.sidebar.subheader("Months")
    col_m1, col_m2 = st.sidebar.columns(2)
    if col_m1.button("Select All Months", use_container_width=True):
        st.session_state.selected_months = list(all_months)
    if col_m2.button("Clear Months", use_container_width=True):
        st.session_state.selected_months = []

    st.session_state.selected_months = st.sidebar.multiselect(
        "Select Month(s):",
        options=all_months,
        default=st.session_state.selected_months,
        help="Filter by chronological calendar months"
    )

    # Infant Sex Selector
    st.sidebar.subheader("Infant Sex")
    st.session_state.selected_sex = st.sidebar.radio(
        "Select Infant Sex:",
        options=["All", "Female", "Male"],
        index=["All", "Female", "Male"].index(st.session_state.selected_sex),
        horizontal=True
    )

    st.sidebar.markdown("---")

    # Reset Filters Button
    if st.sidebar.button("🔄 Reset All Filters", use_container_width=True, type="primary"):
        st.session_state.selected_states = list(all_states)
        st.session_state.selected_months = list(all_months)
        st.session_state.selected_sex = "All"
        st.rerun()

    # Active Filters Summary Pill
    st.sidebar.markdown("### 📊 Active Filter Summary")
    st.sidebar.caption(f"• **States**: {len(st.session_state.selected_states)} of {len(all_states)} selected")
    st.sidebar.caption(f"• **Months**: {len(st.session_state.selected_months)} of {len(all_months)} selected")
    st.sidebar.caption(f"• **Sex**: {st.session_state.selected_sex}")

    # ---------------------------------------------------------
    # 3. FILTER DATASET & DEFENSIVE CHECK
    # ---------------------------------------------------------
    filtered_df = filter_dataset(
        df,
        selected_states=st.session_state.selected_states,
        selected_months=st.session_state.selected_months,
        selected_sex=st.session_state.selected_sex
    )

    if filtered_df.empty:
        st.warning("⚠️ No birth observations found matching the selected filter criteria. Please adjust your sidebar filters.")
        st.stop()

    # ---------------------------------------------------------
    # 4. KPI CARDS
    # ---------------------------------------------------------
    total_births = filtered_df['Births'].sum()
    selected_states_count = filtered_df['State of Residence'].nunique()
    selected_months_count = filtered_df['Month'].nunique()

    # Monthly Average
    avg_births_per_month = total_births / selected_months_count if selected_months_count > 0 else 0

    # Highest State
    state_totals = filtered_df.groupby('State of Residence')['Births'].sum()
    top_state = state_totals.idxmax() if not state_totals.empty else "N/A"
    top_state_val = state_totals.max() if not state_totals.empty else 0

    # Peak Month
    month_totals = filtered_df.groupby('Month', observed=False)['Births'].sum()
    top_month = month_totals.idxmax() if not month_totals.empty else "N/A"
    top_month_val = month_totals.max() if not month_totals.empty else 0

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.markdown(
            f'<div class="kpi-card">'
            f'<div class="kpi-title">Total Selected Births</div>'
            f'<div class="kpi-value">{total_births:,.0f}</div>'
            f'<div class="kpi-sub">{(total_births/EXPECTED_TOTAL_BIRTHS)*100:.1f}% of national data</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with kpi2:
        st.markdown(
            f'<div class="kpi-card">'
            f'<div class="kpi-title">Geographies</div>'
            f'<div class="kpi-value">{selected_states_count} <span style="font-size: 1rem; color: #64748B;">/ 51</span></div>'
            f'<div class="kpi-sub">States & DC included</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with kpi3:
        st.markdown(
            f'<div class="kpi-card">'
            f'<div class="kpi-title">Avg Births / Month</div>'
            f'<div class="kpi-value">{avg_births_per_month:,.0f}</div>'
            f'<div class="kpi-sub">Across {selected_months_count} month(s)</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with kpi4:
        st.markdown(
            f'<div class="kpi-card">'
            f'<div class="kpi-title">Top Geography</div>'
            f'<div class="kpi-value">{top_state}</div>'
            f'<div class="kpi-sub">{top_state_val:,.0f} total births</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    with kpi5:
        st.markdown(
            f'<div class="kpi-card">'
            f'<div class="kpi-title">Peak Month</div>'
            f'<div class="kpi-value">{top_month}</div>'
            f'<div class="kpi-sub">{top_month_val:,.0f} total births</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # 5. DASHBOARD TABS
    # ---------------------------------------------------------
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overview",
        "🗺️ Geographic Analysis",
        "🚻 Monthly & Sex Analysis",
        "📋 Data Table & Download",
        "📚 About the Data"
    ])

    # ---------------------------------------------------------
    # TAB 1: OVERVIEW
    # ---------------------------------------------------------
    with tab1:
        st.subheader("National Birth Overview")
        col_map, col_trend = st.columns([1.1, 1])

        with col_map:
            st.plotly_chart(
                plot_choropleth_map(filtered_df),
                use_container_width=True,
                key="overview_choropleth_map"
            )

        with col_trend:
            st.plotly_chart(
                plot_monthly_trend(filtered_df, st.session_state.selected_sex),
                use_container_width=True,
                key="overview_monthly_trend"
            )

    # ---------------------------------------------------------
    # TAB 2: GEOGRAPHIC ANALYSIS
    # ---------------------------------------------------------
    with tab2:
        st.subheader("Geographic Distribution & Disparities")

        col_rank, col_topbot = st.columns(2)

        with col_rank:
            top_n_slider = st.slider("Select Top N States to Rank:", min_value=5, max_value=51, value=15, step=5)
            st.plotly_chart(
                plot_state_ranking(filtered_df, top_n=top_n_slider),
                use_container_width=True,
                key="geo_state_ranking"
            )

        with col_topbot:
            n_comp_slider = st.slider("Select Top vs Bottom Comparison Size:", min_value=3, max_value=10, value=5)
            st.plotly_chart(
                plot_top_bottom_comparison(filtered_df, n=n_comp_slider),
                use_container_width=True,
                key="geo_top_bottom_comp"
            )

        st.markdown("---")
        st.subheader("State-by-Month Seasonality Heatmap")
        st.plotly_chart(
            plot_state_month_heatmap(filtered_df),
            use_container_width=True,
            key="geo_seasonality_heatmap"
        )

    # ---------------------------------------------------------
    # TAB 3: MONTHLY & SEX ANALYSIS
    # ---------------------------------------------------------
    with tab3:
        st.subheader("Infant Sex Ratio & Monthly Seasonality")

        col_pie, col_ratio = st.columns([1, 1.2])

        with col_pie:
            st.plotly_chart(
                plot_sex_comparison(filtered_df),
                use_container_width=True,
                key="sex_donut_comparison"
            )

        with col_ratio:
            st.markdown("#### ⚖️ Biological Sex Ratio Analysis")
            female_total = filtered_df[filtered_df['Sex of Infant'] == 'Female']['Births'].sum()
            male_total = filtered_df[filtered_df['Sex of Infant'] == 'Male']['Births'].sum()

            sex_ratio = (male_total / female_total * 100) if female_total > 0 else 0

            st.markdown(f"""
            - **Male Births**: `{male_total:,.0f}` ({(male_total/total_births)*100:.2f}%)
            - **Female Births**: `{female_total:,.0f}` ({(female_total/total_births)*100:.2f}%)
            - **Secondary Sex Ratio**: **`{sex_ratio:.2f}` male births per 100 female births**

            > **Analytics Context for Students**:
            > Human natality data globally exhibits a baseline secondary sex ratio of approximately **105 male births per 100 female births**.
            > In this 2025 provisional CDC dataset, the observed ratio of `{sex_ratio:.2f}` aligns closely with historical human biological standards.
            """)

        st.markdown("---")
        st.plotly_chart(
            plot_monthly_trend(filtered_df, selected_sex="All"),
            use_container_width=True,
            key="sex_tab_monthly_trend_all"
        )

    # ---------------------------------------------------------
    # TAB 4: DATA TABLE & DOWNLOAD
    # ---------------------------------------------------------
    with tab4:
        st.subheader("Filtered Natality Dataset")
        st.write(f"Displaying **{len(filtered_df):,}** observations matching your active filter criteria.")

        display_df = filtered_df.copy()
        display_df['Births'] = display_df['Births'].apply(lambda x: f"{x:,}")

        st.dataframe(
            display_df[['State of Residence', 'State Code', 'Month', 'Month Code', 'Sex of Infant', 'Births']],
            use_container_width=True,
            hide_index=True
        )

        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv_data,
            file_name="filtered_cdc_natality_2025.csv",
            mime="text/csv",
            type="primary"
        )

    # ---------------------------------------------------------
    # TAB 5: ABOUT THE DATA
    # ---------------------------------------------------------
    with tab5:
        st.subheader("📚 Dataset Documentation & Student Guide")

        st.markdown("""
        ### Data Source & Attribution
        - **Data Provider**: Centers for Disease Control and Prevention (CDC) / National Center for Health Statistics (NCHS).
        - **Dataset Name**: Provisional Natality Statistics (2025).
        - **Scope**: 50 US States + District of Columbia (51 geographies total), covering 12 months for Male and Female births.

        ---

        ### Key Business Analytics Concepts

        #### 1. Why Counts Are Not Birth Rates
        * **Birth Count**: The absolute number of births occurring in a defined geographic area during a specified timeframe (e.g., *California had 380,000 births in 2025*).
        * **Crude Birth Rate**: The number of births per 1,000 people in a population per year.
        * **General Fertility Rate**: The number of births per 1,000 women of childbearing age (typically 15–44 years old).
        * **Why it matters**: A state like California or Texas records high birth **counts** primarily because it has a large total population. It does not automatically mean women in California have a higher fertility **rate** than women in Vermont.

        #### 2. Provisional Data Nature
        * Provisional counts are based on preliminary birth certificate records received by the NCHS.
        * Final annual natality reports released by the CDC may contain minor retroactive adjustments.

        ---

        ### ❓ Classroom Discussion Questions for Students
        1. **Geographic Volume**: Why is California's birth count so much higher than Wyoming's? What secondary data source (e.g., US Census Bureau population estimates) would you need to calculate Crude Birth Rates?
        2. **Seasonality**: Look at the monthly trend chart. Which months consistently show peak birth volume? What economic or cultural factors might explain this seasonal pattern?
        3. **Sex Ratios**: Why does the male birth count consistently exceed female births across nearly all states? Is this disparity statistically meaningful?
        """)


if __name__ == "__main__":
    main()
