import os
import json
import logging
from autogen import ConversableAgent, LLMConfig
from agents.compatibility import create_compatibility_agent
from agents.gtm_strategist import create_gtm_strategist_agent
from agents.repotale import create_repotale_agent
from agents.matchmaker import create_matchmaker_agent
from agents.executor import create_executor_agent

logger = logging.getLogger(__name__)

def get_llm_config():
    return LLMConfig(
        config_list=[{
            "api_type": "openai",
            "model": "openai/gpt-4o",
            "api_key": os.environ.get("OPENROUTER_API_KEY", ""),
            "base_url": "https://openrouter.ai/api/v1",
        }],
        timeout=60,
    )

def _run_agent(agent, message):
    """Run a single agent and return its text response."""
    try:
        response = agent.run(message=message, max_turns=1, silent=True)
        response.process()
        if hasattr(response, "summary") and response.summary:
            return response.summary
        if hasattr(response, "messages") and response.messages:
            return response.messages[-1].get("content", "")
        return str(response)
    except Exception as e:
        logger.error("Agent %s failed: %s", agent.name, e)
        return None

def run_founder_analysis(founder_a_profile, founder_b_profile, github_data_a=None, github_data_b=None):
    llm_config = get_llm_config()

    base_prompt = f"""Analyze the compatibility between these two founders:

**Founder A:**
{json.dumps(founder_a_profile, indent=2)}

**Founder B:**
{json.dumps(founder_b_profile, indent=2)}
"""
    if github_data_a:
        base_prompt += f"\n**Founder A GitHub Data:**\n{json.dumps(github_data_a, indent=2)}\n"
    if github_data_b:
        base_prompt += f"\n**Founder B GitHub Data:**\n{json.dumps(github_data_b, indent=2)}\n"

    conversation = []
    compat_summary = None

    agents_to_run = [
        ("compatibility", create_compatibility_agent),
        ("gtm_strategist", create_gtm_strategist_agent),
        ("matchmaker", create_matchmaker_agent),
    ]

    if github_data_a or github_data_b:
        agents_to_run.append(("repotale", create_repotale_agent))

    for agent_type, creator in agents_to_run:
        try:
            agent = creator(llm_config)
            result = _run_agent(agent, base_prompt)
            if result:
                conversation.append({"agent": agent_type, "response": result})
                if agent_type == "compatibility":
                    compat_summary = result
        except Exception as e:
            logger.error("Failed to create or run agent %s: %s", agent_type, e)
            conversation.append({"agent": agent_type, "response": f"Agent unavailable: {str(e)}"})

    if not compat_summary and conversation:
        compat_summary = conversation[0]["response"]

    return {
        "status": "complete",
        "conversation": conversation,
        "summary": compat_summary or "Analysis could not be completed.",
    }

def run_single_agent_analysis(agent_type, input_data):
    llm_config = get_llm_config()
    agent_map = {
        "compatibility": create_compatibility_agent,
        "gtm": create_gtm_strategist_agent,
        "repotale": create_repotale_agent,
        "matchmaker": create_matchmaker_agent,
        "executor": create_executor_agent,
    }
    if agent_type not in agent_map:
        raise ValueError(f"Unknown agent type: {agent_type}. Must be one of {list(agent_map.keys())}")

    agent = agent_map[agent_type](llm_config)
    result = _run_agent(agent, json.dumps(input_data, indent=2))
    return {
        "agent": agent_type,
        "status": "complete",
        "response": result or "No response from agent.",
    }
