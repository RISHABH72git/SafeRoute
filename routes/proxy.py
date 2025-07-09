import httpx
from fastapi import APIRouter, Request
from starlette.responses import Response

router = APIRouter(prefix="/proxy", tags=["Proxy"])


@router.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(full_path: str, request: Request):
    query_string = request.url.query
    target_url = f"www.google.com/{full_path}"
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
