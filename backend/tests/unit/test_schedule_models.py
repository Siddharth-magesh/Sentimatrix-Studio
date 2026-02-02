"""Tests for schedule models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models.schedule import (
    Schedule,
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleExecution,
)


class TestScheduleModels:
    """Test schedule models."""

    def test_schedule_create_defaults(self):
        """Test schedule creation with defaults."""
        schedule = ScheduleCreate(project_id="project123")

        assert schedule.project_id == "project123"
        assert schedule.enabled is True
        assert schedule.frequency == "daily"
        assert schedule.time == "09:00"
        assert schedule.timezone == "UTC"
        assert schedule.max_retries == 3

    def test_schedule_create_custom(self):
        """Test schedule creation with custom values."""
        schedule = ScheduleCreate(
            project_id="project123",
            frequency="weekly",
            time="14:30",
            day_of_week=1,  # Tuesday
            timezone="America/New_York",
            max_retries=5,
        )

        assert schedule.frequency == "weekly"
        assert schedule.time == "14:30"
        assert schedule.day_of_week == 1
        assert schedule.timezone == "America/New_York"

    def test_schedule_create_hourly(self):
        """Test hourly schedule doesn't need time."""
        schedule = ScheduleCreate(
            project_id="project123",
            frequency="hourly",
        )

        assert schedule.frequency == "hourly"

    def test_schedule_create_monthly(self):
        """Test monthly schedule."""
        schedule = ScheduleCreate(
            project_id="project123",
            frequency="monthly",
            day_of_month=15,
        )

        assert schedule.frequency == "monthly"
        assert schedule.day_of_month == 15

    def test_schedule_create_invalid_time(self):
        """Test invalid time format."""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleCreate(
                project_id="project123",
                time="25:00",  # Invalid hour
            )

        assert "Time must be in HH:MM format" in str(exc_info.value)

    def test_schedule_create_invalid_time_format(self):
        """Test invalid time format string."""
        with pytest.raises(ValidationError) as exc_info:
            ScheduleCreate(
                project_id="project123",
                time="9am",  # Wrong format
            )

        assert "Time must be in HH:MM format" in str(exc_info.value)

    def test_schedule_create_invalid_day_of_week(self):
        """Test invalid day of week."""
        with pytest.raises(ValidationError):
            ScheduleCreate(
                project_id="project123",
                frequency="weekly",
                day_of_week=7,  # Valid is 0-6
            )

    def test_schedule_create_invalid_day_of_month(self):
        """Test invalid day of month."""
        with pytest.raises(ValidationError):
            ScheduleCreate(
                project_id="project123",
                frequency="monthly",
                day_of_month=29,  # Max is 28 for safety
            )

    def test_schedule_update_partial(self):
        """Test partial schedule update."""
        update = ScheduleUpdate(enabled=False)

        assert update.enabled is False
        assert update.frequency is None
        assert update.time is None

    def test_schedule_update_multiple_fields(self):
        """Test updating multiple fields."""
        update = ScheduleUpdate(
            frequency="hourly",
            enabled=False,
            max_retries=1,
        )

        assert update.frequency == "hourly"
        assert update.enabled is False
        assert update.max_retries == 1


class TestScheduleExecution:
    """Test schedule execution model."""

    def test_execution_defaults(self):
        """Test execution with defaults."""
        execution = ScheduleExecution(
            schedule_id="schedule123",
        )

        assert execution.schedule_id == "schedule123"
        assert execution.status == "pending"
        assert execution.job_id is None
        assert execution.results_count == 0

    def test_execution_completed(self):
        """Test completed execution."""
        execution = ScheduleExecution(
            schedule_id="schedule123",
            job_id="job456",
            status="completed",
            results_count=150,
            started_at=datetime.now(),
            completed_at=datetime.now(),
        )

        assert execution.status == "completed"
        assert execution.job_id == "job456"
        assert execution.results_count == 150

    def test_execution_failed(self):
        """Test failed execution."""
        execution = ScheduleExecution(
            schedule_id="schedule123",
            status="failed",
            error="Connection timeout",
            retry_count=2,
        )

        assert execution.status == "failed"
        assert execution.error == "Connection timeout"
        assert execution.retry_count == 2
