import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

@st.cache
def load_data(file_path):
    df = pd.read_excel(file_path)
    return df

def plot_data(T, Q, q_model, model_label, color):
    plt.figure(figsize=(8, 6))
    plt.plot(T, Q, label="Smoothed Data", color="green")
    plt.plot(T, q_model, label=model_label, color=color)
    plt.legend()
    plt.grid(True)
    plt.title(f"{model_label} Model")
    plt.xlabel("Days")
    plt.ylabel("Smoothed Oil Production")
    st.pyplot(plt)

def exponential(t, qi, di):
    return qi * np.exp(-di * t)

def harmonic(t, qi, di):
    return qi / (1 + di * t)

def hyperbolic(t, qi, di, b):
    return qi / np.abs((1 + b * di * t)) ** (1 / b)

def show_page():
    st.title("Decline Curve Analysis (DCA)")

    file = st.file_uploader("Upload an Excel File", type="xlsx")

    if file:
        df_original = load_data(file)
        df_original = df_original[df_original['NPD_WELL_BORE_NAME'] == "15/9-F-14"]
        df_original = df_original[df_original['BORE_OIL_VOL'] != 0]
        df_original['days'] = (df_original['DATEPRD'] - df_original['DATEPRD'].min()).dt.days

        window_size = st.slider("Select Rolling Mean Window Size", min_value=50, max_value=300, step=10, value=150)
        df_original['smoothed_oil_prod'] = df_original['BORE_OIL_VOL'].rolling(window=window_size, center=True).mean()
        df_original = df_original.dropna(subset=['smoothed_oil_prod'])
        df_original = df_original[np.isfinite(df_original['smoothed_oil_prod'])]

        st.subheader("Smoothed Oil Production")
        plt.figure(figsize=(6, 6))
        plt.plot(df_original['DATEPRD'], df_original['BORE_OIL_VOL'], label="Active Production", color='blue', alpha=0.6)
        plt.plot(df_original['DATEPRD'], df_original['smoothed_oil_prod'], label=f"Smoothed Production ({window_size}-day avg)", color='red', linestyle='--')
        plt.xlabel("Date")
        plt.ylabel("BORE_OIL_VOL")
        plt.xticks(rotation=45)
        plt.legend()
        st.pyplot(plt)

        model_option = st.selectbox("Select Decline Curve Model", ["Exponential", "Harmonic", "Hyperbolic"])

        T = df_original['days']
        Q = df_original['smoothed_oil_prod']
        T_norm = T / max(T)
        Q_norm = Q / max(Q)

        if np.any(np.isnan(T_norm)) or np.any(np.isnan(Q_norm)) or np.any(np.isinf(T_norm)) or np.any(np.isinf(Q_norm)):
            st.error("Data contains NaN or Inf values, which are not allowed for curve fitting.")
        else:
            if model_option == "Exponential":
                st.subheader("Exponential Model")
                params, _ = curve_fit(exponential, T_norm, Q_norm)
                qi, di = params
                qi = qi * max(Q)
                di = di / max(T)
                q_exp = exponential(T, qi, di)
                plot_data(T, Q, q_exp, "Exponential", "blue")
                st.write(f"Exponential Model Parameters: qi = {qi:.2f}, di = {di:.4f}")

            elif model_option == "Harmonic":
                st.subheader("Harmonic Model")
                params, _ = curve_fit(harmonic, T_norm, Q_norm)
                qi, di = params
                qi = qi * max(Q)
                di = di / max(T)
                q_harmonic = harmonic(T, qi, di)
                plot_data(T, Q, q_harmonic, "Harmonic", "orange")
                st.write(f"Harmonic Model Parameters: qi = {qi:.2f}, di = {di:.4f}")

            elif model_option == "Hyperbolic":
                st.subheader("Hyperbolic Model")
                params, _ = curve_fit(hyperbolic, T_norm, Q_norm)
                qi, di, b = params
                qi = qi * max(Q)
                di = di / max(T)
                q_hp = hyperbolic(T, qi, di, b)
                plot_data(T, Q, q_hp, "Hyperbolic", "red")
                st.write(f"Hyperbolic Model Parameters: qi = {qi:.2f}, di = {di:.4f}, b = {b:.4f}")

if __name__ == "__main__":
    show_page()
