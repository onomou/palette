from dash_app import app
import dash_core_components as dcc
import dash_html_components as html
from canvas_offline import *
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_table

grades_page = html.Div(
    id='grades_page',
    children=[
        dcc.Loading(
            id='grades_assignments_list_loading',
            children=[
                dash_table.DataTable(
                    id='grades_table',
                    columns=[{'id': 'user_id', 'name': 'user_id'}],
                    editable=True,
                    data=[{'user_id':12345}]
                ),
            ],
        ),
    ],
)

'''
Callbacks
'''
@app.callback(
    [
        Output('grades_table', 'columns'),
        Output('grades_table', 'data'),
    ],
    [
        Input('grades_link', 'n_clicks'),
        State('user_api_url', 'data'),
        State('user_api_key', 'data'),
        State('courses_dropdown', 'value'),
        State('grades_table', 'columns')
    ]
)
def load_grades_page(n_clicks, api_url, api_key, current_course, existing_columns):
    if n_clicks is None and current_course is None:
        raise PreventUpdate
    else:
        course = get_course(api_url, api_key, current_course)
        print(f'get_course, {get_course.cache_info()}')
        if course is None:
            raise PreventUpdate
        else:
            for assignment in course.assignments:
                existing_columns.append({'id': str(assignment.id), 'name': str(assignment.id)})
            all_users = {user.id:{} for user in course.users}
            for assignment in course.assignments:
                for submission in assignment.submissions:
                    if submission.user_id in all_users:
                        all_users[submission.user_id][assignment.id] = submission.grade
            
            all_rows = []
            for user_id, grades in all_users.items():
                this_row = {'user_id': user_id}
                for assignment_id, grade in grades.items():
                    this_row[assignment_id] = grade
                all_rows.append(this_row)
            return (
                existing_columns, 
                all_rows,
            )
            
