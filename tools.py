import asyncio

from mcp_client import MCPClient

from langchain.agents import tool
from pydantic import BaseModel, Field

class AirbnbRequest(BaseModel):
    location: str = Field(..., description="The location to search for Airbnb listings.")

@tool(args_schema=AirbnbRequest)
def airbnb_search(location: str) -> str:
    """Search for Airbnb listings based on location."""
    client = MCPClient()
    return asyncio.run(client.airbnb_search(location))