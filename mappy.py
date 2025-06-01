import streamlit as st
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from datetime import datetime, timedelta
import os
from sklearn.preprocessing import MinMaxScaler
import altair as alt
import matplotlib.dates as mdates
import folium
from streamlit_folium import folium_static
import google.generativeai as genai
from matplotlib import gridspec
from matplotlib.patches import Arc

# Enhanced page configuration with blue theme
st.set_page_config(
    page_title="🌊 Ganga Water Quality Monitor",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful blue theme
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-blue: #1e3a8a;
        --secondary-blue: #3b82f6;
        --light-blue: #dbeafe;
        --accent-blue: #0ea5e9;
        --dark-blue: #1e40af;
        --gradient-blue: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Custom header styling */
    .main-header {
        background: var(--gradient-blue);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 8px 32px rgba(30, 58, 138, 0.3);
    }
    
    .main-header h1 {
        font-size: 3rem;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Metric cards styling */
    .metric-card {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid var(--secondary-blue);
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.1);
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.2);
    }
    
    /* Weather card styling */
    .weather-card {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(30, 64, 175, 0.3);
        margin-bottom: 2rem;
    }
    
    .weather-card h3 {
        margin-bottom: 1rem;
        font-size: 1.5rem;
    }
    
    .weather-info {
        display: flex;
        justify-content: space-around;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .weather-item {
        text-align: center;
    }
    
    .weather-value {
        font-size: 2rem;
        font-weight: bold;
        display: block;
    }
    
    .weather-label {
        font-size: 0.9rem;
        opacity: 0.8;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: var(--gradient-blue);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background-color: white;
        border: 2px solid var(--light-blue);
        border-radius: 8px;
    }
    
    /* Chart container */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    
    /* Status indicators */
    .status-low {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        text-align: center;
    }
    
    .status-moderate {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        text-align: center;
    }
    
    .status-high {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        text-align: center;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-left: 4px solid var(--secondary-blue);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Map container */
    .map-container {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* Loading animation */
    .loading {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    .spinner {
        border: 4px solid var(--light-blue);
        border-top: 4px solid var(--secondary-blue);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .weather-info {
            flex-direction: column;
        }
        
        .metric-card {
            margin-bottom: 0.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Configuration
GOOGLE_MAPS_API_KEY = 'AIzaSyCAEXog7qWBnXnwlO6wT844mhgaeVAkP00'
LOCATIONS = {
    'ALAKNANDA A/C WITH BHAGIRATHI AT DEVPRAYAG': {
        'file_path': r"Devprayag.csv",
        'lat': 30.140504, 'lon': 78.597358
    },
    'MANDAKINI B/C ALKALNADA AT RUDRAPRAYAG': {
        'file_path': r"Rudraprayag.csv",
        'lat': 30.290028, 'lon': 78.979932
    },
    'GANGA AT HARIDWAR D/S, UPPER GANGA CANAL D/S BALKUMARI MANDIR, AJEETPUR, HARIDWAR ': {
        'file_path': r"Haridwar.csv",
        'lat': 29.945254, 'lon': 78.164675
    },
    'GANGA AT KANNAUJ U/S (RAJGHAT), U.P': {
        'file_path': r"Kannauj.csv",
        'lat': 27.010953, 'lon': 79.986442
    },
    'GANGA AT BITHOOR (KANPUR), U.P.': {
        'file_path': r"Kanpur.csv",
        'lat': 26.610906, 'lon': 80.275419
    },
    'GANGA AT ALLAHABAD D/S (SANGAM), U.P': {
        'file_path': r"Prayagraj.csv",
        'lat': 25.419206, 'lon': 81.900522
    },
    'GANGA AT VARANASI D/S (MALVIYA BRIDGE), U.P ': {
        'file_path': r"Ganga at Varanasi.csv",
        'lat': 25.321486, 'lon': 83.035285
    },
    'GANGA AT TRIGHAT (GHAZIPUR), U.P': {
        'file_path': r"Ganga at ghazipur.csv",
        'lat': 25.578175, 'lon': 83.609594
    },
    'GANGA AT GULABI GHAT, PATNA': {
        'file_path': r"Ganga at Gulabi Ghat.csv",
        'lat': 25.620356, 'lon': 85.179995
    },
    'GANGA AT U/S BHAGALPUR NEAR BARARIGHAT': {
        'file_path': r"Ganga at Bhagalpur.csv",
        'lat': 25.271603, 'lon': 87.025665
    },
    'KOLKATA, WEST BENGAL ': {
        'file_path': r"Ganga at Dakshineshwar.csv",
        'lat': 22.632682, 'lon': 88.355369
    },
    'KOLKATA, WEST BENGAL ': {
        'file_path': r"Ganga at Howrah.csv",
        'lat': 22.586540, 'lon': 88.346611
    }
}

WEATHER_API_KEY = '5f25b8309c72e6259b8b47115ea3f47c'
GEMINI_API_KEY = 'AIzaSyDdksXKVQ8MI46k-KdBMivvW34Ln9jggfI'
genai.configure(api_key=GEMINI_API_KEY)

def create_satellite_map(latitude, longitude):
    """Create a Folium map with satellite view for a given location"""
    m = folium.Map(
        location=[latitude, longitude],
        zoom_start=13,
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}&hl=en',
        attr='Google Satellite'
    )
    
    folium.Marker(
        [latitude, longitude],
        popup='Monitoring Location',
        icon=folium.Icon(color='blue', icon='tint', prefix='fa')
    ).add_to(m)
    
    return m

def parse_date(date_str):
    """Flexible date parsing function to handle different date formats"""
    date_formats = [
        '%d-%m-%Y', '%m-%d-%Y', '%Y-%m-%d',
        '%d/%m/%Y', '%m/%d/%Y'
    ]
    for fmt in date_formats:
        try:
            return pd.to_datetime(date_str, format=fmt)
        except:
            continue
    raise ValueError(f"Unable to parse date: {date_str}")

def prepare_input_data(historical_data, weather_forecast, parameter):
    """Prepare input data for model prediction with fixed sequence length"""
    historical_data['Date'] = historical_data['Date'].apply(parse_date)
    historical_data = historical_data.dropna(subset=['Date'])
    historical_data.set_index('Date', inplace=True)
    
    last_10_days = historical_data[parameter].tail(10)
    
    if len(weather_forecast) < 5:
        while len(weather_forecast) < 5:
            last_forecast = weather_forecast[-1]
            weather_forecast.append({
                'date': last_forecast['date'] + timedelta(days=1),
                'temperature': last_forecast['temperature'],
                'rainfall': last_forecast['rainfall']
            })
    elif len(weather_forecast) > 5:
        weather_forecast = weather_forecast[:5]
    
    temps = [w['temperature'] for w in weather_forecast]
    rainfalls = [w['rainfall'] for w in weather_forecast]
    
    param_scaler = MinMaxScaler()
    scaled_data = param_scaler.fit_transform(last_10_days.values.reshape(-1, 1))
    
    temp_scaler = MinMaxScaler()
    rainfall_scaler = MinMaxScaler()
    scaled_temps = temp_scaler.fit_transform(np.array(temps).reshape(-1, 1))
    scaled_rainfalls = rainfall_scaler.fit_transform(np.array(rainfalls).reshape(-1, 1))
    
    scaled_exogenous = np.column_stack([scaled_temps.flatten(), scaled_rainfalls.flatten()])
    
    X = scaled_data.reshape(1, 10, 1)
    X_exo = scaled_exogenous.reshape(1, 5, 2)
    
    return X, X_exo, param_scaler, last_10_days, temp_scaler, rainfall_scaler

def fetch_weather_forecast(location, start_date):
    """Fetch weather forecast for a given location"""
    location_coords = {
        'ALAKNANDA A/C WITH BHAGIRATHI AT DEVPRAYAG': {'lat': 30.140504,'lon': 78.597358},
        'MANDAKINI B/C ALKALNADA AT RUDRAPRAYAG': {'lat': 30.290028, 'lon': 78.979932},
        'GANGA AT HARIDWAR D/S, UPPER GANGA CANAL D/S BALKUMARI MANDIR, AJEETPUR, HARIDWAR': {'lat': 29.945254,'lon': 78.164675},
        'GANGA AT KANNAUJ U/S (RAJGHAT), U.P':{'lat': 27.010953,'lon': 79.986442},
        'GANGA AT BITHOOR (KANPUR), U.P.':{'lat': 26.610906,'lon': 80.275419},
        'GANGA AT ALLAHABAD D/S (SANGAM), U.P':{'lat': 25.419206,'lon': 81.900522},
        'GANGA AT VARANASI D/S (MALVIYA BRIDGE), U.P':{'lat': 25.321486,'lon': 83.035285},
        'GANGA AT TRIGHAT (GHAZIPUR), U.P':{'lat': 25.578175,'lon': 83.609594},
        'GANGA AT GULABI GHAT, PATNA':{'lat': 25.620356,'lon': 85.179995},
        'GANGA AT U/S BHAGALPUR NEAR BARARIGHAT':{'lat': 25.271603,'lon': 87.025665},
        'KOLKATA, WEST BENGAL':{'lat': 22.5726,'lon': 88.3639}
    }
    
    try:
        coords = location_coords[location]
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={coords['lat']}&lon={coords['lon']}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        
        forecasts_by_date = {}
        for forecast in data['list']:
            forecast_date = datetime.fromtimestamp(forecast['dt']).date()
            if forecast_date >= start_date.date():
                temp = forecast['main']['temp']
                rainfall = forecast.get('rain', {}).get('3h', 0) or 0
                
                if forecast_date not in forecasts_by_date:
                    forecasts_by_date[forecast_date] = {
                        'date': datetime.combine(forecast_date, datetime.min.time()),
                        'temperature': temp,
                        'rainfall': rainfall
                    }
                else:
                    forecasts_by_date[forecast_date]['temperature'] = max(forecasts_by_date[forecast_date]['temperature'], temp)
                    forecasts_by_date[forecast_date]['rainfall'] += rainfall
        
        forecasts = list(forecasts_by_date.values())
        
        while len(forecasts) < 5:
            last_forecast = forecasts[-1]
            forecasts.append({
                'date': last_forecast['date'] + timedelta(days=1),
                'temperature': last_forecast['temperature'],
                'rainfall': last_forecast['rainfall']
            })
        
        return forecasts[:5]
    
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        dummy_forecasts = [
            {
                'date': start_date + timedelta(days=i+1),
                'temperature': 25.0,
                'rainfall': 0.0
            } for i in range(5)
        ]
        return dummy_forecasts

def create_altair_forecast_plot(historical_data, forecast_data, parameter):
    """Create an Altair plot showing historical and forecasted data"""
    if not isinstance(historical_data.index, pd.DatetimeIndex):
        historical_data.index = pd.to_datetime(historical_data.index)
    
    historical_df = pd.DataFrame({
        'Date': historical_data.index,
        'Value': historical_data.values,
        'Type': 'Historical'
    })
    
    forecast_dates = [historical_data.index[-1] + timedelta(days=i+1) for i in range(len(forecast_data))]
    forecast_df = pd.DataFrame({
        'Date': forecast_dates,
        'Value': forecast_data,
        'Type': 'Forecast'
    })
    
    combined_df = pd.concat([historical_df, forecast_df])
    
    chart = alt.Chart(combined_df).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('Value:Q', title=parameter),
        color=alt.Color('Type:N', 
                       scale=alt.Scale(domain=['Historical', 'Forecast'], 
                                     range=['#3b82f6', '#ef4444']),
                       legend=alt.Legend(title='Data Type')),
        tooltip=['Date:T', 'Value:Q', 'Type:N']
    ).properties(
        title=f'{parameter} - Historical and Forecast',
        width=700,
        height=400
    ).interactive()
    
    return chart

def load_model_for_parameter(parameter):
    """Load the pre-trained model for a specific water quality parameter"""
    parameter_model_paths = {
        "Biochemical Oxygen Demand": r"models\Biochemical_Oxygen_Demand_water_quality_lstm_model.keras",
        "Dissolved Oxygen": r"models\Dissolved_Oxygen_water_quality_lstm_model.keras",
        "pH": r"models\pH_water_quality_lstm_model.keras",
        "Turbidity": r"models\Turbidity_water_quality_lstm_model.keras",
        "Nitrate": r"models\Nitrate_water_quality_lstm_model.keras",
        "Fecal Coliform": r"models\Fecal_Coliform_water_quality_lstm_model.keras",
        "Fecal Streptococci": r"models\Fecal_Streptococci_water_quality_lstm_model.keras",
        "Total Coliform": r"models\Total_Coliform_water_quality_lstm_model.keras",
        "Conductivity": r"models\Conductivity_water_quality_lstm_model.keras"
    }
    
    model_path = parameter_model_paths.get(parameter)
    if model_path and os.path.exists(model_path):
        return load_model(model_path)
    else:
        st.error(f"Model for {parameter} not found.")
        return None

def create_altair_historical_plot(df, parameter):
    """Create an Altair plot of historical data"""
    chart = alt.Chart(df).mark_line(strokeWidth=3, color='#3b82f6').encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y(f'{parameter}:Q', title=parameter),
        tooltip=['Date:T', f'{parameter}:Q']
    ).properties(
        title=f'Historical {parameter} Data',
        width=700,
        height=400
    ).interactive()
    
    return chart

def generate_gemini_water_quality_report(parameter, forecasted_values, forecast_dates, historical_data):
    """Generate a detailed water quality report using Gemini API"""
    historical_stats = f"""
    Historical Data Statistics for {parameter}:
    - Mean: {historical_data[parameter].mean():.4f}
    - Standard Deviation: {historical_data[parameter].std():.4f}
    - Minimum: {historical_data[parameter].min():.4f}
    - Maximum: {historical_data[parameter].max():.4f}
    """
    
    forecast_details = "\n".join([
        f"Date: {date.strftime('%Y-%m-%d')}, Predicted Value: {value:.4f}"
        for date, value in zip(forecast_dates, forecasted_values)
    ])
    
    prompt = f"""
    Provide a comprehensive water quality report for {parameter} with the following details:
    
    {historical_stats}
    
    Forecasted Values:
    {forecast_details}
    
    For each forecast date, please analyze:
    1. Potential water quality implications
    2. Risk assessment
    3. Recommended actions
    4. Ecological impact
    5. Potential sources of variation
    
    Format the report with clear headings and provide actionable insights.
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating report: {str(e)}"

def get_status_details(value, parameter_data, selected_parameter):
    """Determine status based on actual parameter thresholds"""
    mean = parameter_data[selected_parameter].mean()
    std = parameter_data[selected_parameter].std()
    
    if value < mean - std:
        return "Low Risk", "green", 30
    elif mean - std <= value < mean + std:
        return "Moderate Risk", "orange", 60
    else:
        return "High Risk", "red", 90

def make_donut(input_response, input_text, parameter, parameter_data, selected_parameter):
    """Create an Altair donut chart for water quality forecast visualization"""
    status, risk_color, risk_percentage = get_status_details(
        input_response, parameter_data, selected_parameter
    )
    
    color_map = {
        'Low Risk': ['#10b981', '#059669'],
        'Moderate Risk': ['#f59e0b', '#d97706'],
        'High Risk': ['#ef4444', '#dc2626']
    }
    
    chart_color = color_map.get(status, color_map['Moderate Risk'])
    
    source = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100 - risk_percentage, risk_percentage]
    })
    
    source_bg = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100, 0]
    })
    
    plot = alt.Chart(source).mark_arc(
        innerRadius=45,
        cornerRadius=25
    ).encode(
        theta="% value",
        color=alt.Color(
            "Topic:N",
            scale=alt.Scale(
                domain=[input_text, ''],
                range=chart_color
            ),
            legend=None
        )
    ).properties(width=130, height=130)
    
    text = alt.Chart(source).mark_text(
        align='center',
        color=chart_color[0],
        font="Arial",
        fontSize=16,
        fontWeight='bold'
    ).encode(
        text=alt.value(f'{input_response:.2f}')
    ).properties(width=130, height=130)
    
    plot_bg = alt.Chart(source_bg).mark_arc(
        innerRadius=45,
        cornerRadius=20
    ).encode(
        theta="% value",
        color=alt.Color(
            "Topic:N",
            scale=alt.Scale(
                domain=[input_text, ''],
                range=chart_color
            ),
            legend=None
        )
    ).properties(width=130, height=130)
    
    return plot_bg + plot + text

def create_aesthetic_weather_kpi(selected_location, last_date):
    """Create an aesthetic weather KPI card"""
    current_time = datetime.now()
    if current_time.hour < 12:
        greeting = "Good Morning"
    elif 12 <= current_time.hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    try:
        weather_forecast = fetch_weather_forecast(selected_location, last_date)
        current_forecast = weather_forecast[0]
        temperature = current_forecast['temperature']
        rainfall = current_forecast.get('rainfall', 0)
        
        st.markdown(f"""
        <div class="weather-card">
            <h3>🌤️ {greeting}! Weather Outlook</h3>
            <div class="weather-info">
                <div class="weather-item">
                    <span class="weather-value">{temperature:.1f}°C</span>
                    <span class="weather-label">Temperature</span>
                </div>
                <div class="weather-item">
                    <span class="weather-value">{rainfall:.1f}mm</span>
                    <span class="weather-label">Rainfall</span>
                </div>
                <div class="weather-item">
                    <span class="weather-value">📍</span>
                    <span class="weather-label">{selected_location.split(' AT ')[1] if ' AT ' in selected_location else selected_location}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Unable to fetch weather data: {e}")

# Main Streamlit App
def main():
    # Custom header
    st.markdown("""
    <div class="main-header">
        <h1>🌊 Ganga Water Quality Monitor</h1>
        <p>Advanced AI-Powered Water Quality Prediction & Analysis System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### 🎛️ **Configuration Panel**")
        st.markdown("---")
        
        # Location selection
        st.markdown("#### 📍 **Select Monitoring Location**")
        selected_location = st.selectbox(
            "Choose a location:",
            list(LOCATIONS.keys()),
            help="Select the Ganga monitoring station for analysis"
        )
        
        st.markdown("#### 🧪 **Select Water Quality Parameter**")
        parameters = [
            "Biochemical Oxygen Demand", "Dissolved Oxygen", "pH", "Turbidity",
            "Nitrate", "Fecal Coliform", "Fecal Streptococci", "Total Coliform", "Conductivity"
        ]
        selected_parameter = st.selectbox(
            "Choose parameter:",
            parameters,
            help="Select the water quality parameter to analyze and predict"
        )
        
        st.markdown("#### 📊 **Analysis Options**")
        show_historical = st.checkbox("📈 Show Historical Data", value=True)
        show_forecast = st.checkbox("🔮 Generate Forecast", value=True)
        show_map = st.checkbox("🗺️ Show Location Map", value=True)
        show_ai_report = st.checkbox("🤖 Generate AI Report", value=False)
        
        st.markdown("---")
        st.markdown("### 📋 **Quick Info**")
        st.info(f"**Location:** {selected_location.split(' AT ')[1] if ' AT ' in selected_location else selected_location}")
        st.info(f"**Parameter:** {selected_parameter}")
    
    # Main content area
    try:
        # Load data
        location_info = LOCATIONS[selected_location]
        file_path = location_info['file_path']
        
        if not os.path.exists(file_path):
            st.error(f"Data file not found: {file_path}")
            return
        
        with st.spinner("🔄 Loading data..."):
            df = pd.read_csv(file_path)
        
        if selected_parameter not in df.columns:
            st.error(f"Parameter '{selected_parameter}' not found in the dataset.")
            return
        
        # Data preprocessing
        df['Date'] = df['Date'].apply(parse_date)
        df = df.dropna(subset=['Date', selected_parameter])
        df = df.sort_values('Date')
        
        # Get the last date for weather forecast
        last_date = df['Date'].max()
        
        # Weather KPI
        create_aesthetic_weather_kpi(selected_location, last_date)
        
        # Main content columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if show_historical:
                st.markdown("## 📈 **Historical Data Analysis**")
                with st.container():
                    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                    
                    # Display recent statistics
                    recent_data = df.tail(30)
                    col_a, col_b, col_c, col_d = st.columns(4)
                    
                    with col_a:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>📊 Current Value</h4>
                            <h2 style="color: #3b82f6;">{df[selected_parameter].iloc[-1]:.2f}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_b:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>📈 30-Day Average</h4>
                            <h2 style="color: #10b981;">{recent_data[selected_parameter].mean():.2f}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_c:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>📉 Minimum</h4>
                            <h2 style="color: #f59e0b;">{recent_data[selected_parameter].min():.2f}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_d:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>📊 Maximum</h4>
                            <h2 style="color: #ef4444;">{recent_data[selected_parameter].max():.2f}</h2>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Historical chart
                    historical_chart = create_altair_historical_plot(df, selected_parameter)
                    st.altair_chart(historical_chart, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            if show_map:
                st.markdown("## 🗺️ **Location Map**")
                with st.container():
                    st.markdown('<div class="map-container">', unsafe_allow_html=True)
                    satellite_map = create_satellite_map(location_info['lat'], location_info['lon'])
                    folium_static(satellite_map, width=350, height=300)
                    st.markdown('</div>', unsafe_allow_html=True)
        
        # Forecast section
        if show_forecast:
            st.markdown("## 🔮 **AI-Powered Forecast**")
            
            with st.spinner("🤖 Generating predictions..."):
                # Load model
                model = load_model_for_parameter(selected_parameter)
                if model is None:
                    st.error("Model not available for this parameter.")
                    return
                
                # Fetch weather forecast
                weather_forecast = fetch_weather_forecast(selected_location, last_date)
                
                # Prepare input data
                X, X_exo, param_scaler, last_10_days, temp_scaler, rainfall_scaler = prepare_input_data(
                    df.copy(), weather_forecast, selected_parameter
                )
                
                # Make predictions
                predictions_scaled = model.predict([X, X_exo])
                predictions = param_scaler.inverse_transform(predictions_scaled.reshape(-1, 1)).flatten()
                
                # Create forecast dates
                forecast_dates = [last_date + timedelta(days=i+1) for i in range(len(predictions))]
            
            # Display forecast results
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                forecast_chart = create_altair_forecast_plot(last_10_days, predictions, selected_parameter)
                st.altair_chart(forecast_chart, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown("### 📊 **Forecast Summary**")
                for i, (date, pred) in enumerate(zip(forecast_dates, predictions)):
                    status, _, _ = get_status_details(pred, df, selected_parameter)
                    status_class = f"status-{status.lower().replace(' ', '-')}"
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h5>{date.strftime('%m/%d')}</h5>
                        <h3 style="color: #3b82f6;">{pred:.2f}</h3>
                        <div class="{status_class}">{status}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Donut charts for risk assessment
            st.markdown("### 🎯 **Risk Assessment Dashboard**")
            donut_cols = st.columns(5)
            
            for i, (date, pred) in enumerate(zip(forecast_dates, predictions)):
                with donut_cols[i]:
                    st.markdown(f"**{date.strftime('%m/%d')}**")
                    donut_chart = make_donut(pred, f"Day {i+1}", selected_parameter, df, selected_parameter)
                    st.altair_chart(donut_chart, use_container_width=True)
        
        # AI Report section
        if show_ai_report and show_forecast:
            st.markdown("## 🤖 **AI-Powered Water Quality Insights**")
            
            with st.spinner("🧠 Generating comprehensive analysis..."):
                gemini_report = generate_gemini_water_quality_report(
                    selected_parameter, predictions, forecast_dates, df
                )
            
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown(gemini_report)
            st.markdown('</div>', unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please check your data files and model paths.")

if __name__ == "__main__":
    main()
