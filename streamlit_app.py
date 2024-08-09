import random
import streamlit as st
import json

from messages import Message, detect_backtick_or_double_quote_enclosed_strings, show_metric_result
from metrics import METRICS_METADATA
from arctic import generate_arctic_response_using_cortex

st.set_page_config(
    page_title="Metric Assistant",
    page_icon="📊",
)


# Deactivate demo
# if "session" not in st.session_state:
#     session = st.connection("cortex").session()
#     session.sql("use warehouse ARCTIC_HACKATHON;").collect()
#     st.session_state["session"] = session


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

BLOG_POST_URL = "https://www.notion.so/snowflake-corp/Building-a-Metric-Assistant-with-Streamlit-and-Snowflake-Cortex-30946496aa9e4993b37822501a845f70#b72c9d998ebe4a17b8be01d613bd9152"

BLOG_POST_CONTEXT = f"""
This app is the companion of a [blog post]({BLOG_POST_URL}) to illustrate 
how one can use Streamlit and Snowflake Arctic to easily set up an 
AI assistant to help your colleagues self-serve metrics they care about.
The data and metrics are all synthetic.
"""

WHAT_DOES_THIS_ASSISTANT_KNOW = f"""
### What does this assistant know?
Here's what the Metric Assistant is given as a starter prompt. It includes 
instructions as well as synthetic metrics metadata:

**Instruction prompt:**

```
{METRIC_ASSISTANT_PROMPT}
```
"""

@st.experimental_dialog("Learn more", width="large")
def learn_more() -> None:
    st.markdown("## Learn more")
    st.markdown(BLOG_POST_CONTEXT)
    st.markdown(WHAT_DOES_THIS_ASSISTANT_KNOW)

left, right = st.columns((1, 2))

with left:
    with st.popover("Learn more", use_container_width=True):
        st.markdown("## Learn more")
        st.markdown(BLOG_POST_CONTEXT)
        st.markdown(WHAT_DOES_THIS_ASSISTANT_KNOW)

right.button("Clear history",  use_container_width=True, on_click=lambda: st.session_state.clear())


""" # Metric Assistant """ 

st.caption(""":blue[Powered by **Snowflake Arctic**] ❄️""")

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
                placeholder.empty()  # Clear the button placeholder
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
if prompt := st.chat_input():
    user_message = Message(role="user", content=prompt)
    st.session_state.messages.append(Message(role="user", content=prompt))
    with st.chat_message("user", avatar=user_message.avatar):
        st.write(prompt)

# Generate a new assistant response if last message is from user
if st.session_state.messages[-1].role == "user":
    with st.chat_message("assistant", avatar="📊"):

        with st.spinner("Looking at metrics..."):
            # Deactivate demo
            # response = generate_arctic_response_using_cortex(METRIC_ASSISTANT_PROMPT)
            response = f"""Sorry, the LLM was deactivated! I'll just return a random 
            metric: `{METRICS_METADATA[random.randint(1, 8)].name}`. Visit this app's 
            repo to deploy your very own LLM!"""
            st.write(response)
        
        detected_metrics = detect_backtick_or_double_quote_enclosed_strings(response)
        matched_metrics = [
            metric for metric in METRICS_METADATA if metric.name in detected_metrics
        ]
        
        for metric in matched_metrics:
            show_metric_result(metric)

    message = Message(role="assistant", content=response, metrics=matched_metrics)
    st.session_state.messages.append(message)
