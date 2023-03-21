import datetime
import io
import json

import dash
from dash import dash_table
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import base64

from PIL import Image
from predict import initialize, predict_image

initialize()

app = dash.Dash(__name__)
# Expose Flask instance
server = app.server

app.layout = html.Div([
    html.Video(id="videoElement",autoPlay=True,height=500,width=500),
    html.Canvas(id="screenshot-canvas"),
    html.Img(id="contentsCamera",height=500,width=500),
    dcc.Input(
            id="secretId",type="text",value=''
        ),
    dcc.Upload(
        id='upload-image',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(id='output-image-upload'),
    html.Div(id="container")
])

def myFunc(e):
  return e["probability"]

def parse_contents(contents, filename, date, y):
    myList = sorted(y["predictions"], key=myFunc, reverse=True)
    return html.Div([
        html.Div(myList[0]["tagName"]),
        # HTML images accept base64 encoded strings in the same format
        # that is supplied by the upload
        html.Img(src=contents,height=500,width=500),
        html.Hr(),
        dash_table.DataTable(myList)
    ])

@app.callback(
    Output("container", "children"),
    Input("contentsCamera", "src")
)
def update_output(input):
    print("inside the function");
    print(input)
    if input is not None:
        base64Image = base64.b64decode(input.split(",")[1]);
        img = Image.open(io.BytesIO(base64Image))
        Y = predict_image(base64Image)
        children = parse_contents(base64Image, "", "", Y)
        print(children)
        return children

@app.callback(Output('output-image-upload', 'children'),
              Input('upload-image', 'contents'),
              State('upload-image', 'filename'),
              State('upload-image', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        base64Image = base64.b64decode(list_of_contents[0].split(",")[1]);
        img = Image.open(io.BytesIO(base64Image))
        Y = predict_image(img)
        children = parse_contents(list_of_contents[0], list_of_names[0], list_of_dates[0], Y)
        return children

if __name__ == '__main__':
    app.run_server(debug=True,port=8080)
