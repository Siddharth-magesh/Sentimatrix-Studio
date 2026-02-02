"""Target endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.deps import get_current_user
from app.models.target import (
    Target,
    TargetCreate,
    TargetBulkCreate,
    TargetList,
    TargetUpdate,
)
from app.models.user import User
from app.repositories.project import ProjectRepository, get_project_repository
from app.repositories.target import TargetRepository, get_target_repository

router = APIRouter()


@router.get(
    "/{project_id}/targets",
    response_model=TargetList,
    summary="List project targets",
)
async def list_targets(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    target_repo: Annotated[TargetRepository, Depends(get_target_repository)],
    status: str | None = None,
) -> TargetList:
    """
    Get all targets for a project.
    """
    # Verify project ownership
    await project_repo.get_project(project_id, current_user.id)

    return await target_repo.get_targets_by_project(
        project_id=project_id,
        user_id=current_user.id,
        status=status,
    )


@router.post(
    "/{project_id}/targets",
    response_model=Target,
    status_code=status.HTTP_201_CREATED,
    summary="Add target to project",
)
async def create_target(
    project_id: str,
    target_data: TargetCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    target_repo: Annotated[TargetRepository, Depends(get_target_repository)],
) -> Target:
    """
    Add a new scraping target to a project.

    The platform will be automatically detected from the URL.
    Supported platforms: Amazon, Steam, YouTube, Reddit, Google, Trustpilot, Yelp.

    - **url**: Target URL (required)
    - **label**: Custom label (optional, auto-generated if not provided)
    - **options**: Platform-specific options (optional)
    """
    # Verify project ownership
    await project_repo.get_project(project_id, current_user.id)

    target = await target_repo.create_target(
        project_id=project_id,
        user_id=current_user.id,
        target_data=target_data,
    )

    # Update project stats
    await project_repo.increment_stats(project_id, "total_targets")

    return target


@router.post(
    "/{project_id}/targets/bulk",
    response_model=list[Target],
    status_code=status.HTTP_201_CREATED,
    summary="Add multiple targets to project",
)
async def create_targets_bulk(
    project_id: str,
    bulk_data: TargetBulkCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    target_repo: Annotated[TargetRepository, Depends(get_target_repository)],
) -> list[Target]:
    """
    Add multiple scraping targets to a project at once.

    Maximum 50 URLs per request.
    """
    # Verify project ownership
    await project_repo.get_project(project_id, current_user.id)

    targets = await target_repo.create_targets_bulk(
        project_id=project_id,
        user_id=current_user.id,
        bulk_data=bulk_data,
    )

    # Update project stats
    await project_repo.increment_stats(project_id, "total_targets", len(targets))

    return targets


@router.get(
    "/{project_id}/targets/{target_id}",
    response_model=Target,
    summary="Get target",
)
async def get_target(
    project_id: str,
    target_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    target_repo: Annotated[TargetRepository, Depends(get_target_repository)],
) -> Target:
    """
    Get a specific target by ID.
    """
    # Verify project ownership
    await project_repo.get_project(project_id, current_user.id)

    return await target_repo.get_target(target_id, current_user.id)


@router.put(
    "/{project_id}/targets/{target_id}",
    response_model=Target,
    summary="Update target",
)
async def update_target(
    project_id: str,
    target_id: str,
    update_data: TargetUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    target_repo: Annotated[TargetRepository, Depends(get_target_repository)],
) -> Target:
    """
    Update a target.

    - **label**: Custom label
    - **status**: "active" or "paused"
    - **options**: Platform-specific options
    """
    # Verify project ownership
    await project_repo.get_project(project_id, current_user.id)

    return await target_repo.update_target(
        target_id=target_id,
        user_id=current_user.id,
        update_data=update_data,
    )


@router.delete(
    "/{project_id}/targets/{target_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete target",
)
async def delete_target(
    project_id: str,
    target_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    target_repo: Annotated[TargetRepository, Depends(get_target_repository)],
) -> None:
    """
    Delete a target from a project.
    """
    # Verify project ownership
    await project_repo.get_project(project_id, current_user.id)

    await target_repo.delete_target(target_id, current_user.id)

    # Update project stats
    await project_repo.increment_stats(project_id, "total_targets", -1)
