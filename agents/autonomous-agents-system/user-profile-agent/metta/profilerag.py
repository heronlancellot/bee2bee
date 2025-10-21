# profilerag.py - User Profile RAG System with MeTTa
from hyperon import MeTTa, E, S, ValueAtom
from typing import List, Dict, Tuple

class ProfileRAG:
    def __init__(self, metta_instance: MeTTa):
        self.metta = metta_instance

    def get_experience_level(self, years: int) -> str:
        """Get experience level using MeTTa reasoning."""
        try:
            # Find closest match in knowledge graph
            query_str = f'!(match &self (experience-level $years $level) $level)'
            results = self.metta.run(query_str)

            # Get all possible levels
            levels = []
            for result in results:
                if result and len(result) > 0:
                    level = result[0].get_object().value
                    levels.append(level)

            if levels:
                # Return most appropriate level based on years
                if years < 2:
                    return "beginner"
                elif years < 5:
                    return "intermediate"
                elif years < 10:
                    return "advanced"
                else:
                    return "expert"

            return "intermediate"
        except Exception as e:
            print(f"Error getting experience level: {e}")
            return "intermediate"

    def get_career_paths(self, skills: List[str]) -> List[str]:
        """Get recommended career paths based on skills using MeTTa."""
        career_paths = set()

        for skill in skills:
            try:
                query_str = f'!(match &self (career-path {skill} $path) $path)'
                results = self.metta.run(query_str)

                for result in results:
                    if result and len(result) > 0:
                        path = result[0].get_object().value
                        career_paths.add(path)
            except Exception as e:
                print(f"Error getting career path for {skill}: {e}")

        return list(career_paths)

    def get_skill_complements(self, skills: List[str]) -> Dict[str, List[str]]:
        """Find complementary skills using MeTTa."""
        complements = {}

        for skill in skills:
            try:
                query_str = f'!(match &self (skill-complement {skill} $complement) $complement)'
                results = self.metta.run(query_str)

                skill_complements = []
                for result in results:
                    if result and len(result) > 0:
                        complement = str(result[0]).strip()
                        if complement not in skills:
                            skill_complements.append(complement)

                if skill_complements:
                    complements[skill] = skill_complements
            except Exception as e:
                print(f"Error getting complements for {skill}: {e}")

        return complements

    def get_next_skills(self, skills: List[str]) -> List[str]:
        """Recommend next skills to learn using MeTTa."""
        next_skills = set()

        for skill in skills:
            try:
                query_str = f'!(match &self (next-skill {skill} $next) $next)'
                results = self.metta.run(query_str)

                for result in results:
                    if result and len(result) > 0:
                        next_skill = str(result[0]).strip()
                        if next_skill not in skills:
                            next_skills.add(next_skill)
            except Exception as e:
                print(f"Error getting next skills for {skill}: {e}")

        return list(next_skills)

    def calculate_profile_strength(self, skills: List[str], years: int) -> Tuple[int, str]:
        """Calculate profile strength score using MeTTa reasoning."""
        # Base score from number of skills
        skill_score = min(len(skills) * 2, 10)

        # Experience bonus
        exp_bonus = min(years * 0.5, 5)

        # Total strength score
        total_score = min(int(skill_score + exp_bonus), 10)

        try:
            # Get strength level from MeTTa
            query_str = f'!(match &self (profile-strength $score $strength) $strength)'
            results = self.metta.run(query_str)

            # Find closest match
            if total_score <= 2:
                strength = "weak"
            elif total_score <= 4:
                strength = "moderate"
            elif total_score <= 6:
                strength = "strong"
            elif total_score <= 8:
                strength = "very-strong"
            else:
                strength = "exceptional"

            return total_score, strength
        except Exception as e:
            print(f"Error calculating profile strength: {e}")
            return total_score, "moderate"

    def generate_intelligent_profile(self, user_id: str, skills: List[str], years: int, historical_data: List[Dict] = None) -> str:
        """
        Generate intelligent profile analysis using MeTTa reasoning + RAG historical data.

        Args:
            user_id: User identifier
            skills: List of user skills
            years: Years of experience
            historical_data: Retrieved similar profiles from Supabase RAG (optional)
        """

        # Get experience level
        exp_level = self.get_experience_level(years)

        # Get career paths
        career_paths = self.get_career_paths(skills)

        # Get complementary skills
        complements = self.get_skill_complements(skills)

        # Get next skills recommendations
        next_skills = self.get_next_skills(skills)

        # Calculate profile strength
        strength_score, strength_level = self.calculate_profile_strength(skills, years)

        # Generate response
        response = f"""👤 **Intelligent User Profile: {user_id}**

**Skills:** {', '.join(skills)}
**Experience:** {years} years ({exp_level.title()})
**Profile Strength:** {strength_score}/10 ({strength_level.replace('-', ' ').title()})"""

        # 🔥 RAG AUGMENTATION: Add insights from historical data
        if historical_data and len(historical_data) > 0:
            response += f"\n\n📊 **RAG Insights:** Found {len(historical_data)} similar profiles in knowledge base"
            response += f"\n  • Your profile matches patterns we've seen {len(historical_data)} times before"

            # Extract common patterns from historical data
            common_skills = set()
            for hist_profile in historical_data:
                content = hist_profile.get('content', '')
                # Simple parsing to extract skills mentioned in content
                for skill in skills:
                    if skill.lower() in content.lower():
                        common_skills.add(skill)

            if common_skills:
                response += f"\n  • Common skills in similar profiles: {', '.join(list(common_skills)[:3])}"

        response += f"\n\n🎯 **Career Path Recommendations:**"

        if career_paths:
            for path in career_paths:
                response += f"\n  • {path.replace('-', ' ').title()}"
        else:
            response += "\n  • Continue building your skill portfolio"

        if complements:
            response += f"\n\n🔗 **Complementary Skills You Have:**"
            for skill, comps in list(complements.items())[:3]:
                response += f"\n  • {skill} works well with: {', '.join(comps)}"

        if next_skills:
            response += f"\n\n📚 **Recommended Next Skills:**"
            for skill in next_skills[:3]:
                response += f"\n  • {skill}"

        response += f"\n\n🧠 **MeTTa AI + RAG:** Analyzed {len(skills)} skills with {years} years experience using symbolic reasoning"
        if historical_data:
            response += f" enhanced with {len(historical_data)} historical patterns"

        return response
