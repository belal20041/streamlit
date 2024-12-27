import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

@st.cache
def load_file(file_path):
    df = pd.read_excel(file_path)
    return df

def hyperbolic_rate_from_cum(Gp, qi, Di, b):
    if b != 1:
        t1 = qi ** (1 - b)
        t2 = Gp * Di * (1 - b) / (qi ** b)
        Qt = (t1 - t2) ** (1 / (1 - b))
    else:
        Qt = qi * np.exp(-(Gp * Di) / qi)
    return Qt

def hyperbolic_cum_from_rate(q, qi, Di, b):
    if b != 1:
        Gp = (qi ** (1 - b)) * (q ** b) / (Di * (1 - b)) - (q ** (1 - b))
    else:
        Gp = (qi / Di) * np.log(qi / q)
    return Gp

def hyperbolic_time_from_rate(q, qi, Di, b):
    return ((qi / q) ** b - 1) / (b * Di)

def plot_data(G_gas, Q_gas, qi_ghy, Di_ghy, b_ghy):
    plt.figure(figsize=(12, 8))
    plt.plot(G_gas, Q_gas, label='Smoothed Gas Production', color='blue', marker='o', linestyle='-', markersize=2)
    plt.plot(G_gas, hyperbolic_rate_from_cum(G_gas, qi_ghy, Di_ghy, b_ghy), label='Hyperbolic Model', color='red', linestyle='--')
    plt.xlabel('Cumulative Gas Production', fontsize=14)
    plt.ylabel('Gas Production Rate', fontsize=14)
    plt.title('Hyperbolic Model Fitting to Smoothed Gas Production', fontsize=16)
    plt.legend()
    plt.grid(which="major", color="#6666", linestyle="-", alpha=0.5)
    plt.grid(which="minor", color="#9999", linestyle="-", alpha=0.1)
    plt.minorticks_on()
    st.pyplot(plt)

def show_page():
    st.title("Hyperbolic Model for Gas Production")
    file = st.file_uploader("Upload the Excel file ('Volve production data.xlsx')", type="xlsx")

    if file:
        df = load_file(file)
        df = df[df['NPD_WELL_BORE_NAME'] == "15/9-F-14"]
        df = df[(df['BORE_GAS_VOL'] > 0) & (df['DATEPRD'] <= '2010-12-31')]
        mean_gas_prod = df['BORE_GAS_VOL'].mean()
        std_gas_prod = df['BORE_GAS_VOL'].std()
        df = df[(df['BORE_GAS_VOL'] > mean_gas_prod - 3 * std_gas_prod) & (df['BORE_GAS_VOL'] < mean_gas_prod + 3 * std_gas_prod)]
        df['smooth_prod'] = df['BORE_GAS_VOL'].rolling(window=10, center=True).mean()
        df = df.dropna(subset=['smooth_prod'])
        df["smooth_cumulative_prod"] = df["smooth_prod"].cumsum()
        df['DATEPRD'] = pd.to_datetime(df['DATEPRD'])
        df["days"] = (df["DATEPRD"] - df["DATEPRD"].min()).dt.days
        T_gas = df["days"]
        Q_gas = df["smooth_prod"]
        G_gas = df["smooth_cumulative_prod"]
        T_normal = T_gas / max(T_gas)
        Q_normal = Q_gas / max(Q_gas)
        G_normal = G_gas / max(G_gas)
        params, covariance = curve_fit(hyperbolic_rate_from_cum, G_normal, Q_normal)
        qi_ghy, Di_ghy, b_ghy = params
        qi_ghy = qi_ghy * max(Q_gas)
        Di_ghy = Di_ghy / max(T_gas)
        st.subheader("Model Parameters")
        st.write(f"Initial gas flow rate (qi): {qi_ghy:.2f}")
        st.write(f"Initial decline rate (Di): {Di_ghy:.6f}")
        st.write(f"Arps' Decline Curve Exponent (b): {b_ghy:.4f}")
        plot_data(G_gas, Q_gas, qi_ghy, Di_ghy, b_ghy)
        q_max = 16500
        time_to = hyperbolic_time_from_rate(q_max, qi_ghy, Di_ghy, b_ghy)
        cumulative_at = hyperbolic_cum_from_rate(q_max, qi_ghy, Di_ghy, b_ghy)
        st.subheader("Prediction Results")
        st.write(f"Time to reach {q_max} MMSCF of gas production per day: {time_to:.2f} days")
        st.write(f"Cumulative production at that time: {cumulative_at:.2f} MMSCF")

if __name__ == "__main__":
    show_page()
