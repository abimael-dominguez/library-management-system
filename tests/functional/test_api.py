from __future__ import annotations

from datetime import date, timedelta

from fastapi.testclient import TestClient

from src.infrastructure.api import create_app


def test_health_endpoint(db_session):
    app = create_app(auto_seed=False)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides.clear()
    from src.infrastructure.database import get_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_book_member_loan_flow(db_session):
    app = create_app(auto_seed=False)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    from src.infrastructure.database import get_db

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

        return_response = client.put(f"/loans/{loan['loan_id']}/return", json={})
        assert return_response.status_code == 200
        assert return_response.json()["status"] == "returned"
