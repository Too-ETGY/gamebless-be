from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.schemas.common import ApiResponse


class AppException(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        body = ApiResponse(success=False, message=exc.message, data=None)
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        # Catches FastAPI/Starlette's own HTTPException (401, 403, 404, etc.)
        # and reshapes it into your consistent format
        messages = {
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not found",
            405: "Method not allowed",
        }
        message = messages.get(exc.status_code, exc.detail or "HTTP error")
        body = ApiResponse(success=False, message=message, data=None)
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        first = errors[0]
        loc = first.get("loc", [])

        if "authorization" in loc:
            message = "Authorization header is required"
        else:
            field = " → ".join(str(l) for l in loc if l != "body")
            message = f"Validation error on '{field}': {first.get('msg')}"

        body = ApiResponse(success=False, message=message, data=None)
        return JSONResponse(status_code=422, content=body.model_dump())

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        body = ApiResponse(success=False, message="Internal server error", data=None)
        return JSONResponse(status_code=500, content=body.model_dump())