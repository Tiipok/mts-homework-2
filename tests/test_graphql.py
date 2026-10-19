from uuid import uuid4


def test_query_returns_greeting_for_supplied_person(graphql_api):
    # Arrange: данные человека для приветствия
    person = {"name": f"Студент {uuid4().hex}", "age": 20}

    # Act: отправляем query
    response = graphql_api(json={
        "query": "query Hello($person: PersonInput!) { hello(person: $person) }",
        "variables": {"person": person},
    })

    # Assert: приветствие правильное, ошибок нет
    assert response.status_code == 200
    result = response.json()
    assert not result.get("errors"), "GraphQL query вернул errors; подробности в логе"
    assert isinstance(result.get("data"), dict)
    assert result["data"]["hello"] == f"Hello {person['name']}"


def test_mutation_creates_person_with_expected_fields(graphql_api):
    # Arrange: данные человека, которого будем создавать
    person = {"name": f"Lab 2 {uuid4().hex}", "age": 25}

    # Act: отправляем mutation
    response = graphql_api(json={
        "query": """
            mutation CreatePerson($person: PersonInput!) {
                createPerson(person: $person) { id name age }
            }
        """,
        "variables": {"person": person},
    })

    # Assert: получили id, имя и возраст совпадают с отправленными
    assert response.status_code == 200
    result = response.json()
    assert not result.get("errors"), "GraphQL mutation вернул errors; подробности в логе"
    assert isinstance(result.get("data"), dict)
    created = result["data"]["createPerson"]
    assert isinstance(created["id"], str) and created["id"].strip()
    assert created["name"] == person["name"]
    assert created["age"] == person["age"]
