import streamlit as st
from io import StringIO
import lasio
import pandas as pd
import matplotlib.pyplot as plt

def load_data(uploaded_file):
    """
    Load and process a LAS file.

    This function reads an uploaded LAS file, decodes it using Windows-1252 encoding,
    and then processes the file with lasio into a pandas DataFrame.
    A DEPTH column is added (using the DataFrame's index) for further plotting.
    """
    if uploaded_file is not None:
        try:
            # Read the uploaded file as bytes and decode it for LAS parsing
            bytes_data = uploaded_file.read()
            str_io = StringIO(bytes_data.decode('Windows-1252'))
            las_file = lasio.read(str_io)
            well_data = las_file.df()
            well_data['DEPTH'] = well_data.index
        except UnicodeDecodeError as e:
            st.error(f"Error loading log.las: {e}")
            las_file, well_data = None, None
    else:
        las_file, well_data = None, None

    return las_file, well_data

# Configure the Streamlit page
st.set_page_config(layout="wide", page_title='Petro Data Explorer')

# App title
st.title('Petro Data Explorer')

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select a page:",
    [
        'Well Logging', 
        'Core Analysis', 
        'Welly Multi Well Projects',
        'Survey Data', 
        'Decline Curve Analysis', 
        'Estimated Ultimate Recovery'
    ]
)

# File descriptions for each page
file_descriptions = {
    'Well Logging': (
        "Upload LAS file (.las format) for well logging data analysis. "
        "LAS files contain well logs, which can be processed to generate different analyses, "
        "including gamma ray, resistivity, and density logs."
    ),
    'Core Analysis': (
        "Upload CSV file containing core analysis data. The core analysis data includes "
        "physical properties like porosity, permeability, and grain density for analyzing reservoir "
        "characteristics."
    ),
    'Welly Multi Well Projects': (
        "Upload LAS files for multiple wells. The project involves analyzing data from several wells "
        "to compare geological properties and production information across different locations."
    ),
    'Survey Data': (
        "Upload LAS file with survey data for well path analysis. This data includes well deviations, "
        "inclination, azimuth, and other survey parameters to analyze the well's trajectory."
    ),
    'Decline Curve Analysis': (
        "Upload an Excel file with production data for decline curve analysis. This analysis helps "
        "estimate future production rates and reserves based on past performance."
    ),
    'Estimated Ultimate Recovery': (
        "Upload an Excel file containing production data for estimating ultimate recovery. The data "
        "helps estimate the total recoverable reserves using different recovery models."
    )
}

# Display the selected page description in the sidebar
st.sidebar.subheader("Page Description")
st.sidebar.write(file_descriptions[page])

# Import and display the corresponding page based on the selected navigation option
if page == 'Well Logging':
    import well_logging
    st.sidebar.subheader("Well Logging Instructions")
    st.sidebar.write("Upload LAS file for detailed well logging analysis.")
    well_logging.show_page()
elif page == 'Core Analysis':
    import core_analysis
    st.sidebar.subheader("Core Analysis Instructions")
    st.sidebar.write("Upload a CSV file containing core data.")
    core_analysis.show_page()
elif page == 'Welly Multi Well Projects':
    import welly_multi_well_projects
    st.sidebar.subheader("Multi-Well Projects Instructions")
    st.sidebar.write("Upload multiple LAS files for comparison.")
    welly_multi_well_projects.show_page()
elif page == 'Survey Data':
    import survey_data
    st.sidebar.subheader("Survey Data Instructions")
    st.sidebar.write("Upload LAS file containing survey data for analysis.")
    survey_data.show_page()
elif page == 'Decline Curve Analysis':
    import decline_curve_analysis
    st.sidebar.subheader("Decline Curve Analysis Instructions")
    st.sidebar.write("Upload Excel file with production data for decline analysis.")
    decline_curve_analysis.show_page()
elif page == 'Estimated Ultimate Recovery':
    import estimated_ultimate_recovery
    st.sidebar.subheader("Estimated Ultimate Recovery Instructions")
    st.sidebar.write("Upload Excel file with production data for recovery estimation.")
    estimated_ultimate_recovery.show_page()
