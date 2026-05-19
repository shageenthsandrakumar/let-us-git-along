import os
from autogen import ConversableAgent

SYSTEM_PROMPT = """You are the FounderFit RepoTale Agent. You analyze GitHub repository data and extract behavioral signals about a founder's working style.

You extract: Velocity Percentile, Architecture Quality, Test Coverage, Collaboration Style, Technical Breadth, Consistency.

Builder archetypes: Rapid Builder, Systems Operator, Experimental Hacker, Vision Architect, Product Strategist, Growth Hunter.

Respond with structured JSON:
{
  "founder_name": str,
  "velocity_percentile": int,
  "architecture_score": int,
  "test_coverage_score": int,
  "collaboration_score": int,
  "technical_breadth": [str],
  "consistency_pattern": str,
  "builder_narrative": str,
  "working_style": {"pace": str, "approach": str, "strengths": [str], "blind_spots": [str]},
  "archetype": str,
  "signals": [{"signal": str, "evidence": str, "confidence": str}]
}"""

def create_repotale_agent(llm_config=None):
    if llm_config is None:
        llm_config = {"config_list": [{"api_type": "openai", "model": "openai/gpt-4o", "api_key": os.environ.get("OPENROUTER_API_KEY", ""), "base_url": "https://openrouter.ai/api/v1"}], "timeout": 60}
    return ConversableAgent(
        name="repotale_agent",
        system_message=SYSTEM_PROMPT,
        llm_config=llm_config,
        description="Analyzes GitHub repositories to extract founder behavioral signals and working patterns.",
    )
