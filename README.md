# FastAPI Response Model Demo

A FastAPI application demonstrating the powerful `response_model` feature for output control, validation, and security filtering.

---

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

---

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Kirankumarvel/fastapi-response-model-demo.git
   cd fastapi-response-model-demo
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies with email support**
   ```bash
   pip install "pydantic[email]"
   pip install fastapi==0.104.1 uvicorn==0.24.0 pydantic==2.6.4 pydantic-extra-types==2.10.5
   ```

   **Or use requirements.txt:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 📦 Dependencies

The project uses the following compatible versions:
- `fastapi==0.104.1` - The web framework for building APIs
- `uvicorn==0.24.0` - ASGI server for running FastAPI applications
- `pydantic==2.6.4` - Data validation with email support
- `pydantic-extra-types==2.10.5` - Additional validation types

**Important:** The `pydantic[email]` installation includes email validation support needed for `EmailStr` type.

---

## 🚀 Running the Application

1. **Start the development server**
   ```bash
   uvicorn main:app --reload --reload-exclude venv
   ```

2. **Access the application**
   - API: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - Alternative docs: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 API Endpoints

### POST /users/
Create a new user with validated request body and controlled response.

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "join_date": "2023-12-07T10:30:00.000000"
}
```
> **Note:** The `password` field is filtered out from the response for security!

---

## 🎯 Key Concept: response_model Power

### What `response_model` Does:
1. **Serialization**: Converts output data to JSON
2. **Validation**: Checks that returned data matches the model (catches bugs!)
3. **Filtering**: Removes any data not defined in the response model
4. **Documentation**: Generates accurate OpenAPI schema

#### Security Example
```python
# Internal data structure (has sensitive fields)
internal_data = {
    "username": "johndoe",
    "email": "john@example.com",
    "password": "secret",          # Sensitive!
    "hashed_password": "abc123",   # Sensitive!
    "join_date": "2023-12-07T10:30:00"
}

# response_model=UserOut filters out to:
{
    "username": "johndoe",
    "email": "john@example.com",
    "join_date": "2023-12-07T10:30:00"
}
```

---

## 🧪 Testing the API

### Test 1: Valid Request (Shows Filtering)
```bash
curl -X POST "http://127.0.0.1:8000/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```
**Response:** (Note: no password fields!)
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "join_date": "2023-12-07T10:30:00.000000"
}
```

### Test 2: View Internal Data vs Response
```bash
curl http://127.0.0.1:8000/debug/users/
```
Shows the internal data structure vs what gets returned.

---

## 📁 Project Structure

```
fastapi-response-model-demo/
├── main.py          # Main application file
├── models.py        # Pydantic model definitions
├── requirements.txt # Project dependencies
├── README.md        # Project documentation
└── venv/            # Virtual environment (gitignored)
```

---

## 🔧 Code Explanation

### models.py
```python
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    """
    Input model for user creation.
    Includes password for registration.
    """
    username: str
    email: EmailStr  # Requires pydantic[email] installation
    password: str
    full_name: Optional[str] = None

class UserOut(BaseModel):
    """
    Output model for user responses.
    - Excludes password fields for security
    - Validates response data structure
    - Filters unwanted fields automatically
    """
    username: str
    email: EmailStr  # Requires pydantic[email] installation
    full_name: Optional[str] = None
    join_date: datetime

    class Config:
        from_attributes = True  # ORM compatibility
```

### main.py
```python
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
```

---

## 🎓 Learning Points

### 1. **Security Filtering**
```python
# Internal data has sensitive fields
internal_data = {
    "email": "user@example.com",
    "password": "secret",          # Filtered out
    "api_key": "abc123"            # Filtered out
}

# response_model returns only allowed fields
return internal_data  # Only email returned!
```

### 2. **Validation (Catches Bugs!)**
```python
# If you accidentally return wrong data structure:
return {"wrong_field": "value"}  # FastAPI will raise validation error!

# This helps catch internal bugs before they reach clients
```

### 3. **Email Validation with pydantic[email]**
```python
# Requires: pip install "pydantic[email]"
from pydantic import EmailStr

class User(BaseModel):
    email: EmailStr  # Validates email format automatically
```

---

## 🔧 Troubleshooting

### Common Issues:

1. **EmailStr import error**
   ```bash
   # Install with email support:
   pip install "pydantic[email]"
   ```

2. **Version compatibility issues**
   ```bash
   # Use the exact versions:
   pip install fastapi==0.104.1 uvicorn==0.24.0 pydantic==2.6.4 pydantic-extra-types==2.10.5
   ```

3. **Response validation errors**
   - Ensure returned data matches response_model structure

4. **Unexpected field filtering**
   - Remember: response_model filters out undefined fields

---

## 📚 Learning Resources

- [FastAPI Response Model](https://fastapi.tiangolo.com/tutorial/response-model/)
- [Pydantic Email Validation](https://docs.pydantic.dev/concepts/types/#emailstr)
- [Pydantic Installation with Extras](https://docs.pydantic.dev/concepts/installation/)

---

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- FastAPI team for the powerful response_model feature
- Pydantic team for robust validation and serialization
- Uvicorn team for the ASGI server
- Python community for ongoing support
