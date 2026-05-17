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
    return max(scores, key=scores.get)

def _score_dimensions(profile: FounderProfile) -> dict:
    return {
        "decision_velocity": 75 if profile.decision_speed == "fast" else 45,
        "risk_tolerance": 80 if profile.risk_tolerance == "high" else 40,
        "communication": 70,
        "execution_pace": 85 if profile.execution_style == "sprint" else 55,
        "vision_alignment": 70,
        "conflict_style": 65,
    }
