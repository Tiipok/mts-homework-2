from uuid import uuid4


def test_create_patch_get_post(rest_api):
    original = {
        "title": f"Lab 2: {uuid4().hex}",
        "body": "Это поле должно сохраниться после изменения заголовка.",
    }
    response = rest_api("POST", "/posts", json=original)
    assert response.status_code == 201
    created = response.json()
    post_id = created["id"]
    assert isinstance(post_id, (int, str)) and post_id

    try:
        assert created["title"] == original["title"]
        assert created["body"] == original["body"]

        updated_title = f"{original['title']} (updated)"
        response = rest_api("PATCH", f"/posts/{post_id}", json={"title": updated_title})
        assert response.status_code == 200
        patched = response.json()
        assert patched["id"] == post_id
        assert patched["title"] == updated_title
        assert patched["body"] == original["body"]

        response = rest_api("GET", f"/posts/{post_id}")
        assert response.status_code == 200
        actual = response.json()
        assert actual["id"] == post_id
        assert actual["title"] == updated_title
        assert actual["title"] != original["title"]
        assert actual["body"] == original["body"]
    finally:
        response = rest_api("DELETE", f"/posts/{post_id}")
        assert response.status_code == 200
