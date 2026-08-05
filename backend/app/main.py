"""ASGI and AWS Lambda entry points."""

from mangum import Mangum

from app.core.application import create_app

app = create_app()
handler = Mangum(app, lifespan="auto")
