import streamlit as st
import pandas as pd
import numpy as np
from bokeh.plotting import figure
from io import StringIO
import lasio

# Function to load data from uploaded files
def load_data(uploaded_file, file_type='las'):
    if uploaded_file:
        bytes_data = uploaded_file.read()
        if file_type == 'las':
            # Decode using Windows-1252 encoding to support LAS files.
            str_io = StringIO(bytes_data.decode('Windows-1252'))
            las_file = lasio.read(str_io)
            well_data = las_file.df()
            # Create a DEPTH column from the index for plotting.
            well_data['DEPTH'] = well_data.index
            return las_file, well_data
        elif file_type == 'csv':
            df = pd.read_csv(StringIO(bytes_data.decode('utf-8')))
            return None, df
    return None, None

# Function to plot Bokeh subplots
def plot_bokeh_subplots(core_data, well_data):
    # 1. LEFT COLUMN FIGURES
    # p1: Scatter plot of Core Porosity vs. Depth.
    p1 = figure(
        title="Core Porosity vs. Depth (Scatter)",
        x_range=(0, 50), 
        y_range=(3825, 4010),  # Corrected range order
        width=400, height=400, 
        tools="pan,wheel_zoom,box_zoom,reset,save"
    )
    try:
        p1.scatter(core_data["CPOR"], core_data["DEPTH"],
                   color="red", size=8, legend_label="Core Porosity")
    except Exception as e:
        st.error("Error plotting CPOR scatter: " + str(e))
    p1.xaxis.axis_label = "Porosity (%)"
    p1.yaxis.axis_label = "Depth (ft)"

    # p1_extra: CPOR Trend Line (line plot with swapped axes to mimic twin axes).
    p1_extra = figure(
        title="CPOR Trend (Line)",
        width=400, height=400,
        tools="pan,wheel_zoom,box_zoom,reset,save"
    )
    try:
        p1_extra.line(core_data["DEPTH"], core_data["CPOR"],
                      color="green", line_width=2, legend_label="CPOR Trend")
    except Exception as e:
        st.error("Error plotting CPOR trend: " + str(e))
    p1_extra.xaxis.axis_label = "Depth (ft)"
    p1_extra.yaxis.axis_label = "Porosity (%)"

    # p1c: Optional plot for PHIF (NEU) vs. Depth from well data.
    p1c = None
    if well_data is not None and 'PHIF' in well_data.columns:
        p1c = figure(
            title="PHIF (NEU) vs. Depth",
            x_range=(0, 0.4), 
            y_range=(3825, 4010),  # Corrected range order
            width=400, height=400, 
            tools="pan,wheel_zoom,box_zoom,reset,save"
        )
        try:
            p1c.line(well_data["PHIF"], well_data["DEPTH"],
                     color="blue", line_width=1, legend_label="PHIF")
        except Exception as e:
            st.error("Error plotting PHIF: " + str(e))
        p1c.xaxis.axis_label = "NEU (Well Data)"
        p1c.yaxis.axis_label = "Depth (ft)"

    # 2. CENTER COLUMN FIGURE
    # p2: Core Permeability vs. Depth with logarithmic x-axis.
    p2 = figure(
        title="Core Permeability vs. Depth",
        x_axis_type="log",
        x_range=(0.01, 100000), 
        y_range=(3825, 4010),  # Corrected range order
        width=400, height=400, 
        tools="pan,wheel_zoom,box_zoom,reset,save"
    )
    try:
        p2.scatter(core_data["CKHG"], core_data["DEPTH"],
                   color="blue", size=8, legend_label="Core Permeability")
    except Exception as e:
        st.error("Error plotting Core Permeability: " + str(e))
    p2.xaxis.axis_label = "Permeability (mD)"
    p2.yaxis.axis_label = "Depth (ft)"

    # 3. RIGHT COLUMN FIGURES
    # p3: Poro-Perm Scatter Plot (Core Porosity vs. Core Permeability).
    p3 = figure(
        title="Poro-Perm Scatter Plot",
        x_range=(0, 50),
        y_axis_type="log",
        width=400, height=300, 
        tools="pan,wheel_zoom,box_zoom,reset,save"
    )
    try:
        p3.scatter(core_data["CPOR"], core_data["CKHG"],
                   color="purple", size=8, alpha=0.5, legend_label="Poro-Perm")
    except Exception as e:
        st.error("Error plotting Poro-Perm scatter: " + str(e))
    p3.xaxis.axis_label = "Core Porosity (%)"
    p3.yaxis.axis_label = "Core Permeability (mD)"

    # p4: Histogram for Core Porosity.
    hist, edges = np.histogram(core_data["CPOR"].dropna(), bins=30)
    p4 = figure(
        title="Core Porosity Histogram",
        width=400, height=300,
        tools="pan,wheel_zoom,box_zoom,reset,save"
    )
    try:
        p4.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
                fill_color="red", line_color="black", alpha=0.6,
                legend_label="Porosity Histogram")
    except Exception as e:
        st.error("Error plotting Porosity Histogram: " + str(e))
        
    p4.xaxis.axis_label = "Core Porosity (%)"
    p4.yaxis.axis_label = "Count"

    # p5: Histogram for Core Grain Density (if available).
    p5 = None
    if 'CGD' in core_data.columns:
        hist2, edges2 = np.histogram(core_data["CGD"].dropna(), bins=30)
        p5 = figure(
            title="Core Grain Density Histogram",
            width=400, height=300,
            tools="pan,wheel_zoom,box_zoom,reset,save"
        )
        try:
            p5.quad(top=hist2, bottom=0, left=edges2[:-1], right=edges2[1:],
                    fill_color="blue", line_color="black", alpha=0.6,
                    legend_label="Grain Density")
        except Exception as e:
            st.error("Error plotting Grain Density Histogram: " + str(e))
            
        p5.xaxis.axis_label = "Core Grain Density"
        p5.yaxis.axis_label = "Count"

    # ----------------------------------------------------
    # Use Streamlit's columns to display the figures separately.
    col_left, col_center, col_right = st.columns(3)
    
    with col_left:
        st.bokeh_chart(p1)
        if p1c is not None:
            st.bokeh_chart(p1c)
        st.bokeh_chart(p1_extra)
    
    with col_center:
        st.bokeh_chart(p2)
    
    with col_right:
        st.bokeh_chart(p3)
        st.bokeh_chart(p4)
        if p5 is not None:
            st.bokeh_chart(p5)

# Main function to display the page
def show_page():
    st.title("Well Logging Analysis – Bokeh Visualizations")
    
    uploaded_las = st.file_uploader("Upload your LAS File", type=["las"])
    
    uploaded_csv = st.file_uploader("Upload your Core Data CSV File", type=["csv"])
    
    las_file, well_data = load_data(uploaded_las, file_type='las')
    
    _, core_data = load_data(uploaded_csv, file_type='csv')
    
    if core_data is not None:
        
        st.write("### Core Data Overview")
        
        st.dataframe(core_data.head())
        
        st.write("### Bokeh Visualizations")
        
        plot_bokeh_subplots(core_data, well_data)
    
    else:
        
        st.info("Please upload your Core Data CSV file to view visualizations.")

# Entry point for the Streamlit app
if __name__ == "__main__":
    
   show_page()
