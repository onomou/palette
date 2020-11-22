from dash_app import app

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State, ALL

'''
Layout
'''
settings_page = html.Div(
    id="settings_page",
    children=[
        dbc.FormGroup([
            dcc.Input(id='api_url_input', placeholder='Your API URL',type='text',size='30'),
            dcc.Input(id='api_key_input', placeholder='Your API key',type='password',size='30'),
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



'''
Callbacks
'''
# clear API URL and key from cache
@app.callback(
    [Output('user_api_url', 'clear_data'),
     Output('user_api_key', 'clear_data'),
     Output('user_api_store_a', 'clear_data'),
     Output('user_api_store_b', 'clear_data'),],
    [Input('clear_config_button', 'n_clicks')],
)
def clear_config(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    cache.clear()
    return (True, True, True, True)

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
