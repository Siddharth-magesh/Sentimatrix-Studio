"""Integration tests for user repository."""

import pytest

from app.core.exceptions import EmailAlreadyExistsError, UserNotFoundError
from app.models.user import UserCreate, UserUpdate
from app.repositories.user import UserRepository


@pytest.mark.asyncio
async def test_create_user(test_db):
    """Test creating a user."""
    repo = UserRepository()
    user_data = UserCreate(
        email="test@example.com",
        name="Test User",
        password="TestPass123",
    )

    user = await repo.create_user(user_data)

    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.id is not None
    assert user.is_active is True
    assert user.is_verified is False


@pytest.mark.asyncio
async def test_create_duplicate_user(test_db):
    """Test creating user with duplicate email."""
    repo = UserRepository()
    user_data = UserCreate(
        email="test@example.com",
        name="Test User",
        password="TestPass123",
    )

    await repo.create_user(user_data)

    with pytest.raises(EmailAlreadyExistsError):
        await repo.create_user(user_data)


@pytest.mark.asyncio
async def test_get_user_by_id(test_db):
    """Test getting user by ID."""
    repo = UserRepository()
    user_data = UserCreate(
        email="test@example.com",
        name="Test User",
        password="TestPass123",
    )

    created_user = await repo.create_user(user_data)
    retrieved_user = await repo.get_user_by_id(created_user.id)

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.email == created_user.email


@pytest.mark.asyncio
async def test_get_user_by_email(test_db):
    """Test getting user by email."""
    repo = UserRepository()
    user_data = UserCreate(
        email="test@example.com",
        name="Test User",
        password="TestPass123",
    )

    created_user = await repo.create_user(user_data)
    retrieved_user = await repo.get_user_by_email("test@example.com")

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id


@pytest.mark.asyncio
async def test_get_user_by_email_case_insensitive(test_db):
    """Test getting user by email is case insensitive."""
    repo = UserRepository()
    user_data = UserCreate(
        email="Test@Example.com",
        name="Test User",
        password="TestPass123",
    )

    await repo.create_user(user_data)
    retrieved_user = await repo.get_user_by_email("TEST@EXAMPLE.COM")

    assert retrieved_user is not None


@pytest.mark.asyncio
async def test_update_user(test_db):
    """Test updating user."""
    repo = UserRepository()
    user_data = UserCreate(
        email="test@example.com",
        name="Test User",
        password="TestPass123",
    )

    created_user = await repo.create_user(user_data)
    update_data = UserUpdate(name="Updated Name")
    updated_user = await repo.update_user(created_user.id, update_data)

    assert updated_user is not None
    assert updated_user.name == "Updated Name"


@pytest.mark.asyncio
async def test_authenticate_success(test_db):
    """Test successful authentication."""
    repo = UserRepository()
    user_data = UserCreate(
        email="test@example.com",
        name="Test User",
        password="TestPass123",
    )

    await repo.create_user(user_data)
    user = await repo.authenticate("test@example.com", "TestPass123")

    assert user is not None
    assert user.email == "test@example.com"


@pytest.mark.asyncio
async def test_authenticate_wrong_password(test_db):
    """Test authentication with wrong password."""
    repo = UserRepository()
    user_data = UserCreate(
        email="test@example.com",
        name="Test User",
        password="TestPass123",
    )

    await repo.create_user(user_data)
    user = await repo.authenticate("test@example.com", "WrongPass123")

    assert user is None


@pytest.mark.asyncio
async def test_authenticate_nonexistent_user(test_db):
    """Test authentication with nonexistent user."""
    repo = UserRepository()
    user = await repo.authenticate("nonexistent@example.com", "TestPass123")

    assert user is None


@pytest.mark.asyncio
async def test_email_exists(test_db):
    """Test checking if email exists."""
    repo = UserRepository()
    user_data = UserCreate(
        email="test@example.com",
        name="Test User",
        password="TestPass123",
    )

    assert await repo.email_exists("test@example.com") is False

    await repo.create_user(user_data)

    assert await repo.email_exists("test@example.com") is True
    assert await repo.email_exists("other@example.com") is False


@pytest.mark.asyncio
async def test_deactivate_user(test_db):
    """Test deactivating user."""
    repo = UserRepository()
    user_data = UserCreate(
        email="test@example.com",
        name="Test User",
        password="TestPass123",
    )

    created_user = await repo.create_user(user_data)
    await repo.deactivate_user(created_user.id)

    user = await repo.get_user_by_id(created_user.id)
    assert user is not None
    assert user.is_active is False


@pytest.mark.asyncio
async def test_inactive_user_cannot_authenticate(test_db):
    """Test that inactive user cannot authenticate."""
    repo = UserRepository()
    user_data = UserCreate(
        email="test@example.com",
        name="Test User",
        password="TestPass123",
    )

    created_user = await repo.create_user(user_data)
    await repo.deactivate_user(created_user.id)

    user = await repo.authenticate("test@example.com", "TestPass123")
    assert user is None
