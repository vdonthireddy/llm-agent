# If you are using neo4j example to create a knowledge graph, 
# please use the following command to start neo4j in docker
docker run --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/VjD0nP@s3w0rd \
    -e NEO4J_PLUGINS='["graph-data-science"]' \
    neo4j:latest

conda deactivate
conda activate llm-agents
streamlit run azure-opeani/nl2sql-azureopenai-llamaindex.py