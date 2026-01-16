"""
Security Scan Protocol

Defines messages for requesting security analysis from Security Agent.
Used by Repository Analyzer and other agents to get vulnerability reports.
"""

from uagents import Context, Model, Protocol
from typing import List, Optional, Dict
from utils.dependency_scanner import scan_dependencies
from utils.osv_client import check_vulnerabilities


class Vulnerability(Model):
    """Individual vulnerability details."""
    package: str
    version: str
    vulnerability_id: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    fixed_version: Optional[str] = None


class SecurityScanQuery(Model):
    """Query to scan a repository for security issues."""
    repo_full_name: str  # Format: "owner/repo"
    scan_types: List[str] = ["dependencies"]  # dependencies, credentials, practices


class SecurityScanResponse(Model):
    """Response with security scan results."""
    repo_full_name: str
    success: bool
    error: Optional[str] = None

    # Vulnerability stats
    total_vulnerabilities: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0

    # Detailed vulnerabilities (limited to top 10)
    vulnerabilities: List[Vulnerability] = []

    # Scores
    security_score: int = 100  # 0-100 (100 = no issues)
    security_tier: str = "secure"  # secure, low-risk, medium-risk, high-risk, critical-risk

    # Dependency info
    total_dependencies: int = 0
    outdated_dependencies: int = 0


# Create protocol
security_proto = Protocol()


@security_proto.on_message(model=SecurityScanQuery, replies=SecurityScanResponse)
async def handle_security_scan(ctx: Context, sender: str, msg: SecurityScanQuery):
    """
    Handle security scan request from another agent.

    Args:
        ctx: Agent context
        sender: Address of requesting agent
        msg: SecurityScanQuery with repo_full_name
    """
    ctx.logger.info(f"Received security scan request for: {msg.repo_full_name}")

    try:
        # Parse owner/repo
        if "/" not in msg.repo_full_name:
            await ctx.send(
                sender,
                SecurityScanResponse(
                    repo_full_name=msg.repo_full_name,
                    success=False,
                    error="Invalid repo format. Expected: 'owner/repo'"
                )
            )
            return

        owner, repo = msg.repo_full_name.split("/", 1)

        # Scan dependencies
        ctx.logger.info(f"Scanning dependencies for {msg.repo_full_name}...")
        dependencies = await scan_dependencies(owner, repo)

        if not dependencies['success']:
            await ctx.send(
                sender,
                SecurityScanResponse(
                    repo_full_name=msg.repo_full_name,
                    success=False,
                    error=dependencies.get('error', 'Failed to scan dependencies')
                )
            )
            return

        # Check vulnerabilities via OSV.dev
        ctx.logger.info(f"Checking vulnerabilities for {len(dependencies['dependencies'])} packages...")
        vuln_results = await check_vulnerabilities(dependencies['dependencies'])

        # Count by severity
        critical = sum(1 for v in vuln_results if v['severity'] == 'CRITICAL')
        high = sum(1 for v in vuln_results if v['severity'] == 'HIGH')
        medium = sum(1 for v in vuln_results if v['severity'] == 'MEDIUM')
        low = sum(1 for v in vuln_results if v['severity'] == 'LOW')

        total_vulns = len(vuln_results)

        # Calculate security score (0-100)
        score = 100
        score -= critical * 25  # -25 per critical
        score -= high * 10      # -10 per high
        score -= medium * 3     # -3 per medium
        score -= low * 1        # -1 per low
        score = max(0, score)

        # Determine tier
        if critical > 0:
            tier = "critical-risk"
        elif high > 2:
            tier = "high-risk"
        elif medium > 5:
            tier = "medium-risk"
        elif low > 10:
            tier = "low-risk"
        else:
            tier = "secure"

        # Convert to Vulnerability models (top 10 only)
        vulnerabilities = [
            Vulnerability(
                package=v['package'],
                version=v['version'],
                vulnerability_id=v['id'],
                severity=v['severity'],
                description=v['description'],
                fixed_version=v.get('fixed_version')
            )
            for v in vuln_results[:10]
        ]

        # Build response
        response = SecurityScanResponse(
            repo_full_name=msg.repo_full_name,
            success=True,
            total_vulnerabilities=total_vulns,
            critical=critical,
            high=high,
            medium=medium,
            low=low,
            vulnerabilities=vulnerabilities,
            security_score=score,
            security_tier=tier,
            total_dependencies=dependencies['total_count'],
            outdated_dependencies=0  # TODO: implement
        )

        ctx.logger.info(
            f"Security scan complete: {total_vulns} vulnerabilities found "
            f"(C:{critical}, H:{high}, M:{medium}, L:{low}), score: {score}/100"
        )

        await ctx.send(sender, response)

    except Exception as e:
        ctx.logger.error(f"Error scanning repository {msg.repo_full_name}: {e}")
        await ctx.send(
            sender,
            SecurityScanResponse(
                repo_full_name=msg.repo_full_name,
                success=False,
                error=str(e)
            )
        )
