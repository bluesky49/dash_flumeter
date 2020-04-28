import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import extra_dash_ui_components as ex
import geopandas as gpd
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from dash.dependencies import Output, Input, State
import dash_table
import asyncio
import pandas as pd
import requests
import json

# Importing the dataset with ratio
flu_rate_df = pd.read_excel("FluDataColFine.xlsx")
cities = pd.read_csv("US_cities.csv", index_col=[0])

# Defining the name of the app
app_name = "FluMeter"

LOGOTYPE = "/assets/logo-placeholder.png"

# Instantianting the Dash APP
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR,  # DARK OPTIONS: CYBORG, SOLAR, DARKLY, SLATE, SUPERHERO
                                     'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
                                     'https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css'])

# Setting the name of the app
app.title = app_name

# server instance to run map when deploying
server = app.server

#dcc._css_dist[0]["relative_package_path"].append("styles.css")
app.css.config.serve_locally = True


flu_20 = dbc.Col([
    dbc.Row([
        dbc.Col(
            html.I([], className='fas fa-male white'),
            width="auto"),
        dbc.Col(
            html.I([], className='fas fa-male white'),
            width="auto"),
        dbc.Col(
            html.I([], className='fas fa-male white'),
            width="auto"),
        dbc.Col(
            html.I([], className='fas fa-male white'),
            width="auto"),
        dbc.Col(
            html.I([], className='fas fa-male red'),
            width="auto"),
    ], className="male-icons fitContent"),
    dbc.Row(dbc.Col(html.Div("REDUCED RISK OF FLU TRANSMITION",
                             className="text-center font-lg top32 bold")))
], width={'width': 8}, className="boxed bottom40 bgGray radius32 padding40")


flu_40 = dbc.Col([
    dbc.Row([
        dbc.Col(
            html.I([], className='fas fa-male white'),
            width="auto"),
        dbc.Col(
            html.I([], className='fas fa-male white'),
            width="auto"),
        dbc.Col(
            html.I([], className='fas fa-male white'),
            width="auto"),
        dbc.Col(
            html.I([], className='fas fa-male red'),
            width="auto"),
        dbc.Col(
            html.I([], className='fas fa-male red'),
            width="auto"),
    ], className="male-icons fitContent"),
    dbc.Row(dbc.Col(html.Div("MEDIUM TO LOW RISK OF FLU TRANSMITION",
                             className="text-center font-lg top32")))
], width={'width': 8}, className="boxed bottom24 bgGray radius32 padding40")


flu_60 = dbc.Col([
    dbc.Row([
        dbc.Col(
            html.I([], className='fas fa-male white'),
            width="auto"),
        dbc.Col(
            html.I([], className='fas fa-male white'),
            width="auto"),
        dbc.Col(
            html.I([], className='fas fa-male red'),
            width="auto"),
        dbc.Col(
            html.I([], className='fas fa-male red'),
            width="auto"),
        dbc.Col(
            html.I([], className='fas fa-male red'),
            width="auto"),
    ], className="male-icons fitContent"),
    dbc.Row(dbc.Col(html.Div("MEDIUM RISK OF FLU TRANSMITION",
                             className="text-center font-lg top32")))
], width={'width': 8}, className="boxed bottom24 bgGray radius32 padding40")


flu_80 = dbc.Col([
    dbc.Row([
        dbc.Col(
            html.I([], className='fas fa-male white'),
            width="auto"),
        dbc.Col(
            html.I([], className='fas fa-male red'),
            width="auto"),
        dbc.Col(
            html.I([], className='fas fa-male red'),
            width="auto"),
        dbc.Col(
            html.I([], className='fas fa-male red'),
            width="auto"),
        dbc.Col(
            html.I([], className='fas fa-male red'),
            width="auto"),
    ], className="male-icons fitContent"),
    dbc.Row(dbc.Col(html.Div("RELATIVE HIGH RISK OF FLU TRANSMITION",
                             className="text-center font-lg top32")))
], width={'width': 8}, className="boxed bottom24 bgGray radius32 padding40")


flu_100 = dbc.Col([
    dbc.Row([
        dbc.Col(
            html.I([], className='fas fa-male red'),
            width="auto"),
        dbc.Col(
            html.I([], className='fas fa-male red'),
            width="auto"),
        dbc.Col(
            html.I([], className='fas fa-male red'),
            width="auto"),
        dbc.Col(
            html.I([], className='fas fa-male red'),
            width="auto"),
        dbc.Col(
            html.I([], className='fas fa-male red'),
            width="auto"),
    ], className="male-icons fitContent"),
    dbc.Row(dbc.Col(html.Div("HIGH RISK OF FLU TRANSMITION",
                             className="text-center font-lg top32")))
], width={'width': 8}, className="boxed bottom24 bgGray radius32 padding40")


def flu_rate(rate):

    if rate <= 20:
        return flu_20

    elif (rate > 20 and rate <= 40):
        return flu_40

    elif (rate > 40 and rate <= 60):
        return flu_60

    elif (rate > 60 and rate <= 80):
        return flu_80

    elif (rate > 80 and rate <= 100):
        return flu_100


navbar = dbc.Navbar(
    [
        dbc.Col(html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(
                        html.Img(src=LOGOTYPE, height="85px")),
                ],
                align="center",
                # no_gutters=True,
            ),
            href="#",
        ), width=7),
        dbc.Col(dbc.NavbarBrand("FluMeter App", className="ml-4 right title",
                                style={'color': '#ffffffbf'}), width=5),

    ],
    color="rgb(51, 113, 130)", className="bottom16", style={'height': '100px'}
    # dark=True,
)


def get_div_children(text):
    return html.Div([
        dbc.Row([dbc.Col(html.Label("Temperature:", className="padding8"), width=7),
                 dbc.Col(html.Label("Modality: ", className="padding8"), width=5)]),
        dbc.Row([
            dbc.Col(dcc.Slider(
                id="fm_temp_slider",
                min=0,
                max=40,
                value=15,
                marks={
                    #-20: {'label': '-20 °C', 'style': {'color': '#f50'}},
                    0: {'label': '0°C', 'style': {'color': '#f50'} },
                    15: {'label': '15°C'},
                    30: {'label': '30°C'},                  
                    40: {'label': '40°C', 'style': {'color': '#f50'}}
                },
                className="bottom24",
                included=False
            ), width=7),
            dbc.Col(dbc.RadioItems(
                options=[
                    {"label": "Outdoor", "value": "Outdoor"},
                    {"label": "Indoor", "value": "Indoor"},
                ],
                value="Indoor",
                id="in-or-out-door",
                inline=True,
                )
            )           
        ]),
        html.Label("Humidity:", className="padding8"),
        dcc.Slider(
            id="fm_humid_slider",
            min=0,
            max=100,
            value=65,
            marks={
                0: {'label': '0%', 'style': {'color': '#f50'}},
                25: {'label': '25%'},
                50: {'label': '50%'},
                75: {'label': '75%'},
               100: {'label': '100%', 'style': {'color': '#f50'}}
            },
            className="bottom24",
            included=True
        ),
        html.Div(children=text),
        # button to submit the values Cities / Tempeature / Humidity
        dbc.Button("Apply", color="primary", block=True, className="top32", id="customize-button")
        # html.Div()
    ], className="info-sliders")


def display_vars(region=None, temp_c=None, humidity=None, modality="Indoor"):

    if (region and temp_c and humidity) is None:
        region = "San Francisco, CA, USA"
        temp_c = 15
        humidity = 40

    else:
        pass

    temp_f = int((temp_c * 9/5) + 32)

    region_html = [dbc.Col(html.P("Region: ", className="font-lg left bold"), width={"size": 3}),
                   dbc.Col(html.P(region, className="font-lg right"), width={"size": 9})]

    temperature_html = [dbc.Col(html.P("Temperature: ", className="font-lg left bold"), width=6),
                        dbc.Col(html.P(f"{temp_c}ºC ({temp_f}ºF)", className="font-lg right"), width=6)]

    humidity_html = [dbc.Col(html.P("Humidity: ", className="font-lg left bold"), width={"size": 6}),
                     dbc.Col(html.P(f"{humidity}%", className="font-lg right"), width={"size": 6})]

    modaility_html = [dbc.Col(html.P("Modality: ", className="font-lg left bold"), width={"size": 6}),
                     dbc.Col(html.P(f"{modality}", className="font-lg right"), width={"size": 6})]

    display_rows = dbc.Col([
        dbc.Row(region_html, className="text-center"),
        dbc.Row(temperature_html, className="text-center"),
        dbc.Row(humidity_html, className="text-center"),
        dbc.Row(modaility_html, className="text-center"),
    ], width=12, className="margin-auto")

    return display_rows

def city_values(text):

    title_buttons = html.Label([text], className="padding8")

    country = dbc.Col(dcc.Dropdown(
        id= "dropdown_country",
        placeholder="Select a Country",
        options=[{'label': i, 'value':i} for i in cities['Country'].unique()],
        value="US"
    ), width=4)

    state = dbc.Col(dcc.Dropdown(
        id="dropdown_state",
        placeholder="Select a State",
        value=""
    ), width = 4)

    city = dbc.Col(dcc.Dropdown(
        id="dropdown_city",
        placeholder="Select a City",
        value=""
    ), width=4)

    text = title_buttons

    location = dbc.Row([country, state, city], className="bottom8")

    return html.Div([text, location])


app_entry_trans_rate = html.Div([
    html.Div([html.P(["Flu Transmition Rate at your current location: ", 
                html.Span(id='flu_cont_range', className="font-xl inline-block padding8")],  
            className="font-xl inline-block padding8"),
            ])
], className="top8 text-center")


collase_buttons = html.Div([
    dbc.Button( 
        "Customize", color="primary",
        id="collapse-button",
        className="mr-1 bold font-md"),
    dbc.Collapse(
        dbc.Card(dbc.CardBody([
            city_values("Select your location: "),
            get_div_children( "Set Indoor temperature and humidity for higher precision."),
        ])),
        className="top32",
        id="collapse",
        is_open=False),
], className="boxed font-md")

# Starting the structure of the APP
app.layout = html.Div([
    navbar,
    ex.GeolocatorComponent(id="Geolocator"),
    html.Div(id="GeoOut"),
    # Container with the content
    dbc.Container([
        collase_buttons,
        app_entry_trans_rate,
        dbc.Row(id='flu_image'),
        html.Div(id='display_infos', className="boxed bottom40"),
        html.Div(id='fm_result')
    ])  # container close
])  # The main close of the application

# @app.callback(Output('GeoOut','children'),[Input('Geolocator','coords')])
# def display_geo(coords):
#     
            

    # city = 
    # state = 
    # country = 
    # display = display_vars(region=f"{city}, {state}, {country}",
    #                        temp_c=temp, humidity=humidity, modality=modality)
    # print(coords)



@app.callback([Output('flu_image', 'children'),
               Output('display_infos', 'children'),
               Output('flu_cont_range', 'children'),
               Output('GeoOut','children')],
              [Input('customize-button', 'n_clicks'),
               Input('Geolocator','coords')],
              [State('fm_temp_slider', 'value'),
               State('fm_humid_slider', 'value'),
               State('dropdown_country', 'value'),
               State('dropdown_state', 'value'),
               State('dropdown_city', 'value'), 
               State('in-or-out-door', 'value')])
def _upload_risk_display(n_clicks, coords, temp, humidity, country, state, city, modality):

    if n_clicks is not None:
        time.sleep(1)

    flu_rate_df['diff_temp'] = (flu_rate_df["T"] - temp)
    flu_rate_df['diff_humi'] = (flu_rate_df["RH"] - humidity)

    flu_rate_df['sum_diff'] = flu_rate_df["diff_humi"].abs() + flu_rate_df["diff_temp"].abs()

    value = flu_rate_df[flu_rate_df.index == flu_rate_df["sum_diff"].idxmin()]['Risk'].values.astype(int)

    var = flu_rate(value[0])
    cityName = city
    countryName = country
    stateName = state
    currentTemp = temp
    currentHumidity = humidity
    if(coords != None):
        altitude = coords['latitude']
        longitude = coords['longitude']
        coordinates = str(altitude) + ", " + str(longitude)
        locator = Nominatim(user_agent="myGeocoder")
        location = locator.reverse(coordinates)
        if ( cityName and countryName ) == "":
            if location != None:
                address = location.address
                address = address.split(', ')
                cityName = address[2]
                countryName = "US"
                stateName = address[3]
        parameter = {
            'lat' : coords['latitude'],
            'lon' : coords['longitude']
        }        
        response = requests.get("https://api.climacell.co/v3/weather/realtime?unit_system=si&fields=humidity&fields=temp&fields=pollen_tree&fields=pollen_weed&fields=pollen_grass&fields=baro_pressure&fields=dewpoint&apikey=pmUtNtawOgsT0PsgFXoeQUBC5fztvlOB&", parameter)
        byteData = response.content
        stringData = byteData.decode("utf-8")
        jsonData = json.loads(stringData) 
        currentTemp = int(jsonData['temp']['value'])
        urrentHumidity = int(jsonData['humidity']['value'])
        print(currentTemp , "-----------------------",currentHumidity)
    print("asdf")
    display = display_vars(region=f"{cityName}, {stateName}, {countryName}",
                           temp_c=currentTemp, humidity=currentHumidity, modality=modality)

    return [var], display, f"{value[0]}%", ""



# Collapse Filters
@app.callback(
    Output("dropdown_state", "options"),
    [Input("dropdown_country", "value")]
)
def toggle_collapse(country):

    state_options = cities[cities["Country"].isin([country])].fillna("Not Define")
    #print([{'label': j, 'value': i} for j, i in zip(state_options['State'].unique(), state_options['State'].unique() )])
    return [{'label': j, 'value': i} for j, i in zip(state_options['State_long'].unique(), state_options['State'].unique() )]

# Collapse Filters
@app.callback(
    Output("dropdown_city", "options"),
    [Input("dropdown_country", "value"),
     Input("dropdown_state", "value")]
)
def toggle_collapse(country, state):

    city_options = cities[cities["Country"].isin([country]) & cities["State"].isin([state])].fillna("Not Define")
    #print([{'label': j, 'value': i} for j, i in zip(state_options['State'].unique(), state_options['State'].unique() )])
    return [{'label': i, 'value': i} for i in city_options['Cities'].unique()]

import time

# Collapse Filters
@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks"), 
     Input("customize-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, n2, is_open):

    if n2:
         return not is_open
    else: 
        pass
    if n:
        return not is_open

    return is_open




if __name__ == '__main__':
    #app.run_server(debug=True)
    app.run_server(host="0.0.0.0", port=int("8080"), debug=True)