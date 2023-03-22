import datetime
import io
import json

import dash
from dash import dash_table
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
import base64


from PIL import Image
from predict_classification import initialize, predict_image

initialize()

app = dash.Dash(__name__)
# Expose Flask instance
server = app.server

app.layout = html.Div([
    html.Video(id="videoElement", autoPlay=True, height=500, width=500),
    dcc.Interval(id='interval_id', interval=1000),
    dcc.Store(id="my_store"),
    html.Canvas(id="screenshot-canvas", hidden=True),
    # dcc.Input(
    #         id="secretId",type="text",value=''
    #     ),
    # dcc.Upload(
    #     id='upload-image',
    #     children=html.Div([
    #         'Drag and Drop or ',
    #         html.A('Select Files')
    #     ]),
    #     style={
    #         'width': '100%',
    #         'height': '60px',
    #         'lineHeight': '60px',
    #         'borderWidth': '1px',
    #         'borderStyle': 'dashed',
    #         'borderRadius': '5px',
    #         'textAlign': 'center',
    #         'margin': '10px'
    #     },
    #     # Allow multiple files to be uploaded
    #     multiple=True
    # ),
    html.Div(id='output-image-upload'),
    html.Div(id="container")
])


def myFunc(e):
    return e["probability"]


def parse_contents(contents, y):
    myList = sorted(y["predictions"], key=myFunc, reverse=True)
    return html.Div([
        html.Div(myList[0]["tagName"]),
        # HTML images accept base64 encoded strings in the same format
        # that is supplied by the upload
        # html.Img(src=contents,height=500,width=500),
        # html.Hr(),
        dash_table.DataTable(myList)
    ])


app.clientside_callback(
    """
    function(interval) {
        var video = document.querySelector("#videoElement");
        var canvas = document.querySelector("#screenshot-canvas");
        canvas.width = 300; // video.videoWidth;
        canvas.height = 300; // video.videoHeight;
        var context = canvas.getContext("2d");
        context.drawImage(video, 0, 0);
        var dataURL = canvas.toDataURL();
        return dataURL;
    }
    """,
    Output("my_store", "data"),
    Input("interval_id", "n_intervals")
)


@app.callback(Output("output-image-upload", "children"),
              Input("my_store", "data"))
def test_method(list_of_contents):
    if (list_of_contents is not None) and (str(list_of_contents) != 'data:,'):
        base64Image = base64.b64decode(list_of_contents.split(",")[1])
        img = Image.open(io.BytesIO(base64Image))
        Y = predict_image(img)
        children = parse_contents(list_of_contents, Y)
        return children

# @app.callback(Output('output-image-upload', 'children'),
#               Input('upload-image', 'contents'),
#               State('upload-image', 'filename'),
#               State('upload-image', 'last_modified'))
# def update_output(list_of_contents, list_of_names, list_of_dates):
#     if list_of_contents is not None:
#         base64Image = base64.b64decode(list_of_contents[0].split(",")[1]);
#         img = Image.open(io.BytesIO(base64Image))
#         Y = predict_image(img)
#         children = parse_contents(list_of_contents[0], list_of_names[0], list_of_dates[0], Y)
#         return children


if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
