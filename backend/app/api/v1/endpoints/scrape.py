"""Scrape job endpoints."""

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Query, status

from app.core.database import get_database
from app.core.deps import get_current_user
from app.models.scrape_job import (
    ScrapeJob,
    ScrapeJobCreate,
    ScrapeJobList,
)
from app.models.user import User
from app.repositories.project import ProjectRepository, get_project_repository
from app.repositories.scrape_job import ScrapeJobRepository, get_scrape_job_repository
from app.services.scrape_executor import get_job_queue

router = APIRouter()


@router.post(
    "/{project_id}/scrape",
    response_model=ScrapeJob,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start scrape job",
)
async def start_scrape(
    project_id: str,
    job_data: ScrapeJobCreate,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    job_repo: Annotated[ScrapeJobRepository, Depends(get_scrape_job_repository)],
    db=Depends(get_database),
) -> ScrapeJob:
    """
    Start a new scrape job for a project.

    The job will be queued and executed in the background. Use the
    returned job ID to check status.

    - **target_ids**: List of specific target IDs to scrape (optional, defaults to all)
    - **options**: Scrape options (max_results, date filters, etc.)
    """
    # Verify project ownership and get config
    project = await project_repo.get_project(project_id, current_user.id)

    # Create job
    job = await job_repo.create_job(
        project_id=project_id,
        user_id=current_user.id,
        job_data=job_data,
        trigger="manual",
    )

    # Enqueue job for background processing
    job_queue = await get_job_queue(db)
    await job_queue.enqueue(job, project)

    return job


@router.get(
    "/{project_id}/scrape/jobs",
    response_model=ScrapeJobList,
    summary="List scrape jobs",
)
async def list_scrape_jobs(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    job_repo: Annotated[ScrapeJobRepository, Depends(get_scrape_job_repository)],
    status_filter: str | None = Query(None, alias="status", description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> ScrapeJobList:
    """
    Get paginated list of scrape jobs for a project.
    """
    # Verify project ownership
    await project_repo.get_project(project_id, current_user.id)

    return await job_repo.get_jobs_by_project(
        project_id=project_id,
        user_id=current_user.id,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{project_id}/scrape/jobs/{job_id}",
    response_model=ScrapeJob,
    summary="Get scrape job",
)
async def get_scrape_job(
    project_id: str,
    job_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    job_repo: Annotated[ScrapeJobRepository, Depends(get_scrape_job_repository)],
) -> ScrapeJob:
    """
    Get details of a specific scrape job.
    """
    # Verify project ownership
    await project_repo.get_project(project_id, current_user.id)

    return await job_repo.get_job(job_id, current_user.id)


@router.post(
    "/{project_id}/scrape/jobs/{job_id}/cancel",
    response_model=ScrapeJob,
    summary="Cancel scrape job",
)
async def cancel_scrape_job(
    project_id: str,
    job_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    job_repo: Annotated[ScrapeJobRepository, Depends(get_scrape_job_repository)],
    db=Depends(get_database),
) -> ScrapeJob:
    """
    Cancel a running or queued scrape job.
    """
    # Verify project ownership
    await project_repo.get_project(project_id, current_user.id)

    # Try to cancel in job queue
    job_queue = await get_job_queue(db)
    await job_queue.cancel_job(job_id)

    # Update status in database
    return await job_repo.cancel_job(job_id, current_user.id)


@router.get(
    "/{project_id}/scrape/jobs/{job_id}/progress",
    response_model=dict,
    summary="Get scrape job progress",
)
async def get_scrape_job_progress(
    project_id: str,
    job_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    project_repo: Annotated[ProjectRepository, Depends(get_project_repository)],
    job_repo: Annotated[ScrapeJobRepository, Depends(get_scrape_job_repository)],
) -> dict:
    """
    Get real-time progress of a scrape job.

    Returns progress percentage, target statuses, and stats.
    """
    # Verify project ownership
    await project_repo.get_project(project_id, current_user.id)

    job = await job_repo.get_job(job_id, current_user.id)

    return {
        "id": job.id,
        "status": job.status,
        "progress": job.progress,
        "targets": [t.model_dump() for t in job.targets],
        "stats": job.stats.model_dump(),
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "error_message": job.error_message,
    }


@router.get(
    "/scrape/running",
    response_model=list[ScrapeJob],
    summary="Get running jobs",
)
async def get_running_jobs(
    current_user: Annotated[User, Depends(get_current_user)],
    job_repo: Annotated[ScrapeJobRepository, Depends(get_scrape_job_repository)],
) -> list[ScrapeJob]:
    """
    Get all running scrape jobs for the current user across all projects.
    """
    jobs = await job_repo.get_jobs_by_project(
        project_id="",  # Will be ignored
        user_id=current_user.id,
        status_filter="running",
        page=1,
        page_size=100,
    )
    return jobs.items
