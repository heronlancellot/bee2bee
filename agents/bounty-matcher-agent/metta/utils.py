# utils.py
"""
Utility functions for bounty matching
- GitHub Issues fetching
- User profile analysis
- Match calculation
- Response formatting
"""

import requests
from typing import Dict, Any, List
import re


def fetch_github_issues(owner: str, repo: str, labels: str = "good first issue") -> List[Dict[str, Any]]:
    """Fetch GitHub issues for bounty matching"""
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        params = {
            "state": "open",
            "labels": labels,
            "per_page": 20
        }

        response = requests.get(
            url,
            headers={"Accept": "application/vnd.github.v3+json"},
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            return []

        issues = response.json()

        # Transform to bounty format
        bounties = []
        for issue in issues:
            bounty = extract_bounty_from_issue(issue)
            bounties.append(bounty)

        return bounties

    except Exception as e:
        print(f"Error fetching issues: {e}")
        return []


def extract_bounty_from_issue(issue: Dict) -> Dict[str, Any]:
    """Extract bounty information from GitHub issue"""
    try:
        # Extract bounty value from labels or body
        bounty_value = 0
        for label in issue.get("labels", []):
            label_name = label.get("name", "").lower()
            if "bounty" in label_name or "$" in label_name:
                # Try to extract dollar amount
                match = re.search(r'\$(\d+)', label_name)
                if match:
                    bounty_value = int(match.group(1))

        # Detect required skills from labels and body
        required_skills = []
        for label in issue.get("labels", []):
            label_name = label.get("name", "")
            # Common skill labels
            skills = ["Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C++",
                     "React", "Vue", "Angular", "Django", "Flask", "FastAPI"]
            for skill in skills:
                if skill.lower() in label_name.lower():
                    required_skills.append(skill)

        # Estimate complexity from labels
        complexity_score = 5  # Default: moderate
        for label in issue.get("labels", []):
            label_name = label.get("name", "").lower()
            if "good first issue" in label_name or "easy" in label_name:
                complexity_score = 3
            elif "hard" in label_name or "difficult" in label_name:
                complexity_score = 8
            elif "critical" in label_name or "complex" in label_name:
                complexity_score = 9

        # Estimate hours (rough heuristic)
        estimated_hours = complexity_score * 2

        return {
            "issue_number": issue.get("number"),
            "title": issue.get("title"),
            "body": issue.get("body", "")[:500],  # First 500 chars
            "url": issue.get("html_url"),
            "repo": issue.get("repository_url", "").split("/")[-2:],
            "labels": [label.get("name") for label in issue.get("labels", [])],
            "created_at": issue.get("created_at"),
            "bounty_value": bounty_value,
            "required_skills": required_skills,
            "complexity_score": complexity_score,
            "estimated_hours": estimated_hours,
            "comments_count": issue.get("comments", 0)
        }

    except Exception as e:
        print(f"Error extracting bounty: {e}")
        return {}


def analyze_user_profile(user_data: Dict) -> Dict[str, Any]:
    """Analyze user profile for matching"""
    try:
        # Extract user information
        skills = user_data.get("skills", [])
        years_experience = user_data.get("years_experience", 0)
        completed_bounties = user_data.get("completed_bounties", 0)
        avg_complexity_solved = user_data.get("avg_complexity_solved", 5)

        # Extract preferences
        preferences = user_data.get("preferences", {})
        min_bounty = preferences.get("min_bounty", 0)
        max_bounty = preferences.get("max_bounty", 10000)
        max_hours_per_week = preferences.get("max_hours_per_week", 40)
        preferred_languages = preferences.get("preferred_languages", [])

        return {
            "skills": skills,
            "years_experience": years_experience,
            "completed_bounties": completed_bounties,
            "avg_complexity_solved": avg_complexity_solved,
            "preferences": {
                "min_bounty": min_bounty,
                "max_bounty": max_bounty,
                "max_hours_per_week": max_hours_per_week,
                "preferred_languages": preferred_languages
            },
            "skill_domains": list(set([
                get_skill_domain(skill) for skill in skills
            ])),
            "experience_level": get_experience_level(years_experience)
        }

    except Exception as e:
        print(f"Error analyzing user profile: {e}")
        return {}


def get_skill_domain(skill: str) -> str:
    """Map skill to domain"""
    domain_map = {
        "Python": "backend-scripting",
        "JavaScript": "frontend-web",
        "TypeScript": "frontend-web",
        "Java": "backend-enterprise",
        "Go": "backend-systems",
        "Rust": "systems-programming",
        "React": "frontend-web",
        "Vue": "frontend-web",
        "Angular": "frontend-web",
        "Django": "backend-web",
        "Flask": "backend-web",
        "FastAPI": "backend-web"
    }
    return domain_map.get(skill, "general-programming")


def get_experience_level(years: float) -> str:
    """Determine experience level"""
    if years < 1:
        return "beginner"
    elif years < 3:
        return "intermediate"
    elif years < 5:
        return "advanced"
    else:
        return "expert"


def find_best_matches(user_profile: Dict, bounties: List[Dict], rag, top_n: int = 5) -> List[Dict]:
    """Find best bounty matches for user using MeTTa reasoning"""
    try:
        matches = []

        for bounty in bounties:
            # Calculate match confidence using MeTTa RAG
            match_analysis = rag.calculate_match_confidence(user_profile, bounty)

            matches.append({
                "bounty": bounty,
                "match_analysis": match_analysis,
                "confidence_score": match_analysis["confidence_score"]
            })

        # Sort by confidence
        matches.sort(key=lambda x: x["confidence_score"], reverse=True)

        return matches[:top_n]

    except Exception as e:
        print(f"Error finding matches: {e}")
        return []


def format_match_response(matches: List[Dict], user_profile: Dict) -> str:
    """Format bounty matches into readable response"""
    try:
        if not matches:
            return "❌ No matching bounties found. Try adjusting your preferences or skills."

        response = f"# 🎯 Top Bounty Matches for You\n\n"
        response += f"**Your Profile:** {', '.join(user_profile.get('skills', []))}\n"
        response += f"**Experience:** {user_profile.get('experience_level', 'unknown').title()}\n\n"

        for idx, match in enumerate(matches, 1):
            bounty = match["bounty"]
            analysis = match["match_analysis"]

            # Confidence emoji
            conf_score = analysis["confidence_score"]
            if conf_score >= 80:
                conf_emoji = "🟢"
            elif conf_score >= 60:
                conf_emoji = "🟡"
            else:
                conf_emoji = "🔴"

            response += f"## {idx}. {bounty['title']}\n\n"
            response += f"**Repository:** {'/'.join(bounty.get('repo', ['unknown', 'repo']))}\n"
            response += f"💰 **Bounty:** ${bounty['bounty_value']}\n"
            response += f"⏱️ **Estimated Time:** ~{bounty['estimated_hours']} hours\n"
            response += f"🎯 **Complexity:** {bounty['complexity_score']}/10\n"
            response += f"{conf_emoji} **Match Confidence:** {conf_score}% ({analysis['confidence_level']})\n\n"

            response += f"**Why This Matches:**\n"
            for reason in analysis.get("reasoning", []):
                response += f"  • {reason}\n"

            response += f"\n**Required Skills:** {', '.join(bounty.get('required_skills', ['General']))}\n"
            response += f"**Labels:** {', '.join(bounty.get('labels', []))}\n"
            response += f"🔗 [View Issue]({bounty['url']})\n\n"

            response += f"**Recommendation:** {analysis.get('recommendation', 'CONSIDER')}\n\n"
            response += "---\n\n"

        response += f"\n_🧠 Analysis powered by MeTTa reasoning engine_"

        return response

    except Exception as e:
        print(f"Error formatting response: {e}")
        return f"❌ Error formatting matches: {str(e)}"


def format_error_response(error_message: str) -> str:
    """Format error response"""
    return f"❌ Error: {error_message}\n\nPlease try again or contact support."
