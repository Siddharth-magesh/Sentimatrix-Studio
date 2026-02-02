"""Schedule endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.database import get_database
from app.core.deps import get_current_user
from app.models.schedule import (
    Schedule,
    ScheduleCreate,
    ScheduleExecutionList,
    ScheduleList,
    ScheduleUpdate,
)
from app.models.user import User
from app.repositories.project import ProjectRepository, get_project_repository
from app.repositories.schedule import ScheduleRepository, get_schedule_repository
from app.services.scheduler import get_scheduler

router = APIRouter()


@router.get(
    "",
    response_model=ScheduleList,
    summary="List schedules",
)
async def list_schedules(
    current_user: Annotated[User, Depends(get_current_user)],
    schedule_repo: Annotated[ScheduleRepository, Depends(get_schedule_repository)],
) -> ScheduleList:
    """
    Get all schedules for the current user.
    """
    return await schedule_repo.get_schedules(current_user.id)


@router.post(
    "",
    response_model=Schedule,
    status_code=status.HTTP_201_CREATED,
    summary="Create schedule",
)
async def create_schedule(
    schedule_data: ScheduleCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    schedule_repo: Annotated[ScheduleRepository, Depends(get_schedule_repository)],
) -> Schedule:
    """
    Create a new schedule for a project.

    Only one schedule per project is allowed.

    - **project_id**: Project to schedule (required)
    - **frequency**: hourly, daily, weekly, or monthly
    - **time**: Time to run in HH:MM format (for daily+)
    - **day_of_week**: 0-6 for weekly schedules
    - **day_of_month**: 1-28 for monthly schedules
    - **timezone**: Timezone for schedule (default UTC)
    """
    # Verify project ownership
    await project_repo.get_project(schedule_data.project_id, current_user.id)

    return await schedule_repo.create_schedule(
        user_id=current_user.id,
        schedule_data=schedule_data,
    )


@router.get(
    "/project/{project_id}",
    response_model=Schedule,
    summary="Get project schedule",
)
async def get_project_schedule(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    schedule_repo: Annotated[ScheduleRepository, Depends(get_schedule_repository)],
) -> Schedule:
    """
    Get the schedule for a specific project.
    """
    # Verify project ownership
    await project_repo.get_project(project_id, current_user.id)

    return await schedule_repo.get_schedule(project_id, current_user.id)


@router.put(
    "/project/{project_id}",
    response_model=Schedule,
    summary="Update schedule",
)
async def update_schedule(
    project_id: str,
    update_data: ScheduleUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    schedule_repo: Annotated[ScheduleRepository, Depends(get_schedule_repository)],
) -> Schedule:
    """
    Update the schedule for a project.

    Only provided fields will be updated.
    """
    # Verify project ownership
    await project_repo.get_project(project_id, current_user.id)

    return await schedule_repo.update_schedule(
        project_id=project_id,
        user_id=current_user.id,
        update_data=update_data,
    )


@router.delete(
    "/project/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete schedule",
)
async def delete_schedule(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    schedule_repo: Annotated[ScheduleRepository, Depends(get_schedule_repository)],
) -> None:
    """
    Delete the schedule for a project.
    """
    # Verify project ownership
    await project_repo.get_project(project_id, current_user.id)

    await schedule_repo.delete_schedule(project_id, current_user.id)


@router.post(
    "/project/{project_id}/run-now",
    response_model=dict,
    summary="Run schedule now",
)
async def run_schedule_now(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    db=Depends(get_database),
) -> dict:
    """
    Manually trigger a scheduled scrape job immediately.
    """
    # Verify project ownership
    await project_repo.get_project(project_id, current_user.id)

    scheduler = await get_scheduler(db)
    job_id = await scheduler.run_now(project_id, current_user.id)

    return {"job_id": job_id, "message": "Scrape job started"}


@router.get(
    "/project/{project_id}/history",
    response_model=ScheduleExecutionList,
    summary="Get schedule history",
)
async def get_schedule_history(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    schedule_repo: Annotated[ScheduleRepository, Depends(get_schedule_repository)],
    page: int = 1,
    page_size: int = 20,
) -> ScheduleExecutionList:
    """
    Get execution history for a schedule.
    """
    # Verify project ownership
    await project_repo.get_project(project_id, current_user.id)

    # Get schedule to get its ID
    schedule = await schedule_repo.get_schedule(project_id, current_user.id)

    return await schedule_repo.get_executions(
        schedule_id=schedule.id,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/project/{project_id}/toggle",
    response_model=Schedule,
    summary="Toggle schedule",
)
async def toggle_schedule(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    schedule_repo: Annotated[ScheduleRepository, Depends(get_schedule_repository)],
) -> Schedule:
    """
    Toggle a schedule on/off.
    """
    # Verify project ownership
    await project_repo.get_project(project_id, current_user.id)

    schedule = await schedule_repo.get_schedule(project_id, current_user.id)

    return await schedule_repo.update_schedule(
        project_id=project_id,
        user_id=current_user.id,
        update_data=ScheduleUpdate(enabled=not schedule.enabled),
    )
