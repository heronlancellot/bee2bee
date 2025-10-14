"""
Chat Protocol for Security Agent

Handles chat-based interactions with frontend/users via ASI-1.
"""

from uagents import Context, Model, Protocol
from typing import Optional
import re

# Chat models
class ChatMessage(Model):
    """Incoming chat message from user."""
    message: str

class ChatResponse(Model):
    """Response to user's chat message."""
    response: str

# Initialize protocol
chat_proto = Protocol(name="AgentChatProtocol")


@chat_proto.on_message(model=ChatMessage, replies=ChatResponse)
async def handle_chat(ctx: Context, sender: str, msg: ChatMessage):
    """
    Handle chat messages from frontend/users.

    Expected formats:
    - "Scan <repo_url>" or "Security scan <repo_url>"
    - "Check vulnerabilities in <repo_url>"
    - "Analyze security <repo_url>"
    """
    user_message = msg.message.lower().strip()

    ctx.logger.info(f"💬 Received chat message: {msg.message}")

    # Extract GitHub repo URL or owner/repo format
    github_patterns = [
        r'github\.com/([a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+)',
        r'([a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+)',
    ]

    repo_full_name = None
    for pattern in github_patterns:
        match = re.search(pattern, msg.message)
        if match:
            repo_full_name = match.group(1).rstrip('/')
            # Remove .git suffix if present
            repo_full_name = repo_full_name.replace('.git', '')
            break

    if not repo_full_name:
        response = (
            "❌ Could not find a valid GitHub repository in your message.\n\n"
            "Please provide a repository in one of these formats:\n"
            "- `scan github.com/owner/repo`\n"
            "- `check vulnerabilities in owner/repo`\n"
            "- `security scan owner/repo`"
        )
        await ctx.send(sender, ChatResponse(response=response))
        return

    ctx.logger.info(f"🔍 Scanning repository: {repo_full_name}")

    # Import here to avoid circular imports
    from utils.dependency_scanner import scan_dependencies
    from utils.osv_client import check_vulnerabilities

    try:
        # Split owner/repo
        parts = repo_full_name.split('/')
        if len(parts) != 2:
            raise ValueError("Invalid repository format")

        owner, repo = parts

        # Scan dependencies
        ctx.logger.info(f"📦 Scanning dependencies for {owner}/{repo}...")
        dep_result = await scan_dependencies(owner, repo)

        if not dep_result['success']:
            response = f"❌ Failed to scan dependencies: {dep_result.get('error', 'Unknown error')}"
            await ctx.send(sender, ChatResponse(response=response))
            return

        dependencies = dep_result['dependencies']
        ctx.logger.info(f"📦 Found {len(dependencies)} dependencies")

        if len(dependencies) == 0:
            response = (
                f"✅ **Security Scan Complete: {repo_full_name}**\n\n"
                f"No dependency files found (package.json, requirements.txt, etc.)\n\n"
                f"🛡️ **Security Score:** 100/100 (No dependencies to scan)\n"
                f"📊 **Security Tier:** Secure"
            )
            await ctx.send(sender, ChatResponse(response=response))
            return

        # Check vulnerabilities
        ctx.logger.info(f"🔍 Checking vulnerabilities via OSV.dev...")
        vulnerabilities = await check_vulnerabilities(dependencies)

        # Calculate stats
        total_vulns = len(vulnerabilities)
        critical = sum(1 for v in vulnerabilities if v['severity'] == 'CRITICAL')
        high = sum(1 for v in vulnerabilities if v['severity'] == 'HIGH')
        medium = sum(1 for v in vulnerabilities if v['severity'] == 'MEDIUM')
        low = sum(1 for v in vulnerabilities if v['severity'] == 'LOW')
        unknown = total_vulns - (critical + high + medium + low)

        # Calculate security score (0-100)
        score = 100
        score -= critical * 20  # -20 per critical
        score -= high * 10      # -10 per high
        score -= medium * 5     # -5 per medium
        score -= low * 2        # -2 per low
        score = max(0, score)

        # Determine tier
        if score >= 90:
            tier = "Secure"
            tier_emoji = "🟢"
        elif score >= 70:
            tier = "Good"
            tier_emoji = "🟡"
        elif score >= 50:
            tier = "Fair"
            tier_emoji = "🟠"
        else:
            tier = "At Risk"
            tier_emoji = "🔴"

        # Build response
        response = f"🔐 **Security Scan Complete: {repo_full_name}**\n\n"
        response += f"📦 **Dependencies Scanned:** {len(dependencies)}\n\n"

        if total_vulns > 0:
            response += f"⚠️ **Vulnerabilities Found:** {total_vulns}\n"
            response += f"   🔴 Critical: {critical}\n"
            response += f"   🟠 High: {high}\n"
            response += f"   🟡 Medium: {medium}\n"
            response += f"   🟢 Low: {low}\n"
            if unknown > 0:
                response += f"   ⚪ Unknown: {unknown}\n"
            response += f"\n"

            # Show top 5 vulnerabilities
            response += f"📋 **Top Vulnerabilities:**\n"
            for vuln in vulnerabilities[:5]:
                response += f"\n• **{vuln['package']}** @ {vuln['version']}\n"
                response += f"  Severity: {vuln['severity']}\n"
                response += f"  ID: {vuln['id']}\n"
                desc = vuln['description'][:100] + "..." if len(vuln['description']) > 100 else vuln['description']
                response += f"  {desc}\n"

            if total_vulns > 5:
                response += f"\n_...and {total_vulns - 5} more vulnerabilities_\n"
        else:
            response += f"✅ **No vulnerabilities found!**\n\n"

        response += f"\n🛡️ **Security Score:** {score}/100\n"
        response += f"📊 **Security Tier:** {tier_emoji} {tier}"

        await ctx.send(sender, ChatResponse(response=response))
        ctx.logger.info(f"✅ Security scan complete for {repo_full_name}")

    except Exception as e:
        ctx.logger.error(f"❌ Error scanning repository: {str(e)}")
        response = f"❌ Error scanning repository: {str(e)}"
        await ctx.send(sender, ChatResponse(response=response))
