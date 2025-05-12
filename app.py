import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Agg")
plt.style.use('dark_background')

st.set_page_config(page_title="Live Drilling Dashboard", layout="wide", page_icon="\U0001F6E0", initial_sidebar_state="expanded")
st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: #c7c7c7;
    }
    .stApp {
        background-color: #0e1117;
    }
    .st-bf {
        color: #c7c7c7;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛠️ Real-Time Drilling Dashboard")

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

step = st.slider("Live Scroll Range (Last N Records)", min_value=5, max_value=len(df), value=10, step=1)

st.subheader("📊 Sensor Time Series")
selected_metric = st.selectbox("Select metric to visualize", sensor_columns)

fig, ax = plt.subplots(figsize=(14, 4))
latest_data = df.tail(step)
ax.plot(latest_data.index, latest_data[selected_metric], marker='o', color='cyan')
ax.set_title(f"{selected_metric} Over Time", fontsize=14)
ax.set_xlabel("Timestamp")
ax.set_ylabel(selected_metric)
st.pyplot(fig)

with st.expander("📊 Summary Statistics"):
    st.dataframe(df[sensor_columns].describe())

with st.expander("🔗 Correlation Matrix"):
    st.dataframe(df[sensor_columns].corr())

if st.button("🔮 Show Summary Insights & Alerts"):
    def generate_alerts(row):
        alerts = []
        if row['Rate Of Penetration (ft_per_hr)'] == 0 and row['Weight on Bit (klbs)'] > 140 and row['Rotary RPM (RPM)'] > 40:
            alerts.append("🚨 Bit stall detected")
        if row['Flow (flow_percent)'] < 10 and row['Standpipe Pressure (psi)'] < 100:
            alerts.append("⚠️ Possible circulation loss")
        if row['Differential Pressure (psi)'] > 600:
            alerts.append("⚡ High differential pressure")
        return "; ".join(alerts)

    df['Alerts'] = df.apply(generate_alerts, axis=1)
    summary_alerts = df[df['Alerts'] != ""][['Alerts']]

    if not summary_alerts.empty:
        st.markdown("### 📢 Operational Summary Alerts")
        for alert in summary_alerts['Alerts'].tail(10):
            st.error(alert)
    else:
        st.success("✅ No major issues detected in the current drilling interval.")