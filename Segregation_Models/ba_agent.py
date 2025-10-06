from Templates.brd_template import brd_template
from Templates.frd_template import frd_template
from Templates.rfp_template import rfp_template
from Templates.sow_template import sow_template
from Templates.srs_template import srs_template
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

SYSTEM_PROMPT = f"""INSTRUCTION
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

async def main():
    # Start with the human. No manual input() before run_stream — avoids duplicate prompts.
    user_agent = UserProxyAgent(
        name="User",
        input_func=input,
        description="Captures user input and provides feedback in the loop."
    )

    ba_agent = AssistantAgent(
        name = "BusinessAnalyst",
        model_client=model_client,
        description="Runs after the user is happy with the Market Research. It Generates business documents (BRD, SRS, FRD, SOW, RFP) based on the finalized idea and estimates.",
        system_message=SYSTEM_PROMPT)

    # Stop when user types /end (or when conversation gets too long)
    termination = (
        TextMentionTermination("/end")
        | TextMentionTermination("TERMINATE")
        | MaxMessageTermination(60)
    )

    team = RoundRobinGroupChat(
        participants=[user_agent, ba_agent],
        termination_condition=termination,
    )

    print("Tip: start with your idea (e.g., “I want an app to sell used musical instruments”).")

    # IMPORTANT: Don't pass a task here; let UserProxyAgent take the first turn.
    stream = team.run_stream()
    await Console(stream)

    # await model_client.close()  # optional if your env complains about open connectors

if __name__ == "__main__":
    asyncio.run(main())
