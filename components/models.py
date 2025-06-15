from typing import List, Dict, Optional, Any
from datetime import datetime

class MCPTool:
    def __init__(self,
                 id: str,
                 name: str,
                 capabilities: List[str],
                 description: str = "",
                 source_url: str = "",
                 version: str = "0.1.0",
                 installation_status: str = "not_installed",
                 performance_metrics: Optional[Dict[str, Any]] = None,
                 last_used: Optional[datetime] = None,
                 success_rate: float = 0.0):
        self.id: str = id
        self.name: str = name
        self.description: str = description
        self.capabilities: List[str] = capabilities
        self.source_url: str = source_url
        self.version: str = version
        self.installation_status: str = installation_status # "not_installed", "discovered", "installed", "failed"
        self.performance_metrics: Dict[str, Any] = performance_metrics if performance_metrics is not None else {}
        self.last_used: Optional[datetime] = last_used
        self.success_rate: float = success_rate

    def __repr__(self):
        return (f"MCPTool(id='{self.id}', name='{self.name}', capabilities={self.capabilities}, "
                f"status='{self.installation_status}', version='{self.version}')")

class ToolRating:
    def __init__(self,
                 score: float = 0.0,
                 compatibility: float = 0.0,
                 community_score: float = 0.0,
                 comments: str = ""):
        self.score: float = score
        self.compatibility: float = compatibility
        self.community_score: float = community_score
        self.comments: str = comments

    def __repr__(self):
        return (f"ToolRating(score={self.score}, compatibility={self.compatibility}, "
                f"community_score={self.community_score}, comments='{self.comments}')")

class ToolSpecification:
    def __init__(self,
                 tool_name: str,
                 capabilities_to_implement: List[str],
                 description: str = "",
                 api_dependencies: Optional[List[str]] = None,
                 implementation_details: str = ""): # Or prompt_for_llm
        self.tool_name: str = tool_name
        self.description: str = description
        self.capabilities_to_implement: List[str] = capabilities_to_implement
        self.api_dependencies: List[str] = api_dependencies if api_dependencies is not None else []
        self.implementation_details: str = implementation_details

    def __repr__(self):
        return (f"ToolSpecification(tool_name='{self.tool_name}', "
                f"capabilities_to_implement={self.capabilities_to_implement})")
