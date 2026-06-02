from fastapi import APIRouter, Depends
from app.services.websearch_service import websearch_service
from app.core.dependencies import get_current_user
from app.models.user import User
from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    num_results: int = 5


class ExtractRequest(BaseModel):
    url: str


router = APIRouter()


@router.post("/search")
async def search_web(req: SearchRequest, current_user: User = Depends(get_current_user)):
    results = await websearch_service.search(req.query, req.num_results)
    formatted = await websearch_service.format_search_results(req.query, results)
    return {"results": results, "formatted": formatted, "total": len(results)}


@router.post("/extract")
async def extract_content(req: ExtractRequest, current_user: User = Depends(get_current_user)):
    return await websearch_service.extract_content(req.url)
