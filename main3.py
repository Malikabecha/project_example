from dash import Dash, dcc, html
#import dash_core_components as dcc
#import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output

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

df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

df2 = pd.read_csv('https://gist.githubusercontent.com/chriddyp/5d1ea79569ed194d432e56108a04d188/raw/a9f9e8076b837d541398e999dcbac2b2826a81f8/gdp-life-exp-2007.csv')

fig2 = px.scatter(df2, x="gdp per capita", y="life expectancy",
                 size="population", color="continent", hover_name="country",
                 log_x=True, size_max=60)




app.layout = html.Div([
    dcc.Tabs(id="tabs-styled-with-inline", value='tab-1', children=[
        dcc.Tab(label='Year Over Year Analysis', value='tab-1', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='By State Analysis', value='tab-2', style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Homelessness Predictors', value='tab-3', style=tab_style, selected_style=tab_selected_style),
 #       dcc.Tab(label='Tab 4', value='tab-4', style=tab_style, selected_style=tab_selected_style),
    ], style=tabs_styles),
    html.Div(id='tabs-content-inline')
])

@app.callback(Output('tabs-content-inline', 'children'),
              Input('tabs-styled-with-inline', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
                html.H1(children='Bye Dash'),

                html.Div(children='''  Dash: A web application framework for your data.   '''),
                dcc.Graph(id='example-graph',  figure=fig ) , 
                html.Div(children='''Dash: Another example for chart '''),
                dcc.Graph(id='example-graph2', figure=fig2 )
                        ])
            
            
            
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Tab content 2')
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Tab content 3')
        ])
  
    
if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
