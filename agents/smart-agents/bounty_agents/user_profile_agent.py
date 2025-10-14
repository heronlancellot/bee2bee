"""
User Profile Agent
Manages user profiles and preferences
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime


class UserProfileAgent:
    """
    Agent specialized in user profile management
    
    Capabilities:
    - Manage user profiles
    - Update preferences
    - Track skills and experience
    - Provide profile insights
    """
    
    def __init__(self):
        self.agent_id = "user_profile_agent"
        self.capabilities = [
            "Profile management",
            "Skill tracking",
            "Preference updates",
            "Profile insights",
            "Experience analysis"
        ]
    
    def process(self, query: str, user_id: str = None, context: Dict = None,
               conversation_history: List[Dict] = None) -> Dict:
        """
        Process user profile query
        
        Args:
            query: User query about profile management
            user_id: User identifier
            context: Additional context (may include profile_data)
            conversation_history: Previous conversation messages
            
        Returns:
            Dict with profile management results
        """
        
        # Determine action type
        action = self._determine_action(query)
        
        if not user_id:
            return {
                "response": "I need your user ID to manage your profile. Please provide your user identifier.",
                "agent_id": self.agent_id,
                "metadata": {"error": "no_user_id"}
            }
        
        try:
            # Process the action
            if action == "view_profile":
                result = self._view_profile(user_id, context)
            elif action == "update_skills":
                result = self._update_skills(query, user_id, context)
            elif action == "update_preferences":
                result = self._update_preferences(query, user_id, context)
            elif action == "get_insights":
                result = self._get_profile_insights(user_id, context)
            else:
                result = self._handle_unknown_action(query)
            
            # Generate response
            response = self._format_profile_response(result, action)
            
            return {
                "response": response,
                "agent_id": self.agent_id,
                "metadata": {
                    "action": action,
                    "user_id": user_id,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "response": f"I encountered an error managing your profile: {str(e)}",
                "agent_id": self.agent_id,
                "metadata": {"error": str(e)}
            }
    
    def _determine_action(self, query: str) -> str:
        """Determine what action the user wants to perform"""
        
        query_lower = query.lower()
        
        # Action patterns
        if any(word in query_lower for word in ["view", "show", "see", "my profile", "profile"]):
            return "view_profile"
        elif any(word in query_lower for word in ["update", "add", "remove", "change", "skills"]):
            return "update_skills"
        elif any(word in query_lower for word in ["preferences", "settings", "configure"]):
            return "update_preferences"
        elif any(word in query_lower for word in ["insights", "analysis", "stats", "summary"]):
            return "get_insights"
        else:
            return "view_profile"  # Default action
    
    def _view_profile(self, user_id: str, context: Dict = None) -> Dict:
        """View user profile"""
        
        # In real implementation, this would fetch from database
        # For now, return mock data or data from context
        profile_data = context.get("profile_data") if context else None
        
        if not profile_data:
            # Mock profile data
            profile_data = {
                "user_id": user_id,
                "github_username": "user123",
                "skills": ["Python", "JavaScript", "React"],
                "preferences": {
                    "min_bounty": 100,
                    "max_hours_per_week": 20,
                    "preferred_languages": ["Python", "JavaScript"]
                },
                "completed_bounties": 5,
                "total_earned": 2500,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": datetime.now().isoformat()
            }
        
        return {
            "action": "view_profile",
            "profile": profile_data,
            "status": "success"
        }
    
    def _update_skills(self, query: str, user_id: str, context: Dict = None) -> Dict:
        """Update user skills"""
        
        # Extract skills from query
        skills_to_add = self._extract_skills_to_add(query)
        skills_to_remove = self._extract_skills_to_remove(query)
        
        # Get current profile
        profile_result = self._view_profile(user_id, context)
        current_profile = profile_result["profile"]
        current_skills = current_profile.get("skills", [])
        
        # Update skills
        updated_skills = current_skills.copy()
        
        # Add new skills
        for skill in skills_to_add:
            if skill not in updated_skills:
                updated_skills.append(skill)
        
        # Remove skills
        for skill in skills_to_remove:
            if skill in updated_skills:
                updated_skills.remove(skill)
        
        # Update profile
        updated_profile = current_profile.copy()
        updated_profile["skills"] = updated_skills
        updated_profile["updated_at"] = datetime.now().isoformat()
        
        return {
            "action": "update_skills",
            "profile": updated_profile,
            "changes": {
                "added": skills_to_add,
                "removed": skills_to_remove,
                "total_skills": len(updated_skills)
            },
            "status": "success"
        }
    
    def _update_preferences(self, query: str, user_id: str, context: Dict = None) -> Dict:
        """Update user preferences"""
        
        # Extract preferences from query
        preferences = self._extract_preferences(query)
        
        # Get current profile
        profile_result = self._view_profile(user_id, context)
        current_profile = profile_result["profile"]
        current_preferences = current_profile.get("preferences", {})
        
        # Update preferences
        updated_preferences = current_preferences.copy()
        updated_preferences.update(preferences)
        
        # Update profile
        updated_profile = current_profile.copy()
        updated_profile["preferences"] = updated_preferences
        updated_profile["updated_at"] = datetime.now().isoformat()
        
        return {
            "action": "update_preferences",
            "profile": updated_profile,
            "changes": preferences,
            "status": "success"
        }
    
    def _get_profile_insights(self, user_id: str, context: Dict = None) -> Dict:
        """Get profile insights and analysis"""
        
        # Get current profile
        profile_result = self._view_profile(user_id, context)
        profile = profile_result["profile"]
        
        # Generate insights
        insights = {
            "skill_diversity": self._analyze_skill_diversity(profile.get("skills", [])),
            "experience_level": self._assess_experience_level(profile),
            "earning_potential": self._calculate_earning_potential(profile),
            "recommendations": self._generate_profile_recommendations(profile)
        }
        
        return {
            "action": "get_insights",
            "insights": insights,
            "profile": profile,
            "status": "success"
        }
    
    def _extract_skills_to_add(self, query: str) -> List[str]:
        """Extract skills to add from query"""
        
        # Common skill patterns
        add_patterns = [
            r"add\s+([A-Za-z\s,]+)",
            r"learn\s+([A-Za-z\s,]+)",
            r"include\s+([A-Za-z\s,]+)",
            r"new skill[s]?\s+([A-Za-z\s,]+)"
        ]
        
        skills = []
        
        for pattern in add_patterns:
            import re
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                # Split by common delimiters
                skill_list = re.split(r'[,;|&]', match.strip())
                for skill in skill_list:
                    skill = skill.strip()
                    if len(skill) > 1:
                        skills.append(skill.title())
        
        return list(set(skills))  # Remove duplicates
    
    def _extract_skills_to_remove(self, query: str) -> List[str]:
        """Extract skills to remove from query"""
        
        remove_patterns = [
            r"remove\s+([A-Za-z\s,]+)",
            r"delete\s+([A-Za-z\s,]+)",
            r"no longer\s+([A-Za-z\s,]+)",
            r"stop using\s+([A-Za-z\s,]+)"
        ]
        
        skills = []
        
        for pattern in remove_patterns:
            import re
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                skill_list = re.split(r'[,;|&]', match.strip())
                for skill in skill_list:
                    skill = skill.strip()
                    if len(skill) > 1:
                        skills.append(skill.title())
        
        return list(set(skills))
    
    def _extract_preferences(self, query: str) -> Dict:
        """Extract preferences from query"""
        
        preferences = {}
        
        # Extract min bounty
        import re
        min_bounty_match = re.search(r"min.*?bounty.*?(\d+)", query, re.IGNORECASE)
        if min_bounty_match:
            preferences["min_bounty"] = int(min_bounty_match.group(1))
        
        # Extract max hours
        max_hours_match = re.search(r"max.*?hours.*?(\d+)", query, re.IGNORECASE)
        if max_hours_match:
            preferences["max_hours_per_week"] = int(max_hours_match.group(1))
        
        # Extract preferred languages
        lang_match = re.search(r"prefer.*?languages?\s+([A-Za-z\s,]+)", query, re.IGNORECASE)
        if lang_match:
            languages = [lang.strip() for lang in lang_match.group(1).split(',')]
            preferences["preferred_languages"] = languages
        
        return preferences
    
    def _analyze_skill_diversity(self, skills: List[str]) -> Dict:
        """Analyze skill diversity"""
        
        if not skills:
            return {"score": 0, "analysis": "No skills listed"}
        
        # Categorize skills
        categories = {
            "programming": ["Python", "JavaScript", "Java", "C++", "Go", "Rust"],
            "web": ["React", "Vue", "Angular", "HTML", "CSS"],
            "mobile": ["React Native", "Flutter", "Swift", "Kotlin"],
            "data": ["SQL", "Pandas", "NumPy", "TensorFlow"],
            "devops": ["Docker", "Kubernetes", "AWS", "CI/CD"]
        }
        
        skill_categories = set()
        for skill in skills:
            for category, category_skills in categories.items():
                if skill in category_skills:
                    skill_categories.add(category)
                    break
        
        diversity_score = len(skill_categories) / len(categories) * 100
        
        return {
            "score": diversity_score,
            "categories": list(skill_categories),
            "analysis": f"You have skills in {len(skill_categories)} categories"
        }
    
    def _assess_experience_level(self, profile: Dict) -> str:
        """Assess user experience level"""
        
        completed_bounties = profile.get("completed_bounties", 0)
        total_earned = profile.get("total_earned", 0)
        skills_count = len(profile.get("skills", []))
        
        if completed_bounties >= 20 and total_earned >= 10000:
            return "Expert"
        elif completed_bounties >= 10 and total_earned >= 5000:
            return "Advanced"
        elif completed_bounties >= 5 and total_earned >= 2000:
            return "Intermediate"
        else:
            return "Beginner"
    
    def _calculate_earning_potential(self, profile: Dict) -> Dict:
        """Calculate earning potential"""
        
        skills = profile.get("skills", [])
        completed_bounties = profile.get("completed_bounties", 0)
        
        # Base earning potential by skill count
        base_potential = len(skills) * 500
        
        # Adjust by experience
        experience_multiplier = min(2.0, 1 + (completed_bounties * 0.1))
        
        estimated_potential = base_potential * experience_multiplier
        
        return {
            "estimated_monthly": estimated_potential,
            "estimated_yearly": estimated_potential * 12,
            "factors": {
                "skill_count": len(skills),
                "experience": completed_bounties,
                "multiplier": experience_multiplier
            }
        }
    
    def _generate_profile_recommendations(self, profile: Dict) -> List[str]:
        """Generate profile improvement recommendations"""
        
        recommendations = []
        
        skills = profile.get("skills", [])
        completed_bounties = profile.get("completed_bounties", 0)
        
        # Skill recommendations
        if len(skills) < 3:
            recommendations.append("📚 Add more skills to increase your marketability")
        
        # Experience recommendations
        if completed_bounties < 5:
            recommendations.append("🎯 Complete more bounties to build your reputation")
        
        # Profile completeness
        if not profile.get("github_username"):
            recommendations.append("🔗 Add your GitHub username to your profile")
        
        # Skill diversity
        skill_diversity = self._analyze_skill_diversity(skills)
        if skill_diversity["score"] < 50:
            recommendations.append("🌟 Diversify your skills across different categories")
        
        return recommendations
    
    def _handle_unknown_action(self, query: str) -> Dict:
        """Handle unknown actions"""
        
        return {
            "action": "unknown",
            "message": "I can help you with:\n- View your profile\n- Update skills\n- Update preferences\n- Get profile insights",
            "status": "info"
        }
    
    def _format_profile_response(self, result: Dict, action: str) -> str:
        """Format profile response"""
        
        if action == "view_profile":
            profile = result["profile"]
            response = f"## 👤 Your Profile\n\n"
            response += f"**GitHub:** {profile.get('github_username', 'Not set')}\n"
            response += f"**Skills:** {', '.join(profile.get('skills', []))}\n"
            response += f"**Completed Bounties:** {profile.get('completed_bounties', 0)}\n"
            response += f"**Total Earned:** ${profile.get('total_earned', 0):,}\n"
            
            preferences = profile.get('preferences', {})
            if preferences:
                response += f"**Min Bounty:** ${preferences.get('min_bounty', 0)}\n"
                response += f"**Max Hours/Week:** {preferences.get('max_hours_per_week', 0)}\n"
        
        elif action == "update_skills":
            changes = result["changes"]
            response = f"## ✅ Skills Updated\n\n"
            if changes["added"]:
                response += f"**Added:** {', '.join(changes['added'])}\n"
            if changes["removed"]:
                response += f"**Removed:** {', '.join(changes['removed'])}\n"
            response += f"**Total Skills:** {changes['total_skills']}\n"
        
        elif action == "update_preferences":
            changes = result["changes"]
            response = f"## ⚙️ Preferences Updated\n\n"
            for key, value in changes.items():
                response += f"**{key.replace('_', ' ').title()}:** {value}\n"
        
        elif action == "get_insights":
            insights = result["insights"]
            response = f"## 📊 Profile Insights\n\n"
            
            # Skill diversity
            diversity = insights["skill_diversity"]
            response += f"**Skill Diversity:** {diversity['score']:.1f}% - {diversity['analysis']}\n"
            
            # Experience level
            response += f"**Experience Level:** {insights['experience_level']}\n"
            
            # Earning potential
            potential = insights["earning_potential"]
            response += f"**Estimated Monthly Potential:** ${potential['estimated_monthly']:,.0f}\n"
            
            # Recommendations
            if insights["recommendations"]:
                response += "\n**Recommendations:**\n"
                for rec in insights["recommendations"]:
                    response += f"{rec}\n"
        
        else:
            response = result.get("message", "Profile action completed")
        
        return response
    
    def get_description(self) -> str:
        """Get agent description"""
        return "Manages user profiles, skills, and preferences"
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities"""
        return self.capabilities
