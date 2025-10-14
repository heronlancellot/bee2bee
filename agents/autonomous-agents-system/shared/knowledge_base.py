# shared/knowledge_base.py
"""
Shared MeTTa Knowledge Base for All Agents
This is the central knowledge graph that all agents access and contribute to
"""

from hyperon import MeTTa, E, S, ValueAtom
from typing import Dict, Any, List
import json
import os


class SharedKnowledgeBase:
    """
    Centralized knowledge base that all agents can query and update

    This enables:
    - Cross-agent learning
    - Consistent reasoning
    - Knowledge sharing
    - Historical patterns
    """

    def __init__(self):
        self.metta = MeTTa()
        self._initialize_base_knowledge()
        self._load_learned_knowledge()

    def _initialize_base_knowledge(self):
        """Initialize core knowledge that all agents share"""

        # ==================== SKILL LEVELS ====================
        self.metta.space().add_atom(E(S("skill-level"), S("beginner"), ValueAtom(0)))
        self.metta.space().add_atom(E(S("skill-level"), S("intermediate"), ValueAtom(1)))
        self.metta.space().add_atom(E(S("skill-level"), S("advanced"), ValueAtom(3)))
        self.metta.space().add_atom(E(S("skill-level"), S("expert"), ValueAtom(5)))

        # ==================== BOUNTY TIERS ====================
        self.metta.space().add_atom(E(S("bounty-tier"), S("micro"), ValueAtom(10)))
        self.metta.space().add_atom(E(S("bounty-tier"), S("small"), ValueAtom(50)))
        self.metta.space().add_atom(E(S("bounty-tier"), S("medium"), ValueAtom(200)))
        self.metta.space().add_atom(E(S("bounty-tier"), S("large"), ValueAtom(500)))
        self.metta.space().add_atom(E(S("bounty-tier"), S("xlarge"), ValueAtom(1000)))

        # ==================== COMPLEXITY ====================
        self.metta.space().add_atom(E(S("complexity-level"), S("trivial"), ValueAtom(1)))
        self.metta.space().add_atom(E(S("complexity-level"), S("easy"), ValueAtom(3)))
        self.metta.space().add_atom(E(S("complexity-level"), S("moderate"), ValueAtom(5)))
        self.metta.space().add_atom(E(S("complexity-level"), S("hard"), ValueAtom(7)))
        self.metta.space().add_atom(E(S("complexity-level"), S("very-hard"), ValueAtom(9)))

        # ==================== REPOSITORY SIZE ====================
        self.metta.space().add_atom(E(S("repo-size"), S("tiny"), ValueAtom(100)))
        self.metta.space().add_atom(E(S("repo-size"), S("small"), ValueAtom(500)))
        self.metta.space().add_atom(E(S("repo-size"), S("medium"), ValueAtom(2000)))
        self.metta.space().add_atom(E(S("repo-size"), S("large"), ValueAtom(10000)))
        self.metta.space().add_atom(E(S("repo-size"), S("huge"), ValueAtom(50000)))

        # ==================== LANGUAGE → DOMAIN ====================
        languages_domains = {
            "Python": "backend-scripting",
            "JavaScript": "frontend-web",
            "TypeScript": "frontend-web",
            "Java": "backend-enterprise",
            "Go": "backend-systems",
            "Rust": "systems-programming",
            "C++": "systems-programming",
            "C#": "backend-enterprise",
            "Ruby": "backend-web",
            "PHP": "backend-web",
            "Swift": "mobile-ios",
            "Kotlin": "mobile-android",
            "Solidity": "blockchain",
        }

        for lang, domain in languages_domains.items():
            self.metta.space().add_atom(
                E(S("language-domain"), S(lang), ValueAtom(domain))
            )

        # ==================== ISSUE TYPES → SKILLS ====================
        issue_skills = {
            "bug-fix": "debugging",
            "feature": "development",
            "documentation": "writing",
            "refactoring": "architecture",
            "performance": "optimization",
            "security": "security-audit",
            "testing": "qa-testing",
        }

        for issue_type, skill in issue_skills.items():
            self.metta.space().add_atom(
                E(S("issue-type-skill"), S(issue_type), ValueAtom(skill))
            )

        # ==================== CONFIDENCE LEVELS ====================
        self.metta.space().add_atom(E(S("confidence-level"), S("low"), ValueAtom(30)))
        self.metta.space().add_atom(E(S("confidence-level"), S("medium"), ValueAtom(60)))
        self.metta.space().add_atom(E(S("confidence-level"), S("high"), ValueAtom(80)))
        self.metta.space().add_atom(E(S("confidence-level"), S("perfect"), ValueAtom(95)))

        # ==================== TIME ESTIMATES ====================
        self.metta.space().add_atom(E(S("time-estimate"), S("quick"), ValueAtom(2)))
        self.metta.space().add_atom(E(S("time-estimate"), S("short"), ValueAtom(8)))
        self.metta.space().add_atom(E(S("time-estimate"), S("medium"), ValueAtom(20)))
        self.metta.space().add_atom(E(S("time-estimate"), S("long"), ValueAtom(40)))
        self.metta.space().add_atom(E(S("time-estimate"), S("very-long"), ValueAtom(80)))

    def _load_learned_knowledge(self):
        """Load previously learned patterns and insights"""
        knowledge_file = "shared_knowledge.json"

        if os.path.exists(knowledge_file):
            try:
                with open(knowledge_file, 'r') as f:
                    learned = json.load(f)
                    # TODO: Re-add learned patterns to MeTTa space
                    print(f"[SharedKB] Loaded {len(learned.get('patterns', []))} learned patterns")
            except Exception as e:
                print(f"[SharedKB] Error loading learned knowledge: {e}")

    def add_user_insight(self, user_id: str, insight: Dict[str, Any]):
        """
        Agent contributes insight about a user
        Example: UserProfileAgent shares that user prefers repos < 1000 stars
        """
        insight_key = f"user-insight-{user_id}"

        # Store in MeTTa (simplified - real implementation would be more complex)
        # self.metta.space().add_atom(...)

        print(f"[SharedKB] Added user insight: {insight}")

    def add_repo_insight(self, repo: str, insight: Dict[str, Any]):
        """
        Agent contributes insight about a repository
        Example: RepoAnalyzer shares repo health score
        """
        print(f"[SharedKB] Added repo insight for {repo}: {insight}")

    def add_match_pattern(self, pattern: Dict[str, Any]):
        """
        Agent contributes successful match pattern
        Example: SkillMatcher shares that Python+asyncio users like certain issues
        """
        print(f"[SharedKB] Added match pattern: {pattern}")

    def query_skill_level(self, years_experience: float) -> str:
        """Query skill level based on experience"""
        try:
            query_str = '!(match &self (skill-level $level $threshold) ($level $threshold))'
            results = self.metta.run(query_str)

            thresholds = []
            for r in results:
                if r and len(r) > 0:
                    if len(r) == 1 and hasattr(r[0], 'get_children'):
                        children = r[0].get_children()
                        if len(children) >= 2:
                            level = str(children[0]).strip()
                            threshold = children[1].get_object().value if hasattr(children[1], 'get_object') else 0
                            thresholds.append((level, threshold))

            thresholds.sort(key=lambda x: x[1], reverse=True)

            for level, threshold in thresholds:
                if years_experience >= threshold:
                    return level

            return "beginner"
        except Exception as e:
            print(f"Error in query_skill_level: {e}")
            return "beginner"

    def query_language_domain(self, language: str) -> str:
        """Query domain for a programming language"""
        try:
            query_str = f'!(match &self (language-domain {language} $domain) $domain)'
            results = self.metta.run(query_str)

            if results and len(results) > 0 and results[0]:
                return results[0][0].get_object().value

            return "general-programming"
        except Exception as e:
            print(f"Error in query_language_domain: {e}")
            return "general-programming"

    def query_complexity_level(self, complexity_score: int) -> str:
        """Query complexity level from score"""
        try:
            query_str = '!(match &self (complexity-level $level $score) ($level $score))'
            results = self.metta.run(query_str)

            thresholds = []
            for r in results:
                if r and len(r) > 0:
                    if len(r) == 1 and hasattr(r[0], 'get_children'):
                        children = r[0].get_children()
                        if len(children) >= 2:
                            level = str(children[0]).strip()
                            score = children[1].get_object().value if hasattr(children[1], 'get_object') else 0
                            thresholds.append((level, score))

            thresholds.sort(key=lambda x: x[1], reverse=True)

            for level, score in thresholds:
                if complexity_score >= score:
                    return level

            return "trivial"
        except Exception as e:
            print(f"Error in query_complexity_level: {e}")
            return "moderate"

    def get_metta_instance(self) -> MeTTa:
        """Get MeTTa instance for direct querying"""
        return self.metta

    def save_learned_knowledge(self):
        """Persist learned knowledge to disk"""
        # TODO: Implement saving of learned patterns
        pass


# Global shared knowledge base
shared_kb = SharedKnowledgeBase()
