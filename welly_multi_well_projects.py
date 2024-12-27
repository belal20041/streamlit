import streamlit as st
import pandas as pd
import lasio
from io import StringIO
import matplotlib.pyplot as plt
from welly import Well, Project, Curve

# Load multiple wells using Project
def load_wells(directory_path):
    wells = Project.from_las(directory_path)
    return wells

# Function to display well details
def show_well_details(wells):
    st.write(f"Number of wells loaded: {len(wells)}")
    for well in wells:
        st.write(f"Well: {well.name}")
        st.write(f"Curves: {list(well.data.keys())}")

# Function to plot GR and DEPTH from all wells
def plot_gr_curves(wells):
    fig, axs = plt.subplots(figsize=(14, 10), ncols=len(wells))
    for i, (ax, well) in enumerate(zip(axs, wells)):
        gr = well.get_curve('GR')
        if gr is not None:
            ax = gr.plot(ax=ax, c='green')
            ax.set_title(f"GR for\n{well.name}")
    plt.tight_layout()
    st.pyplot(fig)

# Function to plot RHOB and DEPTH from all wells
def plot_rhob_curves(wells):
    fig, axs = plt.subplots(figsize=(14, 10), ncols=len(wells))
    curve_name = 'RHOB'
    for i, (ax, well) in enumerate(zip(axs, wells)):
        rhob = well.get_curve(curve_name)
        if rhob is not None:
            ax = rhob.plot(ax=ax, c='red')
            ax.set_title(f"{curve_name} for\n{well.name}")
    plt.tight_layout()
    st.pyplot(fig)

# Streamlit App to display the page
def show_page():
    st.title("Welly Multi Well Project")

    directory_path = st.text_input("Enter the path to your 'welly_data' folder containing LAS files")
    if directory_path:
        wells = load_wells(directory_path)
        st.success(f"{len(wells)} wells loaded successfully")

        display_options = st.multiselect(
            "Select what to display:",
            ["Well Details", "GR Curves", "RHOB Curves"]
        )

        if "Well Details" in display_options:
            show_well_details(wells)

        if "GR Curves" in display_options:
            plot_gr_curves(wells)

        if "RHOB Curves" in display_options:
            plot_rhob_curves(wells)

if __name__ == "__main__":
    show_page()
