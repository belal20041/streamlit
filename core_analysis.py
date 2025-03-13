import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import lasio

# Function to load and process LAS file
def load_data(uploaded_file, file_type='las'):
    if uploaded_file:
        bytes_data = uploaded_file.read()
        if file_type == 'las':
            str_io = StringIO(bytes_data.decode('Windows-1252'))
            las_file = lasio.read(str_io)
            well_data = las_file.df()
            well_data['DEPTH'] = well_data.index
            return las_file, well_data
        elif file_type == 'csv':
            df = pd.read_csv(StringIO(bytes_data.decode('utf-8')))
            return None, df
    return None, None

def plot_subplots(core_data, well_data):
    fig = plt.figure(figsize=(10, 10))
    ax1 = plt.subplot2grid(shape=(3, 3), loc=(0, 0), rowspan=3)
    ax2 = plt.subplot2grid(shape=(3, 3), loc=(0, 1), rowspan=3)
    ax3 = plt.subplot2grid(shape=(3, 3), loc=(0, 2))
    ax4 = plt.subplot2grid(shape=(3, 3), loc=(1, 2))
    ax5 = plt.subplot2grid(shape=(3, 3), loc=(2, 2))
    ax6 = ax1.twiny()

    if 'CPOR' in core_data.columns:
        ax1.scatter(core_data["CPOR"], core_data["DEPTH"], marker='o', c='red')
        ax1.set_xlim(0, 50)
        ax1.set_ylim(4010, 3825)
        ax1.set_title('Core Porosity')
        ax1.set_xlabel('Porosity (%)')
        ax1.set_ylabel('Depth (ft)')
        ax1.grid()
        
        ax1_twin = ax1.twinx()
        ax1_twin.plot(core_data["DEPTH"], core_data["CPOR"], color='green', linewidth=2)
        ax1_twin.set_ylabel('CPOR Line', color='green')
        ax1_twin.tick_params(axis='y', labelcolor='green')
    
    if 'CKHG' in core_data.columns:
        ax2.scatter(core_data["CKHG"], core_data["DEPTH"], marker='o', c='blue')
        ax2.set_xlim(0.01, 100000)
        ax2.set_xscale('log')
        ax2.set_ylim(4010, 3825)
        ax2.set_title('Core Permeability')
        ax2.set_xlabel('Permeability (mD)')
        ax2.grid()
    
    if 'CPOR' in core_data.columns and 'CKHG' in core_data.columns:
        ax3.scatter(core_data["CPOR"], core_data["CKHG"], marker='o', alpha=0.5)
        ax3.set_yscale('log')
        ax3.set_xlim(0, 50)
        ax3.set_title('Poro-Perm Scatter Plot')
        ax3.set_xlabel('Core Porosity (%)')
        ax3.set_ylabel('Core Permeability (mD)')
        ax3.grid()
    
    if 'CPOR' in core_data.columns:
        ax4.hist(core_data["CPOR"].dropna(), bins=30, edgecolor='black', color='red', alpha=0.6)
        ax4.set_xlabel('Core Porosity')
        ax4.set_title('Porosity Histogram')
    
    if 'CGD' in core_data.columns:
        ax5.hist(core_data["CGD"].dropna(), bins=30, edgecolor='black', color='blue', alpha=0.6)
        ax5.set_xlabel('Core Grain Density')
        ax5.set_title('Grain Density Histogram')
    
    if 'PHIF' in well_data.columns:
        ax6.plot(well_data['PHIF'], well_data['DEPTH'], color='blue', lw=0.5)
        ax6.set_xlim(0, 0.4)
        ax6.set_xlabel('NEU (Well Data)')
    
    plt.tight_layout()
    st.pyplot(fig)

def show_page():
    st.title("Well Logging Analysis")
    uploaded_las = st.file_uploader("Upload your LAS file", type=["las"])
    uploaded_csv = st.file_uploader("Upload your Core Data CSV file", type=["csv"])
    las_file, well_data = load_data(uploaded_las, file_type='las')
    _, core_data = load_data(uploaded_csv, file_type='csv')
    if core_data is not None:
        st.write("### Core Data Overview")
        st.write(core_data.head())
        st.write("### Subplots for Core Porosity, Core Permeability, Histograms, and PHIF vs Depth")
        plot_subplots(core_data, well_data)

if __name__ == "__main__":
    show_page()
