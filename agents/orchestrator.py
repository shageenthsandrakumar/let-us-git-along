import os
import json
from autogen import ConversableAgent, LLMConfig
from autogen.agentchat import run_group_chat
from autogen.agentchat.group.patterns import AutoPattern
from agents.compatibility import create_compatibility_agent
from agents.gtm_strategist import create_gtm_strategist_agent
from agents.repotale import create_repotale_agent
from agents.matchmaker import create_matchmaker_agent
from agents.executor import create_executor_agent

def get_llm_config():
    return LLMConfig(api_type="openai", model="gpt-4o", api_key=os.environ.get("OPENAI_API_KEY", ""))

def run_founder_analysis(founder_a_profile, founder_b_profile, github_data_a=None, github_data_b=None):
    llm_config = get_llm_config()
    compatibility_agent = create_compatibility_agent(llm_config)
    gtm_agent = create_gtm_strategist_agent(llm_config)
    repotale_agent = create_repotale_agent(llm_config)
    matchmaker_agent = create_matchmaker_agent(llm_config)
    executor_agent = create_executor_agent(llm_config)

    coordinator = ConversableAgent(
        name="coordinator",
        system_message="You are the FounderFit Coordinator. Orchestrate the analysis by delegating to specialized agents and synthesizing their outputs into a unified founder compatibility report.",
        llm_config=llm_config,
        description="Coordinates the multi-agent analysis workflow.",
    )

    analysis_prompt = f"""Analyze the compatibility between these two founders:

**Founder A Profile:**
{json.dumps(founder_a_profile, indent=2)}

**Founder B Profile:**
{json.dumps(founder_b_profile, indent=2)}
"""
    if github_data_a:
        analysis_prompt += f"\n**Founder A GitHub Data:**\n{json.dumps(github_data_a, indent=2)}\n"
    if github_data_b:
        analysis_prompt += f"\n**Founder B GitHub Data:**\n{json.dumps(github_data_b, indent=2)}\n"

    analysis_prompt += "\nProvide a complete founder compatibility analysis including six-dimension scores, GTM archetype, match assessment, and execution recommendations."

    agents = [coordinator, compatibility_agent, gtm_agent, repotale_agent, matchmaker_agent, executor_agent]
    pattern = AutoPattern(
        agents=agents,
        initial_agent=coordinator,
        group_manager_args={"name": "analysis_manager", "llm_config": llm_config},
    )
    result = run_group_chat(pattern=pattern, message=analysis_prompt, max_turns=12)
    result.process()

    return {
        "status": "complete",
        "conversation": [msg for msg in result.messages] if hasattr(result, "messages") else [],
        "summary": result.summary if hasattr(result, "summary") else str(result),
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
    response = agent.run(message=json.dumps(input_data, indent=2), max_turns=1)
    response.process()
    return {
        "agent": agent_type,
        "status": "complete",
        "response": response.summary if hasattr(response, "summary") else str(response),
    }
