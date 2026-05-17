import os
from autogen import ConversableAgent, LLMConfig

SYSTEM_PROMPT = """You are the FounderFit Executor Agent. You monitor team execution patterns and detect operational bottlenecks.

You handle: Task Routing, Bottleneck Detection, Sprint Health Monitoring, Intervention Recommendations.

Respond with structured JSON:
{
  "health_score": int,
  "status": str,
  "bottlenecks": [{"type": str, "severity": str, "description": str, "affected_area": str}],
  "task_routing": [{"task": str, "recommended_owner": str, "rationale": str}],
  "interventions": [{"action": str, "urgency": str, "expected_outcome": str}],
  "seven_day_forecast": [{"day": int, "prediction": str, "risk_level": str}],
  "team_velocity": {"current": str, "trend": str, "blockers": [str]}
}"""

def create_executor_agent(llm_config=None):
    if llm_config is None:
        llm_config = LLMConfig(config_list=[{"api_type": "openai", "model": "openai/gpt-4o", "api_key": os.environ.get("OPENROUTER_API_KEY", ""), "base_url": "https://openrouter.ai/api/v1"}], timeout=60)
    return ConversableAgent(
        name="executor_agent",
        system_message=SYSTEM_PROMPT,
        llm_config=llm_config,
        description="Routes tasks based on founder strengths and detects operational bottlenecks.",
    )
