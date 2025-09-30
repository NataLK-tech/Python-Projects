from created_data import result_df

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp


def create_fig_3(df):
    # Сводим данные в матрицу (pivot)
    pivot_df = df.pivot(index='Symbol', columns='NormalizedQuarter', values='Ratio_CCP_LTD')

    # Формируем метки кварталов
    quarter_labels = [pd.Timestamp(q).to_period('Q').strftime('%Y Q%q') for q in pivot_df.columns]

    # Определяем максимальное значение для шкалы цвета
    max_val = np.nanmax(pivot_df.values)
    if np.isnan(max_val) or max_val <= 0:
        max_val = 1.0
    elif max_val < 1.0:
        max_val = 1.0

    # Цветовая шкала
    colorscale = [
        [0.0, 'rgba(255, 0, 0, 0.5)'],
        [0.1999 / max_val, 'rgba(255, 182, 193, 0.5)'],
        [0.1999 / max_val, 'rgba(255, 255, 204, 0.5)'],
        [0.4999 / max_val, 'rgba(255, 215, 0, 0.5)'],
        [0.4999 / max_val, 'rgba(173, 216, 230, 0.2)'],
        [0.9999 / max_val, 'rgba(30, 144, 255, 0.3)'],
        [0.9999 / max_val, 'rgba(144, 238, 144, 0.3)'],
        [1.0, 'rgba(34, 139, 34, 0.5)']
    ]

    # Создаем фигуру с тепловой картой
    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=quarter_labels,
        y=pivot_df.index,
        colorscale=colorscale,
        zmin=0,
        zmax=max_val,
        text=pivot_df.values,
        texttemplate="%{text:.2f}",
        textfont={"size": 12},
        hovertemplate="Company: %{y}<br>Quarter: %{x}<br>Ratio CCP/LTD: %{z:.4f}<extra></extra>",
    ))

    # Оформление
    fig.update_layout(
        title="Ratio CCP/LTD Heatmap by Company and Quarter",
        title_x=0.5,
        title_y=0.95,
        title_font=dict(family="Georgia", size=20, color="black", weight="bold"),
        xaxis=dict(
            title="Quarter",
            title_font=dict(size=14, color="black", weight="bold"),
            tickangle=45,
            showgrid=False
        ),
        yaxis=dict(
            title="Company",
            title_font=dict(size=14, color="black", weight="bold"),
            showgrid=False
        ),
        plot_bgcolor="white",
        width=1200,
        height=600
    )

    return fig
