from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from modal.functions import FunctionCall

from app.auth.auth_bearer import AuthBearer

router = APIRouter()

@router.get(
	"/modal/{call_id}",
	dependencies=[
		Depends(
			AuthBearer(),
		),
	],
)
async def get_brain_chat_results(call_id: str):
	function_call = FunctionCall.from_id(call_id)
	try:
		result = function_call.get(timeout=0)
	except TimeoutError:
		return JSONResponse(content="", status_code=202)
	return result