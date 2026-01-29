"""
Componente grafice reutilizabile
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import Optional


# Paletă de culori standard
COLORS = {
    "primary": "#1E3A5F",
    "secondary": "#457B9D",
    "accent": "#E63946",
    "success": "#2A9D8F",
    "warning": "#F4A261",
    "light": "#A8DADC",
    "background": "#F1FAEE"
}

COUNTY_COLORS = {
    "Timiș": "#1E3A5F",
    "Arad": "#2E5A8F",
    "Hunedoara": "#4E7ABF",
    "Caraș-Severin": "#7E9ACF"
}


def create_kpi_card(
    title: str,
    value: str,
    delta: Optional[str] = None,
    delta_color: str = "normal"
) -> dict:
    """
    Creează datele pentru un card KPI.
    """
    return {
        "title": title,
        "value": value,
        "delta": delta,
        "delta_color": delta_color
    }


def create_line_chart(
    x_data: list,
    y_data: dict,
    title: str = "",
    x_title: str = "An",
    y_title: str = "Valoare",
    height: int = 400
) -> go.Figure:
    """
    Creează un grafic liniar cu multiple serii.

    Args:
        x_data: Valori pentru axa X
        y_data: Dict cu {nume_serie: [valori]}
        title: Titlul graficului
        x_title: Eticheta axei X
        y_title: Eticheta axei Y
        height: Înălțimea graficului
    """
    fig = go.Figure()

    colors = list(COLORS.values())

    for i, (name, values) in enumerate(y_data.items()):
        fig.add_trace(go.Scatter(
            x=x_data,
            y=values,
            name=name,
            mode="lines+markers",
            line=dict(color=colors[i % len(colors)], width=2)
        ))

    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=height,
        hovermode="x unified"
    )

    return fig


def create_bar_chart(
    x_data: list,
    y_data: list,
    title: str = "",
    x_title: str = "",
    y_title: str = "",
    color: str = None,
    horizontal: bool = False,
    height: int = 400
) -> go.Figure:
    """
    Creează un grafic cu bare.
    """
    fig = go.Figure()

    if horizontal:
        fig.add_trace(go.Bar(
            y=x_data,
            x=y_data,
            orientation='h',
            marker_color=color or COLORS["primary"]
        ))
    else:
        fig.add_trace(go.Bar(
            x=x_data,
            y=y_data,
            marker_color=color or COLORS["primary"]
        ))

    fig.update_layout(
        title=title,
        xaxis_title=y_title if horizontal else x_title,
        yaxis_title=x_title if horizontal else y_title,
        height=height
    )

    return fig


def create_grouped_bar_chart(
    x_data: list,
    y_data: dict,
    title: str = "",
    x_title: str = "",
    y_title: str = "",
    height: int = 400
) -> go.Figure:
    """
    Creează un grafic cu bare grupate.
    """
    fig = go.Figure()

    colors = list(COLORS.values())

    for i, (name, values) in enumerate(y_data.items()):
        fig.add_trace(go.Bar(
            x=x_data,
            y=values,
            name=name,
            marker_color=colors[i % len(colors)]
        ))

    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        barmode='group',
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=height
    )

    return fig


def create_pie_chart(
    labels: list,
    values: list,
    title: str = "",
    hole: float = 0.3,
    height: int = 400
) -> go.Figure:
    """
    Creează un grafic pie/donut.
    """
    fig = go.Figure()

    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=hole,
        marker=dict(colors=list(COUNTY_COLORS.values()))
    ))

    fig.update_layout(
        title=title,
        height=height
    )

    return fig


def create_dual_axis_chart(
    x_data: list,
    y1_data: list,
    y2_data: list,
    y1_name: str,
    y2_name: str,
    y1_title: str,
    y2_title: str,
    title: str = "",
    height: int = 400
) -> go.Figure:
    """
    Creează un grafic cu axă Y duală.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x_data,
        y=y1_data,
        name=y1_name,
        yaxis="y",
        line=dict(color=COLORS["primary"], width=2)
    ))

    fig.add_trace(go.Scatter(
        x=x_data,
        y=y2_data,
        name=y2_name,
        yaxis="y2",
        line=dict(color=COLORS["accent"], width=2, dash="dash")
    ))

    fig.update_layout(
        title=title,
        xaxis=dict(title="An"),
        yaxis=dict(title=y1_title, side="left", showgrid=False),
        yaxis2=dict(title=y2_title, side="right", overlaying="y", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=height,
        hovermode="x unified"
    )

    return fig


def create_heatmap(
    z_data: list,
    x_labels: list,
    y_labels: list,
    title: str = "",
    height: int = 400
) -> go.Figure:
    """
    Creează o hartă de căldură / matrice de corelație.
    """
    fig = px.imshow(
        z_data,
        x=x_labels,
        y=y_labels,
        color_continuous_scale="RdBu_r",
        aspect="auto",
        text_auto=".2f"
    )

    fig.update_layout(
        title=title,
        height=height
    )

    return fig


def create_treemap(
    labels: list,
    parents: list,
    values: list,
    title: str = "",
    height: int = 400
) -> go.Figure:
    """
    Creează un treemap.
    """
    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        marker=dict(
            colors=values,
            colorscale='Blues'
        )
    ))

    fig.update_layout(
        title=title,
        height=height
    )

    return fig


def create_gauge(
    value: float,
    title: str = "",
    min_val: float = 0,
    max_val: float = 100,
    thresholds: dict = None,
    height: int = 300
) -> go.Figure:
    """
    Creează un indicator de tip gauge.

    Args:
        thresholds: Dict cu praguri {"low": 30, "medium": 70}
    """
    if thresholds is None:
        thresholds = {"low": 30, "medium": 70}

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': COLORS["primary"]},
            'steps': [
                {'range': [min_val, thresholds["low"]], 'color': COLORS["accent"]},
                {'range': [thresholds["low"], thresholds["medium"]], 'color': COLORS["warning"]},
                {'range': [thresholds["medium"], max_val], 'color': COLORS["success"]}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))

    fig.update_layout(height=height)

    return fig
