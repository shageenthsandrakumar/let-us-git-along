from pydantic import BaseModel
from typing import Any

class FounderProfile(BaseModel):
    name: str
    email: str | None = None
    role: str | None = None
    decision_speed: str = "moderate"
    risk_tolerance: str = "moderate"
    communication_style: str = "balanced"
    execution_style: str = "steady"
    conflict_approach: str = "collaborative"
    leadership_style: str | None = None
    ambition_level: str = "high"
    time_commitment: str = "full_time"
    domain_expertise: list[str] = []
    tool_preferences: list[str] = []
    github_username: str | None = None
    linkedin_url: str | None = None

class CompatibilityRequest(BaseModel):
    founder_a: FounderProfile
    founder_b: FounderProfile
    github_data_a: dict | None = None
    github_data_b: dict | None = None

class SingleAgentRequest(BaseModel):
    agent_type: str
    input_data: dict[str, Any]

class AssessmentResponse(BaseModel):
    founder_name: str
    archetype: str
    dimensions: dict[str, int]
    status: str

class CompatibilityResponse(BaseModel):
    status: str
    summary: str
    conversation: list[Any] = []
