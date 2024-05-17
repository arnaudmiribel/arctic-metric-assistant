from dataclasses import dataclass, field
from typing import Literal
import streamlit as st 

from metrics import Metric 

AVATARS = {"assistant": "📊", "user": "🤔"}

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


def show_metric_result(metric: Metric) -> None:
    """
    Whenever a metric is indentified in the assistant's answer,
    this method is called and will display the metric.

    Args:
        metric (Metric): Metric to show
    """

    with st.expander(f"Metric detected: **📊 {metric.name}**"):
        metric.visualize()