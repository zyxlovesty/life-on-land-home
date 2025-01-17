import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_leaflet as dl
 
import xml.etree.ElementTree as ET
from shapely.geometry import LineString
import pandas as pd
import base64
import os
 
external_stylesheets = [
    'https://fonts.googleapis.com/css?family=Poppins:300,400,500,600,700,800,900&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
    '/assets/style.css'
]
 
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
 
df = pd.read_csv('data/50_trails.csv', encoding='utf-8')
 
def load_trail_names():
    return [{'label': name, 'value': name} for name in df['name'].unique()]
 
def gpx_to_points(gpx_path):
    tree = ET.parse(gpx_path)
    root = tree.getroot()
    namespaces = {'default': 'http://www.topografix.com/GPX/1/1'}
    route_points = [(float(pt.attrib['lat']), float(pt.attrib['lon'])) for pt in root.findall('.//default:trkpt', namespaces)]
    return LineString(route_points)
 
def create_trail_card(trail_number, trail_name, duration, elevation_gain, distance):
    return dbc.Card(
        dbc.CardBody([
            html.H3(style={'display': 'inline'}, children=[
                html.Span(f"{trail_number}. ", style={'font-weight': 'bold'}),  # Display the trail number
                html.A(trail_name, href=f'/{trail_name.replace(" ", "-")}',
                    style={'color': '#112434', 'text-decoration': 'none', 'margin-bottom': '8px'}),
                html.A(html.I(className="fas fa-external-link-alt",
                              style={'color': '#112434', 'text-decoration': 'none', 'margin-bottom': '8px', 'margin-left':'8px', 'font-size': '13px'}),
                      href=f'/{trail_name.replace(" ", "-")}')
            ]),
            html.Div([
                html.I(className="fas fa-clock", style={'color': '#808080', 'margin-right': '5px'}),
                html.Span(f"Duration: {duration} hours", style={'color': '#808080'}),
                html.I(className="fas fa-mountain", style={'color': '#808080', 'margin-right': '5px', 'margin-left': '10px'}),
                html.Span(f"Elevation Gain: {elevation_gain} m", style={'color': '#808080'}),
                html.I(className="fas fa-route", style={'color': '#808080', 'margin-right': '5px', 'margin-left': '10px'}),
                html.Span(f"Distance: {distance} km", style={'color': '#808080'}),
            ], style={'font-size': '14px', 'margin-bottom': '30px'})
        ])
    )
   
 
def b64_image(img):
    with open(img, 'rb') as f:
        image = f.read()
    return 'data:image/png;base64,' + base64.b64encode(image).decode('utf-8')
 
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Row([
        dbc.Col(
            html.Header([
                html.A('InSync', href='#', className='logo'),
                html.Ul([
                    html.Li(dcc.Link('Home', href='/', className='active')),
                    html.Li(dcc.Link('My Trail', href='/my-trail')),
                    html.Li(dcc.Link('All Trails', href='/all-trails')),
                ], className='navigation')
            ])
        )
    ]),
   
    html.Section(className='sec', children=[
        html.H2('Trails in Victoria'),
        html.H4('Explore the diverse trails of Victoria with our carefully curated selection.'),
        html.P('Our trails span across Victoria and offer a variety of terrains and difficulty levels. We provide average estimates of trail details to help you choose the perfect trail for your adventure.', style={'margin-right':'100px'}),
        html.P("    "),
        html.H4('Happy Hiking!', style={'margin-top': '20px'})
    ]),
    # html.Div(id='trail-cards-row'),
    html.Div([
        dcc.Dropdown(
            id='trail-search-dropdown',
            options=load_trail_names(),
            searchable=True,
            placeholder='Search for trails...',
            style={
                'width':'600px',
                'padding': '12px',
                'margin-top': '10px',
                'margin-right': '16px',
                'font-size': '16px',
                'border-radius': '30px',
                'vertical-align':'center'
            }
        ),
        html.Div(id='trail-cards-row'),  # This is where the trail cards will be displayed
    ], style={'padding-top': '20px', 'margin-left': '20px'}),
    html.Div(id='trail-info'),
    dl.Map(
        id='trail-map',
        children=[dl.TileLayer(), dl.LayerGroup(id='trail-layer'), dl.LayerGroup(id='image-layer')],
        style={'width': '70%', 'height': '500px', 'margin-top': '15px', 'margin-left': '200px', 'align': 'center', 'display': 'none'}  # Initially hide the trail-map
    ),
    html.Div(id='mountain-backgrounds')
 
])
 
@app.callback(
    Output('mountain-backgrounds', 'children'),
    [Input('url', 'pathname')]
)
def update_background_images(pathname):
    if pathname == '/' or pathname == '/all-trails':
        return html.Div([
            html.Img(src=b64_image('assets/monutain_03.png'),
                style={
                'position': 'fixed',
                'bottom': '0',
                'right': '0',
                'width': '60%',
                'height': '60%',
                'background-size': 'cover',
                'background-attachment': 'fixed',
                'z-index': '-1',
            }),
            html.Img(src=b64_image('assets/monutain_02.png'),
                style={
                'position': 'fixed',
                'bottom': '0',
                'right': '0',
                'width': '60%',
                'height': '60%',
                'background-size': 'cover',
                'background-attachment': 'fixed',
                'z-index': '-1',
            }),
        ])
    else:
        return None
 
@app.callback(
    Output('trail-search-dropdown', 'style'),
    [Input('url', 'pathname')]
)
def toggle_search_visibility(pathname):
    if pathname == '/' or pathname == '/all-trails':
        return {
                'width':'600px',
                'padding': '12px',
                'margin-top': '10px',
                'margin-right': '16px',
                'font-size': '16px',
                'border-radius': '30px',
                'vertical-align':'center'
                }
    else:
        return {'display': 'none'}
   
@app.callback(
    [Output('trail-cards-row', 'children'),
     Output('trail-info', 'children')],
    [Input('url', 'pathname'),
     Input('trail-search-dropdown', 'value')]
)
def update_trail_info(pathname, search_input):
    url = pathname[1:]
    if len(url) == 0:
        if search_input is None or search_input == '':
            filtered_trails = df
        else:
            filtered_trails = df[df['name'].str.contains(search_input, case=False)]
 
        cards = [
            dbc.Col(create_trail_card(index+1, row['name'], row['duration'], row['elevation_gain'], row['distance']), width=4)
            for index, row in filtered_trails.iterrows()
        ]
        return html.Div(className='trail-cards', style={'padding-top': '20px', 'margin-left': '20px'}, children=[
            dbc.Row(id='trail-cards-row', children=cards)
        ]), None
    else:
        splitname = [x.split('-') for x in url.split('---')]
        trail_name = ' - '.join([' '.join(x) for x in splitname])
        trail = df[df['name'] == trail_name]
        description = trail['description'].values[0]
        duration = trail['duration'].values[0]
        elevation_gain = trail['elevation_gain'].values[0]
        distance = trail['distance'].values[0]
        dist_mel = trail['distance_from_mel'].values[0]
        time_mel = trail['drive_from_mel'].values[0]
        loop = trail['loop'].values[0]
   
        return None, html.Div([
            dbc.Row([
                dcc.Link(html.I(className="fas fa-arrow-left", style={'margin-right': '5px'}), href='/'),
                dcc.Link('View all trails', href='/', className='active')
                ], style={'margin': '0 auto', 'padding': '40px'}),
            dbc.Row(html.H2(trail_name, style={'color': '#112434', 'text-decoration': 'none', 'margin-bottom': '15px',
                                               'margin-left':'40px'})),
            dbc.Row([
                dbc.Col(html.Img(src=b64_image(f"assets/{trail_name}.jpg"),
                                 style={'max-width': '100%', 'height': 'auto'}), width=4),
                dbc.Col([
                    html.P(description, style={'margin-left': '30px', 'text-align': 'justify'}),
                    html.Div([
                        dbc.Row([
                            dbc.Col([
                                html.I(className="fas fa-clock", style={'color': '#808080', 'margin-right': '5px', 'margin-top': '20px', 'margin-left':'30px'}),
                                html.Span(f"Duration: {duration}hours", style={'color': '#808080'}),
                                html.Div(""),
                                html.I(className="fas fa-mountain", style={'color': '#808080', 'margin-right': '5px', 'margin-left': '30px', 'margin-top':'15px'}),  # Mountain icon
                                html.Span(f"Elevation Gain: {elevation_gain}m", style={'color': '#808080'}),
                                html.Div(""),
                                html.I(className="fas fa-route", style={'color': '#808080', 'margin-right': '5px', 'margin-left': '30px', 'margin-top':'15px'}),  # Route icon
                                html.Span(f" Distance: {distance}km", style={'color': '#808080'}),
                            ], width=3),
                            dbc.Col([
                                html.I(className="fas fa-solid fa-car", style={'color': '#808080', 'margin-right': '5px', 'margin-top': '20px', 'margin-left':'200px'}),
                                html.Span(f"Drive from Melbourne: {time_mel}hours", style={'color': '#808080'}),
                                html.Div(""),
                                html.I(className="fas fa-map-pin", style={'color': '#808080', 'margin-right': '5px', 'margin-top': '15px', 'margin-left':'200px'}),
                                html.Span(f"Distance from Melbourne: {dist_mel}km", style={'color': '#808080'}),
                                html.Div(""),
                                html.I(className="fas fa-redo", style={'color': '#808080', 'margin-right': '5px', 'margin-top': '15px', 'margin-left':'200px'}),
                                html.Span(f"Trail route: {loop}", style={'color': '#808080'}),
                            ], width=3),
                        ], style={'display': 'flex'}),
                ])], width=4)
            ], style={'margin': '0 30px', 'padding': '40px', 'display': 'flex', 'border': '1px solid', 'border-color': 'rgba(0, 0, 0, 0.2)', 'border-radius': '50px', 'box-shadow': '0 2px 4px rgba(0, 0, 0, 0.1)',}),
            dbc.Row([
            dl.Map(
                id='trail-map',
                children=[dl.TileLayer(), dl.LayerGroup(id='trail-layer'), dl.LayerGroup(id='image-layer')],
                style={'width': '70%', 'height': '500px', 'margin-top': '15px', 'margin-left':'200px', 'align':'center'},
                center=(-37.8136, 144.9631),
                zoom=12)
    ])
    ])
       
@app.callback(
    [Output('trail-layer', 'children'), Output('trail-map', 'center')],
    [Input('url', 'pathname')],
    prevent_initial_call=True
)
def update_map(pathname):
    if not pathname or pathname == '/':
        return [], dash.no_update
    pathname = pathname[1:]
    splitname = [x.split('-') for x in pathname.split('---')]
    trail_name = ' - '.join([' '.join(x) for x in splitname])
    gpx_path = os.path.join('data/trails', f'{trail_name}.gpx')
    line_string = gpx_to_points(gpx_path)
    centroid = line_string.centroid.coords[0]
    positions = list(line_string.coords)
    features = [dl.Polyline(positions=positions, color='blue')]
    return features, centroid
 
@app.callback(
    [Output('image-layer', 'children')],
    [Input('url', 'pathname')],
    [State('trail-map', 'zoom')]
)
def display_image_marker(pathname, zoom):
    if zoom is None:
        zoom = 10
 
    markers = []
    if not pathname or pathname == '/':
        return [dash.no_update]
    pathname = pathname[1:]
    splitname = [x.split('-') for x in pathname.split('---')]
    trail_name = ' - '.join([' '.join(x) for x in splitname])
    gpx_path = os.path.join('data/trails', f'{trail_name}.gpx')
   
    if not os.path.exists(gpx_path):
        return [dash.no_update]
 
    trail_points = gpx_to_points(gpx_path).coords
    start_marker = dl.Marker(
        position=trail_points[0],
        children=[dl.Tooltip("Start")],
        icon={
            "iconUrl": 'assets/start.png',
            "iconSize": [zoom * 10, zoom * 10],
            "className": "dynamic-icon"
        }
    )
    finish_marker = dl.Marker(
        position=trail_points[-1],
        children=[dl.Tooltip("Finish")],
        icon={
            "iconUrl": 'assets/finish.png',
            "iconSize": [zoom * 10, zoom * 10],
            "className": "dynamic-icon"
        }
    )
    markers.extend([start_marker, finish_marker])
    return [markers]
 
 
 
if __name__ == '__main__':
    app.run_server(debug=True)