from typing import List, Optional

from models.models import TaskStatus
from utils.service import BaseService
from utils.unit_of_work import UnitOfWork


class TaskService(BaseService):
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_task(
        self,
        title: str,
        description: Optional[str],
        author_id: int,
        responsible_id: int,
        observer_ids: List[int],
        executor_ids: List[int],
        deadline: Optional[str],
        estimated_time: Optional[float],
        status: Optional[str] = TaskStatus.NEW.value,
    ):
        print(f"Received status: {status}")
        async with self.uow:
            task_id = await self.uow.task.add_one_and_get_id(
                title=title,
                description=description,
                author_id=author_id,
                responsible_id=responsible_id,
                deadline=deadline,
                estimated_time=estimated_time,
                status=status,
            )

            observers = []
            for id in observer_ids:
                user = await self.uow.user.get_by_id(id)
                if not user:
                    raise ValueError(f"Observer with ID {id} not found")
                observers.append(user)

            executors = []
            for id in executor_ids:
                user = await self.uow.user.get_by_id(id)
                if not user:
                    raise ValueError(f"Executor with ID {id} not found")
                executors.append(user)
            if status not in TaskStatus._value2member_map_:
                raise ValueError(f"Invalid status: {status}")

            task = await self.uow.task.get_by_id(task_id)
            task.observers = observers
            task.executors = executors
            print(f"Received status: {status}")
            await self.uow.commit()
            return task

    async def get_task(self, task_id: int):
        async with self.uow:
            task = await self.uow.task.get_by_id(task_id)
            if not task:
                raise ValueError("Task not found")
            return task

    async def update_task(self, task_id: int, updates: dict):
        async with self.uow:
            task = await self.uow.task.update_one_by_id(task_id, **updates)
            if not task:
                raise ValueError("Task not found")
            if (
                "status" in updates
                and updates["status"] not in TaskStatus._value2member_map_
            ):
                raise ValueError(f"Invalid status: {updates['status']}")
            await self.uow.commit()
            return task

    async def delete_task(self, task_id: int):
        async with self.uow:
            await self.uow.task.delete_one_by_id(task_id)
            await self.uow.commit()
