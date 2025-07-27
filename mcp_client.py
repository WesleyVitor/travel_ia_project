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
                title = item['demandStayListing']['description']['name']['localizedStringWithTranslationPreference']
                room_description = item['structuredContent']['primaryLine']
                localizacao = item['demandStayListing']['location']
                latitude = localizacao['coordinate']['latitude']
                longitude = localizacao['coordinate']['longitude']
                for_amount_adults = item['listingParamOverrides']['adults']
                checkin_date = item['listingParamOverrides']['checkin']
                checkout_date = item['listingParamOverrides']['checkout']
                id_item = item['id']
                url = item['url']

                response = await client.call_tool("airbnb_listing_details", {
                    "id": id_item,
                })
                
                # Get additional details
                policie_details = ""
                description_details = ""
                amenities_details = ""
                for value in json.loads(response.content[0].text)["details"]:
                    if value["id"] == "POLICIES_DEFAULT":
                        policie_details = value["houseRulesSections"]
                    elif value["id"] == "DESCRIPTION_DEFAULT":
                        description_details = value["htmlDescription"]["htmlText"]
                    elif value["id"] == "AMENITIES_DEFAULT":
                        amenities_details = value["seeAllAmenitiesGroups"]

                msg = (
                    f"ID do Item: {id_item}\n"
                    f"Preço: {preco}\n"
                    f"Detalhes do Preço: {preco_detail}\n"
                    f"Título: {title}\n"
                    f"Localização: {localizacao}\n"
                    f"Latitude: {latitude}\n"
                    f"Longitude: {longitude}\n"
                    f"Descrição do Quarto: {room_description}\n"
                    f"Quantidade de Adultos: {for_amount_adults}\n"
                    f"Data de Check-in: {checkin_date}\n"
                    f"Data de Check-out: {checkout_date}\n"
                    f"URL: {url}\n"
                    f"Políticas: {policie_details}\n"
                    f"Descrição Detalhada: {description_details}\n"
                    f"Comodidades: {amenities_details}\n"
                    "-----\n"
                )

                message.append(msg)
            
            
            final = "\n".join(message)

            return final