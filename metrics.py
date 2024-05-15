import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st
from dataclasses import dataclass


# Parent dataclass for metrics
@dataclass
class Metric:
    name: str
    description: str
    data: pd.DataFrame
    chart_function: callable

    def visualize(self):
        st.markdown(self.description)
        chart, data = st.tabs(["Chart", "Data"])
        chart.plotly_chart(self.chart_function(self.data), use_container_width=True)
        data.dataframe(self.data, use_container_width=True)


# Helper function to generate fake data
def generate_fake_data(days=30, min_val=10, max_val=100, seed=None):
    if seed is not None:
        np.random.seed(seed)  # Ensure reproducibility
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days).tolist()
    values = np.random.randint(min_val, max_val, size=days)
    return pd.DataFrame({"Date": dates, "Value": values})


# Define visualization functions
def line_chart(data, title):
    return px.line(data, x="Date", y="Value", title=title)


def bar_chart(data, title):
    return px.bar(data, x="Date", y="Value", title=title)


# Define metadata for all metrics and instantiate them
METRICS_METADATA = [
    Metric(
        name="User Enrollment Rate",
        description="Measures the number of new users enrolling in courses over time.",
        data=generate_fake_data(seed=1),
        chart_function=lambda data: line_chart(data, "User Enrollment Rate"),
    ),
    Metric(
        name="Course Completion Rate",
        description="Shows the percentage of users completing their courses.",
        data=generate_fake_data(seed=2),
        chart_function=lambda data: bar_chart(data, "Course Completion Rate"),
    ),
    Metric(
        name="Average Session Duration",
        description="Tracks the average time users spend on the platform per session.",
        data=generate_fake_data(seed=3),
        chart_function=lambda data: line_chart(data, "Average Session Duration"),
    ),
    Metric(
        name="Daily Active Users",
        description="Counts unique users interacting with the platform daily.",
        data=generate_fake_data(seed=4),
        chart_function=lambda data: bar_chart(data, "Daily Active Users"),
    ),
    Metric(
        name="Retention Rate",
        description="Percentage of users who return to the platform after their first visit.",
        data=generate_fake_data(seed=5),
        chart_function=lambda data: line_chart(data, "Retention Rate"),
    ),
    Metric(
        name="Net Promoter Score",
        description="Measures user satisfaction and the likelihood of recommending the platform to others.",
        data=generate_fake_data(seed=6),
        chart_function=lambda data: bar_chart(data, "Net Promoter Score"),
    ),
    Metric(
        name="Revenue",
        description="Total revenue generated over time.",
        data=generate_fake_data(seed=7),
        chart_function=lambda data: line_chart(data, "Revenue"),
    ),
    Metric(
        name="Churn Rate",
        description="Percentage of users who stop using the product over time.",
        data=generate_fake_data(seed=8),
        chart_function=lambda data: line_chart(data, "Churn Rate"),
    ),
    Metric(
        name="Average Revenue per User",
        description="Average revenue generated per user over time.",
        data=generate_fake_data(seed=9),
        chart_function=lambda data: bar_chart(data, "Average Revenue per User"),
    ),
    Metric(
        name="Daily Sessions",
        description="Number of sessions held on the platform daily.",
        data=generate_fake_data(seed=10),
        chart_function=lambda data: line_chart(data, "Daily Sessions"),
    ),
    Metric(
        name="Conversion Rate",
        description="Percentage of users who take a desired action (e.g., make a purchase) over time.",
        data=generate_fake_data(seed=11),
        chart_function=lambda data: line_chart(data, "Conversion Rate"),
    ),
    Metric(
        name="Active Subscriptions",
        description="Number of active subscriptions over time.",
        data=generate_fake_data(seed=12),
        chart_function=lambda data: bar_chart(data, "Active Subscriptions"),
    ),
    Metric(
        name="Customer Lifetime Value",
        description="Predicted revenue a user will generate over their entire time as a customer.",
        data=generate_fake_data(seed=13),
        chart_function=lambda data: line_chart(data, "Customer Lifetime Value"),
    ),
    Metric(
        name="Bounce Rate",
        description="Percentage of users who leave the platform without interacting.",
        data=generate_fake_data(seed=14),
        chart_function=lambda data: line_chart(data, "Bounce Rate"),
    ),
    Metric(
        name="Average Transaction Value",
        description="Average value of transactions made on the platform over time.",
        data=generate_fake_data(seed=15),
        chart_function=lambda data: bar_chart(data, "Average Transaction Value"),
    ),
    Metric(
        name="Engagement Score",
        description="Measure of how engaged users are with the platform.",
        data=generate_fake_data(seed=16),
        chart_function=lambda data: line_chart(data, "Engagement Score"),
    ),
]
