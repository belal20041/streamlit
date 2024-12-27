import streamlit as st
import pandas as pd
import lasio
from io import StringIO
import matplotlib.pyplot as plt
from welly import Well, Project


def load_data(file_path):
    return Well.from_las(file_path)


def load_survey(file_path):
    return pd.read_csv(file_path)


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


def show_page():
    st.title("Petroleum Data Analysis")

    las_file_path = st.text_input("Enter the path to your LAS file")
    survey_file_path = st.text_input("Enter the path to your Survey CSV file")

    display_options = st.multiselect(
        "Select what to display:",
        ["LAS Curves", "Survey Data", "Location Plots", "3D Plot of Well Path"]
    )

    if las_file_path:
        data = load_data(las_file_path)
        if "LAS Curves" in display_options:
            las_df = pd.DataFrame({curve: data.data[curve].values for curve in data.data.keys()})
            st.write("LAS Data in DataFrame:")
            st.dataframe(las_df)
            data.plot(extents='curves')

    if survey_file_path:
        survey = load_survey(survey_file_path)
        if "Survey Data" in display_options:
            st.write("Survey Data:")
            st.dataframe(survey)

        if "Location Plots" in display_options:
            survey_subset = survey[['MD', 'INC', 'AZI']]
            data.location.add_deviation(survey_subset.values)
            show_location_plots(data, survey)

        if "3D Plot of Well Path" in display_options:
            show_3d_plot(data)


if __name__ == "__main__":
    show_page()
