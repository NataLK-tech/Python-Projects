#from preparation_data import result_df

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as sp

def create_fig_1(df: pd.DataFrame) -> go.Figure:
    df = df.sort_values(['Symbol', 'NormalizedQuarter'])

    unique_quarters = df['NormalizedQuarter'].dropna().unique()
    unique_quarters = pd.Series(unique_quarters).sort_values()
    if unique_quarters.empty:
        raise ValueError("No valid quarters found in the data.")
    quarter_labels = [pd.Timestamp(q).to_period('Q').strftime('%Y Q%q') for q in unique_quarters]

    min_val = min(df['CCP'].min(), df['LTD'].min(), 0)
    max_val = max(df['CCP'].max(), df['LTD'].max())
    padding = (max_val - min_val) * 0.1
    y_range = [max(0, min_val - padding), max_val + padding]

    fig = sp.make_subplots(specs=[[{"secondary_y": True}]],
                          figure=go.Figure(layout=dict(width=1300, height=400)))

    companies = df['Symbol'].unique()

    for i, company in enumerate(companies):
        company_data = df[df['Symbol'] == company].sort_values('NormalizedQuarter')
        color = px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]

        hovertext_ccp = [
            f"Company: {company}<br>Quarter: {q.to_period('Q').strftime('%Y Q%q')}<br>CCP: $ {val:.0f} M"
            for q, val in zip(company_data['NormalizedQuarter'], company_data['CCP'])
        ]

        fig.add_trace(
            go.Scatter(
                x=company_data['NormalizedQuarter'],
                y=company_data['CCP'],
                mode='lines',
                name=f"{company}_CCP",
                line=dict(color=color, width=2, dash='solid'),
                marker=dict(
                    color=color,
                    line=dict(color='black', width=2),
                    opacity=0.8
                ),
                hovertext=hovertext_ccp,
                hovertemplate="%{hovertext}<extra></extra>",
                showlegend=True
            ),
            secondary_y=False
        )

    for i, company in enumerate(companies):
        company_data = df[df['Symbol'] == company].sort_values('NormalizedQuarter')
        color = px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)]

        hovertext_ltd = [
            f"Company: {company}<br>Quarter: {q.to_period('Q').strftime('%Y Q%q')}<br>LTD: $ {val:.0f} M"
            for q, val in zip(company_data['NormalizedQuarter'], company_data['LTD'])
        ]

        fig.add_trace(
            go.Scatter(
                x=company_data['NormalizedQuarter'],
                y=company_data['LTD'],
                mode='lines',
                name=f"{company}_LTD",
                line=dict(color=color, width=2, dash='dash'),
                marker=dict(
                    color=color,
                    line=dict(color='black', width=2),
                    opacity=0.8
                ),
                hovertext=hovertext_ltd,
                hovertemplate="%{hovertext}<extra></extra>",
                showlegend=True
            ),
            secondary_y=True
        )

    fig.update_layout(
        updatemenus=[
            dict(
                active=2,
                buttons=list([
                    dict(label="CCP",
                         method="update",
                         args=[{"visible": [True] * len(companies) + [False] * len(companies)},
                               {"yaxis.visible": True, "yaxis2.visible": False,
                                "yaxis.title": "CCP, $ M", "yaxis2.title": "",
                                "yaxis.range": y_range, "yaxis2.range": y_range}]),
                    dict(label="LTD",
                         method="update",
                         args=[{"visible": [False] * len(companies) + [True] * len(companies)},
                               {"yaxis.visible": False, "yaxis2.visible": True,
                                "yaxis.title": "", "yaxis2.title": "LTD, $ M",
                                "yaxis.range": y_range, "yaxis2.range": y_range}]),
                    dict(label="Both",
                         method="update",
                         args=[{"visible": [True] * (2 * len(companies))},
                               {"yaxis.visible": True, "yaxis2.visible": True,
                                "yaxis.title": "CCP, $ M", "yaxis2.title": "LTD, $ M",
                                "yaxis.range": y_range, "yaxis2.range": y_range}])
                ]),
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=1.15,
                yanchor="top"
            )
        ]
    )

    fig.update_layout(
        title="CCP and LTD by Company",
        title_x=0.5,
        title_y=1,
        title_font=dict(family="Georgia", size=20, color="black", weight="bold"),
        xaxis=dict(
            title=dict(text="Quarter", font=dict(size=14, color="black", weight="bold")),
            tickangle=45,
            tickmode='array',
            tickvals=unique_quarters,
            ticktext=quarter_labels,
            showline=False,
            zeroline=True,
            zerolinecolor='black',
            zerolinewidth=2,
            showgrid=False
        ),
        plot_bgcolor="white",
        showlegend=True,
        legend_title="Companies:"
    )

    fig.update_yaxes(
        title_text="CCP, $ M",
        title_font=dict(size=14, color="black", weight="bold"),
        showgrid=False,
        range=y_range,
        showline=True,
        linecolor='black',
        linewidth=1,
        zeroline=True,
        zerolinecolor='black',
        zerolinewidth=2,
        secondary_y=False
    )
    fig.update_yaxes(
        title_text="LTD, $ M",
        title_font=dict(size=14, color="black", weight="bold"),
        showgrid=False,
        range=y_range,
        showline=True,
        linecolor='black',
        linewidth=1,
        zeroline=True,
        zerolinecolor='black',
        zerolinewidth=2,
        secondary_y=True
    )

    return fig






