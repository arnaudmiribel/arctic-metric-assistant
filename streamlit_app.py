import streamlit as st
import replicate
import os
from transformers import AutoTokenizer
import streamlit as st
import json

from metrics import METRICS_METADATA

icons = {"assistant": "📊", "user": "🤔"}

st.set_page_config(
    page_title="Metric Assistant",
    page_icon="📊",
)

""" # Metric Assistant 📊 """

PROMPT_METRICS_METADATA = {
    metric.name: metric.description for metric in METRICS_METADATA
}

DEFAULT_ASSISTANT_MESSAGE = """
Hey! I'm your Metric Assistant. Ask me a question and I'll show you a 
relevant metric (if existing). Some examples include "active users", 
"retention rate"... Be creative! You can also check-out everything I 
know from the button above.
"""

METRIC_ASSISTANT_PROMPT = f"""
You are a metric assistant. Building upon the following metrics 
metadata, you are asked to retrieve the most relevant 1 or 2 metrics 
that best answer the questions you get asked from the user.

You should answer the user by quoting the explicit metric name, enclosed with 
backticks so it's easily parsable later, and also don't forget to
explain verbally why the question matches this metric, most likely 
looking at the description.

Metrics metadata: 
{json.dumps(PROMPT_METRICS_METADATA, indent=2)}
"""

WHAT_DOES_THIS_ASSISTANT_KNOW = f"""
Here's what the Metric Assistant is given as a starter prompt. It includes 
instructions as well as synthetic metrics metadata:

### Prompt:

```
{METRIC_ASSISTANT_PROMPT}
```
"""


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
    code_pattern = r'`(.*?)`|"(.*?)"'

    # Find all substrings that match the patterns
    inline_code_substrings = re.findall(code_pattern, text)

    return list(dict.fromkeys(inline_code_substrings))


st.caption("See [blog post](https://todo) · Powered by Snowflake Cortex and Arctic.")


@st.experimental_dialog("What does this assistant know?", width="large")
def what_does_this_assistant_know():
    st.markdown(WHAT_DOES_THIS_ASSISTANT_KNOW)


if st.button("Learn more about what this assistant knows"):
    what_does_this_assistant_know()

st.divider()

if "REPLICATE_API_TOKEN" in st.secrets:
    replicate_api = st.secrets["REPLICATE_API_TOKEN"]
else:
    replicate_api = st.text_input("Enter Replicate API token:", type="password")
    if not (replicate_api.startswith("r8_") and len(replicate_api) == 40):
        st.warning("Please enter your Replicate API token.", icon="⚠️")
        st.markdown(
            "**Don't have an API token?** Head over to [Replicate](https://replicate.com) to sign up for one."
        )

os.environ["REPLICATE_API_TOKEN"] = replicate_api
temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.3, step=0.01)
top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
# temperature = 0.3
# top_p = 0.9

# Store LLM-generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": DEFAULT_ASSISTANT_MESSAGE}
    ]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=icons[message["role"]]):
        st.write(message["content"])


def clear_chat_history():
    st.session_state.messages = [
        {"role": "assistant", "content": DEFAULT_ASSISTANT_MESSAGE}
    ]


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


# Function for generating Snowflake Arctic response
def generate_arctic_response():
    prompt = []
    prompt.append(METRIC_ASSISTANT_PROMPT)
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            prompt.append("<|im_start|>user\n" + dict_message["content"] + "<|im_end|>")
        else:
            prompt.append(
                "<|im_start|>assistant\n" + dict_message["content"] + "<|im_end|>"
            )

    prompt.append("<|im_start|>assistant")
    prompt.append("")
    prompt_str = "\n".join(prompt)

    if get_num_tokens(prompt_str) >= 3072:
        st.error("Conversation length too long. Please keep it under 3072 tokens.")
        st.button(
            "Clear chat history",
            on_click=clear_chat_history,
            key="clear_chat_history",
        )
        st.stop()

    for event in replicate.stream(
        "snowflake/snowflake-arctic-instruct",
        input={
            "prompt": prompt_str,
            "prompt_template": r"{prompt}",
            "temperature": temperature,
            "top_p": top_p,
        },
    ):
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

        detected_metrics = detect_backtick_enclosed_strings(full_response)
        matched_metrics = [
            metric for metric in METRICS_METADATA if metric.name in detected_metrics
        ]
        for metric in matched_metrics:
            with st.expander(f"Metric detected: `{metric.name}`"):
                metric.visualize()

    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
