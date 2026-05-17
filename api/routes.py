from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.models import (
    FounderProfile, CompatibilityRequest, SingleAgentRequest,
    AssessmentResponse, CompatibilityResponse,
)
from agents.orchestrator import run_founder_analysis, run_single_agent_analysis

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "founderfit-api", "version": "0.1.0"}

@router.post("/analyze/compatibility", response_model=CompatibilityResponse)
async def analyze_compatibility(request: CompatibilityRequest):
    try:
        result = run_founder_analysis(
            founder_a_profile=request.founder_a.model_dump(),
            founder_b_profile=request.founder_b.model_dump(),
            github_data_a=request.github_data_a,
            github_data_b=request.github_data_b,
        )
        return CompatibilityResponse(
            status=result["status"],
            summary=result.get("summary", ""),
            conversation=result.get("conversation", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/single")
async def analyze_single_agent(request: SingleAgentRequest):
    try:
        result = run_single_agent_analysis(
            agent_type=request.agent_type,
            input_data=request.input_data,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assessment/submit")
async def submit_assessment(profile: FounderProfile):
    return AssessmentResponse(
        founder_name=profile.name,
        archetype=_classify_archetype(profile),
        dimensions=_score_dimensions(profile),
        status="profile_created",
    )

@router.get("/archetypes")
async def list_archetypes():
    return {
        "archetypes": [
            {"id": "rapid_builder", "name": "Rapid Builder", "description": "Ships fast, iterates aggressively, tolerates tech debt", "best_for": ["consumer apps", "marketplaces", "MVPs"]},
            {"id": "systems_operator", "name": "Systems Operator", "description": "Infrastructure-first, scalability-focused, methodical", "best_for": ["enterprise SaaS", "fintech", "infrastructure"]},
            {"id": "experimental_hacker", "name": "Experimental Hacker", "description": "Explores widely, prototypes fast, low attachment to code", "best_for": ["R&D", "AI/ML products", "innovation labs"]},
            {"id": "vision_architect", "name": "Vision Architect", "description": "Designs for the future, documentation-heavy, strategic", "best_for": ["platform companies", "developer tools", "deeptech"]},
            {"id": "product_strategist", "name": "Product Strategist", "description": "Feature-driven, user-facing, pragmatic trade-offs", "best_for": ["B2B SaaS", "productivity tools", "vertical software"]},
            {"id": "growth_hunter", "name": "Growth Hunter", "description": "Metrics-obsessed, A/B test heavy, conversion-focused", "best_for": ["consumer growth", "e-commerce", "ad-tech"]},
        ]
    }

def _classify_archetype(profile: FounderProfile) -> str:
    scores = {"rapid_builder": 0, "systems_operator": 0, "vision_architect": 0, "product_strategist": 0, "experimental_hacker": 0, "growth_hunter": 0}
    if profile.decision_speed == "fast":
        scores["rapid_builder"] += 2; scores["growth_hunter"] += 1
    elif profile.decision_speed == "deliberate":
        scores["systems_operator"] += 2; scores["vision_architect"] += 1
    if profile.risk_tolerance == "high":
        scores["experimental_hacker"] += 2; scores["rapid_builder"] += 1
    elif profile.risk_tolerance == "low":
        scores["systems_operator"] += 2
    if profile.communication_style == "async":
        scores["vision_architect"] += 1; scores["systems_operator"] += 1
    elif profile.communication_style == "sync":
        scores["rapid_builder"] += 1; scores["growth_hunter"] += 1
    if profile.gtm_orientation == "product_led":
        scores["product_strategist"] += 2; scores["growth_hunter"] += 1
    elif profile.gtm_orientation == "sales_led":
        scores["growth_hunter"] += 2
    if profile.tooling_affinity == "heavy":
        scores["systems_operator"] += 2
    elif profile.tooling_affinity == "minimal":
        scores["experimental_hacker"] += 1; scores["rapid_builder"] += 1
    if profile.domain_expertise == "specialist":
        scores["systems_operator"] += 1; scores["vision_architect"] += 1
    elif profile.domain_expertise == "generalist":
        scores["experimental_hacker"] += 1; scores["rapid_builder"] += 1
    if profile.execution_style == "sprint":
        scores["rapid_builder"] += 1; scores["growth_hunter"] += 1
    elif profile.execution_style == "steady":
        scores["systems_operator"] += 2
    return max(scores, key=scores.get)

def _score_dimensions(profile: FounderProfile) -> dict:
    return {
        "Execution Style": 85 if profile.execution_style == "fast" else 55 if profile.execution_style == "steady" else 68,
        "Communication Cadence": 80 if profile.communication_style == "async" else 65 if profile.communication_style == "sync" else 72,
        "Decision-Making": 80 if profile.decision_speed == "fast" else 45 if profile.decision_speed == "deliberate" else 62,
        "Risk Posture": 85 if profile.risk_tolerance == "high" else 40 if profile.risk_tolerance == "low" else 62,
        "Conflict Resolution": 82 if profile.conflict_approach == "collaborative" else 65 if profile.conflict_approach == "compromising" else 52,
        "Tooling Affinity": 75 if profile.tooling_affinity == "pragmatic" else 60 if profile.tooling_affinity == "heavy" else 70,
        "Domain Coverage": 82 if profile.domain_expertise == "specialist" else 70 if profile.domain_expertise == "collaborative" else 65,
        "Time & Energy": 78 if profile.time_commitment == "full_time" else 55 if profile.time_commitment == "part_time" else 65,
        "Ownership Philosophy": 80 if profile.ownership_philosophy == "flexible" else 70,
        "GTM Orientation": 78 if profile.gtm_orientation == "product_led" else 72 if profile.gtm_orientation == "sales_led" else 70,
    }
