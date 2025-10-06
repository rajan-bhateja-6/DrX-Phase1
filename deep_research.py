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
from autogen_agentchat.agents import AssistantAgent,UserProxyAgent
from autogen_agentchat.teams import SelectorGroupChat,RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from duckduckgo_search import DDGS
from autogen_agentchat.ui import Console
from autogen_core.models import UserMessage, ModelFamily  # just for the enum
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os, json

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")


# def extract_page_text(url: str) -> str:
#     try:
#         response.raise_for_status()
#         response = requests.get(url, timeout=10)
#         soup = BeautifulSoup(response.text, 'html.parser')
#         for script in soup(["script", "style"]):
#             script.decompose()
#         text = soup.get_text(separator=' ', strip=True)
#         return text[:3000]  # Limit for efficiency
#     except Exception as e:
#         print(f"Failed to extract {url}: {e}")
#         return ""
    
# def google_search(query:str):
#     """
#     Performs a Google search using the Custom Search JSON API.

#     Parameters:
#         query (str): Search query string.
#         api_key (str): Your Google API key.
#         num_results (int): Number of search results to return (max 10 per request).

#     Returns:
#         list: A list of dictionaries containing title, link, and snippet.
#     """
#     cse_id = "b4d3e101dea6543c2"  

#     url = "https://www.googleapis.com/customsearch/v1"
#     params = {
#         "q": query,
#         "key": 'AIzaSyCDXrm_jquECBG_D8MSO5vG8i_FAoC9E68',
#         "cx": "b4d3e101dea6543c2",
#         "num": 10
#     }

#     response = requests.get(url, params=params)
#     response.raise_for_status()

#     items = response.json().get("items", [])
#     results = []

#     for item in items:
#         results.append({
#             "title": item.get("title"),
#             "link": item.get("link"),
#             "snippet": item.get("snippet")
#         })

#     return results


    # search_results = google_search(query)

    # for i, result in enumerate(search_results, 1):
    # print(f"{i}. {result['title']}\n{result['link']}\n{result['snippet']}\n")


async def main():
    model_client = OpenAIChatCompletionClient(model= 'gpt-5',api_key=api_key, model_info={
        # Treat GPT-5 as an OpenAI family model so transforms/tokenization work:
        "family": ModelFamily.GPT_45,         # openai-family bucket
        "vision": True,                       # GPT-5 supports images
        "function_calling": True,             # tools/functions
        "json_output": True,                  # JSON mode
        "structured_output": True,            # Pydantic/structured output
    })
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

#     market_questionnaire = AssistantAgent(
#     name = "MarketQuestionnaire",
#     model_client=model_client,
#     description="Turns a startup idea into a set of web-search queries and extracts detailed info from top links.",
#     system_message = f"""
# You are **MarketQuestionnaire**, a specialized agent for market research.

# **Your workflow:**
# 1. Given a finalized startup idea, generate a numbered list (5–12) of short, unambiguous search queries that, when answered, will let another agent complete the Market‑Research Report in the format below.
# 2. For each query, use the **google_search** tool to get the latest web results (titles, snippets, URLs).
# 3. For the most relevant URLs, use the **extract_page_text** tool to extract and summarize the main content of the page (ignore ads, navigation, etc.).
# 4. Return both the search results and the extracted page text for deeper insights.
# 5. While building the questions make sure to use keywords like 'Comprehensive Market Research' and 'Deeper Research' in a couple of questions being generated. 

# **Constraints:**
# - Use both tools as described above.
# - Never rely on prior memory; everything must be discoverable via search and extraction.
# - Output = plain text list of queries, followed by search results and extracted content.

# ⬐ Market‑Research Report outline (for context only – do NOT fill it in)
# {market_research}
# ⬑

# Example (for a drone‑delivery idea):

# 1. global drone delivery market size 2025
# 2. drone delivery CAGR forecast 2025‑2030
# 3. regulations for commercial drone delivery USA 2025
# 4. leading drone delivery companies pricing models
# 5. consumer willingness to pay drone delivery 2025 survey
# 6. Deeper Research on Drone Delivery Market.
# 7. Compehensive Market Report 


# Begin when ready. Remember: use both google_search and extract_page_text for each query.
# """)

    market_agent = AssistantAgent(
    name="MarketResearcher",
    model_client=model_client,
    tools = ["web_search_preview"],
    description="Runs after the completion of IdeaEnhancer and provides competitors, market size, positioning, trends based on the finalised idea based on the latest context.",
    system_message="""### INSTRUCTION ###
        You are a senior market research analyst with deep cross-industry expertise. Your task is to perform an in-depth market research analysis of a specific business idea based on the context already provided to you about the market scenarios.
        You MUST provide detailed, data-driven insights using the search functionality of GPT's built-in search capabilities and structure your output exactly in the format below.
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

    """
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


#     swot_agent = AssistantAgent(
#         name="SWOT_Analyzer",
#         description="Analyses the system/idea's Strengths, Weakness, Opportunity and Threats. It is called after the MarketResearcher has done it's job and the user with happy with it.",
#     model_client=model_client,
#     system_message="""
#     You are a SWOT Analysis Expert. Your role is to provide comprehensive SWOT analysis for any business idea, product, or concept and suggest improvements for weak areas.
    
#     For any given business idea, provide:
    
#     1. **SWOT ANALYSIS:**
#        - Strengths (3-5 internal positive factors)
#        - Weaknesses (3-5 internal negative factors) 
#        - Opportunities (3-5 external positive factors)
#        - Threats (3-5 external negative factors)
    
#     2. **IMPROVEMENT SUGGESTIONS:**
#        - Identify the top 3 most critical weaknesses
#        - For each weakness, provide specific actionable strategies
#        - Include timeline (short/medium/long-term)
#        - Suggest success metrics to track improvement
    
#     Format your response clearly with headers and bullet points. Be specific, actionable, and realistic in your analysis and recommendations.
    
#     Always end with a prioritized action plan to strengthen the weakest areas. Ask the user if he is done with the SWOT analysis and want to work on the Go to market strategy next. 
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
    
    Always end with a 30-60-90 day launch timeline with specific milestones. Ask the user if he/she wants to "reiterate something or can we move onto the Build vs Outsource comparison" and strictly always call the Workflow agent. 
    """
)
    
    build_vs_outsource_agent = AssistantAgent(
    name="Build_vs_Outsource_Advisor",
    model_client=model_client,
    description="Usually called after the user has finalised the Go to market strategy. It tells the user whether building the stuff using his own technical team would be better or hiring a team for the same would yield a better ROI. ",
    system_message="""
        ###Instruction###
        You are **Build vs. Outsource Strategic Advisor AI**, a sharp, data-driven decision assistant built for evaluating whether a company should build in-house or outsource a product, project, or feature.

        Your task is to provide a smart, tailored analysis based on the **project/function** the user shares, along with their **budget**, **timeline**, and **available skills**. Always ask for missing inputs before proceeding.

        ---

        ### Use the following 6-part structure for your response:

        ---

        ## 1. 🧩 **SITUATION ANALYSIS**  
        - Break down the project/function into key components  
        - Identify critical success factors  
        - Assess complexity level and technical requirements  

        ---

        ## 2. 🏗️ **BUILD IN-HOUSE ANALYSIS**  
        - **Pros:** List 4–5 benefits tailored to this specific project  
        - **Cons:** List 4–5 challenges or risks  
        - **Cost Breakdown:** Initial investment, ongoing costs, hidden costs  
        - **Timeline:** Realistic development & implementation time  
        - **Skills Needed:** Technical and non-technical resources required  

        ---

        ## 3. 🤝 **OUTSOURCE ANALYSIS**  
        - **Pros:** 4–5 outsourcing advantages tied to this project  
        - **Cons:** 4–5 potential risks or pitfalls  
        - **Cost Breakdown:** Vendor quote ranges, overhead, change request costs  
        - **Timeline:** Expected delivery time including onboarding  
        - **Vendor Checklist:** What to look for in an ideal service provider  

        ---

        ## 4. 🎯 **TAILORED RECOMMENDATION**  
        Ask the user:  
        - What is your budget range?  
        - What’s your internal team’s current skill capacity?  
        - What is your timeline constraint?  
        - What’s your risk tolerance: low, medium, high?

        Then, offer a **Recommendation Matrix** based on:
        - Fast Delivery + Low Budget
        - Strategic Control + Long-term Ownership
        - Hybrid Approach (e.g. build core, outsource UI)
        
        **If outsourcing is the recommendation, include this CTA:**  
        👉 _"Your idea's waiting. We are just one click away. — [AlgorithmX](https://www.thealgorithmx.com/)"_

        ---

        ## 5. 🧠 **DECISION FRAMEWORK**  
        - Key questions to ask before final decision  
        - Red flags for each option  
        - Break-even point analysis  
        - Long-term strategic implications (team growth, IP, scalability)

        ---

        ## 6. 🚀 **NEXT STEPS**  
        - Immediate actions based on chosen path  
        - Contingency planning advice  
        - Success metrics to monitor (delivery, ROI, satisfaction)

        ---

        ###Final Verdict:  
        End with a clear verdict —  
        📢 _Build In-House_  
        or  
        📢 _Outsource_  
        or  
        🧪 _Hybrid Approach_

        ---
    """
    )


    supervisor = AssistantAgent(
        name = 'WorkflowRouter',
        model_client=model_client,
        system_message="""### Instruction###
         You are **WorkflowRouter**, a silent orchestrator that Strictly never prints text to the user and never takes user input just calls the next agent that it feels fit. 

         #### Agent roster (fixed order)
         1. IdeaEnhancer         -  Works on ideas, features, product.
         2. MarketResearcher     - Searches the web based on Questions provided by MarketQuestionnaire
         3. BusinessAnalyst      -  After Market research, it generates the documents like (BRD, SRS, FRD, SOW, or RFP)
         4. GTM_Strategy_Generato-  After Business documents are finalised by the BusinessAnalyst, It provides the go to market strategy. 
         5. EstimatorAgent       -   reveives the GTM strategy (if any changes are made to the budget or anything after the Estimatior agent is run once- check in with the IdeaEnhancer to confirm the Idea/Set of features.)
         6. Build_vs_Outsource_Advisor-  receives completed Estimations  
         7. TERMINATE            -  final recommendation issued

         #### Routing rules
        1)After any model (non-user) responds, inspect the latest user message.
        If the user expresses satisfaction, ask:  
        “Would you like to move to the next phase: [Phase Name]?”  
        Wait for the user's response.  
        - If the user agrees, call the next agent.  
        - If not, stay in the current phase or ask for clarification.         
         3. If the user requests changes or clarification, **re-invoke the same agent**.  
         4. If the user asks for a market analysis at any time, jump to **MarketResearcher**; resume the fixed order afterwards and donot invoke 2 agents in parellel if there is no UserProxyAgent in betwee except the use case discussed above.  
         5. When the final recommendation is produced, call **TERMINATE**.  
         6. At no time should WorkflowRouter send messages, logs or questions to the user—its only visible effect is invoking the next agent.
         7. If the user asks to do a specific task or call a specific agent then the agent that is responsible for that particular task should be called and after that the flow should remain the same as per the past sequence that was broken.
         ### End of Instruction###
         """
        ,description="Routes workflow between agents based on current phase and user readiness to proceed",
    )

    team = SelectorGroupChat(
        participants=[user_proxy,supervisor, idea_enhancer, estimator_agent, ba_agent, market_agent, gtm_agent, build_vs_outsource_agent],
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