from uuid import uuid4


def test_query_returns_greeting_for_supplied_person(graphql_api):
    person = {"name": f"Студент {uuid4().hex}", "age": 20}
    response = graphql_api(json={
        "query": "query Hello($person: PersonInput!) { hello(person: $person) }",
        "variables": {"person": person},
    })
    assert response.status_code == 200
    result = response.json()
    assert not result.get("errors"), "GraphQL query вернул errors; подробности в логе"
    assert isinstance(result.get("data"), dict)
    assert result["data"]["hello"] == f"Hello {person['name']}"


def test_mutation_creates_person_with_expected_fields(graphql_api):
    person = {"name": f"Lab 2 {uuid4().hex}", "age": 25}
    response = graphql_api(json={
        "query": """
            mutation CreatePerson($person: PersonInput!) {
                createPerson(person: $person) { id name age }
            }
        """,
        "variables": {"person": person},
    })
    assert response.status_code == 200
    result = response.json()
    assert not result.get("errors"), "GraphQL mutation вернул errors; подробности в логе"
    assert isinstance(result.get("data"), dict)
    created = result["data"]["createPerson"]
    assert isinstance(created["id"], str) and created["id"].strip()
    assert created["name"] == person["name"]
    assert created["age"] == person["age"]
