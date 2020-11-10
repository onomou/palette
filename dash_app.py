# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from flask_caching import Cache

from canvasapi import Canvas
import configparser
from markdownify import markdownify

config = configparser.ConfigParser()
config.optionxform = str
config.read('config.ini')

canvas = None

external_stylesheets = [dbc.themes.BOOTSTRAP] # ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
server = app.server

# TODO: this
CACHE_CONFIG = {
    # try 'filesystem' if you don't want to setup redis
    # 'CACHE_TYPE': 'simple',
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
    # 'CACHE_TYPE': 'redis',
    # 'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379')
}
cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)

'''
Styles
'''

# From https://dash-bootstrap-components.opensource.faculty.ai/examples/simple-sidebar/
# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": "4rem",
    "width": "12rem",
    "padding": "1rem 1rem",
    "background-color": "#f8f9fa",
}
# the styles for the main content position it to the right of the sidebar and add some padding.
CONTENT_STYLE = {
    "position": "static",
    "margin-left": "12rem",
    "margin-top": "4rem",
    "margin-bottom": "4rem",
    "padding": "1rem 1rem",
    "z-index": "auto",
}
HEADER_STYLE = {
    "position": "fixed",
    "margin-left": "12rem",
    "top": 0,
    "width": "100%",
    "height": "4rem",
    "padding": "1rem 1rem",
    "background-color": "#f8f9fa",
    "border-bottom": "1px solid rgba(0,0,0,.1)",
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
}

'''
Layout
'''
header = html.Header(
    [
        dcc.Store(id='user_api_store', storage_type='local'),
        dcc.Store(id='user_api_store_a', storage_type='local'),
        dcc.Store(id='user_api_store_b', storage_type='local'),
        dcc.Store(id='current_course', storage_type='local'),
        dbc.Nav(
            [
                dbc.NavLink("Assignments", href="/assignments", id="assignments-link"),
                dbc.NavLink("Assignment Groups", href="/assignment-groups", id="assignment-groups-link"),
                dbc.NavLink("Modules", href="/modules", id="modules-link"),
                dbc.NavLink("Users", href="/users", id="users-link"),
                dbc.NavLink("Settings", href="/settings", id="settings-link"),
                dbc.NavLink("Log", href="/log", id="log-link"),
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
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

assignments_page = html.Div(
    id="assignments-page",
    children=[
        dcc.Dropdown(
            id='assignments_list',
            multi=True,
            placeholder='Select one or more assignments',
            # persistence=True,
            # persistence_type='memory',
        ),

        html.Div([
            html.P(id='assignment_id'),
            html.P(['Created: ',html.B(id='assignment_created')]),
            html.P(['Last Updated: ',html.B(id='assignment_updated')]),
            html.P(['Position in Group: ',html.B(id='assignment_position')]),
            html.P(['Needs Grading: ',html.B(id='assignment_needs_grading')]),
            html.Frame(title='Assignment Name',children=[dcc.Input(id='assignment_name', type='text', placeholder='Assignment Name')]),
            html.Frame(title='Due At',children=[dcc.Input(id='assignment_due_at', type='text')]),
            html.Frame(title='Points Possible',children=[dcc.Input(id='assignment_points_possible', type='text')]),
            dbc.Button('Web',id='assignment_webpage')
        ]),

        html.Div([
        
            html.Label([
                "Assignment Description (Markdown)",
                dcc.Markdown(id='assignment_description_markdown')
            ],style={'width': '48%', 'display': 'inline-block'}),

            html.Label([
                "Assignment Description (HTML)",
                html.P(id='assignment_description_html',contentEditable='true')
            ], style={'width': '48%', 'display': 'inline-block'}),
        ], style={'border-style':'solid','border-color':'#000000'}),

        html.Div([
            dcc.Dropdown(id='assignment_modules', placeholder='Assignment Modules', multi=True)
        ], style={'width': '24%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(id='assignment_groups', placeholder='Assignment Group', clearable=False)
        ], style={'width': '24%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='assignment_grading_type',
                options=[
                    {'label': 'pass_fail', 'value': 'pass_fail'},
                    {'label': 'percent', 'value': 'percent'},
                    {'label': 'letter_grade', 'value': 'letter_grade'},
                    {'label': 'gpa_scale', 'value': 'gpa_scale'},
                    {'label': 'points', 'value': 'points',},
                ],
                placeholder='Assignment Grading Type',
                clearable=False
            )
        ], style={'width': '24%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='assignment_submission_types', 
                options=[
                    {'label': 'online_quiz', 'value': 'online_quiz'},
                    {'label': 'none', 'value': 'none'},
                    {'label': 'on_paper', 'value': 'on_paper'},
                    {'label': 'discussion_topic', 'value': 'discussion_topic'},
                    {'label': 'external_tool', 'value': 'external_tool'},
                    {'label': 'online_upload', 'value': 'online_upload'},
                    {'label': 'online_text_entry', 'value': 'online_text_entry'},
                    {'label': 'online_url', 'value': 'online_url'},
                    {'label': 'media_recording', 'value': 'media_recording'},
                ],
                placeholder='Assignment Submission Types', 
                multi=True
            )
        ], style={'width': '24%', 'display': 'inline-block'}),
    ]
)

assignment_groups_page = html.Div(
    'Assignment Groups: no content here yet'
)

modules_page = html.Div(
    'Modules: no content here yet'
)

users_page = html.Div(
    'Users: no content here yet'
)

settings_page = html.Div(
    id="settings-page",
    children=[
        dbc.FormGroup([
            dcc.Input(id='api_url_input', placeholder='Your API URL',type='text',size='30'),
            dcc.Input(id='api_key_input', placeholder='Your API key',type='text',size='30'),
        ]),
        dbc.Button('Load Canvas',id='load_canvas_button',color="primary"),
        dbc.Button('Clear Configuration',id='clear_config_button',color="secondary",outline=True),
        dbc.FormGroup([
            dcc.Loading(
                id='api_url_loading',
                type='default',
                children=[
                    html.P(id='api_key_connected'),
                ]
            )
        ]),
    ]
)

log_page = html.Div(
    'Log: no content here yet'
)

url_and_sidebar = html.Div([dcc.Location(id="url"), sidebar])

app.title = 'Palette - a GUI for Canvas' 
app.validation_layout = html.Div(children=[
    header, url_and_sidebar, content, assignments_page, settings_page, footer
])
app.layout = html.Div(
    children = [
        header,
        footer,
        url_and_sidebar,
        content,
    ]
)



'''
Callbacks
'''

page_names = {
    'assignments':assignments_page,
    'assignment-groups':assignment_groups_page,
    'modules':modules_page,
    'users':users_page,
    'settings':settings_page,
    'log':log_page,
}
# use the current pathname to set the active state of the
# corresponding nav link to true so users to see which page they are on
@app.callback(
    [Output(f"{i}-link", "active") for i in page_names.keys()],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True, False, False
    return [pathname == f"/{i}" for i in page_names.keys()]

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/"]:
        return [assignments_page]
    elif pathname[1:] in page_names:
        return [page_names[pathname[1:]]]
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )

# clear API URL and key from cache
@app.callback(
    [Output('user_api_store', 'clear_data'),
     Output('user_api_store_a', 'clear_data'),
     Output('user_api_store_b', 'clear_data'),],
    [Input('clear_config_button', 'n_clicks')],
)
def clear_config(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    cache.clear()
    return (True, True, True)

@app.callback(
    [Output('user_api_store_a', 'data')],
    [Input('load_canvas_button', 'n_clicks'),
     Input('api_url_input', 'value'),
     Input('api_key_input', 'value'),
     ],
)
def save_api_info(n_clicks, api_url, api_key):
    if n_clicks is None:
        raise PreventUpdate
    else:
        return [{'api_url': api_url, 'api_key': api_key}]

@app.callback(
    [Output('user_api_store_b', 'data')],
    [Input('reload_cache_button', 'n_clicks'),
     State('user_api_store', 'data',)],
)
def load_api_cache(n_clicks, api_store):
    if n_clicks is not None and api_store is not None: # TODO: ensure api_store has the data required
        return [{'api_key': api_store['api_key'], 'api_url': api_store['api_url']}]
    else:
        raise PreventUpdate

# connect to Canvas API with given URL and key
@app.callback(
    [Output('user_api_store', 'data'),
     Output('api_url_connected', 'children'),
     ],
    [Input('user_api_store_a', 'data'),
     Input('user_api_store_b', 'data'),
     State('user_api_store', 'data'),
     ],
)
def init_canvas(api_a, api_b, api_store):
    if api_a is not None and 'api_url' in api_a and 'api_key' in api_a:
        print('Using user_api_store_a')
        # cache.clear()
        api_url = api_a['api_url']
        api_key = api_a['api_key']
    elif api_b is not None and 'api_url' in api_b and 'api_key' in api_b:
        print('Using user_api_store_b')
        api_url = api_b['api_url']
        api_key = api_b['api_key']
    else:
        raise PreventUpdate
    api_store_new = {'api_url': api_url, 'api_key': api_key}
    try:
        print(f'api_url is {api_url} and api_key is {api_key}')
        canvas = get_canvas(api_store_new)
        print(f'canvas is {canvas}')
        if canvas is None:
            print('Something broke here... Unable to connect to Canvas')
            raise PreventUpdate
        else:
            return (
                api_store_new,
                ['Connected to ',html.A(html.Strong(api_url),href=api_url,target='_blank')],
            )
    except:
        print('Something broke here... Error while connecting to Canvas')
        raise PreventUpdate

@app.callback(
    [Output('courses_dropdown', 'options')],
    [Input('user_api_store', 'data')]
)
def load_courses_list(api_store):
    canvas = get_canvas(api_store)
    if canvas is not None:
        return [{'label': x.name, 'value': x.id} for x in canvas.courses],
    else:
        raise PreventUpdate


# @app.callback(
#     Output('current_course', 'data'),
#     [Input('courses_dropdown', 'value'),
#      State('user_api_store', 'data')]
# )
# def load_course(course_id, api_store):
#     canvas = get_canvas(api_store)
#     if course_id is None:
#         raise PreventUpdate
#     course = canvas.get_course(course_id)
#     return course




@app.callback(
    [Output('assignments_list', 'options'),],
    [Input('assignments-page', 'n_clicks'),
     State('user_api_store', 'data'),
     State('courses_dropdown', 'value')]
)
def load_assignments_page(n_clicks, api_store, current_course):
    if n_clicks is None or api_store is None:
        raise PreventUpdate
    #canvas = get_canvas(api_store)
    course = get_course(api_store, current_course)
    if course is None:
        raise PreventUpdate
    else:
        assignments = course.assignments
        return [{'label': x.name, 'value': x.id} for x in course.assignments], 

@app.callback(
    [
        Output('assignment_groups', 'options'),
        Output('assignment_groups', 'value'),
        Output('assignment_id', 'children'),
        Output('assignment_created', 'children'),
        Output('assignment_updated', 'children'),
        Output('assignment_position', 'children'),
        Output('assignment_needs_grading', 'children'),
        Output('assignment_name', 'value'),
        Output('assignment_due_at', 'value'),
        Output('assignment_points_possible', 'value'),
        Output('assignment_description_markdown', 'children'),
        Output('assignment_description_html', 'children'),
        Output('assignment_modules', 'options'),
        Output('assignment_grading_type', 'value'),
        Output('assignment_submission_types', 'value'),
    ],
    [Input('assignments_list', 'value'),
     State('user_api_store', 'data'),
     State('courses_dropdown', 'value')]
)
def load_assignment_details(assignment_ids, api_store, current_course):
    if assignment_ids is None:
        raise PreventUpdate
    elif assignment_ids == []:
        return ([],'','','','','','','','','','',[],[],[],[])
    course = get_course(api_store, current_course)
    assignments = course.assignments
    assignment_groups = course.assignment_groups

    # TODO: support multiple assignments
    assignments = [x for x in assignments if x.id in assignment_ids]
    assignment = assignments[0]
    details = assignment.description
    if len(assignments) > 1:
        assignment_groups = []
    else:
        pass
    
    return (
        [{'label': x.name, 'value': x.id} for x in assignment_groups], # assignment_groups options
        assignment.assignment_group_id,
        assignment.id,
        assignment.created_at,
        assignment.updated_at,
        assignment.position,
        sum([getattr(assignment,'needs_grading_count',0)]),
        assignment.name,
        assignment.due_at,
        assignment.points_possible,
        markdownify(details),
        details,
        [{'label': 'None', 'value': 'None'}],
        assignment.grading_type,
        [x for x in assignment.submission_types],
    )

'''
Cached functions
'''
@cache.memoize(timeout=600)
def get_canvas(api_store):
    # global canvas, config
    try:
        #canvas = Canvas(config['Environment']['API_URL'],
        #                config['Environment']['API_KEY'])
        canvas = Canvas(api_store['api_url'], api_store['api_key'])
        canvas.api_url = api_store['api_url']
        canvas.api_key = api_store['api_key']
        canvas.courses = [x for x in canvas.get_courses()]
        canvas.courses_dict = {x.id: x for x in canvas.courses}
        return canvas
    except:
        return None

@cache.memoize(timeout=600)
def get_course(api_store, course_id):
    canvas = get_canvas(api_store)
    try:
        course = canvas.get_course(course_id)
        course.assignments = course.get_assignments()
        course.assignment_groups = course.get_assignment_groups()
        return course
    except:
        return None

if __name__ == '__main__':
    app.run_server(debug=True)
