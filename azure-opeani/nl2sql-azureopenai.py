import os
from openai import AzureOpenAI

class NLToSQL:
    def __init__(self):
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            azure_endpoint = os.getenv("ENDPOINT_URL"),
            api_key = os.getenv("AZURE_OPENAI_API_KEY"),
            api_version = "2024-08-01-preview",
        )
        self.model = os.getenv("DEPLOYMENT_NAME")

    def generate_sql(self, natural_language_query: str, table_schema: str) -> str:
        """
        Convert natural language to SQL using Azure OpenAI.
        
        Args:
            natural_language_query: The natural language question
            table_schema: Description of database schema
        """
        prompt = f"""
        Given the following database schema:
        {table_schema}
        
        Convert this question to SQL:
        {natural_language_query}
        
        Return only the SQL query, nothing else.
        """

        response = self.client.chat.completions.create(
            model=self.model, # or your deployed model name
            messages=[
                {"role": "system", "content": "You are a SQL expert. Generate SQL queries from natural language."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        
        return response.choices[0].message.content.strip()

def main():
    # Example usage
    nl_to_sql = NLToSQL()
    
    # Example schema
    schema = """
    Customers(customer_id, name, email, country)
    Orders(order_id, customer_id, order_date, total_amount)
    """
    
    # Example queries
    queries = [
        "Show me all customers from the USA",
        "What are the total orders per customer in 2023?",
        "I want to know how many transactions in the last 3 months",
        "I want to know how many transactions made by each customer in the last 3 months",
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