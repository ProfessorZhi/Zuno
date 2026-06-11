from typing import List

from sqlmodel import delete, select

from zuno.database.models.role import AdminRole
from zuno.database.models.user_role import UserRole, UserRoleBase
from zuno.database.session import session_getter


class UserRoleDao(UserRoleBase):
    @classmethod
    def get_user_roles(cls, user_id: str) -> List[UserRole]:
        with session_getter() as session:
            return session.exec(select(UserRole).where(UserRole.user_id == user_id)).all()

    @classmethod
    def get_roles_user(cls, role_ids: List[str], page: int = 0, limit: int = 0) -> List[UserRole]:
        with session_getter() as session:
            statement = select(UserRole).where(UserRole.role_id.in_(role_ids))
            if page and limit:
                statement = statement.offset((page - 1) * limit).limit(limit)
            return session.exec(statement).all()

    @classmethod
    def get_admins_user(cls) -> List[UserRole]:
        with session_getter() as session:
            statement = select(UserRole).where(UserRole.role_id == AdminRole)
            return session.exec(statement).all()

    @classmethod
    def set_admin_user(cls, user_id: str) -> UserRole:
        with session_getter() as session:
            user_role = UserRole(user_id=user_id, role_id=AdminRole)
            session.add(user_role)
            session.commit()
            session.refresh(user_role)
            return user_role

    @classmethod
    def add_user_roles(cls, user_id: str, role_ids: List[str]) -> List[UserRole]:
        with session_getter() as session:
            user_roles = [UserRole(user_id=user_id, role_id=role_id) for role_id in role_ids]
            session.add_all(user_roles)
            session.commit()
            return user_roles

    @classmethod
    def delete_user_roles(cls, user_id: str, role_ids: List[str]) -> None:
        with session_getter() as session:
            statement = delete(UserRole).where(UserRole.user_id == user_id).where(UserRole.role_id.in_(role_ids))
            session.exec(statement)
            session.commit()


__all__ = ["UserRoleDao"]
