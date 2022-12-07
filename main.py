
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
from census import Census
import plotly.graph_objects as go

#from dash import Dash, dcc, html



#####################################  Cleaning steps ############################################################################


data = pd.read_csv(r'https://storage.googleapis.com/assignment-data/Point_in_Time_Estimates_of_Homelessness_in_the_US_by_State.csv')

data.rename(columns = {'count_type' : 'homeless_type'} , inplace = True)
data = data[data['state']!= 'MP']
data = data[data['state']!='Total']
data['count'] = data['count'].astype(int)

#########



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

###Median Rent
median_contract_rent = pd.DataFrame()
for i in range(2009,2019):
    c = Census("52b7c26667eed84927ca68b61e8cd4b3ff00f5f0" , year = i)
    
    df=pd.DataFrame(c.acs5.state('B25058_001E', Census.ALL))
    df['year']= i
    median_contract_rent = median_contract_rent.append(df)
    
median_contract_rent.rename(columns = {'B25058_001E':'median_contract_rent'} , inplace = True)

median_contract_rent[median_contract_rent['year'] == 2015]
median_contract_rent['state'] = median_contract_rent['state'].map(state_codes) 



                                                       
                                                       
##############################################


pivoted_data = data.pivot_table(values='count', index = ['year' , 'state' ],   columns= 'homeless_type',    aggfunc= ['sum'],   margins = False)
pivoted_data.columns = pivoted_data.columns.to_series().str.join('')
pivoted_data.columns = pivoted_data.columns.str.replace("sum", "")

pivoted_data.reset_index(inplace = True)

states_dictionary = pd.read_csv(r'https://raw.githubusercontent.com/cphalpert/census-regions/master/us%20census%20bureau%20regions%20and%20divisions.csv')


pivoted_data = pd.merge(pivoted_data , states_dictionary, left_on = 'state' ,right_on = 'State Code' , how = 'left')
pivoted_data  = pd.merge(pivoted_data , population_table , left_on = ['year' , 'state'] , right_on = ['year' , 'state'] , how = 'left')



pivoted_data['Homelessness Rate' ] = pivoted_data['Overall Homeless' ]/ pivoted_data['population' ]
pivoted_data['Homelessness Rate ' ] = pivoted_data['Homelessness Rate' ].apply(lambda x : '{:.2%}'.format(x))



selected_year = 2018
pivoted_data_sliced = pivoted_data[pivoted_data['year'].isin([selected_year])].reset_index()

def state_level_summary (selected_year=2018):
    pivoted_data_sliced = pivoted_data[pivoted_data['year'].isin([selected_year])].reset_index()
    yoy_homeless = pd.merge(pivoted_data_sliced.groupby('Region').sum('Overall Homeless')['Overall Homeless'], 
                        pivoted_data[pivoted_data['year'].isin([selected_year-1])][['Region' , 'Overall Homeless']].groupby('Region').sum('Overall Homeless')['Overall Homeless'], 
                        how = 'left',
                        on = 'Region').rename(columns = {'Overall Homeless_y':'Prior Year Overall Homeless',
                                                        'Overall Homeless_x':'Overall Homeless during {x}'.format(x=selected_year)})


    yoy_homeless['Overall Homeless Distribution'] = yoy_homeless['Overall Homeless during {x}'.format(x=selected_year)]/yoy_homeless['Overall Homeless during {x}'.format(x=selected_year)].sum()  
    yoy_homeless[['Overall Homeless during {x}'.format(x=selected_year) , 'Prior Year Overall Homeless']] = yoy_homeless[['Overall Homeless during {x}'.format(x=selected_year) , 'Prior Year Overall Homeless']].astype(int)

    yoy_homeless['Percent change vs prior Year'] = (yoy_homeless['Overall Homeless during {x}'.format(x=selected_year)]/yoy_homeless['Prior Year Overall Homeless']) -1

    yoy_homeless['Percent change vs prior Year']  = yoy_homeless['Percent change vs prior Year'].apply(lambda x : '{:.2%}'.format(x))
    yoy_homeless['Overall Homeless Distribution']=yoy_homeless['Overall Homeless Distribution'].apply(lambda x : '{:.2%}'.format(x))


    yoy_homeless = yoy_homeless[['Overall Homeless Distribution' , 'Overall Homeless during {x}'.format(x=selected_year) , 'Percent change vs prior Year']].sort_values(by = 'Overall Homeless during {x}'.format(x=selected_year) ,  ascending = False)
    return yoy_homeless


def top_10_highest_homeless_rate(selected_year = 2018):
    pivoted_data_sliced = pivoted_data[pivoted_data['year'].isin([selected_year])].reset_index()
    fig_1_state = px.bar(pivoted_data_sliced.sort_values(by = 'Homelessness Rate' , ascending = True )[0:10], x="Homelessness Rate", y="state" , orientation = 'h'
             , title  = 'Top 10 States with Highest Homelessness Rate' , custom_data =['Homelessness Rate ' , 'Homelessness Rate' ],)


    fig_1_state.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor':'rgba(0, 0, 0, 0)',
    } , width = 450 , height  = 450)


    fig_1_state.update_traces(
        hovertemplate="<br>".join([
            "State: %{x}",
            "Homelessness Rate: %{customdata[0]}"
        ])
    )
    return fig_1_state






### Fig1 - Tab: State-wise Analysis - Summary table 

yoy_homeless = pd.merge(pivoted_data_sliced.groupby('Region').sum('Overall Homeless')['Overall Homeless'], 
                        pivoted_data[pivoted_data['year'].isin([selected_year-1])][['Region' , 'Overall Homeless']].groupby('Region').sum('Overall Homeless')['Overall Homeless'], 
                        how = 'left',
                        on = 'Region').rename(columns = {'Overall Homeless_y':'Prior Year Overall Homeless',
                                                        'Overall Homeless_x':'Overall Homeless during {x}'.format(x=selected_year)})


yoy_homeless['Overall Homeless Distribution'] = yoy_homeless['Overall Homeless during {x}'.format(x=selected_year)]/yoy_homeless['Overall Homeless during {x}'.format(x=selected_year)].sum()  
yoy_homeless[['Overall Homeless during {x}'.format(x=selected_year) , 'Prior Year Overall Homeless']] = yoy_homeless[['Overall Homeless during {x}'.format(x=selected_year) , 'Prior Year Overall Homeless']].astype(int)

yoy_homeless['Percent change vs prior Year'] = (yoy_homeless['Overall Homeless during {x}'.format(x=selected_year)]/yoy_homeless['Prior Year Overall Homeless']) -1

yoy_homeless['Percent change vs prior Year']  = yoy_homeless['Percent change vs prior Year'].apply(lambda x : '{:.2%}'.format(x))
yoy_homeless['Overall Homeless Distribution']=yoy_homeless['Overall Homeless Distribution'].apply(lambda x : '{:.2%}'.format(x))


yoy_homeless = yoy_homeless[['Overall Homeless Distribution' , 'Overall Homeless during {x}'.format(x=selected_year) , 'Percent change vs prior Year']].sort_values(by = 'Overall Homeless during {x}'.format(x=selected_year) ,  ascending = False)





### Fig2 - Tab: State-wise Analysis - Top 10 states with highest Homelessness Rate

fig_1_state = px.bar(pivoted_data_sliced.sort_values(by = 'Homelessness Rate' , ascending = True )[0:10], x="Homelessness Rate", y="state" , orientation = 'h'
             , title  = 'Top 10 States with Highest Homelessness Rate' , custom_data =['Homelessness Rate ' , 'Homelessness Rate' ],)


fig_1_state.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor':'rgba(0, 0, 0, 0)',
} , width = 450 , height  = 450)


fig_1_state.update_traces(
    hovertemplate="<br>".join([
        "State: %{x}",
        "Homelessness Rate: %{customdata[0]}"
    ])
)



### Fig3 - Tab: State-wise Analysis - Top 10 states with highest Overall homeless
fig_3_state = px.bar(pivoted_data_sliced.sort_values(by = 'Overall Homeless' , ascending = True )[0:10], x="Overall Homeless", y="state" , orientation = 'h'
             , title  = 'Top 10 States with Highest Overall Homelessness'  ,  custom_data =['Overall Homeless' , 'Homelessness Rate' ],)


fig_3_state.update_layout({
'plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor':'rgba(0, 0, 0, 0)',
} , width = 450 , height  = 450
 ,colorway =['green'])


fig_3_state.update_traces(marker_color='orange',
    hovertemplate="<br>".join([
        "State: %{x}",
        "Overall Homeless: %{customdata[0]}"
    ])
)




### Fig4 - Tab: State-wise Analysis - Map - distribution of Homelessness Rate

fig_2_state = go.Figure(data=go.Choropleth(
    locations=pivoted_data_sliced['state'], 
    z = pivoted_data_sliced['Homelessness Rate'], 
    locationmode = 'USA-states',
#    colorscale = 'Reds'
 

    text=pivoted_data_sliced['Homelessness Rate '], 
    marker_line_color='white' , customdata =['Homelessness Rate ' , 'Homelessness Rate' ]
))

fig_2_state.update_layout(
    title_text = 'The State-wise distribution of the Homelessness Rate',
    geo_scope='usa'  , width = 800 , height  = 450
)

fig_2_state.update_traces(
    hovertemplate="<br>".join([
        "Overall Homeless: %{locations}",
        "ColY: %{y}",
        "Col1: %{customdata[0]}",
        "Col2: %{customdata[1]}",
        "Col3: %{customdata[2]}",
    ])
)

drop_down = dcc.Dropdown(id = "selected_year" 
             , options = [
                 {'label':'2015' , 'value':2015},
                 {'label':'2016' , 'value':2016},
                 {'label':'2017' , 'value':2017},
                 {'label':'2018' , 'value':2018},
                         ]
             , multi = False
             , value = 2018 
             , style = {'width' : '60%' }
            ),


yoy_analysis = dbc.Container(dcc.Graph(figure={"data": [{"x": [1, 2, 3], "y": [1, 4, 9]}]}))
state_level_analysis = dbc.Container([
            
            #dbc.Row([  dbc.Col([ dbc.Table.from_dataframe(   yoy_homeless, striped=False, bordered=True, hover=True, index=True , size = 'sm'), ]  ) ,    ]),
            dbc.Row([ html.Div(id = 'kassra' , children = {} ) ]),
            dbc.Row([    dbc.Col( )  , dbc.Col( ) ,  dbc.Col( drop_down    ) , ]),
            dbc.Row([  dbc.Col([ dcc.Graph(id="fig_3_state",figure =fig_3_state ,  style={'display': 'inline-block'}) ,  ]) ,    dbc.Col([ dcc.Graph(id="fig_2_state",figure =fig_2_state ,  style={'display': 'inline-block'}) ,  ]) ,         ]),
            dbc.Row([  dbc.Col([ dcc.Graph(id="fig_1_state",figure ={} ,  style={'display': 'inline-block'}) ,  ]) , dbc.Col([ dbc.Table.from_dataframe(state_level_summary (2018), striped=False, bordered=True, hover=True, index=True , size = 'lg'  ), ]  ) ,        ]),

            #dbc.Row([  dbc.Col([ html.H3("Every tree in the Random Forest:"), ]), ])
        #    dbc.Row([  dbc.Col([ dbc.Table.from_dataframe(   yoy_homeless, striped=False, bordered=True, hover=True, index=True , size = 'lg'), ]  ) ,    ]),
        ])


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([dbc.Tabs(
    [
        dbc.Tab(yoy_analysis, label="YOY Analysis"),
        dbc.Tab(state_level_analysis, label="State Level Analysis")
        ]
    )])

@app.callback(
 [#Output(component_id = 'yoy_summary' , component_property = 'children'),
 #Output(component_id = 'fig_1_state' , component_property = 'figure'),
Output(component_id = 'kassra' , component_property = 'children')],
 [Input(component_id = 'selected_year', component_property = 'value' )]
)
def update_graphs(year):
    kassra = 'hi {}  '.format(year)
    #return state_level_summary(selected_year=year) , top_10_highest_homeless_rate(selected_year = year) ,
    return kassra
    



if __name__ == "__main__":
    app.run_server()



