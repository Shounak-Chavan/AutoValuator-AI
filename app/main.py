from fastapi import FastAPI
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware
from app.api import routes_auth, routes_predict
from app.middleware.logging_middleware import LoggingMiddleware
from app.core.exceptions import register_exception_handlers
from app.db.init_db import init_db
from app.api import routes_predictions



@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    init_db()
    yield
    # shutdown (nothing for now)


app = FastAPI(
    title="Car Price Prediction Api",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

# middleware
app.add_middleware(LoggingMiddleware)

# routes
app.include_router(routes_auth.router, tags=["Authorization"])
app.include_router(routes_predict.router, tags=["Prediction"])
app.include_router(routes_predictions.router , tags = ['List Predictions'])

# monitoring
Instrumentator().instrument(app).expose(app)

# exception handlers
register_exception_handlers(app)

@app.get("/")
def root():
    return {"message": "AutoValuator API Running"}
