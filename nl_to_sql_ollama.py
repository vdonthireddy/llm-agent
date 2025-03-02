import requests

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
        prompt = f"""You are a SQL expert. Generate SQL queries from natural language. 
        Please return as many as columns as possible. If you use "group by", please use all the required 
        columns from the "select" clause. use name columns instead of id columns.

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
    
    # Example queries
    queries = [
        "Show me all customers from the USA",
        "What are the total orders per customer in 2023?"
    ]
    
    for query in queries:
        try:
            sql = nl_to_sql.generate_sql(query, schema)
            print(f"\nNatural Language: {query}")
            print(f"SQL: {sql}")
        except Exception as e:
            print(f"Error processing query: {e}")

if __name__ == "__main__":
    main()