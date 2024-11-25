from .unit_of_work import UnitOfWork


class BaseService:
    base_repository: str

    def __init__(self) -> None:
        self.uow: UnitOfWork = UnitOfWork()
