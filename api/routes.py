import asyncio
import os
import logging
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from api.models import (
    FounderProfile, CompatibilityRequest, SingleAgentRequest,
    AssessmentResponse, CompatibilityResponse,
)
from agents.orchestrator import run_founder_analysis, run_single_agent_analysis, run_assessment_synthesis
from tools.github_analyzer import fetch_github_profile
from tools.resume_parser import extract_text_from_pdf

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "founderfit-api", "version": "0.1.0"}

@router.get("/health/llm")
async def health_check_llm():
    """Diagnostic endpoint: verifies the LLM pipeline can reach OpenRouter and get a response."""
    import traceback
    from autogen import ConversableAgent, LLMConfig

    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return {
            "status": "error",
            "problem": "OPENROUTER_API_KEY environment variable is not set",
            "fix": "Add OPENROUTER_API_KEY to your Railway environment variables",
            "api_key_present": False,
        }

    def _test_llm():
        try:
            llm_config = LLMConfig(
                {
                    "api_type": "openai",
                    "model": "google/gemini-2.0-flash-exp:free",
                    "api_key": api_key,
                    "base_url": "https://openrouter.ai/api/v1",
                },
                timeout=30,
            )
            agent = ConversableAgent(
                name="health_probe",
                system_message="You are a health check. Reply with exactly: OK",
                llm_config=llm_config,
            )
            response = agent.run(message="Reply with OK", max_turns=1, silent=True)
            response.process()
            if hasattr(response, "summary") and response.summary:
                return {"status": "ok", "response": response.summary[:100]}
            if hasattr(response, "messages") and response.messages:
                content = ""
                for m in response.messages:
                    if isinstance(m, dict):
                        content = m.get("content", "")
                    else:
                        content = getattr(m, "content", str(m))
                return {"status": "ok", "response": content[:100]}
            return {"status": "ok", "response": str(response)[:100]}
        except Exception as e:
            return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}

    result = await asyncio.to_thread(_test_llm)
    result["api_key_present"] = True
    result["api_key_length"] = len(api_key)
    # Show first 15 chars so we can confirm which key Railway is running with
    # (safe to expose — the secret is in the remaining 58 chars)
    result["api_key_prefix"] = api_key[:15]
    return result

async def _safe_github_fetch(username: str | None) -> dict | None:
    """Fetch GitHub profile, returning None silently on any failure."""
    if not username or not username.strip():
        return None
    try:
        data = await fetch_github_profile(username.strip())
        if "error" in data:
            logger.warning("GitHub fetch failed for %s: %s", username, data["error"])
            return None
        return data
    except Exception as e:
        logger.warning("GitHub fetch error for %s: %s", username, e)
        return None

@router.post("/upload/resume")
async def upload_resume(file: UploadFile = File(...)):
    """Accept a PDF (e.g. LinkedIn export) and return extracted text."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:  # 5 MB cap
        raise HTTPException(status_code=400, detail="File too large. Max 5 MB.")
    text = extract_text_from_pdf(contents)
    if not text:
        raise HTTPException(status_code=422, detail="Could not extract text from PDF. Make sure it is a text-based PDF, not a scanned image.")
    return {"text": text, "char_count": len(text)}

@router.post("/analyze/compatibility", response_model=CompatibilityResponse)
async def analyze_compatibility(request: CompatibilityRequest):
    try:
        # Fetch GitHub data in parallel if usernames provided
        github_data_a, github_data_b = await asyncio.gather(
            _safe_github_fetch(request.founder_a.github_username),
            _safe_github_fetch(request.founder_b.github_username),
        )
        # Allow caller to override with pre-fetched data
        github_data_a = github_data_a or request.github_data_a
        github_data_b = github_data_b or request.github_data_b

        # Run the sync agent pipeline in a thread so it doesn't block the event loop
        result = await asyncio.to_thread(
            run_founder_analysis,
            founder_a_profile=request.founder_a.model_dump(),
            founder_b_profile=request.founder_b.model_dump(),
            github_data_a=github_data_a,
            github_data_b=github_data_b,
            resume_text_a=request.resume_text_a,
            resume_text_b=request.resume_text_b,
            resume_pdf_text_a=request.resume_pdf_text_a,
            resume_pdf_text_b=request.resume_pdf_text_b,
        )
        return CompatibilityResponse(
            status=result["status"],
            summary=result.get("summary", ""),
            conversation=result.get("conversation", []),
            narrative=result.get("narrative"),
            stack=result.get("stack"),
            overall_score=result.get("overall_score"),
            dimensions=result.get("dimensions"),
            archetype=result.get("archetype"),
            friction_predictions=result.get("friction_predictions"),
            strengths=result.get("strengths"),
            recommendations=result.get("recommendations"),
        )
    except Exception as e:
        logger.error("Compatibility analysis failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/single")
async def analyze_single_agent(request: SingleAgentRequest):
    try:
        # Run in a thread â€” LLM calls block and would stall the event loop
        result = await asyncio.to_thread(
            run_single_agent_analysis,
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
    archetype = _classify_archetype(profile)
    dimensions = _score_dimensions(profile)

    # Run synthesis if any enrichment data is available
    synthesis = None
    github_data = None
    resume_text = getattr(profile, "resume_text", None)
    resume_pdf_text = getattr(profile, "resume_pdf_text", None)

    if profile.github_username:
        github_data = await _safe_github_fetch(profile.github_username)

    if github_data or resume_text or resume_pdf_text:
        try:
            synthesis = await asyncio.to_thread(
                run_assessment_synthesis,
                profile=profile.model_dump(),
                self_report_archetype=archetype,
                github_data=github_data,
                resume_text=resume_text,
                resume_pdf_text=resume_pdf_text,
            )
        except Exception as e:
            logger.warning("Assessment synthesis failed: %s", e)

    return AssessmentResponse(
        founder_name=profile.name,
        archetype=synthesis.get("final_archetype", archetype).lower().replace(" ", "_") if synthesis else archetype,
        dimensions=dimensions,
        status="profile_created",
        synthesis=synthesis,
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
    # execution_style: onboarding uses sprint/steady/flexible, assessment uses fast/moderate/deliberate
    if profile.execution_style in ("sprint", "fast"):
        scores["rapid_builder"] += 1; scores["growth_hunter"] += 1
    elif profile.execution_style in ("steady", "moderate"):
        scores["systems_operator"] += 1
    elif profile.execution_style == "deliberate":
        scores["systems_operator"] += 2; scores["vision_architect"] += 1
    return max(scores, key=scores.get)

def _score_dimensions(profile: FounderProfile) -> dict:
    return {
        "Execution Style": 85 if profile.execution_style in ("fast", "sprint") else 45 if profile.execution_style == "deliberate" else 55 if profile.execution_style == "steady" else 68,
        "Communication Cadence": 80 if profile.communication_style == "async" else 65 if profile.communication_style == "sync" else 72,
        "Decision-Making": 80 if profile.decision_speed == "fast" else 45 if profile.decision_speed == "deliberate" else 62,
        "Risk Posture": 85 if profile.risk_tolerance == "high" else 40 if profile.risk_tolerance == "low" else 62,
        "Conflict Resolution": 82 if profile.conflict_approach == "collaborative" else 65 if profile.conflict_approach == "compromising" else 52,
        "Tooling Affinity": 75 if profile.tooling_affinity == "pragmatic" else 60 if profile.tooling_affinity == "heavy" else 70,
        "Domain Coverage": 82 if profile.domain_expertise == "specialist" else 70 if profile.domain_expertise == "collaborative" else 65,
        # time_commitment: onboarding uses full_time/part_time/transitioning, assessment uses sprint/steady/flexible
        "Time & Energy": 85 if profile.time_commitment in ("full_time", "sprint") else 55 if profile.time_commitment in ("part_time", "flexible") else 65,
        "Ownership Philosophy": 80 if profile.ownership_philosophy == "flexible" else 70,
        "GTM Orientation": 78 if profile.gtm_orientation == "product_led" else 72 if profile.gtm_orientation == "sales_led" else 70,
        # Network Proximity: scored on data richness for individual assessment;
        # cross-profile comparison happens inside the compatibility agent pipeline
        "Network Proximity": 75 if profile.location and profile.timezone else 65 if profile.location or profile.timezone else 55,
    }
