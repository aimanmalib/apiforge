"""Minimal app that mounts the example routes: ``uvicorn main:app --reload``."""

from fastapi import FastAPI

from routes import router

app = FastAPI(title="E-Commerce API (APIForge example)")
app.include_router(router)
