import httpx
from fastapi import Request
from sqlalchemy.orm import Session, joinedload
from starlette.responses import Response
from fastapi import APIRouter, Depends
from models.global_model import ApiKey, Proxy, ProxyPath
from utils.common import get_api_key
from utils.db import get_db
router = APIRouter(prefix="/proxy", tags=["Proxy"])


@router.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(full_path: str, request: Request, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    apikey = db.query(ApiKey).filter(ApiKey.apikey == api_key).first()
    proxy_data = (db.query(Proxy).join(Proxy.paths).filter(Proxy.user_id == apikey.user_id,
                                                           ProxyPath.path == full_path, ).options(
        joinedload(Proxy.paths)).first())
    if not proxy_data:
        return Response(content=f"Proxy host not found", status_code=404)
    query_string = request.url.query
    target_url = f"{proxy_data.host}/{full_path}"
    if query_string:
        target_url += f"?{query_string}"
    try:
        headers = dict(request.headers)
        headers.pop("host", None)
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=await request.body()
            )
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    except httpx.RequestError as e:
        return Response(content=f"Proxy request failed: {str(e)}", status_code=500)
