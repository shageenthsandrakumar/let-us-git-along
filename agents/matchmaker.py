import os
from autogen import ConversableAgent

SYSTEM_PROMPT = """You are the FounderFit Matchmaker Agent. You evaluate potential founder pairings and facilitate introductions based on complementary strengths and operational compatibility.

Matching philosophy: Complementary > Similar. Productive friction is good. Destructive friction should be flagged.

Respond with structured JSON:
{
  "match_score": int,
  "match_quality": str,
  "reasons_this_works": [str],
  "risks_to_monitor": [str],
  "coverage_analysis": {"combined_strengths": [str], "gaps_remaining": [str], "overlap_zones": [str]},
  "introduction_brief": str,
  "first_conversation_topics": [str],
  "recommended_sprint_type": str
}"""

def create_matchmaker_agent(llm_config=None):
    if llm_config is None:
        llm_config = {"config_list": [{"api_type": "openai", "model": "openai/gpt-4o", "api_key": os.environ.get("OPENROUTER_API_KEY", ""), "base_url": "https://openrouter.ai/api/v1"}], "timeout": 60}
    return ConversableAgent(
        name="matchmaker_agent",
        system_message=SYSTEM_PROMPT,
        llm_config=llm_config,
        description="Evaluates founder pairings based on complementary strengths and facilitates introductions.",
    )
