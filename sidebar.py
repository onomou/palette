from dash_app import app
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from canvas_offline import *
from dateutil.parser import parse
from datetime import datetime

'''
Layout
'''
# From https://dash-bootstrap-components.opensource.faculty.ai/examples/simple-sidebar/
# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": "3rem",
    "width": "12rem",
    "padding": "1rem 1rem",
    "background-color": "rgb(138, 188, 242)",
    "border-right": "thin lightgrey solid",
    "z-index":"10",
}
HEADER_STYLE = {
    "position": "fixed",
    "margin-left": "12rem",
    "top": 0,
    "width": "100%",
    "height": "4rem",
    "padding": "1rem 1rem",
    "background-color": "#f8f9fa",
    "border-right": "thin lightgrey solid",
    "z-index":"10",
}
FOOTER_STYLE = {
    "position": "fixed",
    "bottom": "0rem",
    "height": "3rem",
    "padding": "0.7rem 1rem",
    "width": "100%",
    "background": "white",
    "font-size": "small",
    "background-color": "#3b4045",
    "color": "white",
    "z-index":"10",
}

header = html.Header(
    [
        dcc.Store(id='user_api_url', storage_type='local'),
        dcc.Store(id='user_api_key', storage_type='local'),
        dcc.Store(id='user_api_store_a', storage_type='local'),
        dcc.Store(id='user_api_store_b', storage_type='local'),
        dcc.Store(id='current_course', storage_type='local'),
        dbc.Nav(
            [
                dbc.NavLink("Assignments", href="/assignments", id="assignments_link"),
                dbc.NavLink("Assignment Groups", href="/assignment_groups", id="assignment_groups_link"),
                dbc.NavLink("Modules", href="/modules", id="modules_link"),
                dbc.NavLink("Users", href="/users", id="users_link"),
                dbc.NavLink("Grades", href="/grades", id="grades_link"),
                dbc.NavLink("Settings", href="/settings", id="settings_link"),
                dbc.NavLink("Log", href="/log", id="log_link"),
                dbc.NavLink("About", href="/about", id="about_link"),
            ],
            pills=True,
        ),
    ], style=HEADER_STYLE
)

footer = html.Footer(
    [
        dbc.Button('Reload from cache',id='reload_cache_button',color="primary",size='sm',style={'line-height':'1rem'}),
        html.Div([
            html.P('Not Connected',id='api_url_connected',style={"margin-left": "15px"}),
            html.Em('Status: '),
        ],style={'float':'right'}),
    ], style=FOOTER_STYLE
)


sidebar = html.Div(
    [
        html.H2("Palette", className="display-4"),
        html.Hr(),
        dcc.Dropdown(
            id='courses_dropdown',
            placeholder='Select a course',
            persistence=True,
            persistence_type='session',
            optionHeight=45,
            style={'font-size':'0.85em'}
        ),
        dcc.RadioItems(
            id='courses_filter',
            options=[
                {'label': 'All', 'value': 'all'},
                {'label': 'Current', 'value': 'current'},
                {'label': 'Concluded', 'value': 'concluded'},
            ],
            value='current',
            labelStyle={'display': 'block'},
        )
    ],
    style=SIDEBAR_STYLE,
)



'''
Callbacks
'''

@app.callback(
    [Output('courses_dropdown', 'options')],
    [Input('user_api_url', 'data'),
     Input('user_api_key', 'data'),
     Input('courses_filter', 'value')]
)
def load_courses_list(api_url, api_key, filter):
    canvas = get_canvas(api_url, api_key)
    if canvas is not None:
        if filter == 'all':
            courses = [x for x in canvas.courses]
        elif filter == 'current':
            courses = [x for x in canvas.courses if x.end_at is None or parse(x.end_at,ignoretz=True) > datetime.today()]
        elif filter == 'concluded':
            courses = [x for x in canvas.courses if x.end_at is not None and parse(x.end_at,ignoretz=True) < datetime.today()]
        
        return [{'label': x.course_code, 'value': x.id} for x in courses],
    else:
        raise PreventUpdate

@app.callback(
    [Output('user_api_store_b', 'data')],
    [Input('reload_cache_button', 'n_clicks'),
     State('user_api_url', 'data',),
     State('user_api_key', 'data',),],
)
def load_api_cache(n_clicks, api_url, api_key):
    if n_clicks is None or api_url is None or api_key is None:
        raise PreventUpdate
    else:
        return [{'api_key': api_key, 'api_url': api_url}]
