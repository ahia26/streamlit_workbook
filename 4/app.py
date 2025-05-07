import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import altair as alt

# Page setup
st.title("COVID-19 Global Stats Dashboard")

# API call
url = "https://disease.sh/v3/covid-19/countries"
response = requests.get(url)
data = response.json()

# Parse JSON to DataFrame
df = pd.json_normalize(data)
df = df[["country", "cases", "todayCases", "deaths", "recovered", "active", "critical"]]
df = df.sort_values("cases", ascending=False).head(10)

st.subheader("Top 10 Countries by Total Cases")
st.dataframe(df)

# 1. Matplotlib bar chart
st.subheader("Bar Chart - Total Cases (Matplotlib)")
fig, ax = plt.subplots()
ax.bar(df["country"], df["cases"], color="orange")
plt.xticks(rotation=45)
st.pyplot(fig)

# 2. Plotly bar chart
st.subheader("Bar Chart - Active Cases (Plotly)")
fig_plotly = px.bar(df, x="country", y="active", color="country", title="Active Cases")
st.plotly_chart(fig_plotly)

# 3. Seaborn heatmap
st.subheader("Heatmap - Cases, Deaths, Recovered (Seaborn)")
fig2, ax2 = plt.subplots()
sns.heatmap(df[["cases", "deaths", "recovered"]], annot=True, fmt="d", cmap="Blues", ax=ax2)
st.pyplot(fig2)

# 4. Altair line chart
st.subheader("Line Chart - Critical Cases (Altair)")
line_chart = alt.Chart(df).mark_line(point=True).encode(
    x="country", y="critical", color="country"
).properties(title="Critical Cases")
st.altair_chart(line_chart, use_container_width=True)

# 5. Plotly pie chart
st.subheader("Pie Chart - Today's Cases Distribution")
fig_pie = px.pie(df, values='todayCases', names='country', title='Today\'s Cases Share')
st.plotly_chart(fig_pie)
