from uuid import uuid4
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

def install(app):
    @app.exception_handler(RequestValidationError)
    async def validation(_: Request, error: RequestValidationError):
        return JSONResponse(422,{"code":"invalid_request","message":"Invalid request.","trace_id":str(uuid4()),"details":error.errors()})
    @app.exception_handler(Exception)
    async def unexpected(_: Request, __: Exception):
        return JSONResponse(500,{"code":"internal_error","message":"Unexpected server error.","trace_id":str(uuid4())})
