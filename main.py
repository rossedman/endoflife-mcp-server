from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("endoflife")

@mcp.tool()
async def product_list_all() -> list[str]:
    """
    Fetches a list of all products from the endoflife.date API.
    
    Returns:
        list[str]: A list of product names if successful, or an empty list if an error occurs.
    Raises:
        httpx.HTTPStatusError: If the API response indicates an error status code.
        httpx.RequestError: If there is a problem with the request.
        Exception: For any other unexpected errors.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://endoflife.date/api/all.json")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        print(f"Request error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    return []
        
@mcp.tool()
async def product_get_all(product: str) -> dict[str, Any] | None:
    """
    Fetches the end-of-life information for a given product from the endoflife.date API.
    
    Args:
        product (str): The name of the product to check for end-of-life status.
        
    Returns:
        dict[str, Any] | None: A dictionary containing the end-of-life information if successful,
                                or None if an error occurs.
    Raises:
        httpx.HTTPStatusError: If the API response indicates an error status code.
        httpx.RequestError: If there is a problem with the request.
        Exception: For any other unexpected errors.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://endoflife.date/api/{product}.json")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        print(f"Request error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    return None

@mcp.tool()
async def product_get_cycle(product: str, cycle: str) -> dict[str, Any] | None:
    """
    Fetches the end-of-life cycle information for a specific product and cycle from the endoflife.date API.
    
    Args:
        product (str): The name of the product to check.
        cycle (str): The specific cycle to check for the product.
        
    Returns:
        dict[str, Any] | None: A dictionary containing the cycle information if successful,
                                or None if an error occurs.
    Raises:
        httpx.HTTPStatusError: If the API response indicates an error status code.
        httpx.RequestError: If there is a problem with the request.
        Exception: For any other unexpected errors.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://endoflife.date/api/{product}/{cycle}.json")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        print(f"Request error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    return None
        
if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')