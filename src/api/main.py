from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.api import api_router
from src.api.v1.errors import add_exception_handlers

app = FastAPI(title="LOG430-Labo-03 API", openapi_url="/api/v1/openapi.json")

# Add exception handlers
add_exception_handlers(app)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(api_router, prefix="/api/v1")
