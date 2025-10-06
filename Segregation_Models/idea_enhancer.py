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

SYSTEM_PROMPT = """### Instruction ###
You are **Idea Enhancer AI**, a high-energy, mature product ideation coach.

Your job is to transform the user's evolving idea into a sharper concept *through a conversation*.
Rules:
1) Speak naturally, be vivid and specific.
2) After every message, ask exactly ONE smart follow-up that moves the idea forward.
3) Keep bias/stereotypes out.
4) Keep answers substantial (>= 450 words when the user gives a big prompt; otherwise be concise but meaty).
5) End each turn by explicitly inviting the user to respond (e.g., “Your move—what would you tweak next?”).
6) The final section must include:
   **🛣️ Next Step**
7) Continue collaborating until the user types /end to finish.
"""

async def main():
    # Start with the human. No manual input() before run_stream — avoids duplicate prompts.
    user_agent = UserProxyAgent(
        name="User",
        input_func=input,
        description="Captures user input and provides feedback in the loop."
    )

    idea_agent = AssistantAgent(
        name="IdeaEnhancer",
        model_client=model_client,
        system_message=SYSTEM_PROMPT,
        description="Refines the user's idea into a polished concept and iterates interactively."
    )

    # Stop when user types /end (or when conversation gets too long)
    termination = (
        TextMentionTermination("/end")
        | TextMentionTermination("TERMINATE")
        | MaxMessageTermination(60)
    )

    team = RoundRobinGroupChat(
        participants=[user_agent, idea_agent],
        termination_condition=termination,
    )

    print("Tip: start with your idea (e.g., “I want an app to sell used musical instruments”).")

    # IMPORTANT: Don't pass a task here; let UserProxyAgent take the first turn.
    stream = team.run_stream()
    await Console(stream)

    # await model_client.close()  # optional if your env complains about open connectors

if __name__ == "__main__":
    asyncio.run(main())