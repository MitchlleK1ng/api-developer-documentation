import os
import secrets
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field


app = FastAPI(
    title="ContentMG API",
    description="Customer management API for the ContentMG platform.",
    version="1.0.0",
)

security = HTTPBearer(auto_error=False)

API_TOKEN = os.getenv("CONTENTMG_API_TOKEN")

customers = {}
next_customer_id = 1001


class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr


class Customer(CustomerCreate):
    id: str


def require_authentication(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(security),
    ],
):
    if not API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not configured.",
        )

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not secrets.compare_digest(
        credentials.credentials,
        API_TOKEN,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


Auth = Annotated[None, Depends(require_authentication)]


@app.get("/")
def root():
    return {
        "name": "ContentMG API",
        "version": "1.0.0",
        "status": "running",
    }


@app.post(
    "/v1/customers",
    response_model=Customer,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    customer_data: CustomerCreate,
    auth: Auth,
):
    global next_customer_id

    for existing in customers.values():
        if existing["email"] == str(customer_data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A customer with this email already exists.",
            )

    customer_id = f"cust_{next_customer_id}"
    next_customer_id += 1

    customer = {
        "id": customer_id,
        "name": customer_data.name,
        "email": str(customer_data.email),
    }

    customers[customer_id] = customer

    return customer


@app.get("/v1/customers", response_model=list[Customer])
def list_customers(auth: Auth):
    return list(customers.values())


@app.get("/v1/customers/{customer_id}", response_model=Customer)
def get_customer(customer_id: str, auth: Auth):
    customer = customers.get(customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    return customer


@app.put("/v1/customers/{customer_id}", response_model=Customer)
def update_customer(
    customer_id: str,
    customer_data: CustomerCreate,
    auth: Auth,
):
    customer = customers.get(customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    for existing_id, existing in customers.items():
        if (
            existing_id != customer_id
            and existing["email"] == str(customer_data.email)
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A customer with this email already exists.",
            )

    updated_customer = {
        "id": customer_id,
        "name": customer_data.name,
        "email": str(customer_data.email),
    }

    customers[customer_id] = updated_customer

    return updated_customer


@app.delete(
    "/v1/customers/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_customer(customer_id: str, auth: Auth):
    if customer_id not in customers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    del customers[customer_id]

    return Response(status_code=status.HTTP_204_NO_CONTENT)
