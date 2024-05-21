from dataclasses import dataclass, field
from typing import Literal
import streamlit as st 
import random

from streamlit_pills import pills
from metrics import Metric 

AVATARS = {"assistant": "📊", "user": "👤"}

@dataclass
class Message:
    role: Literal["user", "assistant"]
    content: str
    metrics: list[Metric] = field(default_factory=lambda: [])

    @property
    def avatar(self):
        return AVATARS[self.role]
    

def detect_backtick_or_double_quote_enclosed_strings(text: str) -> list[str]:
    """
    This function finds substrings enclosed between backticks (`) or double quotes (").
    This is useful to identify metrics in Arctic responses.

    Args:
        text (str): The text to be parsed

    Returns:
        list: A list with unique detected inline code substrings.
    """
    import re

    # Pattern to find substrings between backticks or double quotes
    code_pattern = r'`([^`]*)`|"([^"]*)"'

    # Find all substrings that match the patterns
    matches = re.findall(code_pattern, text)

    # Flatten the list of tuples and filter out empty strings
    inline_code_substrings = [match for group in matches for match in group if match]

    # Remove duplicates while preserving order
    return list(dict.fromkeys(inline_code_substrings))


def get_date_ranges():
    from datetime import date, timedelta

    today = date.today()
    
    # Last Month (28 days)
    last_month_start = today - timedelta(days=28)
    last_month_end = today
    
    # Last 3 Months (90 days)
    last_3_months_start = today - timedelta(days=90)
    last_3_months_end = today
    
    # Last 6 Months (180 days)
    last_6_months_start = today - timedelta(days=180)
    last_6_months_end = today
    
    # Year to Date
    year_start = date(today.year, 1, 1)
    year_to_date_start = year_start
    year_to_date_end = today
    
    # All Time (assuming from beginning of current year)
    all_time_start = date(2000, 1, 1)
    all_time_end = today
    
    return {
        "All time": (all_time_start, all_time_end),
        "1M": (last_month_start, last_month_end),
        "3M": (last_3_months_start, last_3_months_end),
        "6M": (last_6_months_start, last_6_months_end),
        "YTD": (year_to_date_start, year_to_date_end),
    }


@st.experimental_fragment
def show_metric_result(metric: Metric) -> None:
    """
    Whenever a metric is indentified in the assistant's answer,
    this method is called and will display the metric.

    Args:
        metric (Metric): Metric to show
    """
    with st.expander(f"**{metric.name}**", expanded=True):
        st.markdown(metric.description)
        date_ranges = get_date_ranges()
        random.seed(42)
        random_num = random.randint(1, 1e9)
        selected_range = pills("Date range", list(date_ranges.keys()), label_visibility="collapsed", key=f"{metric.name}_{random_num}")
        date_from, date_to = date_ranges[selected_range]
        metric.show_tile(date_range=(date_from, date_to))