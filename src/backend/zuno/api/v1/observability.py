from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from zuno.api.services.product import (
    ObservabilityEvalQueryService,
    ObservabilityProjectionQueryService,
    ObservabilityQueryAuthorizationError,
    ObservabilityQueryPrincipal,
)
from zuno.api.services.user import UserPayload, get_login_user
from zuno.platform.database import engine
from zuno.api.dto.schemas import resp_200

router = APIRouter(tags=["Observability"])


def _build_projection_query_service() -> ObservabilityProjectionQueryService:
    return ObservabilityProjectionQueryService(engine=engine)


def _build_eval_query_service() -> ObservabilityEvalQueryService:
    return ObservabilityEvalQueryService(engine=engine)


@router.get("/observability/traces/{trace_id}", summary="Get authorized observability trace projection")
async def get_observability_trace_projection(
    trace_id: str,
    tenant_id: str = Query(...),
    workspace_id: str = Query(...),
    stream_id: str = Query(...),
    login_user: UserPayload = Depends(get_login_user),
):
    principal = ObservabilityQueryPrincipal(
        principal_id=str(login_user.user_id),
        tenant_ids=frozenset({tenant_id}) if login_user.is_admin() else frozenset(),
        workspace_ids=frozenset({workspace_id}) if login_user.is_admin() else frozenset(),
        scopes=frozenset({"observability:read"}) if login_user.is_admin() else frozenset(),
        is_admin=login_user.is_admin(),
    )
    try:
        result = _build_projection_query_service().get_trace_projection(
            principal=principal,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            trace_id=trace_id,
            stream_id=stream_id,
        )
    except ObservabilityQueryAuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return resp_200(data=result)


@router.get("/eval/runs/{eval_run_id}", summary="Get authorized eval run projection")
async def get_eval_run_projection(
    eval_run_id: str,
    tenant_id: str = Query(...),
    workspace_id: str = Query(...),
    login_user: UserPayload = Depends(get_login_user),
):
    principal = ObservabilityQueryPrincipal(
        principal_id=str(login_user.user_id),
        tenant_ids=frozenset({tenant_id}) if login_user.is_admin() else frozenset(),
        workspace_ids=frozenset({workspace_id}) if login_user.is_admin() else frozenset(),
        scopes=frozenset({"eval:read", "observability:read"}) if login_user.is_admin() else frozenset(),
        is_admin=login_user.is_admin(),
    )
    try:
        result = _build_eval_query_service().get_eval_run_projection(
            principal=principal,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            eval_run_id=eval_run_id,
        )
    except ObservabilityQueryAuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return resp_200(data=result)


@router.get("/eval/release-gates/{gate_id}", summary="Get authorized eval release gate report")
async def get_eval_release_gate_report(
    gate_id: str,
    tenant_id: str = Query(...),
    workspace_id: str = Query(...),
    login_user: UserPayload = Depends(get_login_user),
):
    principal = ObservabilityQueryPrincipal(
        principal_id=str(login_user.user_id),
        tenant_ids=frozenset({tenant_id}) if login_user.is_admin() else frozenset(),
        workspace_ids=frozenset({workspace_id}) if login_user.is_admin() else frozenset(),
        scopes=frozenset({"eval:read", "observability:read"}) if login_user.is_admin() else frozenset(),
        is_admin=login_user.is_admin(),
    )
    try:
        result = _build_eval_query_service().get_release_gate_report(
            principal=principal,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            gate_id=gate_id,
        )
    except ObservabilityQueryAuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return resp_200(data=result)


@router.get("/eval/runs/{eval_run_id}/metrics", summary="Get authorized eval run metrics projection")
async def get_eval_run_metrics_projection(
    eval_run_id: str,
    tenant_id: str = Query(...),
    workspace_id: str = Query(...),
    login_user: UserPayload = Depends(get_login_user),
):
    principal = _eval_query_principal(login_user=login_user, tenant_id=tenant_id, workspace_id=workspace_id)
    try:
        result = _build_eval_query_service().get_eval_metrics_projection(
            principal=principal,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            eval_run_id=eval_run_id,
        )
    except ObservabilityQueryAuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return resp_200(data=result)


@router.get("/eval/runs/{eval_run_id}/failures", summary="Get authorized eval run failure projection")
async def get_eval_run_failures_projection(
    eval_run_id: str,
    tenant_id: str = Query(...),
    workspace_id: str = Query(...),
    login_user: UserPayload = Depends(get_login_user),
):
    principal = _eval_query_principal(login_user=login_user, tenant_id=tenant_id, workspace_id=workspace_id)
    try:
        result = _build_eval_query_service().get_eval_failures_projection(
            principal=principal,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            eval_run_id=eval_run_id,
        )
    except ObservabilityQueryAuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return resp_200(data=result)


@router.get("/eval/comparisons/{comparison_hash}", summary="Get authorized eval benchmark comparison report")
async def get_eval_comparison_report(
    comparison_hash: str,
    tenant_id: str = Query(...),
    workspace_id: str = Query(...),
    login_user: UserPayload = Depends(get_login_user),
):
    principal = _eval_query_principal(login_user=login_user, tenant_id=tenant_id, workspace_id=workspace_id)
    try:
        result = _build_eval_query_service().get_comparison_report(
            principal=principal,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            comparison_hash=comparison_hash,
        )
    except ObservabilityQueryAuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return resp_200(data=result)


@router.get("/evidence/{evidence_id}", summary="Get authorized evidence record report")
async def get_evidence_report(
    evidence_id: str,
    tenant_id: str = Query(...),
    workspace_id: str = Query(...),
    login_user: UserPayload = Depends(get_login_user),
):
    principal = _eval_query_principal(login_user=login_user, tenant_id=tenant_id, workspace_id=workspace_id)
    try:
        result = _build_eval_query_service().get_evidence_report(
            principal=principal,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
            evidence_id=evidence_id,
        )
    except ObservabilityQueryAuthorizationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return resp_200(data=result)


def _eval_query_principal(
    *,
    login_user: UserPayload,
    tenant_id: str,
    workspace_id: str,
) -> ObservabilityQueryPrincipal:
    return ObservabilityQueryPrincipal(
        principal_id=str(login_user.user_id),
        tenant_ids=frozenset({tenant_id}) if login_user.is_admin() else frozenset(),
        workspace_ids=frozenset({workspace_id}) if login_user.is_admin() else frozenset(),
        scopes=frozenset({"eval:read", "observability:read"}) if login_user.is_admin() else frozenset(),
        is_admin=login_user.is_admin(),
    )


__all__ = [
    "get_observability_trace_projection",
    "get_eval_release_gate_report",
    "get_eval_comparison_report",
    "get_eval_run_failures_projection",
    "get_eval_run_metrics_projection",
    "get_eval_run_projection",
    "get_evidence_report",
    "router",
]
