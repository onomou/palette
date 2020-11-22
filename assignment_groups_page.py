from dash_app import app
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from canvas_offline import *


assignment_groups_page = html.Div(
    id='assignment_groups_page',
    children = [
        dcc.Loading(
            id='assignment_groups_page_loading',
            children=[
                dcc.Dropdown(
                    id='assignment_groups_list',
                    multi=False,
                    placeholder='Assignment Group',
                ),
            ],
        ),
        dash_table.DataTable(
            id='assignment_groups_assignment_table',
            columns=[
                {'name':'Name', 'id': 'name'},
                {'name':'ID', 'id': 'id'},
                {'name':'Group', 'id': 'group'},
            ],
            sort_action="native",
            sort_mode="multi",
        )
    ],
)

'''
Callbacks
'''
@app.callback(
    Output('assignment_groups_list', 'options'),
    [
        Input('assignment_groups_link', 'n_clicks'),
        State('user_api_url', 'data'),
        State('user_api_key', 'data'),
        State('courses_dropdown', 'value'),
    ]
)
def load_assignment_groups_page(n_clicks, api_url, api_key, current_course):
    if n_clicks is None and current_course is None:
        raise PreventUpdate
    else:
        course = get_course(api_url, api_key, current_course)
        if course is None:
            raise PreventUpdate
        else:
            assignment_groups = course.assignment_groups
            return [{'label':x.name,'value':x.id} for x in assignment_groups]

@app.callback(
    Output('assignment_groups_assignment_table', 'data'),
    [Input('assignment_groups_list', 'value'),
     State('user_api_url', 'data'),
     State('user_api_key', 'data'),
     State('courses_dropdown', 'value'),]
)
def populate_assignment_groups_assignment_table(assignment_group_id, api_url, api_key, current_course):
    if assignment_group_id is None:
        raise PreventUpdate
    elif  api_url is None or api_key is None:
        return [{'name':None,'id':None,'group':None}]
    else:
        course = get_course(api_url, api_key, current_course)
        if course is None:
            raise PreventUpdate
        else:
            table_data = [
                {
                    'name':assignment.name,
                    'id':assignment.id,
                    'group':assignment.assignment_group_id
                } for assignment in course.assignments if assignment.assignment_group_id == assignment_group_id
            ]
            return table_data
