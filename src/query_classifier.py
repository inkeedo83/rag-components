from re import MULTILINE, search

from langchain.prompts import PromptTemplate
from langchain_ollama.llms import OllamaLLM

from constants.prompts import QUERY_CLASSIFIER_TEMPLATE


def query_classifier(model: OllamaLLM, query: str) -> int:
    prompt = PromptTemplate(
        template=QUERY_CLASSIFIER_TEMPLATE,
        input_variables=["query"],
    )

    chain = prompt | model

    answer = chain.invoke({"query": query})
    match = search(r"\d+", answer, MULTILINE)

    if not match:
        return 0
    else:
        result = match.group()
        return int(result)


def test(user_query: str):
    model = OllamaLLM(
        model="llama3.1",
        temperature=0.7,
    )
    result = query_classifier(model=model, query=user_query)
    print(f"result: {result}")


test("сколько сотрудников в компании?")
