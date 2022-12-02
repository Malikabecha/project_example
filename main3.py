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


data = pd.read_csv(r'https://storage.googleapis.com/assignment-data/Point_in_Time_Estimates_of_Homelessness_in_the_US_by_State.csv')

data.rename(columns = {'count_type' : 'homeless_type'} , inplace = True)
data = data[data['state']!= 'MP']
data = data[data['state']!='Total']
data['count'] = data['count'].astype(int)





######################### population from census

population_table = pd.DataFrame()
for i in range(2009,2019):
    c = Census("52b7c26667eed84927ca68b61e8cd4b3ff00f5f0" , year = i)
    
    df=pd.DataFrame(c.acs5.state('B01001_001E', Census.ALL))
    df['year']= i
    population_table = population_table.append(df)
    
population_table.rename(columns = {'B01001_001E':'population'} , inplace = True)

state_codes = {
    'WA': '53', 'DE': '10', 'DC': '11', 'WI': '55', 'WV': '54', 'HI': '15','FL': '12', 'WY': '56', 'PR': '72', 'NJ': '34', 'NM': '35', 'TX': '48',
    'LA': '22', 'NC': '37', 'ND': '38', 'NE': '31', 'TN': '47', 'NY': '36','PA': '42', 'AK': '02', 'NV': '32', 'NH': '33', 'VA': '51', 'CO': '08',
    'CA': '06', 'AL': '01', 'AR': '05', 'VT': '50', 'IL': '17', 'GA': '13','IN': '18', 'IA': '19', 'MA': '25', 'AZ': '04', 'ID': '16', 'CT': '09',
    'ME': '23', 'MD': '24', 'OK': '40', 'OH': '39', 'UT': '49', 'MO': '29','MN': '27', 'MI': '26', 'RI': '44', 'KS': '20', 'MT': '30', 'MS': '28',
    'SC': '45', 'KY': '21', 'OR': '41', 'SD': '46'}
state_codes = {v: k for k, v in state_codes.items()}
population_table['state'] = population_table['state'].map(state_codes) 

#################################################




pivoted_data = data.pivot_table(values='count', index = ['year' , 'state' ],   columns= 'homeless_type',    aggfunc= ['sum'],   margins = False)
pivoted_data.columns = pivoted_data.columns.to_series().str.join('')
pivoted_data.columns = pivoted_data.columns.str.replace("sum", "")
pivoted_data.reset_index(inplace = True)

pivoted_data.columns
pivoted_data_sliced = pivoted_data[pivoted_data['year'].isin([2018])].reset_index()

pivoted_data_sliced  = pd.merge(pivoted_data_sliced , population_table , left_on = ['year' , 'state'] , right_on = ['year' , 'state'] , how = 'left')



pivoted_data_sliced['Homelessness Rate' ] = pivoted_data_sliced['Overall Homeless' ]/ pivoted_data_sliced['population' ]
pivoted_data_sliced['Homelessness Rate - hover' ]  = pivoted_data_sliced['Homelessness Rate' ].apply(lambda x : '{:.2%}'.format(x))



### State Analysis 

fig_1_state = px.bar(pivoted_data_sliced.sort_values(by = 'Homelessness Rate' )[1:10], x="Homelessness Rate", y="state"
             , title  = 'Top 10 States with Highest Overall Homelessness' , hover_data=['Homelessness Rate - hover'],)


fig_1_state.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor':'rgba(0, 0, 0, 0)',
})



fig_2_state = go.Figure(data=go.Choropleth(
    locations=pivoted_data_sliced['state'], 
    z = pivoted_data_sliced['Homelessness Rate'], 
    locationmode = 'USA-states',
#    colorscale = 'Reds'
    hovertemplate = 'Overall Homeless: %{Overall Homeless}'

    ,text=pivoted_data_sliced['Homelessness Rate - hover'], 
    marker_line_color='white' 
))

fig_2_state.update_layout(
    title_text = 'The State-wise distribution of the Homelessness Rate',
    geo_scope='usa'
)


#
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
        return html.Div( children= [ html.Div([
            dcc.Graph(id='example-graph',  figure=fig_1_state ) , dcc.Graph(id='example-graph',  figure=fig_2_state ) 
        ]) , style={'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '3vw', 'margin-top': '3vw'}),
                        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Tab content 3')
        ])
  
    
if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
