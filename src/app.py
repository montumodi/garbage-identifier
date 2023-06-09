import base64
from io import BytesIO
import time
import io

import dash
from dash import dash_table
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from predict_recycle_type_object_detection import initialize, predict_image
from predict_plastic_type_classification import initialize as initialize_plastic_classification, predict_image as predict_plastic_type_classification
from predict_recycle_type_classification import initialize as initialize_recycle_classification, predict_image as predict_recycle_classification

from PIL import Image
from carbon_emission import get_carbon_emission_graph
from plastic_type import mapping
from recycle_type import mapping as mapping_recycle
minimum_confidence_score = 0.10

initialize()
initialize_plastic_classification()
initialize_recycle_classification()
# plotly.py helper functions
bools = ('No','Yes')


def pil_to_b64(im, enc="png"):
    io_buf = BytesIO()
    im.save(io_buf, format=enc)
    encoded = base64.b64encode(io_buf.getvalue()).decode("utf-8")
    return f"data:img/{enc};base64, " + encoded

# Dash component wrappers


def Row(children=None, **kwargs):
    return html.Div(children, className="six columns", **kwargs)


def pil_to_fig(im, showlegend=False, title=None):
    img_width, img_height = im.size
    fig = go.Figure()
    # This trace is added to help the autoresize logic work.
    fig.add_trace(go.Scatter(
        x=[img_width * 0.05, img_width * 0.95],
        y=[img_height * 0.95, img_height * 0.05],
        showlegend=False, mode="markers", marker_opacity=0,
        hoverinfo="none", legendgroup='Image'))

    fig.add_layout_image(dict(
        source=pil_to_b64(im), sizing="stretch", opacity=1, layer="below",
        x=0, y=0, xref="x", yref="y", sizex=img_width, sizey=img_height,))

    # Adapt axes to the right width and height, lock aspect ratio
    fig.update_xaxes(
        showgrid=False, visible=False, constrain="domain", range=[0, img_width])

    fig.update_yaxes(
        showgrid=False, visible=False,
        scaleanchor="x", scaleratio=1,
        range=[img_height, 0])

    fig.update_layout(title=title, showlegend=showlegend)

    return fig


def add_bbox(fig, x0, y0, x1, y1,
             showlegend=True, name=None, color=None,
             opacity=0.5, group=None, text=None):
    fig.add_trace(go.Scatter(
        x=[x0, x1, x1, x0, x0],
        y=[y0, y0, y1, y1, y0],
        mode="lines",
        fill="toself",
        opacity=opacity,
        marker_color=color,
        hoveron="fills",
        name=name,
        hoverlabel_namelength=0,
        text=text,
        legendgroup=group,
        showlegend=showlegend,
    ))

def get_graph(id):
    return dcc.Graph(id=id, config={'displayModeBar': False}, figure={"layout": go.Layout(xaxis={'showgrid': False, 'visible': False, 'zeroline': False},yaxis = {'showgrid': False, 'zeroline': False, 'visible': False,})}, style={"height": "70vh"})

# colors for visualization
COLORS = ['#fe938c', '#86e7b8', '#f9ebe0', '#208aae', '#fe4a49',
          '#291711', '#5f4b66', '#b98b82', '#87f5fb', '#63326e'] * 50


# Start Dash
app = dash.Dash(__name__)
server = app.server  # Expose the server variable for deployments

def get_upload_control(id):
    return html.Div(children=[dcc.Upload(
             id=id,
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
             multiple=False
             )], className="row")

app.layout = html.Div(children=[
    html.Div(children=[html.H1("Sortify")], className="row"),
    dcc.Tabs([
        dcc.Tab(label='Recycle type detection (Multi)', id="recycle_tab", children=[
            get_upload_control("upload-image"),
            html.Div([
                dcc.Loading(
                     id="loading-model-ouput-prediction",
                     children=[get_graph("model-output")])], className="seven columns"),
            html.Div([
                dcc.Loading(
                    id="loading-model-ouput-graph",
                    children=[html.Div(id="emissions-graph")], type="circle")], className="four columns")
        ]),
        dcc.Tab(label='Recycle type detection (Single)', children=[
            html.Button('Open Camera', id='camera-btn',className="row"),
            html.Video(id='videoElement', autoPlay=True, className="seven columns", height=500, width=500),
            html.Div(id="data-table-recycle", className="four columns"),
            dcc.Interval(id='interval_id', interval=1000, n_intervals=0),
            dcc.Store(id="my_store",data=[]),
            html.Canvas(id="screenshot-canvas", hidden=True)
        ]),
        dcc.Tab(label='Plastic type detection', id="plastic_tab", children=[
            get_upload_control("upload-image-plastic"),
            html.Div([
                dcc.Loading(
                     id="loading-model-ouput-prediction-plastic",
                     children=[
                        get_graph("model-output-plastic")],
                     type="circle",
                     )
            ], className="seven columns"),
            html.Div(id="data-table-plastic", className="four columns")
        ])
    ])
])

def sort_func(e):
    return e["probability"]

def get_image(list_of_contents):
    base64Image = base64.b64decode(list_of_contents.split(",")[1])
    img = Image.open(io.BytesIO(base64Image))
    return img

@app.callback(Output("data-table-recycle", "children"),
              [Input("my_store", "data"), Input('camera-btn', 'n_clicks')])
def run_model_recycle_single(list_of_contents, n_clicks):
    if (list_of_contents is not None) and (str(list_of_contents) != 'data:,' and len(list_of_contents) > 3500) and (n_clicks is not None):
        # Get Image
        img = get_image(list_of_contents)

        # Predict
        tstart = time.time()
        predictions = predict_recycle_classification(img)
        tend = time.time()

        predictions = sorted(
            predictions["predictions"], key=sort_func, reverse=True)
        predicted_tag = predictions[0]['tagName']
        print(predicted_tag)
        element = [x for x in mapping_recycle if x["label"] == predicted_tag][0]
        
        return html.Div([
            html.H3(f"This looks like {element['full text']}. Confidence:{int(float(predictions[0]['probability']) * 100)}%"),
            html.H6(f'Can it be recycled?: {bools[element["is_recyclable"]]}'),
            html.H6(f'How can it be recycled?: {element["how_to_recyle"]}'),
            html.H6(f'This can be recycled at: {", ".join(element["places_it_can_be_recycled"])}'),
            ])
    return html.Div()

app.clientside_callback(
    """
    function(interval) {
        var video = document.querySelector("#videoElement");
        var canvas = document.querySelector("#screenshot-canvas");
        if(canvas)
            {
                canvas.width = 300; // video.videoWidth;
                canvas.height = 300; // video.videoHeight;
                var context = canvas.getContext("2d");
                context.drawImage(video, 0, 0);
                var dataURL = canvas.toDataURL();
                return dataURL;
            }
        return null;
    }
    """,
    Output("my_store", "data"),
    Input("interval_id", "n_intervals")

)

app.clientside_callback(
    """
        function(n_clicks) {
        if (n_clicks) {
            navigator.mediaDevices.getUserMedia({'video': {facingMode: 'environment'}})
            .then(function(stream) {
                document.getElementById('videoElement').srcObject = stream;
            })
            .catch(function(error) {
                console.error('Failed to open camera: ' + error.message);
            });
        }
    }
    """,
    Output('videoElement', 'src'),
    Input('camera-btn', 'n_clicks')
)

@app.callback(
    [Output('model-output', 'figure'),
     Output('emissions-graph', 'children')],
    [Input('upload-image', 'contents')])
def run_model(list_of_contents):
    if list_of_contents is not None:
        # Get Image
        img = get_image(list_of_contents)

        # Predict
        tstart = time.time()
        predictions = predict_image(img)
        tend = time.time()

        # Plot
        fig = pil_to_fig(img, showlegend=True,
                         title=f'Predictions took {tend-tstart:.2f}s')
        predictions = sorted(
            predictions["predictions"], key=sort_func, reverse=True)
        predictions = list(filter(
            lambda item: item["probability"] >= minimum_confidence_score, predictions))
        img_width, img_height = img.size

        for bbox in predictions:
            left = bbox["boundingBox"]["left"]
            width = bbox["boundingBox"]["width"]
            height = bbox["boundingBox"]["height"]
            top = bbox["boundingBox"]["top"]

            x0 = left * img_width
            y0 = top * img_height
            x1 = (left + width) * img_width
            y1 = (top + height) * img_height
            label = bbox["tagName"]
            confidence = bbox["probability"]
            tagId = bbox["tagId"]
            text = f"class={label}<br>confidence={confidence:.3f}"
            add_bbox(
                fig, x0, y0, x1, y1,
                opacity=0.7, group=label, name=label, color=COLORS[tagId],
                showlegend=False, text=text
            )

        return [fig, get_carbon_emission_graph(predictions)]
    raise dash.exceptions.PreventUpdate

@app.callback(
    [Output('model-output-plastic', 'figure'),
     Output('data-table-plastic', 'children')],
    [Input('upload-image-plastic', 'contents')])
def run_model_plastic(list_of_contents):
    if list_of_contents is not None:
        # Get Image
        img = get_image(list_of_contents)

        # Predict
        tstart = time.time()
        predictions = predict_plastic_type_classification(img)
        tend = time.time()

        # Plot
        fig = pil_to_fig(img, showlegend=True,
                         title=f'Predictions took {tend-tstart:.2f}s')
        predictions = sorted(
            predictions["predictions"], key=sort_func, reverse=True)
        predicted_tag = predictions[0]['tagName']
        element = [x for x in mapping if x["label"] == predicted_tag][0]
        return [fig, html.Div([
            html.H3(f"This looks like {element['full text']}. Confidence:{int(float(predictions[0]['probability']) * 100)}%"),
            html.H6(f'Can it be recycled?: {bools[element["is_recyclable"]]}'),
            html.H6(f'How can it be recycled?: {element["how_to_recyle"]}'),
            html.H6(f'Some examples: {", ".join(element["examples"])}'),
            html.H6(f'This can be recycled into: {", ".join(element["recycle_into"])}'),
            html.H6(f'This can be recycled at: {", ".join(element["places_it_can_be_recycled"])}'),
            ])]
    raise dash.exceptions.PreventUpdate

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
