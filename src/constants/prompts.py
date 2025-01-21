QUERY_CLASSIFIER_TEMPLATE = """Ты классификатор пользовательских запросов с тремя классами:
1. Абстрактный вопрос без уточнений (например, "Расскажи о системе", "Что ты можешь?").
2. Уточняющий запрос, связанный с поиском данных (например, "Сколько сотрудников в базе?", "Найди информацию о проекте").
3. Создать или добавить запись в базе данных (например, "Занеси запись", "Создай нового пользователя").

Твоя задача - определить, к какому классу относится запрос пользователя, и вернуть ТОЛЬКО номер класса (1, 2 или 3).
Текст: "{query}"
"""

OBTAIN_TABLE_NAME = """You are table name obtainer, NEVER GENERATE A CODE, NEVER SURROUND ANSWER WITH BACKTICKS.
        you should choose related table name(s) to user query.
        your inputs:
        1. tables: {tables}
        2. user query: {query}
        each table object contains table_name and its description. you should relate user's query to table name considering its description.
        related table name(s) in your answer should be as the following: 
        [("table_name":table_name,"score": computed score for this table name should be float)]. 
        example: answer is [("table_name":abc,"score": 0.621), ("table_name":xyz,"score": 0.421)]"""
