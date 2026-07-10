from __future__ import annotations

from datetime import date, timedelta

from fastapi.testclient import TestClient

from src.infrastructure.api.app import create_app


def test_health_endpoint(db_session):
    app = create_app(auto_seed=False)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides.clear()
    from src.infrastructure.persistence.database import get_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_import_summary_endpoint(db_session):
    app = create_app(auto_seed=False)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    from src.infrastructure.persistence.database import get_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        response = client.get("/import-summary")

    assert response.status_code == 200
    payload = response.json()
    assert "warnings" in payload
    assert "errors" in payload
    assert "copies" in payload


def test_book_member_loan_flow(db_session):
    app = create_app(auto_seed=False)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    from src.infrastructure.persistence.database import get_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        book_response = client.post(
            "/books",
            json={
                "title": "Transactional Systems",
                "author": "Pat Helland",
                "total_copies": 2,
            },
        )
        assert book_response.status_code == 201
        book = book_response.json()
        assert book["available_copies"] == 2

        member_response = client.post(
            "/members",
            json={
                "first_name": "Luisa",
                "last_name": "Campos",
                "email": "luisa.campos@example.com",
            },
        )
        assert member_response.status_code == 201
        member = member_response.json()

        employee_response = client.post(
            "/employees",
            json={
                "first_name": "Sofia",
                "last_name": "Mendez",
                "position": "Assistant",
            },
        )
        assert employee_response.status_code == 201
        employee = employee_response.json()

        loan_response = client.post(
            "/loans",
            json={
                "book_copy_id": book["first_available_copy_id"],
                "member_id": member["member_id"],
                "employee_id": employee["employee_id"],
                "loan_date": str(date.today()),
                "due_date": str(date.today() + timedelta(days=14)),
            },
        )
        assert loan_response.status_code == 201
        loan = loan_response.json()
        assert loan["status"] == "in_progress"

        book_after_loan_response = client.get(f"/books/{book['book_id']}")
        assert book_after_loan_response.status_code == 200
        assert book_after_loan_response.json()["available_copies"] == 1

        loans_response = client.get("/loans")
        assert loans_response.status_code == 200
        loans_payload = loans_response.json()
        assert loans_payload["meta"]["total"] == 1
        assert loans_payload["meta"]["returned"] == 1
        listed_loan = loans_payload["loans"][0]
        assert listed_loan["book_title"] == "Transactional Systems"
        assert listed_loan["member_name"] == "Luisa Campos"

        open_loans_response = client.get("/loans?status=open")
        assert open_loans_response.status_code == 200
        assert open_loans_response.json()["meta"]["total"] == 1

        second_loan_response = client.post(
            "/loans",
            json={
                "book_copy_id": book["first_available_copy_id"],
                "member_id": member["member_id"],
                "employee_id": employee["employee_id"],
                "loan_date": str(date.today()),
                "due_date": str(date.today() + timedelta(days=14)),
            },
        )
        assert second_loan_response.status_code == 400
        assert second_loan_response.json()["error"]["code"] == "domain_error"

        return_response = client.put(f"/loans/{loan['loan_id']}/return", json={})
        assert return_response.status_code == 200
        assert return_response.json()["status"] == "returned"
        assert return_response.json()["actual_return_date"] == str(date.today())

        returned_loans_response = client.get("/loans?status=returned")
        assert returned_loans_response.status_code == 200
        assert returned_loans_response.json()["meta"]["total"] == 1
        assert returned_loans_response.json()["loans"][0]["status"] == "returned"

        book_after_return_response = client.get(f"/books/{book['book_id']}")
        assert book_after_return_response.status_code == 200
        assert book_after_return_response.json()["available_copies"] == 2

        reloaded_response = client.get(f"/loans/{loan['loan_id']}")
        assert reloaded_response.status_code == 200
        assert reloaded_response.json()["status"] == "returned"
        assert reloaded_response.json()["actual_return_date"] == str(date.today())

        new_loan_response = client.post(
            "/loans",
            json={
                "book_copy_id": book["first_available_copy_id"],
                "member_id": member["member_id"],
                "employee_id": employee["employee_id"],
                "loan_date": str(date.today()),
                "due_date": str(date.today() + timedelta(days=7)),
            },
        )
        assert new_loan_response.status_code == 201


def test_api_contract_pagination_filters_and_errors(db_session):
    app = create_app(auto_seed=False)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    from src.infrastructure.persistence.database import get_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        book_response = client.post(
            "/books",
            json={
                "title": "Overdue Systems",
                "author": "Grace Hopper",
                "total_copies": 1,
            },
        )
        member_response = client.post(
            "/members",
            json={"first_name": "Mario", "last_name": "Rios"},
        )
        assert book_response.status_code == 201
        assert member_response.status_code == 201

        book = book_response.json()
        member = member_response.json()
        overdue_loan_response = client.post(
            "/loans",
            json={
                "book_copy_id": book["first_available_copy_id"],
                "member_id": member["member_id"],
                "loan_date": str(date.today() - timedelta(days=10)),
                "due_date": str(date.today() - timedelta(days=1)),
            },
        )
        assert overdue_loan_response.status_code == 201

        books_response = client.get("/books?limit=1&offset=0")
        assert books_response.status_code == 200
        assert books_response.json()["meta"] == {
            "limit": 1,
            "offset": 0,
            "returned": 1,
            "total": 1,
            "has_more": False,
        }

        overdue_response = client.get("/loans?status=overdue")
        assert overdue_response.status_code == 200
        overdue_payload = overdue_response.json()
        assert overdue_payload["meta"]["total"] == 1
        assert overdue_payload["loans"][0]["status"] == "overdue"

        validation_response = client.get("/loans?status=unknown")
        assert validation_response.status_code == 422
        validation_payload = validation_response.json()
        assert validation_payload["error"]["code"] == "validation_error"
        assert validation_payload["error"]["field_errors"]

        missing_response = client.get("/books/missing-book")
        assert missing_response.status_code == 404
        assert missing_response.json()["error"]["code"] == "book_not_found"
