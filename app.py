from flask import Flask, render_template, request, url_for
import requests
import pygal
from datetime import datetime
import os

app = Flask(__name__)
API_KEY = 'WFZIS351NY5T9JDF'

# Ensure charts directory exists
if not os.path.exists("static/charts"):
    os.makedirs("static/charts")

def get_stock_symbols(api_key=API_KEY):
    url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_key}'
    response = requests.get(url)
    symbols = []

    if response.status_code == 200:
        data = response.text.splitlines()
        for line in data[1:]:  
            parts = line.split(',')
            if len(parts) > 0:
                symbols.append(parts[0])  
    else:
        print("Error fetching stock symbols:", response.status_code)

    return symbols

# Function to fetch stock data from Alpha Vantage API
def get_stock_data(symbol, api_key):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    
    if 'Error Message' in data:
        return False, "Invalid stock symbol. Please try again."
    elif 'Note' in data:
        return False, "API limit reached. Please wait before trying again."
    elif 'Time Series (Daily)' not in data:
        return False, "Unexpected error. Please try again."
    else:
        return True, data  

# Function to filter and plot stock data
def fetch_and_plot_stock_data(symbol, start_date, end_date, chart_type, time_series_choice):
    # Fetch stock data
    is_valid, data = get_stock_data(symbol, API_KEY)
    if not is_valid:
        return None, data  

    # Extract time series data
    time_series_data = data.get('Time Series (Daily)', {})
    filtered_data = {date: values for date, values in time_series_data.items() 
                     if start_date <= datetime.strptime(date, '%Y-%m-%d') <= end_date}
    
    if not filtered_data:
        return None, "No data available for the selected date range."

    # Prepare data for plotting
    dates = list(filtered_data.keys())
    open_prices = [float(data['1. open']) for data in filtered_data.values()]
    high_prices = [float(data['2. high']) for data in filtered_data.values()]
    low_prices = [float(data['3. low']) for data in filtered_data.values()]
    close_prices = [float(data['4. close']) for data in filtered_data.values()]

    # Create the chart using Pygal
    if chart_type == 'line':
        chart = pygal.Line(x_label_rotation=45)
    elif chart_type == 'bar':
        chart = pygal.Bar(x_label_rotation=45)

    chart.title = f'{symbol} Stock Data from {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}'
    chart.x_labels = dates
    chart.add('Open', open_prices)
    chart.add('High', high_prices)
    chart.add('Low', low_prices)
    chart.add('Close', close_prices)

    chart_file = f'static/charts/{symbol}_stock_data_chart.svg'
    chart.render_to_file(chart_file)
    return chart_file, None 

@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    chart_file = None

    if request.method == "POST":
        symbol = request.form.get("symbol")
        chart_type = request.form.get("chart_type")
        start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d")
        end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d")
        time_series_choice = request.form.get("time_series_choice")

        chart_file, error = fetch_and_plot_stock_data(symbol, start_date, end_date, chart_type, time_series_choice)
    
    symbols = get_stock_symbols()
    return render_template("index.html", symbols=symbols, chart_file=chart_file, error=error)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

