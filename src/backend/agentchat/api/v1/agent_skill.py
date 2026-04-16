from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from agentchat.api.services.agent_skill import AgentSkillService
from agentchat.api.services.user import UserPayload, get_login_user
from agentchat.schema.agent_skill import (
    AgentSkillCreateReq,
    AgentSkillDeleteReq,
    AgentSkillFileAddReq,
    AgentSkillFileDeleteReq,
    AgentSkillFileUpdateReq,
)
from agentchat.schema.schemas import resp_200

router = APIRouter(prefix="/agent_skill", tags=["Agent-Skill"])


@router.post("/create", summary="用户创建 Agent Skill")
async def create_agent_skill(
    req: AgentSkillCreateReq,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        result = await AgentSkillService.create_agent_skill(req, login_user.user_id)
        return resp_200(data=result)
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err)) from err


@router.post("/delete", summary="用户删除 Agent Skill")
async def delete_agent_skill(
    req: AgentSkillDeleteReq,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        result = await AgentSkillService.delete_agent_skill(req.agent_skill_id)
        return resp_200(data=result)
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err)) from err


@router.get("/all", summary="获取当前用户可用的 Agent Skill")
async def get_agent_skills(login_user: UserPayload = Depends(get_login_user)):
    try:
        result = await AgentSkillService.get_agent_skills(login_user.user_id)
        return resp_200(data=result)
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err)) from err


@router.post("/file/update", summary="修改 Agent Skill 文件")
async def update_agent_skill_file(
    req: AgentSkillFileUpdateReq,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        result = await AgentSkillService.update_agent_skill_file(
            target_path=req.path,
            new_content=req.content,
            agent_skill_id=req.agent_skill_id,
        )
        return resp_200(data=result)
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err)) from err


@router.post("/file/add", summary="新增 Agent Skill 文件")
async def add_agent_skill_file(
    req: AgentSkillFileAddReq,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        result = await AgentSkillService.add_agent_skill_file(**req.model_dump())
        return resp_200(data=result)
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err)) from err


@router.post("/file/upload", summary="上传 Agent Skill 文件")
async def upload_agent_skill_file(
    agent_skill_id: str = Form(...),
    path: str = Form(...),
    file: UploadFile = File(...),
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        file_content = await file.read()
        result = await AgentSkillService.upload_agent_skill_file(
            agent_skill_id=agent_skill_id,
            path=path,
            name=file.filename,
            content=file_content.decode("utf-8"),
        )
        return resp_200(data=result)
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err)) from err


@router.post("/file/delete", summary="删除 Agent Skill 文件")
async def delete_agent_skill_file(
    req: AgentSkillFileDeleteReq,
    login_user: UserPayload = Depends(get_login_user),
):
    try:
        result = await AgentSkillService.delete_agent_skill_file(**req.model_dump())
        return resp_200(data=result)
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err)) from err
