import os
import asyncio
import requests
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
import mcp.types as types
from mcp.server.stdio import stdio_server
from pydantic import BaseModel, Field

# 1. Initialize the Swiggy Instamart MCP Server
server = Server("swiggy-instamart-mcp-server")

# Swiggy API Base URL configuration (To be updated with actual production endpoints post-onboarding)
SWIGGY_API_BASE_URL = "https://api.swiggy.com/v1/instamart" 

# 2. Define Input Argument Schemas using Pydantic
class SearchItemArgs(BaseModel):
    item_name: str = Field(description="The grocery or daily essential item to search on Instamart (e.g., 'milk', 'eggs', 'bread')")

class AddToCartArgs(BaseModel):
    item_id: str = Field(description="The unique identifier/SKU of the item to add to the cart")
    quantity: int = Field(default=1, description="The quantity of the item to be added")

# 3. Expose capabilities/tools to the LLM Client
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="search_instamart_item",
            description="Search for items, groceries, and essentials available on Swiggy Instamart.",
            inputSchema=SearchItemArgs.model_json_schema(),
        ),
        types.Tool(
            name="add_to_instamart_cart",
            description="Add a specific grocery item with the required quantity to the user's Swiggy Instamart cart.",
            inputSchema=AddToCartArgs.model_json_schema(),
        ),
    ]

# 4. Implement Tool Execution Logic
@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    
    if name == "search_instamart_item":
        if not arguments or "item_name" not in arguments:
            raise ValueError("Missing 'item_name' argument")
        
        item_name = arguments["item_name"]
        
        # Mocking the Swiggy Instamart API catalog response for initial testing/validation
        mock_catalog_response = [
            {"item_id": "instamart_sku_101", "name": f"Fresh {item_name.capitalize()}", "price_in_inr": 45, "in_stock": True},
            {"item_id": "instamart_sku_102", "name": f"Organic {item_name.capitalize()}", "price_in_inr": 70, "in_stock": True}
        ]
        
        return [
            types.TextContent(
                type="text",
                text=f"Successfully fetched items for '{item_name}' from Swiggy Instamart:\n{mock_catalog_response}"
            )
        ]

    elif name == "add_to_instamart_cart":
        if not arguments or "item_id" not in arguments:
            raise ValueError("Missing 'item_id' argument")
            
        item_id = arguments["item_id"]
        quantity = arguments.get("quantity", 1)
        
        # Mocking cart modification response
        return [
            types.TextContent(
                type="text",
                text=f"Success: Added Item ID '{item_id}' (Quantity: {quantity}) to your Swiggy Instamart cart."
            )
        ]
        
    else:
        raise ValueError(f"Unknown or unsupported tool name: {name}")

# 5. Main entry point to run the server over standard I/O (Stdio)
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="swiggy-instamart-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
