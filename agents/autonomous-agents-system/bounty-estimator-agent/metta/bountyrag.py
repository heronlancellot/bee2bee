# bountyrag.py - Bounty Estimation RAG System with MeTTa
from hyperon import MeTTa, E, S, ValueAtom
from typing import List, Dict, Tuple

class BountyRAG:
    def __init__(self, metta_instance: MeTTa):
        self.metta = metta_instance

    def get_complexity_level(self, score: int) -> str:
        """Get complexity level using MeTTa reasoning."""
        try:
            query_str = f'!(match &self (complexity-level {score} $level) $level)'
            results = self.metta.run(query_str)

            if results and len(results) > 0 and results[0]:
                return results[0][0].get_object().value

            # Fallback
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
        except Exception as e:
            print(f"Error getting complexity level: {e}")
            return "moderate"

    def get_base_rate(self, complexity_level: str) -> int:
        """Get base rate for complexity level using MeTTa."""
        try:
            query_str = f'!(match &self (base-rate {complexity_level} $rate) $rate)'
            results = self.metta.run(query_str)

            if results and len(results) > 0 and results[0]:
                return results[0][0].get_object().value

            # Fallback
            rates = {"trivial": 25, "easy": 50, "moderate": 100, "hard": 200, "very-hard": 400}
            return rates.get(complexity_level, 100)
        except Exception as e:
            print(f"Error getting base rate: {e}")
            return 100

    def get_premium_multiplier(self, skills: List[str]) -> Tuple[float, List[str]]:
        """Get premium skill multiplier using MeTTa."""
        max_multiplier = 1.0
        premium_skills_found = []

        for skill in skills:
            try:
                query_str = f'!(match &self (premium-skill {skill} $multiplier) $multiplier)'
                results = self.metta.run(query_str)

                if results and len(results) > 0 and results[0]:
                    multiplier = results[0][0].get_object().value
                    if multiplier > max_multiplier:
                        max_multiplier = multiplier
                    premium_skills_found.append(skill)
            except Exception as e:
                print(f"Error checking premium skill {skill}: {e}")

        return max_multiplier, premium_skills_found

    def get_repo_multiplier(self, stars: int) -> float:
        """Get repository multiplier based on stars using MeTTa."""
        try:
            # Find closest match
            thresholds = [100, 500, 1000, 5000, 10000, 50000]
            closest = min(thresholds, key=lambda x: abs(x - stars) if x <= stars else float('inf'))

            query_str = f'!(match &self (repo-multiplier {closest} $multiplier) $multiplier)'
            results = self.metta.run(query_str)

            if results and len(results) > 0 and results[0]:
                return results[0][0].get_object().value

            # Fallback logic
            if stars < 500:
                return 1.0
            elif stars < 1000:
                return 1.1
            elif stars < 5000:
                return 1.2
            elif stars < 10000:
                return 1.3
            else:
                return 1.5
        except Exception as e:
            print(f"Error getting repo multiplier: {e}")
            return 1.0

    def get_bounty_tier(self, value: int) -> str:
        """Get bounty tier using MeTTa."""
        try:
            # Find appropriate tier
            if value >= 5000:
                tier_value = 5000
            elif value >= 1000:
                tier_value = 1000
            elif value >= 500:
                tier_value = 500
            elif value >= 200:
                tier_value = 200
            elif value >= 50:
                tier_value = 50
            else:
                tier_value = 25

            query_str = f'!(match &self (bounty-tier {tier_value} $tier) $tier)'
            results = self.metta.run(query_str)

            if results and len(results) > 0 and results[0]:
                return results[0][0].get_object().value

            return "Medium"
        except Exception as e:
            print(f"Error getting bounty tier: {e}")
            return "Medium"

    def assess_fair_rate(self, hourly_rate: float) -> Tuple[str, str]:
        """Assess if hourly rate is fair using MeTTa."""
        if hourly_rate >= 100:
            level = "expert"
            assessment = "EXCELLENT"
        elif hourly_rate >= 50:
            level = "senior"
            assessment = "VERY GOOD"
        elif hourly_rate >= 25:
            level = "mid"
            assessment = "GOOD"
        elif hourly_rate >= 15:
            level = "junior"
            assessment = "FAIR"
        else:
            level = "below market"
            assessment = "LOW"

        return level, assessment

    def calculate_intelligent_estimate(self, complexity_score: int, skills: List[str],
                                      hours: int, repo_stars: int) -> Dict:
        """Calculate bounty estimate using MeTTa reasoning."""

        # Get complexity level
        complexity_level = self.get_complexity_level(complexity_score)

        # Get base rate
        base_rate = self.get_base_rate(complexity_level)

        # Get premium multiplier
        premium_mult, premium_skills = self.get_premium_multiplier(skills)

        # Get repo multiplier
        repo_mult = self.get_repo_multiplier(repo_stars)

        # Calculate final value
        estimated_value = int(base_rate * premium_mult * repo_mult)
        min_value = int(estimated_value * 0.8)
        max_value = int(estimated_value * 1.3)

        # Calculate hourly rate
        hourly_rate = estimated_value / hours if hours > 0 else 0

        # Get tier
        tier = self.get_bounty_tier(estimated_value)

        # Assess fairness
        rate_level, assessment = self.assess_fair_rate(hourly_rate)

        return {
            "complexity_level": complexity_level,
            "base_rate": base_rate,
            "premium_multiplier": premium_mult,
            "premium_skills": premium_skills,
            "repo_multiplier": repo_mult,
            "estimated_value": estimated_value,
            "min_value": min_value,
            "max_value": max_value,
            "hourly_rate": hourly_rate,
            "tier": tier,
            "rate_level": rate_level,
            "assessment": assessment
        }

    def generate_intelligent_response(self, complexity_score: int, skills: List[str],
                                     hours: int, repo_stars: int, historical_data: List[Dict] = None) -> str:
        """
        Generate intelligent bounty estimation using MeTTa reasoning + RAG historical data.

        Args:
            complexity_score: Complexity rating 1-10
            skills: Required skills for bounty
            hours: Estimated hours
            repo_stars: Repository star count
            historical_data: Retrieved similar estimates from Supabase RAG (optional)
        """

        estimate = self.calculate_intelligent_estimate(complexity_score, skills, hours, repo_stars)

        response = f"""💰 **Intelligent Bounty Estimation**

**Complexity:** {estimate['complexity_level'].title()} ({complexity_score}/10)
**Estimated Time:** ~{hours} hours
**Repository:** {repo_stars} stars

**Estimated Value:** ${estimate['min_value']} - ${estimate['max_value']}
**Recommended:** ${estimate['estimated_value']}
**Hourly Rate:** ~${estimate['hourly_rate']:.2f}/hour"""

        # 🔥 RAG AUGMENTATION: Add insights from historical data
        if historical_data and len(historical_data) > 0:
            response += f"\n\n📊 **RAG Insights:** Found {len(historical_data)} similar estimates in knowledge base"

            # Extract average hourly rate from historical data
            historical_rates = []
            for hist_estimate in historical_data:
                content = hist_estimate.get('content', '')
                # Simple parsing to extract hourly rate
                import re
                rate_match = re.search(r'Hourly Rate: \$(\d+\.?\d*)/hour', content)
                if rate_match:
                    historical_rates.append(float(rate_match.group(1)))

            if historical_rates:
                avg_historical_rate = sum(historical_rates) / len(historical_rates)
                response += f"\n  • Historical average for similar bounties: ${avg_historical_rate:.2f}/hour"
                rate_diff = estimate['hourly_rate'] - avg_historical_rate
                if rate_diff > 5:
                    response += f"\n  • 📈 This estimate is ${rate_diff:.2f}/hour ABOVE historical average!"
                elif rate_diff < -5:
                    response += f"\n  • 📉 This estimate is ${abs(rate_diff):.2f}/hour BELOW historical average"
                else:
                    response += f"\n  • ✅ This estimate aligns with historical patterns"

        response += f"""

**AI Analysis:**
• Base Rate (complexity): ${estimate['base_rate']}
• Premium Skills Multiplier: {estimate['premium_multiplier']}x"""

        if estimate['premium_skills']:
            response += f" ({', '.join(estimate['premium_skills'])})"

        response += f"""
• Repository Multiplier: {estimate['repo_multiplier']}x
• Tier: {estimate['tier']}

💡 **AI Recommendation:** """

        if estimate['assessment'] == "EXCELLENT":
            response += f"EXCELLENT value at ${estimate['hourly_rate']:.2f}/hour! Well above market rates."
        elif estimate['assessment'] == "VERY GOOD":
            response += f"VERY GOOD value at ${estimate['hourly_rate']:.2f}/hour! Senior-level rate."
        elif estimate['assessment'] == "GOOD":
            response += f"GOOD value at ${estimate['hourly_rate']:.2f}/hour! Fair mid-level rate."
        elif estimate['assessment'] == "FAIR":
            response += f"FAIR value at ${estimate['hourly_rate']:.2f}/hour! Junior-level rate."
        else:
            response += f"Consider negotiating - ${estimate['hourly_rate']:.2f}/hour is below market standards."

        response += f"\n\n🧠 **MeTTa AI + RAG:** Analyzed {len(skills)} skills, complexity {complexity_score}/10, {repo_stars} stars using symbolic AI"
        if historical_data:
            response += f" enhanced with {len(historical_data)} historical estimates"

        return response
