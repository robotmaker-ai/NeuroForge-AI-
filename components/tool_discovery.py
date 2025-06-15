from typing import List, Dict, Any, Optional
from datetime import datetime # Added for MCPTool's last_used
from components.models import MCPTool, ToolRating

class ToolDiscovery:

    _MOCK_GITHUB_API_RESPONSE = [
        {
            "id": 12345,
            "name": "mcp-server-python",
            "full_name": "example_org/mcp-server-python",
            "description": "A general purpose MCP server framework in Python.",
            "html_url": "https://github.com/example_org/mcp-server-python",
            "stargazers_count": 150,
            "forks_count": 30,
            "updated_at": "2023-10-01T10:00:00Z",
            "language": "Python"
        },
        {
            "id": 67890,
            "name": "weather-mcp-tool",
            "full_name": "weather_tools/weather-mcp-tool",
            "description": "An MCP tool to fetch weather forecasts.",
            "html_url": "https://github.com/weather_tools/weather-mcp-tool",
            "stargazers_count": 75,
            "forks_count": 15,
            "updated_at": "2023-09-15T14:30:00Z",
            "language": "Python"
        },
        {
            "id": 13579,
            "name": "image-processing-mcp-plugin",
            "full_name": "image_plugins/image-processing-mcp-plugin",
            "description": "MCP plugin for advanced image processing capabilities.",
            "html_url": "https://github.com/image_plugins/image-processing-mcp-plugin",
            "stargazers_count": 90,
            "forks_count": 20,
            "updated_at": "2023-08-20T12:00:00Z",
            "language": "Python"
        },
        {
            "id": 24680,
            "name": "text_summarization_tool_for_mcp",
            "full_name": "nlp_tools/text_summarization_tool_for_mcp",
            "description": "A powerful tool for summarizing text, compatible with MCP.",
            "html_url": "https://github.com/nlp_tools/text_summarization_tool_for_mcp",
            "stargazers_count": 120,
            "forks_count": 25,
            "updated_at": "2023-11-01T18:00:00Z",
            "language": "Python"
        }
    ]

    def __init__(self):
        """
        Initializes the ToolDiscovery component.
        Future: May take API keys or other configurations.
        """
        print("ToolDiscovery initialized.")
        # Example: self.github_token = os.getenv("GITHUB_TOKEN")

    def search_github(self, capability_query: str) -> List[MCPTool]:
        """
        Searches for tools on GitHub based on a capability query by filtering a mock API response.
        """
        print(f"Simulating GitHub search for tools related to: '{capability_query}'...")

        results_from_api = self._MOCK_GITHUB_API_RESPONSE
        discovered_tools: List[MCPTool] = []

        query_terms = [term.lower() for term in capability_query.replace("_", " ").split()]

        for item in results_from_api:
            # Simple filtering logic:
            # Check if any query term is in the repo name or description
            # Or if capability_query is a generic term like "mcp tool" or "mcp server"
            item_name_lower = item['name'].lower()
            item_desc_lower = item['description'].lower()

            match = False
            if any(term in item_name_lower for term in query_terms) or \
               any(term in item_desc_lower for term in query_terms):
                match = True
            elif "mcp tool" in capability_query.lower() or "mcp server" in capability_query.lower() or "mcp plugin" in capability_query.lower():
                 if "mcp" in item_name_lower or "mcp" in item_desc_lower: # General MCP related tools
                    match = True

            if match:
                # Heuristic for capabilities:
                # If a specific term from query matches tool name, use that term.
                # Otherwise, use the original capability_query, or parse from name if obvious.
                assigned_capabilities = []
                for term in query_terms:
                    if term in item_name_lower or term in item_desc_lower:
                        if term not in assigned_capabilities: # Avoid duplicates from query terms
                             # Try to map common terms to standardized capabilities
                            if term == "weather":
                                assigned_capabilities.append("weather_api")
                            elif term == "image" and "processing" in item_desc_lower:
                                assigned_capabilities.append("image_processing")
                            elif term == "summarization":
                                 assigned_capabilities.append("text_summarization")
                            elif term == "server" and "mcp" in item_name_lower : # generic server
                                assigned_capabilities.append("mcp_server_framework")
                            elif term not in ["mcp", "tool", "plugin", "python", "server"]: # filter out generic query terms
                                assigned_capabilities.append(term) # Add specific term

                if not assigned_capabilities: # Fallback
                    if "weather" in item_name_lower:
                        assigned_capabilities.append("weather_api")
                    elif "image_processing" in item_name_lower or ("image" in item_name_lower and "processing" in item_desc_lower):
                        assigned_capabilities.append("image_processing")
                    elif "summarization" in item_name_lower:
                        assigned_capabilities.append("text_summarization")
                    elif "mcp-server" in item_name_lower:
                         assigned_capabilities.append("mcp_server_framework")
                    else: # Default if no specific capability could be derived
                        assigned_capabilities.append(item['name'].replace('-', '_')) # e.g., "mcp_server_python"

                # Ensure the original capability_query if it's a recognized one and not too generic
                if capability_query in ["weather_api", "text_summarization", "image_processing"] and capability_query not in assigned_capabilities:
                    assigned_capabilities.append(capability_query)

                # Remove duplicates just in case
                assigned_capabilities = sorted(list(set(cap for cap in assigned_capabilities if cap)))


                tool = MCPTool(
                    id=str(item['id']),
                    name=item['name'],
                    description=item['description'],
                    capabilities=assigned_capabilities if assigned_capabilities else [capability_query], # Fallback to query
                    source_url=item['html_url'],
                    version="0.1.0", # Default, or parse if available (e.g., from tags)
                    installation_status="discovered",
                    performance_metrics={'stars': item['stargazers_count'], 'forks': item['forks_count']},
                    last_used=None, # datetime.strptime(item['updated_at'], "%Y-%m-%dT%H:%M:%SZ") could be an option
                    success_rate=0.0
                )
                discovered_tools.append(tool)
                print(f"  Found and processed: {tool.name} with capabilities: {tool.capabilities}")

        if not discovered_tools:
            print(f"  No tools matched the query '{capability_query}' in the mock GitHub data.")

        return discovered_tools

    def search_npm(self, capability_query: str) -> List[MCPTool]:
        """
        Searches for tools on npm (Node Package Manager) based on a capability query.
        Placeholder implementation.
        """
        print(f"Searching npm for tools related to: '{capability_query}'...")
        # Simulate API call delay (optional)
        # import time; time.sleep(1)

        # For now, returns an empty list as per instructions
        print("Mock npm search found no tools.")
        return []

    def evaluate_tool(self, tool_data: Dict[str, Any]) -> ToolRating: # Or tool: MCPTool
        """
        Evaluates a discovered tool based on its metadata.
        Placeholder implementation.
        `tool_data` is a dictionary, which might represent raw data from an API before an MCPTool object is fully formed.
        """
        print(f"Evaluating tool data: {tool_data.get('name', 'Unknown Tool')}...")

        # Simulate evaluation logic
        rating = ToolRating() # Create a default rating

        if tool_data.get("source") == "github":
            rating.score = 0.6 # Arbitrary score
            rating.compatibility = 0.7
            rating.community_score = tool_data.get("stars", 0) / 1000.0 # Example: score based on stars
            rating.comments = "Evaluation based on mock GitHub data."
        elif tool_data.get("source") == "npm":
            rating.score = 0.5
            rating.compatibility = 0.6
            rating.community_score = tool_data.get("downloads", 0) / 10000.0
            rating.comments = "Evaluation based on mock npm data."
        else:
            rating.comments = "Tool source unknown, default evaluation."

        print(f"Evaluation result for '{tool_data.get('name', 'Unknown Tool')}': Score {rating.score}")
        return rating

# Example Usage
if __name__ == '__main__':
    print("--- ToolDiscovery Example Usage ---")
    discovery_service = ToolDiscovery()
    print("\n")

    # Test search_github
    print("--- GitHub Search ---")
    queries_to_test = ["weather", "mcp tool", "image processing", "text_summarization", "nonexistent_query", "mcp server"]

    for query in queries_to_test:
        print(f"Testing GitHub search with query: '{query}'")
        gh_tools = discovery_service.search_github(query)
        if gh_tools:
            for tool in gh_tools:
                print(f"  - Found: {tool.name} (ID: {tool.id})")
                print(f"    Description: {tool.description}")
                print(f"    Capabilities: {tool.capabilities}")
                print(f"    Source: {tool.source_url}")
                print(f"    Status: {tool.installation_status}")
                print(f"    Metrics: {tool.performance_metrics}")
                print(f"    Repr: {tool!r}") # Test the __repr__
        else:
            print(f"  No tools found on GitHub for '{query}'.")
        print("-" * 20)
    print("\n")

    # Test search_npm (remains unchanged, but good to keep in test)
    print("--- NPM Search ---")
    npm_query = "react_component_for_data_visualization"
    npm_tools = discovery_service.search_npm(npm_query)
    if npm_tools:
        for tool in npm_tools:
            print(f"Found on npm: {tool.name} (ID: {tool.id})")
    else:
        print(f"No tools found on npm for '{npm_query}'.")
    print("\n")

    # Test evaluate_tool
    print("--- Tool Evaluation ---")
    mock_github_tool_data_for_eval = {
        "name": "Cool GitHub Library",
        "source": "github",
        "description": "A very useful library from GitHub.",
        "stars": 1500, # Example metric
        "license": "MIT"
    }
    gh_rating = discovery_service.evaluate_tool(mock_github_tool_data_for_eval)
    print(f"Rating for '{mock_github_tool_data_for_eval['name']}': Score={gh_rating.score}, Compatibility={gh_rating.compatibility}, Community={gh_rating.community_score}, Comments='{gh_rating.comments}'")
    print("\n")

    mock_npm_tool_data_for_eval = {
        "name": "Awesome NPM Package",
        "source": "npm",
        "description": "A popular package from npm.",
        "downloads": 50000, # Example metric
        "version": "1.2.3"
    }
    npm_rating = discovery_service.evaluate_tool(mock_npm_tool_data_for_eval)
    print(f"Rating for '{mock_npm_tool_data_for_eval['name']}': Score={npm_rating.score}, Compatibility={npm_rating.compatibility}, Community={npm_rating.community_score}, Comments='{npm_rating.comments}'")
    print("\n")

    unknown_tool_data = {"name": "Mysterious Tool"}
    unknown_rating = discovery_service.evaluate_tool(unknown_tool_data)
    print(f"Rating for '{unknown_tool_data['name']}': {unknown_rating}")

    print("\n--- ToolDiscovery Example Usage Complete ---")
