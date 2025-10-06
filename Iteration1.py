import asyncio
from Templates.brd_template import brd_template
from Templates.frd_template import frd_template
from Templates.rfp_template import rfp_template
from Templates.sow_template import sow_template
from Templates.srs_template import srs_template
from Prompts.idea_enhancer import idea_enhancer_prompt
from Sample_output.market_research import market_research
from Sample_output.team_structure import team_structure
from Sample_output.tech_stack import tech_stack
from Sample_output.timeline import timeline
from Sample_output.budget import budget
from Prompts.technical_solutioning import technical_solutioning_prompt
from autogen_core.tools import FunctionTool
from autogen_agentchat.agents import AssistantAgent,UserProxyAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from duckduckgo_search import DDGS
from autogen_agentchat.ui import Console
from typing import Literal, Optional, Dict, Any
from openai import AsyncOpenAI
import requests
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
gq_api_key = os.getenv("GROQ_API_KEY")

client = AsyncOpenAI()

async def web_search_tool(
    query: str,
    depth: Literal["low", "medium", "high"] = "high"
) -> str:
    """Run OpenAI hosted web search and return a cited summary (optionally deeper)."""
    resp = await client.responses.create(
        model="gpt-5",
        input=f"Search the web for: {query}. Summarize with dates and include citations. "
              f"Return JSON with fields: summary, sources[{ '{title,url,date}' }].",
        tools=[{"type": "web_search", "search_context_size": depth}],
        tool_choice="auto",
    )
    return resp.output_text

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

web_search_fn = FunctionTool(
    web_search_tool,
    description="Run OpenAI hosted web search and return a dated, cited summary.",
    name="web_search_tool",   # optional; defaults to function name
)
   
def google_search(query:str):
    """
    Performs a Google search using the Custom Search JSON API.

    Parameters:
        query (str): Search query string.
        api_key (str): Your Google API key.
        num_results (int): Number of search results to return (max 10 per request).

    Returns:
        list: A list of dictionaries containing title, link, and snippet.
    """
    cse_id = "b4d3e101dea6543c2"  

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": 'AIzaSyCDXrm_jquECBG_D8MSO5vG8i_FAoC9E68',
        "cx": "b4d3e101dea6543c2",
        "num": 10
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    items = response.json().get("items", [])
    results = []

    for item in items:
        results.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet")
        })

    return results


    # search_results = google_search(query)

    # for i, result in enumerate(search_results, 1):
    # print(f"{i}. {result['title']}\n{result['link']}\n{result['snippet']}\n")


async def main():
    model_client = OpenAIChatCompletionClient(model = "gpt-4.1",api_key=api_key)
    user_proxy = UserProxyAgent(
        name = "User",
        input_func=input,
        description= "Captures user input and provides feedback. It is called after each agent response no matter who is the agent."
    )

    idea_enhancer = AssistantAgent(
        name = "IdeaEnhancer",
        model_client=model_client,
        system_message=f"""{idea_enhancer_prompt}""",

        description="A creative AI agent that transforms vague ideas into polished product concepts, complete with a name, description, key features, and next-step suggestions. Also helps the user in refining the project idea and answering queries/followups."
    )    
# Market questionnaire for web_search_preview functionality:

    # market_questionnaire = AssistantAgent(
    # name="MarketQuestionnaire",
    # model_client=model_client,  
    # description="Turns a startup idea into a set of web-search queries and extracts detailed info from top links.",
    # system_message=f"""
    #     You are **MarketQuestionnaire**, a specialized agent for market research.

    #     Workflow:
    #     1) Given a finalized startup idea, generate 5–12 short, unambiguous search queries.
    #     2) For each query, call **web_search_tool(query, depth="high")** to get the latest results with citations.
    #     3) For the most relevant URLs, call **extract_page_text(url)** to pull the main article text (ignore nav/ads).
    #     4) Return:
    #     - The list of queries.
    #     - For each query: a JSON block with `summary`, and `sources`[{ '{title,url,date}' }].
    #     - Any extracted page text snippets (max 500 words per URL) with the URL noted.
    #     5) Include the keywords "Comprehensive Market Research", "Latest 2025" and "Deeper Research"in a couple of the queries.

    #     Constraints:
    #     - Use only these tools.
    #     - Do not rely on prior memory; everything must be discoverable via the tools.
    #     - Output plain text with clearly delimited JSON blocks per query.
    #     """,
    #         tools=[web_search_fn],   # <-- swapped in
    #         max_tool_iterations=5,                     # allow repeated tool use in one turn
    #     )


#
    market_questionnaire = AssistantAgent(
    name="MarketQuestionnaire",
    model_client=model_client,  
    description="Turns a startup idea into search queries and extracts details.",
    system_message="""
    You are MarketQuestionnaire.
    1) Produce 6–12 short queries (include 'Comprehensive Market Research' and 'Deeper Research' in two).
    2) For each query, call g4o_search_tool(query, search_context_size="high", country="IN") to get recent, cited results.
    3) For top URLs, call extract_page_text(url) and include in depth anallysis with citations.
    Output: numbered queries, then per-query findings + extracts.
    """,
    tools=[g4o_search_fn],
    max_tool_iterations=30,
)


    market_agent = AssistantAgent(
    name="MarketResearcher",
    model_client=model_client,
    description="Runs after the completion of MarketQuestionnnaire and provides competitors, market size, positioning, trends based on the finalised idea based on the latest context.",
    system_message="""### INSTRUCTION ###
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
    **“Would you like me to add some features based on the Market Research or move on with the technical solutioning for the same.?”**
    and call the user agent. 
    """
    )

    tech_solution = AssistantAgent(
        name = "TechnicalSolutioning",
        model_client=model_client,
        description = "Tells the user about what kind of Tech stack needs to be used based on the idea and market research.",
        system_message = f"{technical_solutioning_prompt}"
    )

    ba_agent = AssistantAgent(
        name = "BusinessAnalyst",
        model_client=model_client,
        description="Runs after the user is happy with the Market Research. It Generates business documents (BRD, SRS, FRD, SOW, RFP) based on the finalized idea and estimates.",
        system_message=f"""
        INSTRUCTION
        You are a professional Business Analyst AI assistant.

        Your job is to generate in depth and detailed business documentation based on a finalized product idea and technical estimates. Use a minimum of 5 lines per paragraph and use the context to give out the best and professional grade content. Leave the date as [Today's date]. 

        Strictly donot generate a document till the user asks for it explicitly, Ask clarification questions (Strictly only 1 question at a time so the user doesn't get overwhelmed) to the user regarding what document he/she needs. You can ask a maximum of 3 questions. 
        All the documents must be generated in simple Markdown format. 

        Document Types You Can Generate (ONE at a time):
        BRD- Business Requirements Document
        SRS- Software Requirements Specification
        FRD- Functional Requirements Document
        SOW-  Statement of Work
        RFP- Request for Proposal

        Templates (Use EXACTLY these formats):
        BRD Template - 
        {brd_template}
        SRS Template
        {srs_template}
        FRD Template
        {frd_template}
        SOW Template
        {sow_template}
        RFP Template
        {rfp_template}

        Operating Logic (You MUST follow this loop):
        WAIT for the user to request a specific document out of BRD, SRS, FRD, SOW, or RFP.

        If ambiguous (e.g., “make me something”) or not specified a type of document yet, ask:
        “Which document would you like me to generate: BRD, SRS, FRD, SOW, or RFP?”

        Only generate one document per request and the document should be long and extensive, try to incorporate as many things from the idea as possible. 
        Strictly donot move onto the Go to market agent until the user specificly asks for it. 

        After each document, ask:
        “Would you like me to generate another document (BRD, SRS, FRD, SOW, RFP), or move towards Go-to-Market Planning?" and call the User agent everytime. 
"""
    )


#     gtm_agent = AssistantAgent(
#     name="GTM_Strategy_Generator",
#     description="Go to market strategy agent is called after the SWOT_Analyzer has done his job and the user is happy and wants to continue " ,
#     model_client=model_client,
#     system_message="""
#     You are a Go-To-Market (GTM) Strategy Expert. Your role is to create comprehensive GTM strategies for any business idea, product, or service.
    
#     For any given business idea, provide:
    
#     1. **TARGET PERSONAS:**
#        - Define 2-3 primary customer personas
#        - Include demographics, pain points, and motivations
#        - Specify where they spend time online/offline
    
#     2. **LAUNCH CHANNELS:**
#        - Recommend 3-5 most effective channels for launch
#        - Include digital (social media, email, content marketing, PPC)
#        - Include traditional channels if relevant
#        - Prioritize channels based on target personas
    
#     3. **PRICING STRATEGY:**
#        - Suggest pricing model (subscription, one-time, freemium, etc.)
#        - Provide specific price points or ranges
#        - Include competitor analysis considerations
#        - Recommend pricing tiers if applicable
    
#     4. **BRANDING IDEAS:**
#        - Brand positioning statement
#        - Key messaging pillars
#        - Visual identity suggestions
#        - Tone of voice recommendations
    
#     5. **READY-TO-USE COPY:**
#        - 3 email subject lines + body copy templates
#        - 5 social media post ideas with copy
#        - 1 landing page headline + description
#        - 3 ad copy variations for different channels
    
#     Format your response with clear headers and actionable content. Make all copy compelling, benefit-focused, and ready to implement immediately.
    
#     Always end with a 30-60-90 day launch timeline with specific milestones. Ask the user if he/she wants to "reiterate something or can we move onto the Estimation Agent" and strictly always call the User agent. 
#     """
# )
    

    estimator_agent = AssistantAgent(name = "estimator_agent",
        model_client=model_client, description=
        """Runs only when Provides cost, timeline, tech stack, and team composition estimates based on a finalized business or product idea.""",
        system_message=f"""You are a startup estimator AI. Only proceed when the user explicitly confirms the idea is finalized.

        When given a finalized product idea, your job is to return an estimation of:
        1) Budget in INR- Give a budget breakdown as well for each component like (in the form of a table.):-
        #Sample Output
        {budget}
        
        2) Development timeline in weeks - The timeline should also include a breakdown of all the things that need to be done with respect to the time required for each, always keep it well detailed. 
        #Sample Output
        {timeline}

        3) Suggested tech stack (frontend, backend, DB, tools)
        #Sample Output- 
        {tech_stack}

        4) Suggested team structure (e.g., 1 frontend dev, 1 backend dev, 1 designer)
        #Sample output- 
        {team_structure} - Do note to always provide the team structure in the provided format only. 

        Note- Strictly use whole numbers for the entire process and donot under any circumstance give numbers as decimal.

        Be concise and clear. Use markdown format. After providing the estimates, ask the user if they would like to make any iterations with the provided requirements and call the user agent. """
    )

    supervisor = AssistantAgent(
        name = 'WorkflowRouter',
        model_client=model_client,
        system_message="""### Instruction###
         You are **WorkflowRouter**, a silent orchestrator that Strictly never prints text to the user and never takes user input just calls the next agent that it feels fit. your task is to manage the workflow below and after each agent you have to call the user agent to get the responses, this is non negotiable except for  MarketQuestionnaire agent where you can call Market Researcher right after the market questionnaire. 

         #### Agent roster (fixed order)
         1. IdeaEnhancer         -  Works on ideas, features, product. Calls the MarketQuestionnaire once the user says specifically to call it or is happy with the final idea. 
         2. MarketQuestionnaire. - Formulates questions based on Finalised product idea.
         3. MarketResearcher     - Searches the web based on Questions provided by MarketQuestionnaire.
         4. TechnicalSolutioning - gives the technical specifications based on the Market research and the finalised idea. 
         5. BusinessAnalyst      -  After Market research, it generates the documents like (BRD, SRS, FRD, SOW, or RFP)
         6. EstimatorAgent       -   After the Go to Market Strategy is finalised, the EstimatorAgent provides the estimates for the product(if any changes are made to the budget or any estimations- also check in with the IdeaEnhancer to confirm the Idea/Set of features.)

         #### Routing rules
        1)After any model (non-user) responds, inspect the latest user message.
        If the user expresses satisfaction, ask:  
        “Would you like to move to the next phase: [Phase Name]?”  
        Wait for the user's response.  
        - If the user agrees, call the next agent.  
        - If not, stay in the current phase or ask for clarification.         
         3. If the user requests changes or clarification, **re-invoke the same agent**.  
         4. If the user asks for a market analysis at any time, jump to **MarketQuestionnaire** and then directly to **MarketResearcher**; resume the fixed order afterwards and donot invoke 2 agents in parellel if there is no UserProxyAgent in betwee except the use case discussed above.  
         5. When the final recommendation is produced, call **TERMINATE**.  
         6. At no time should WorkflowRouter send messages, logs or questions to the user—its only visible effect is invoking the next agent.
         7. If the user asks to do a specific task or call a specific agent then the agent that is responsible for that particular task should be called and after that the flow should remain the same as per the past sequence that was broken.
         ### End of Instruction###
         """
        ,description="Routes workflow between agents based on current phase and user readiness to proceed",
    )

    team = SelectorGroupChat(
        participants=[user_proxy,supervisor, idea_enhancer,market_questionnaire, tech_solution, estimator_agent, ba_agent, market_agent],
        model_client=model_client,
        allow_repeated_speaker=True,
        termination_condition=MaxMessageTermination(50) | TextMentionTermination("TERMINATE")
    )

    task = input('Enter your idea here: ')
    stream = team.run_stream(task=task)
    await Console(stream)
    # await model_client.close()

if __name__ == "__main__":
    asyncio.run(main())