import requests
import streamlit as st

# Title
st.set_page_config(page_title="English questions to SQL query")
st.title("NL 2 SQL Converter!")

class NLToSQLOllama:
    def __init__(self, model_name="llama3.1:8b", host="http://localhost:11434"):
        self.model_name = model_name
        self.host = host
        self.api_endpoint = f"{host}/api/generate"

    def generate_sql(self, natural_language_query: str, table_schema: str) -> str:
        """
        Convert natural language to SQL using Ollama.
        
        Args:
            natural_language_query: The natural language question
            table_schema: Description of database schema
        """
        prompt = f"""
        You are an SQL expert expert in converting English questions to SQL query!
        The SQL database has the name MOVIE and has the following columns 
        - Name, Revenue, Year, Universe
        
        For example,
        Example 1 - Show me all customers from the USA?, 
        the SQL command will be something like this SELECT * FROM ORDERS WHERE country="USA" ;
        
        Example 2 - What are the total orders per customer in 2023?, 
        the SQL command will be something like this SELECT C.CUSTOMER_ID, SUM(ORDER_ID) FROM ORDERS O JOIN CUSTOMERS C ON O.CUSTOMER_ID=C.CUSTOMER_ID
        where year=(EXTRACT(YEAR FROM O.ORDER_DATE)) group by C.CUSTOMER_ID; 
        
        also the sql code should not have ``` in beginning or end 
        and sql word in output.

        Please return as many as columns as possible. If you use "group by", please use all the required 
        columns from the "select" clause and also make sure the group by columns are added to "select" clause as well. 
        Please use name columns instead of id columns.

        Given the following database schema:
        {table_schema}

        Convert this question to SQL:
        {natural_language_query}

        Return only the SQL query, nothing else."""

        response = requests.post(
            self.api_endpoint,
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            return response.json()['response'].strip()
        else:
            raise Exception(f"API call failed with status code: {response.status_code}")

def main():
    # Example usage
    nl_to_sql = NLToSQLOllama(model_name="llama3.1:8b")  # or specify your model name
    
    # Example schema
    schema = """
    Customers(customer_id, name, email, country)
    Orders(order_id, customer_id, order_date, total_amount)
    """
    
    st.write("Sample Questions:")
    st.markdown("- Show me all customers from the USA")
    st.markdown("- What are the total orders per customer in 2023?")
    
    st.header("Meta llama3.1 App To Retrieve SQL Data")
    question=st.text_input("Input: ", key="input")
    submit=st.button("Ask the question")
    if submit:
        sql = nl_to_sql.generate_sql(question, schema)
        st.success(f"SQL: {sql}")

    # for query in queries:
    #     try:
    #         sql = nl_to_sql.generate_sql(query, schema)
    #         st.info(f"\nNatural Language: {query}")
    #         st.success(f"SQL: {sql}")
    #     except Exception as e:
    #         st.error(f"Error processing query: {e}")

if __name__ == "__main__":
    main()