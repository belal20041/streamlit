import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import lasio
from io import StringIO


def load_data(uploaded_file):
    if uploaded_file:
        bytes_data = uploaded_file.read()
        str_io = StringIO(bytes_data.decode('Windows-1252'))
        las_file = lasio.read(str_io)
        well_data = las_file.df()
        well_data['DEPTH'] = well_data.index
        return las_file, well_data
    return None, None


def handle_outliers(well_data, method):
    if method == 'Fillna().mean':
        return well_data.fillna(well_data.mean())
    elif method == 'Dropna()':
        return well_data.dropna()
    elif method == 'Linear Interpolation':
        return well_data.interpolate(method='linear')
    elif method == 'IQR':
        Q1 = well_data.quantile(0.25)
        Q3 = well_data.quantile(0.75)
        IQR = Q3 - Q1
        return well_data[~((well_data < (Q1 - 1.5 * IQR)) | (well_data > (Q3 + 1.5 * IQR))).any(axis=1)]
    return well_data


def plot_scatter(well_data, x_col, y_col):
    if not pd.api.types.is_numeric_dtype(well_data[x_col]) or not pd.api.types.is_numeric_dtype(well_data[y_col]):
        st.error(f"Both {x_col} and {y_col} must be numeric.")
        return

    well_data = well_data.dropna(subset=[x_col, y_col])
    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(x=well_data[x_col], y=well_data[y_col],
                          c=well_data['GR'], vmin=0, vmax=100, cmap='rainbow')
    plt.xlim(-5, 60)
    plt.ylim(3, 1.5)
    plt.xlabel(f"{x_col} (g/cc)")
    plt.ylabel(f"{y_col} (%)")
    plt.colorbar(scatter, label="Gamma Ray (GR) - API")
    st.pyplot(plt)


def plot_subplots(well_data):
    fig, axes = plt.subplots(figsize=(10, 10))
    curve_names = ['Gamma', 'Deep Res', 'Density', 'Neutron']
    ax1 = plt.subplot2grid((1, 3), (0, 0), rowspan=1, colspan=1)
    ax2 = plt.subplot2grid((1, 3), (0, 1), rowspan=1, colspan=1)
    ax3 = plt.subplot2grid((1, 3), (0, 2), rowspan=1, colspan=1)
    ax4 = ax3.twiny()

    ax1.plot(well_data["GR"], well_data["DEPTH"], color="green", lw=0.5)
    ax1.set_xlim(0, 200)
    ax1.spines['top'].set_edgecolor('green')

    ax2.plot(well_data["RDEP"], well_data["DEPTH"], color="red", lw=0.5)
    ax2.set_xlim(0.2, 2000)
    ax2.semilogx()
    ax2.spines['top'].set_edgecolor('red')

    ax3.plot(well_data["DEN"], well_data["DEPTH"], color="red", lw=0.5)
    ax3.set_xlim(1.95, 2.95)
    ax3.spines['top'].set_edgecolor('red')

    ax4.plot(well_data["NEU"], well_data["DEPTH"], color="blue", lw=0.5)
    ax4.set_xlim(45, -15)
    ax4.spines['top'].set_edgecolor('blue')

    for i, ax in enumerate([ax1, ax2, ax3, ax4]):
        ax.set_ylim(4700, 3500)
        ax.xaxis.set_ticks_position("top")
        ax.xaxis.set_label_position("top")
        ax.set_xlabel(curve_names[i])
        if i == 3:
            ax.spines["top"].set_position(("axes", 1.08))
        else:
            ax.grid()

    for ax in [ax2, ax3]:
        plt.setp(ax.get_yticklabels(), visible=False)
    fig.subplots_adjust(wspace=0.05)
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    st.pyplot(fig)


def plot_boxplot(well_data):
    plt.figure(figsize=(10, 6))
    well_data.plot.box(figsize=(10, 6), patch_artist=True, notch=True, grid=True)
    plt.title("Boxplot for Well Logging Data")
    plt.ylabel("Values")
    st.pyplot(plt)


def show_page():
    st.title("Well Logging Analysis")
    uploaded_file = st.file_uploader("Upload a LAS file", type=["las"])
    las_file, well_data = load_data(uploaded_file)

    if las_file:
        display_options = st.multiselect(
            "Select what to display:",
            ["Data Overview", "Boxplot", "Handle Outliers", "Scatter Plot", "Subplots"]
        )

        if "Data Overview" in display_options:
            st.write("### Data Overview")
            st.write(well_data.head())

        if "Boxplot" in display_options:
            st.write("### Boxplot to Identify Outliers")
            plot_boxplot(well_data)

        if "Handle Outliers" in display_options:
            st.write("### Handle Outliers")
            outlier_method = st.selectbox(
                "Choose how to handle outliers",
                ['None', 'Fillna().mean', 'Dropna()', 'Linear Interpolation', 'IQR']
            )
            well_data = handle_outliers(well_data, outlier_method)

        if "Scatter Plot" in display_options:
            st.write("### Scatter Plot")
            selected_columns = st.multiselect("Select Columns", well_data.columns)
            if len(selected_columns) == 2:
                col1, col2 = selected_columns
                plot_scatter(well_data, col1, col2)
            else:
                st.warning("Please select exactly two columns for the scatter plot.")

        if "Subplots" in display_options:
            st.write("### Subplots for Gamma Ray, Resistivity, and Porosity vs Depth")
            plot_subplots(well_data)


if __name__ == "__main__":
    show_page()
