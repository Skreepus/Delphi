"""
Reusable Plotly chart builders for the dashboard.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


PLOTLY_TEMPLATE = "plotly_dark"


def risk_distribution_chart(df: pd.DataFrame, score_col: str = "risk_score") -> go.Figure:
    """Histogram of satellite risk score distribution."""
    fig = px.histogram(
        df, x=score_col, nbins=30,
        title="Satellite Risk Score Distribution",
        color_discrete_sequence=["#00D4FF"],
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(showlegend=False)
    return fig


def top_risky_operators_chart(operator_df: pd.DataFrame, n: int = 15) -> go.Figure:
    """Horizontal bar chart of lowest-reliability operators."""
    top = operator_df.nsmallest(n, "reliability_score")
    fig = px.bar(
        top, x="reliability_score", y="operator", orientation="h",
        title=f"Top {n} Lowest-Reliability Operators",
        color="reliability_score",
        color_continuous_scale="RdYlGn",
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig


def dead_satellites_on_orbit_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart of operators with most inactive satellites still orbiting."""
    dead = (
        df[df["is_inactive"] == True]
        .groupby("operator")
        .size()
        .reset_index(name="count")
        .nlargest(15, "count")
    )
    fig = px.bar(
        dead, x="count", y="operator", orientation="h",
        title="Operators with Most Dead Satellites Still On Orbit",
        color_discrete_sequence=["#FF4444"],
        template=PLOTLY_TEMPLATE,
    )
    return fig
