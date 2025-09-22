import streamlit as st
import pandas as pd, duckdb, re, matplotlib.pyplot as plt
from io import StringIO

st.title("Conversational BI Assistant")
st.caption("Ask business questions in natural language. This starter routes to SQL patterns over DuckDB.")

@st.cache_data
def load_df():
    return pd.read_csv("data/business_data.csv", parse_dates=["date"])

df = load_df()
con = duckdb.connect(database=':memory:')
con.register('sales', df)

def nl_to_sql(q: str):
    qs = q.lower().strip()

    # Examples of patterns -> SQL
    if "revenue by month" in qs or re.search(r"revenue.*(per|by).*month", qs):
        return "SELECT date_trunc('month', date) AS month, SUM(revenue) AS revenue FROM sales GROUP BY 1 ORDER BY 1"
    if "top product" in qs or "top products" in qs:
        return "SELECT product, SUM(revenue) AS revenue FROM sales GROUP BY 1 ORDER BY revenue DESC LIMIT 5"
    if "region" in qs and "revenue" in qs:
        return "SELECT region, SUM(revenue) AS revenue FROM sales GROUP BY 1 ORDER BY revenue DESC"
    if ("profit" in qs) and ("region" in qs):
        # approximate profit = revenue - 0.4*revenue - marketing
        return "SELECT region, SUM(revenue - 0.4*revenue - marketing_spend) AS profit FROM sales GROUP BY 1 ORDER BY profit DESC"
    if "churn" in qs and ("trend" in qs or "by month" in qs):
        return "SELECT date_trunc('month', date) AS month, AVG(churn_rate) AS churn FROM sales GROUP BY 1 ORDER BY 1"
    if "marketing efficiency" in qs or "romi" in qs or "roi" in qs:
        return "SELECT date_trunc('month', date) AS month, SUM(revenue)/NULLIF(SUM(marketing_spend),0) AS romi FROM sales GROUP BY 1 ORDER BY 1"
    if "q" in qs and "revenue" in qs:
        # quarterly revenue
        return "SELECT date_trunc('quarter', date) AS quarter, SUM(revenue) AS revenue FROM sales GROUP BY 1 ORDER BY 1"
    if "show me data" in qs or "raw" in qs:
        return "SELECT * FROM sales LIMIT 200"
    return None

prompt = st.text_input("Ask a question (e.g., 'Revenue by month', 'Top products', 'Churn trend by month', 'Revenue by region')")

if prompt:
    sql = nl_to_sql(prompt)
    if sql is None:
        st.warning("I don't have a pattern for that yet. Try: 'revenue by month', 'top products', 'churn trend by month', 'marketing efficiency'.")
    else:
        st.code(sql, language="sql")
        result = con.execute(sql).df()
        st.dataframe(result)

        # Simple chart if monthly/quarterly series
        if "month" in result.columns or "quarter" in result.columns:
            xcol = "month" if "month" in result.columns else "quarter"
            ycols = [c for c in result.columns if c not in [xcol]]
            if len(ycols)==1:
                fig = plt.figure()
                plt.plot(result[xcol], result[ycols[0]])
                plt.xlabel(xcol.capitalize()); plt.ylabel(ycols[0].replace("_"," ").capitalize())
                plt.title(f"{ycols[0].replace('_',' ').capitalize()} by {xcol.capitalize()}")
                st.pyplot(fig)

st.subheader("Examples")
st.write("- Revenue by month")
st.write("- Top products")
st.write("- Revenue by region")
st.write("- Churn trend by month")
st.write("- Marketing efficiency")
