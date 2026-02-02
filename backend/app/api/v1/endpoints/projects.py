"""Project endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.deps import get_current_user
from app.models.project import (
    Project,
    ProjectCreate,
    ProjectList,
    ProjectUpdate,
)
from app.models.user import User
from app.repositories.project import ProjectRepository, get_project_repository

router = APIRouter()


@router.get(
    "",
    response_model=ProjectList,
    summary="List projects",
)
async def list_projects(
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    status: str | None = Query(None, description="Filter by status"),
    search: str | None = Query(None, description="Search in name/description"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> ProjectList:
    """
    Get paginated list of projects for the current user.

    Supports filtering by status and searching by name/description.
    """
    return await project_repo.get_projects(
        user_id=current_user.id,
        status=status,
        search=search,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=Project,
    status_code=status.HTTP_201_CREATED,
    summary="Create project",
)
async def create_project(
    project_data: ProjectCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
) -> Project:
    """
    Create a new analysis project.

    - **name**: Project name (required)
    - **description**: Project description (optional)
    - **preset**: Configuration preset (starter, standard, advanced, budget, custom)
    - **config**: Custom configuration (required if preset is "custom")
    """
    return await project_repo.create_project(
        user_id=current_user.id,
        project_data=project_data,
    )


@router.get(
    "/{project_id}",
    response_model=Project,
    summary="Get project",
)
async def get_project(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
) -> Project:
    """
    Get a specific project by ID.

    Returns 404 if the project doesn't exist or doesn't belong to the current user.
    """
    return await project_repo.get_project(
        project_id=project_id,
        user_id=current_user.id,
    )


@router.put(
    "/{project_id}",
    response_model=Project,
    summary="Update project",
)
async def update_project(
    project_id: str,
    update_data: ProjectUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
) -> Project:
    """
    Update a project.

    Only provided fields will be updated. Setting status to "archived" will
    archive the project (soft delete).
    """
    return await project_repo.update_project(
        project_id=project_id,
        user_id=current_user.id,
        update_data=update_data,
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
)
async def delete_project(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    permanent: bool = Query(False, description="Permanently delete (cannot be undone)"),
) -> None:
    """
    Delete a project.

    By default, projects are soft-deleted (archived). Use permanent=true to
    permanently delete the project and all its data.
    """
    if permanent:
        await project_repo.hard_delete_project(project_id, current_user.id)
    else:
        await project_repo.delete_project(project_id, current_user.id)


@router.get(
    "/{project_id}/stats",
    response_model=dict,
    summary="Get project statistics",
)
async def get_project_stats(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
) -> dict:
    """
    Get detailed statistics for a project.
    """
    project = await project_repo.get_project(project_id, current_user.id)
    return project.stats.model_dump()
