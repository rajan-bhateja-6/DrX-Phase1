# idea_enhancer.py
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.ui import Console
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Use a model that your autogen_ext install supports ("gpt-4o" or "gpt-4.1" if it works in your env)
model_client = OpenAIChatCompletionClient(model="gpt-4o", api_key=api_key)

SYSTEM_PROMPT = """    You are a Go-To-Market (GTM) Strategy Expert. Your role is to create comprehensive GTM strategies for any business idea, product, or service.
    
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
    
    Always end with a 30-60-90 day launch timeline with specific milestones. Ask the user if he/she wants to "reiterate something or can we move onto the Build vs Outsource comparison" and strictly always call the User agent. 
    """

async def main():
    # Start with the human. No manual input() before run_stream — avoids duplicate prompts.
    user_agent = UserProxyAgent(
        name="User",
        input_func=input,
        description="Captures user input and provides feedback in the loop."
    )

    gtm_agent = AssistantAgent(
    name="GTM_Strategy_Generator",
    description="Go to market strategy agent is called after the SWOT_Analyzer has done his job and the user is happy and wants to continue " ,
    model_client=model_client,
    system_message=SYSTEM_PROMPT)

    # Stop when user types /end (or when conversation gets too long)
    termination = (
        TextMentionTermination("/end")
        | TextMentionTermination("TERMINATE")
        | MaxMessageTermination(60)
    )

    team = RoundRobinGroupChat(
        participants=[user_agent, gtm_agent],
        termination_condition=termination,
    )

    print("Tip: start with your idea (e.g., “I want an app to sell used musical instruments”).")

    # IMPORTANT: Don't pass a task here; let UserProxyAgent take the first turn.
    stream = team.run_stream()
    await Console(stream)

    # await model_client.close()  # optional if your env complains about open connectors

if __name__ == "__main__":
    asyncio.run(main())
