import json
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    async def airbnb_search(self, location: str) -> None:
        """Connect to the MCP server."""
        async with AsyncExitStack() as stack:
            server_params = StdioServerParameters(
                command="npx",
                args=["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
            )

            stdio_transport = await stack.enter_async_context(stdio_client(server_params))
            stdio, write = stdio_transport

            client: Optional[ClientSession] = await stack.enter_async_context(ClientSession(stdio, write))
            await client.initialize()
            
            response = await client.call_tool("airbnb_search", {
                "location": location,
            })
            message = []

            for item in json.loads(response.content[0].text)['searchResults']:
                preco = item['structuredDisplayPrice']['primaryLine']['accessibilityLabel']
                preco_detail = item['structuredDisplayPrice']['explanationData']['priceDetails']
                descricao = item['demandStayListing']['description']['name']['localizedStringWithTranslationPreference']
                localizacao = item['demandStayListing']['location']
                latitude = localizacao['coordinate']['latitude']
                longitude = localizacao['coordinate']['longitude']

                msg = (
                    f"Preço: {preco}\n"
                    f"Detalhes do Preço: {preco_detail}\n"
                    f"Descrição: {descricao}\n"
                    f"Localização: {localizacao}\n"
                    f"Latitude: {latitude}\n"
                    f"Longitude: {longitude}\n"
                    "-----\n"
                )

                message.append(msg)
    
            final = "\n".join(message)

            return final