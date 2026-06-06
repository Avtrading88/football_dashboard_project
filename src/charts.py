import plotly.express as px

from src.config import APP_BG, TEXT_LIGHT, COLOR_PALETTE


def chart_layout(fig, height=420):
    """Apply the same design to each chart."""
    fig.update_layout(
        paper_bgcolor=APP_BG,
        plot_bgcolor=APP_BG,
        font=dict(color=TEXT_LIGHT, size=12),
        height=height,
        margin=dict(l=10, r=10, t=50, b=20),
        xaxis=dict(
            gridcolor="rgba(147,164,184,0.14)",
            zerolinecolor="rgba(147,164,184,0.14)",
            title_font=dict(color=TEXT_LIGHT),
            tickfont=dict(color=TEXT_LIGHT),
        ),
        yaxis=dict(
            gridcolor="rgba(147,164,184,0.14)",
            zerolinecolor="rgba(147,164,184,0.14)",
            title_font=dict(color=TEXT_LIGHT),
            tickfont=dict(color=TEXT_LIGHT),
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

    fig.update_traces(textposition="outside")
    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        showlegend=show_legend,
    )
    fig.update_yaxes(autorange="reversed")
    chart_layout(fig, height)
    return fig
