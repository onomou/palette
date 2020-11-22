from dash_app import app
import dash_core_components as dcc

about_page = dcc.Markdown(
    '''
    This site is written by [Steven Williams](https://onomou.github.io).

    You can find the source code [on GitHub](https://github.com/onomou/palette).

    A live demo site is [on Heroku](http://canvas-palette.herokuapp.com/).

    Built with [Dash](https://plotly.com/) from Plotly.

    Uses the Python [CanvasAPI](https://github.com/ucfopen/canvasapi/) from University of Central Florida - Open Source.
    '''
)