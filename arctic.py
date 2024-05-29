import streamlit as st
from snowflake.cortex import Complete


def generate_arctic_response_using_cortex(instruction_prompt: str) -> str:
    # Construct prompt
    prompt_items = []
    prompt_items.append(instruction_prompt)

    for message in st.session_state.messages:
        prompt_items.append(f"<|im_start|>{message.role}\n{message.content}<|im_end|>")

    prompt_items.append("<|im_start|>assistant\n")
    prompt = "\n".join(prompt_items)

    return Complete(
        prompt=prompt,
        session=st.session_state.session,
        model="snowflake-arctic",
    )