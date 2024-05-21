from typing import Generator
import streamlit as st
from transformers import AutoTokenizer
import replicate 


@st.cache_resource(show_spinner=False)
def get_tokenizer() -> AutoTokenizer:
    """Get a tokenizer to make sure we're not sending too much text
    text to the Model. Eventually we will replace this with ArcticTokenizer
    """
    return AutoTokenizer.from_pretrained("huggyllama/llama-7b")


def get_num_tokens(prompt: str) -> int:
    """Get the number of tokens in a given prompt"""
    tokenizer = get_tokenizer()
    tokens = tokenizer.tokenize(prompt)
    return len(tokens)

# Function for generating Snowflake Arctic response
def generate_arctic_response(instruction_prompt:str) -> str:
    return "Go for `Net Promoter Score`"

def generate_arctic_response(instruction_prompt: str) -> Generator[str, None, None]:
    prompt_items = []
    prompt_items.append(instruction_prompt)
    
    for message in st.session_state.messages:
        prompt_items.append(f"<|im_start|>{message.role}\n{message.content}<|im_end|>")

    prompt_items.append("<|im_start|>assistant\n")
    prompt = "\n".join(prompt_items)

    # Limit the prompt to 3072 chars
    if get_num_tokens(prompt) >= 3072:
        st.error("Conversation length too long. Please keep it under 3072 tokens.")
        st.button(
            "Clear chat history",
            on_click=lambda: st.session_state.clear(),
            key="clear_chat_history",
        )
        st.stop()

    # Call Arctic through Replicate
    for event in replicate.stream(
        "snowflake/snowflake-arctic-instruct",
        input={
            "prompt": prompt,
            "prompt_template": r"{prompt}",
            "temperature": 0.3,
            "top_p": 0.9,
        },
    ):
        yield str(event)