import chromadb
from fastapi import APIRouter, Depends

from settings import CHROMA_DATABASE, CHROMA_HOST, CHROMA_TENANT, CHROMA_TOKEN

router = APIRouter()

# Global client instance
CLIENT = None


async def get_chroma_client():
    global CLIENT
    if CLIENT is None:
        CLIENT = await chromadb.AsyncHttpClient(
            ssl=True,
            host=CHROMA_HOST,
            tenant=CHROMA_TENANT,
            database=CHROMA_DATABASE,
            headers={"x-chroma-token": CHROMA_TOKEN},
        )
    return CLIENT


@router.get("/collections")
async def list_collections(client=Depends(get_chroma_client)):
    collections = await client.list_collections()
    return {"collections": [{"name": collection.name, "id": collection.id} for collection in collections]}
