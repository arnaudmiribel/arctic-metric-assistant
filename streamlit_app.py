import streamlit as st
import os
import streamlit as st
import json

from messages import Message, detect_backtick_or_double_quote_enclosed_strings, show_metric_result
from metrics import METRICS_METADATA
from arctic import generate_arctic_response

st.set_page_config(
    page_title="Metric Assistant",
    page_icon="📊",
)

PROMPT_METRICS_METADATA = {
    metric.name: metric.description for metric in METRICS_METADATA
}

DEFAULT_ASSISTANT_MESSAGE = """
Hey! I'm your Metric Assistant. Ask me a question and I'll show you a 
related metric. You can also check everything I know from the button above.
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

BLOG_POST_CONTEXT = """
This app is the companion of a [blog post](https://todo) to illustrate 
how one can use Streamlit and Snowflake Arctic to easily set up an 
AI assistant to help your colleagues self-serve metrics they care about.
The data and metrics are all synthetic.
"""

WHAT_DOES_THIS_ASSISTANT_KNOW = f"""
## What does this assistant know?
Here's what the Metric Assistant is given as a starter prompt. It includes 
instructions as well as synthetic metrics metadata:

**Instruction prompt:**

```
{METRIC_ASSISTANT_PROMPT}
```
"""

@st.experimental_dialog("Learn more", width="large")
def learn_more() -> None:
    st.markdown(BLOG_POST_CONTEXT)
    st.markdown(WHAT_DOES_THIS_ASSISTANT_KNOW)

if st.button("Learn more"):
    learn_more()

""" # Metric Assistant """ 

st.caption(""":blue[Powered by **Snowflake Arctic**] ❄️""")


# Make sure to pass a Replicate API Token
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

# Store LLM-generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        Message(role="assistant", content=DEFAULT_ASSISTANT_MESSAGE)
    ]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message.role, avatar=message.avatar):
        st.write(message.content)

        # Give an example button
        if "used_example" not in st.session_state:
            st.session_state["used_example"] = True
            button_placeholder = st.empty()

            def run_example(placeholder):
                placeholder = st.empty()  # Clear the button placeholder
                st.session_state.messages.append(
                    Message(role="user", content="What's our retention rate?")
                ) 

            button_placeholder.button(
                "What's our retention rate?", 
                on_click=lambda: run_example(button_placeholder),
            )
        
        if message.role == "assistant":
            for metric in message.metrics:
                show_metric_result(metric)
            

    
# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    user_message = Message(role="user", content=prompt)
    st.session_state.messages.append(Message(role="user", content=prompt))
    with st.chat_message("user", avatar=user_message.avatar):
        st.write(prompt)

# Generate a new assistant response if last message is from user
if st.session_state.messages[-1].role == "user":
    with st.chat_message("assistant", avatar="📊"):
        response = generate_arctic_response(METRIC_ASSISTANT_PROMPT)
        full_response = st.write_stream(response)

        detected_metrics = detect_backtick_or_double_quote_enclosed_strings(full_response)
        detected_metrics = detect_backtick_or_double_quote_enclosed_strings(full_response)
        matched_metrics = [
            metric for metric in METRICS_METADATA if metric.name in detected_metrics
        ]
        
        for metric in matched_metrics:
            show_metric_result(metric)

    message = Message(role="assistant", content=full_response, metrics=matched_metrics)
    st.session_state.messages.append(message)
