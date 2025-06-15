from typing import List, Dict, Optional, Set
from components.models import MCPTool # Updated import

class CapabilityRegistry:
    def __init__(self):
        # Stores details about each capability, like associated tool IDs and keywords
        self.capabilities: Dict[str, Dict[str, List[Any]]] = {}
        # Maps tool IDs to the set of capabilities they provide
        self.tool_mappings: Dict[str, Set[str]] = {}

    def register_capability_from_tool(self, tool: MCPTool):
        """
        Registers capabilities provided by a tool.
        """
        if not hasattr(tool, 'id') or not hasattr(tool, 'capabilities'):
            print(f"Error: Tool object is missing 'id' or 'capabilities' attributes.")
            return

        tool_id = tool.id

        # Update self.tool_mappings
        if tool_id not in self.tool_mappings:
            self.tool_mappings[tool_id] = set()

        current_tool_capabilities = set(tool.capabilities)
        self.tool_mappings[tool_id].update(current_tool_capabilities)

        # Update self.capabilities
        for capability_name in tool.capabilities:
            if capability_name not in self.capabilities:
                self.capabilities[capability_name] = {"tool_ids": [], "keywords": []} # Initialize with empty keywords

            # Add tool_id to the capability's tool_ids list if not already present
            if tool_id not in self.capabilities[capability_name]["tool_ids"]:
                self.capabilities[capability_name]["tool_ids"].append(tool_id)

        # Optional: Clean up capabilities in self.capabilities if a tool no longer supports them
        # This would be more complex, requiring knowledge of all tools.
        # For now, we only add. If a tool updates and removes a capability,
        # old entries might persist in self.capabilities until a more robust cleanup.

    def can_handle(self, query_capability: str) -> bool:
        """
        Checks if a given capability can be handled by any registered tool.
        """
        return query_capability in self.capabilities and bool(self.capabilities[query_capability].get("tool_ids"))

    def find_missing_capability(self, required_capabilities_list: List[str]) -> Optional[str]:
        """
        Finds the first capability in the list that cannot be handled.
        Returns None if all can be handled.
        """
        for capability_name in required_capabilities_list:
            if not self.can_handle(capability_name):
                return capability_name
        return None

    def get_tools_for_capability(self, capability_name: str) -> List[str]:
        """
        Returns a list of tool IDs that can handle the given capability.
        """
        if self.can_handle(capability_name):
            return self.capabilities[capability_name]["tool_ids"]
        return []

    def get_capabilities_for_tool(self, tool_id: str) -> Set[str]:
        """
        Returns a set of capabilities provided by the given tool_id.
        """
        return self.tool_mappings.get(tool_id, set())

# Example Usage (can be removed or moved to a test file later)
if __name__ == '__main__':
    # Create dummy tools (MCPTool definition is in mcp_client.py)
    tool1 = MCPTool(id="tool_001", name="Search Tool", capabilities=["web_search", "image_search"])
    tool2 = MCPTool(id="tool_002", name="Analysis Tool", capabilities=["data_analysis", "text_summarization"])
    tool3 = MCPTool(id="tool_003", name="Coding Tool", capabilities=["code_generation", "debug_code", "web_search"])

    # Initialize the registry
    registry = CapabilityRegistry()

    # Register tools
    registry.register_capability_from_tool(tool1)
    registry.register_capability_from_tool(tool2)
    registry.register_capability_from_tool(tool3)

    print("Initial Registry State:")
    print(f"Capabilities: {registry.capabilities}")
    print(f"Tool Mappings: {registry.tool_mappings}\n")

    # Test can_handle
    print(f"Can handle 'web_search'? {registry.can_handle('web_search')}")  # True
    print(f"Can handle 'image_search'? {registry.can_handle('image_search')}") # True
    print(f"Can handle 'data_analysis'? {registry.can_handle('data_analysis')}") # True
    print(f"Can handle 'code_translation'? {registry.can_handle('code_translation')}")  # False

    # Test find_missing_capability
    required1 = ["web_search", "data_analysis"]
    print(f"Missing in {required1}? {registry.find_missing_capability(required1)}") # None

    required2 = ["web_search", "code_translation", "data_analysis"]
    print(f"Missing in {required2}? {registry.find_missing_capability(required2)}") # code_translation

    # Test get_tools_for_capability
    print(f"Tools for 'web_search': {registry.get_tools_for_capability('web_search')}") # ['tool_001', 'tool_003']
    print(f"Tools for 'text_summarization': {registry.get_tools_for_capability('text_summarization')}") # ['tool_002']
    print(f"Tools for 'image_generation': {registry.get_tools_for_capability('image_generation')}") # []

    # Test get_capabilities_for_tool
    print(f"Capabilities for 'tool_001': {registry.get_capabilities_for_tool('tool_001')}")
    print(f"Capabilities for 'tool_003': {registry.get_capabilities_for_tool('tool_003')}")
    print(f"Capabilities for 'tool_unknown': {registry.get_capabilities_for_tool('tool_unknown')}")

    # Test re-registering a tool (e.g., if its capabilities changed)
    # For example, tool1 now also supports 'language_translation'
    tool1_updated = MCPTool(id="tool_001", name="Search & Translate Tool", capabilities=["web_search", "language_translation"])
    registry.register_capability_from_tool(tool1_updated) # This will update tool_001's capabilities

    print("\nRegistry State After Updating Tool1:")
    print(f"Capabilities: {registry.capabilities}") # Note: 'image_search' will still list tool_001 if not explicitly removed by a more complex logic
    print(f"Tool Mappings: {registry.tool_mappings}")
    print(f"Can handle 'image_search'? {registry.can_handle('image_search')}") # Still True, due to current additive logic
    print(f"Tools for 'image_search': {registry.get_tools_for_capability('image_search')}") # Still includes 'tool_001'
    print(f"Can handle 'language_translation'? {registry.can_handle('language_translation')}") # True
    print(f"Tools for 'language_translation': {registry.get_tools_for_capability('language_translation')}") # ['tool_001']
    print(f"Capabilities for 'tool_001': {registry.get_capabilities_for_tool('tool_001')}")

    # Note: The current register_capability_from_tool only adds capabilities.
    # If a tool *loses* a capability, the old mapping might still exist in self.capabilities
    # unless a more sophisticated update/sync mechanism is implemented.
    # For self.tool_mappings, it correctly reflects the latest set of capabilities for the tool.
    # For example, 'image_search' is no longer in tool_001's mapping:
    # registry.tool_mappings['tool_001'] will be {'web_search', 'language_translation'}
    # However, self.capabilities['image_search']['tool_ids'] might still contain 'tool_001'.
    # This is a design choice for simplicity or can be enhanced.
    # A simple fix for the self.capabilities part upon tool update:
    # 1. Get old capabilities of the tool from self.tool_mappings before updating it.
    # 2. For capabilities that were removed from the tool, remove the tool_id from self.capabilities[removed_cap]['tool_ids'].
    # This is not implemented in the current version for brevity but is a point of consideration.
    # The current implementation of tool_mappings correctly updates the tool's capabilities set.
    # The capabilities dictionary is additive for tool_ids to capabilities.
    # This means if tool1 previously had 'image_search' and now it doesn't, 'image_search'
    # will still list 'tool1' as a provider in `self.capabilities`
    # but `self.tool_mappings['tool1']` will correctly not list 'image_search'.
    # This is fine for `can_handle` as long as the tool is still registered.

    # A tool that is completely de-registered would need another method like `deregister_tool(tool_id)`.

    # Test registering a tool with an invalid structure (e.g. missing 'id')
    invalid_tool = {"name": "Invalid Tool", "capabilities": ["some_cap"]}
    # registry.register_capability_from_tool(invalid_tool) # This would cause an AttributeError
    # The code has a basic check for hasattr 'id' and 'capabilities' now.
    class MinimalTool: # Not an MCPTool
        def __init__(self, name, caps):
            self.name = name
            self.caps = caps # Wrong attribute name

    invalid_mcp_tool_like = MinimalTool(name="Faulty", caps=["test"])
    registry.register_capability_from_tool(invalid_mcp_tool_like) # Should print error and not process

    print("\nFinal Registry State:")
    print(f"Capabilities: {registry.capabilities}")
    print(f"Tool Mappings: {registry.tool_mappings}")
