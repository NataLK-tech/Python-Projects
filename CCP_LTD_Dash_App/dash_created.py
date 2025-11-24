# pip install dash

from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import os

from preparation_data_2 import result_df
from f1 import create_fig_1
from f2 import create_fig_2
from f3 import create_fig_3

# Info for filters
result_df['year'] = result_df['NormalizedQuarter'].dt.year

companies = sorted(result_df['Symbol'].dropna().unique())
min_year = int(result_df['year'].min())
max_year = int(result_df['year'].max())

# created Dash
app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Div([
            html.H1("Trends of CCP & LTD", style={
                'margin': '0',
                'fontSize': '46px'
            })
        ], style={'width': '60%', 'display': 'flex', 'alignItems': 'center'}),


        html.Div([
            html.Label("Choose a company:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='company-dropdown',
                options=[{'label': 'All companies', 'value': 'ALL'}] + [{'label': c, 'value': c} for c in companies],
                value=['ALL'],
                multi=True,
                placeholder="Select one or more companies"
            )
        ], style={'width': '20%', 'marginLeft': '20px', 'marginRight': '20px'}),

        html.Div([
            html.Label("Select a range of years:", style={'fontWeight': 'bold'}),
            dcc.RangeSlider(
                id='year-slider',
                min=min_year,
                max=max_year,
                step=1,
                value=[min_year, max_year],
                marks={str(y): str(y) for y in range(min_year, max_year + 1)}
            )
        ], style={'width': '20%'})
    ], style={
        'display': 'flex',
        'flexDirection': 'row',
        'alignItems': 'center',
        'justifyContent': 'space-between',
        'padding': '20px',
        'maxWidth': '1300px',
        'margin': '0 auto'
    }),

    dcc.Graph(id='graph-1', style={'margin': '20px'}),

    html.Div([
        dcc.Graph(id='graph-2', style={'marginRight': '10px', 'width': '600px'}),
        dcc.Graph(id='graph-3', style={'marginLeft': '10px', 'width': '600px'})
    ], style={
        'display': 'flex',
        'flexDirection': 'row',
        'justifyContent': 'center',
        #'margin': '0 20px 20px 20px',
        'maxWidth': '1300px',
        'margin': '0 auto'
    })
])

@app.callback(
    Output('company-dropdown', 'options'),
    Output('company-dropdown', 'value'),
    Input('company-dropdown', 'value'),
    prevent_initial_call=True
)
def filter_companies(selected):
    if not selected:
        return (
            [{'label': 'All companies', 'value': 'ALL'}] + [{'label': c, 'value': c} for c in companies],
            []
        )
    if 'ALL' in selected:
        return (
            [{'label': 'All companies', 'value': 'ALL'}],
            ['ALL']
        )
    else:
        return (
            [{'label': 'All companies', 'value': 'ALL'}] + [{'label': c, 'value': c} for c in companies],
            [v for v in selected if v != 'ALL']
        )

@app.callback(
    [Output('graph-1', 'figure'),
     Output('graph-2', 'figure'),
     Output('graph-3', 'figure')],
    [Input('company-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_graphs(selected_companies, selected_year_range):
    if not selected_companies:
        return go.Figure(), go.Figure(), go.Figure()

    if 'ALL' in selected_companies:
        filtered_companies = companies
    else:
        filtered_companies = selected_companies

    filtered_df = result_df[
        (result_df['Symbol'].isin(filtered_companies)) &
        (result_df['year'] >= selected_year_range[0]) &
        (result_df['year'] <= selected_year_range[1])
    ]

    if filtered_df.empty:
        return go.Figure(), go.Figure(), go.Figure()

    fig1 = create_fig_1(filtered_df)
    fig2 = create_fig_2(filtered_df)
    fig3 = create_fig_3(filtered_df)
    return fig1, fig2, fig3

if __name__ == '__main__':
    if os.environ.get('RENDER') == 'true':
        port = int(os.environ.get('PORT', 8051))
        app.run(debug=True, host='0.0.0.0', port=port)
    else:
        app.run(debug=True, port=8051)



