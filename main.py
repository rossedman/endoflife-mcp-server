from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("endoflife")

async def get_end_of_life_data(url: str) -> dict[str, Any] | None:
    """
    Fetch end-of-life data from the specified URL.
    
    Args:
        url (str): The URL to fetch the end-of-life data from.
        
    Returns:
        dict[str, Any] | None: The end-of-life data or None if not found.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    return None
        
@mcp.tool()
async def get_endoflife(product: str) -> dict[str, Any] | None:
    """
    Tool to get end-of-life data for a specific product.
    
    Args:
        product (str): The name of the product to check.
        
    Returns:
        dict[str, Any] | None: The end-of-life data or None if not found.
    """
    url = f"https://endoflife.date/api/{product}.json"
    return await get_end_of_life_data(url)
        
if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')