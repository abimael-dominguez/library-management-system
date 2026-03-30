from __future__ import annotations

from uuid import uuid4

from ...domain.entities.employee import Employee
from ...domain.interfaces.employee_repository import EmployeeRepository
from ..dtos.employee_dto import EmployeeCreateRequest
from ..interfaces.unit_of_work import UnitOfWork


class CreateEmployeeUseCase:
    """Registers a new library employee inside a single transaction."""

    def __init__(self, employee_repo: EmployeeRepository, unit_of_work: UnitOfWork) -> None:
        self._employee_repo = employee_repo
        self._unit_of_work = unit_of_work

    def execute(self, *, payload: EmployeeCreateRequest) -> Employee:
        employee = Employee(
            employee_id=str(uuid4()),
            first_name=payload.first_name,
            last_name=payload.last_name,
            position=payload.position,
        )
        self._employee_repo.create_employee(employee)
        self._unit_of_work.commit()
        created = self._employee_repo.get_employee_by_id(employee.employee_id)
        return created or employee
