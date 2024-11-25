from models.models import Invite, User, Company, Position
from utils.repository import SQLAlchemyBaseRepository


class UserRepository(SQLAlchemyBaseRepository):
    def __init__(self, session):
        super().__init__(session, User)


class CompanyRepository(SQLAlchemyBaseRepository):
    def __init__(self, session):
        super().__init__(session, Company)


class PositionRepository(SQLAlchemyBaseRepository):
    def __init__(self, session):
        super().__init__(session, Position)


class InviteRepository(SQLAlchemyBaseRepository):
    def __init__(self, session):
        super().__init__(session, Invite)
