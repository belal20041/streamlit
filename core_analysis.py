import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
import lasio
import plotly.graph_objects as go

# Function to load data from uploaded files
def load_data(uploaded_file, file_type='las'):
    if uploaded_file:
        bytes_data = uploaded_file.read()
        if file_type == 'las':
            try:
                # Decode using Windows-1252 encoding to support LAS files.
                str_io = StringIO(bytes_data.decode('Windows-1252'))
                las_file = lasio.read(str_io)
                well_data = las_file.df()
                # Create a DEPTH column from the index for plotting.
                well_data['DEPTH'] = well_data.index
                return las_file, well_data
            except Exception as e:
                st.error(f"Error loading LAS file: {e}")
        elif file_type == 'csv':
            try:
                df = pd.read_csv(StringIO(bytes_data.decode('utf-8')))
                return None, df
            except Exception as e:
                st.error(f"Error loading CSV file: {e}")
    return None, None

# Function to plot Plotly subplots
def plot_plotly_subplots(core_data, well_data):
    # 1. LEFT COLUMN FIGURES
    # Scatter plot of Core Porosity vs. Depth.
    try:
        scatter_cpor_depth = go.Figure()
        scatter_cpor_depth.add_trace(go.Scatter(
            x=core_data["CPOR"], 
            y=core_data["DEPTH"], 
            mode='markers', 
            marker=dict(color='red', size=8),
            name="Core Porosity"
        ))
        scatter_cpor_depth.update_layout(
            title="Core Porosity vs. Depth (Scatter)",
            xaxis_title="Porosity (%)",
            yaxis_title="Depth (ft)",
            yaxis=dict(autorange="reversed"),
            height=400,
            width=400
        )
    except Exception as e:
        st.error(f"Error creating Core Porosity scatter plot: {e}")

    # Line plot for CPOR Trend.
    try:
        line_cpor_trend = go.Figure()
        line_cpor_trend.add_trace(go.Scatter(
            x=core_data["DEPTH"], 
            y=core_data["CPOR"], 
            mode='lines', 
            line=dict(color='green', width=2),
            name="CPOR Trend"
        ))
        line_cpor_trend.update_layout(
            title="CPOR Trend (Line)",
            xaxis_title="Depth (ft)",
            yaxis_title="Porosity (%)",
            height=400,
            width=400
        )
    except Exception as e:
        st.error(f"Error creating CPOR trend line plot: {e}")

    # Optional PHIF (NEU) vs. Depth line plot.
    phif_plot = None
    if well_data is not None and 'PHIF' in well_data.columns:
        try:
            phif_plot = go.Figure()
            phif_plot.add_trace(go.Scatter(
                x=well_data["PHIF"], 
                y=well_data["DEPTH"], 
                mode='lines',
                line=dict(color='blue', width=1),
                name="PHIF"
            ))
            phif_plot.update_layout(
                title="PHIF (NEU) vs. Depth",
                xaxis_title="NEU (Well Data)",
                yaxis_title="Depth (ft)",
                yaxis=dict(autorange="reversed"),
                height=400,
                width=400
            )
        except Exception as e:
            st.error(f"Error creating PHIF plot: {e}")

    # 2. CENTER COLUMN FIGURE
    # Core Permeability vs. Depth with logarithmic x-axis.
    try:
        scatter_perm_depth = go.Figure()
        scatter_perm_depth.add_trace(go.Scatter(
            x=core_data["CKHG"], 
            y=core_data["DEPTH"], 
            mode='markers',
            marker=dict(color='blue', size=8),
            name="Core Permeability"
        ))
        scatter_perm_depth.update_layout(
            title="Core Permeability vs. Depth",
            xaxis_title="Permeability (mD)",
            yaxis_title="Depth (ft)",
            xaxis_type="log",
            yaxis=dict(autorange="reversed"),
            height=400,
            width=400
        )
    except Exception as e:
        st.error(f"Error creating Core Permeability scatter plot: {e}")

    # 3. RIGHT COLUMN FIGURES
    # Poro-Perm Scatter Plot.
    try:
        poro_perm_scatter = go.Figure()
        poro_perm_scatter.add_trace(go.Scatter(
            x=core_data["CPOR"], 
            y=core_data["CKHG"], 
            mode='markers',
            marker=dict(color='purple', size=8, opacity=0.5),
            name="Poro-Perm"
        ))
        poro_perm_scatter.update_layout(
            title="Poro-Perm Scatter Plot",
            xaxis_title="Core Porosity (%)",
            yaxis_title="Core Permeability (mD)",
            yaxis_type="log",
            height=300,
            width=400
        )
    except Exception as e:
        st.error(f"Error creating Poro-Perm scatter plot: {e}")

    # Histogram for Core Porosity.
    try:
        hist_cpor = go.Figure()
        hist_cpor.add_trace(go.Histogram(
            x=core_data["CPOR"],
            nbinsx=30,
            marker_color='red',
            opacity=0.6,
        ))
        hist_cpor.update_layout(
            title="Core Porosity Histogram",
            xaxis_title="Core Porosity (%)",
            yaxis_title="Count",
            height=300,
            width=400
        )
    except Exception as e:
        st.error(f"Error creating Core Porosity histogram: {e}")

    # Optional Histogram for Core Grain Density.
    cgd_histogram = None
    if 'CGD' in core_data.columns:
        try:
            cgd_histogram = go.Figure()
            cgd_histogram.add_trace(go.Histogram(
                x=core_data["CGD"],
                nbinsx=30,
                marker_color='blue',
                opacity=0.6,
            ))
            cgd_histogram.update_layout(
                title="Core Grain Density Histogram",
                xaxis_title="Core Grain Density",
                yaxis_title="Count",
                height=300,
                width=400
            )
        except Exception as e:
            st.error(f"Error creating Core Grain Density histogram: {e}")

    # ----------------------------------------------------
    # Use Streamlit's columns to display the figures separately.
    col_left, col_center, col_right = st.columns(3)
    
    with col_left:
        st.plotly_chart(scatter_cpor_depth)
        if phif_plot is not None:
           st.plotly_chart(phif_plot)
        st.plotly_chart(line_cpor_trend)
    
    with col_center:
       st.plotly_chart(scatter_perm_depth)
    
    with col_right:
       st.plotly_chart(poro_perm_scatter)
       st.plotly_chart(hist_cpor)
       if cgd_histogram is not None:
           st.plotly_chart(cgd_histogram)

# Main function to display the page
def show_page():
    st.title("Well Logging Analysis – Plotly Visualizations")
    
    uploaded_las = st.file_uploader("Upload your LAS File", type=["las"])
    
    uploaded_csv = st.file_uploader("Upload your Core Data CSV File", type=["csv"])
    
    las_file, well_data = load_data(uploaded_las, file_type='las')
    
    _, core_data = load_data(uploaded_csv, file_type='csv')
    
    if core_data is not None:
        
        st.write("### Core Data Overview")
        
        st.dataframe(core_data.head())
        
        st.write("### Plotly Visualizations")
        
        plot_plotly_subplots(core_data, well_data)
    
    else:
        
       st.info("Please upload your Core Data CSV file to view visualizations.")

# Entry point for the Streamlit app
if __name__ == "__main__":
   show_page()
