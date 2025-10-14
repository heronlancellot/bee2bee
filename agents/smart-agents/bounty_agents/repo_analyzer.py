"""
Repository Analyzer Agent
Analyzes repositories, code quality, and project structure
"""

import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime


class RepoAnalyzer:
    """
    Agent specialized in repository analysis
    
    Capabilities:
    - Analyze repository structure
    - Assess code quality
    - Identify technologies used
    - Evaluate project health
    - Suggest improvements
    """
    
    def __init__(self):
        self.agent_id = "repo_analyzer"
        self.capabilities = [
            "Repository structure analysis",
            "Code quality assessment", 
            "Technology stack identification",
            "Project health evaluation",
            "Improvement suggestions"
        ]
    
    def process(self, query: str, user_id: str = None, context: Dict = None,
               conversation_history: List[Dict] = None) -> Dict:
        """
        Process repository analysis query
        
        Args:
            query: User query about repository analysis
            user_id: User identifier
            context: Additional context (may include repo_url)
            conversation_history: Previous conversation messages
            
        Returns:
            Dict with analysis results
        """
        
        # Extract repository URL from query or context
        repo_url = self._extract_repo_url(query, context)
        
        if not repo_url:
            return {
                "response": "I need a repository URL to analyze. Please provide a GitHub repository link.",
                "agent_id": self.agent_id,
                "metadata": {"error": "no_repo_url"}
            }
        
        try:
            # Analyze repository
            analysis = self._analyze_repository(repo_url)
            
            # Generate response
            response = self._format_analysis_response(analysis, repo_url)
            
            return {
                "response": response,
                "agent_id": self.agent_id,
                "metadata": {
                    "repo_url": repo_url,
                    "analysis": analysis,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "response": f"I encountered an error analyzing the repository: {str(e)}",
                "agent_id": self.agent_id,
                "metadata": {"error": str(e), "repo_url": repo_url}
            }
    
    def _extract_repo_url(self, query: str, context: Dict = None) -> Optional[str]:
        """Extract repository URL from query or context"""
        
        # Check context first
        if context and "repo_url" in context:
            return context["repo_url"]
        
        # Look for GitHub URLs in query
        import re
        
        # GitHub URL patterns
        patterns = [
            r'https://github\.com/[^/\s]+/[^/\s]+',
            r'github\.com/[^/\s]+/[^/\s]+',
            r'https://github\.com/[^/\s]+/[^/\s]+/tree/[^\s]+',
            r'https://github\.com/[^/\s]+/[^/\s]+/blob/[^\s]+'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                url = match.group(0)
                # Clean up URL to basic repo format
                if '/tree/' in url or '/blob/' in url:
                    url = '/'.join(url.split('/')[:5])
                return url
        
        return None
    
    def _analyze_repository(self, repo_url: str) -> Dict:
        """Analyze repository using GitHub API"""
        
        # Extract owner and repo from URL
        parts = repo_url.replace('https://github.com/', '').split('/')
        if len(parts) < 2:
            raise ValueError("Invalid repository URL format")
        
        owner, repo = parts[0], parts[1]
        
        # GitHub API endpoints
        base_url = "https://api.github.com"
        
        # Get repository info
        repo_info = self._fetch_github_data(f"{base_url}/repos/{owner}/{repo}")
        
        # Get repository languages
        languages = self._fetch_github_data(f"{base_url}/repos/{owner}/{repo}/languages")
        
        # Get recent commits
        commits = self._fetch_github_data(f"{base_url}/repos/{owner}/{repo}/commits?per_page=10")
        
        # Get issues (open and closed)
        open_issues = self._fetch_github_data(f"{base_url}/repos/{owner}/{repo}/issues?state=open&per_page=10")
        closed_issues = self._fetch_github_data(f"{base_url}/repos/{owner}/{repo}/issues?state=closed&per_page=10")
        
        # Analyze the data
        analysis = {
            "basic_info": {
                "name": repo_info.get("name"),
                "description": repo_info.get("description"),
                "stars": repo_info.get("stargazers_count", 0),
                "forks": repo_info.get("forks_count", 0),
                "watchers": repo_info.get("watchers_count", 0),
                "created_at": repo_info.get("created_at"),
                "updated_at": repo_info.get("updated_at"),
                "size": repo_info.get("size", 0),
                "language": repo_info.get("language")
            },
            "languages": languages,
            "activity": {
                "recent_commits": len(commits),
                "open_issues": len(open_issues),
                "closed_issues": len(closed_issues),
                "last_commit": commits[0].get("commit", {}).get("author", {}).get("date") if commits else None
            },
            "health_score": self._calculate_health_score(repo_info, commits, open_issues, closed_issues),
            "recommendations": self._generate_recommendations(repo_info, commits, open_issues, closed_issues)
        }
        
        return analysis
    
    def _fetch_github_data(self, url: str) -> Dict:
        """Fetch data from GitHub API"""
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[RepoAnalyzer] GitHub API error: {e}")
            return {}
    
    def _calculate_health_score(self, repo_info: Dict, commits: List, 
                               open_issues: List, closed_issues: List) -> float:
        """Calculate repository health score (0-100)"""
        
        score = 0
        
        # Activity score (40 points)
        if commits:
            score += min(40, len(commits) * 4)  # Max 40 for recent commits
        
        # Issue management (30 points)
        total_issues = len(open_issues) + len(closed_issues)
        if total_issues > 0:
            closed_ratio = len(closed_issues) / total_issues
            score += closed_ratio * 30
        
        # Popularity (20 points)
        stars = repo_info.get("stargazers_count", 0)
        score += min(20, stars / 10)  # 1 point per 10 stars, max 20
        
        # Maintenance (10 points)
        updated_at = repo_info.get("updated_at")
        if updated_at:
            from datetime import datetime, timezone
            last_update = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            days_since_update = (datetime.now(timezone.utc) - last_update).days
            
            if days_since_update < 30:
                score += 10
            elif days_since_update < 90:
                score += 5
        
        return min(100, score)
    
    def _generate_recommendations(self, repo_info: Dict, commits: List,
                                 open_issues: List, closed_issues: List) -> List[str]:
        """Generate improvement recommendations"""
        
        recommendations = []
        
        # Activity recommendations
        if not commits:
            recommendations.append("⚠️ No recent commits - consider adding new features or fixes")
        
        # Issue management
        if len(open_issues) > 20:
            recommendations.append("📋 High number of open issues - consider prioritizing and closing old ones")
        
        # Documentation
        if not repo_info.get("description"):
            recommendations.append("📝 Add a clear repository description")
        
        # Popularity
        stars = repo_info.get("stargazers_count", 0)
        if stars < 5:
            recommendations.append("⭐ Consider improving documentation and examples to attract more stars")
        
        # Maintenance
        updated_at = repo_info.get("updated_at")
        if updated_at:
            from datetime import datetime, timezone
            last_update = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            days_since_update = (datetime.now(timezone.utc) - last_update).days
            
            if days_since_update > 90:
                recommendations.append("🔄 Repository hasn't been updated recently - consider regular maintenance")
        
        return recommendations
    
    def _format_analysis_response(self, analysis: Dict, repo_url: str) -> str:
        """Format analysis results into readable response"""
        
        basic_info = analysis["basic_info"]
        languages = analysis["languages"]
        activity = analysis["activity"]
        health_score = analysis["health_score"]
        recommendations = analysis["recommendations"]
        
        response = f"## 📊 Repository Analysis: {basic_info['name']}\n\n"
        
        # Basic info
        response += f"**Repository:** {repo_url}\n"
        response += f"**Description:** {basic_info['description'] or 'No description'}\n"
        response += f"**Primary Language:** {basic_info['language'] or 'Unknown'}\n"
        response += f"**Stars:** {basic_info['stars']} | **Forks:** {basic_info['forks']} | **Watchers:** {basic_info['watchers']}\n\n"
        
        # Languages
        if languages:
            response += "**Languages Used:**\n"
            total_bytes = sum(languages.values())
            for lang, bytes_count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]:
                percentage = (bytes_count / total_bytes) * 100
                response += f"- {lang}: {percentage:.1f}%\n"
            response += "\n"
        
        # Activity
        response += "**Recent Activity:**\n"
        response += f"- Recent commits: {activity['recent_commits']}\n"
        response += f"- Open issues: {activity['open_issues']}\n"
        response += f"- Closed issues: {activity['closed_issues']}\n"
        if activity['last_commit']:
            response += f"- Last commit: {activity['last_commit'][:10]}\n"
        response += "\n"
        
        # Health score
        health_emoji = "🟢" if health_score >= 80 else "🟡" if health_score >= 60 else "🔴"
        response += f"**Health Score:** {health_emoji} {health_score:.1f}/100\n\n"
        
        # Recommendations
        if recommendations:
            response += "**Recommendations:**\n"
            for rec in recommendations:
                response += f"{rec}\n"
        
        return response
    
    def get_description(self) -> str:
        """Get agent description"""
        return "Analyzes GitHub repositories for code quality, structure, and health metrics"
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return self.capabilities
