import os
import requests
import asyncio
from mcp_client import MCPClient

from langchain.agents import tool
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()
class AirbnbRequest(BaseModel):
    location: str = Field(..., description="The location to search for Airbnb listings.")

class DuffelRequest(BaseModel):
    origin: str = Field(..., description="The origin airport code.")
    destination: str = Field(..., description="The destination airport code.")
    departure_date: str = Field(..., description="The departure date in YYYY-MM-DD format.")

@tool(args_schema=AirbnbRequest)
def airbnb_search(location: str) -> str:
    """Search for Airbnb listings based on location."""
    client = MCPClient()
    return asyncio.run(client.airbnb_search(location))

@tool(args_schema=DuffelRequest)
def duffel_search(origin: str, destination: str, departure_date: str) -> str:
    """Search for flights using Duffel API."""

    headers = {
        "Authorization": f"Bearer {os.getenv('DUFFEL_API_KEY')}",
        "Accept": "application/json",
        "Duffel-Version": "v2",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip"
    }

    data = {
        "data": {
            "slices": [
                {
                    "origin": origin,
                    "destination": destination,
                    "departure_date": departure_date
                }
            ],
            "passengers": [{"type": "adult"}],
            "max_connections": 0,
            "cabin_class": "economy"
        }
    }

    r = requests.post(
        "https://api.duffel.com/air/offer_requests?return_offers=true&supplier_timeout=10000", 
        headers=headers, 
        json=data,
        timeout=15
    )
    data = r.json()['data']

    # for item in data['slices'][0]['destination']['airports']:
    #     print(item)
    #     print()

    offers = []
    for offer in data['offers']:
        segment = offer['slices'][0]['segments'][0]

        offer = (
            f"ID: {offer['id']}\n"
            f"Total: {offer['total_amount']}\n"
            f"Currency: {offer['total_currency']}\n"
            f"Documents: {offer['supported_passenger_identity_document_types']}\n"
            f"Duration: {segment['duration']}\n"
            f"Destination: {segment['destination']['city_name']}\n"
            f"Airport: {segment['destination']['name']}\n"
            f"Time Zone: {segment['destination']['time_zone']}\n"
            f"Passengers: {segment['passengers']}\n"
            f"Departure: {segment['departing_at']}\n"
            f"Arrival: {segment['arriving_at']}\n"
            #f"Aircraft: {segment['aircraft']['name'] if segment['aircraft'] else 'N/A'}\n"
            f"--------------------"
        )

        offers.append(offer)
    
    return "\n".join(offers)