import streamlit as st
import replicate
import os
from transformers import AutoTokenizer

# Set assistant icon to Snowflake logo
icons = {"assistant": "📊", "user": "🤔"}

# App title
st.set_page_config(page_title="Metric Assistant")

""" # Metric Assistant 📊 """

import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

# Helper function to generate fake data
def generate_fake_data(metric_name, days=30, min_val=10, max_val=100, seed=None):
    if seed is not None:
        np.random.seed(seed)  # Ensure reproducibility
    dates = pd.date_range(end=pd.Timestamp.today(), periods=days).tolist()
    values = np.random.randint(min_val, max_val, size=days)
    return pd.DataFrame({'Date': dates, metric_name: values})

# Visualization functions
def user_enrollment_rate():
    data = generate_fake_data('User Enrollment Rate', seed=1)
    return px.line(data, x='Date', y='User Enrollment Rate')

def course_completion_rate():
    data = generate_fake_data('Course Completion Rate', seed=2)
    return px.bar(data, x='Date', y='Course Completion Rate')

def average_session_duration():
    data = generate_fake_data('Average Session Duration', min_val=50, max_val=300, seed=3)
    return px.scatter(data, x='Date', y='Average Session Duration')

def daily_active_users():
    data = generate_fake_data('Daily Active Users', seed=4)
    return px.area(data, x='Date', y='Daily Active Users')

def retention_rate():
    data = generate_fake_data('Retention Rate', min_val=1, max_val=100, seed=5)
    return px.line(data, x='Date', y='Retention Rate', markers=True)

def net_promoter_score():
    data = generate_fake_data('Net Promoter Score', min_val=-100, max_val=100, seed=6)
    return px.histogram(data, x='Net Promoter Score')

METADATA = [
    {
        'name': 'user_enrollment_rate',
        'description': 'Measures the number of new users enrolling in courses over time.',
        'chart_function': user_enrollment_rate
    },
    {
        'name': 'course_completion_rate',
        'description': 'Shows the percentage of users completing their courses.',
        'chart_function': course_completion_rate
    },
    {
        'name': 'average_session_duration',
        'description': 'Tracks the average time users spend on the platform per session.',
        'chart_function': average_session_duration
    },
    {
        'name': 'daily_active_users',
        'description': 'Counts unique users interacting with the platform daily.',
        'chart_function': daily_active_users
    },
    {
        'name': 'retention_rate',
        'description': 'Percentage of users who return to the platform after their first visit.',
        'chart_function': retention_rate
    },
    {
        'name': 'net_promoter_score',
        'description': 'Measures user satisfaction and the likelihood of recommending the platform to others.',
        'chart_function': net_promoter_score
    }
    # Add additional metrics as needed
]

def detect_backtick_enclosed_strings(text: str) -> list:
    """
    This function finds substrings enclosed between
    backticks (`). Because the LLM is prompted to
    enclose metric names between backticks, this is
    then useful to identify metrics.

    Args:
        text (str): The markdown text to be parsed

    Returns:
        list: A list with unique detected inline code substrings.
    """
    import re

    # Pattern to find substrings between backticks
    code_pattern = r"`(.*?)`"

    # Find all substrings that match the patterns
    inline_code_substrings = re.findall(code_pattern, text)

    return list(dict.fromkeys(inline_code_substrings))

st.caption("See [blog post](https://todo) · Powered by Snowflake Cortex and Arctic.")
st.expander("What does this assistant know?").json(METADATA)
# with st.expander("Lookup all metrics"):
#     for metric in METADATA:
#         st.write(f"**{metric['name'].replace('_', ' ').title()}** - {metric['description']}")
#         st.plotly_chart(metric['chart_function'](), use_container_width=True)


if 'REPLICATE_API_TOKEN' in st.secrets:
    replicate_api = st.secrets['REPLICATE_API_TOKEN']
else:
    replicate_api = st.text_input('Enter Replicate API token:', type='password')
    if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
        st.warning('Please enter your Replicate API token.', icon='⚠️')
        st.markdown("**Don't have an API token?** Head over to [Replicate](https://replicate.com) to sign up for one.")

os.environ['REPLICATE_API_TOKEN'] = replicate_api
# temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.3, step=0.01)
# top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
temperature = 0.3
top_p = 0.9

DEFAULT_ASSISTANT_MESSAGE = """
Hey! I'm your Metric Assistant. Ask me a question and I'll show you a 
relevant metric (if existing). 
"""

# Store LLM-generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": DEFAULT_ASSISTANT_MESSAGE}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=icons[message["role"]]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": DEFAULT_ASSISTANT_MESSAGE}]


@st.cache_resource(show_spinner=False)
def get_tokenizer():
    """Get a tokenizer to make sure we're not sending too much text
    text to the Model. Eventually we will replace this with ArcticTokenizer
    """
    return AutoTokenizer.from_pretrained("huggyllama/llama-7b")

def get_num_tokens(prompt):
    """Get the number of tokens in a given prompt"""
    tokenizer = get_tokenizer()
    tokens = tokenizer.tokenize(prompt)
    return len(tokens)


METRIC_ASSISTANT_PROMPT = f"""
You are a metric assistant. Building upon the following metrics 
metadata, you are asked to retrieve the most relevant 1 or 2 metrics 
that best answer the questions you get asked from the user.

You should answer the user by quoting the explicit metric name, enclosed with 
backticks so it's easily parsable later, and also explain verbally why 
the question matches this metric, most likely looking at the description.

Metrics metadata: {METADATA}
"""

# Function for generating Snowflake Arctic response
def generate_arctic_response():
    prompt = []
    prompt.append(METRIC_ASSISTANT_PROMPT)
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            prompt.append("<|im_start|>user\n" + dict_message["content"] + "<|im_end|>")
        else:
            prompt.append("<|im_start|>assistant\n" + dict_message["content"] + "<|im_end|>")
    
    prompt.append("<|im_start|>assistant")
    prompt.append("")
    prompt_str = "\n".join(prompt)
    
    if get_num_tokens(prompt_str) >= 3072:
        st.error("Conversation length too long. Please keep it under 3072 tokens.")
        st.button('Clear chat history', on_click=clear_chat_history, key="clear_chat_history")
        st.stop()

    for event in replicate.stream("snowflake/snowflake-arctic-instruct",
                           input={"prompt": prompt_str,
                                  "prompt_template": r"{prompt}",
                                  "temperature": temperature,
                                  "top_p": top_p,
                                  }):
        yield str(event)

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🤔"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant", avatar="📊"):
        response = generate_arctic_response()
        full_response = st.write_stream(response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)

    metric_names = detect_backtick_enclosed_strings(full_response)

    metrics = [m for m in METADATA if m["name"] in metric_names]
    for metric in metrics:
        with st.expander(f"Metric detected: `{metric['name']}`"):
            st.plotly_chart(metric["chart_function"]())
