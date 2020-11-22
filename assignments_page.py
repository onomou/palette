from dash_app import app
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from canvas_offline import *

from markdownify import markdownify # to format assignment description
import textwrap # to wrap tooltips



assignments_page = html.Div(
    id="assignments_page",
    children=[
        dcc.Store(id='assignment_details_store', storage_type='local'),
        dcc.Loading(
            id='assignments_list_loading',
            children=[
                dcc.Dropdown(
                    id='assignments_list',
                    multi=True,
                    placeholder='Select one or more assignments',
                    # persistence=True,
                    # persistence_type='memory',
                ),
            ],
        ),

        dcc.Tabs(
            id='assignment_tabs',
            children=[
                dcc.Tab(
                    label='Details',
                    children=[
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
                            dcc.Tabs(
                                id='assignment_description',
                                children=[
                                    dcc.Tab(label='HTML',id='assignment_description_html'),
                                    dcc.Tab(label='Markdown',id='assignment_description_markdown'),
                                ],
                            )
                        ], style={
                            'border-style':'solid',
                            'border-color':'#000000',
                            # 'width':'50%',
                        }),

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
                    ],
                ),
                dcc.Tab(
                    label='Grades',
                    children=[
                        dash_table.DataTable(
                            id='grades_table_two',
                            columns=[
                                {'name':'ID', 'id': 'id', 'hideable': True},
                                {'name':'Name', 'id': 'user_name', 'hideable': True},
                                {'name':'Attempt', 'id': 'attempt', 'hideable': True},
                                {'name':'Student ID', 'id': 'user_id', 'hideable': True},
                                {'name':'Entered Grade', 'id': 'grade', 'hideable': True},
                                {'name':'Penalty', 'id': 'points_deducted', 'hideable': True},
                                {'name':'Final Score', 'id': 'final_score', 'hideable': True},
                                {'name':'Comment', 'id': 'comment', 'hideable': True},
                                {'name':'Previous Comments', 'id': 'comments', 'hideable': True},
                                {'name':'Excused', 'id': 'excused', 'hideable': True},
                                {'name':'Late Status', 'id': 'late_policy_status', 'hideable': True},
                                {'name':'Days Late', 'id': 'seconds_late', 'hideable': True},
                                {'name':'Preview', 'id': 'preview_url', 'hideable': True},
                                {'name':'Download', 'id': 'download_url', 'hideable': True},
                                {'name':'Open', 'id': 'open', 'hideable': True},
                                {'name':'Upload', 'id': 'upload', 'hideable': True},
                            ],
                            hidden_columns=['id','user_id',],
                        ),
                    ],
                ),
            ],
        ),
    ],
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
     State('courses_dropdown', 'value'),]
)
def load_assignments_page(n_clicks, api_url, api_key, current_course):
    if current_course is None and (n_clicks is None or api_url is None or api_key is None):
        raise PreventUpdate
    #canvas = get_canvas(api_store)
    #cache.clear()
    course = get_course(api_url, api_key, current_course)

    if course is None:
        raise PreventUpdate
    else:
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
        Output('grades_table_two', 'data'),
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
        return ([],'','','','','','','','','','','',[],'',[],[],)
    print(assignment_ids)
    course = get_course(api_url, api_key, current_course)
    assignments = [course.assignment.get(assignment_id) for assignment_id in assignment_ids]
    assignment_groups = course.assignment_groups

    # TODO: support multiple assignments
    assignments = [x for x in assignments if x.id in assignment_ids]
    assignment = assignments[0]
    if len(assignments) > 1:
        assignment_groups = []
    else:
        pass
    
    # grades table things go here
    data_rows = []
    for submission in assignment.submissions:
        this_row = {
            'id': submission.id,
            'user_name': getattr(course.user.get(submission.user_id),'name',submission.user_id),
            'attempt': submission.attempt,
            'user_id': submission.user_id,
            'entered': submission.entered_score,# will be overwritten by posted_grade
            'points_deducted': submission.points_deducted,
            'grade': submission.grade,
            # 'comment': submission.comment,
            'comments': textwrap.fill('\n'.join([f"({x['created_at']}) {x['author_name']}: {x['comment']}" for x in submission.submission_comments]),60),
            'excused': submission.excused,
            'late_policy_status': submission.late_policy_status,
            'seconds_late': submission.seconds_late,
            # 'preview_url': submission.preview_url,
            # 'download_url': submission.download_url,
            # 'open': submission.open,
            # 'upload': submission.upload,
        }
        data_rows.append(this_row)
    
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
        markdownify(assignment.description or '_No description set in Canvas_'),
        assignment.description,
        [{'label': 'None', 'value': 'None'}],
        assignment.grading_type,
        [x for x in assignment.submission_types],
        data_rows,
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
