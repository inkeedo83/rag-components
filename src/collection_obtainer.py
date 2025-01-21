from dataclasses import dataclass
from enum import Enum
from re import findall
from typing import List

from langchain.prompts import PromptTemplate
from langchain_ollama.llms import OllamaLLM
from sentence_transformers import SentenceTransformer, util

from constants.prompts import OBTAIN_TABLE_NAME


@dataclass
class FoundTableName:
    table_name: str
    score: float


class IntersectionBy(Enum):
    TABLE_NAME = "TABLE_NAME"
    SCORE = "SCORE"
    BOTH = "BOTH"


def find_similar_table_name(tables: list[dict], user_query: str, threshold=0.5):
    model = SentenceTransformer(
        "all-MiniLM-L6-v2",
    )
    # model = SentenceTransformer("all-mpnet-base-v2")

    texts = [
        f"{table['table_name']} {table['table_name']}: {table['description']}"
        for table in tables
    ]
    print(f"texts => {texts}")

    tables_embeddings = model.encode(sentences=texts, convert_to_tensor=True)

    query_embedding = model.encode(sentences=user_query, convert_to_tensor=True)

    similarities = util.cos_sim(query_embedding, tables_embeddings)

    results: list[FoundTableName] = []
    for i, score in enumerate(similarities[0]):
        print(f"score => {score}, collection_name => {tables[i]['table_name']}")
        if score >= threshold:
            results.append(
                FoundTableName(table_name=tables[i]["table_name"], score=score.item())
            )

    print(f"similarity results =>> {results}")
    return results


def text_to_found_table_names(text: str) -> List[FoundTableName]:
    # TODO: sometime not working, need to fix
    # pattern = r'\(\s*"table_name":\s*(\w+)\s*,\s*"score":\s*([\d.]+)\s*\)'
    # pattern = r'"table_name":\s*"([^"]+)"\s*,\s*"score":\s*([\d.]+)'
    pattern = r'"table_name":\s*["\']([^"\']+)["\']\s*,\s*"score":\s*([\d.]+)'
    matches = findall(pattern, text)
    print(f"matches => {matches}")
    return [
        FoundTableName(table_name=match[0], score=float(match[1])) for match in matches
    ]


def table_name_obtainer(
    tables: list[dict],
    user_query: str,
):
    model = OllamaLLM(model="llama3.1", temperature=0.7)
    # TODO fix prompt
    template = OBTAIN_TABLE_NAME

    prompt = PromptTemplate(
        template=template,
        input_variables=["tables", "query"],
    )
    chain = prompt | model

    response = chain.invoke({"tables": tables, "query": user_query})

    print(f"response =>> {response}")

    result = text_to_found_table_names(response)

    print(f"result =>> {result}")
    return result


def intersectionFounds(
    list1: List[FoundTableName],
    list2: List[FoundTableName],
    intersectionBy: IntersectionBy,
) -> List[FoundTableName]:
    if not list1 and not list2:
        return []
    if not list1:
        return list2
    elif not list2:
        return list1

    dict1 = {item.table_name: item for item in list1}
    dict2 = {item.table_name: item for item in list2}

    # Highest by score intersections (by table_name)
    if intersectionBy == IntersectionBy.SCORE:
        result = []
        for table_name in dict1.keys() & dict2.keys():
            result.append(
                max(dict1[table_name], dict2[table_name], key=lambda x: x.score)
            )
        return sorted(result, key=lambda x: x.score, reverse=True)

    # Only table_name intersections
    elif intersectionBy == IntersectionBy.TABLE_NAME:
        intersection_table_names = dict1.keys() & dict2.keys()
        return sorted(
            (dict1[table_name] for table_name in intersection_table_names),
            key=lambda x: x.table_name,
        )

    # Highest score sorted, resolving duplicates
    elif intersectionBy == IntersectionBy.BOTH:
        combined_dict = {}
        for item in list1 + list2:
            if (
                item.table_name not in combined_dict
                or item.score > combined_dict[item.table_name].score
            ):
                combined_dict[item.table_name] = item
        return sorted(combined_dict.values(), key=lambda x: x.score, reverse=True)

    else:
        raise ValueError(
            "Invalid intersectionBy value. Choose TABLE_NAME, SCORE, or BOTH."
        )


def test(user_query: str):
    tables_sample = [
        {
            "table_name": "users",
            "description": "users profiles, including email, age, phone number and address",
        },
        {
            "table_name": "employees",
            "description": "this table contains info about employees, including their name, position ,salary and department",
        },
        {
            "table_name": "projects",
            "description": "this table contains info about projects' details and employees working on them",
        },
    ]
    list1 = find_similar_table_name(
        tables=tables_sample, user_query=user_query, threshold=0.1
    )
    list2 = table_name_obtainer(tables=tables_sample, user_query=user_query)
    result = intersectionFounds(list1, list2, intersectionBy=IntersectionBy.SCORE)
    print(f"intersection =>> {result}")


test("what is the project A start date?")
print("--------------------------------------")
test("how old is Tom?")
