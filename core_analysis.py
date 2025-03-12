import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from io import StringIO
import lasio

def load_data(uploaded_file, file_type='las'):
    if uploaded_file:
        bytes_data = uploaded_file.read()
        if file_type == 'las':
            str_io = StringIO(bytes_data.decode('Windows-1252'))
            las_file = lasio.read(str_io)
            well_data = las_file.df()
            # Create a DEPTH column for plotting
            well_data['DEPTH'] = well_data.index
            return las_file, well_data
        elif file_type == 'csv':
            df = pd.read_csv(StringIO(bytes_data.decode('utf-8')))
            return None, df
    return None, None

def plot_interactive_subplots(core_data, well_data):
    # Create a 3x3 grid:
    # - Left column spans all 3 rows and supports a secondary y-axis.
    # - Middle column spans all 3 rows.
    # - Right column contains three individual subplots.
    fig = make_subplots(
        rows=3, cols=3,
        specs=[
            [{"rowspan": 3, "secondary_y": True}, {"rowspan": 3}, {}],
            [None, None, {}],
            [None, None, {}]
        ],
        horizontal_spacing=0.08,
        vertical_spacing=0.08
    )
    
    # ----- Subplot (1,1): Core Porosity vs. Depth with twin axes -----
    if 'CPOR' in core_data.columns:
        # Trace 1: Red scatter (Core Porosity vs. Depth)
        fig.add_trace(
            go.Scatter(
                x=core_data["CPOR"],
                y=core_data["DEPTH"],
                mode='markers',
                marker=dict(color='red'),
                name="Core Porosity"
            ),
            row=1, col=1, secondary_y=False
        )
        # Trace 2: Green line on secondary y-axis.
        # (Note: In your original code this trace plots core_data["DEPTH"] on x and CPOR on y.)
        fig.add_trace(
            go.Scatter(
                x=core_data["DEPTH"],
                y=core_data["CPOR"],
                mode='lines',
                line=dict(color='green', width=2),
                name="CPOR Line"
            ),
            row=1, col=1, secondary_y=True
        )
        
        # Configure axes for cell (1,1)
        fig.update_xaxes(title_text="Core Porosity (%)", range=[0, 50], row=1, col=1)
        fig.update_yaxes(title_text="Depth (ft)", range=[4010, 3825], autorange="reversed", row=1, col=1, secondary_y=False)
        fig.update_yaxes(title_text="CPOR Line", row=1, col=1, secondary_y=True)
        
        # Trace 3: Blue line for PHIF vs. Depth on an overlaid twin x-axis (if available).
        if well_data is not None and 'PHIF' in well_data.columns:
            # Add the PHIF trace and assign it to a new x-axis.
            fig.add_trace(
                go.Scatter(
                    x=well_data["PHIF"],
                    y=well_data["DEPTH"],
                    mode='lines',
                    line=dict(color='blue', width=1),
                    name="PHIF (Well Data)"
                ),
                row=1, col=1, secondary_y=False
            )
            # Force this trace to use a new x-axis ("xaxis3").
            fig.data[-1].xaxis = "x3"
            # Define xaxis3 to overlay the main x-axis (xaxis1) and appear on top.
            fig.update_layout(
                xaxis3=dict(
                    overlaying="x1",
                    side='top',
                    title="NEU (Well Data)",
                    range=[0, 0.4]
                )
            )
    
    # ----- Subplot (1,2): Core Permeability vs. Depth -----
    if 'CKHG' in core_data.columns:
        fig.add_trace(
            go.Scatter(
                x=core_data["CKHG"],
                y=core_data["DEPTH"],
                mode='markers',
                marker=dict(color='blue'),
                name="Core Permeability"
            ),
            row=1, col=2
        )
        fig.update_xaxes(title_text="Permeability (mD)", type="log",
                         range=[np.log10(0.01), np.log10(100000)], row=1, col=2)
        fig.update_yaxes(title_text="Depth (ft)", range=[4010, 3825], autorange="reversed", row=1, col=2)
    
    # ----- Subplot (1,3): Poro-Perm Scatter Plot (Core Porosity vs. Core Permeability) -----
    if 'CPOR' in core_data.columns and 'CKHG' in core_data.columns:
        fig.add_trace(
            go.Scatter(
                x=core_data["CPOR"],
                y=core_data["CKHG"],
                mode='markers',
                marker=dict(opacity=0.5),
                name="Poro-Perm Scatter"
            ),
            row=1, col=3
        )
        fig.update_xaxes(title_text="Core Porosity (%)", range=[0, 50], row=1, col=3)
        fig.update_yaxes(title_text="Core Permeability (mD)", type="log", row=1, col=3)
    
    # ----- Subplot (2,3): Histogram for Core Porosity -----
    if 'CPOR' in core_data.columns:
        fig.add_trace(
            go.Histogram(
                x=core_data["CPOR"].dropna(),
                nbinsx=30,
                marker_color="red",
                opacity=0.6,
                name="Porosity Histogram"
            ),
            row=2, col=3
        )
        fig.update_xaxes(title_text="Core Porosity", row=2, col=3)
        fig.update_yaxes(title_text="Count", row=2, col=3)
    
    # ----- Subplot (3,3): Histogram for Core Grain Density -----
    if 'CGD' in core_data.columns:
        fig.add_trace(
            go.Histogram(
                x=core_data["CGD"].dropna(),
                nbinsx=30,
                marker_color="blue",
                opacity=0.6,
                name="Grain Density Histogram"
            ),
            row=3, col=3
        )
        fig.update_xaxes(title_text="Core Grain Density", row=3, col=3)
        fig.update_yaxes(title_text="Count", row=3, col=3)
    
    fig.update_layout(
        height=800,
        width=1200,
        title_text="Core Data Visualizations",
        showlegend=True,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

def show_page():
    st.title("Well Logging Analysis")
    uploaded_las = st.file_uploader("Upload your LAS file", type=["las"])
    uploaded_csv = st.file_uploader("Upload your Core Data CSV file", type=["csv"])
    las_file, well_data = load_data(uploaded_las, file_type='las')
    _, core_data = load_data(uploaded_csv, file_type='csv')
    
    if core_data is not None:
        st.write("### Core Data Overview")
        st.dataframe(core_data.head())
        st.write("### Subplots for Core Porosity, Core Permeability, Histograms, and Poro-Perm Scatter")
        plot_interactive_subplots(core_data, well_data)
    else:
        st.info("Please upload your Core Data CSV file to view visualizations.")

if __name__ == "__main__":
    show_page()
