# Integration of Django and FastAPI for Authentication and Document Processing

This project demonstrates the integration of Django and FastAPI, where Django handles user authentication and FastAPI processes document uploads and queries. The FastAPI endpoints are secured with JWT tokens issued by Django.

## Prerequisites
- Python 3.8+
- Django
- FastAPI
- Uvicorn
- PyJWT
- SentenceTransformers
- FAISS
- PyPDF2
- Transformers

## Setup Instructions

### 1. Clone the Repository
```bash
$ git clone <repository_url>
$ cd <repository_folder>
```

### 2. Create a Virtual Environment
```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
```

### 3. Install Dependencies
```bash
$ pip install -r requirements.txt
```

### 4. Configure Django
1. Navigate to the Django project directory.
2. Set up the database by running:
```bash
$ python manage.py migrate
```
3. Create a superuser:
```bash
$ python manage.py createsuperuser
```
4. Run the Django development server on port `8001`:
```bash
$ python manage.py runserver 8001
```

### 5. Configure FastAPI
1. In a new terminal, activate the virtual environment:
```bash
$ source .venv/bin/activate
```
2. Navigate to the FastAPI project directory.
3. Run the FastAPI server on port `8000`:
```bash
$ uvicorn main:app --reload --port 8000
```

### 6. Endpoints

#### Django Endpoints (Port 8001)
1. **User Signup**
   - URL: `http://127.0.0.1:8001/signup/`
   - Method: `POST`
   - Payload:
     ```json
     {
         "username": "<username>",
         "password": "<password>"
     }
     ```
   - Response:
     ```json
     {
         "username": "<username>",
         "message": "User registered successfully."
     }
     ```

2. **User Login**
   - URL: `http://127.0.0.1:8001/login/`
   - Method: `POST`
   - Payload:
     ```json
     {
         "username": "<username>",
         "password": "<password>"
     }
     ```
   - Response:
     ```json
     {
         "refresh": "<refresh_token>",
         "access": "<access_token>"
     }
     ```

#### FastAPI Endpoints (Port 8000)

> **Note**: Add the `Authorization` header with `Bearer <access_token>` in requests to these endpoints.

1. **Upload Document**
   - URL: `http://127.0.0.1:8001/document/`
   - Method: `POST`
   - Headers:
     ```
     Authorization: Bearer <access_token>
     ```
   - Payload: Upload a file (`application/pdf` or `text/plain`).
   - Response:
     ```json
     {
         "message": "Document uploaded and processed successfully."
     }
     ```

2. **Query Document**
   - URL: `http://127.0.0.1:8001/query/`
   - Method: `POST`
   - Headers:
     ```
     Authorization: Bearer <access_token>
     ```
   - Payload:
     ```json
     {
         "question": "<your_question>"
     }
     ```
   - Response:
     ```json
     {
         "answer": "<answer_to_question>"
     }
     ```

### 7. Project Structure

```
.
├── django_project/
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── settings.py
│   └── ...
|── main.py
│   └── ...
├── requirements.txt
└── README.md
```

### 8. Notes
- Ensure the `SECRET_KEY` and `ALGORITHM` are the same in both Django and FastAPI.
- Use separate terminals to run Django and FastAPI servers simultaneously.
- The FastAPI endpoints will reject requests without a valid JWT token.

### 9. Testing the Integration
1. **Register and Login**:
   - Use Django `/signup/` and `/login/` endpoints to create a user and obtain a JWT token.Use access token for Authorization with Bearer.
2. **Upload Document**:
   - Use the FastAPI `/upload` endpoint to upload a document.
3. **Query Document**:
   - Use the FastAPI `/query` endpoint to ask questions about the uploaded document.

Happy Coding!

