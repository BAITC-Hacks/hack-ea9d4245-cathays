from uuid import uuid4
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from ..execution.actions import ActionError

def install(app):
    @app.exception_handler(RequestValidationError)
    async def validation(_: Request, error: RequestValidationError):
        details = [{"loc": item["loc"], "msg": item["msg"], "type": item["type"]} for item in error.errors()]
        return JSONResponse(status_code=422, content={"code":"invalid_request","message":"Invalid request.","trace_id":str(uuid4()),"details":details})
    @app.exception_handler(HTTPException)
    async def http_error(_: Request, error: HTTPException):
        detail = error.detail if isinstance(error.detail, dict) else {"code": "request_failed", "message": str(error.detail)}
        return JSONResponse(status_code=error.status_code, content={**detail, "trace_id": str(uuid4())}, headers=error.headers)
    @app.exception_handler(ActionError)
    async def action_error(_: Request, error: ActionError):
        return JSONResponse(status_code=422, content={"code":error.code,"message":"The action could not be completed. Please check the supplied details.","trace_id":str(uuid4())})
    @app.exception_handler(Exception)
    async def unexpected(_: Request, __: Exception):
        return JSONResponse(status_code=500, content={"code":"internal_error","message":"Unexpected server error.","trace_id":str(uuid4())})
