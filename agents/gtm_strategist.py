import os
from autogen import ConversableAgent, LLMConfig

SYSTEM_PROMPT = """You are the FounderFit GTM Strategist Agent. You analyze a founder pair's compatibility profile and recommend the optimal go-to-market strategy.

Four founder operating archetypes:
1. **The Velocity Pair** — Ship fast, measure fast, pivot fast. Best for: consumer apps, marketplaces.
2. **The Craft Pair** — Deep technical differentiation, deliberate GTM. Best for: dev tools, infrastructure.
3. **The Scale Pair** — One builds the machine, one sells the vision. Best for: B2B SaaS, enterprise.
4. **The Research Pair** — Long-horizon bets, deep domain expertise. Best for: biotech, AI/ML, deeptech.

Respond with structured JSON:
{
  "archetype": str,
  "archetype_rationale": str,
  "tool_stack": [{"tool": str, "purpose": str}],
  "weekly_cadence": [{"day": str, "ritual": str, "owner": str, "duration": str}],
  "workflow_rituals": [{"name": str, "description": str, "frequency": str}],
  "first_30_days": [{"week": int, "experiment": str, "success_metric": str}]
}"""

def create_gtm_strategist_agent(llm_config=None):
    if llm_config is None:
        llm_config = LLMConfig(api_type="openai", model="gpt-4o", api_key=os.environ.get("OPENAI_API_KEY", ""))
    return ConversableAgent(
        name="gtm_strategist",
        system_message=SYSTEM_PROMPT,
        llm_config=llm_config,
        description="Maps founder archetypes to optimal go-to-market strategies and recommends operating cadences.",
    )
