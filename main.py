import asyncio
from fastapi import FastAPI
from typing import List, Dict, Any, Optional

from components.mcp_client import MCPClient, MCPTool
from components.capability_registry import CapabilityRegistry

# --- Global Variables ---
# These will be initialized by setup_essential_tools()
mcp_client: MCPClient
capability_registry: CapabilityRegistry

# --- Essential Tools Setup ---
ESSENTIAL_TOOLS_LIST = [
    "web_search",
    "gmail_api",
    "google_drive",
    "news_api",
    "weather_api"
]

def setup_essential_tools():
    """
    Initializes and registers essential tools for the MCP system.
    Returns the initialized client and registry.
    """
    print("Setting up essential tools...")
    client = MCPClient()
    registry = CapabilityRegistry()

    for tool_name in ESSENTIAL_TOOLS_LIST:
        tool_id = f"{tool_name}_tool"
        tool_display_name = f"{tool_name.replace('_', ' ').title()} Tool"
        tool_capabilities = [tool_name]

        tool = MCPTool(id=tool_id, name=tool_display_name, capabilities=tool_capabilities)

        client.register_tool(tool)
        # print(f"Registered '{tool.name}' with MCPClient.")
        registry.register_capability_from_tool(tool)
        # print(f"Registered capabilities of '{tool.name}' with CapabilityRegistry.")

    print("--- Essential Tools Setup Complete ---")

    # Verification (optional, can be commented out for production)
    # print("\nVerifying tool registration in CapabilityRegistry:")
    # for tool_name_as_capability in ESSENTIAL_TOOLS_LIST:
    #     if registry.can_handle(tool_name_as_capability):
    #         print(f"SUCCESS: Capability '{tool_name_as_capability}' is handled.")
    #     else:
    #         print(f"ERROR: Capability '{tool_name_as_capability}' is NOT handled.")

    return client, registry

# Initialize client and registry globally
mcp_client, capability_registry = setup_essential_tools()

# --- FastAPI App Instantiation ---
app = FastAPI()

# --- Placeholder Functions ---
def analyze_capabilities(query: str) -> List[str]:
    """
    Analyzes the query to determine required capabilities.
    Placeholder implementation.
    """
    print(f"Analyzing capabilities for query: '{query}'")
    if "news" in query.lower():
        return ["news_api", "text_summarization"] # news_api is essential, text_summarization might be missing
    elif "weather" in query.lower():
        return ["weather_api"]
    elif "search" in query.lower() or "find" in query.lower():
        return ["web_search"]
    return ["unknown_capability"] # Default if no keywords match

async def discover_tools_placeholder(capabilities_needed: List[str]) -> List[MCPTool]:
    """
    Discovers tools that can provide the given capabilities.
    Placeholder: Returns a dummy tool if 'text_summarization' is needed.
    """
    print(f"Discovering tools for capabilities: {capabilities_needed}")
    discovered_tools = []
    if "text_summarization" in capabilities_needed:
        # Simulate discovering a new tool for text_summarization
        summarization_tool = MCPTool(
            id="summarizer_001",
            name="Text Summarization Tool",
            capabilities=["text_summarization"]
        )
        discovered_tools.append(summarization_tool)
        print(f"Discovered tool: {summarization_tool.name}")
    return discovered_tools

async def integrate_tool_placeholder(tool: MCPTool):
    """
    Integrates a new tool into the system.
    Placeholder implementation.
    """
    print(f"Integrating tool: {tool.name} (ID: {tool.id}) with capabilities: {tool.capabilities}")
    # In a real scenario, this might involve downloading, configuring, etc.
    await asyncio.sleep(0.1) # Simulate async work

async def execute_query_placeholder(query: str, client: MCPClient, primary_capability: Optional[str]) -> Dict[str, Any]:
    """
    Executes the query using the MCPClient.
    Placeholder implementation.
    """
    print(f"Executing query: '{query}' using primary capability: '{primary_capability}'")
    if primary_capability and client.capabilities.get(primary_capability):
        # Attempt to use the first tool found for that capability
        return await client.execute_task(primary_capability, {"query": query})
    elif primary_capability:
        print(f"Warning: Primary capability '{primary_capability}' identified, but no tool available in client.")
        return {"status": "error", "result": f"No tool available for primary capability: {primary_capability}"}
    else:
        print("No primary capability identified or capability not supported for execution.")
        return {"status": "error", "result": "Could not determine primary capability or capability not supported."}

# --- FastAPI Endpoint ---
@app.post("/query")
async def process_query_endpoint(query: str): # Using query: str for simplicity (form data)
    """
    Processes a query by analyzing capabilities, discovering and integrating missing tools (mocked),
    and then executing the query (mocked).
    """
    global mcp_client, capability_registry # Ensure we're using the global instances

    print(f"\nReceived query: '{query}'")

    # 1. Analyze capabilities
    required_capabilities = analyze_capabilities(query)
    print(f"Required capabilities: {required_capabilities}")

    # 2. Find missing capabilities
    # find_missing_capability returns the *first* missing one or None.
    # For this logic, we want to see if *any* capability in required_capabilities is missing.
    # A more robust check might be needed if we want to discover tools for *all* missing ones at once.

    missing_capability_found: Optional[str] = None
    all_required_available = True
    for cap in required_capabilities:
        if not capability_registry.can_handle(cap):
            missing_capability_found = cap # Record the first one found for the response
            all_required_available = False
            print(f"Missing capability: {cap}")
            break # For this flow, we handle one missing capability discovery at a time

    # 3. Initialize newly integrated tools count
    newly_integrated_tools_count = 0

    # 4. If a capability is missing, try to discover and integrate tools
    if not all_required_available and missing_capability_found:
        print(f"Attempting to discover tools for missing capability: {missing_capability_found}")
        # Pass a list with the specific missing capability we are trying to resolve now
        discovered_tools = await discover_tools_placeholder([missing_capability_found])

        if discovered_tools:
            print(f"Discovered {len(discovered_tools)} tool(s). Integrating them...")
            for tool in discovered_tools:
                await integrate_tool_placeholder(tool)
                mcp_client.register_tool(tool)
                capability_registry.register_capability_from_tool(tool)
                newly_integrated_tools_count += 1
                print(f"Successfully registered: {tool.name}")
            # Re-check if the specific missing capability is now handled
            if capability_registry.can_handle(missing_capability_found):
                print(f"Capability '{missing_capability_found}' is now handled.")
            else:
                print(f"WARN: Capability '{missing_capability_found}' still not handled after integration attempt.")
        else:
            print(f"No tools discovered for missing capability: {missing_capability_found}")

    # 5. Execute the query
    # Determine a primary capability for execution (e.g., the first one from the required list)
    primary_capability_for_execution = required_capabilities[0] if required_capabilities else None

    # We need to re-evaluate if the primary capability (or all) are now available
    final_execution_capability = None
    if primary_capability_for_execution and capability_registry.can_handle(primary_capability_for_execution):
        final_execution_capability = primary_capability_for_execution
    else:
        # Fallback or alternative logic if primary is still missing
        # For now, we'll just note it won't execute if primary is not ready
        print(f"Primary capability '{primary_capability_for_execution}' not available for execution.")

    if final_execution_capability:
        result = await execute_query_placeholder(query, mcp_client, final_execution_capability)
    else:
        result = {"status": "error", "result": f"Could not execute query. Primary capability '{primary_capability_for_execution}' not available."}


    # 6. Return response
    response_data = {
        "response": result,
        "new_tools_integrated": newly_integrated_tools_count,
        "required_capabilities": required_capabilities,
        "initial_missing_capability": missing_capability_found, # The first one we tried to resolve
        "primary_capability_executed": final_execution_capability
    }
    print(f"Sending response: {response_data}")
    return response_data

# --- Uvicorn Runner ---
# This is for local development. In production, you'd use Gunicorn or another ASGI server.
if __name__ == "__main__":
    import uvicorn

    print("Starting FastAPI application with Uvicorn...")
    # Note: The global mcp_client and capability_registry are set up when the module is imported.
    # If setup_essential_tools had async operations, it would need to be run in an event loop
    # or via FastAPI's startup events. For now, it's synchronous.
    uvicorn.run(app, host="0.0.0.0", port=8000)

# To run this:
# 1. Ensure fastapi and uvicorn are installed: pip install fastapi uvicorn
# 2. Save as main.py
# 3. Run from terminal: python main.py
# 4. Send a POST request to http://localhost:8000/query (e.g., using curl or Postman)
#    Example using curl:
#    curl -X POST "http://localhost:8000/query?query=tell%20me%20the%20latest%20news" -H "accept: application/json"
#    curl -X POST "http://localhost:8000/query?query=what%20is%20the%20weather" -H "accept: application/json"
#    curl -X POST "http://localhost:8000/query?query=search%20for%20cats" -H "accept: application/json"
#    curl -X POST "http://localhost:8000/query?query=summarize%20this%20news" -H "accept: application/json" (to test discovery)
