from dash_app import app
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from canvas_offline import *

from markdownify import markdownify



assignments_page = html.Div(
    id="assignments_page",
    children=[
        dcc.Store(id='assignment_details_store', storage_type='local'),
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



'''
Callbacks
'''
# page click
@app.callback(
    [Output('assignments_list', 'options'),],
    [Input('assignments_link', 'n_clicks'),
     State('user_api_url', 'data'),
     State('user_api_key', 'data'),
     State('courses_dropdown', 'value')]
)
def load_assignments_page(n_clicks, api_url, api_key, current_course):
    if n_clicks is None or api_url is None or api_key is None:
        raise PreventUpdate
    #canvas = get_canvas(api_store)
    #cache.clear()
    course = get_course(api_url, api_key, current_course)

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
     State('user_api_url', 'data'),
     State('user_api_key', 'data'),
     State('courses_dropdown', 'value')]
)
def load_assignment_details(assignment_ids, api_url, api_key, current_course):
    if assignment_ids is None:
        raise PreventUpdate
    elif assignment_ids == []:
        return ([],'','','','','','','','','','',[],[],[],[])
    course = get_course(api_url, api_key, current_course)
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
        markdownify(details or '_No description set in Canvas_'),
        details,
        [{'label': 'None', 'value': 'None'}],
        assignment.grading_type,
        [x for x in assignment.submission_types],
    )

@app.callback(
    [
        Output('api_url_input','value'),
        Output('api_key_input','value'),
    ],
    [Input('settings_link', 'n_clicks'),
     State('user_api_url', 'data'),
     State('user_api_key', 'data'),]
)
def load_assignment_details(n_clicks, api_url, api_key):
    if n_clicks is None:
        raise PreventUpdate
    elif  api_url is None or api_key is None:
        return (None,None)
    else:
        return (
            api_url,
            api_key,
        )

# store which assignments are selected
@app.callback(
    [Output('assignment_details_store', 'data')],
    [Input('assignments_list', 'value'),]
)
def store_assignment_details(assignment_ids):
    return (
        {'selected_assignments': assignment_ids},
    )
