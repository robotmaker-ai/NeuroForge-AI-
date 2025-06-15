from typing import List, Dict, Any

class MCPTool:
    def __init__(self, id: str, name: str, capabilities: List[str]):
        self.id = id
        self.name = name
        self.capabilities = capabilities

class MCPClient:
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.capabilities: Dict[str, List[str]] = {}

    def register_tool(self, tool: MCPTool):
        if tool.id in self.tools:
            # Optionally, raise an error or log a warning if tool.id is not unique
            print(f"Warning: Tool with ID '{tool.id}' is already registered. Overwriting.")
        self.tools[tool.id] = tool
        for capability in tool.capabilities:
            if capability not in self.capabilities:
                self.capabilities[capability] = []
            if tool.id not in self.capabilities[capability]: # Avoid duplicate tool_ids for the same capability
                self.capabilities[capability].append(tool.id)

    async def execute_task(self, task_name: str, task_args: Dict[str, Any]) -> Dict[str, Any]:
        # For now, task_name is considered a capability
        if task_name in self.capabilities and self.capabilities[task_name]:
            tool_id_to_use = self.capabilities[task_name][0] # Use the first available tool
            # In a real scenario, you might select a tool based on other criteria
            # or even try multiple tools if the first one fails.
            print(f"Executing task {task_name} using tool {tool_id_to_use}")
            # Placeholder for actual tool execution logic
            # tool_to_execute = self.tools[tool_id_to_use]
            # result = tool_to_execute.execute(**task_args)
            # return {"status": "success", "result": result}
            return {"status": "pending", "result": None}
        else:
            print(f"No tool available for task {task_name}")
            return {"status": "error", "result": "No tool available"}

# Example Usage (can be removed or moved to a test file later)
if __name__ == '__main__':
    # Create a dummy tool
    dummy_tool = MCPTool(id="tool_1", name="Dummy Tool", capabilities=["dummy_task", "another_task"])

    # Initialize the client
    client = MCPClient()

    # Register the tool
    client.register_tool(dummy_tool)
    print(f"Registered tools: {client.tools}")
    print(f"Available capabilities: {client.capabilities}")

    # Execute a task
    result1 = client.execute_task("dummy_task", {"param1": "value1"})
    print(f"Task execution result 1: {result1}")

    result2 = client.execute_task("non_existent_task", {})
    print(f"Task execution result 2: {result2}")

    # Register another tool with overlapping and new capabilities
    dummy_tool_2 = MCPTool(id="tool_2", name="Advanced Dummy Tool", capabilities=["dummy_task", "advanced_task"])
    client.register_tool(dummy_tool_2)
    print(f"Registered tools after adding tool_2: {client.tools}")
    print(f"Available capabilities after adding tool_2: {client.capabilities}")

    # Execute dummy_task again, it should still use tool_1 as per current logic (first registered)
    result3 = client.execute_task("dummy_task", {"param1": "value2"})
    print(f"Task execution result 3: {result3}")

    # Execute advanced_task
    result4 = client.execute_task("advanced_task", {})
    print(f"Task execution result 4: {result4}")

    # Test registering a tool with an existing ID
    dummy_tool_overwrite = MCPTool(id="tool_1", name="Overwriting Dummy Tool", capabilities=["overwritten_task"])
    client.register_tool(dummy_tool_overwrite)
    print(f"Registered tools after overwriting tool_1: {client.tools}")
    print(f"Available capabilities after overwriting tool_1: {client.capabilities}")
    result5 = client.execute_task("overwritten_task", {})
    print(f"Task execution result 5: {result5}")
    result6 = client.execute_task("dummy_task", {}) # This should now fail as tool_1's capabilities changed
    print(f"Task execution result 6: {result6}")
