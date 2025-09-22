# Conversational AI for Business Insights (BA Assistant)

**Goal:** Ask natural language questions about KPIs and get tables/charts back.

This starter uses a **lightweight NL→SQL pattern router** over DuckDB (in-process analytics). 
You can swap in LangChain/OpenAI later for full LLM parsing.

## Run
```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```
