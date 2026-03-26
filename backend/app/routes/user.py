from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User
import uuid

router = APIRouter()


@router.post("/create-user")
async def create_user(
    name: str,
    email: str,
    target_role: str = "Software Engineer",
    db: AsyncSession = Depends(get_db)
):
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        return {
            "message": "User already exists",
            "user_id": str(existing_user.id),
            "name": existing_user.name,
            "email": existing_user.email,
            "target_role": existing_user.target_role,
        }

    # Create new user
    new_user = User(
        id=str(uuid.uuid4()),
        name=name,
        email=email,
        target_role=target_role
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user_id": str(new_user.id),
        "name": new_user.name,
        "email": new_user.email,
        "target_role": new_user.target_role,
    }


@router.post("/login")
async def login(
    email: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if not user:
        return {"success": False, "message": "No account found with this email."}

    return {
        "success": True,
        "user_id": str(user.id),
        "name": user.name,
        "email": user.email,
        "target_role": user.target_role,
    }
