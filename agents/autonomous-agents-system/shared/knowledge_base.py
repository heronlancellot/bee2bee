"""
Simple Knowledge Base for Agents
"""


class SharedKnowledgeBase:
    """Shared knowledge base for all agents"""

    def query_complexity_level(self, score: int) -> str:
        """Map complexity score to level"""
        if score <= 2:
            return "trivial"
        elif score <= 4:
            return "easy"
        elif score <= 6:
            return "moderate"
        elif score <= 8:
            return "hard"
        else:
            return "very-hard"

    def query_skill_level(self, years: int) -> str:
        """Map years of experience to skill level"""
        if years < 2:
            return "beginner"
        elif years < 5:
            return "intermediate"
        elif years < 10:
            return "advanced"
        else:
            return "expert"

    def query_language_domain(self, skill: str) -> str:
        """Get domain for a skill"""
        domains = {
            "Python": "backend",
            "JavaScript": "frontend-web",
            "TypeScript": "frontend-web",
            "React": "frontend-web",
            "Node.js": "backend",
            "Go": "backend",
            "Rust": "systems",
            "Java": "backend",
            "C++": "systems",
            "Ruby": "backend",
            "asyncio": "backend",
            "FastAPI": "backend",
        }
        return domains.get(skill, "general")

    def add_user_insight(self, user_id: str, insight: dict):
        """Store user insight (placeholder)"""
        pass

    def add_match_pattern(self, pattern: dict):
        """Store match pattern (placeholder)"""
        pass


# Global instance
shared_kb = SharedKnowledgeBase()
