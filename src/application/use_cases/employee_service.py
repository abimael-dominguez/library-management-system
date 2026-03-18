from __future__ import annotations

from uuid import uuid4

from ...domain.entities.employee import Employee
from ...domain.repositories.employee_repository import EmployeeRepository
from ..dto.employee_dto import EmployeeCreateRequest


class EmployeeService:
    def __init__(self, employee_repo: EmployeeRepository, commit, rollback):
        self.employee_repo = employee_repo
        self.commit = commit
        self.rollback = rollback

    def list_employees(self, limit: int = 50) -> list[Employee]:
        return self.employee_repo.list_employees(limit)

    def create_employee(self, payload: EmployeeCreateRequest) -> Employee:
        employee = Employee(
            employee_id=str(uuid4()),
            first_name=payload.first_name,
            last_name=payload.last_name,
            position=payload.position,
        )
        self.employee_repo.create_employee(employee)
        self.commit()
        created = self.employee_repo.get_employee_by_id(employee.employee_id)
        return created or employee
