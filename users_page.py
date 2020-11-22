from dash_app import app
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_table
from canvas_offline import *
from dash.exceptions import PreventUpdate

enrollment_types = {
    'Student':'StudentEnrollment',
    'Teacher':'TeacherEnrollment',
    'TA':'TaEnrollment',
    'Observer':'ObserverEnrollment',
    'Designer':'DesignerEnrollment'
}

users_information = [
    {'api_name': 'id',             'display_name': 'ID',             'table_name': 'u_id',             },
    {'api_name': 'name',           'display_name': 'Name',           'table_name': 'u_name',           },
    {'api_name': 'created_at',     'display_name': 'Created At',     'table_name': 'u_created_at',     },
    {'api_name': 'sortable_name',  'display_name': 'Sortable Name',  'table_name': 'u_sortable_name',  },
    {'api_name': 'short_name',     'display_name': 'Short Name',     'table_name': 'u_short_name',     },
    {'api_name': 'sis_user_id',    'display_name': 'SIS User ID',    'table_name': 'u_sis_user_id',    },
    {'api_name': 'integration_id', 'display_name': 'Integration ID', 'table_name': 'u_integration_id', },
    {'api_name': 'root_account',   'display_name': 'Root Account',   'table_name': 'u_root_account',   },
    {'api_name': 'login_id',       'display_name': 'Login ID',       'table_name': 'u_login_id',       },
    {'api_name': 'email',          'display_name': 'Email',          'table_name': 'u_email',          },
]
enrollments_information = [
    {'api_name': 'id',                                 'display_name': 'Enrollment ID',          'table_name': 'e_id',                                 },
    {'api_name': 'course_section_id',                  'display_name': 'Section ID',             'table_name': 'e_course_section_id',                  },
    {'api_name': 'enrollment_state',                   'display_name': 'State',                  'table_name': 'e_enrollment_state',                   },
    {'api_name': 'type',                               'display_name': 'Type',                   'table_name': 'e_type',                               },
    {'api_name': 'user_id',                            'display_name': 'User ID',                'table_name': 'e_user_id',                            },
    {'api_name': 'root_account_id',                    'display_name': 'Root Account ID',        'table_name': 'e_root_account_id',                    },
    {'api_name': 'course_id',                          'display_name': 'Course',                 'table_name': 'e_course_id',                          },
    {'api_name': 'associated_user_id',                 'display_name': 'Associated User',        'table_name': 'e_associated_user_id',                 },
    {'api_name': 'created_at',                         'display_name': 'Created At',             'table_name': 'e_created_at',                         },
    {'api_name': 'created_at_date',                    'display_name': 'Created At Date',        'table_name': 'e_created_at_date',                    },
    {'api_name': 'updated_at',                         'display_name': 'Updated At',             'table_name': 'e_updated_at',                         },
    {'api_name': 'updated_at_date',                    'display_name': 'Updated At Date',        'table_name': 'e_updated_at_date',                    },
    {'api_name': 'start_at',                           'display_name': 'Start At',               'table_name': 'e_start_at',                           },
    {'api_name': 'end_at',                             'display_name': 'End At',                 'table_name': 'e_end_at',                             },
    {'api_name': 'last_activity_at',                   'display_name': 'Last Activity',          'table_name': 'e_last_activity_at',                   },
    {'api_name': 'total_activity_time',                'display_name': 'Total Activity Time',    'table_name': 'e_total_activity_time',                },
    {'api_name': 'html_url',                           'display_name': 'HTML URL',               'table_name': 'e_html_url',                           },
    {'api_name': 'limit_privileges_to_course_section', 'display_name': 'Limit...',               'table_name': 'e_limit_privileges_to_course_section', },
    {'api_name': 'role',                               'display_name': 'Role',                   'table_name': 'e_role',                               },
    {'api_name': 'role_id',                            'display_name': 'Role ID',                'table_name': 'e_role_id',                            },
    {'api_name': 'last_attended_at',                   'display_name': 'Last Attended At',       'table_name': 'e_last_attended_at',                   },
    {'api_name': 'sis_account_id',                     'display_name': 'SIS Account Id',         'table_name': 'e_sis_account_id',                     },
    {'api_name': 'sis_course_id',                      'display_name': 'SIS Course Id',          'table_name': 'e_sis_course_id',                      },
    {'api_name': 'course_integration_id',              'display_name': 'Course Integration Id',  'table_name': 'e_course_integration_id',              },
    {'api_name': 'sis_section_id',                     'display_name': 'Sis Section Id',         'table_name': 'e_sis_section_id',                     },
    {'api_name': 'section_integration_id',             'display_name': 'Section Integration Id', 'table_name': 'e_section_integration_id',             },
    {'api_name': 'sis_user_id',                        'display_name': 'SIS User Id',            'table_name': 'e_sis_user_id',                        },
    # 'grades',
]
grades_information = [
    {'api_name': 'html_url',                'display_name': 'HTML URL',               'table_name': 'g_html_url',               },
    {'api_name': 'current_grade',           'display_name': 'Current Grade',          'table_name': 'g_current_grade',          },
    {'api_name': 'current_score',           'display_name': 'Current Score',          'table_name': 'g_current_score',          },
    {'api_name': 'final_grade',             'display_name': 'Final Grade',            'table_name': 'g_final_grade',            },
    {'api_name': 'final_score',             'display_name': 'Final Score',            'table_name': 'g_final_score',            },
    {'api_name': 'unposted_current_score',  'display_name': 'Unposted Current Score', 'table_name': 'g_unposted_current_score', },
    {'api_name': 'unposted_current_grade',  'display_name': 'Unposted Current Grade', 'table_name': 'g_unposted_current_grade', },
    {'api_name': 'unposted_final_score',    'display_name': 'Unposted Final Score',   'table_name': 'g_unposted_final_score',   },
    {'api_name': 'unposted_final_grade',    'display_name': 'Unposted Final Grade',   'table_name': 'g_unposted_final_grade',   },
]

hidden_columns = [
    'e_course_id',
    'e_course_integration_id',
    'e_course_section_id',
    'e_created_at',
    'e_end_at',
    'e_last_attended_at',
    'e_limit_privileges_to_course_section',
    'e_root_account_id',
    'e_section_integration_id',
    'e_sis_account_id',
    'e_sis_course_id',
    'e_sis_section_id',
    'e_sis_user_id',
    'e_start_at',
    'e_updated_at',

    'g_current_grade',
    'g_final_grade',
    'g_unposted_current_grade',
    'g_unposted_final_grade',

    'u_avatar_url',
    'u_bio',
    'u_enrollments',
    'u_id',
    'u_integration_id',
    'u_last_login',
    'u_locale',
    'u_sis_import_id',
    'u_sis_user_id',
    'u_time_zone',
]

users_page = html.Div(
    children=[
        dcc.Dropdown(
            id='users_type',
            options=[{'label':key,'value':val} for key, val in enrollment_types.items()],
            value=[x for x in enrollment_types.values()],
            multi=True,
        ),
        dcc.Checklist(
            id='show_inactive_enrollments',
            options=[
                {'label': 'Inactive', 'value': 'inactive'},
            ],
        ),
        html.Br(),
        dcc.Loading(
            id='enrollments_table_loading',
            children = [dash_table.DataTable(
                id='enrollments_table',
                columns=[
                    {'name':x['display_name'],'id':x['table_name'],'hideable': True} for x in enrollments_information + grades_information + users_information
                ],
                hidden_columns=hidden_columns,
                # fixed_rows={'headers': True},
                tooltip_header={x['table_name']:x['api_name'] for x in enrollments_information},
                sort_action="native",
                sort_mode="multi",
                style_header={'textDecoration': 'underline','textDecorationStyle': 'dotted', 'overflow-wrap': 'normal'}, # overflow-wrap doesn't do anything right now
            ),],
        )
    ],
)


'''
Callbacks
'''
@app.callback(
    [
        Output(f'enrollments_table', 'data'),
    ],
    [
        Input('users_link', 'n_clicks'),
        Input('users_type', 'value'),
        Input('show_inactive_enrollments', 'value'),
        State('user_api_url', 'data'),
        State('user_api_key', 'data'),
        State('courses_dropdown', 'value'),
    ]
)
def load_users_page(n_clicks, users_type, show_inactive_enrollments, api_url, api_key, current_course):
    if n_clicks is None and current_course is None:
        raise PreventUpdate
    else:
        course = get_course(api_url, api_key, current_course)
        if course is None:
            raise PreventUpdate
        else:
            # users_dict = {x.id:x for x in course.users}
            users_table_out = []
            enrollments_table_out = []
            # grades_table_out = []
            for enrollment in course.get_enrollments():
                if not show_inactive_enrollments and enrollment.enrollment_state == 'inactive':
                    continue
                if enrollment.type in users_type:
                    this_row = {x['table_name']:getattr(enrollment,x['api_name'],'') for x in enrollments_information}
                    if hasattr(enrollment,'grades'):
                        this_row.update({x['table_name']:enrollment.grades.get(x['api_name']) for x in grades_information})
                    if enrollment.user_id in course.users:
                        user = course.users[enrollment.user_id]
                        this_row.update({x['table_name']:getattr(user,x['api_name'],'') for x in users_information})
                    enrollments_table_out.append(this_row)
            return [
                enrollments_table_out,
            ]
