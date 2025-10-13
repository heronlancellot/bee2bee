"""
Repository Analysis Protocol

Defines messages for requesting repository analysis from Repository Analyzer Agent.
Used by other agents (Security, Matcher, Verifier) to get complexity metrics.
"""

from uagents import Context, Model, Protocol
from typing import Dict, List, Optional
from metta.utils import fetch_github_repo, analyze_file_structure, analyze_with_metta
from metta.reporag import RepoRAG


class RepositoryAnalysisQuery(Model):
    """Query to analyze a repository."""
    repo_full_name: str  # Format: "owner/repo"


class RepositoryAnalysisResponse(Model):
    """Response with repository analysis results."""
    repo_full_name: str
    success: bool
    error: Optional[str] = None

    # Basic stats
    stars: int = 0
    forks: int = 0
    open_issues: int = 0
    file_count: int = 0
    size_kb: int = 0
    contributors_count: int = 0

    # Complexity metrics
    estimated_loc: int = 0
    complexity_tier: str = ""  # simple, moderate, complex, very-complex
    size_category: str = ""  # tiny, small, medium, large, very-large
    difficulty_tier: str = ""  # beginner, intermediate, advanced, expert

    # Scores (0-100)
    documentation_score: int = 0
    test_coverage_score: int = 0
    complexity_score: int = 0  # Weighted final score

    # Details
    project_type: str = ""  # web3-project, ml-project, frontend-app, etc
    tech_domains: List[str] = []
    test_frameworks: List[str] = []
    has_ci: bool = False


# Create protocol
repository_proto = Protocol()


@repository_proto.on_message(model=RepositoryAnalysisQuery, replies=RepositoryAnalysisResponse)
async def handle_repository_analysis(ctx: Context, sender: str, msg: RepositoryAnalysisQuery):
    """
    Handle repository analysis request from another agent.

    Args:
        ctx: Agent context
        sender: Address of requesting agent
        msg: RepositoryAnalysisQuery with repo_full_name
    """
    ctx.logger.info(f"Received repository analysis request for: {msg.repo_full_name}")

    try:
        # Parse owner/repo
        if "/" not in msg.repo_full_name:
            await ctx.send(
                sender,
                RepositoryAnalysisResponse(
                    repo_full_name=msg.repo_full_name,
                    success=False,
                    error="Invalid repo format. Expected: 'owner/repo'"
                )
            )
            return

        owner, repo = msg.repo_full_name.split("/", 1)

        # Fetch repo data
        repo_data = fetch_github_repo(owner, repo)

        if "error" in repo_data:
            await ctx.send(
                sender,
                RepositoryAnalysisResponse(
                    repo_full_name=msg.repo_full_name,
                    success=False,
                    error=repo_data["error"]
                )
            )
            return

        # Analyze file structure
        tree = repo_data.get('tree', [])
        file_analysis = analyze_file_structure(tree)

        # Analyze with MeTTa
        rag = RepoRAG()
        insights = analyze_with_metta(repo_data, file_analysis, rag)

        # Extract metrics
        doc_analysis = insights.get('documentation', {})
        test_analysis = insights.get('test_coverage', {})
        complexity_result = insights.get('complexity_score', {})

        # Build response
        response = RepositoryAnalysisResponse(
            repo_full_name=msg.repo_full_name,
            success=True,
            stars=repo_data.get('stars', 0),
            forks=repo_data.get('forks', 0),
            open_issues=repo_data.get('open_issues', 0),
            file_count=file_analysis.get('file_count', 0),
            size_kb=repo_data.get('size', 0),
            contributors_count=repo_data.get('contributors_count', 0),
            estimated_loc=complexity_result.get('breakdown', {}).get('loc_score', 0),
            complexity_tier=insights.get('complexity_tier', ''),
            size_category=insights.get('size_category', ''),
            difficulty_tier=insights.get('difficulty_tier', ''),
            documentation_score=doc_analysis.get('score', 0),
            test_coverage_score=test_analysis.get('coverage_score', 0),
            complexity_score=complexity_result.get('final_score', 0),
            project_type=insights.get('project_type', ''),
            tech_domains=insights.get('tech_domains', []),
            test_frameworks=test_analysis.get('test_frameworks', []),
            has_ci=test_analysis.get('has_ci', False),
        )

        ctx.logger.info(f"Sending analysis response for {msg.repo_full_name} (score: {response.complexity_score})")
        await ctx.send(sender, response)

    except Exception as e:
        ctx.logger.error(f"Error analyzing repository {msg.repo_full_name}: {e}")
        await ctx.send(
            sender,
            RepositoryAnalysisResponse(
                repo_full_name=msg.repo_full_name,
                success=False,
                error=str(e)
            )
        )
