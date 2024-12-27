import streamlit as st
import pandas as pd
import lasio
from io import StringIO
import matplotlib.pyplot as plt
from welly import Well, Project

# Function to load and process multiple LAS files
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

# Function to load survey data from CSV file
def load_survey(uploaded_file):
    try:
        return pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error processing survey file {uploaded_file.name}: {e}")
        return None

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
            gr.plot(ax=ax, c='green')
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
            rhob.plot(ax=ax, c='red')
            ax.set_title(f"{curve_name} for\n{well.name}")
    plt.tight_layout()
    st.pyplot(fig)

# Function to display location plots
def show_location_plots(data, survey):
    x_loc = data.location.position[:, 0]
    y_loc = data.location.position[:, 1]
    z_loc = data.location.position[:, 2]

    fig, ax = plt.subplots(figsize=(15, 5))
    ax1 = plt.subplot2grid(shape=(1, 3), loc=(0, 0))
    ax2 = plt.subplot2grid(shape=(1, 3), loc=(0, 1))
    ax3 = plt.subplot2grid(shape=(1, 3), loc=(0, 2))

    ax1.plot(x_loc, y_loc, lw=7)
    ax1.plot(x_loc[0], y_loc[0], marker='s', color='black', ms=8)
    ax1.plot(survey['X-offset'], survey['Y-offset'])
    ax1.plot(x_loc[-1], y_loc[-1], marker='*', color='red', ms=8)
    ax1.set_title('X Location vs Y Location')

    ax2.plot(x_loc, z_loc, lw=7)
    ax2.plot(x_loc[0], z_loc[0], marker='s', color='black', ms=8)
    ax2.plot(survey['X-offset'], survey['TVD'])
    ax2.plot(x_loc[-1], z_loc[-1], marker='*', color='red', ms=8)
    ax2.invert_yaxis()
    ax2.set_title('X Location vs TVD')

    ax3.plot(y_loc, z_loc, lw=7)
    ax3.plot(y_loc[0], z_loc[0], marker='s', color='black', ms=8)
    ax3.plot(survey['Y-offset'], survey['TVD'])
    ax3.plot(y_loc[-1], z_loc[-1], marker='*', color='red', ms=8)
    ax3.invert_yaxis()
    ax3.set_title('Y Location vs TVD')

    plt.tight_layout()
    st.pyplot(fig)

# Function to display 3D plot of well path
def show_3d_plot(data):
    location_data = data.location.trajectory(datum=[589075.56, 5963534.91, 0], elev=False)
    xs = location_data[:, 0]
    ys = location_data[:, 1]
    zs = location_data[:, 2]

    fig = plt.figure(figsize=(8, 8))
    ax = plt.axes(projection='3d')
    ax.plot3D(xs, ys, zs, lw=10)
    ax.set_zlim(3000, 0)
    ax.set_xlabel('X Location')
    ax.set_ylabel('Y Location')
    ax.set_zlabel('TVD')
    plt.ticklabel_format(style='plain')
    st.pyplot(fig)

# Streamlit App to display the page
def show_page():
    st.title("Petroleum Data Analysis")

    # Allow users to upload multiple LAS files
    las_files = st.file_uploader("Upload LAS files", type=["las"], accept_multiple_files=True)
    
    # Allow users to upload a survey CSV file
    survey_file = st.file_uploader("Upload Survey CSV file", type=["csv"])

    display_options = st.multiselect(
        "Select what to display:",
        ["LAS Curves", "Survey Data", "Location Plots", "3D Plot of Well Path"]
    )

    if las_files:
        wells = load_wells(las_files)
        st.success(f"{len(wells)} wells loaded successfully")

        if "LAS Curves" in display_options:
            for well in wells:
                las_df = pd.DataFrame({curve: well.data[curve].values for curve in well.data.keys()})
                st.write(f"LAS Data in DataFrame for {well.name}:")
                st.dataframe(las_df)
                well.plot(extents='curves')

    if survey_file:
        survey = load_survey(survey_file)
        if survey is not None:
            if "Survey Data" in display_options:
                st.write("Survey Data:")
                st.dataframe(survey)

            if "Location Plots" in display_options:
                if las_files:
                    for well in wells:
                        survey_subset = survey[['MD', 'INC', 'AZI']]
                        well.location.add_deviation(survey_subset.values)
                        show_location_plots(well, survey)

            if "3D Plot of Well Path" in display_options:
                if las_files:
                    for well in wells:
                        show_3d_plot(well)

if __name__ == "__main__":
    show_page()
