from langchain.prompts import PromptTemplate
from langchain_ollama.llms import OllamaLLM
from qdrant_client import QdrantClient, models

# Initialize Qdrant client
client = QdrantClient(host="localhost", port=6333)  # Update host and port if needed
collection_name = "table_attributes"
search_result = client.scroll(
    collection_name=collection_name,
    scroll_filter=models.Filter(
        should=[
            models.FieldCondition(
                key="table_id",
                match=models.MatchValue(value=5),
            )
        ]
    ),
)

res_list = []
for item in search_result[0]:
    print("----")
    res_list.append(item.payload)
    print(item.payload)


llama_model = OllamaLLM(model="llama3.1", temperature=0.7)

user_query = "create a chart for users ages?"

template = """you are a widget/chart generator, NO CODE GENERATOR.
Based on the following retrieved information records_list:{context} and user query: {query}
        u should generate a markdown widget in the following format:
       template: 
       ```<Widget>
       (
            recordSours: (
                databaseId:<database id>,
                tableId:<table id>
            )
            
            groupingAttributes:(
                id:<attribute id>
                name:'<attribute name>'
            )
            aggregations:(
                aggregationType:'SUM'
                ), 
                
                id:<attribute id>
                name:'<attribute name>'
            )
        )
        </Widget>
        ```
        
        consider that u should find attribute by label from record_list and use record (id) and (name) fields values to fill the template.
        also, change the parenthesis to curly braces.
        
        example:
        for selected record:
        ('name': 'date', 'label': 'Дата', 'id': 185, 'data_type': 'DATETIME', 'meta': ('useTime': True, 'timemode': 'GLOBAL'), 'table_id': 5, 'table_name': 'users', 'database': 17)
        the output should be:
        ```<Widget>
        (
            recordSours: (
                databaseId: 17,
                tableId: 5
            )

            groupingAttributes:(
                id:185
                name: 'date'
            )
            aggregations:(
                aggregationType:'SUM'
                ),

                id:185
                name: 'date'
            )
        </Widget>
        ```
        """
# prompt = PromptTemplate(
prompt = PromptTemplate(
    template=template,
    input_variables=["context", "query"],
)

chain = prompt | llama_model
response = chain.invoke({"context": res_list, "query": user_query})
print(f"response => {response}")
