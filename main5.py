import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

yoy_analysis = dbc.Container(dcc.Graph(figure={"data": [{"x": [1, 2, 3], "y": [1, 4, 9]}]}))
state_level_analysis = dbc.Container([
            dbc.Row([  dbc.Col([ html.H3("Enter name:"),  ]) ,      dbc.Col([ html.H3("MAloukaaa"),  ])     ]),
            dbc.Row([  dbc.Col([ html.H3("Contributions to prediction:"),  ]), ]),
            dbc.Row([  dbc.Col([ html.H3("Every tree in the Random Forest:"), ]), ])
        ])




app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([dbc.Tabs(
    [
        dbc.Tab(yoy_analysis, label="YOY Analysis"),
        dbc.Tab(state_level_analysis, label="State Level Analysis")
        ]
    )])

if __name__ == "__main__":
    app.run_server()
