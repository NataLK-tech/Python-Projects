# pip install dash
# pip show dash - проверка версии даш в строке терминала

import dash
from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go

from created_data import result_df
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
    html.H1("CCP / LTD Dashboard", style={'textAlign': 'left', 'margin': '20px'}),

    # Внешний контейнер для фильтров
    html.Div([
        # Фильтр компаний
        html.Div([
            html.Label("Choose a company:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='company-dropdown',
                options=[{'label': 'All companies', 'value': 'ALL'}] + [{'label': c, 'value': c} for c in companies],
                value=['ALL'],
                multi=True,
                placeholder="Select one or more companies"
            )
        ], style={'width': '50%', 'marginRight': '20px'}),

        # Слайдер годов
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
        ], style={'width': '50%'})
    ], style={  # ← теперь всё правильно закрыто
        'display': 'flex',
        'flexDirection': 'row',
        'margin': '20px'
    }),

    # Графики
    dcc.Graph(id='graph-1', style={'margin': '20px'}),
    dcc.Graph(id='graph-2', style={'margin': '20px'}),
    dcc.Graph(id='graph-3', style={'margin': '20px'})
])

# Callback
@app.callback(
    [Output('graph-1', 'figure'),
     Output('graph-2', 'figure'),
     Output('graph-3', 'figure')],
     [Input('company-dropdown', 'value'),
     Input('year-slider', 'value')]
)

def update_graphs(selected_companies, selected_year_range):
    # Если выбрано "ALL", заменяем на список всех компаний
    if 'ALL' in selected_companies:
        filtered_companies = companies
    else:
        filtered_companies = selected_companies

    # Фильтрация данных
    filtered_df = result_df[
        (result_df['Symbol'].isin(filtered_companies)) &
        (result_df['year'] >= selected_year_range[0]) &
        (result_df['year'] <= selected_year_range[1])
    ]

    if filtered_df.empty:
        return go.Figure(), go.Figure(), go.Figure()

    # Построение графиков
    fig1 = create_fig_1(filtered_df)
    fig2 = create_fig_2(filtered_df)
    fig3 = create_fig_3(filtered_df)
    return fig1, fig2, fig3

if __name__ == '__main__':
    app.run(debug=True, port=8051)