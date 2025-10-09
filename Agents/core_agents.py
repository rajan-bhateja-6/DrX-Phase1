from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from Prompts.idea_enhancer import idea_enhancer_prompt
from Prompts.technical_solutioning import technical_solutioning_prompt
from Prompts.market_research_prompt import market_research_prompt, market_questionnaire_prompt
from Prompts.estimator_agent_prompt import estimator_agent_prompt
from Prompts.business_analysist_prompt import business_analyst_prompt
from Prompts.workflow_router_prompt import workflow_router_prompt
from .search_tools import g4o_search_fn, initialize_client
from config.model_config import config


def create_agents():
    # Initialize the OpenAI client for search tools
    initialize_client(config.get_api_key())
    model_client = config.get_model_client()

    user_proxy = UserProxyAgent(
        name="User",
        input_func=input,
        description="Captures user input and provides feedback. It is called after each agent response no matter who is the agent."
    )

    idea_enhancer = AssistantAgent(
        name="IdeaEnhancer",
        model_client=model_client,
        system_message=f"{idea_enhancer_prompt}",
        description="A creative AI agent that transforms vague ideas into polished product concepts, complete with a name, description, key features, and next-step suggestions. Also helps the user in refining the project idea and answering queries/followups."
    )

    market_questionnaire = AssistantAgent(
        name="MarketQuestionnaire",
        model_client=model_client,
        description="Turns a startup idea into search queries and extracts details.",
        system_message=f"""{market_questionnaire_prompt}
        """,
        tools=[g4o_search_fn],
        max_tool_iterations=30,
    )

    market_agent = AssistantAgent(
        name="MarketResearcher",
        model_client=model_client,
        description="Runs after the completion of MarketQuestionnnaire and provides competitors, market size, positioning, trends based on the finalised idea based on the latest context.",
        system_message=f"""{market_research_prompt}
        """
    )

    tech_solution = AssistantAgent(
        name="TechnicalSolutioning",
        model_client=model_client,
        description="Tells the user about what kind of Tech stack needs to be used based on the idea and market research.",
        system_message=f"{technical_solutioning_prompt}"
    )

    ba_agent = AssistantAgent(
        name="BusinessAnalyst",
        model_client=model_client,
        description="Runs after the user is happy with the Market Research. It Generates business documents (BRD, SRS, FRD, SOW, RFP) based on the finalized idea and estimates.",
        system_message=f"""{business_analyst_prompt}"""
    )

    estimator_agent = AssistantAgent(
        name="estimator_agent",
        model_client=model_client,
        description="""Runs only when Provides cost, timeline, tech stack, and team composition estimates based on a finalized business or product idea.""",
        system_message=f"""{estimator_agent_prompt}"""
    )

    supervisor = AssistantAgent(
        name='WorkflowRouter',
        model_client=model_client,
        system_message=f"""{workflow_router_prompt}""",
        description="Routes workflow between agents based on current phase and user readiness to proceed",
    )

    return user_proxy, idea_enhancer, market_questionnaire, market_agent, tech_solution, ba_agent, estimator_agent, supervisor, model_client