#from preparation_data import result_df

import numpy as np
import pandas as pd
import plotly.graph_objects as go

def create_fig_3(df):
    pivot_df = df.pivot(index='Symbol', columns='NormalizedQuarter', values='Ratio_CCP_LTD')

    quarter_labels = [pd.Timestamp(q).to_period('Q').strftime('%Y Q%q') for q in pivot_df.columns]

    max_val = np.nanmax(pivot_df.values)
    if np.isnan(max_val) or max_val <= 0:
        max_val = 1.0
    elif max_val < 1.0:
        max_val = 1.0

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

    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=quarter_labels,
        y=pivot_df.index,
        colorscale=colorscale,
        zmin=0,
        zmax=max_val,
        # ext=pivot_df.values,
        # texttemplate="%{text:.2f}",
        # textfont={"size": 12},
        hovertemplate="Company: %{y}<br>Quarter: %{x}<br>Ratio CCP/LTD: %{z:.4f}<extra></extra>",
    ))

    fig.update_layout(
        title="Ratio CCP/LTD Heatmap by Company and Quarter",
        title_x=0.5,
        title_y=0.95,
        title_font=dict(family="Georgia", size=20, color="black", weight="bold"),
        xaxis=dict(
            #title="Quarter",
            title="Quarter<br><br>"
                  "<span style='font-size:12px; color:gray; font-weight:100;'>"
                  "<i>Change in the level of companies financial stability by quarters.<br>"
                  "The higher the ratio, the greater the companies financial stability: <br> "
                  "green — high, blue — acceptable, yellow — optimal, red — critical.<i>"
                    "</span>",
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
        width=600,
        height=500
    )



    return fig



