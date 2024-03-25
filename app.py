import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load dataset
df = pd.read_csv("student_spending.csv")

# Lists of categories
spending_categories = ['tuition', 'housing', 'food', 
                       'transportation', 'books_supplies', 'entertainment', 'personal_care', 
                       'technology', 'health_wellness', 'miscellaneous']
earning_categories = ['monthly_income', 'financial_aid']
demographic_categories = ['gender', 'year_in_school', 'major']

# Initialize
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div([
    html.Link(
        rel='stylesheet',
        href='/assets/style.css'
    ),
    
    html.Div([
        html.Div([
            dcc.Graph(id='bar-chart-spending'),
            dcc.Graph(id='bar-chart-earning')
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id='bar-chart-total'),
            dcc.Graph(id='pie-chart')
        ], style={'width': '50%', 'display': 'inline-block'})
    ]),

    html.Div([
        # Demographic category dropdown
        html.Div([
            html.Div([
                dcc.Dropdown(
                id='demographic-selector',
                options=[{'label': category, 'value': category} for category in demographic_categories],
                value=demographic_categories[0],  # Default value
                clearable=False,
                style={'width': '100%'}  # Adjust width as needed
                )
            ]),
            # Radio items for selecting specific demographic option
            html.Div([
                dcc.RadioItems(id='demographic-options')
            ]),
        ], style={'width': '33%', 'display': 'inline-block'}),
        
        # Earning category checklist
        html.Div([
            dcc.Checklist(
                id='earning-categories',
                options=[{'label': category, 'value': category} for category in earning_categories],
                value=earning_categories[:1],  # Default value
                inline=True
            )
        ], style={'width': '33%', 'display': 'inline-block'}),
        
        html.Div([
            # Financial category checklist for spending
            dcc.Checklist(
                id='spending-categories',
                options=[{'label': category, 'value': category} for category in spending_categories],
                value=spending_categories[:3],  # Default value
                inline=True
            )
        ], style={'width': '33%', 'display': 'inline-block'}),
    ]),
])


# Define callback to populate radio items based on selected demographic category
@app.callback(
    Output('demographic-options', 'options'),
    [Input('demographic-selector', 'value')]
)
def update_demographic_options(selected_demographic):
    # Get unique options for the selected demographic category
    options = [{'label': option, 'value': option} for option in df[selected_demographic].unique()]
    return options

# Define callback to update bar chart for spending based on user inputs
@app.callback(
    Output('bar-chart-spending', 'figure'),
    [Input('demographic-selector', 'value'),
     Input('spending-categories', 'value')]
)
def update_bar_chart_spending(selected_demographic, selected_categories):
    # Filter the dataframe based on selected demographic category
    filtered_df = df.groupby(selected_demographic)[selected_categories].sum().reset_index()

    # Melt the dataframe to long format for plotting
    filtered_df = pd.melt(filtered_df, id_vars=selected_demographic, value_vars=selected_categories,
                          var_name='Spending Category', value_name='Total Spending')

    # Plot the bar chart for spending
    fig = px.bar(filtered_df, x=selected_demographic, y='Total Spending', color='Spending Category',
                 title='Total Spending by Category and Demographic Group')
    
    return fig

# Define callback to update bar chart for earning based on user inputs
@app.callback(
    Output('bar-chart-earning', 'figure'),
    [Input('demographic-selector', 'value'),
     Input('earning-categories', 'value')]
)
def update_bar_chart_earning(selected_demographic, selected_categories):
    # Filter the dataframe based on selected demographic category
    filtered_df = df.groupby(selected_demographic)[selected_categories].sum().reset_index()

    # Melt the dataframe to long format for plotting
    filtered_df = pd.melt(filtered_df, id_vars=selected_demographic, value_vars=selected_categories,
                          var_name='Earning Category', value_name='Total Earning')

    # Plot the bar chart for earning
    fig = px.bar(filtered_df, x=selected_demographic, y='Total Earning', color='Earning Category',
                 title='Total Earning by Category and Demographic Group')
    
    return fig

# Define callback to update bar chart for both spending and earning based on user inputs
@app.callback(
    Output('bar-chart-total', 'figure'),
    [Input('demographic-selector', 'value'),
     Input('spending-categories', 'value'),
     Input('earning-categories', 'value')]
)
def update_bar_chart_total(selected_demographic, selected_spending_categories, selected_earning_categories):
    # Filter the dataframe based on selected demographic category
    filtered_df = df.groupby(selected_demographic)[selected_spending_categories + selected_earning_categories].sum().reset_index()

    # Melt the dataframe to long format for plotting
    spending_df = pd.melt(filtered_df, id_vars=selected_demographic, 
                          value_vars=selected_spending_categories,
                          var_name='Spending Category', value_name='Total Spending')

    earning_df = pd.melt(filtered_df, id_vars=selected_demographic, 
                          value_vars=selected_earning_categories,
                          var_name='Earning Category', value_name='Total Earning')

    # Plot the bar chart for both spending and earning
    fig = px.bar(spending_df, x=selected_demographic, y='Total Spending', 
                 title='Total Spending by Category and Demographic Group', 
                 color_discrete_sequence=['blue'])

    earning_df[selected_demographic] = earning_df[selected_demographic].astype(str)  # Ensure proper grouping
    earning_df['Earning Category'] = 'Total Earning'
    fig.add_trace(px.bar(earning_df, x=selected_demographic, y='Total Earning', 
                         color_discrete_sequence=['orange']).data[0])

    fig.update_layout(barmode='group')
    
    return fig


# Define callback to update pie chart for spending percentage based on user inputs
@app.callback(
    Output('pie-chart', 'figure'),
    [Input('demographic-selector', 'value'),
     Input('demographic-options', 'value'),
     Input('spending-categories', 'value')]
)
def update_pie_chart(selected_demographic, selected_demographic_option, selected_categories):
    if not selected_demographic_option or not selected_categories:
        return px.pie(title='Select a demographic option and spending categories to display pie chart.')

    # Filter the dataframe based on selected demographic option
    filtered_df = df[df[selected_demographic] == selected_demographic_option]

    # Calculate the sum of values for each selected spending category
    spending_sums = filtered_df[selected_categories].sum()

    # Plot the pie chart
    fig = px.pie(values=spending_sums, names=spending_sums.index,
                 title=f'Spending Distribution for {selected_demographic_option}')

    return fig
# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
