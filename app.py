import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import flask
import pickle
import pandas as pd

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)

df = pd.read_csv('com_20_all_all.csv')
df2 = pd.read_csv('com_20_all_all_para.csv')
with open('bac_20_top5taxa.pkl', 'rb') as f:
    taxa = pickle.load(f)


model_explanation='''
## Identifying Bacterial Communities
This project is a proof of concept using machine learning to identify bacterial communities for market segmentation in the probiotic space.

### Bacteria are everywhere, and we are only just learning how to harness them
There are more bacterial cells in a human body than human cells. Bacteria shape the world around them. They act like contract workers for larger organisms, performing chemistry that animals and plants are unable to do for themselves. Sometimes they are needed break down molecules, other times to defend against other bacteria that is harmful. Until recently, most bacterial species were a mystery to biologists. Only bacteria that could be grown in a lab could be studied, or even identified, and this is only possible for a very small subset of all bacterial species. With recent advances in DNA sequencing technology, we can now record DNA from all the bacteria present in a given sample. Even with this powerful tool, sometimes all we know about a sample is that it contains DNA not present in other bacteria previously observed.

### What are probiotics?
Probiotics apply the notion that some bacteria are beneficial for human, animal or plant health and package those benefits as a commercial product.

### Bacterial subpopulations can be targeted with probiotics
Current probiotics products use a one-size-fits-all approach. But there is increasing information about how bacteria interact with each other, giving us the opportunity to target different probiotics to people and places with different bacterial populations. This is especially true for plant probiotics, where the beneficial bacteria need to be optimized not only for the plants themselves, but also for the bacteria that live in the surrounding soil. Practical market segmentation is particularly important in this field because the number of possible bacteria species stretches into the millions. Market segments would ideally be communities of positively interacting bacteria. We can assume that if bacteria have positive interactions they are more likely to occur together.

### We have data on the presence of bateria at locations across the US
Data for this analysis is from dust samples collected from across the US as part of the "Wild life of our homes" citizen science project and published [here](/pnas.org/content/112/18/5756.full). Participants from over 1000 locations collected dust samples, and over 130,000 bacterial species (OTUs) were identified. As with most data of this type, the data is only 3% dense, meaning that most species are not observed at most locations. This is important for determining the appropriate clustering mechanism.

### Latent Dirichlet allocation can identify bacterial subpopulations
For this project, I chose to use latent Dirichlet allocation (LDA) to define bacterial communities. We assume that when each location is sampled (e.g., a doorway is swabbed) we are picking up bacteria from multiple coexisting bacterial communities. Additionally, multiple bacterial communities might contain the same species. The LDA model fits with these assumptions. In brief, LDA is a generative probabilistic model in which each sampled location is a random mixture over the latent communities defined by the model and each community is defined by a distribution over bacterial species.

### We can identify 20 bacterial communities across the US
The classic way to validate an LDA model is by evaluating the perplexity of the model. The perplexity is a measure of the likelihood of producing the observations in a test dataset assuming that the distributions defined by the model are true. Specifically, it can be calculated as the inverse geometric mean of the per-species likelihood. The smaller the perplexity, the more accurately the model predicts the observed data. I used the perplexity score to define the minimal number of communities required to describe the bacterial diversity in my dataset; the minimum is approximately 20 communities. (See slide show for graph).

### The bacterial communities are easily visualized
#### Taxa
In addition to calculating the perplexity on a held-out test dataset, I examined the bacterial species present in each community. I found that some communities were defined completely by unknown bacterial species, while in other communities, the top weighted bacteria were all in the same phylum, class, or order. Explore more in the Taxa tab.

#### Locations
Using a separate dataset containing latitude and longitude data for each location, I visualized the distribution of each community across the US. Explore in the Locations tab.

#### Climate data
I also determined the mutual information as well as a weighted mean and standard deviation metric for the elevation, mean annual precipitation and mean annual temperature associated with each location. Interestingly, none of the communities are strongly defined by these location parameters alone. Explore further in the Climate tab.
'''

def plot_parameter(characteristic, ptitle):
    return {
        'data': [
            go.Scatter(
                x=list(range(1,21)),
                y=df2[characteristic+'mean'],
                error_y={
                    'type': 'data',
                    'array': df2[characteristic+'std'],
                    'visible': True
                },
                mode='markers',
                opacity=0.7,
                marker={
                    'size': 15,
                    'line': {'width': 0.5, 'color': 'white'}
                },
                name='Name'
            )
    ],
    'layout': go.Layout(
        xaxis={'title': 'Community'},
        yaxis={'title': ptitle},
        margin={'l': 50, 'b': 50, 't': 50, 'r': 50},
        # legend={'x': 0, 'y': 1},
        hovermode='closest'
        )
    }

app.config.supress_callback_exceptions = True

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        html.Div([
            html.Div([
                dcc.Link('Bacterial States of America', href='/', className='navbar-brand'),
            ], className='navbar-header'),
            html.Ul([
                html.Li([dcc.Link('Project Explanation', href='/model')]),
                html.Li([dcc.Link('Location Explorer', href='/')]),
                html.Li([dcc.Link('Community Properties', href='/about')]),
                html.Li([dcc.Link('Taxa Explorer', href='/taxa')]),
                html.Li([html.A('Slides', href='https://docs.google.com/presentation/d/e/2PACX-1vTzvJQWZRATdPWl7HDEMyJuMKlDC0N7FMkiUxn31qLSaTGd3Vope0FdFP94cJns13K95nlNNXJPxwJn/pub?start=false&loop=false&delayms=3000')])
            ], className='nav navbar-nav')
        ], className='container-fluid')
    ], className='navbar navbar-dark navbar-inverse navbar-fixed-top'),
    html.Div(id='page-content', style={'padding-top': '80px'})
])

index_layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.H3('Choose a bacterial community to examine:'),
                dcc.Slider(
                    id='community-slider',
                    min=0,
                    max=19,
                    value=0,
                    step=None,
                    marks={str(i): str(i+1) for i in range(20)}
                )],
                style={'margin': '0 50px 50px 50px'}
            ),
            html.P('Hover over map to see details on the communities present at each location'),
            dcc.Graph(id='map', animate=True)
            ],className='col-md-7'
        ),
        html.Div([
            dcc.Graph(id='location-values', style={'margin': '0 0 0 0'}),
            dcc.Graph(id='communities-dist')
            ], className='col-md-5'
        )
    ], className='row'),
], className='container-fluid')

about_layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.H3('Choose a bacterial community to examine:'),
                    dcc.Slider(
                        id='community-slider',
                        min=0,
                        max=19,
                        value=0,
                        step=None,
                        marks={str(i): str(i+1) for i in range(20)}
                    )
                ], style={'margin': '0 50px 50px 50px'}),
                dcc.Graph(id='map', animate=True)
            ], className='col-md-7', style={'position': 'fixed'})
        ]),
        html.Div([
            html.H2('Geoclimate factors associated with each community'),
            dcc.Graph(
                id='longitude-plot',
                figure=plot_parameter('Longitude', 'Mean community longitude')
                ),
            dcc.Graph(
                id='latitude-plot',
                figure=plot_parameter('Latitude', 'Mean community latitude')
                ),
            dcc.Graph(
                id='elevation-plot',
                figure=plot_parameter('Elevation', 'Mean community elevation (m)')
                ),
            dcc.Graph(
                id='precipitation-plot',
                figure=plot_parameter('MeanAnnualPrecipitation', 'Mean community precipitation (cm)')
                ),
            dcc.Graph(
                id='temperature-plot',
                figure=plot_parameter('MeanAnnual Temperature', 'Mean community temperature (C)')
                )
        ], className='col-md-5', style={'float': 'right'}),
    ], className='row')
], className='container-fluid')

taxa_layout = html.Div([
    html.Div([
        html.Div([
            html.H3('Choose a bacterial community to examine:'),
            dcc.Slider(
                id='community-slider',
                min=0,
                max=19,
                value=0,
                step=None,
                marks={str(i): str(i+1) for i in range(20)}
            )],
            style={'margin': '0 50px 50px 50px'}
        )
    ], className='row'),
    html.Div([
        html.Div([
            dcc.Graph(id='map', animate=True)
            ],className='col-md-7'
        ),
        html.Div(children=[
            html.Div(id='top-species-table')
            ], className='col-md-5')
    ], className='row'),
], className='container-fluid')

model_layout = html.Div([
    html.Div([
        html.Div([
            dcc.Markdown(children=model_explanation)
        ], className='col-md-8')
    ], className='row', style={'margin': '0 50px 50px 50px'})
], className='container-fluid')


@app.callback(
    dash.dependencies.Output('top-species-table', 'children'),
    [dash.dependencies.Input('community-slider', 'value')])
def generate_table(community):
    return html.Table([
        html.Thead([html.Tr([
            html.Th('Taxa of top weighted species'),
            html.Th('Species weight')
            ])]),
        html.Tbody([
            html.Tr([
                html.Td(taxa[community].index[i]),
                html.Td(taxa[community].values[i].round(2))
            ])
            for i in range(len(taxa[community]))
        ])
        ], className = 'table')

@app.callback(
    dash.dependencies.Output('location-values', 'figure'),
    [dash.dependencies.Input('map', 'hoverData')])
def location_values(hoverData):
    s = df[df['ID'] == hoverData['points'][0]['customdata']]
    scales = ['<b>Precipitation</b>', '<b>Temperature</b>', '<b>Elevation</b>']
    max_P = df['MeanAnnualPrecipitation'].max().round(-1) + 10
    max_T = df['MeanAnnual Temperature'].max().round(-1) + 10
    max_E = df['Elevation'].max().round(-2) + 100
    max_values = [max_P, max_T, max_E]

    # Add Scale Titles to the Plot
    traces = []
    for i in range(len(scales)):
        traces.append(go.Scatter(
            x=[-.25], # Pad the title - a longer scale title would need a higher value
            y=[0],
            text=scales[i],
            mode='text',
            hoverinfo='none',
            showlegend=False,
            xaxis='x'+str(i+1),
            yaxis='y'+str(i+1)
        ))
    # Create Scales
    ## Since we have 7 lables, the scale will range from 0-6
    shapes = []
    for i in range(len(scales)):
        shapes.append({'type': 'line',
                       'x0': 0, 'x1': 1,
                       'y0': 0, 'y1': 0,
                       'xref':'x'+str(i+1), 'yref':'y'+str(i+1)})

    y_domains = [[0, .33], [.33, .67], [.67, 1]] # Split for 3 scales

    # Define Y-Axes
    yaxes = []
    for i in range(len(scales)):
        yaxes.append({'domain': y_domains[i], 'range':[-.5,1],
                      'showgrid': False, 'showline': False,
                      'zeroline': False, 'showticklabels': False})

    # Define X-Axes (and set scale labels)
    xaxes = []
    for i in range(len(scales)):
        xaxes.append({'anchor':'y'+str(i+1), 'range':[-0.5,1.1],
                      'showgrid': False, 'showline': False, 'zeroline': False,
                      'ticks': 'inside', 'ticklen': 6,
                      'ticktext':[0, int(max_values[i])], 'tickvals':[0, 1]
                     })

    loc_values = [s.iloc[0]['MeanAnnualPrecipitation'],
                  s.iloc[0]['MeanAnnual Temperature'],
                  s.iloc[0]['Elevation']]
    for i in range(len(loc_values)):
        traces.append(go.Scatter(
                x=[loc_values[i]/max_values[i]], y=[0],
                xaxis='x'+str(i+1), yaxis='y'+str(i+1),
                mode='marker', marker={'size': 12, 'color': '#29ABD6'},
                text=loc_values[i], hoverinfo='text', showlegend=False
        ))

    # Put all elements of the layout together
    layout = {'shapes': shapes,
              'title': 'Climate data in {}, {}'.format(
                s.iloc[0]['City'].title().strip(),
                s.iloc[0]['State']),
              'xaxis1': xaxes[0],
              'xaxis2': xaxes[1],
              'xaxis3': xaxes[2],
              'yaxis1': yaxes[0],
              'yaxis2': yaxes[1],
              'yaxis3': yaxes[2],
              'autosize': True,
              'margin': go.Margin(l=50, r=50, b=50, t=30),
              'height': 200
    }
    return {'data': traces, 'layout': layout}

@app.callback(
    dash.dependencies.Output('map', 'figure'),
    [dash.dependencies.Input('community-slider', 'value')])
def update_map(community):
    return {
        'data': [{
            'lat': df['Latitude'],
            'lon': df['Longitude'],
            'marker': {
                'color': 'white',
                'size': 40 * df['Community {}'.format(community)],
                'opacity': 0.6
            },
            'customdata': df['ID'],
            'type': 'scattermapbox'
        }],
        'layout': {
            'mapbox': {
                'accesstoken': 'pk.eyJ1IjoibmhlZXIxMiIsImEiOiJjajdueWN0M2Mxb3F3MnFvNmJ0bHoyb3NuIn0.9hzvd8-dM_WSARnKjjOZ8A',
                'center': {'lat': 39.83, 'lon': -95.58},
                'zoom': 3,
                'style': 'mapbox://styles/nheer12/cj7nzag5y71bh2rl08ksp1jbk'
            },
            'hovermode': 'closest',
            'margin': {'l': 0, 'r': 0, 'b': 0, 't': 0}
        }
    }
@app.callback(
    dash.dependencies.Output('communities-dist', 'figure'),
    [dash.dependencies.Input('map', 'hoverData')])
def update_plot(hoverData):
    s = df[df['ID'] == hoverData['points'][0]['customdata']]
    return {
        'data': [go.Bar(
            x=['Com. {}'.format(com+1) for com in range(20)],
            y=[s.iloc[0]['Community {}'.format(com)] for com in range(20)]
        )],
        'layout': go.Layout(
            title='The distribution of communities in {}, {}'.format(
                        s.iloc[0]['City'].title().strip(),
                        s.iloc[0]['State']
                    ),
            yaxis={
                'title': 'Weight of each community',
                'type': 'log',
                'range': [-2, 0],
                'color': '#7f7f7f'
            },
            xaxis={
                'title': 'Bacterial Community'
            },
            plot_bgcolor={
                'color': '##7f7f7f'
            },
            height=400,
            margin=go.Margin(l=70, r=50, b=100, t=50),
        )
    }


@app.callback(
    dash.dependencies.Output('page-content', 'children'),
    [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/model':
        return model_layout
    if pathname == '/about':
        return about_layout
    if pathname == '/taxa':
        return taxa_layout
    else:
        return index_layout

app.css.append_css({
    'external_url': 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css'
})
app.scripts.append_script({
    'external_url': 'https://code.jquery.com/jquery-3.2.1.slim.min.js'
})
app.scripts.append_script({
    'external_url': 'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.11.0/umd/popper.min.js'
})
app.scripts.append_script({
    'external_url': 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js'
})

if __name__ == '__main__':
    app.run_server(debug=True)
