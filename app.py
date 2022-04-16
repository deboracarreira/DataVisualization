# Importing dependencies.
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output

# access token for the map
token= "pk.eyJ1IjoiZmF5ZXotaCIsImEiOiJja3kxc3N1azkwZXJnMnBsZzhkY3owY3NvIn0.bZf3aU9wAEx1mx4Vzbd0Xg"

# blank figure function to be a placeholder until the callbacks load
def blank_fig():
    fig = go.Figure(go.Scatter(x=[], y = []))
    fig.update_layout(template = None,
                     plot_bgcolor="rgba( 0, 0, 0, 0)",
                     paper_bgcolor="rgba( 0, 0, 0, 0)",)
    fig.update_xaxes(showgrid = False, showticklabels = False, zeroline=False)
    fig.update_yaxes(showgrid = False, showticklabels = False, zeroline=False)

    return fig


# configuration for the figures
config = {'displaylogo': False,
         'modeBarButtonsToAdd':['drawline',
                                'drawopenpath',
                                'drawclosedpath',
                                'drawcircle',
                                'drawrect',
                                'eraseshape'
                               ]}


# reading the data into a pandas dataframe
df = pd.read_csv('df_preprocessed.csv')


# initializing the dash app instance
app = dash.Dash(__name__, 
# the update title when the callback is loading
update_title=None, 
meta_tags=[{'name': 'viewport','content': 'width=device-width, initial-scale=1.0'}])

server = app.server

# the app title that appears in the browser tab
app.title = 'Denver Crime'


# the layout
app.layout = html.Div([
    html.Div([
        # The header section
        html.Div([
            html.P("Denver Criminality Dashboard", id = "title"),
            html.P("In order to understand the criminality patterns in Denver, go through this interactive dashboard and explore the crimes by year, offenses type and offenses categories", className = "headertext"),
          #  html.P("Our names", className = "headertext")
        ], id = "header"),
            # the charts and filters section
            html.Div([
                # the filters section
                html.Div([
                    html.Div([
                        html.P("Offence Choice", className = "filter-text"),
                        dcc.Dropdown(
                                id = 'dropdown',
                                options = [
                                    {'label': 'Traffic', 'value': 0},
                                    {'label': 'Criminal', 'value': 1},
                                ],
                                value = 1,
                                clearable = False,
                                searchable = False
                                )
                    ], id = "dropdown-container"),
                    html.Div([
                        html.P("Year Slider", className = "filter-text"),
                        dcc.RangeSlider(
                            id = 'year-slider',
                            min = df['REPORTED_YEAR'].min(),
                            max = df['REPORTED_YEAR'].max(),
                            step = 1,
                            marks = {int(x): str(x) for x in df.sort_values('REPORTED_YEAR')['REPORTED_YEAR'].unique()},
                            value = [df['REPORTED_YEAR'].min(), df['REPORTED_YEAR'].max()]
                        )
                    ], id = "slider-container")
                ], id = "filters", className = "graphbox"),
                # the graphs section
                html.Div([
                    dcc.Graph(id = 'figure1', figure = blank_fig(), config = config)
                ], id = "graph1", className = "graphbox"),

                html.Div([
                    dcc.Graph(id = 'figure2', figure = blank_fig(), config = config), 
                ], id = "graph2", className = "graphbox"),

                html.Div([
                    html.Div(
                        dcc.Graph(id = 'figure3', figure = blank_fig(), config = config), 
                        id = 'graph3'),

                    html.Div(
                        dcc.Graph(id = 'figure4', figure = blank_fig(), config = config), 
                    id = 'graph4'),

                ], id = "graph3-4", className = "graphbox"),

                html.Div([
                        dcc.Graph(id = 'figure5', figure = blank_fig(), config = config), 
                ], id = "graph5", className = "graphbox"),
            
        ], id = "graphs"),
        html.Div([
            html.P("Elaborated by: Adriana Gamboa, Andreas Schneeweiss, Débora Carreira and Ferdinand Meinzinger")
        ], id = "footer")
    ], id = "main")
], id = "layout")



# The first figure callback
@app.callback(
    Output('figure1', 'figure'),
    [Input('year-slider', 'value'),
     Input('dropdown', 'value')
    ]
)
def update_fig1(years, choice):
    # filter the data by crime or traffic
    dff = df[df['IS_CRIME'] == choice]
    # filter the data by year
    dff=dff[(dff['REPORTED_YEAR']>=years[0])&(dff['REPORTED_YEAR']<=years[1])]
    # data manipulation necessary for the chart
    dff = dff.groupby('OFFENSE_CATEGORY_ID', as_index = False).count()
    dff = dff.sort_values('incident_id')
    dff = dff.rename(columns = {'incident_id': 'Count'})

    #create the chart
    #try and except are done due to a bug in the current version of dash.
    try:
        fig = px.bar(dff, 
        y = 'OFFENSE_CATEGORY_ID', 
        x = 'Count', 
        orientation = 'h', 
        text_auto = True,
        color_discrete_sequence = ['#ffadab'],
        title = 'Recorded Crime by Offense')
    except ValueError:
        fig = px.bar(dff, 
        y = 'OFFENSE_CATEGORY_ID', 
        x = 'Count', 
        orientation = 'h', 
        text_auto = True,
        color_discrete_sequence = ['#ffadab'],
        title = 'Recorded Crime by Offense')

    # update the layout of the figure
    fig.update_layout(margin = dict(t = 40, b = 0, l = 0, r = 0),
    plot_bgcolor = '#f3f3f3', 
    paper_bgcolor = '#f3f3f3',
    xaxis = dict(title = '', showgrid = False, zeroline = False), 
    yaxis = dict(title = ''),
    title_x=0.5
    )


    return fig


# the second figure callback
@app.callback(
    Output('figure2', 'figure'),
    [Input('year-slider', 'value'),
     Input('dropdown', 'value')
    ]
)
def update_fig2(years, choice):
    #filter the data by crime or traffic
    dff = df[df['IS_CRIME'] == choice]
    #filter the data by year
    dff = dff[(dff['REPORTED_YEAR']>=years[0])&(dff['REPORTED_YEAR']<=years[1])]
    # data manipulation necessary for the chart
    dff = dff.groupby(['GEO_LON', 'GEO_LAT', 'NEIGHBORHOOD_ID', 'DISTRICT_ID'], as_index = False).count()
    dff = dff.rename(columns = {'IS_CRIME': 'Crime Count'})

    try:
        fig = px.density_mapbox(dff, lat='GEO_LAT', lon='GEO_LON', z='Crime Count', radius=10, opacity = 1,
                            center=dict(lat=39.7392, lon=-104.9903), zoom=10,
                            mapbox_style="light", color_continuous_scale='RdBu',
                            hover_data = {'GEO_LAT': False, 'GEO_LON': False, 'NEIGHBORHOOD_ID': True, 'DISTRICT_ID': True})

    except ValueError:
        fig = px.density_mapbox(dff, lat='GEO_LAT', lon='GEO_LON', z='Crime Count', radius=10, opacity = 1,
                            center=dict(lat=39.7392, lon=-104.9903), zoom=10,
                            mapbox_style="light", color_continuous_scale='RdBu',
                            hover_data = {'GEO_LAT': False, 'GEO_LON': False, 'NEIGHBORHOOD_ID': True, 'DISTRICT_ID': True})

    # update the layout of the chart
    fig.update_layout(mapbox_accesstoken = token)

    fig.update_layout(margin = dict(t = 40, b = 0, l = 0, r = 0),
    plot_bgcolor = '#f3f3f3', 
    paper_bgcolor = '#f3f3f3',
    xaxis = dict(
    showgrid = False, zeroline = False
    ), 
    title_x=0.5
    )
    return fig


# The third figure callback
@app.callback(
    Output('figure3', 'figure'),
    [Input('year-slider', 'value'),
     Input('dropdown', 'value')
    ]
)
def update_fig3(years, choice):
    # filter the data by crime or traffic
    dff = df[df['IS_CRIME'] == choice]
    # data manipulation necessary for the chart
    dff = dff.groupby('OFFENSE_CATEGORY_ID', as_index = False).count()
    dff = dff.rename(columns = {'incident_id': 'Count'})
    top5 = list(dff['OFFENSE_CATEGORY_ID'].iloc[:5])
    df2 = df[df['OFFENSE_CATEGORY_ID'].isin(top5) == True]
    df2 = df2.groupby(['OFFENSE_CATEGORY_ID', 'REPORTED_YEAR'], as_index = False).count()
    # filter the data by year
    df2 = df2[(df2['REPORTED_YEAR']>=years[0])&(df2['REPORTED_YEAR']<=years[1])]
    df2 = df2.rename(columns = {'incident_id': 'Count'})

    try:
        fig = px.line(df2, x = 'REPORTED_YEAR', y = 'Count', color = 'OFFENSE_CATEGORY_ID')
    except ValueError:
        fig = px.line(df2, x = 'REPORTED_YEAR', y = 'Count', color = 'OFFENSE_CATEGORY_ID')

    fig.update_layout(margin = dict(t = 40, b = 0, l = 0, r = 0),
    plot_bgcolor = '#f3f3f3', 
    paper_bgcolor = '#f3f3f3',
    xaxis = dict(
    showgrid = False, zeroline = False
    ), 
    title_x=0.5
    )
    return fig


# The forth figure callback
@app.callback(
    Output('figure4', 'figure'),
    [Input('year-slider', 'value'),
     Input('dropdown', 'value')
    ]
)
def update_fig4(years, choice):
    # filter the data by crime or traffic
    dff = df[df['IS_CRIME'] == choice]
    dff = dff.groupby('OFFENSE_CATEGORY_ID', as_index = False).count()
    dff = dff.rename(columns = {'incident_id': 'Count'})
    top5 = list(dff['OFFENSE_CATEGORY_ID'].iloc[:5])
    df2 = df[df['OFFENSE_CATEGORY_ID'].isin(top5) == True]
    # filter the data by year
    df2 = df2[(df2['REPORTED_YEAR']>=years[0])&(df2['REPORTED_YEAR']<=years[1])]

    df2 = df2.groupby(['OFFENSE_CATEGORY_ID', 'REPORTED_MONTH'], as_index = False).count()
    df2 = df2.rename(columns = {'incident_id': 'Count'})
    #create the chart
    try:
        fig = px.line(df2, x = 'REPORTED_MONTH', y = 'Count', color = 'OFFENSE_CATEGORY_ID')
    except ValueError:
        fig = px.line(df2, x = 'REPORTED_MONTH', y = 'Count', color = 'OFFENSE_CATEGORY_ID')
    #update the layout of the chart
    fig.update_layout(margin = dict(t = 40, b = 0, l = 0, r = 0),
    plot_bgcolor = '#f3f3f3', 
    paper_bgcolor = '#f3f3f3',
    xaxis = dict(
    showgrid = False, zeroline = False
    ), 
    title_x=0.5
    )
    return fig



# The fifth figure callback
@app.callback(
    Output('figure5', 'figure'),
    [Input('year-slider', 'value'),
     Input('dropdown', 'value')
    ]
)
def update_fig4(years, choice):
    # filter the data by year
    df1 = df[(df['REPORTED_YEAR']>=years[0])&(df['REPORTED_YEAR']<=years[1])]
    #filter the data by crime or traffic
    df1 = df1[df1['IS_CRIME'] == choice]
    # data manipulation necessary for the chart
    df1 = df1[['NEIGHBORHOOD_ID', 'OFFENSE_CATEGORY_ID', 'incident_id']]
    df1 = df1[df1['NEIGHBORHOOD_ID'].isin(list(df1.groupby('NEIGHBORHOOD_ID', as_index = False).count().sort_values('incident_id', ascending = False).iloc[:5]['NEIGHBORHOOD_ID']))]
    dff = df1.groupby(['NEIGHBORHOOD_ID', 'OFFENSE_CATEGORY_ID'], as_index = False).count()
    df2 = pd.DataFrame()
    for neighborhood in dff['NEIGHBORHOOD_ID'].unique():
        df2 = pd.concat(objs = [df2, dff[dff['NEIGHBORHOOD_ID'] == neighborhood].sort_values('incident_id', ascending = False).iloc[:5]])
    df2 = df2.rename(columns = {'incident_id': 'Count'})
    #create the chart
    try:
        fig = px.treemap(df2, path=[px.Constant("Top 5 neighborhoods"), 'NEIGHBORHOOD_ID', 'OFFENSE_CATEGORY_ID'], values='Count',
                        color='Count', 
                        color_continuous_scale=['white', '#ff8885'],)

    except ValueError:
        fig = px.treemap(df2, path=[px.Constant("Top 5 neighborhoods"), 'NEIGHBORHOOD_ID', 'OFFENSE_CATEGORY_ID'], values='Count',
                        color='Count', 
                        color_continuous_scale=['white', '#ff8885'],)
    #update the layout of the chart
    fig.update_layout(margin = dict(t = 40, b = 0, l = 0, r = 0),
    plot_bgcolor = '#f3f3f3', 
    paper_bgcolor = '#f3f3f3',
    xaxis = dict(
    showgrid = False, zeroline = False
    ), 
    title_x=0.5
    )

    return fig


# run the app
if __name__ == "__main__":
    app.run_server(debug=True)