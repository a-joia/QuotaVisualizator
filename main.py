import dash
from dash import dcc, html, Input, Output, State
import dash_table
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import base64
import io

# Initialize the Dash app
app = dash.Dash(__name__)

# Normalize the RequestCreationTimeStamp and calculate the accumulated difference
def normalize_dates_and_calculate_accumulation(df):
    df = df.copy()
    df['RequestCreationTimeStamp'] = pd.to_datetime(df['RequestCreationTimeStamp'])
    df['DaysFromLatest'] = df.groupby('SubscriptionId')['RequestCreationTimeStamp'].transform(lambda x: (x.max() - x).dt.days)
    df['QuotaDifference'] = df['NewQuota'] - df['CurrentQuota']
    df['AccumulatedQuotaDifference'] = df.groupby('SubscriptionId')['QuotaDifference'].cumsum()
    df['NormalizedDate'] = df.groupby('SubscriptionId')['RequestCreationTimeStamp'].transform(lambda x: (x - x.min()).dt.days)
    return df

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    if 'csv' in filename:
        # Assume that the user uploaded a CSV file
        return pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    elif 'json' in filename:
        # Assume that the user uploaded a JSON file
        return json.loads(decoded.decode('utf-8'))

# App layout
app.layout = html.Div([
    html.Div([
        html.H2("Upload Files", style={'textAlign': 'center', 'color': '#4A90E2'}),
        html.Div([
            dcc.Upload(
                id='upload-subscriptions',
                children=html.Div(['Drag and Drop or ', html.A('Select subscriptions.csv')]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px',
                    'backgroundColor': '#f9f9f9',
                    'cursor': 'pointer'
                },
                multiple=False
            ),
            html.Div(id='subscriptions-upload-status', style={'margin-bottom': '20px', 'textAlign': 'center', 'color': 'green'}),
        ], style={'margin': '20px'}),
        html.Div([
            dcc.Upload(
                id='upload-similarities',
                children=html.Div(['Drag and Drop or ', html.A('Select similarities.json')]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px',
                    'backgroundColor': '#f9f9f9',
                    'cursor': 'pointer'
                },
                multiple=False
            ),
            html.Div(id='similarities-upload-status', style={'margin-bottom': '20px', 'textAlign': 'center', 'color': 'green'}),
        ], style={'margin': '20px'}),
    ], style={'margin': '50px auto', 'width': '60%', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0px 0px 10px 0px rgba(0,0,0,0.1)', 'backgroundColor': '#fff'}),
    html.Div([
        html.H3("Select Subscription and Comparisons", style={'textAlign': 'center', 'color': '#4A90E2'}),
        dcc.Dropdown(
            id='subscription-dropdown',
            placeholder="Select a Subscription ID",
            style={'margin-bottom': '20px'}
        ),
        dcc.Dropdown(
            id='comparison-dropdown',
            multi=True,
            placeholder="Select Subscriptions to Compare",
            style={'margin-bottom': '20px'}
        ),
        html.Div(id='similarity-info', style={'textAlign': 'center', 'margin': '20px', 'color': '#4A90E2'}),
    ], style={'margin': '50px auto', 'width': '60%', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0px 0px 10px 0px rgba(0,0,0,0.1)', 'backgroundColor': '#fff'}),
    html.Div([
        html.H3("Selected Subscription Data", style={'textAlign': 'center', 'color': '#4A90E2'}),
        dash_table.DataTable(id='main-datatable', style_table={'margin': '20px auto', 'width': '90%'}),
    ], style={'margin': '50px auto', 'width': '80%', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0px 0px 10px 0px rgba(0,0,0,0.1)', 'backgroundColor': '#fff'}),
    html.Div([
        html.H3("Comparison Subscriptions Data", style={'textAlign': 'center', 'color': '#4A90E2'}),
        dash_table.DataTable(id='comparison-datatable', style_table={'margin': '20px auto', 'width': '90%'}),
    ], style={'margin': '50px auto', 'width': '80%', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0px 0px 10px 0px rgba(0,0,0,0.1)', 'backgroundColor': '#fff'}),
    html.Div([
        dcc.Graph(id='aggregated-bar-plot', style={'margin': '20px auto', 'width': '90%'}),
        dcc.Graph(id='normalized-accumulated-quota-plot', style={'margin': '20px auto', 'width': '90%'}),
    ], style={'margin': '50px auto', 'width': '90%', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0px 0px 10px 0px rgba(0,0,0,0.1)', 'backgroundColor': '#fff'}),
    html.Div(id='extra-info', style={'margin': '50px auto', 'width': '60%', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0px 0px 10px 0px rgba(0,0,0,0.1)', 'backgroundColor': '#fff'}),
    html.Div(id='column-aggregator-info', style={'margin': '50px auto', 'width': '60%', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0px 0px 10px 0px rgba(0,0,0,0.1)', 'backgroundColor': '#fff'}),
    html.Div(id='additional-info', style={'margin': '50px auto', 'width': '60%', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0px 0px 10px 0px rgba(0,0,0,0.1)', 'backgroundColor': '#fff'})
], style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#f4f4f9', 'padding': '20px'})

@app.callback(
    [Output('subscription-dropdown', 'options'),
     Output('subscriptions-upload-status', 'children'),
     Output('similarities-upload-status', 'children')],
    [Input('upload-subscriptions', 'contents'),
     Input('upload-similarities', 'contents')],
    [State('upload-subscriptions', 'filename'),
     State('upload-similarities', 'filename')]
)
def update_dropdowns(subscriptions_contents, similarities_contents, subscriptions_filename, similarities_filename):
    subscription_status = ""
    similarity_status = ""
    options = []

    if subscriptions_contents:
        df = parse_contents(subscriptions_contents, subscriptions_filename)
        num_records = len(df)
        subscription_status = f"File '{subscriptions_filename}' uploaded successfully. {num_records} records found."

    if similarities_contents:
        similarity_data = parse_contents(similarities_contents, similarities_filename)
        num_subscriptions = len(similarity_data)
        similarity_status = f"File '{similarities_filename}' uploaded successfully. {num_subscriptions} subscriptions found."
        options = [{'label': sub_id, 'value': sub_id} for sub_id in similarity_data.keys()]

    return options, subscription_status, similarity_status

@app.callback(
    [Output('comparison-dropdown', 'options'),
     Output('comparison-dropdown', 'value')],
    Input('subscription-dropdown', 'value'),
    State('upload-similarities', 'contents'),
    State('upload-similarities', 'filename')
)
def set_comparison_options(selected_subscription, similarities_contents, similarities_filename):
    if similarities_contents:
        similarity_data = parse_contents(similarities_contents, similarities_filename)
        if selected_subscription:
            options = [
                {'label': f"{sub_id} (Similarity: {similarity_data[selected_subscription]['Similarity'][idx]})", 'value': sub_id}
                for idx, sub_id in enumerate(similarity_data[selected_subscription]['SimilarSubscriptions'])
            ]
            return options, []
    return [], []

@app.callback(
    [Output('similarity-info', 'children'),
     Output('aggregated-bar-plot', 'figure'),
     Output('normalized-accumulated-quota-plot', 'figure'),
     Output('main-datatable', 'data'),
     Output('main-datatable', 'columns'),
     Output('comparison-datatable', 'data'),
     Output('comparison-datatable', 'columns'),
     Output('extra-info', 'children'),
     Output('column-aggregator-info', 'children'),
     Output('additional-info', 'children')],
    [Input('subscription-dropdown', 'value'),
     Input('comparison-dropdown', 'value')],
    [State('upload-subscriptions', 'contents'),
     State('upload-subscriptions', 'filename'),
     State('upload-similarities', 'contents'),
     State('upload-similarities', 'filename')]
)
def update_outputs(selected_subscription, comparison_subscriptions, subscriptions_contents, subscriptions_filename, similarities_contents, similarities_filename):
    if selected_subscription and subscriptions_contents and similarities_contents:
        df = parse_contents(subscriptions_contents, subscriptions_filename)
        df_normalized = normalize_dates_and_calculate_accumulation(df)
        similarity_data = parse_contents(similarities_contents, similarities_filename)

        # Ensure the key is a string
        selected_subscription = str(selected_subscription)

        # Filter main DataFrame
        main_df = df[df['SubscriptionId'] == int(selected_subscription)]
        main_df_normalized = df_normalized[df_normalized['SubscriptionId'] == int(selected_subscription)]

        # Prepare main DataTable
        main_data = main_df.to_dict('records')
        main_columns = [{"name": i, "id": i} for i in main_df.columns]

        # Prepare ExtraInfo for the selected subscription
        extra_info = html.Div([
            html.H4(f"Extra Information for {selected_subscription}", style={'textAlign': 'center', 'color': '#4A90E2'}),
            html.Ul([html.Li(str(info)) for info in similarity_data[selected_subscription]['ExtraInfo']])
        ], style={'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9', 'marginBottom': '20px'})

        # Filter and plot comparison DataFrame
        similarity_text = ""
        column_aggregator_info = []
        additional_info = []
        if comparison_subscriptions:
            comparison_df = df[df['SubscriptionId'].isin([int(sub_id) for sub_id in comparison_subscriptions])]
            comparison_df_normalized = df_normalized[df_normalized['SubscriptionId'].isin([int(sub_id) for sub_id in comparison_subscriptions])]

            # Prepare comparison DataTable
            comparison_data = comparison_df.to_dict('records')
            comparison_columns = [{"name": i, "id": i} for i in comparison_df.columns]

            similarities = [
                f"{sub_id}: {similarity_data[selected_subscription]['Similarity'][similarity_data[selected_subscription]['SimilarSubscriptions'].index(sub_id)]}"
                for sub_id in comparison_subscriptions
            ]
            similarity_text = "Similarities: " + ", ".join(similarities)

            for sub_id in comparison_subscriptions:
                idx = similarity_data[selected_subscription]['SimilarSubscriptions'].index(sub_id)
                column_aggregator_info.append(
                    html.Div([
                        html.H4(f"Column Aggregator for {sub_id}", style={'textAlign': 'center', 'color': '#4A90E2'}),
                        html.Ul([html.Li(str(aggregator)) for aggregator in similarity_data[selected_subscription]['ColumnAggregator'][idx]])
                    ], style={'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9', 'marginBottom': '20px'})
                )
                additional_info.append(
                    html.Div([
                        html.H4(f"Additional Information for {sub_id}", style={'textAlign': 'center', 'color': '#4A90E2'}),
                        html.Ul([html.Li(str(info)) for info in similarity_data[selected_subscription]['AdditionalInformation'][idx]])
                    ], style={'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'backgroundColor': '#f9f9f9', 'marginBottom': '20px'})
                )

            # Create the aggregated bar plot
            df_aggregated = df.groupby(['SubscriptionId', 'Region']).agg({
                'NewQuota': 'sum',
                'CurrentQuota': 'sum'
            }).reset_index()
            df_aggregated['QuotaDifference'] = df_aggregated['NewQuota'] - df_aggregated['CurrentQuota']
            aggregated_bar_df = df_aggregated[df_aggregated['SubscriptionId'].isin([int(selected_subscription)] + [int(sub_id) for sub_id in comparison_subscriptions])]
            
            # Create bar traces for each region
            bar_traces = []
            for region in aggregated_bar_df['Region'].unique():
                region_data = aggregated_bar_df[aggregated_bar_df['Region'] == region]
                bar_traces.append(go.Bar(
                    x=region_data['SubscriptionId'],
                    y=region_data['QuotaDifference'],
                    name=region,
                    hoverinfo='name+x+y',
                    marker=dict(line=dict(width=0.5))
                ))
            
            # Add vertical lines to separate each subscription
            vertical_lines = []
            subscription_ids = sorted(aggregated_bar_df['SubscriptionId'].unique())
            for i in range(len(subscription_ids) - 1):
                mid_point = (subscription_ids[i] + subscription_ids[i + 1]) / 2
                vertical_lines.append(go.layout.Shape(
                    type="line",
                    x0=mid_point,
                    x1=mid_point,
                    y0=0,
                    y1=1,
                    xref='x',
                    yref='paper',
                    line=dict(color="black", width=1)
                ))
            
            aggregated_bar_plot = go.Figure(data=bar_traces)
            aggregated_bar_plot.update_layout(
                title='Sum of (NewQuota - CurrentQuota) by Subscription and Region',
                xaxis=dict(
                    title='Subscription ID',
                    tickvals=subscription_ids,
                    ticktext=subscription_ids,
                    showgrid=True,
                    gridcolor='lightgrey'
                ),
                yaxis=dict(
                    title='Quota Difference',
                    showgrid=True,
                    gridcolor='lightgrey'
                ),
                plot_bgcolor='white',
                paper_bgcolor='white',
                shapes=vertical_lines,
                legend=dict(
                    title='Region',
                    orientation='v',
                    yanchor='top',
                    y=1,
                    xanchor='left',
                    x=1.02
                ),
                bargap=0.15
            )

            # Create the normalized accumulated quota plot
            normalized_accumulated_quota_plot_df = df_normalized[df_normalized['SubscriptionId'].isin([int(selected_subscription)] + [int(sub_id) for sub_id in comparison_subscriptions])]
            normalized_accumulated_quota_plot = px.line(normalized_accumulated_quota_plot_df, x='NormalizedDate', y='AccumulatedQuotaDifference', color='SubscriptionId', title='Accumulated Quota Difference by Normalized Request Creation Date')

        else:
            comparison_data = []
            comparison_columns = []

            # Create the aggregated bar plot for only the selected subscription
            df_aggregated = df.groupby(['SubscriptionId', 'Region']).agg({
                'NewQuota': 'sum',
                'CurrentQuota': 'sum'
            }).reset_index()
            df_aggregated['QuotaDifference'] = df_aggregated['NewQuota'] - df_aggregated['CurrentQuota']
            aggregated_bar_df = df_aggregated[df_aggregated['SubscriptionId'] == int(selected_subscription)]
            
            # Create bar traces for each region
            bar_traces = []
            for region in aggregated_bar_df['Region'].unique():
                region_data = aggregated_bar_df[aggregated_bar_df['Region'] == region]
                bar_traces.append(go.Bar(
                    x=region_data['SubscriptionId'],
                    y=region_data['QuotaDifference'],
                    name=region,
                    hoverinfo='name+x+y',
                    marker=dict(line=dict(width=0.5))
                ))
            
            # Add vertical lines to separate each subscription
            vertical_lines = []
            subscription_ids = sorted(aggregated_bar_df['SubscriptionId'].unique())
            for i in range(len(subscription_ids) - 1):
                mid_point = (subscription_ids[i] + subscription_ids[i + 1]) / 2
                vertical_lines.append(go.layout.Shape(
                    type="line",
                    x0=mid_point,
                    x1=mid_point,
                    y0=0,
                    y1=1,
                    xref='x',
                    yref='paper',
                    line=dict(color="black", width=1)
                ))
            
            aggregated_bar_plot = go.Figure(data=bar_traces)
            aggregated_bar_plot.update_layout(
                title='Sum of (NewQuota - CurrentQuota) by Subscription and Region',
                xaxis=dict(
                    title='Subscription ID',
                    tickvals=subscription_ids,
                    ticktext=subscription_ids,
                    showgrid=True,
                    gridcolor='lightgrey'
                ),
                yaxis=dict(
                    title='Quota Difference',
                    showgrid=True,
                    gridcolor='lightgrey'
                ),
                plot_bgcolor='white',
                paper_bgcolor='white',
                shapes=vertical_lines,
                legend=dict(
                    title='Region',
                    orientation='v',
                    yanchor='top',
                    y=1,
                    xanchor='left',
                    x=1.02
                ),
                bargap=0.15
            )

            # Create the normalized accumulated quota plot for only the selected subscription
            normalized_accumulated_quota_plot = px.line(main_df_normalized, x='NormalizedDate', y='AccumulatedQuotaDifference', title='Accumulated Quota Difference by Normalized Request Creation Date')

        return similarity_text, aggregated_bar_plot, normalized_accumulated_quota_plot, main_data, main_columns, comparison_data, comparison_columns, extra_info, column_aggregator_info, additional_info
    return "", {}, {}, [], [], [], [], "", "", ""

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
