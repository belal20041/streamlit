import streamlit as st
import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.layouts import column, row
from io import StringIO
import lasio

def load_data(uploaded_file, file_type='las'):
    if uploaded_file:
        bytes_data = uploaded_file.read()
        if file_type == 'las':
            # Decode using Windows-1252 to support LAS files.
            str_io = StringIO(bytes_data.decode('Windows-1252'))
            las_file = lasio.read(str_io)
            well_data = las_file.df()
            # Create a DEPTH column from the DataFrame index.
            well_data['DEPTH'] = well_data.index
            return las_file, well_data
        elif file_type == 'csv':
            df = pd.read_csv(StringIO(bytes_data.decode('utf-8')))
            return None, df
    return None, None

def plot_bokeh_subplots(core_data, well_data):
    # -------------------------------
    # LEFT COLUMN: Core Porosity Figures
    # p1: Scatter plot of Core Porosity vs. Depth.
    p1 = figure(
        title="Core Porosity vs. Depth (Scatter)",
        x_range=(0, 50), y_range=(4010, 3825),
        width=400, height=400, tools="pan,wheel_zoom,box_zoom,reset,save"
    )
    p1.scatter(core_data["CPOR"], core_data["DEPTH"],
               color="red", size=8, legend_label="Core Porosity")
    p1.xaxis.axis_label = "Porosity (%)"
    p1.yaxis.axis_label = "Depth (ft)"
    
    # p1_extra: CPOR Trend Line (Line plot with swapped axes to mimic twin axis).
    p1_extra = figure(
        title="CPOR Trend (Line)",
        width=400, height=400, tools="pan,wheel_zoom,box_zoom,reset,save"
    )
    p1_extra.line(core_data["DEPTH"], core_data["CPOR"],
                  color="green", line_width=2, legend_label="CPOR Trend")
    p1_extra.xaxis.axis_label = "Depth (ft)"
    p1_extra.yaxis.axis_label = "Porosity (%)"
    
    # p1c: Optional plot for PHIF (NEU) vs. Depth, if available.
    if well_data is not None and 'PHIF' in well_data.columns:
        p1c = figure(
            title="PHIF (NEU) vs. Depth",
            x_range=(0, 0.4), y_range=(4010, 3825),
            width=400, height=400, tools="pan,wheel_zoom,box_zoom,reset,save"
        )
        p1c.line(well_data["PHIF"], well_data["DEPTH"],
                 color="blue", line_width=1, legend_label="PHIF")
        p1c.xaxis.axis_label = "NEU (Well Data)"
        p1c.yaxis.axis_label = "Depth (ft)"
    else:
        p1c = None

    # Arrange the left column sub-layout.
    if p1c is not None:
        left_top = row(p1, p1c)
    else:
        left_top = p1
    left_col = column(left_top, p1_extra)
    
    # -------------------------------
    # CENTER COLUMN: Core Permeability vs. Depth.
    p2 = figure(
        title="Core Permeability vs. Depth",
        x_axis_type="log",
        x_range=(0.01, 100000), y_range=(4010, 3825),
        width=400, height=400, tools="pan,wheel_zoom,box_zoom,reset,save"
    )
    p2.scatter(core_data["CKHG"], core_data["DEPTH"],
               color="blue", size=8, legend_label="Core Permeability")
    p2.xaxis.axis_label = "Permeability (mD)"
    p2.yaxis.axis_label = "Depth (ft)"
    
    # -------------------------------
    # RIGHT COLUMN: Additional Figures (stacked vertically)
    # p3: Poro-Perm Scatter Plot.
    p3 = figure(
        title="Poro-Perm Scatter Plot",
        x_range=(0, 50), y_axis_type="log",
        width=400, height=300, tools="pan,wheel_zoom,box_zoom,reset,save"
    )
    p3.scatter(core_data["CPOR"], core_data["CKHG"],
               color="purple", size=8, alpha=0.5, legend_label="Poro-Perm")
    p3.xaxis.axis_label = "Core Porosity (%)"
    p3.yaxis.axis_label = "Core Permeability (mD)"
    
    # p4: Histogram for Core Porosity.
    hist, edges = np.histogram(core_data["CPOR"].dropna(), bins=30)
    p4 = figure(
        title="Core Porosity Histogram",
        width=400, height=300, tools="pan,wheel_zoom,box_zoom,reset,save"
    )
    p4.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
            fill_color="red", line_color="black", alpha=0.6,
            legend_label="Porosity Histogram")
    p4.xaxis.axis_label = "Core Porosity (%)"
    p4.yaxis.axis_label = "Count"
    
    # p5: Histogram for Core Grain Density (if available)
    if 'CGD' in core_data.columns:
        hist2, edges2 = np.histogram(core_data["CGD"].dropna(), bins=30)
        p5 = figure(
            title="Core Grain Density Histogram",
            width=400, height=300, tools="pan,wheel_zoom,box_zoom,reset,save"
        )
        p5.quad(top=hist2, bottom=0, left=edges2[:-1], right=edges2[1:],
                fill_color="blue", line_color="black", alpha=0.6,
                legend_label="Grain Density")
        p5.xaxis.axis_label = "Core Grain Density"
        p5.yaxis.axis_label = "Count"
    else:
        p5 = None

    if p5 is not None:
        right_col = column(p3, p4, p5)
    else:
        right_col = column(p3, p4)
    
    # -------------------------------
    # Use Streamlit columns to lay out the three groups separately.
    col1, col2, col3 = st.columns(3)
    with col1:
        st.bokeh_chart(left_col, use_container_width=True)
    with col2:
        st.bokeh_chart(p2, use_container_width=True)
    with col3:
        st.bokeh_chart(right_col, use_container_width=True)

def show_page():
    st.title("Well Logging Analysis - Bokeh Visualizations")
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

if __name__ == "__main__":
    show_page()
