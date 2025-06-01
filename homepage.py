import streamlit as st
import folium
from streamlit_folium import st_folium

# Function to create the Streamlit app
def create_home_page():
    st.set_page_config(page_title="Ganga Water Quality Forecasting", layout="centered")
    
    # Water-themed background style using CSS
    st.markdown(
        """
        <style>
        .main {
            background: linear-gradient(to bottom, #a2d5f2, #07689f);
            color: white;
            font-family: 'Arial', sans-serif;
        }
        .stApp {
            background: linear-gradient(to bottom, #a2d5f2, #07689f);
        }
        .title {
            font-size: 3rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px #003366;
            color: white;
            text-align: center;
        }
        .subtitle {
            font-size: 1.5rem;
            margin-bottom: 2rem;
            text-shadow: 1px 1px 3px #004080;
            color: white;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Title and subtitle
    st.markdown('<div class="title">Ganga Water Quality Forecasting</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Predicting the purity of the sacred river</div>', unsafe_allow_html=True)

    # Create a folium map centered on India with OpenStreetMap tiles
    m = folium.Map(
        location=[22.9734, 78.6569],
        zoom_start=5,
        tiles="OpenStreetMap"
    )
    
    # Highlight the Ganga river path
    ganga_coordinates = [
        [30.9910, 78.9200],  # Gangotri (source)
        [29.9457, 78.1642],  # Rishikesh
        [25.3176, 83.0130],  # Varanasi
        [25.6200, 85.1800],  # Patna
        [24.7914, 87.9336],  # Farakka
        [22.5726, 88.3639]   # Kolkata (near delta)
    ]
    
    folium.PolyLine(
        ganga_coordinates,
        color='#3498db',
        weight=4,
        opacity=0.8,
        tooltip='Ganga River'
    ).add_to(m)

    # Display the map in Streamlit with a container for better styling
    st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
    st_folium(m, width=700, height=500)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add a footer with information about the application
    st.markdown("""
    <div style='text-align: center; color: white; padding: 20px; margin-top: 20px;'>
        <p>This application provides forecasting and analysis of water quality parameters along the Ganga river.</p>
        <p>Navigate to different sections using the sidebar menu.</p>
    </div>
    """, unsafe_allow_html=True)

# Run the app function if this script is executed
if __name__ == '__main__':
    create_home_page()
