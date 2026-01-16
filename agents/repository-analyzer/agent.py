# agent.py
from hyperon import MeTTa
from uagents import Context, Model, Protocol, Agent
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)
import os
from datetime import datetime
from dotenv import load_dotenv

# Import MeTTa components
from metta.knowledge import initialize_knowledge_graph
from metta.reporag import RepoRAG
from metta.utils import fetch_github_repo, analyze_file_structure, analyze_with_metta, format_repo_response

# Import protocols
from protocols.repository import repository_proto

# Load environment
load_dotenv()

# Initialize agent
agent = Agent(
    name="Repository Analyzer",
    seed="repo_analyzer_nectardao_2025",
    port=8007,
    mailbox=True,
    publish_agent_details=True
)

# Initialize global MeTTa components
metta = MeTTa()
initialize_knowledge_graph(metta)
rag = RepoRAG(metta)

# Protocol setup
chat_proto = Protocol(spec=chat_protocol_spec)

@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    """Handle incoming chat messages and analyze GitHub repositories."""

    # Extract text from message
    text_content = next(
        (item for item in msg.content if isinstance(item, TextContent)),
        None
    )

    if not text_content:
        await ctx.send(
            sender,
            ChatMessage(
                content=[
                    TextContent(text="❌ No text content found in message.")
                ],
                timestamp=datetime.now(),
                msg_id=msg.msg_id
            )
        )
        return

    user_message = text_content.text.strip()

    ctx.logger.info(f"Analyzing repository: {user_message}")

    # Parse owner/repo from input (format: "owner/repo" or "analyze owner/repo")
    repo_input = user_message.lower().replace("analyze", "").strip()

    if "/" not in repo_input:
        await ctx.send(
            sender,
            ChatMessage(
                content=[
                    TextContent(
                        text="❌ Invalid format. Please use: `owner/repo`\n\nExample: `facebook/react`"
                    )
                ],
                timestamp=datetime.now(),
                msg_id=msg.msg_id
            )
        )
        return

    try:
        owner, repo = repo_input.split("/", 1)
        owner = owner.strip()
        repo = repo.strip()

        # Fetch GitHub repo data
        repo_data = fetch_github_repo(owner, repo)

        if "error" in repo_data:
            await ctx.send(
                sender,
                ChatMessage(
                    content=[
                        TextContent(text=format_repo_response(repo_data, {}))
                    ],
                    timestamp=datetime.now(),
                    msg_id=msg.msg_id
                )
            )
            return

        # Analyze file structure
        file_analysis = analyze_file_structure(repo_data.get('tree', []))

        # MeTTa reasoning
        insights = analyze_with_metta(repo_data, file_analysis, rag)
        repo_data['metta_insights'] = insights

        # Format response
        response_text = format_repo_response(repo_data, file_analysis)

        # Send response
        await ctx.send(
            sender,
            ChatMessage(
                content=[
                    TextContent(text=response_text)
                ],
                timestamp=datetime.now(),
                msg_id=msg.msg_id
            )
        )

        # Send acknowledgement
        await ctx.send(
            sender,
            ChatAcknowledgement(
                msg_id=msg.msg_id,
                ack_type="delivered"
            )
        )

    except ValueError:
        await ctx.send(
            sender,
            ChatMessage(
                content=[
                    TextContent(
                        text="❌ Invalid format. Please use: `owner/repo`\n\nExample: `facebook/react`"
                    )
                ],
                timestamp=datetime.now(),
                msg_id=msg.msg_id
            )
        )
    except Exception as e:
        ctx.logger.error(f"Error analyzing repository: {e}")
        await ctx.send(
            sender,
            ChatMessage(
                content=[
                    TextContent(text=f"❌ Error analyzing repository: {str(e)}")
                ],
                timestamp=datetime.now(),
                msg_id=msg.msg_id
            )
        )

@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    """Handle acknowledgements."""
    ctx.logger.info(f"Received acknowledgement from {sender}: {msg.ack_type}")

# Register protocols
agent.include(chat_proto, publish_manifest=True)  # For chat interface (ASI-1, frontend)
agent.include(repository_proto, publish_manifest=True)  # For inter-agent communication

if __name__ == "__main__":
    agent.run()
