from pydantic import BaseModel, Field, field_validator
from typing import Any, Literal

class FounderProfile(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: str | None = Field(default=None, max_length=254)
    role: str | None = Field(default=None, max_length=100)
    # Core 6 dimensions — validated against known values, default applied for unknowns
    decision_speed: Literal["fast", "moderate", "deliberate"] = "moderate"
    risk_tolerance: Literal["high", "medium", "moderate", "low"] = "moderate"
    communication_style: Literal["async", "sync", "balanced"] = "balanced"
    execution_style: Literal["sprint", "fast", "steady", "moderate", "deliberate", "flexible"] = "steady"
    conflict_approach: Literal["collaborative", "direct", "compromising", "avoidant"] = "collaborative"
    leadership_style: str | None = Field(default=None, max_length=100)
    ambition_level: Literal["high", "medium", "low"] = "high"
    time_commitment: Literal["full_time", "part_time", "transitioning", "sprint", "flexible"] = "full_time"
    # 4 new dimensions (PRD spec)
    tooling_affinity: Literal["heavy", "pragmatic", "minimal"] = "pragmatic"
    domain_expertise: Literal["generalist", "specialist", "collaborative"] = "generalist"
    ownership_philosophy: Literal["equal", "merit", "flexible"] = "flexible"
    gtm_orientation: Literal["product_led", "sales_led", "community_led"] = "product_led"
    # Optional enrichment
    domain_expertise_list: list[str] = []
    tool_preferences: list[str] = []
    github_username: str | None = Field(default=None, max_length=100)
    linkedin_url: str | None = Field(default=None, max_length=500)
    resume_text: str | None = Field(default=None, max_length=100_000)
    resume_pdf_text: str | None = Field(default=None, max_length=100_000)
    # Network Proximity signals
    location: str | None = Field(default=None, max_length=200)
    timezone: str | None = Field(default=None, max_length=50)

class CompatibilityRequest(BaseModel):
    founder_a: FounderProfile
    founder_b: FounderProfile
    github_data_a: dict | None = None
    github_data_b: dict | None = None
    resume_text_a: str | None = None
    resume_text_b: str | None = None
    resume_pdf_text_a: str | None = None
    resume_pdf_text_b: str | None = None

class SingleAgentRequest(BaseModel):
    agent_type: str
    input_data: dict[str, Any]

class AssessmentResponse(BaseModel):
    founder_name: str
    archetype: str
    dimensions: dict
    status: str
    synthesis: dict | None = None  # enriched output from Synthesis Agent

class CompatibilityResponse(BaseModel):
    status: str
    summary: str
    conversation: list[Any] = []
    narrative: str | None = None
    stack: list[Any] | None = None
    # Structured fields parsed from compatibility agent (BUG-024 fix)
    overall_score: int | None = None
    dimensions: dict | None = None
    archetype: str | None = None
    friction_predictions: list[Any] | None = None
    strengths: list[str] | None = None
    recommendations: list[str] | None = None
