# Metric Assistant

This is the repository for the companion app to the [Building a Metric Assistant with Streamlit and Snowflake Cortex](https://medium.com/snowflake/building-a-metric-assistant-with-streamlit-and-snowflake-cortex-5ae3fdf0b017) blog post.

### Demo

The app is hosted on Streamlit Community Cloud at [arctic-metric-assistant.streamlit.app](https://arctic-metric-assistant.streamlit.app) and here's how it looks:
<img width="250px" src="https://github.com/user-attachments/assets/8f736cdf-3c0a-4f18-a2ce-5314ee8f1cb8">

### Use this app

> [!IMPORTANT]  
> This app uses an LLM called Arctic that is powered by Snowflake Cortex. You will need a Snowflake account that has Cortex activated to run this app.

Now...
- Clone this repository
- Set up your Snowflake credentials in a `.streamlit/secrets.toml` file. Read more on [how to connect to Snowflake](https://docs.streamlit.io/develop/tutorials/databases/snowflake#add-connection-parameters-to-your-local-app-secrets).
- Install requirements in the `requirements.txt` file using your preferred python dependency manager (pip, pipenv, ...)
- Run `streamlit run streamlit_app.py` ☘️
   
### Support
Need help? Feel free to [DM me on X!](https://x.com/arnaudmiribel)
