import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
import lasio

def load_data(uploaded_file, file_type='las'):
    if uploaded_file:
        bytes_data = uploaded_file.read()
        if file_type == 'las':
            # Decode using Windows-1252 encoding to support LAS files
            str_io = StringIO(bytes_data.decode('Windows-1252'))
            las_file = lasio.read(str_io)
            well_data = las_file.df()
            # Create a DEPTH column from the index for plotting
            well_data['DEPTH'] = well_data.index
            return las_file, well_data
        elif file_type == 'csv':
            df = pd.read_csv(StringIO(bytes_data.decode('utf-8')))
            return None, df
    return None, None

def plot_interactive(core_data, well_data):
    # Chart 1: Core Porosity vs. Depth with an overlay of PHIF (from well data) on a secondary x-axis.
    if 'CPOR' in core_data.columns:
        fig1 = go.Figure()
        
        # Scatter for Core Porosity from core_data
        fig1.add_trace(go.Scatter(
            x=core_data["CPOR"],
            y=core_data["DEPTH"],
            mode='markers',
            marker=dict(color='red'),
            name='Core Porosity'
        ))
        
        # If well_data is provided and contains PHIF, plot it as a line on a secondary x-axis.
        if well_data is not None and 'PHIF' in well_data.columns:
            fig1.add_trace(go.Scatter(
                x=well_data["PHIF"],
                y=well_data["DEPTH"],
                mode='lines',
                line=dict(color='blue', width=1),
                name='PHIF (Well Data)',
                xaxis='x2'
            ))
            # Define the secondary x-axis (displayed at the top)
            fig1.update_layout(
                xaxis2=dict(
                    overlaying='x',
                    side='top',
                    title='NEU (Well Data)',
                    range=[0, 0.4]
                )
            )
        
        fig1.update_layout(
            title="Core Porosity vs. Depth with PHIF Overlay",
            xaxis=dict(title="Core Porosity (%)", range=[0, 50]),
            yaxis=dict(title="Depth (ft)", autorange='reversed'),
            legend=dict(x=0.02, y=0.98)
        )
        st.plotly_chart(fig1, use_container_width=True)

    # Chart 2: Core Permeability vs. Depth (with a logarithmic x-axis)
    if 'CKHG' in core_data.columns:
        fig2 = px.scatter(
            core_data,
            x="CKHG", 
            y="DEPTH",
            title="Core Permeability vs. Depth",
            labels={"CKHG": "Permeability (mD)", "DEPTH": "Depth (ft)"},
            log_x=True
        )
        fig2.update_yaxes(autorange="reversed")
        st.plotly_chart(fig2, use_container_width=True)

    # Chart 3: Poro-Perm Scatter Plot (Core Porosity vs. Core Permeability)
    if 'CPOR' in core_data.columns and 'CKHG' in core_data.columns:
        fig3 = px.scatter(
            core_data,
            x="CPOR",
            y="CKHG",
            title="Core Porosity vs. Permeability",
            labels={"CPOR": "Core Porosity (%)", "CKHG": "Core Permeability (mD)"},
            log_y=True
        )
        fig3.update_xaxes(range=[0, 50])
        st.plotly_chart(fig3, use_container_width=True)

    # Chart 4: Histogram for Core Porosity
    if 'CPOR' in core_data.columns:
        fig4 = px.histogram(
            core_data,
            x="CPOR",
            nbins=30,
            title="Core Porosity Histogram",
            labels={"CPOR": "Core Porosity (%)"}
        )
        st.plotly_chart(fig4, use_container_width=True)

    # Chart 5: Histogram for Core Grain Density
    if 'CGD' in core_data.columns:
        fig5 = px.histogram(
            core_data,
            x="CGD",
            nbins=30,
            title="Core Grain Density Histogram",
            labels={"CGD": "Core Grain Density"}
        )
        st.plotly_chart(fig5, use_container_width=True)

def show_page():
    st.title("Well Logging Analysis")

    # File uploaders for the LAS file (well data) and CSV (core data)
    uploaded_las = st.file_uploader("Upload your LAS file", type=["las"])
    uploaded_csv = st.file_uploader("Upload your Core Data CSV file", type=["csv"])
    
    las_file, well_data = load_data(uploaded_las, file_type='las')
    _, core_data = load_data(uploaded_csv, file_type='csv')
    
    if core_data is not None:
        st.write("### Core Data Overview")
        st.dataframe(core_data.head())
        st.write("### Interactive Visualizations")
        plot_interactive(core_data, well_data)
    else:
        st.info("Please upload your Core Data CSV file to view visualizations.")

if __name__ == "__main__":
    show_page()
