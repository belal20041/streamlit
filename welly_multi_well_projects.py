import streamlit as st
import pandas as pd
import lasio
from io import StringIO
import matplotlib.pyplot as plt
from welly import Well, Project
import folium
from streamlit_folium import folium_static

def load_wells(uploaded_files):
    wells = []
    for uploaded_file in uploaded_files:
        try:
            bytes_data = uploaded_file.read()
            str_io = StringIO(bytes_data.decode('Windows-1252'))
            las = lasio.read(str_io)
            well = Well.from_lasio(las)
            wells.append(well)
        except Exception as e:
            st.error(f"Error processing file {uploaded_file.name}: {e}")
    return wells

def show_well_details(wells):
    st.write(f"Number of wells loaded: {len(wells)}")
    for well in wells:
        st.write(f"Well: {well.name}")
        st.write(f"Curves: {list(well.data.keys())}")

def plot_gr_curves(wells):
    fig, axs = plt.subplots(figsize=(14, 10), ncols=len(wells))
    for i, (ax, well) in enumerate(zip(axs, wells)):
        gr = well.get_curve('GR')
        if gr is not None:
            gr.plot(ax=ax, c='green')
            ax.set_title(f"GR for\n{well.name}")
    plt.tight_layout()
    st.pyplot(fig)

def plot_rhob_curves(wells):
    fig, axs = plt.subplots(figsize=(14, 10), ncols=len(wells))
    curve_name = 'RHOB'
    for i, (ax, well) in enumerate(zip(axs, wells)):
        rhob = well.get_curve(curve_name)
        if rhob is not None:
            rhob.plot(ax=ax, c='red')
            ax.set_title(f"{curve_name} for\n{well.name}")
    plt.tight_layout()
    st.pyplot(fig)

def show_map(wells):
    map_center = [30.0, 31.0]
    m = folium.Map(location=map_center, zoom_start=5)
    for well in wells:
        loc = well.location
        if loc is not None:
            folium.Marker([loc.latitude, loc.longitude], tooltip=well.name).add_to(m)
    folium_static(m)

def show_page():
    st.title("Welly Multi Well Project")

    uploaded_files = st.file_uploader("Upload LAS files", type=["las"], accept_multiple_files=True)
    if uploaded_files:
        wells = load_wells(uploaded_files)
        st.success(f"{len(wells)} wells loaded successfully")

        display_options = st.multiselect(
            "Select what to display:",
            ["Well Details", "GR Curves", "RHOB Curves", "Well Locations Map"]
        )
        if "Well Details" in display_options:
            show_well_details(wells)

        if "GR Curves" in display_options:
            plot_gr_curves(wells)

        if "RHOB Curves" in display_options:
            plot_rhob_curves(wells)

        if "Well Locations Map" in display_options:
            show_map(wells)

if __name__ == "__main__":
    show_page()
