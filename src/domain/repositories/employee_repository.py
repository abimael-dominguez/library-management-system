from __future__ import annotations

from abc import ABC, abstractmethod

from ..entities.employee import Employee


class EmployeeRepository(ABC):
    @abstractmethod
    def create_employee(self, employee: Employee) -> Employee:
        raise NotImplementedError

    @abstractmethod
    def get_employee_by_id(self, employee_id: str) -> Employee | None:
        raise NotImplementedError

    @abstractmethod
    def list_employees(self, limit: int = 50) -> list[Employee]:
        raise NotImplementedError
