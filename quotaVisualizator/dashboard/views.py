from django.shortcuts import render, redirect
import pandas as pd
import os
import plotly.express as px
import plotly.io as pio

# def service_view(request):
#     columns = []
#     selected_columns = []
#     selected_filter_column = ''
#     filter_value = ''
#     table_data = None
#     plot_div = None
#     csv_path =  'data.csv'

#     if os.path.exists(csv_path):
#         data = pd.read_csv(csv_path)
#         columns = list(data.columns)

#     if request.method == 'POST':
#         selected_columns = request.POST.getlist('columns')
#         selected_filter_column = request.POST.get('filter_column')
#         filter_value = request.POST.get('filter_value')
#         request.session['selected_columns'] = selected_columns
#         request.session['selected_filter_column'] = selected_filter_column
#         request.session['filter_value'] = filter_value
#         return redirect('dashboard:loading')

#     selected_columns = request.session.get('selected_columns', [])
#     selected_filter_column = request.session.get('selected_filter_column', '')
#     filter_value = request.session.get('filter_value', '')

#     if selected_columns:
#         try:
#             if selected_filter_column and filter_value:
#                 data = data[data[selected_filter_column] == filter_value]
#             table_data = data[selected_columns].to_dict(orient='records')
#             if 'id' in data.columns and 'age' in data.columns:
#                 fig = px.scatter(data, x='id', y='age', title='id vs age', width=800, height=600)
#                 plot_div = pio.to_html(fig, full_html=False)
#         except KeyError:
#             table_data = "Error: One or more columns do not exist in the data."

#     return render(request, 'dashboard/service.html', {
#         'table_data': table_data,
#         'columns': columns,
#         'selected_columns': selected_columns,
#         'selected_filter_column': selected_filter_column,
#         'filter_value': filter_value,
#         'plot_div': plot_div
#     })



def service_view(request):
    columns = []
    selected_columns = []
    selected_filter_column = ''
    filter_value = ''
    table_data = None
    plot_div = None
    csv_path = 'data.csv'

    if os.path.exists(csv_path):
        data = pd.read_csv(csv_path)
        columns = list(data.columns)

    if request.method == 'POST':
        selected_columns = request.POST.getlist('columns')
        selected_filter_column = request.POST.get('filter_column')
        filter_value = str(request.POST.get('filter_value'))

        log(filter_value)
        log(type(filter_value))
        
        request.session['selected_columns'] = selected_columns
        request.session['selected_filter_column'] = selected_filter_column
        request.session['filter_value'] = filter_value
        
        return redirect('dashboard:loading')

    selected_columns = request.session.get('selected_columns', [])
    selected_filter_column = request.session.get('selected_filter_column', '')
    filter_value = request.session.get('filter_value', '')

    if selected_columns:
        try:
            if selected_filter_column and filter_value!="":
                log('Filter')
                # set all data columns to str
                data = data.astype(str)
                
                data = data[data[selected_filter_column] == filter_value]
            table_data = data[selected_columns].to_dict(orient='records')
            if 'id' in data.columns and 'age' in data.columns:
                fig = px.scatter(data, x='id', y='age', title='id vs age', width=800, height=600)
                plot_div = pio.to_html(fig, full_html=False)
        except KeyError:
            table_data = "Error: One or more columns do not exist in the data."

    return render(request, 'dashboard/service.html', {
        'table_data': table_data,
        'columns': columns,
        'selected_columns': selected_columns,
        'selected_filter_column': selected_filter_column,
        'filter_value': filter_value,
        'plot_div': plot_div
    })

def loading_view(request):
    # Simulate processing delay for demonstration
    import time
    time.sleep(2)  # Simulate delay for processing
    
    return redirect('dashboard:service')

def log(text):
    with open('log_.txt', 'a') as f:
        f.write(str(text) + '\n')

# def loading_view(request):
#     csv_path = os.path.join(os.path.dirname(__file__), 'data.csv')
#     data_loaded = False

#     if os.path.exists(csv_path):
#         data = pd.read_csv(csv_path)
#         data_loaded = True
#         request.session['data_loaded'] = True

#     return render(request, 'dashboard/loading.html', {
#         'data_loaded': data_loaded
#     })


def home_view(request):
    csv_path =  'data.csv'
    data_loaded = False

    if os.path.exists(csv_path):
        data = pd.read_csv(csv_path)
        data_loaded = True

    return render(request, 'dashboard/home.html', {
        'data_loaded': data_loaded
    })
