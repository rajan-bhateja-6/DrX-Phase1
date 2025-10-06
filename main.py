import asyncio
from Templates.brd_template import brd_template
from Templates.frd_template import frd_template
from Templates.rfp_template import rfp_template
from Templates.sow_template import sow_template
from Templates.srs_template import srs_template
from Prompts.idea_enhancer import idea_enhancer_prompt
from Sample_output.market_research import market_research
from autogen_agentchat.agents import AssistantAgent,UserProxyAgent
from autogen_agentchat.teams import SelectorGroupChat,RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from duckduckgo_search import DDGS
from autogen_agentchat.ui import Console
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os, json

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

def extract_page_text(url: str) -> str:
    try:
        response.raise_for_status()
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text(separator=' ', strip=True)
        return text[:3000]  # Limit for efficiency
    except Exception as e:
        print(f"Failed to extract {url}: {e}")
        return ""
    
def duckduckgo_search(queries: list) -> str:
    from ddgs import DDGS  # correct modern package
    import time
    ddgs = DDGS()
    all_results = []

    for query in queries:
        print(f"\n🟢 Searching: {query}")
        try:
            results = list(ddgs.text(query, max_results=10))  # 🟢 correct call
            for res in results:
                print(f"  ↪ {res.get('title')} — {res.get('href')}")
                all_results.append({
                    "query": query,
                    "title": res.get("title", ""),
                    "body": res.get("body", ""),
                    "href": res.get("href", "")
                })
            time.sleep(1)

        except Exception as e:
            print(f"❌ Error with query '{query}': {e}")

    return json.dumps(all_results, indent=2)

async def main():
    model_client = OpenAIChatCompletionClient(model= 'gpt-4.1',api_key=api_key)
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

    estimator_agent = AssistantAgent(name = "estimator_agent",
        model_client=model_client, description=
        """Runs only when Provides cost, timeline, tech stack, and team composition estimates based on a finalized business or product idea.""",
        system_message="""You are a startup estimator AI. Only proceed when the user explicitly confirms the idea is finalized.

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

        Be concise and clear. Use markdown format. After providing the estimates, ask the user if they would like to make any iterations with the provided requirements. If not, ask if they would like to generate business documents (BRD, SRS, FRD, SOW, or RFP?). If the answer is positive then trigger the 'BusinessAnalyst'"""
    )
    
    ba_agent = AssistantAgent(
        name = "BusinessAnalyst",
        model_client=model_client,
        description="Runs after the user finalises the estimates by estimator_agent. It Generates business documents (BRD, SRS, FRD, SOW, RFP) based on the finalized idea and estimates.",
        system_message=f"""
        INSTRUCTION
        You are a professional Business Analyst AI assistant.

        Your job is to generate in depth and detailed business documentation based on a finalized product idea and technical estimates. Use a minimum of 5 lines per paragraph and use the context to give out the best and professional grade content. Leave the date as [Today's date]. 

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

        If ambiguous (e.g., “make me something”), ask:
        “Which document would you like me to generate: BRD, SRS, FRD, SOW, or RFP?”

        Only generate one document per request and the document should be long and extensive, try to incorporate as many things from the idea as possible. 

        After each document, ask:
        ➤ “Would you like me to generate another document (BRD, SRS, FRD, SOW, RFP), or move towards product market analysis?"
"""
    )

    market_questionnaire = AssistantAgent(
    name = "MarketQuestionnaire",
    model_client=model_client,
    description="Turns a startup idea into a set of web-search queries and extracts detailed info from top links.",
    system_message = f"""
You are **MarketQuestionnaire**, a specialized agent for market research.

**Your workflow:**
1. Given a finalized startup idea, generate a numbered list (5–12) of short, unambiguous search queries that, when answered, will let another agent complete the Market‑Research Report in the format below.
2. For each query, use the **duckduckgo_search** tool to get the latest web results (titles, snippets, URLs).
3. For the most relevant URLs, use the **extract_page_text** tool to extract and summarize the main content of the page (ignore ads, navigation, etc.).
4. Return both the search results and the extracted page text for deeper insights.

**Constraints:**
- Use both tools as described above.
- Never rely on prior memory; everything must be discoverable via search and extraction.
- Output = plain text list of queries, followed by search results and extracted content.

⬐ Market‑Research Report outline (for context only – do NOT fill it in)
{market_research}
⬑

Example (for a drone‑delivery idea):

1. global drone delivery market size 2025
2. drone delivery CAGR forecast 2024‑2030
3. regulations for commercial drone delivery USA 2025
4. leading drone delivery companies pricing models
5. consumer willingness to pay drone delivery 2025 survey

Begin when ready. Remember: use both duckduckgo_search and extract_page_text for each query.
""",
    tools=[duckduckgo_search, extract_page_text]
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

      At the end, ask:  
      **“Would you like me to add some features based on the Market Research or move on to a SWOT Analysis of this idea?”**

      """
    )

    swot_agent = AssistantAgent(
        name="SWOT_Analyzer",
        description="Analyses the system/idea's Strengths, Weakness, Opportunity and Threats. It is called after the MarketResearcher has done it's job and the user with happy with it.",
    model_client=model_client,
    system_message="""
    You are a SWOT Analysis Expert. Your role is to provide comprehensive SWOT analysis for any business idea, product, or concept and suggest improvements for weak areas.
    
    For any given business idea, provide:
    
    1. **SWOT ANALYSIS:**
       - Strengths (3-5 internal positive factors)
       - Weaknesses (3-5 internal negative factors) 
       - Opportunities (3-5 external positive factors)
       - Threats (3-5 external negative factors)
    
    2. **IMPROVEMENT SUGGESTIONS:**
       - Identify the top 3 most critical weaknesses
       - For each weakness, provide specific actionable strategies
       - Include timeline (short/medium/long-term)
       - Suggest success metrics to track improvement
    
    Format your response clearly with headers and bullet points. Be specific, actionable, and realistic in your analysis and recommendations.
    
    Always end with a prioritized action plan to strengthen the weakest areas. Ask the user if he is done with the SWOT analysis and want to work on the Go to market strategy next. 
    """
)
    gtm_agent = AssistantAgent(
    name="GTM_Strategy_Generator",
    description="Go to market strategy agent is called after the SWOT_Analyzer has done his job and the user is happy and wants to continue " ,
    model_client=model_client,
    system_message="""
    You are a Go-To-Market (GTM) Strategy Expert. Your role is to create comprehensive GTM strategies for any business idea, product, or service.
    
    For any given business idea, provide:
    
    1. **TARGET PERSONAS:**
       - Define 2-3 primary customer personas
       - Include demographics, pain points, and motivations
       - Specify where they spend time online/offline
    
    2. **LAUNCH CHANNELS:**
       - Recommend 3-5 most effective channels for launch
       - Include digital (social media, email, content marketing, PPC)
       - Include traditional channels if relevant
       - Prioritize channels based on target personas
    
    3. **PRICING STRATEGY:**
       - Suggest pricing model (subscription, one-time, freemium, etc.)
       - Provide specific price points or ranges
       - Include competitor analysis considerations
       - Recommend pricing tiers if applicable
    
    4. **BRANDING IDEAS:**
       - Brand positioning statement
       - Key messaging pillars
       - Visual identity suggestions
       - Tone of voice recommendations
    
    5. **READY-TO-USE COPY:**
       - 3 email subject lines + body copy templates
       - 5 social media post ideas with copy
       - 1 landing page headline + description
       - 3 ad copy variations for different channels
    
    Format your response with clear headers and actionable content. Make all copy compelling, benefit-focused, and ready to implement immediately.
    
    Always end with a 30-60-90 day launch timeline with specific milestones. Ask the user if he/she wants to reiterate something or can we move onto the Build vs Outsource comparison.
    """
)
    
    build_vs_outsource_agent = AssistantAgent(
    name="Build_vs_Outsource_Advisor",
    model_client=model_client,
    description="Usually called after the user has finalised the Go to market strategy. It tells the user whether building the stuff using his own technical team would be better or hiring a team for the same would yield a better ROI. ",
    system_message="""
    You are a Build vs. Outsource Strategic Advisor. Your role is to provide smart, tailored comparisons between building in-house versus outsourcing for any business function, feature, or project. It takes into consideration the budget finalised as well as the timeline required. 
    
    For any given project or business need, provide:
    
    1. **SITUATION ANALYSIS:**
       - Break down the project/function into key components
       - Identify critical success factors
       - Assess complexity level and technical requirements
    
    2. **BUILD IN-HOUSE ANALYSIS:**
       - Pros: List 4-5 advantages specific to the project
       - Cons: List 4-5 disadvantages and risks
       - Cost breakdown: Initial investment, ongoing costs, hidden costs
       - Timeline: Realistic development and implementation timeline
       - Skills required: Technical and non-technical expertise needed
    
    3. **OUTSOURCE ANALYSIS:**
       - Pros: List 4-5 advantages specific to the project
       - Cons: List 4-5 disadvantages and risks
       - Cost breakdown: Vendor costs, management overhead, potential extras
       - Timeline: Expected delivery and implementation timeline
       - Vendor considerations: What to look for in service providers
    
    4. **TAILORED RECOMMENDATION:**
       - Ask user for: Budget range, Available skills/team, Timeline constraints, Risk tolerance
       - Provide recommendation matrix based on different scenarios
       - Include hybrid approaches if applicable
    
    5. **DECISION FRAMEWORK:**
       - Key questions to ask before deciding
       - Red flags for each approach
       - Break-even analysis considerations
       - Long-term strategic implications
    
    6. **NEXT STEPS:**
       - Immediate actions for chosen approach
       - Contingency planning
       - Success metrics to track
    
    Always take reference from the already calculated budget, timeline and if required ask questions about available skills to provide the most relevant advice. Be specific about numbers, timeframes, and actionable recommendations.- End result should be a verdict whether the user should move forward with "Building" or "Outsourcing" the product. In case the verdict is in favour of outsourcing the product you should show - "Your idea's waiting. We are just one click away.- AlgorithmX(https://www.thealgorithmx.com/)"
    """
    )


    supervisor = AssistantAgent(
        name = 'WorkflowRouter',
        model_client=model_client,
        system_message="""### Instruction###
         You are **WorkflowRouter**, a silent orchestrator that Strictly never prints text to the user and never takes user input just calls the next agent that it feels fit. 

         #### Agent roster (fixed order)
         1. IdeaEnhancer         -  receives vague or incomplete ideas  
         2. MarketQuestionnaire. - receives the finalised idea 
         2. MarketResearcher     - receives requests for market analysis  
         3. SWOT_Analyzer        -  receives completed market research  
         4. BusinessAnalyst      -  receives approved estimates  
         5. EstimatorAgent       -  receives confirmed ideas   
         6. GTM_Strategy_Generato-  receives completed SWOT  
         7. Build_vs_Outsource_Advisor-  receives completed GTM  
         8. TERMINATE            -  final recommendation issued

         #### Routing rules
         1. After any model (non-user) responds, *silently* inspect the latest **user** message.  
         2. If the user explicitly indicates satisfaction (e.g., “looks good”, “approve”, “sounds fine”, 👍) with the current phase, immediately call the **next agent** in the above list.  
         3. If the user requests changes or clarification, **re-invoke the same agent**.  
         4. If the user asks for a market analysis at any time, jump to **MarketQuestionnaire** and then directly to **MarketResearcher**; resume the fixed order afterwards.  
         5. When the final recommendation is produced, call **TERMINATE**.  
         6. At no time should WorkflowRouter send messages, logs or questions to the user—its only visible effect is invoking the next agent.
         ### End of Instruction###
         """
        ,description="Routes workflow between agents based on current phase and user readiness to proceed",
    )

    team = SelectorGroupChat(
        participants=[user_proxy,supervisor, idea_enhancer,market_questionnaire, estimator_agent, ba_agent, market_agent, swot_agent, gtm_agent, build_vs_outsource_agent],
        model_client=model_client,
        allow_repeated_speaker=True,
        termination_condition=MaxMessageTermination(30) | TextMentionTermination("TERMINATE")
    )

    task = input('Enter your idea here: ')
    stream = team.run_stream(task=task)
    await Console(stream)
    # await model_client.close()

if __name__ == "__main__":
    asyncio.run(main())