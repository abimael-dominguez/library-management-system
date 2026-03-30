from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ...domain.entities.employee import Employee
from ...domain.interfaces.employee_repository import EmployeeRepository
from ..persistence.models import EmployeeModel


def _to_domain_employee(model: EmployeeModel) -> Employee:
    """Map an EmployeeModel ORM instance to the domain Employee entity."""
    return Employee(
        employee_id=model.employee_id,
        first_name=model.first_name,
        last_name=model.last_name,
        position=model.position,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyEmployeeRepository(EmployeeRepository):
    """SQLAlchemy-backed implementation of the EmployeeRepository interface."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def create_employee(self, employee: Employee) -> Employee:
        self._db.add(
            EmployeeModel(
                employee_id=employee.employee_id,
                first_name=employee.first_name,
                last_name=employee.last_name,
                position=employee.position,
            )
        )
        return employee

    def get_employee_by_id(self, employee_id: str) -> Employee | None:
        model = self._db.get(EmployeeModel, employee_id)
        return _to_domain_employee(model) if model else None

    def list_employees(self, limit: int = 50) -> list[Employee]:
        stmt = select(EmployeeModel).order_by(EmployeeModel.first_name, EmployeeModel.last_name).limit(limit)
        return [_to_domain_employee(model) for model in self._db.scalars(stmt).all()]
