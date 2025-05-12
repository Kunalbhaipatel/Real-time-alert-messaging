import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Drilling Dashboard", layout="wide")
st.title("🛠️ Drilling Sensor Dashboard with Visual Insights + Real-Time Alerts")

uploaded_file = st.file_uploader("Upload drilling sensor CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    st.info("Using sample data.")
    df = pd.read_csv("sample_data.csv")

df['Timestamp'] = pd.to_datetime(df['YYYY/MM/DD'] + ' ' + df['HH:MM:SS'])
df.set_index('Timestamp', inplace=True)
df.sort_index(inplace=True)

sensor_columns = [
    'Rate Of Penetration (ft_per_hr)', 'Weight on Bit (klbs)',
    'Rotary RPM (RPM)', 'Standpipe Pressure (psi)',
    'Hook Load (klbs)', 'Flow (flow_percent)',
    'Differential Pressure (psi)'
]

def generate_alerts(row):
    alerts = []
    if row['Rate Of Penetration (ft_per_hr)'] == 0 and row['Weight on Bit (klbs)'] > 140 and row['Rotary RPM (RPM)'] > 40:
        alerts.append("🛑 Possible bit stall: ROP = 0, WOB > 140 klbs, RPM > 40")
    if row['Flow (flow_percent)'] < 10 and row['Standpipe Pressure (psi)'] < 100:
        alerts.append("⚠️ Circulation loss suspected: low flow and SPP")
    if row['Differential Pressure (psi)'] > 600:
        alerts.append("🚨 High differential pressure: check for plugging or restriction")
    return "; ".join(alerts)

df['Alert Messages'] = df.apply(generate_alerts, axis=1)

st.subheader("🚨 Live Alert Feed")
recent_alerts = df[df['Alert Messages'] != ""][['Alert Messages']].tail(10)
if not recent_alerts.empty:
    for alert in recent_alerts['Alert Messages']:
        st.warning(alert)
else:
    st.success("✅ No active alerts based on current data.")

st.subheader("📊 Time Series Plots")
selected_metric = st.selectbox("Select metric to plot", sensor_columns)
fig, ax = plt.subplots(figsize=(14, 4))
ax.plot(df.index, df[selected_metric], label=selected_metric)
ax.set_title(f"{selected_metric} Over Time")
ax.set_xlabel("Timestamp")
ax.set_ylabel(selected_metric)
st.pyplot(fig)

st.subheader("🧮 Summary Statistics")
st.write(df[sensor_columns].describe())

st.subheader("📈 Correlation Heatmap")
st.write(df[sensor_columns].corr())