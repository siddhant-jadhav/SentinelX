"""
SentinelX Chart Components
Plotly chart builders styled with the cybersecurity color palette.
"""
import plotly.graph_objects as go
import plotly.express as px
from frontend.utils.helpers import SEVERITY_COLORS, CHART_COLORS, SEVERITY_ORDER


def _base_layout(title: str = "", height: int = 400) -> dict:
    """Base Plotly layout configuration."""
    return dict(
        title=dict(
            text=title,
            font=dict(family="Inter", size=16, color="#1B2A4A"),
            x=0,
            xanchor="left",
        ),
        font=dict(family="Inter", color="#475569"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(
            font=dict(size=11),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#E2E8F0",
            borderwidth=1,
        ),
        hoverlabel=dict(
            bgcolor="white",
            font=dict(family="Inter", size=12, color="#1B2A4A"),
            bordercolor="#E2E8F0",
        ),
    )


def threat_trend_chart(daily_data: list[dict], height: int = 350) -> go.Figure:
    """
    Create an area chart showing daily threat volume trends.

    Args:
        daily_data: List of dicts with 'date' and 'count' keys.
    """
    dates = [d["date"] for d in daily_data]
    counts = [d["count"] for d in daily_data]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=counts,
        mode="lines",
        fill="tozeroy",
        line=dict(color="#0A84FF", width=2.5, shape="spline"),
        fillcolor="rgba(10, 132, 255, 0.08)",
        hovertemplate="<b>%{x}</b><br>Threats: %{y}<extra></extra>",
    ))

    layout = _base_layout("Daily Threat Volume", height)
    layout.update(
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor="#E2E8F0",
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#F0F2F6",
            showline=False,
            tickfont=dict(size=10),
        ),
    )
    fig.update_layout(**layout)
    return fig


def threats_by_type_chart(type_data: dict, height: int = 350) -> go.Figure:
    """
    Create a donut chart showing threats by indicator type.

    Args:
        type_data: Dictionary of type_name -> count.
    """
    labels = list(type_data.keys())
    values = list(type_data.values())

    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=CHART_COLORS[:len(labels)]),
        textinfo="label+percent",
        textfont=dict(size=11, family="Inter"),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
    ))

    layout = _base_layout("Threats by Indicator Type", height)
    layout.update(showlegend=True)
    fig.update_layout(**layout)
    return fig


def threats_by_severity_chart(severity_data: dict, height: int = 350) -> go.Figure:
    """
    Create a horizontal bar chart showing threats by severity level.

    Args:
        severity_data: Dictionary of severity_name -> count.
    """
    # Ensure consistent ordering
    ordered_severities = [s for s in SEVERITY_ORDER if s in severity_data]
    counts = [severity_data[s] for s in ordered_severities]
    colors = [SEVERITY_COLORS.get(s, "#6B7280") for s in ordered_severities]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=ordered_severities,
        x=counts,
        orientation="h",
        marker=dict(
            color=colors,
            cornerradius=6,
        ),
        text=counts,
        textposition="outside",
        textfont=dict(size=12, family="Inter", color="#475569"),
        hovertemplate="<b>%{y}</b><br>Count: %{x}<extra></extra>",
    ))

    layout = _base_layout("Threats by Severity", height)
    layout.update(
        xaxis=dict(showgrid=True, gridcolor="#F0F2F6", showline=False),
        yaxis=dict(showgrid=False, autorange="reversed"),
        bargap=0.3,
    )
    fig.update_layout(**layout)
    return fig


def daily_volume_chart(daily_data: list[dict], height: int = 350) -> go.Figure:
    """
    Create a bar chart with line overlay for daily volume.
    """
    dates = [d["date"] for d in daily_data]
    counts = [d["count"] for d in daily_data]

    fig = go.Figure()

    # Bar chart
    fig.add_trace(go.Bar(
        x=dates,
        y=counts,
        marker=dict(
            color="rgba(10, 132, 255, 0.3)",
            cornerradius=4,
        ),
        hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>",
        name="Daily Count",
    ))

    # Line overlay (moving average)
    if len(counts) >= 3:
        ma = []
        for i in range(len(counts)):
            start = max(0, i - 2)
            ma.append(sum(counts[start:i + 1]) / (i - start + 1))

        fig.add_trace(go.Scatter(
            x=dates,
            y=ma,
            mode="lines",
            line=dict(color="#00D4AA", width=2.5, shape="spline"),
            name="3-Day Avg",
            hovertemplate="Avg: %{y:.1f}<extra></extra>",
        ))

    layout = _base_layout("Daily Threat Volume", height)
    layout.update(
        xaxis=dict(showgrid=False, showline=True, linecolor="#E2E8F0"),
        yaxis=dict(showgrid=True, gridcolor="#F0F2F6", showline=False),
        barmode="overlay",
    )
    fig.update_layout(**layout)
    return fig


def community_pie_chart(stats: dict, height: int = 300) -> go.Figure:
    """
    Create a pie chart for community submission statuses.
    """
    labels = ["Approved", "Pending", "Rejected"]
    values = [
        stats.get("approved_count", 0),
        stats.get("pending_count", 0),
        stats.get("rejected_count", 0),
    ]
    colors = ["#10B981", "#F59E0B", "#EF4444"]

    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker=dict(colors=colors),
        textinfo="label+value",
        textfont=dict(size=11, family="Inter"),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
    ))

    layout = _base_layout("Community Submissions", height)
    fig.update_layout(**layout)
    return fig


def top_categories_chart(type_data: dict, height: int = 350) -> go.Figure:
    """
    Create a horizontal bar chart for top threat categories.
    """
    # Sort by count descending
    sorted_items = sorted(type_data.items(), key=lambda x: x[1], reverse=True)[:8]
    labels = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=labels,
        x=values,
        orientation="h",
        marker=dict(
            color=CHART_COLORS[:len(labels)],
            cornerradius=6,
        ),
        text=values,
        textposition="outside",
        textfont=dict(size=11, family="Inter", color="#475569"),
        hovertemplate="<b>%{y}</b><br>Count: %{x}<extra></extra>",
    ))

    layout = _base_layout("Top Threat Categories", height)
    layout.update(
        xaxis=dict(showgrid=True, gridcolor="#F0F2F6", showline=False),
        yaxis=dict(showgrid=False, autorange="reversed"),
        bargap=0.25,
    )
    fig.update_layout(**layout)
    return fig
