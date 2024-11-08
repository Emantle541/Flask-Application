import requests
import datetime
import pygal
import lxml  

API_KEY = 'WFZIS351NY5T9JDF'

# Function to fetch and validate stock data
def get_stock_data(symbol, api_key):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={api_key}'
    
    try:
        response = requests.get(url)
        data = response.json()

        # Check if the API request was successful and the symbol is valid
        if 'Error Message' in data:
            return False, "Invalid stock symbol. Please try again."
        elif 'Note' in data:
            return False, "API limit reached. Please wait before trying again."
        elif 'Time Series (Daily)' not in data:
            return False, "Unexpected error. Please try again."
        else:
            return True, data  # Return the data itself when successful
    
    except requests.exceptions.RequestException as e:
        return False, f"Error fetching data: {str(e)}"

# Function to fetch and plot stock data  
def fetch_and_plot_stock_data(symbol, start_date, end_date, chart_type, api_key, time_series_choice):
    # Fetch stock data
    is_valid, data = get_stock_data(symbol, api_key)
    
    if not is_valid:
        print(f"Error: {data}")
        return
    
    # Extract time series data
    time_series_data = get_time_series(data, time_series_choice)
    
    # Filter data by date range
    filtered_data = {date: values for date, values in time_series_data.items() 
                     if start_date <= datetime.datetime.strptime(date, '%Y-%m-%d') <= end_date}
    
    if not filtered_data:
        print("No data available for the selected date range.")
        return
    
    # Prepare data for plotting
    dates = list(filtered_data.keys())
    open_prices = [float(data['1. open']) for data in filtered_data.values()]
    high_prices = [float(data['2. high']) for data in filtered_data.values()]
    low_prices = [float(data['3. low']) for data in filtered_data.values()]
    close_prices = [float(data['4. close']) for data in filtered_data.values()]
    
    # Create the chart using Pygal based on the selected chart type
    if chart_type == 'line':
        chart = pygal.Line(x_label_rotation=45) # Line chart
    elif chart_type == 'bar':
        chart = pygal.Bar(x_label_rotation=45) # Bar chart 

    # Set chart title and labels
    chart.title = f'{symbol} Stock Data from {start_date.strftime("%Y-%m-%d")} to {end_date.strftime("%Y-%m-%d")}'
    chart.x_labels = dates

    # Add each series to the chart (Open, High, Low, Close)
    chart.add('Open', open_prices)
    chart.add('High', high_prices)
    chart.add('Low', low_prices)
    chart.add('Close', close_prices)
    
    # Save chart as an SVG file
    chart.render_to_file(f'{symbol}_stock_data_chart.svg')
    
    # Open the chart in the web browser
    import webbrowser
    webbrowser.open(f'{symbol}_stock_data_chart.svg')


# Function to validate the selected chart type
def validate_chart_type(chart_type):
    valid_chart_types = ['line', 'bar']  # Supported chart types

    if chart_type not in valid_chart_types:
        return False, f"Invalid chart type. Available options are: {', '.join(valid_chart_types)}."
    else:
        return True, f"Chart type '{chart_type}' selected."
    
# Function to get the start date
def get_start_date():
    while(True):
        start_date = input("Enter start date (YYYY-MM-DD): ")
        try:
            parsed_date = start_date.split("-")
            date = datetime.datetime(int(parsed_date[0]), int(parsed_date[1]), int(parsed_date[2]))
            break
        except:
            print("Please only enter a valid date in YYYY-MM-DD format.")
        
    return date

# Function to get the end date
def get_end_date(start_date):
    while(True):
        end_date = input("Enter end date (YYYY-MM-DD): ")
        try:
            parsed_date = end_date.split("-")
            date = datetime.datetime(int(parsed_date[0]), int(parsed_date[1]), int(parsed_date[2]))
            if (date < start_date):
                print(f"Please enter an end date that occurs after the start date {start_date}.")
                continue
            break
        except:
            print("Please only enter a valid date in YYYY-MM-DD format.")

    return date

# Function to get the time series choice
def get_time_series_choice():
    while(True):
        print("\nSelect the time series of the chart you want to generate: \n---------------------------------------------\n")
        print("1. Intraday\n2. Daily\n3. Weekly\n4. Monthly\n")

        # Get input and convert to integer
        try:
            time_series = int(input("Enter time series option (1, 2, 3, 4): "))
            # Return the correct time series
            if time_series == 1:
                return 1
            elif time_series == 2:
                return 2
            elif time_series == 3:
                return 3
            elif time_series == 4:
                return 4
            else:
                print("Please only enter 1-4.")
                continue
        except:
            print("Please only enter 1-4.")
            continue

# Function to get time series data
def get_time_series(data, time_series):
    # Return the correct time series data
    if time_series == 1:
        time_series_data = data.get('Time Series (Intraday)', {})
        return time_series_data
    elif time_series == 2:
        time_series_data = data.get('Time Series (Daily)', {})
        return time_series_data
    elif time_series == 3:
        time_series_data = data.get('Time Series (Weekly)', {})
        return time_series_data
    elif time_series == 4:
        time_series_data = data.get('Time Series (Monthly)', {})
        return time_series_data
    

def main():
    # Step 1: Prompt for stock symbol and validate
    while True:
        symbol = input("Enter the stock symbol: ").upper()
        is_valid, message = get_stock_data(symbol, API_KEY)
        
        if is_valid:
            print("Stock symbol validated successfully!")
            break
        else:
            print(f"Error: {message}")

    # Step 2: Display available chart types
    print("\nAvailable chart types:")
    print("1. Line Chart (line)")
    print("2. Bar Chart (bar)")
    
    # Step 3: Prompt for chart type and validate
    while True:
        chart_type = input("Enter the chart type (line/bar): ").lower()
        is_valid, message = validate_chart_type(chart_type)
        
        if is_valid:
            print(message)
            break
        else:
            print(f"Error: {message}")

    #Step 4: Get the start date
    start_date = get_start_date()

    # Step 5: Get the end date
    end_date = get_end_date(start_date)

    # Step 6: Get time series function
    time_series_choice = get_time_series_choice()

    # Step 7: Call the new function to fetch and plot stock data
    fetch_and_plot_stock_data(symbol, start_date, end_date, chart_type, API_KEY, time_series_choice)

if __name__ == "__main__":
    main()
