from dash_app import app, server
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from canvas_offline import *


'''
Layout
'''
# the styles for the main content position it to the right of the sidebar and add some padding.
CONTENT_STYLE = {
    "position": "static",
    "margin-left": "12rem",
    "margin-top": "4rem",
    "margin-bottom": "4rem",
    "padding": "1rem 1rem",
    "z-index": "auto",
}

from importlib import import_module

from sidebar import sidebar, header, footer
pages_imports = {
    'assignments_page': 'assignments_page',
    'settings_page': 'settings_page',
    'assignment_groups_page': 'assignment_groups_page',
    'modules_page': 'modules_page',
    'users_page': 'users_page',
    'grades_page': 'grades_page',
    'log_page': 'log_page',
    'about_page':'about_page',
}
for variable, module in pages_imports.items():
   exec('from ' + module +' import ' + variable)
page_names = {key[:-5]:eval(key) for key in pages_imports.keys()}

content = html.Div(id="page-content", style=CONTENT_STYLE)

'''
Main Layout
'''
app.title = 'Palette - a GUI for Canvas' 
app.validation_layout = html.Div(
    children=[
        dcc.Location(id="url"),
        header,
        footer,
        sidebar,
        content,
    ] + [
        list(page_names.values())
        # eval(module) for module in pages_imports.keys()
    ]
)
app.layout = html.Div(
    children = [
        dcc.Location(id="url"),
        header,
        footer,
        sidebar,
        content,
    ],
    style={'max-width': '1000px',},
)

'''
Callbacks
'''

# connect to Canvas API with given URL and key
@app.callback(
    [Output('user_api_url', 'data'),
     Output('user_api_key', 'data'),
     Output('api_url_connected', 'children'),
     ],
    [Input('user_api_store_a', 'data'),
     Input('user_api_store_b', 'data'),
     ],
)
def init_canvas(api_a, api_b):
    if api_a is not None and 'api_url' in api_a and 'api_key' in api_a:
        # cache.clear()
        api_url = api_a['api_url']
        api_key = api_a['api_key']
    elif api_b is not None and 'api_url' in api_b and 'api_key' in api_b:
        api_url = api_b['api_url']
        api_key = api_b['api_key']
    else:
        raise PreventUpdate
    try:
        canvas = get_canvas(api_url, api_key)
        if canvas is None:
            return(
                None,
                None,
                ['Something broke here... Error while connecting to Canvas'],
            )
        else:
            return (
                api_url,
                api_key,
                ['Connected to ',html.A(html.Strong(api_url),href=api_url,target='_blank')],
            )
    except:
        return(
            None,
            None,
            ['Something broke here... Error while connecting to Canvas'],
        )

# use the current pathname to set the active state of the
# corresponding nav link to true so users to see which page they are on
@app.callback(
    [Output(f"{i}_link", "active") for i in page_names.keys()],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return [True] + [False for i in page_names.keys()][1:]
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



if __name__ == '__main__':
    app.run_server(debug=True)
