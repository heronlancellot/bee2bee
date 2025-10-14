"""
Skill Matcher Agent
Matches developers with required skills and project needs
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime


class SkillMatcher:
    """
    Agent specialized in skill matching
    
    Capabilities:
    - Match developers with required skills
    - Analyze skill gaps
    - Recommend skill development
    - Evaluate skill compatibility
    """
    
    def __init__(self):
        self.agent_id = "skill_matcher"
        self.capabilities = [
            "Developer skill matching",
            "Skill gap analysis",
            "Skill development recommendations",
            "Compatibility assessment",
            "Team composition analysis"
        ]
        
        # Common skill categories
        self.skill_categories = {
            "programming_languages": [
                "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust",
                "PHP", "Ruby", "Swift", "Kotlin", "Scala", "R", "MATLAB"
            ],
            "frameworks": [
                "React", "Vue.js", "Angular", "Django", "Flask", "Express.js", "Spring",
                "Laravel", "Rails", "FastAPI", "Next.js", "Nuxt.js", "Svelte"
            ],
            "databases": [
                "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch", "SQLite",
                "Cassandra", "DynamoDB", "Neo4j", "InfluxDB"
            ],
            "cloud_platforms": [
                "AWS", "Azure", "Google Cloud", "DigitalOcean", "Heroku", "Vercel",
                "Netlify", "Railway", "Supabase", "Firebase"
            ],
            "devops": [
                "Docker", "Kubernetes", "Jenkins", "GitLab CI", "GitHub Actions",
                "Terraform", "Ansible", "Prometheus", "Grafana"
            ],
            "mobile": [
                "React Native", "Flutter", "Ionic", "Xamarin", "Cordova", "NativeScript"
            ],
            "ai_ml": [
                "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "OpenCV",
                "Hugging Face", "LangChain", "Pinecone", "Weaviate"
            ]
        }
    
    def process(self, query: str, user_id: str = None, context: Dict = None,
               conversation_history: List[Dict] = None) -> Dict:
        """
        Process skill matching query
        
        Args:
            query: User query about skill matching
            user_id: User identifier
            context: Additional context (may include required_skills, user_skills)
            conversation_history: Previous conversation messages
            
        Returns:
            Dict with matching results
        """
        
        # Extract skills from query or context
        required_skills = self._extract_required_skills(query, context)
        user_skills = self._extract_user_skills(query, context, user_id)
        
        if not required_skills:
            return {
                "response": "I need to know what skills you're looking for. Please specify the required skills or technologies.",
                "agent_id": self.agent_id,
                "metadata": {"error": "no_required_skills"}
            }
        
        try:
            # Perform skill matching
            match_result = self._match_skills(required_skills, user_skills)
            
            # Generate response
            response = self._format_match_response(match_result, required_skills, user_skills)
            
            return {
                "response": response,
                "agent_id": self.agent_id,
                "metadata": {
                    "required_skills": required_skills,
                    "user_skills": user_skills,
                    "match_result": match_result,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "response": f"I encountered an error matching skills: {str(e)}",
                "agent_id": self.agent_id,
                "metadata": {"error": str(e)}
            }
    
    def _extract_required_skills(self, query: str, context: Dict = None) -> List[str]:
        """Extract required skills from query or context"""
        
        # Check context first
        if context and "required_skills" in context:
            return context["required_skills"]
        
        # Extract skills from query text
        query_lower = query.lower()
        found_skills = []
        
        # Check each skill category
        for category, skills in self.skill_categories.items():
            for skill in skills:
                if skill.lower() in query_lower:
                    found_skills.append(skill)
        
        # Also look for common patterns
        import re
        
        # Look for "need", "require", "looking for" patterns
        patterns = [
            r"need.*?([A-Za-z\s]+)",
            r"require.*?([A-Za-z\s]+)",
            r"looking for.*?([A-Za-z\s]+)",
            r"skills.*?([A-Za-z\s]+)"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                # Split by common delimiters
                skills = re.split(r'[,;|&]', match.strip())
                for skill in skills:
                    skill = skill.strip()
                    if len(skill) > 2 and skill.title() in [s.title() for s in self._get_all_skills()]:
                        found_skills.append(skill.title())
        
        return list(set(found_skills))  # Remove duplicates
    
    def _extract_user_skills(self, query: str, context: Dict = None, user_id: str = None) -> List[str]:
        """Extract user skills from query or context"""
        
        # Check context first
        if context and "user_skills" in context:
            return context["user_skills"]
        
        # For now, return empty list - in real implementation, 
        # this would fetch from user profile database
        return []
    
    def _get_all_skills(self) -> List[str]:
        """Get all available skills"""
        all_skills = []
        for skills in self.skill_categories.values():
            all_skills.extend(skills)
        return all_skills
    
    def _match_skills(self, required_skills: List[str], user_skills: List[str]) -> Dict:
        """Perform skill matching analysis"""
        
        # Normalize skill names
        required_normalized = [self._normalize_skill(skill) for skill in required_skills]
        user_normalized = [self._normalize_skill(skill) for skill in user_skills]
        
        # Find matches
        exact_matches = []
        partial_matches = []
        missing_skills = []
        
        for req_skill in required_normalized:
            found_match = False
            
            # Check for exact matches
            for user_skill in user_normalized:
                if req_skill.lower() == user_skill.lower():
                    exact_matches.append(req_skill)
                    found_match = True
                    break
            
            if not found_match:
                # Check for partial matches (same category)
                req_category = self._get_skill_category(req_skill)
                if req_category:
                    for user_skill in user_normalized:
                        user_category = self._get_skill_category(user_skill)
                        if req_category == user_category:
                            partial_matches.append({
                                "required": req_skill,
                                "user_has": user_skill,
                                "category": req_category
                            })
                            found_match = True
                            break
            
            if not found_match:
                missing_skills.append(req_skill)
        
        # Calculate match score
        total_required = len(required_normalized)
        exact_score = len(exact_matches) / total_required if total_required > 0 else 0
        partial_score = len(partial_matches) * 0.5 / total_required if total_required > 0 else 0
        overall_score = (exact_score + partial_score) * 100
        
        # Generate recommendations
        recommendations = self._generate_skill_recommendations(
            exact_matches, partial_matches, missing_skills
        )
        
        return {
            "exact_matches": exact_matches,
            "partial_matches": partial_matches,
            "missing_skills": missing_skills,
            "match_score": overall_score,
            "recommendations": recommendations,
            "total_required": total_required,
            "total_user": len(user_normalized)
        }
    
    def _normalize_skill(self, skill: str) -> str:
        """Normalize skill name"""
        return skill.strip().title()
    
    def _get_skill_category(self, skill: str) -> Optional[str]:
        """Get category for a skill"""
        for category, skills in self.skill_categories.items():
            if skill in skills:
                return category
        return None
    
    def _generate_skill_recommendations(self, exact_matches: List[str], 
                                      partial_matches: List[Dict], 
                                      missing_skills: List[str]) -> List[str]:
        """Generate skill development recommendations"""
        
        recommendations = []
        
        # Exact matches
        if exact_matches:
            recommendations.append(f"✅ You have exact matches for: {', '.join(exact_matches)}")
        
        # Partial matches
        if partial_matches:
            for match in partial_matches:
                recommendations.append(
                    f"🔄 You have {match['user_has']} experience, which is related to required {match['required']} "
                    f"(both in {match['category']} category)"
                )
        
        # Missing skills
        if missing_skills:
            recommendations.append(f"❌ You need to learn: {', '.join(missing_skills)}")
            
            # Suggest learning resources
            for skill in missing_skills[:3]:  # Top 3 missing skills
                category = self._get_skill_category(skill)
                if category:
                    recommendations.append(f"📚 For {skill}: Consider online courses, documentation, or tutorials")
        
        # Overall recommendation
        total_missing = len(missing_skills)
        if total_missing == 0:
            recommendations.append("🎉 Perfect match! You have all required skills.")
        elif total_missing <= 2:
            recommendations.append("👍 Good match! You're missing only a few skills.")
        else:
            recommendations.append("📈 Consider focusing on the most critical missing skills first.")
        
        return recommendations
    
    def _format_match_response(self, match_result: Dict, required_skills: List[str], 
                              user_skills: List[str]) -> str:
        """Format matching results into readable response"""
        
        exact_matches = match_result["exact_matches"]
        partial_matches = match_result["partial_matches"]
        missing_skills = match_result["missing_skills"]
        match_score = match_result["match_score"]
        recommendations = match_result["recommendations"]
        
        response = f"## 🎯 Skill Matching Analysis\n\n"
        
        # Match score
        score_emoji = "🟢" if match_score >= 80 else "🟡" if match_score >= 60 else "🔴"
        response += f"**Match Score:** {score_emoji} {match_score:.1f}%\n\n"
        
        # Required skills
        response += f"**Required Skills:** {', '.join(required_skills)}\n"
        response += f"**Your Skills:** {', '.join(user_skills) if user_skills else 'Not specified'}\n\n"
        
        # Matches breakdown
        response += "**Match Breakdown:**\n"
        
        if exact_matches:
            response += f"✅ **Exact Matches ({len(exact_matches)}):** {', '.join(exact_matches)}\n"
        
        if partial_matches:
            response += f"🔄 **Related Skills ({len(partial_matches)}):**\n"
            for match in partial_matches:
                response += f"   - You have {match['user_has']} (related to {match['required']})\n"
        
        if missing_skills:
            response += f"❌ **Missing Skills ({len(missing_skills)}):** {', '.join(missing_skills)}\n"
        
        response += "\n"
        
        # Recommendations
        response += "**Recommendations:**\n"
        for rec in recommendations:
            response += f"{rec}\n"
        
        return response
    
    def get_description(self) -> str:
        """Get agent description"""
        return "Matches developers with required skills and provides skill gap analysis"
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return self.capabilities
