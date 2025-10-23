"""
Bounty Estimator Agent
Estimates bounty values and project costs
"""

import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime


class BountyEstimator:
    """
    Agent specialized in bounty estimation
    
    Capabilities:
    - Estimate bounty values
    - Calculate project costs
    - Analyze complexity factors
    - Provide pricing recommendations
    """
    
    def __init__(self):
        self.agent_id = "bounty_estimator"
        self.capabilities = [
            "Bounty value estimation",
            "Project cost calculation",
            "Complexity analysis",
            "Pricing recommendations",
            "Time estimation"
        ]
        
        # Base rates by skill level and technology
        self.base_rates = {
            "beginner": {"hourly": 25, "daily": 200},
            "intermediate": {"hourly": 50, "daily": 400},
            "advanced": {"hourly": 100, "daily": 800},
            "expert": {"hourly": 150, "daily": 1200}
        }
        
        # Technology multipliers
        self.tech_multipliers = {
            "ai_ml": 1.5,
            "blockchain": 1.4,
            "mobile": 1.2,
            "web": 1.0,
            "devops": 1.3,
            "data_science": 1.4
        }
        
        # Complexity factors
        self.complexity_factors = {
            "simple": 1.0,
            "moderate": 1.5,
            "complex": 2.0,
            "very_complex": 3.0
        }
    
    def process(self, query: str, user_id: str = None, context: Dict = None,
               conversation_history: List[Dict] = None) -> Dict:
        """
        Process bounty estimation query
        
        Args:
            query: User query about bounty estimation
            user_id: User identifier
            context: Additional context (may include project_details, skills_required)
            conversation_history: Previous conversation messages
            
        Returns:
            Dict with estimation results
        """
        
        # Extract project details from query
        project_details = self._extract_project_details(query, context)
        
        if not project_details:
            return {
                "response": "I need more details about the project to estimate the bounty. Please provide:\n" +
                           "- Project description\n" +
                           "- Required skills/technologies\n" +
                           "- Estimated complexity\n" +
                           "- Timeline requirements",
                "agent_id": self.agent_id,
                "metadata": {"error": "insufficient_details"}
            }
        
        try:
            # Perform bounty estimation
            estimation = self._estimate_bounty(project_details)
            
            # Generate response
            response = self._format_estimation_response(estimation, project_details)
            
            return {
                "response": response,
                "agent_id": self.agent_id,
                "metadata": {
                    "project_details": project_details,
                    "estimation": estimation,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "response": f"I encountered an error estimating the bounty: {str(e)}",
                "agent_id": self.agent_id,
                "metadata": {"error": str(e)}
            }
    
    def _extract_project_details(self, query: str, context: Dict = None) -> Dict:
        """Extract project details from query or context"""
        
        # Check context first
        if context and "project_details" in context:
            return context["project_details"]
        
        details = {}
        
        # Extract technologies/skills
        technologies = self._extract_technologies(query)
        if technologies:
            details["technologies"] = technologies
        
        # Extract complexity indicators
        complexity = self._extract_complexity(query)
        if complexity:
            details["complexity"] = complexity
        
        # Extract timeline
        timeline = self._extract_timeline(query)
        if timeline:
            details["timeline"] = timeline
        
        # Extract project type
        project_type = self._extract_project_type(query)
        if project_type:
            details["project_type"] = project_type
        
        # Extract specific requirements
        requirements = self._extract_requirements(query)
        if requirements:
            details["requirements"] = requirements
        
        return details
    
    def _extract_technologies(self, query: str) -> List[str]:
        """Extract technologies from query"""
        
        tech_keywords = {
            "ai_ml": ["ai", "machine learning", "ml", "tensorflow", "pytorch", "neural", "deep learning"],
            "blockchain": ["blockchain", "crypto", "ethereum", "solidity", "web3", "defi"],
            "mobile": ["mobile", "ios", "android", "react native", "flutter", "swift", "kotlin"],
            "web": ["web", "frontend", "backend", "react", "vue", "angular", "node", "django"],
            "devops": ["devops", "docker", "kubernetes", "aws", "azure", "ci/cd"],
            "data_science": ["data", "analytics", "pandas", "numpy", "sql", "database"]
        }
        
        found_techs = []
        query_lower = query.lower()
        
        for tech_type, keywords in tech_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    found_techs.append(tech_type)
                    break
        
        return list(set(found_techs))
    
    def _extract_complexity(self, query: str) -> str:
        """Extract complexity level from query"""
        
        complexity_indicators = {
            "simple": ["simple", "basic", "easy", "straightforward", "quick"],
            "moderate": ["moderate", "medium", "standard", "typical"],
            "complex": ["complex", "difficult", "challenging", "advanced", "sophisticated"],
            "very_complex": ["very complex", "extremely difficult", "highly complex", "enterprise"]
        }
        
        query_lower = query.lower()
        
        for complexity, indicators in complexity_indicators.items():
            for indicator in indicators:
                if indicator in query_lower:
                    return complexity
        
        return "moderate"  # Default
    
    def _extract_timeline(self, query: str) -> Dict:
        """Extract timeline information from query"""
        
        # Look for time patterns
        time_patterns = [
            r"(\d+)\s*(hours?|hrs?)",
            r"(\d+)\s*(days?|d)",
            r"(\d+)\s*(weeks?|wks?)",
            r"(\d+)\s*(months?|mos?)",
            r"urgent|asap|immediately|quickly"
        ]
        
        timeline = {}
        
        for pattern in time_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                if "urgent" in pattern or "asap" in pattern:
                    timeline["urgency"] = "high"
                else:
                    number = int(match.group(1))
                    unit = match.group(2).lower()
                    
                    if unit in ["hour", "hours", "hr", "hrs"]:
                        timeline["hours"] = number
                    elif unit in ["day", "days", "d"]:
                        timeline["days"] = number
                    elif unit in ["week", "weeks", "wk", "wks"]:
                        timeline["weeks"] = number
                    elif unit in ["month", "months", "mo", "mos"]:
                        timeline["months"] = number
        
        return timeline
    
    def _extract_project_type(self, query: str) -> str:
        """Extract project type from query"""
        
        project_types = {
            "bug_fix": ["bug", "fix", "debug", "error", "issue"],
            "feature": ["feature", "new functionality", "add", "implement"],
            "integration": ["integrate", "connect", "api", "webhook"],
            "optimization": ["optimize", "performance", "speed", "efficiency"],
            "migration": ["migrate", "upgrade", "convert", "port"],
            "new_project": ["new project", "from scratch", "build", "create"]
        }
        
        query_lower = query.lower()
        
        for project_type, keywords in project_types.items():
            for keyword in keywords:
                if keyword in query_lower:
                    return project_type
        
        return "feature"  # Default
    
    def _extract_requirements(self, query: str) -> List[str]:
        """Extract specific requirements from query"""
        
        requirements = []
        
        # Common requirement patterns
        req_patterns = [
            r"must have",
            r"required",
            r"need to",
            r"should include",
            r"must include"
        ]
        
        for pattern in req_patterns:
            matches = re.findall(pattern + r".*?([^.]+)", query, re.IGNORECASE)
            for match in matches:
                requirements.append(match.strip())
        
        return requirements
    
    def _estimate_bounty(self, project_details: Dict) -> Dict:
        """Perform bounty estimation"""
        
        # Base estimation
        base_hours = self._estimate_base_hours(project_details)
        
        # Apply multipliers
        tech_multiplier = self._get_tech_multiplier(project_details.get("technologies", []))
        complexity_multiplier = self._get_complexity_multiplier(project_details.get("complexity", "moderate"))
        
        # Calculate adjusted hours
        adjusted_hours = base_hours * tech_multiplier * complexity_multiplier
        
        # Calculate costs by skill level
        costs_by_level = {}
        for level, rates in self.base_rates.items():
            hourly_cost = adjusted_hours * rates["hourly"]
            daily_cost = (adjusted_hours / 8) * rates["daily"]
            
            costs_by_level[level] = {
                "hours": adjusted_hours,
                "hourly_rate": rates["hourly"],
                "total_cost": hourly_cost,
                "daily_rate": rates["daily"],
                "daily_cost": daily_cost
            }
        
        # Generate recommendations
        recommendations = self._generate_pricing_recommendations(
            project_details, adjusted_hours, costs_by_level
        )
        
        return {
            "base_hours": base_hours,
            "adjusted_hours": adjusted_hours,
            "tech_multiplier": tech_multiplier,
            "complexity_multiplier": complexity_multiplier,
            "costs_by_level": costs_by_level,
            "recommendations": recommendations,
            "timeline": project_details.get("timeline", {})
        }
    
    def _estimate_base_hours(self, project_details: Dict) -> float:
        """Estimate base hours for project"""
        
        project_type = project_details.get("project_type", "feature")
        complexity = project_details.get("complexity", "moderate")
        
        # Base hours by project type
        base_hours_by_type = {
            "bug_fix": 8,
            "feature": 40,
            "integration": 24,
            "optimization": 32,
            "migration": 80,
            "new_project": 160
        }
        
        base_hours = base_hours_by_type.get(project_type, 40)
        
        # Adjust for complexity
        complexity_adjustments = {
            "simple": 0.5,
            "moderate": 1.0,
            "complex": 1.5,
            "very_complex": 2.0
        }
        
        adjustment = complexity_adjustments.get(complexity, 1.0)
        return base_hours * adjustment
    
    def _get_tech_multiplier(self, technologies: List[str]) -> float:
        """Get technology multiplier"""
        
        if not technologies:
            return 1.0
        
        # Use highest multiplier among technologies
        max_multiplier = 1.0
        for tech in technologies:
            multiplier = self.tech_multipliers.get(tech, 1.0)
            max_multiplier = max(max_multiplier, multiplier)
        
        return max_multiplier
    
    def _get_complexity_multiplier(self, complexity: str) -> float:
        """Get complexity multiplier"""
        return self.complexity_factors.get(complexity, 1.5)
    
    def _generate_pricing_recommendations(self, project_details: Dict, 
                                         adjusted_hours: float, 
                                         costs_by_level: Dict) -> List[str]:
        """Generate pricing recommendations"""
        
        recommendations = []
        
        # Timeline recommendations
        timeline = project_details.get("timeline", {})
        if timeline.get("urgency") == "high":
            recommendations.append("⚡ **Urgent project** - Consider premium pricing (+20-30%)")
        
        # Technology recommendations
        technologies = project_details.get("technologies", [])
        if "ai_ml" in technologies:
            recommendations.append("🤖 **AI/ML project** - Requires specialized expertise, premium rates recommended")
        if "blockchain" in technologies:
            recommendations.append("⛓️ **Blockchain project** - High demand, consider premium pricing")
        
        # Complexity recommendations
        complexity = project_details.get("complexity", "moderate")
        if complexity in ["complex", "very_complex"]:
            recommendations.append("🔧 **Complex project** - Consider breaking into phases or milestone-based pricing")
        
        # Skill level recommendations
        intermediate_cost = costs_by_level["intermediate"]["total_cost"]
        expert_cost = costs_by_level["expert"]["total_cost"]
        
        if expert_cost > intermediate_cost * 2:
            recommendations.append("💡 **Consider intermediate developer** - Significant cost savings with good quality")
        
        # Timeline recommendations
        if adjusted_hours > 160:  # More than 4 weeks
            recommendations.append("📅 **Long project** - Consider milestone-based payments")
        
        return recommendations
    
    def _format_estimation_response(self, estimation: Dict, project_details: Dict) -> str:
        """Format estimation results into readable response"""
        
        adjusted_hours = estimation["adjusted_hours"]
        costs_by_level = estimation["costs_by_level"]
        recommendations = estimation["recommendations"]
        
        response = f"## 💰 Bounty Estimation\n\n"
        
        # Project summary
        response += f"**Estimated Hours:** {adjusted_hours:.1f} hours\n"
        response += f"**Complexity:** {project_details.get('complexity', 'moderate').title()}\n"
        response += f"**Project Type:** {project_details.get('project_type', 'feature').replace('_', ' ').title()}\n\n"
        
        # Technology multipliers
        if estimation["tech_multiplier"] > 1.0:
            response += f"**Technology Multiplier:** {estimation['tech_multiplier']:.1f}x\n"
        if estimation["complexity_multiplier"] > 1.0:
            response += f"**Complexity Multiplier:** {estimation['complexity_multiplier']:.1f}x\n"
        response += "\n"
        
        # Cost breakdown
        response += "**Cost Breakdown by Skill Level:**\n"
        for level, costs in costs_by_level.items():
            response += f"- **{level.title()}:** ${costs['total_cost']:,.0f} "
            response += f"(${costs['hourly_rate']}/hr × {costs['hours']:.1f}hrs)\n"
        response += "\n"
        
        # Recommendations
        if recommendations:
            response += "**Recommendations:**\n"
            for rec in recommendations:
                response += f"{rec}\n"
        
        return response
    
    def get_description(self) -> str:
        """Get agent description"""
        return "Estimates bounty values and project costs based on complexity and technology requirements"
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return self.capabilities
