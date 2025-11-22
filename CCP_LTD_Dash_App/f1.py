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
                          figure=go.Figure(layout=dict(width=1200, height=500)))

    companies = df['Symbol'].unique()

    symbol_colors = {
        'AAPL': '#1f77b4',
        'AMGN': '#ff7f0e',
        'AMZN': '#2ca02c',
        'BBWI': '#d62728',
        'BMY': '#9467bd',
        'CNC': '#8c564b',
        'COP': '#e377c2',
        'GILD': '#7f7f7f',
        'HSIC': '#bcbd22',
        'KO': '#17becf',
        'TMO': '#aec7e8',
        'UPS': '#ffbb78'
    }

    for i, company in enumerate(companies):
        company_data = df[df['Symbol'] == company].sort_values('NormalizedQuarter')
        color = symbol_colors.get(company, '#000000')

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
        color = symbol_colors.get(company, '#000000')

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
                    dict(label="━━ 𝐂𝐂𝐏",
                         method="update",
                         args=[{"visible": [True] * len(companies) + [False] * len(companies)},
                               {"yaxis.visible": True, "yaxis2.visible": False,
                                "yaxis.title": "CCP, $ M", "yaxis2.title": "",
                                "yaxis.range": y_range, "yaxis2.range": y_range}]),
                    dict(label="- - -  𝐋𝐓𝐃",
                         method="update",
                         args=[{"visible": [False] * len(companies) + [True] * len(companies)},
                               {"yaxis.visible": False, "yaxis2.visible": True,
                                "yaxis.title": "", "yaxis2.title": "LTD, $ M",
                                "yaxis.range": y_range, "yaxis2.range": y_range}]),
                    dict(label="─── 𝐂𝐂𝐏, - - -  𝐋𝐓𝐃",
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
        title={
            'text': "<span style='font-size:18px; color:black; font-weight:200;'>"
                    "<i>The dynamics of Cash and Cash-equivalent Position (CCP) and Long-Term Debt (LTD) for several companies <br>over multiple years. "
                    "You can quickly identify trends and assess the financial stability of these companies.</i>"
                    "</span><br><br>"
                    "<span style='font-size:20px; color:black; font-weight:bold;'>CCP and LTD by Company</span>",
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.95,
            'yanchor': 'top'
        },
        margin=dict(t=150),

        xaxis=dict(
            title=dict(text="Quarter<br><br>"
                            "<span style='font-size:12px; color:gray; font-weight:100;'>"
                            "<i>Changes over time in the absolute values of CCP and LTD allow you to compare the scale and trends of different companies’ activities.<i>"
                            "</span>",
                       font=dict(size=14, color="black", weight="bold")),
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
        title_text="Cash and Cash Position, $ M",
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
        title_text="Long-Term Debt, $ M",
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









