from loguru import logger

from zuno.api.services.agent import AgentService
from zuno.database.dao.dialog import DialogDao
from zuno.database.dao.history import HistoryDao
from zuno.database.models.user import AdminUser
from zuno.api.services.security_admin_actions import require_admin_action_authorized


class DialogService:
    @classmethod
    async def create_dialog(cls, name: str, agent_id: str, agent_type: str, user_id: str):
        try:
            dialog = await DialogDao.create_dialog(name, agent_id, agent_type, user_id)
            return dialog.to_dict()
        except Exception as err:
            raise ValueError(f"Add Dialog Appear Error: {err}")

    @classmethod
    async def select_dialog(cls, dialog_id: str):
        try:
            results = await DialogDao.select_dialog(dialog_id)
            return [res.to_dict() for res in results]
        except Exception as err:
            raise ValueError(f"Select Dialog Appear Error: {err}")

    @classmethod
    async def get_list_dialog(cls, user_id: str):
        try:
            results = await DialogDao.get_dialog_by_user(user_id=user_id)
            return [res.to_dict() for res in results]
        except Exception as err:
            raise ValueError(f"Get List Dialog Appear Error: {err}")

    @classmethod
    async def get_agent_by_dialog_id(cls, dialog_id: str):
        try:
            dialog = await DialogDao.get_agent_by_dialog_id(dialog_id)
            return await AgentService.select_agent_by_id(agent_id=dialog.agent_id)
        except Exception as err:
            raise ValueError(f"Select Dialog Appear Error: {err}")

    @classmethod
    async def update_dialog_time(cls, dialog_id: str):
        try:
            await DialogDao.update_dialog_time(dialog_id=dialog_id)
        except Exception as err:
            raise ValueError(f"Update Dialog Create Time Appear Error: {err}")

    @classmethod
    async def delete_dialog(cls, dialog_id: str):
        try:
            await DialogDao.delete_dialog_by_id(dialog_id=dialog_id)
            await HistoryDao.delete_history_by_dialog_id(dialog_id=dialog_id)
        except Exception as err:
            raise ValueError(f"Delete Dialog Appear Error: {err}")

    @classmethod
    async def verify_user_permission(cls, dialog_id, user_id, action: str = "access"):
        dialog = await DialogDao.get_agent_by_dialog_id(dialog_id)
        if user_id == AdminUser:
            if dialog.user_id != AdminUser:
                require_admin_action_authorized(
                    principal_id=user_id,
                    action=f"admin.dialog.{action}",
                    resource_ref=f"dialog:{dialog_id}",
                )
            return
        if user_id != dialog.user_id:
            logger.warning("dialog permission denied: dialog_id={} user_id={}", dialog_id, user_id)
            raise ValueError("没有权限访问")


__all__ = ["DialogService"]
