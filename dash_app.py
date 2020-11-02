# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from canvasapi import Canvas
import configparser
from markdownify import markdownify

config = configparser.ConfigParser()
config.optionxform = str
config.read('config.ini')

canvas = None

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)
app.title = 'Palette - a GUI for Canvas' 
app.layout = html.Div(children=[
    dcc.Store(id='user_api_store', storage_type='local'),
    html.H1(children='Canvas GUI -- in a browser!'),

    html.Div(children=[
        dcc.Input(id='api_url_input', placeholder='Your API URL'),
        dcc.Input(id='api_key_input', placeholder='Your API key'),
        html.P(children=[
            dcc.Loading(
                id='api_url_loading',
                type='default',
                children=[
                    html.P(id='api_url_connected'),
                    html.P(id='api_key_connected'),
                ]
            )
        ]),
        
    ]),
    html.Button('Load Canvas',id='load_canvas_button'),
    html.Button('Clear Configuration',id='clear_config_button'),

    html.Label([
        dcc.Dropdown(id='courses_dropdown',placeholder='Select a course')
    ]),
    html.Div([
        
        html.Label([
            dcc.Dropdown(id='assignments_list',multi=True,placeholder='Select one or more assignments')
        ]),

    ]),

    html.Div([
        html.P(id='assignment_id'),
        html.P(id='assignment_created', children='Created'),
        html.P(id='assignment_updated', children='Last Updated'),
        html.P(id='assignment_position', children='Position in Group'),
        html.P(id='assignment_needs_grading', children=''),
        dcc.Input(id='assignment_name', type='text', placeholder='Assignment Name'),
        dcc.Input(id='assignment_due_at', type='text', placeholder='Due At'),
        dcc.Input(id='assignment_points_possible', type='text', placeholder='Points Possible'),
        html.Button(id='assignment_webpage')
    ]),

    html.Div([
      
        html.Label([
            "Assignment Description (Markdown)",
            dcc.Markdown(id='assignment_description_markdown')
        ],style={'width': '48%', 'display': 'inline-block'}),

        html.Label([
            "Assignment Description (HTML)",
            html.P(id='assignment_description_html')
        ], style={'width': '48%', 'display': 'inline-block'}),
    ], style={'border-style':'solid','border-color':'#000000'}),

    html.Div([
        dcc.Dropdown(id='assignment_modules', placeholder='Assignment Modules', multi=True)
    ], style={'width': '24%', 'display': 'inline-block'}),
    html.Div([
        dcc.Dropdown(id='assignment_groups', placeholder='Assignment Group')
    ], style={'width': '24%', 'display': 'inline-block'}),
    html.Div([
        dcc.Dropdown(id='assignment_grading_type', placeholder='Assignment Grading Type')
    ], style={'width': '24%', 'display': 'inline-block'}),
    html.Div([
        dcc.Dropdown(id='assignment_submission_types', placeholder='Assignment Submission Types', multi=True)
    ], style={'width': '24%', 'display': 'inline-block'}),
])

@app.callback(
    Output('user_api_store', 'clear_data'),
    [Input('clear_config_button', 'n_clicks')],
)
def clear_config(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    return True


@app.callback(
    [Output('courses_dropdown', 'options'),
     Output('user_api_store', 'data'),
     Output('api_url_connected', 'children'),
     Output('api_key_connected', 'children')],
    [Input('load_canvas_button', 'n_clicks'),
     Input('api_url_input', 'value'),
     Input('api_key_input', 'value'),
     State('user_api_store', 'data'),]
)
def load_canvas(n_clicks, api_url, api_key, state_data):
    if state_data is not None:
        api_url = state_data['api_url']
        api_key = state_data['api_key']
    elif n_clicks is None:
        raise PreventUpdate

    global canvas, config
    try:
        #canvas = Canvas(config['Environment']['API_URL'],
        #                config['Environment']['API_KEY'])
        canvas = Canvas(api_url, api_key)
        canvas.api_url = api_url
        canvas.api_key = api_key
        canvas.courses = [x for x in canvas.get_courses()]
        canvas.courses_dict = {x.id: x for x in canvas.courses}
        
        return (
            [{'label': x.name, 'value': x.id} for x in canvas.courses],
            {'api_url': api_url, 'api_key': api_key},
            ['Connected to ',html.A(html.Strong(api_url),href=api_url,target='_blank')],
            ['Your API key is ',html.Strong(api_key)],
        )
    except:
        return [], f'Error connecting to site! Check your internet connection and API URL/key.', None, 'None', 'None'

@app.callback(
    [
        Output('assignments_list', 'options'),
        Output('assignment_groups', 'options'),
        Output('assignment_grading_type', 'options'),
        Output('assignment_submission_types', 'options'),
    ],
    [Input('courses_dropdown', 'value')]
)
def load_courses(course_ids):
    if course_ids is None:
        raise PreventUpdate
    canvas.current_course = canvas.courses_dict[course_ids]
    canvas.current_course.assignments = canvas.current_course.get_assignments()
    canvas.current_course.assignments_dict = {x.id: x for x in canvas.current_course.assignments}
    canvas.current_course.assignment_groups = canvas.current_course.get_assignment_groups()
    grading_types = ['pass_fail', 'percent', 'letter_grade', 'gpa_scale', 'points']
    submission_types = ['online_quiz', 'none', 'on_paper', 'discussion_topic',
                        'external_tool', 'online_upload', 'online_text_entry',
                        'online_url', 'media_recording']
    return (
        [{'label': x.name, 'value': x.id} for x in canvas.current_course.assignments],
        [{'label': x.name, 'value': x.id} for x in canvas.current_course.assignment_groups],
        [{'label': x, 'value': x} for x in grading_types],
        [{'label': x, 'value': x} for x in submission_types],
    )

@app.callback(
    [
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
        Output('assignment_groups', 'value'),
        Output('assignment_grading_type', 'value'),
        Output('assignment_submission_types', 'value'),
    ],
    [Input('assignments_list', 'value')]
)
def load_assignment_details(assignment_ids):
    if assignment_ids is None:
        raise PreventUpdate
    elif assignment_ids == []:
        return ('','','','','','','','','','',[],[],[],[])
    assignments = [canvas.current_course.assignments_dict[x] for x in assignment_ids]
    assignment = assignments[0]
    details = assignment.description
    return (
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
        assignment.assignment_group_id,
        assignment.grading_type,
        [x for x in assignment.submission_types],
    )

if __name__ == '__main__':
    app.run_server(debug=True)
