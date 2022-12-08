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
    yoy_homeless['Overall Homeless during {x}'.format(x=selected_year)] = yoy_homeless['Overall Homeless during {x}'.format(x=selected_year)].apply(lambda x:  f'{x:,}' )
    return yoy_homeless
    


def homeless_count_map(selected_year = 2018 , count_type = 'Overall Homeless'):
    fig_2_state = go.Figure(data=go.Choropleth(
        locations=pivoted_data[pivoted_data['year'] == selected_year]['state'], 
        z = pivoted_data[pivoted_data['year'] == selected_year][count_type], 
        locationmode = 'USA-states',
        #    colorscale = 'Reds'
 

    text=pivoted_data[pivoted_data['year'] == selected_year][count_type], 
    marker_line_color='white' , customdata =['Overall Homelessness' , 'Homelessness Rate ']
    ))

    fig_2_state.update_layout(
        title_text = 'State-wise distribution of the Homelessness',
        geo_scope='usa'  , width = 800 , height  = 450
    )


    return fig_2_state




def top_10_highest_homeless_count(selected_year = 2018 ,  count_type = 'Overall Homeless' ):
    fig_3_state = px.bar(pivoted_data[pivoted_data['year'] == selected_year].sort_values(by = count_type , ascending = True )[0:10], x=count_type, y="state" , orientation = 'h'
                 , title  = 'Top 10 States with Highest Overall Homelessness'  ) #,  custom_data =[count_type],)


    fig_3_state.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor':'rgba(0, 0, 0, 0)',
    } , width = 450 , height  = 450
     ,colorway =['green'])


    fig_3_state.update_traces(marker_color='orange',
     #   hovertemplate="<br>".join([
     #       "State: %{x}",
     #       "{t}: %{customdata[0]}".format(t=count_type)
     #   ])
    )
    return fig_3_state



########################### TAB 1 ##################################

def Chronically_Homeless_Prop_Pie(selected_year = 2018):
    data_pie_1 = data[data['homeless_type'].isin(['Chronically Homeless' , 'Overall Homeless'])].groupby(['year' , 'homeless_type']).sum('count').reset_index( )
    for year in range(2011,2019) :
            Other_type_count = data_pie_1[(data_pie_1['year'] == year) & (data_pie_1['homeless_type'] == 'Overall Homeless') ].reset_index(drop = True)['count'][0]  - data_pie_1[(data_pie_1['year'] == year) & (data_pie_1['homeless_type'] == 'Chronically Homeless') ].reset_index(drop = True)['count'][0] 

            df = pd.DataFrame({'year': [year] , 'homeless_type': ['Other Homeless Types'] ,   'count': [Other_type_count]  })
            data_pie_1 = data_pie_1.append(df)
    Chronically_Homeless_Prop_fig = px.pie(data_pie_1[(data_pie_1['homeless_type']!= 'Overall Homeless') & (data_pie_1['year']==selected_year)], values='count', names='homeless_type', title='Proportion of Chronically Homeless' )
    
    
    Chronically_Homeless_Prop_fig.update_layout({ 'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor':'rgba(0, 0, 0, 0)', } 
                                  , width = 600 , height  = 600 )
 
    
    return Chronically_Homeless_Prop_fig




def  Overall_Homeless_subpop_bar (selected_year = 2018):
    data_bar_1 = data[data['homeless_type'].isin(['Homeless Individuals' , 'Homeless People in Families' ])].groupby(['year' , 'homeless_type']).sum('count').reset_index( )
    Chronically_Homeless_Prop_fig = px.bar(data_bar_1[ data_bar_1['year']==selected_year], x='homeless_type', y = 'count'  ,  color = 'homeless_type'  ,  title='Homeless Household Composition' )
    
    Chronically_Homeless_Prop_fig.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor':'rgba(0, 0, 0, 0)',
    } , width = 450 , height  = 650, xaxis_title='Homeless Type' , 
    xaxis={'visible': True, 'showticklabels': False} , showlegend=False)
 
    return Chronically_Homeless_Prop_fig    

    

def Homeless_by_shelter(selected_year = 2018):
    data_pie_2 = data[data['homeless_type'].isin(['Sheltered Total Homeless' , 'Unsheltered Homeless'])].groupby(['year' , 'homeless_type']).sum('count').reset_index( )
    fig_homeless_by_shelter = px.pie(data_pie_2[ data_pie_2['year']==selected_year], values='count', names='homeless_type', title='Shelter Status'  , hole = 0.4)
    fig_homeless_by_shelter.update_layout({ 'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor':'rgba(0, 0, 0, 0)', } 
                                  , width = 450 , height  = 450 )
    return fig_homeless_by_shelter


def sheltered_by_shelter_type (selected_year = 2018):

    data_pie_2 = data[data['homeless_type'].isin(['Sheltered ES Homeless' , 'Sheltered TH Homeless' , 'Sheltered SH Homeless'])].groupby(['year' , 'homeless_type']).sum('count').reset_index( )


    fig_sheltered_by_shelter_type = px.pie(data_pie_2[ data_pie_2['year']==selected_year], values='count', names='homeless_type', title='Shelter Types'  , hole = 0.4)
    fig_sheltered_by_shelter_type.update_layout({ 'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor':'rgba(0, 0, 0, 0)', } 
                                  , width = 450 , height  = 450 )
    return fig_sheltered_by_shelter_type






def Homeless_Type_by_Shelter(selected_year = 2018):

    data_bar_3 = data[(data['homeless_type'].isin(['Sheltered SH Homeless Individuals' , 'Sheltered SH Homeless People in Families' ,'Sheltered ES Homeless Individuals'
     , 'Sheltered ES Homeless People in Families' , 'Sheltered TH Homeless Individuals' , 'Sheltered TH Homeless People in Families'
    ])) &  (data['year'] == selected_year) ].reset_index(drop = True)

    data_bar_3['Shelter Type']  = data_bar_3['homeless_type'].apply( lambda x :x.split()[1]    )
    data_bar_3['Homeless Category'] =   data_bar_3['homeless_type'].apply( lambda x :x.split()[len(x.split())-2]  + ' ' + x.split()[len(x.split())-1])

    data_bar_3['Homeless Category']  = data_bar_3['Homeless Category'].apply(lambda x :'Homeless Individuals' if x == 'Homeless Individuals' else 'Homeless people in familes'  )                                                    

    data_bar_3 = data_bar_3.groupby(['year' , 'homeless_type' , 'Shelter Type' , 'Homeless Category']).sum('count').reset_index()

    fig_Homeless_Type_by_Shelter = px.bar(data_bar_3.sort_values(by = 'count', ascending = False ) , x="Shelter Type", color="Homeless Category",
                 y='count',
                 title="Homeless Household Composition by Shelter Type",
                 barmode='group',
                 height=700,

                )
    
    fig_Homeless_Type_by_Shelter.update_layout({
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
    'paper_bgcolor':'rgba(0, 0, 0, 0)',
    } , width = 800 , height  = 650)

    return fig_Homeless_Type_by_Shelter


def Youth_Homeless_Prop_Pie(selected_year = 2018):
    data_pie_1 = data[data['homeless_type'].isin(['Homeless Unaccompanied Youth (Under 25)'    ,  'Homeless Parenting Youth (Under 25)'   , 'Overall Homeless'])].groupby(['year' , 'homeless_type']).sum('count').reset_index( )
    for year in range(2015,2019) :
            Other_type_count = data_pie_1[(data_pie_1['year'] == year) & (data_pie_1['homeless_type'] == 'Overall Homeless') ].reset_index(drop = True)['count'][0]  - (data_pie_1[(data_pie_1['year'] == year) & (data_pie_1['homeless_type'] == 'Homeless Unaccompanied Youth (Under 25)') ].reset_index(drop = True)['count'][0]+ data_pie_1[(data_pie_1['year'] == year) & (data_pie_1['homeless_type'] == 'Homeless Parenting Youth (Under 25)') ].reset_index(drop = True)['count'][0]     ) 

            df = pd.DataFrame({'year': [year] , 'homeless_type': ['Others'] ,   'count': [Other_type_count]  })
            data_pie_1 = data_pie_1.append(df)
    
    
    
    
    
    Youth_Homeless_Prop_fig = px.pie(data_pie_1[(data_pie_1['homeless_type']!= 'Overall Homeless') & (data_pie_1['year']==selected_year)], values='count', names='homeless_type', title='Proportion of Chronically Homeless' )
    
    
    Youth_Homeless_Prop_fig.update_layout({ 'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor':'rgba(0, 0, 0, 0)', } 
                                  , width = 600 , height  = 600 )
 
    
    return Youth_Homeless_Prop_fig




def homeless_youth(selected_year = 2018):
    data_pie_5 = data[data['homeless_type'].isin(['Sheltered Total Homeless Parenting Youth (Under 25)' , 'Sheltered Total Homeless Unaccompanied Youth (Under 25)'
     , 'Unsheltered Homeless Parenting Youth (Under 25)' , 'Unsheltered Homeless Unaccompanied Youth (Under 25)'])].groupby(['year' , 'homeless_type']).sum('count').reset_index( )


    Unsheltered_youth = data_pie_5[(data_pie_5['year'] == selected_year) & (data_pie_5['homeless_type'] == 'Unsheltered Homeless Parenting Youth (Under 25)') ].reset_index(drop = True)['count'][0] + (data_pie_5[(data_pie_5['year'] == selected_year) & (data_pie_5['homeless_type'] == 'Unsheltered Homeless Unaccompanied Youth (Under 25)') ].reset_index(drop = True)['count'][0]     ) 
    Sheltered_youth = data_pie_5[(data_pie_5['year'] == selected_year) & (data_pie_5['homeless_type'] == 'Sheltered Total Homeless Parenting Youth (Under 25)') ].reset_index(drop = True)['count'][0] + (data_pie_5[(data_pie_5['year'] == selected_year) & (data_pie_5['homeless_type'] == 'Sheltered Total Homeless Unaccompanied Youth (Under 25)') ].reset_index(drop = True)['count'][0]     ) 

    df_1 = pd.DataFrame({'year': [selected_year] , 'homeless_type': ['Sheltered Youth'] ,   'count': [Sheltered_youth]  })
    df_2 = pd.DataFrame({'year': [selected_year] , 'homeless_type': ['Unsheltered Youth'] ,   'count': [Unsheltered_youth]  })

    data_pie_5 = data_pie_5.append(df_1).append(df_2)


    data_pie_5 = data_pie_5[data_pie_5['homeless_type'].isin(['Sheltered Youth' , 'Unsheltered Youth'])]
    fig_homeless_youth = px.pie(data_pie_5[ data_pie_5['year']==selected_year], values='count', names='homeless_type', title='Youths Shelter Status'  , hole = 0.4)
    fig_homeless_youth.update_layout({ 'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor':'rgba(0, 0, 0, 0)', } 
                                      , width = 450 , height  = 450 )


    return fig_homeless_youth 




def homeless_youth_by_age(selected_year = 2018):
    data_pie_6= data[data['homeless_type'].isin(['Homeless Parenting Youth Under 18' , 'Homeless Parenting Youth Age 18-24' ,
    'Homeless Unaccompanied Youth Age 18-24' , 'Homeless Unaccompanied Youth Under 18'])].groupby(['year' , 'homeless_type']).sum('count').reset_index( )


    youth_18_24 = data_pie_6[(data_pie_6['year'] == selected_year) & (data_pie_6['homeless_type'] == 'Homeless Unaccompanied Youth Age 18-24') ].reset_index(drop = True)['count'][0] + (data_pie_6[(data_pie_6['year'] == selected_year) & (data_pie_6['homeless_type'] == 'Homeless Parenting Youth Age 18-24') ].reset_index(drop = True)['count'][0]     ) 
    youth_under_18 = data_pie_6[(data_pie_6['year'] == selected_year) & (data_pie_6['homeless_type'] == 'Homeless Unaccompanied Youth Under 18') ].reset_index(drop = True)['count'][0] + (data_pie_6[(data_pie_6['year'] == selected_year) & (data_pie_6['homeless_type'] == 'Homeless Parenting Youth Under 18') ].reset_index(drop = True)['count'][0]     ) 

    df_1 = pd.DataFrame({'year': [selected_year] , 'homeless_type': ['Between 18-24'] ,   'count': [youth_18_24]  })
    df_2 = pd.DataFrame({'year': [selected_year] , 'homeless_type': ['Under 18'] ,   'count': [youth_under_18]  })


    data_pie_6 = data_pie_6.append(df_1).append(df_2)
    data_pie_6 = data_pie_6[data_pie_6['homeless_type'].isin(['Between 18-24'  ,  'Under 18'  ])]

    fig_homeless_youth_by_age = px.pie(data_pie_6, values='count', names='homeless_type', title='Homeless Youth by Age'  , hole = 0.4)
    fig_homeless_youth_by_age.update_layout({ 'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor':'rgba(0, 0, 0, 0)', } 
                                          , width = 450 , height  = 450 )

    return fig_homeless_youth_by_age



drop_down_state_container = dcc.Dropdown(id = "selected_year_state_tab" 
             , options = [
                 {'label':'2015' , 'value':2015},
                 {'label':'2016' , 'value':2016},
                 {'label':'2017' , 'value':2017},
                 {'label':'2018' , 'value':2018},
                         ]
             , multi = False
             , value = 2018 
             , style = {'width' : '100%' }
            ),


drop_down_state_container_variable = dcc.Dropdown(id = "variable" 
             , options = [
                 {'label':'Overall Homeless' , 'value':'Overall Homeless'},
                 {'label':'Homelessness Rate' , 'value':'Homelessness Rate'},

                         ]
             , multi = False
             , value = 'Overall Homeless' 
             , style = {'width' : '100%' }
            ),




################ Subpopulations Tab ##########################
Homeless_Subpopulation = dbc.Container([
            
            dbc.Row([  html.H2('Overall Homelessness during 2018')  ]),
            
            dbc.Row([ dbc.Col() , dbc.Col([ dcc.Graph(figure = Chronically_Homeless_Prop_Pie(2018) ,  style={'display': 'inline-block'}) ,  ]  ) , dbc.Col()  ]),
            
            dbc.Row([   dbc.Col([ dcc.Graph(figure = Homeless_by_shelter(2018),  style={'display': 'inline-block'}) ,  ]),
                         dbc.Col([ dcc.Graph(figure = sheltered_by_shelter_type(2018) ,  style={'display': 'inline-block'}) ,  ])
                    ]),
    
            dbc.Row([   dbc.Col([ dcc.Graph(figure = Overall_Homeless_subpop_bar (selected_year = 2018)  ,  style={'display': 'inline-block'}) ,  ]),
                         dbc.Col([ dcc.Graph(figure = Homeless_Type_by_Shelter(2018) ,  style={'display': 'inline-block'}) ,  ])  ]),

            dbc.Row([  html.H2('Youth Homelessness during 2018')  ]),
            
            dbc.Row([ dbc.Col() , dbc.Col([ dcc.Graph(figure = Youth_Homeless_Prop_Pie(2018) ,  style={'display': 'inline-block'}) ,  ]  ) , dbc.Col()  ]),

    
            dbc.Row([   dbc.Col([ dcc.Graph(figure = homeless_youth(selected_year = 2018)  ,  style={'display': 'inline-block'}) ,  ]),
                         dbc.Col([ dcc.Graph(figure = homeless_youth_by_age(2018) ,  style={'display': 'inline-block'}) ,  ])  ]),
    
        ]  , fluid = True, style={"height": "100vh"} )

    


################ YOY Analysis Tab ##########################


yoy_analysis = dbc.Container(dcc.Graph(figure={"data": [{"x": [1, 2, 3], "y": [1, 4, 9]}]}))


################ State level tab ##########################
state_level_analysis = dbc.Container([
            
            dbc.Row([   html.Br() ]), 
            dbc.Row([    dbc.Col(), dbc.Col() , dbc.Col( drop_down_state_container ) ]),
            dbc.Row([ html.H2('Homelessness by US Regions' ) ]),
            dbc.Row([   dbc.Col([html.Div(id = 'yoy_summary'  )])   ]),
            dbc.Row([ html.H2('Homelessness by US States' ) ]),
            dbc.Row([    dbc.Col(), dbc.Col() , dbc.Col( drop_down_state_container_variable ) ]),
            dbc.Row([   html.Br() ]),
            dbc.Row([  dbc.Col([ dcc.Graph(id="fig_3_state" ,  style={'display': 'inline-block'}) ,  ]) ,  dbc.Col([ dcc.Graph(id="fig_2_state",  style={'display': 'inline-block'}) ,  ]) ,         ]),


        ])

dbc.Col([ html.Div(id = 'yoy_summary' ) , ]) ,
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([dbc.Tabs(
    [
        dbc.Tab(Homeless_Subpopulation, label="Homeless Subpopulation"),
        dbc.Tab(yoy_analysis, label="YOY Analysis"),
        dbc.Tab(state_level_analysis, label="State Level Analysis")
        ]
    )])


@app.callback(
   [
     Output(component_id = 'fig_2_state' , component_property = 'figure'),
     Output(component_id = 'fig_3_state' , component_property = 'figure'),
     Output(component_id = 'yoy_summary' , component_property = 'children')
    ],

 [Input(component_id = 'selected_year_state_tab', component_property = 'value' ),
  Input(component_id = 'variable', component_property = 'value' )
 ],
)

def update_graphs_state(year , variable):
    year = int(year)
      
    yoy_homeless = state_level_summary (selected_year=year)

    return  homeless_count_map(selected_year = year , count_type = variable ),top_10_highest_homeless_count(selected_year = year , count_type = variable ) ,  dbc.Table.from_dataframe(  yoy_homeless, striped=False, bordered=True, hover=True, index=True , size = 'sm') 
    
    
  
if __name__ == "__main__":
    app.run_server()
