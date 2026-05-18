from pydantic import BaseModel
from typing import Any

class FounderProfile(BaseModel):
    name: str
    email: str | None = None
    role: str | None = None
    # Core 6 dimensions
    decision_speed: str = "moderate"
    risk_tolerance: str = "moderate"
    communication_style: str = "balanced"
    execution_style: str = "steady"
    conflict_approach: str = "collaborative"
    leadership_style: str | None = None
    ambition_level: str = "high"
    time_commitment: str = "full_time"
    # 4 new dimensions (PRD spec)
    tooling_affinity: str = "pragmatic"        # heavy | pragmatic | minimal
    domain_expertise: str = "generalist"       # generalist | specialist | collaborative
    ownership_philosophy: str = "flexible"     # equal | merit | flexible
    gtm_orientation: str = "product_led"       # product_led | sales_led | community_led
    # Optional enrichment
    domain_expertise_list: list[str] = []
    tool_preferences: list[str] = []
    github_username: str | None = None
    linkedin_url: str | None = None
    resume_text: str | None = None
    resume_pdf_text: str | None = None
    # Network Proximity signals
    location: str | None = None      # e.g. "New York, NY"
    timezone: str | None = None      # e.g. "EST", "PST", "GMT"

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
