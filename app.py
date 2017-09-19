import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

app = dash.Dash()

df = pd.read_csv('20_Communities_train_data.csv')

app.config.supress_callback_exceptions = True

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        html.Div([
            html.Div([
                dcc.Link('Bacterial Communities', href='/', className='navbar-brand'),
            ], className='navbar-header'),
            html.Ul([
                html.Li([dcc.Link('Communities', href='/')]),
                html.Li([dcc.Link('Modeling', href='/about')])
            ], className='nav navbar-nav')
        ], className='container-fluid')
    ], className='navbar navbar-dark navbar-inverse navbar-fixed-top'),
    html.Div(id='page-content')
])

index_layout = html.Div([
    html.Div([
        html.Div([
            html.Div(
                dcc.Slider(
                    id='community-slider',
                    min=0,
                    max=19,
                    value=0,
                    step=None,
                    marks={str(i): str(i) for i in range(20)}
                ),
                style={'margin': '50px'}
            ),
        ], className='col-md-12')
    ], className='row'),
    html.Div([
        html.Div(
            dcc.Graph(id='map', animate=True),
            className='col-md-7'
        ),
        html.Div(
            dcc.Graph(id='communities-dist'),
            className='col-md-5'
        )
    ], className='row'),
    html.Div(id='text-content')
], className='container-fluid')

about_layout = html.Div([
    html.P('this text is a test')
], className='container-fluid')

@app.callback(
    dash.dependencies.Output('text-content', 'children'),
    [dash.dependencies.Input('map', 'hoverData')])
def update_text(hoverData):
    s = df[df['ID'] == hoverData['points'][0]['customdata']]
    return html.P(
        'The mean precipitation in {}, {} is {} cm'.format(
            s.iloc[0]['City'],
            s.iloc[0]['State'],
            s.iloc[0]['MeanAnnualPrecipitation']
        )
    )

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
                'center': {'lat': 39.83, 'lon': -98.58},
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
            x=['Com. {}'.format(com) for com in range(20)],
            y=[s.iloc[0]['Community {}'.format(com)] for com in range(20)]
        )],
        'layout': go.Layout(
            yaxis={
                'type': 'log',
                'range': [-2, 0]
            }
        )
    }

@app.callback(
    dash.dependencies.Output('page-content', 'children'),
    [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/about':
        return about_layout
    else:
        return index_layout

app.css.append_css({
    'external_url': 'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/css/bootstrap.min.css'
})
app.scripts.append_script({
    'external_url': 'https://code.jquery.com/jquery-3.2.1.slim.min.js'
})
app.scripts.append_script({
    'external_url': 'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.11.0/umd/popper.min.js'
})
app.scripts.append_script({
    'external_url': 'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-beta/js/bootstrap.min.js'
})

if __name__ == '__main__':
    app.run_server(debug=True)
