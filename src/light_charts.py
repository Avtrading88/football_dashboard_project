import plotly.express as px

from src.light_config import APP_BG, TEXT_LIGHT, TEXT_MUTED, GRID_COLOR, COLOR_PALETTE


def chart_layout(fig, height=420):
    """Apply the light theme to each chart."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=APP_BG,
        font=dict(color=TEXT_LIGHT, size=12),
        height=height,
        margin=dict(l=10, r=10, t=50, b=20),
        title_font=dict(color=TEXT_LIGHT, size=18),
        xaxis=dict(
            gridcolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR,
            title_font=dict(color=TEXT_MUTED),
            tickfont=dict(color=TEXT_MUTED),
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            zerolinecolor=GRID_COLOR,
            title_font=dict(color=TEXT_MUTED),
            tickfont=dict(color=TEXT_MUTED),
        ),
        legend=dict(
            font=dict(color=TEXT_LIGHT),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
        ),
    )
    return fig


def make_horizontal_bar(data, x_col, y_col, color_col, title, x_title, y_title, height=430, show_legend=False):
    """Build one horizontal bar chart."""
    fig = px.bar(
        data,
        x=x_col,
        y=y_col,
        orientation="h",
        text=x_col,
        color=color_col,
        color_discrete_sequence=COLOR_PALETTE,
    )

    fig.update_traces(textposition="outside", textfont=dict(color=TEXT_LIGHT))
    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        showlegend=show_legend,
    )
    fig.update_yaxes(autorange="reversed")
    chart_layout(fig, height)
    return fig
