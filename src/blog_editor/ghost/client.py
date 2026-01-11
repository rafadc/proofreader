import jwt
import httpx
from datetime import datetime
from .models import Post, PostsResponse

class GhostClient:
    def __init__(self, url: str, api_key: str):
        self.url = url
        self.api_key = api_key
        self.token = self._generate_token()
        self.headers = {"Authorization": f"Ghost {self.token}"}

    def _generate_token(self) -> str:
        id, secret = self.api_key.split(':')
        iat = int(datetime.now().timestamp())
        header = {'alg': 'HS256', 'typ': 'JWT', 'kid': id}
        payload = {
            'iat': iat,
            'exp': iat + 5 * 60,
            'aud': '/admin/'
        }
        return jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)

    async def get_posts(self, limit: int = 15, status: str = "all") -> list[Post]:
        async with httpx.AsyncClient() as client:
             # This is a simplification. URL construction should be more robust.
            api_url = f"{self.url}/ghost/api/admin/posts/"
            params = {"limit": limit, "formats": "html,mobiledoc"}
            if status != "all":
                params["filter"] = f"status:{status}"
            
            response = await client.get(
                api_url, 
                headers=self.headers, 
                params=params # type: ignore
            )
            response.raise_for_status()
            data = response.json()
            return PostsResponse(**data).posts

    async def get_post(self, post_id: str) -> Post:
        async with httpx.AsyncClient() as client:
            api_url = f"{self.url.rstrip('/')}/ghost/api/admin/posts/{post_id}/"
            params = {"formats": "html,mobiledoc"}
            response = await client.get(
                api_url, 
                headers=self.headers, 
                params=params # type: ignore
            )
            response.raise_for_status()
            data = response.json()
            return Post(**data.get("posts")[0])
            
    async def update_post(self, post_id: str, updated_data: dict, updated_at: datetime) -> Post:
        async with httpx.AsyncClient() as client:
            api_url = f"{self.url.rstrip('/')}/ghost/api/admin/posts/{post_id}/"
            # Ghost requires the updated_at timestamp to match the server's to prevent conflicts
            # We must pass the original updated_at back
            if "posts" not in updated_data:
                 updated_data = {"posts": [updated_data]}
            
            # Ensure updated_at is properly formatted
            updated_data["posts"][0]["updated_at"] = updated_at.isoformat().replace("+00:00", "Z")

            response = await client.put(api_url, headers=self.headers, json=updated_data)
            response.raise_for_status()
            data = response.json()
            return Post(**data.get("posts")[0])
