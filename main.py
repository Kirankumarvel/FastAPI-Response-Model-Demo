from fastapi import FastAPI, status
from datetime import datetime
from models import UserCreate, UserOut

app = FastAPI()

# In-memory "database" for demonstration
fake_db = []

@app.post("/users/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """
    Create user with response_model demonstrating:
    - Serialization: Output to JSON
    - Validation: Check response matches UserOut
    - Filtering: Remove sensitive fields
    """
    
    # Internal data structure with sensitive information
    db_user = {
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "join_date": datetime.now(),
        # Sensitive fields that should NOT be returned
        "password": user_data.password,              # Raw password (BAD!)
        "hashed_password": f"hashed_{user_data.password}",  # Hashed but still sensitive
        "internal_id": "secret_123",                 # Internal identifier
        "api_key": "key_abc123"                      # Secret API key
    }
    fake_db.append(db_user)
    
    # response_model=UserOut automatically filters out:
    # - password, hashed_password, internal_id, api_key
    # Returns only: username, email, full_name, join_date
    return db_user

@app.get("/debug/users/")
async def debug_users():
    """
    Debug endpoint to show internal vs response data.
    Demonstrates what response_model filters out.
    """
    if not fake_db:
        return {"message": "No users created yet"}
    
    user = fake_db[0]
    return {
        "internal_data": user,
        "what_response_model_returns": {
            "username": user["username"],
            "email": user["email"],
            "full_name": user["full_name"],
            "join_date": user["join_date"]
        },
        "filtered_out_fields": [
            "password", "hashed_password", "internal_id", "api_key"
        ]
    }

@app.get("/")
async def root():
    return {"message": "FastAPI Response Model Demo - Check /docs for interactive API"}
