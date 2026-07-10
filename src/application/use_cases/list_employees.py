from __future__ import annotations

from ...domain.entities.employee import Employee
from ...domain.interfaces.employee_repository import EmployeeRepository


class ListEmployeesUseCase:
    """Retrieves a paginated list of library employees."""

    def __init__(self, employee_repo: EmployeeRepository) -> None:
        self._employee_repo = employee_repo

    def execute(self, *, limit: int = 50, offset: int = 0) -> list[Employee]:
        return self._employee_repo.list_employees(limit=limit, offset=offset)

    def count(self) -> int:
        return self._employee_repo.count_employees()
