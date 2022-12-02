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


###  Project ############################################################################
data = pd.read_csv(r'C:\Users\asus\Downloads/Point_in_Time_Estimates_of_Homelessness_in_the_US_by_State.csv')

data.rename(columns = {'count_type' : 'homeless_type'} , inplace = True)
data = data[data['state']!= 'MP']
data = data[data['state']!='Total']
data['count'] = data['count'].astype(int)


pivoted_data = data.pivot_table(values='count', index = ['year' , 'state' ],   columns= 'homeless_type',    aggfunc= ['sum'],   margins = False)
pivoted_data.columns = pivoted_data.columns.to_series().str.join('')
pivoted_data.columns = pivoted_data.columns.str.replace("sum", "")
pivoted_data.reset_index(inplace = True)

pivoted_data_sliced = pivoted_data[pivoted_data['year'].isin([2015,2016,2017,2018])]
pivoted_data_sliced = pivoted_data_sliced.groupby('state').sum(['count'])

pivoted_data_top_10 = pivoted_data_2018.sort_values(by='Overall Homeless' , ascending = False).reset_index()[0:10]

fig3 = px.bar(pivoted_data_top_10, x="Overall Homeless", y="state", orientation='h' , title  = 'Top 10 States with Highest Overall Homelessness' ) #, hover_data=["tip", "size"],)
fig3.update_layout(yaxis={'categoryorder':'total ascending'})


###  Project ############################################################################


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
                
                html.Div([
                html.H1(children='Bye Dash'),

                html.Div(children='''  Dash: A web application framework for your data.   '''),
                dcc.Graph(id='example-graph',  figure=fig ) , 
                html.Div(children='''Dash: Another example for chart '''),
                dcc.Graph(id='example-graph2', figure=fig2 )
                        ])
            
            ])
            
            
            
    elif tab == 'tab-2':
        return html.Div([
            dcc.Graph(id='example-graph',  figure=fig3 ) 
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Tab content 3')
        ])
  
    
if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
