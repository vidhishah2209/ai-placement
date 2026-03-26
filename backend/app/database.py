import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL, USE_LOCAL_DB

# SQLite doesn't support the json_serializer/deserializer args the same way
engine_kwargs = dict(echo=True)

if not USE_LOCAL_DB:
    engine_kwargs["json_serializer"] = lambda obj: json.dumps(obj, ensure_ascii=False)
    engine_kwargs["json_deserializer"] = json.loads

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Dependency for FastAPI routes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session