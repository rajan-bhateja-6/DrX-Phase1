# idea_enhancer.py
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.ui import Console
from autogen_core.tools import FunctionTool
from openai import AsyncOpenAI
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Use a model that your autogen_ext install supports ("gpt-4o" or "gpt-4.1" if it works in your env)
model_client = OpenAIChatCompletionClient(model="gpt-4o", api_key=api_key)

client = AsyncOpenAI()

async def g4o_search_tool(
    query: str,
    search_context_size: str = "high",
    country: str = None, city: str = None, region: str = None, timezone: str = None
) -> str:
    web_search_options = {"search_context_size": search_context_size}
    if any([country, city, region, timezone]):
        web_search_options["user_location"] = {
            "type": "approximate",
            "approximate": {
                **({"country": country} if country else {}),
                **({"city": city} if city else {}),
                **({"region": region} if region else {}),
                **({"timezone": timezone} if timezone else {}),
            }
        }

    comp = await client.chat.completions.create(
        model="gpt-4o-search-preview",
        messages=[
            {"role": "system", "content": "Be concise. Include URLs and dates as citations."},
            {"role": "user", "content": query},
        ],
        # pass search controls here; no temperature/top_p/etc.
        extra_body={"web_search_options": web_search_options},
    )
    return comp.choices[0].message.content

g4o_search_fn = FunctionTool(
    g4o_search_tool,
    description="Search the web (GPT-4o Search Preview) and return a concise, cited summary.",
    name="g4o_search_tool",
)

SYSTEM_PROMPT_1 = """    You are MarketQuestionnaire.
    1) Produce 6–12 short queries (include 'Comprehensive Market Research' and 'Deeper Research' in two).
    2) For each query, call g4o_search_tool(query, search_context_size="high", country="IN") to get recent, cited results.
    3) For top URLs, call extract_page_text(url) and include in depth anallysis with citations.
    Output: numbered queries, then per-query findings + extracts.

"""

SYSTEM_PROMPT_2 = """### INSTRUCTION ###
    You are a senior market research analyst with deep cross-industry expertise. Your task is to perform an in-depth market research analysis of a specific business idea based on the context already provided to you about the market scenarios. 

    You MUST provide detailed, data-driven insights using the knowledge provided to you as context and structure your output exactly in the format below.

    ### FORMAT TO FOLLOW (OUTPUT PRIMER) ###

    Title: [Business Idea Name] Market Analysis Report

    1. Executive Summary  
    - Write a concise overview (5–7 sentences) introducing the business idea, core market, major opportunities, and competitive highlights. Be persuasive and data-backed.

    2. Competitor Analysis  
    - List 5–10 direct and indirect competitors in a table format with columns:  
    - App/Brand  
    - Key Features  
    - Unique Value Proposition  
    - User Base (Estimated)  
    - Sources  
    - Follow with a written analysis comparing the idea with competitors, highlighting strengths, weaknesses, market gaps, and strategic advantage.

    3. Market Size & Growth  
    - Calculate and explain:
    - Total Addressable Market (TAM)  
    - Serviceable Addressable Market (SAM)  
    - Serviceable Obtainable Market (SOM)  
    - Include CAGR, demographic breakdowns, monetization models, and regional insights. Use actual or estimated figures (e.g., USD billions).

    4. Trends & Opportunities  
    - Highlight emerging trends, technologies, and user behaviors.  
    - Include industry citations or data-backed insights where possible.  
    - Spot market gaps and competitive white spaces.

    5. Strategic Positioning  
    - Recommend clear Unique Value Propositions.  
    - Suggest differentiation strategies and marketing angles.  
    - Identify competitive advantages and customer segments to focus on.

    6. Deep Dive Recommendations  
    - Suggest 3–5 focused research recommendations:  
    - Specific competitors to study further  
    - Customer personas or niches worth validating  
    - Risk areas or assumptions to test  
    - Data sources or reports to seek out  

    7. SWOT Analysis  
    - Present a comprehensive SWOT analysis table with four quadrants:
    - **Strengths**: Internal advantages, unique assets, strong partnerships, team expertise, etc.  
    - **Weaknesses**: Internal gaps, scalability concerns, resource constraints, limited brand equity, etc.  
    - **Opportunities**: External trends or shifts that can be leveraged — market expansion, tech advancements, customer needs, etc.  
    - **Threats**: Competitive pressures, regulatory risks, economic downturns, shifts in customer behavior, etc.

    - After the table, write 1–2 paragraphs explaining the most critical insights from the SWOT. 
    - Highlight what can be *amplified*, *mitigated*, or *capitalized on*.  
    - Recommend immediate strategic actions for the most urgent items (e.g., turning a weakness into a strength or mitigating a top threat).

    At the end, ask:  
    **“Would you like me to add some features based on the Market Research or move on with building Business Documents for the same.?”**
    and call the user agent. """

async def main():
    # Start with the human. No manual input() before run_stream — avoids duplicate prompts.
    user_agent = UserProxyAgent(
        name="User",
        input_func=input,
        description="Captures user input and provides feedback in the loop."
    )

    market_questionnaire = AssistantAgent(
    name="MarketQuestionnaire",
    model_client=model_client,  
    description="Turns a startup idea into search queries and extracts details.",
    system_message=SYSTEM_PROMPT_1,
    tools=[g4o_search_fn],
    max_tool_iterations=30,
)
    
    market_agent = AssistantAgent(
    name="MarketResearcher",
    model_client=model_client,
    description="Runs after the completion of MarketQuestionnnaire and provides competitors, market size, positioning, trends based on the finalised idea based on the latest context.",
    system_message=SYSTEM_PROMPT_2)



    # Stop when user types /end (or when conversation gets too long)
    termination = (
        TextMentionTermination("/end")
        | TextMentionTermination("TERMINATE")
        | MaxMessageTermination(60)
    )

    team = RoundRobinGroupChat(
        participants=[user_agent, market_questionnaire, market_agent],
        termination_condition=termination,
    )

    print("Tip: start with your idea (e.g., “I want an app to sell used musical instruments”).")

    # IMPORTANT: Don't pass a task here; let UserProxyAgent take the first turn.
    stream = team.run_stream()
    await Console(stream)

    # await model_client.close()  # optional if your env complains about open connectors

if __name__ == "__main__":
    asyncio.run(main())
