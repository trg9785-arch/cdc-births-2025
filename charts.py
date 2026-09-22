import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.data_loader import MONTH_ORDER

# Custom Accessible Color Palette
COLOR_FEMALE = "#E07A5F"  # Coral / Warm Terracotta
COLOR_MALE = "#2B547E"    # Deep Indigo / Navy
COLOR_TOTAL = "#008080"   # Teal
COLOR_ACCENT = "#81B29A"  # Soft Sage Green
COLOR_BG = "rgba(0,0,0,0)"

def apply_common_layout(fig, title_text, y_title="Birth Count", x_title=""):
    """Applies common visual styling, hover template, zero-based axis, and layout formatting."""
    fig.update_layout(
        title={
            'text': f"<b>{title_text}</b>",
            'y': 0.95,
            'x': 0.0,
            'xanchor': 'left',
            'yanchor': 'top',
            'font': dict(size=18)
        },
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_BG,
        font=dict(family="Arial, sans-serif", size=13),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hoverlabel=dict(bgcolor="white", font_size=13, font_family="Arial")
    )
    if y_title:
        fig.update_yaxes(title_text=y_title, rangemode="tozero", gridcolor="#E2E8F0")
    if x_title:
        fig.update_xaxes(title_text=x_title, gridcolor="#E2E8F0")
    return fig


def plot_monthly_trend(df: pd.DataFrame, selected_sex: str = "All"):
    """Plots chronological monthly birth trends, grouped by infant sex or as a total aggregate."""
    if df.empty:
        return go.Figure()

    if selected_sex == "All":
        # Group by Month and Sex
        monthly = df.groupby(['Month', 'Sex of Infant'], observed=False)['Births'].sum().reset_index()
        fig = px.line(
            monthly,
            x='Month',
            y='Births',
            color='Sex of Infant',
            markers=True,
            color_discrete_map={'Female': COLOR_FEMALE, 'Male': COLOR_MALE},
            labels={'Births': 'Birth Count', 'Month': 'Month'}
        )
        fig.update_traces(
            hovertemplate="<b>%{x}</b> (%{fullData.name})<br>Births: <b>%{y:,.0f}</b><extra></extra>",
            line=dict(width=3),
            marker=dict(size=8)
        )
    else:
        # Single sex trend line
        monthly = df.groupby('Month', observed=False)['Births'].sum().reset_index()
        color = COLOR_FEMALE if selected_sex == "Female" else COLOR_MALE
        fig = px.line(
            monthly,
            x='Month',
            y='Births',
            markers=True,
            labels={'Births': 'Birth Count', 'Month': 'Month'}
        )
        fig.update_traces(
            line=dict(color=color, width=3),
            marker=dict(size=8, color=color),
            hovertemplate="<b>%{x}</b><br>Births: <b>%{y:,.0f}</b><extra></extra>"
        )

    return apply_common_layout(
        fig,
        title_text=f"Monthly Birth Trend ({selected_sex} Infants)",
        x_title="Month of Birth",
        y_title="Total Birth Count"
    )


def plot_sex_comparison(df: pd.DataFrame):
    """Plots a donut chart comparing Female vs Male birth counts and relative percentage shares."""
    if df.empty:
        return go.Figure()

    sex_summary = df.groupby('Sex of Infant')['Births'].sum().reset_index()
    total_births = sex_summary['Births'].sum()

    fig = px.pie(
        sex_summary,
        names='Sex of Infant',
        values='Births',
        color='Sex of Infant',
        color_discrete_map={'Female': COLOR_FEMALE, 'Male': COLOR_MALE},
        hole=0.55
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate="<b>%{label} Infants</b><br>Birth Count: <b>%{value:,.0f}</b><br>Share of Births: <b>%{percent}</b><extra></extra>",
        marker=dict(line=dict(color='#FFFFFF', width=2))
    )
    fig.update_layout(
        title={'text': "<b>Sex Distribution (Female vs. Male)</b>", 'y': 0.95, 'x': 0.0, 'xanchor': 'left'},
        annotations=[dict(
            text=f"<b>Total</b><br>{total_births:,.0f}",
            x=0.5, y=0.5,
            font_size=16,
            showarrow=False
        )],
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_BG,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    return fig


def plot_state_ranking(df: pd.DataFrame, top_n: int = 15):
    """Plots a horizontal bar chart ranking the selected states by total birth count."""
    if df.empty:
        return go.Figure()

    state_summary = df.groupby('State of Residence')['Births'].sum().reset_index()
    state_summary = state_summary.sort_values(by='Births', ascending=True).tail(top_n)

    fig = px.bar(
        state_summary,
        x='Births',
        y='State of Residence',
        orientation='h',
        color='Births',
        color_continuous_scale='Teal',
        labels={'Births': 'Total Births', 'State of Residence': 'State'}
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Total Births: <b>%{x:,.0f}</b><extra></extra>"
    )
    fig.update_layout(coloraxis_showscale=False)
    return apply_common_layout(
        fig,
        title_text=f"Top {len(state_summary)} Geographies by Birth Count",
        x_title="Total Birth Count",
        y_title="State / Territory"
    )


def plot_choropleth_map(df: pd.DataFrame):
    """Plots an interactive US Choropleth map using 2-letter state postal abbreviations."""
    if df.empty:
        return go.Figure()

    state_map_df = df.groupby(['State Code', 'State of Residence'])['Births'].sum().reset_index()

    fig = px.choropleth(
        state_map_df,
        locations='State Code',
        locationmode="USA-states",
        color='Births',
        scope="usa",
        color_continuous_scale="Viridis",
        labels={'Births': 'Total Births'},
        hover_name='State of Residence'
    )
    fig.update_traces(
        hovertemplate="<b>%{hovertext} (%{location})</b><br>Total Births: <b>%{z:,.0f}</b><extra></extra>"
    )
    fig.update_layout(
        title={'text': "<b>Geographic Distribution of Provisional 2025 Birth Counts</b>", 'y': 0.95, 'x': 0.0},
        geo=dict(lakecolor='rgb(255, 255, 255)', bgcolor=COLOR_BG),
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor=COLOR_BG
    )
    return fig


def plot_state_month_heatmap(df: pd.DataFrame):
    """Plots a State vs. Month matrix heatmap showing seasonal birth patterns across states."""
    if df.empty:
        return go.Figure()

    # Pivot table with ordered months
    pivot = df.pivot_table(
        index='State of Residence',
        columns='Month',
        values='Births',
        aggfunc='sum',
        observed=False
    ).fillna(0)

    # Reorder columns to ensure strict chronological month order
    valid_months = [m for m in MONTH_ORDER if m in pivot.columns]
    pivot = pivot[valid_months]

    # Sort states alphabetically for clear lookup
    pivot = pivot.sort_index(ascending=False)

    fig = px.imshow(
        pivot,
        labels=dict(x="Month", y="State / Geography", color="Births"),
        x=pivot.columns,
        y=pivot.index,
        color_continuous_scale="Blues",
        aspect="auto"
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b> - %{x}<br>Birth Count: <b>%{z:,.0f}</b><extra></extra>"
    )
    fig.update_layout(
        title={'text': "<b>Seasonal Birth Density Matrix (State vs. Month)</b>", 'y': 0.95, 'x': 0.0},
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_BG,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig


def plot_top_bottom_comparison(df: pd.DataFrame, n: int = 5):
    """Plots a bar chart comparing the top N and bottom N states by total birth count."""
    if df.empty:
        return go.Figure()

    state_totals = df.groupby('State of Residence')['Births'].sum().reset_index()
    state_totals = state_totals.sort_values(by='Births', ascending=False)

    if len(state_totals) <= n * 2:
        comp_df = state_totals.copy()
        comp_df['Group'] = 'Selected Geographies'
    else:
        top_df = state_totals.head(n).copy()
        top_df['Group'] = f'Top {n}'
        bottom_df = state_totals.tail(n).copy()
        bottom_df['Group'] = f'Bottom {n}'
        comp_df = pd.concat([top_df, bottom_df])

    fig = px.bar(
        comp_df,
        x='State of Residence',
        y='Births',
        color='Group',
        color_discrete_map={f'Top {n}': COLOR_TOTAL, f'Bottom {n}': COLOR_FEMALE, 'Selected Geographies': COLOR_TOTAL},
        labels={'Births': 'Total Births', 'State of Residence': 'Geography'}
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b> (%{fullData.name})<br>Births: <b>%{y:,.0f}</b><extra></extra>"
    )
    return apply_common_layout(
        fig,
        title_text=f"Geographic Volume Disparity: Top {n} vs. Bottom {n} States",
        x_title="State / Geography",
        y_title="Total Birth Count"
    )
