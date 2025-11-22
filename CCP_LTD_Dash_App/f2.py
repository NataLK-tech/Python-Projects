#from preparation_data import result_df

import pandas as pd
import plotly.graph_objects as go


def create_fig_2(filtered_df: pd.DataFrame) -> go.Figure:
    filtered_df = filtered_df.sort_values(['Symbol', 'NormalizedQuarter'])

    unique_quarters = filtered_df['NormalizedQuarter'].dropna().unique()
    unique_quarters = pd.Series(unique_quarters).sort_values()
    if unique_quarters.empty:
        return go.Figure().update_layout(title="There is no data for the selected filters")

    quarter_labels = [pd.Timestamp(q).to_period('Q').strftime('%Y Q%q') for q in unique_quarters]

    # Y axis
    min_val = filtered_df['Ratio_CCP_LTD'].min()
    max_val = filtered_df['Ratio_CCP_LTD'].max()
    padding = (max_val - min_val) * 0.1 if max_val > min_val else 0.1
    y_range = [0, max_val + padding]

    fig_2 = go.Figure(layout=dict(width=600, height=500))

    x_min = unique_quarters.iloc[0]
    x_max = unique_quarters.iloc[-1]

    rectangles = [
        {"y0": 0, "y1": 0.2, "fillcolor": "rgba(255, 99, 71, 0.15)"},
        {"y0": 0.2, "y1": 0.5, "fillcolor": "rgba(255, 255, 102, 0.15)"},
        {"y0": 0.5, "y1": 1, "fillcolor": "rgba(135, 206, 250, 0.15)"},
        {"y0": 1, "y1": max_val + padding, "fillcolor": "rgba(144, 238, 144, 0.15)"}
    ]

    for rect in rectangles:
        fig_2.add_shape(
            type="rect",
            x0=x_min,
            x1=x_max,
            y0=rect["y0"],
            y1=rect["y1"],
            fillcolor=rect["fillcolor"],
            layer="below",
            line_width=0
        )

    companies = filtered_df['Symbol'].unique()

    for i, company in enumerate(companies):
        company_data = filtered_df[filtered_df['Symbol'] == company]
        if company_data.empty:
            continue

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

        company_data = company_data.sort_values('NormalizedQuarter')
        color = symbol_colors.get(company, '#000000')

        hovertext = [
            f"Company: {company}<br>Quarter: {q.to_period('Q').strftime('%Y Q%q')}<br>Ratio CCP/LTD: {val:.4f}"
            for q, val in zip(company_data['NormalizedQuarter'], company_data['Ratio_CCP_LTD'])
        ]

        fig_2.add_trace(
            go.Scatter(
                x=company_data['NormalizedQuarter'],
                y=company_data['Ratio_CCP_LTD'],
                mode='lines',
                name=f"{company}_Ratio",
                line=dict(color=color, width=2, dash='solid'),
                marker=dict(
                    color=color,
                    size=4,
                    line=dict(color='black', width=2),
                    opacity=0.8
                ),
                hovertext=hovertext,
                hovertemplate="%{hovertext}<extra></extra>",
                showlegend=False
            )
        )

    fig_2.add_hline(y=0, line_color='black', line_width=2, layer="below")

    fig_2.update_layout(
        title="Ratio CCP/LTD by Company",
        title_x=0.5,
        title_y=0.95,
        title_font=dict(family="Georgia", size=20, color="black", weight="bold"),
        xaxis=dict(
            title=dict(text="Quarter<br><br>"
                            "<span style='font-size:12px; color:gray; font-weight:100;'>"
                            "<i>The dynamics of the ratio between CCP and LTD.<br>"
                            "Values are distributed across ranges: below 0.2 — red,<br> "
                            "from 0.2 to 0.5 — yellow, from 0.5 to 1 — blue, above 1 — green.<i>"
                            "</span>",
                       font=dict(size=14, color="black", weight="bold")),
            tickangle=45,
            tickmode='array',
            tickvals=unique_quarters,
            ticktext=quarter_labels,
            showline=False,
            zeroline=False,
            showgrid=False
        ),
        yaxis=dict(
            title_text="Ratio CCP/LTD",
            title_font=dict(size=14, color="black", weight="bold"),
            showgrid=False,
            range=y_range,
            showline=True,
            linecolor='black',
            linewidth=1,
            zeroline=False
        ),
        plot_bgcolor="white",
        #showlegend=True,
        #legend_title="Companies"
    )

    return fig_2




