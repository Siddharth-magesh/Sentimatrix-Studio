# API Development Guide

This guide covers best practices for developing and extending the Sentimatrix Studio API.

## API Structure

### Versioning

The API uses URL-based versioning:

```
/api/v1/projects
/api/v1/targets
/api/v1/results
```

New versions should be introduced for breaking changes:

```
/api/v2/projects  # New version with breaking changes
```

### Endpoint Organization

Endpoints are organized by resource in `backend/app/api/v1/endpoints/`:

```
endpoints/
├── auth.py         # Authentication endpoints
├── projects.py     # Project CRUD
├── targets.py      # Target management
├── scrape_jobs.py  # Job operations
├── results.py      # Result queries
├── schedules.py    # Schedule management
├── webhooks.py     # Webhook management
├── settings.py     # User settings
└── dashboard.py    # Dashboard statistics
```

## Creating a New Endpoint

### 1. Define the Schema

Create Pydantic models in `backend/app/models/`:

```python
# models/example.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ExampleCreate(BaseModel):
    """Schema for creating an example."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    value: int = Field(..., ge=0, le=100)

class ExampleUpdate(BaseModel):
    """Schema for updating an example."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    value: Optional[int] = Field(None, ge=0, le=100)

class ExampleResponse(BaseModel):
    """Schema for example response."""
    id: str
    name: str
    description: Optional[str]
    value: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

### 2. Create the Service

Business logic goes in `backend/app/services/`:

```python
# services/example_service.py
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from typing import Optional

from app.models.example import ExampleCreate, ExampleUpdate, ExampleResponse

class ExampleService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.examples

    async def create(self, user_id: str, data: ExampleCreate) -> ExampleResponse:
        """Create a new example."""
        doc = {
            "user_id": ObjectId(user_id),
            "name": data.name,
            "description": data.description,
            "value": data.value,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await self.collection.insert_one(doc)
        doc["id"] = str(result.inserted_id)
        return ExampleResponse(**doc)

    async def get(self, example_id: str, user_id: str) -> Optional[ExampleResponse]:
        """Get an example by ID."""
        doc = await self.collection.find_one({
            "_id": ObjectId(example_id),
            "user_id": ObjectId(user_id),
        })
        if doc:
            doc["id"] = str(doc["_id"])
            return ExampleResponse(**doc)
        return None

    async def update(
        self,
        example_id: str,
        user_id: str,
        data: ExampleUpdate
    ) -> Optional[ExampleResponse]:
        """Update an example."""
        update_data = {k: v for k, v in data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(example_id), "user_id": ObjectId(user_id)},
            {"$set": update_data},
            return_document=True,
        )
        if result:
            result["id"] = str(result["_id"])
            return ExampleResponse(**result)
        return None

    async def delete(self, example_id: str, user_id: str) -> bool:
        """Delete an example."""
        result = await self.collection.delete_one({
            "_id": ObjectId(example_id),
            "user_id": ObjectId(user_id),
        })
        return result.deleted_count > 0
```

### 3. Create the Endpoint

Route handlers go in `backend/app/api/v1/endpoints/`:

```python
# api/v1/endpoints/examples.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.api.v1.deps import get_current_user, get_db
from app.models.user import User
from app.models.example import ExampleCreate, ExampleUpdate, ExampleResponse
from app.services.example_service import ExampleService

router = APIRouter()

@router.post("", response_model=ExampleResponse, status_code=status.HTTP_201_CREATED)
async def create_example(
    data: ExampleCreate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db),
):
    """Create a new example."""
    service = ExampleService(db)
    return await service.create(current_user.id, data)

@router.get("/{example_id}", response_model=ExampleResponse)
async def get_example(
    example_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db),
):
    """Get an example by ID."""
    service = ExampleService(db)
    example = await service.get(example_id, current_user.id)
    if not example:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Example not found",
        )
    return example

@router.put("/{example_id}", response_model=ExampleResponse)
async def update_example(
    example_id: str,
    data: ExampleUpdate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db),
):
    """Update an example."""
    service = ExampleService(db)
    example = await service.update(example_id, current_user.id, data)
    if not example:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Example not found",
        )
    return example

@router.delete("/{example_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_example(
    example_id: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db),
):
    """Delete an example."""
    service = ExampleService(db)
    deleted = await service.delete(example_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Example not found",
        )
```

### 4. Register the Router

Add to the main router in `backend/app/api/v1/api.py`:

```python
from app.api.v1.endpoints import examples

api_router = APIRouter()
api_router.include_router(examples.router, prefix="/examples", tags=["examples"])
```

## Error Handling

### Standard Exceptions

Use FastAPI's HTTPException for errors:

```python
from fastapi import HTTPException, status

# 404 Not Found
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Resource not found",
)

# 400 Bad Request
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Invalid input data",
)

# 403 Forbidden
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You don't have permission to access this resource",
)
```

### Custom Exception Handler

For consistent error responses:

```python
# core/exceptions.py
from fastapi import Request
from fastapi.responses import JSONResponse

class AppException(Exception):
    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code

async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        },
    )
```

## Authentication

### Protecting Endpoints

Use dependency injection for authentication:

```python
from app.api.v1.deps import get_current_user, get_current_admin_user

# Requires authenticated user
@router.get("/protected")
async def protected_endpoint(current_user: User = Depends(get_current_user)):
    return {"user": current_user.email}

# Requires admin user
@router.get("/admin-only")
async def admin_endpoint(admin: User = Depends(get_current_admin_user)):
    return {"admin": admin.email}

# Optional authentication
@router.get("/public")
async def public_endpoint(
    current_user: Optional[User] = Depends(get_optional_user)
):
    if current_user:
        return {"message": f"Hello, {current_user.email}"}
    return {"message": "Hello, guest"}
```

## Pagination

### Standard Pagination

Use cursor-based or offset pagination:

```python
from typing import List, Optional
from pydantic import BaseModel

class PaginatedResponse(BaseModel):
    items: List[ExampleResponse]
    total: int
    page: int
    per_page: int
    pages: int

@router.get("", response_model=PaginatedResponse)
async def list_examples(
    page: int = 1,
    per_page: int = 20,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db),
):
    """List examples with pagination."""
    service = ExampleService(db)
    skip = (page - 1) * per_page

    items = await service.list(
        user_id=current_user.id,
        skip=skip,
        limit=per_page,
    )
    total = await service.count(user_id=current_user.id)

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        pages=(total + per_page - 1) // per_page,
    )
```

## Caching

### Response Caching

Use the cache decorator for read endpoints:

```python
from app.core.cache import cache_response

@router.get("/{example_id}")
@cache_response(ttl=300)  # Cache for 5 minutes
async def get_example(
    example_id: str,
    current_user: User = Depends(get_current_user),
):
    ...
```

### Cache Invalidation

Invalidate cache when data changes:

```python
from app.core.cache import invalidate_cache

@router.put("/{example_id}")
async def update_example(...):
    result = await service.update(...)
    await invalidate_cache(f"examples:{example_id}")
    return result
```

## Testing

### Writing Tests

Create tests in `backend/tests/api/`:

```python
# tests/api/test_examples.py
import pytest
from httpx import AsyncClient

@pytest.fixture
async def auth_headers(client: AsyncClient, test_user_data: dict) -> dict:
    """Get auth headers for authenticated requests."""
    await client.post("/api/v1/auth/register", json=test_user_data)
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"],
        },
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

class TestExamples:
    @pytest.mark.asyncio
    async def test_create_example(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        response = await client.post(
            "/api/v1/examples",
            json={"name": "Test Example", "value": 50},
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Example"
        assert data["value"] == 50

    @pytest.mark.asyncio
    async def test_get_example_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict,
    ):
        response = await client.get(
            "/api/v1/examples/000000000000000000000000",
            headers=auth_headers,
        )

        assert response.status_code == 404
```

## OpenAPI Documentation

### Endpoint Documentation

Add detailed documentation to endpoints:

```python
@router.post(
    "",
    response_model=ExampleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an example",
    description="Create a new example for the authenticated user.",
    responses={
        201: {"description": "Example created successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Not authenticated"},
    },
)
async def create_example(
    data: ExampleCreate,
    current_user: User = Depends(get_current_user),
):
    """
    Create a new example with the following properties:

    - **name**: Required. 1-100 characters.
    - **description**: Optional. Free-form text.
    - **value**: Required. Integer from 0 to 100.
    """
    ...
```

### Schema Documentation

Add examples to schemas:

```python
class ExampleCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        example="My Example",
        description="The name of the example",
    )
    value: int = Field(
        ...,
        ge=0,
        le=100,
        example=50,
        description="A value between 0 and 100",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "My Example",
                "description": "An example description",
                "value": 50,
            }
        }
```
