from dash import Dash, dcc, html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
from census import Census

app = Dash(__name__)
server = app.server


tabs_styles = {
    'height': '44px'
}

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold',
    'font-family': 'Calibri, sans-serif'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px',
    'font-family': 'Calibri, sans-serif'
}


app.layout = html.Div([
    dcc.Tabs(id="tabs-styled-with-inline", value='tab-1', children=[
        dcc.Tab(label='Year Over Year Analysis', value='tab-1', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='By State Analysis', value='tab-2', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Homelessness Predictors', value='tab-3', style=tab_style, selected_style=tab_selected_style),
    ], style=tabs_styles),
    html.Div(id='tabs-content-inline')
])


@app.callback(Output('tabs-content-inline', 'children'),
              Input('tabs-styled-with-inline', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H1(children='Tab 2'),
        ])

    elif tab == 'tab-2':
        return html.Div([
            html.H1(children='Tab 2'),
        ])

    elif tab == 'tab-3':
        return html.Div([
            html.H3('Tab 3'),
        ])


if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
