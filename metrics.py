import pandas as pd
import numpy as np
# import plotly.express as px
import streamlit as st
import altair as alt
from dataclasses import dataclass
from datetime import date

HEIGHT = 200

# Parent dataclass for metrics
@dataclass
class Metric:
    name: str
    description: str
    data: pd.DataFrame
    chart_function: callable

    def show_tile(self, date_range: list[date, date] | None = None):

        # If a date range is passed, slice the data
        if date_range is not None:
            date_from, date_to = date_range
            data = self.data.set_index("Date").sort_index().loc[date_from:date_to].reset_index()
        else:
            data = self.data
        
        # Construct the tile with two tabs
        chart_tab, data_tab = st.tabs(["Chart", "Data"])
        chart_tab.altair_chart(
            self.chart_function(data), 
            use_container_width=True,
        )
        data_tab.dataframe(data, use_container_width=True, height=HEIGHT, hide_index=True,)




# Helper function to generate fake data
def generate_fake_data(days=180, min_val=10, max_val=100, seed=None):
    if seed is not None:
        np.random.seed(seed)  # Ensure reproducibility
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days).tolist()
    values = np.random.randint(min_val, max_val, size=days)
    data = pd.DataFrame({"Date": dates, "Value": values}).sort_values(by="Date", ascending=False)
    data["Date"] = pd.to_datetime(data["Date"]).dt.date
    data["Value"] = data["Value"].rolling(7).mean()
    return data.dropna(subset="Value")


# Define visualization functions
def line_chart(data: pd.DataFrame) -> alt.Chart:
    return alt.Chart(
        data=data, 
        height=HEIGHT,
    ).mark_line(
        point=True
    ).encode(
        x=alt.X("yearmonthdate(Date)", title="Date"), 
        y=alt.Y("Value", title="", scale=alt.Scale(domain=[data.Value.min(), data.Value.max()]))
    )


def bar_chart(data: pd.DataFrame) -> alt.Chart:
    return alt.Chart(
        data=data, 
        height=HEIGHT,
    ).mark_bar(
        point=True
    ).encode(
        x=alt.X("yearmonthdate(Date)"), 
        y="Value",
    )
    # return px.bar(
    #     data, 
    #     x="Date", 
    #     y="Value", 
    #     height=HEIGHT,
    #     # title=title
    # )


# Define metadata for all metrics and instantiate them
METRICS_METADATA = [
    Metric(
        name="User Enrollment Rate",
        description="Measures the number of new users enrolling in courses over time.",
        data=generate_fake_data(seed=1),
        chart_function=line_chart,
    ),
    Metric(
        name="Course Completion Rate",
        description="Shows the percentage of users completing their courses.",
        data=generate_fake_data(seed=2),
        chart_function=bar_chart,
    ),
    Metric(
        name="Average Session Duration",
        description="Tracks the average time users spend on the platform per session.",
        data=generate_fake_data(seed=3),
        chart_function=line_chart,
    ),
    Metric(
        name="Daily Active Users",
        description="Counts unique users interacting with the platform daily.",
        data=generate_fake_data(seed=4),
        chart_function=bar_chart,
    ),
    Metric(
        name="Retention Rate",
        description="Percentage of users who return to the platform after their first visit.",
        data=generate_fake_data(seed=5),
        chart_function=line_chart,
    ),
    Metric(
        name="Net Promoter Score",
        description="Measures user satisfaction and the likelihood of recommending the platform to others.",
        data=generate_fake_data(seed=6),
        chart_function=bar_chart,
    ),
    Metric(
        name="Revenue",
        description="Total revenue generated over time.",
        data=generate_fake_data(seed=7),
        chart_function=line_chart,
    ),
    Metric(
        name="Churn Rate",
        description="Percentage of users who stop using the product over time.",
        data=generate_fake_data(seed=8),
        chart_function=bar_chart,
    ),
    Metric(
        name="Average Revenue per User",
        description="Average revenue generated per user over time.",
        data=generate_fake_data(seed=9),
        chart_function=bar_chart,
    ),
    Metric(
        name="Daily Sessions",
        description="Number of sessions held on the platform daily.",
        data=generate_fake_data(seed=10),
        chart_function=bar_chart,
    ),
    Metric(
        name="Conversion Rate",
        description="Percentage of users who take a desired action (e.g., make a purchase) over time.",
        data=generate_fake_data(seed=11),
        chart_function=line_chart,
    ),
    Metric(
        name="Active Subscriptions",
        description="Number of active subscriptions over time.",
        data=generate_fake_data(seed=12),
        chart_function=bar_chart,
    ),
    Metric(
        name="Customer Lifetime Value",
        description="Predicted revenue a user will generate over their entire time as a customer.",
        data=generate_fake_data(seed=13),
        chart_function=line_chart,
    ),
    Metric(
        name="Bounce Rate",
        description="Percentage of users who leave the platform without interacting.",
        data=generate_fake_data(seed=14),
        chart_function=line_chart,
    ),
    Metric(
        name="Average Transaction Value",
        description="Average value of transactions made on the platform over time.",
        data=generate_fake_data(seed=15),
        chart_function=bar_chart,
    ),
    Metric(
        name="Engagement Score",
        description="Measure of how engaged users are with the platform.",
        data=generate_fake_data(seed=16),
        chart_function=line_chart,
    ),
]
