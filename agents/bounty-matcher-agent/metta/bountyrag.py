# bountyrag.py
"""
BountyRAG - Retrieval Augmented Generation for Bounty Matching
Uses MeTTa reasoning to match developers with bounties
"""

from hyperon import MeTTa, E, S, ValueAtom
from typing import List, Dict, Any


class BountyRAG:
    """RAG system for bounty matching using MeTTa reasoning"""

    def __init__(self, metta_instance: MeTTa):
        self.metta = metta_instance

    def get_skill_level(self, years_experience: float) -> str:
        """Determine skill level based on years of experience"""
        try:
            query_str = '!(match &self (skill-level $level $threshold) ($level $threshold))'
            results = self.metta.run(query_str)

            if not results:
                return "beginner"

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
            print(f"Error in get_skill_level: {e}")
            return "beginner"

    def get_bounty_tier(self, bounty_value: int) -> str:
        """Categorize bounty by value"""
        try:
            query_str = '!(match &self (bounty-tier $tier $threshold) ($tier $threshold))'
            results = self.metta.run(query_str)

            if not results:
                return "micro"

            thresholds = []
            for r in results:
                if r and len(r) > 0:
                    if len(r) == 1 and hasattr(r[0], 'get_children'):
                        children = r[0].get_children()
                        if len(children) >= 2:
                            tier = str(children[0]).strip()
                            threshold = children[1].get_object().value if hasattr(children[1], 'get_object') else 0
                            thresholds.append((tier, threshold))

            thresholds.sort(key=lambda x: x[1], reverse=True)

            for tier, threshold in thresholds:
                if bounty_value >= threshold:
                    return tier

            return "micro"
        except Exception as e:
            print(f"Error in get_bounty_tier: {e}")
            return "micro"

    def get_complexity_level(self, complexity_score: int) -> str:
        """Get complexity level from score (0-10)"""
        try:
            query_str = '!(match &self (complexity-level $level $score) ($level $score))'
            results = self.metta.run(query_str)

            if not results:
                return "moderate"

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
            print(f"Error in get_complexity_level: {e}")
            return "moderate"

    def get_time_estimate_category(self, hours: int) -> str:
        """Categorize time estimate"""
        try:
            query_str = '!(match &self (time-estimate $category $threshold) ($category $threshold))'
            results = self.metta.run(query_str)

            if not results:
                return "medium"

            thresholds = []
            for r in results:
                if r and len(r) > 0:
                    if len(r) == 1 and hasattr(r[0], 'get_children'):
                        children = r[0].get_children()
                        if len(children) >= 2:
                            category = str(children[0]).strip()
                            threshold = children[1].get_object().value if hasattr(children[1], 'get_object') else 0
                            thresholds.append((category, threshold))

            thresholds.sort(key=lambda x: x[1], reverse=True)

            for category, threshold in thresholds:
                if hours >= threshold:
                    return category

            return "quick"
        except Exception as e:
            print(f"Error in get_time_estimate_category: {e}")
            return "medium"

    def get_language_skill_domain(self, language: str) -> str:
        """Get skill domain for a programming language"""
        try:
            query_str = f'!(match &self (language-skill {language} $domain) $domain)'
            results = self.metta.run(query_str)

            if results and len(results) > 0 and results[0]:
                return results[0][0].get_object().value

            return "general-programming"
        except Exception as e:
            print(f"Error in get_language_skill_domain: {e}")
            return "general-programming"

    def get_confidence_level(self, confidence_score: int) -> str:
        """Get confidence level from score (0-100)"""
        try:
            query_str = '!(match &self (confidence-level $level $threshold) ($level $threshold))'
            results = self.metta.run(query_str)

            if not results:
                return "medium"

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
                if confidence_score >= threshold:
                    return level

            return "low"
        except Exception as e:
            print(f"Error in get_confidence_level: {e}")
            return "medium"

    def calculate_match_confidence(self, user_data: Dict, issue_data: Dict) -> Dict[str, Any]:
        """
        Calculate match confidence between user and issue

        Returns comprehensive match analysis
        """
        try:
            confidence_factors = {
                "skill_match": 0,
                "experience_match": 0,
                "complexity_match": 0,
                "bounty_preference_match": 0,
                "time_match": 0
            }

            reasoning = []

            # 1. Skill Match (40 points)
            user_skills = set(user_data.get("skills", []))
            required_skills = set(issue_data.get("required_skills", []))

            if required_skills:
                matches = user_skills.intersection(required_skills)
                skill_match_pct = len(matches) / len(required_skills)
                confidence_factors["skill_match"] = int(skill_match_pct * 40)
                reasoning.append(f"Skill match: {len(matches)}/{len(required_skills)} skills ({skill_match_pct*100:.0f}%)")

            # 2. Experience Match (20 points)
            user_exp = user_data.get("years_experience", 0)
            issue_complexity = issue_data.get("complexity_score", 5)

            skill_level = self.get_skill_level(user_exp)
            required_level = "intermediate" if issue_complexity < 6 else "advanced" if issue_complexity < 8 else "expert"

            exp_match = 20 if skill_level == required_level else 10 if abs(["beginner", "intermediate", "advanced", "expert"].index(skill_level) - ["beginner", "intermediate", "advanced", "expert"].index(required_level)) == 1 else 5
            confidence_factors["experience_match"] = exp_match
            reasoning.append(f"Experience: {skill_level} vs required {required_level}")

            # 3. Complexity Match (15 points)
            user_avg_complexity = user_data.get("avg_complexity_solved", 5)
            complexity_diff = abs(user_avg_complexity - issue_complexity)

            if complexity_diff <= 1:
                confidence_factors["complexity_match"] = 15
            elif complexity_diff <= 2:
                confidence_factors["complexity_match"] = 10
            else:
                confidence_factors["complexity_match"] = 5

            reasoning.append(f"Complexity: issue={issue_complexity}/10, user avg={user_avg_complexity}/10")

            # 4. Bounty Preference Match (15 points)
            bounty_value = issue_data.get("bounty_value", 0)
            user_min_bounty = user_data.get("preferences", {}).get("min_bounty", 0)
            user_max_bounty = user_data.get("preferences", {}).get("max_bounty", 10000)

            if user_min_bounty <= bounty_value <= user_max_bounty:
                confidence_factors["bounty_preference_match"] = 15
                reasoning.append(f"Bounty ${bounty_value} in preferred range")
            else:
                confidence_factors["bounty_preference_match"] = 5
                reasoning.append(f"Bounty ${bounty_value} outside preferred range")

            # 5. Time Match (10 points)
            estimated_hours = issue_data.get("estimated_hours", 10)
            user_max_hours = user_data.get("preferences", {}).get("max_hours_per_week", 40)

            if estimated_hours <= user_max_hours:
                confidence_factors["time_match"] = 10
                reasoning.append(f"Time estimate {estimated_hours}h within capacity")
            else:
                confidence_factors["time_match"] = 5
                reasoning.append(f"Time estimate {estimated_hours}h exceeds capacity")

            # Calculate total confidence
            total_confidence = sum(confidence_factors.values())
            confidence_level = self.get_confidence_level(total_confidence)

            return {
                "confidence_score": total_confidence,
                "confidence_level": confidence_level,
                "confidence_factors": confidence_factors,
                "reasoning": reasoning,
                "recommendation": "HIGHLY RECOMMENDED" if total_confidence >= 80 else "RECOMMENDED" if total_confidence >= 60 else "CONSIDER" if total_confidence >= 40 else "NOT RECOMMENDED"
            }

        except Exception as e:
            print(f"Error calculating match confidence: {e}")
            return {
                "confidence_score": 0,
                "confidence_level": "low",
                "reasoning": [f"Error: {str(e)}"]
            }
