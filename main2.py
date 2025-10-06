import asyncio
import os
import json
from datetime import datetime
from typing import List, Dict, Any
from Templates.brd_template import brd_template
from Templates.frd_template import frd_template
from Templates.rfp_template import rfp_template
from Templates.sow_template import sow_template
from Templates.srs_template import srs_template

from Sample_output.budget import budget
from Sample_output.team_structure import team_structure
from Sample_output.tech_stack import tech_stack
from Sample_output.timeline import timeline
from Sample_output.market_research import market_research

# Updated imports for AutoGen 0.4+ compatibility
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import SelectorGroupChat, RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.ui import Console

# Web search imports
try:
    from ddgs import DDGS
except ImportError:
    print("Installing ddgs...")
    import subprocess
    subprocess.check_call(["pip", "install", "ddgs"])
    from ddgs import DDGS

from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

model_client = OpenAIChatCompletionClient(model = 'gpt-4.1', api_key=api_key)

# Web Search Tool Functions
# 1. Update search functions to accept queries
def search_competitors(queries: list) -> str:
    ddgs = DDGS()
    all_results = []
    for query in queries:
        try:
            results = list(ddgs.text(query, max_results=3))
            all_results.extend(results)
        except Exception as e:
            print(f"Search error for query '{query}': {e}")
    formatted_results = []
    for result in all_results[:15]:
        formatted_results.append({
            "title": result.get("title", ""),
            "body": result.get("body", ""),
            "href": result.get("href", "")
        })
    return json.dumps(formatted_results, indent=2)

def search_market_data(queries: list) -> str:
    ddgs = DDGS()
    all_results = []
    for query in queries:
        try:
            results = list(ddgs.text(query, max_results=3))
            all_results.extend(results)
        except Exception as e:
            print(f"Search error for query '{query}': {e}")
    formatted_results = []
    for result in all_results[:12]:
        formatted_results.append({
            "title": result.get("title", ""),
            "body": result.get("body", ""),
            "href": result.get("href", "")
        })
    return json.dumps(formatted_results, indent=2)

def search_industry_trends(queries: list) -> str:
    ddgs = DDGS()
    all_results = []
    for query in queries:
        try:
            results = list(ddgs.text(query, max_results=3))
            all_results.extend(results)
        except Exception as e:
            print(f"Search error for query '{query}': {e}")
    formatted_results = []
    for result in all_results[:12]:
        formatted_results.append({
            "title": result.get("title", ""),
            "body": result.get("body", ""),
            "href": result.get("href", "")
        })
    return json.dumps(formatted_results, indent=2)

def search_recent_news(queries: list) -> str:
    ddgs = DDGS()
    all_results = []
    for query in queries:
        try:
            news_results = list(ddgs.news(query, max_results=3))
            all_results.extend(news_results)
        except Exception as e:
            print(f"News search error for query '{query}': {e}")
            try:
                results = list(ddgs.text(query, max_results=2))
                all_results.extend(results)
            except Exception as e2:
                print(f"Text search fallback error: {e2}")
    formatted_results = []
    for result in all_results[:10]:
        formatted_results.append({
            "title": result.get("title", ""),
            "body": result.get("body", ""),
            "href": result.get("href", ""),
            "date": result.get("date", "")
        })
    return json.dumps(formatted_results, indent=2)

async def main():
    model_client = OpenAIChatCompletionClient(model='gpt-4.1', api_key=api_key)

    user_proxy = UserProxyAgent(
        name="User",
        input_func=input,
        description="Captures user input and provides feedback. It is called after each agent response no matter who is the agent."
    )

    idea_enhancer = AssistantAgent(
        name="IdeaEnhancer",
        model_client=model_client,
        system_message="""###Instruction###
            You are **Idea Enhancer AI**, a high-energy and Mature product ideation coach.  
            Your task is to transform the raw <IDEA_INPUT> into a full-length concept deck in the *exact* structure below. You MUST:

            1. Follow the section order & emoji markers verbatim.  
            2. Write at least 450 words; aim for vivid, expressive copy (never short).  
            3. Keep the vibe playful but clear—think pitch-deck meets group-chat.  
            4. Use second-person where natural ("you jump into…").  
            5. Ensure that your answer is unbiased and does not rely on stereotypes.  
            6. Answer the question given in a natural human-like manner.  
            7. Finish with **🛣️ Next Step** questions; question 1 MUST always be the same i.e.-> 
               *"Did you like this idea? Do you want to iterate it further or just move on to next step."*

            ###Output Format (primer starts below—do not delete emojis or quotes)###
            💡 **Concept:** _{Catchy Name}_  
            "_{Tagline in quotes (≤ 12 words)}_"

            🚀 **Concept Overview**  
            {1–2 juicy paragraphs describing what it is, why it matters, and the big aha.}

            🧠 **Core Philosophy**  
            - ✨ _Vibe-first_ → {one-line explainer}  
            - 🌀 _Live & rotating_ → {one-line explainer}  
            - 🎮 _Fun & interactive_ → {one-line explainer}  
            - 💬 _Talk before looks_ → {one-line explainer}  
            (Feel free to rename/expand bullets to fit the idea.)

            🧩 **Key Features**  
            1. **{Emoji + Feature Name} (Core Mechanic)**  
               _How it works:_ {3–4 bullet rundown or mini-narrative}  
            2. **{Emoji + Feature Name}**  
               {details…}  
            3. **{Emoji + Feature Name}**  
               {details…}  
            4. **{Emoji + Feature Name}**  
               {details…}  
            5. **{Emoji + Feature Name}**  
               {details…}

            🔮 **AI Assist (Optional)**  
            If relevant, outline any AI-powered matchmaking, content curation, safety, etc.

            💰 **Monetization & Growth Hooks**  
            Briefly outline possible revenue streams + viral loops.

            🛡️ **Safety & Trust Layer**  
            Summarise privacy, moderation, control features in 2–3 sentences.

            🛣️ **Next Step — Questions for You**  
            1. Did you like this idea? Do you want to iterate it further or just move on to next step.  
            2. What part of the concept excites you most (so we double-down)?  
            3. Which feature feels least clear or risky to you?  
            4. Any must-have integrations or platforms we should consider?  
            5. What success metric would make this idea a win in your eyes?
        """,
        description="A creative AI agent that transforms vague ideas into polished product concepts, complete with a name, description, key features, and next-step suggestions."
    )

    estimator_agent = AssistantAgent(
        name="estimator_agent",
        model_client=model_client,
        description="Provides cost, timeline, tech stack, and team composition estimates based on a finalized business or product idea.",
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

        Be concise and clear. Use markdown format. After providing the estimates, ask the user if they would like to make any iterations with the provided requirements. If not, ask if they would like to generate business documents (BRD, SRS, FRD, SOW, or RFP?). If the answer is positive then trigger the 'BusinessAnalyst'"""
    )
    
    ba_agent = AssistantAgent(
        name="BusinessAnalyst",
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

        If ambiguous (e.g., "make me something"), ask:
        "Which document would you like me to generate: BRD, SRS, FRD, SOW, or RFP?"

        Only generate one document per request and the document should be long and extensive, try to incorporate as many things from the idea as possible. 

        After each document, ask:
        ➤ "Would you like me to generate another document (BRD, SRS, FRD, SOW, RFP), or move towards product market analysis?"
        """
    )
    
    market_query_formulator = AssistantAgent(
        name="MarketQueryFormulator",
        model_client=model_client,
        description="Generates tailored web search queries for market research based on the business idea, industry, and research goal.",
        system_message="""You are a market research query expert. 
        Given a business idea, industry, and a research goal (e.g., 'find competitors', 'market size', 'industry trends', 'recent news'), 
        generate a list of 3-5 highly relevant, up-to-date, and specific search queries for that goal. 
        Return ONLY a Python list of strings. Do not include any explanation or extra text.
        Strictly formulate the queries that help fetch a large number of data and use the current year i.e. 2025 for formulating these queries."""
    )

    market_search_agent = AssistantAgent(
    name="MarketSearcherAgent",
    model_client=model_client,
    description="Executes market research web queries and gathers raw search results for analysis.",
    system_message="""
    ### MARKET RESEARCH SEARCH AGENT ###
    You are a specialized search agent. Your task is to:
    1. Formulate tailored search queries (3–5) for each research goal.
    2. Use the current year (2025) in all search queries.
    3. Run real-time web searches using the correct tools:
    - 'find competitors' → search_competitors
    - 'market size' → search_market_data
    - 'industry trends' → search_industry_trends
    - 'recent news' → search_recent_news

    ### OUTPUT FORMAT:
    Return a JSON object with 4 keys:
    - "competitors": [... raw search results ...]
    - "market_size": [... raw search results ...]
    - "industry_trends": [... raw search results ...]
    - "recent_news": [... raw search results ...]

    DO NOT analyze or summarize.
    Only search and return raw data with source URLs.
    """,
    tools=[search_competitors, search_market_data, search_industry_trends, search_recent_news]
)

    market_report_agent = AssistantAgent(
    name="MarketReportWriterAgent",
    model_client=model_client,
    description="Analyzes market research search results and generates a detailed, structured report.",
    system_message=f"""
    ### MARKET RESEARCH REPORT WRITER AGENT ###
    You are a senior market research analyst.

    You will be given raw search results grouped under 4 research goals:
    - competitors
    - market size
    - industry trends
    - recent news

    Your task is to:
    1. Carefully analyze each category of results.
    2. Cross-reference multiple sources.
    3. Prioritize recent data (2024–2025).
    4. Include citations and URLs where relevant.

    ### OUTPUT FORMAT:
    {market_research}

    Only output the final structured report. No explanations or notes.
    Do NOT perform any web search — only use the provided data.
    """
    )

    # Now create the team AFTER all agents are defined
    team = SelectorGroupChat(
        participants=[user_proxy, idea_enhancer, estimator_agent, ba_agent, market_query_formulator, market_search_agent, market_report_agent],
        model_client=model_client,
        max_turns=50,
        termination_condition=MaxMessageTermination(max_messages=100)
    )
    
    task = input('Enter your idea here: ')
    stream = team.run_stream(task=task)
    await Console(stream)
    # await model_client.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())