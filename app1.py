import dash
from dash import dcc, html, Input, Output
import seaborn as sns
import plotly.express as px
# Load the tips_df dataset from Seaborn
tips_df = sns.load_dataset("tips")

# Get the categorical columns
categorical_columns = tips_df.select_dtypes(include=['category']).columns.tolist()

# Get the numeric columns
numeric_columns = tips_df.select_dtypes(include=['number']).columns.tolist()

dropdown1=html.Div(className="child1_1_1",children=[dcc.Dropdown(id='x-axis-dropdown',options=categorical_columns, value=categorical_columns[0])], style=dict(width="100%"))
dropdown2=html.Div(className="child1_1_2",children=[dcc.Dropdown(id='y-axis-dropdown',options=numeric_columns, value=numeric_columns[0])], style=dict(width="100%"))

radio1=html.Div(className="child2_1_1",children=[dcc.RadioItems(id='radio', options=["a"], value="", inline=True)])

app = dash.Dash(__name__)

app.layout = html.Div(className="parent", children=[
    html.Div(className="child1",children=[html.Div([dropdown1, dropdown2], className="child1_1"),html.Div(dcc.Graph(id="graph1"), className="child1_2")]),
    html.Div(className="child2",children=[html.Div(radio1, className="child2_1"),html.Div(dcc.Graph(id='graph2'), className="child2_2")])])

@app.callback([Output("graph1", "figure"), Output('radio', 'options')], [Input("x-axis-dropdown", "value"), Input("y-axis-dropdown", "value")])
def myfunc(x_axis_column, y_axis_column):
    avg_y = tips_df.groupby(x_axis_column)[y_axis_column].mean().reset_index()
    figure = px.bar(avg_y, x=x_axis_column, y=y_axis_column, text_auto=True)
    return figure,tips_df[x_axis_column].unique()

@app.callback(Output('graph2', 'figure'),[Input('radio', 'value'),Input('x-axis-dropdown', 'value'),Input('y-axis-dropdown', 'value')])
def update_graph(selected_value,x_attr,y_attr):
    if(len(selected_value)==0):
        return {}
    filtered_df=tips_df[tips_df[x_attr]==selected_value]
    figure = px.scatter(filtered_df, x=filtered_df.reset_index().index, y=y_attr)
    figure.update_layout(plot_bgcolor="#f7f7f7")
    figure.update_xaxes(showticklabels=False)
    figure.update_traces(marker=dict(size=10,color='gray',opacity=0.8))
    figure.add_shape(type="line", x0=0, x1=filtered_df.reset_index().index.max(), y0=filtered_df[y_attr].mean(), y1=filtered_df[y_attr].mean(), line=dict(color="#77a3ba", width=2))
    print(figure.layout.xaxis)
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
