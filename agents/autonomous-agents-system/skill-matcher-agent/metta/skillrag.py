# skillrag.py - Skill Matching RAG System
from hyperon import MeTTa, E, S, ValueAtom
from typing import List, Dict, Tuple
import re

class SkillRAG:
    def __init__(self, metta_instance: MeTTa):
        self.metta = metta_instance

    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from natural language text using pattern matching."""
        skills = []
        text_lower = text.lower()
        
        # Common skill patterns (expanded)
        skill_patterns = {
            "python": ["python", "py", "django", "flask", "fastapi", "pandas", "numpy", "pytorch", "tensorflow"],
            "javascript": ["javascript", "js", "node", "nodejs", "express", "jquery"],
            "typescript": ["typescript", "ts"],
            "react": ["react", "reactjs", "jsx", "nextjs", "next.js"],
            "vue": ["vue", "vuejs", "nuxt"],
            "angular": ["angular", "angularjs"],
            "go": ["go", "golang"],
            "rust": ["rust"],
            "java": ["java", "spring", "springboot"],
            "c++": ["c++", "cpp", "cplusplus"],
            "c#": ["c#", "csharp", "dotnet"],
            "ruby": ["ruby", "rails"],
            "php": ["php", "laravel", "symfony"],
            "swift": ["swift", "ios"],
            "kotlin": ["kotlin", "android"],
            "html": ["html", "html5"],
            "css": ["css", "css3", "scss", "sass", "tailwind", "bootstrap"],
            "sql": ["sql", "mysql", "postgresql", "mongodb", "redis"],
            "git": ["git", "github", "gitlab"],
            "docker": ["docker", "containerization"],
            "kubernetes": ["kubernetes", "k8s"],
            "aws": ["aws", "amazon web services", "lambda", "s3"],
            "azure": ["azure", "microsoft azure"],
            "gcp": ["gcp", "google cloud"],
            "linux": ["linux", "ubuntu", "centos", "debian"],
            "bash": ["bash", "shell", "scripting"],
            "api": ["api", "rest", "graphql", "microservices"]
        }
        
        # Extract skills from patterns
        for skill, patterns in skill_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                skills.append(skill.title())
        
        # If no skills detected, try to infer from context
        if not skills:
            # Check for common phrases that might indicate skills
            if any(word in text_lower for word in ["programming", "coding", "development", "developer"]):
                skills.append("General Programming")
            if any(word in text_lower for word in ["frontend", "front-end", "ui", "ux"]):
                skills.append("Frontend Development")
            if any(word in text_lower for word in ["backend", "back-end", "server"]):
                skills.append("Backend Development")
            if any(word in text_lower for word in ["fullstack", "full-stack", "full stack"]):
                skills.append("Fullstack Development")
        
        return list(set(skills))  # Remove duplicates

    def get_skill_domain(self, skill: str) -> str:
        """Get domain expertise for a skill using MeTTa."""
        try:
            query_str = f'!(match &self (language-domain {skill} $domain) $domain)'
            results = self.metta.run(query_str)
            
            if results and len(results) > 0 and results[0]:
                return results[0][0].get_object().value
            
            return "general-programming"
        except Exception as e:
            print(f"Error getting domain for {skill}: {e}")
            return "general-programming"

    def find_skill_relationships(self, user_skills: List[str], required_skills: List[str]) -> Dict[str, List[str]]:
        """Find relationships between user skills and required skills."""
        relationships = {
            "exact_matches": [],
            "alternatives": [],
            "prerequisites": [],
            "domain_matches": []
        }
        
        for req_skill in required_skills:
            # Check for exact matches
            if req_skill in user_skills:
                relationships["exact_matches"].append(req_skill)
                continue
            
            # Check for alternatives
            try:
                query_str = f'!(match &self (skill-alternative {req_skill} $alt) $alt)'
                results = self.metta.run(query_str)
                if results:
                    for result in results:
                        if result and len(result) > 0:
                            alt_skill = str(result[0]).strip()
                            if alt_skill in user_skills:
                                relationships["alternatives"].append({
                                    "required": req_skill,
                                    "user_has": alt_skill,
                                    "type": "alternative"
                                })
            except Exception as e:
                print(f"Error checking alternatives for {req_skill}: {e}")
            
            # Check for prerequisites
            try:
                query_str = f'!(match &self (skill-prerequisite {req_skill} $prereq) $prereq)'
                results = self.metta.run(query_str)
                if results:
                    for result in results:
                        if result and len(result) > 0:
                            prereq_skill = str(result[0]).strip()
                            if prereq_skill in user_skills:
                                relationships["prerequisites"].append({
                                    "required": req_skill,
                                    "user_has": prereq_skill,
                                    "type": "prerequisite"
                                })
            except Exception as e:
                print(f"Error checking prerequisites for {req_skill}: {e}")
            
            # Check for domain matches
            req_domain = self.get_skill_domain(req_skill)
            for user_skill in user_skills:
                user_domain = self.get_skill_domain(user_skill)
                if req_domain == user_domain and req_skill != user_skill:
                    relationships["domain_matches"].append({
                        "required": req_skill,
                        "user_has": user_skill,
                        "domain": req_domain,
                        "type": "domain"
                    })
        
        return relationships

    def calculate_match_score(self, relationships: Dict[str, List[str]], required_skills: List[str]) -> Tuple[float, float]:
        """Calculate match score and confidence using MeTTa reasoning."""
        if not required_skills:
            return 0.0, 0.0
        
        exact_count = len(relationships["exact_matches"])
        alternative_count = len(relationships["alternatives"])
        prerequisite_count = len(relationships["prerequisites"])
        domain_count = len(relationships["domain_matches"])
        
        # Calculate base match score
        exact_score = exact_count * 100
        alternative_score = alternative_count * 70
        prerequisite_score = prerequisite_count * 30
        domain_score = domain_count * 50
        
        total_score = exact_score + alternative_score + prerequisite_score + domain_score
        match_percentage = total_score / (len(required_skills) * 100)
        
        # Calculate confidence based on relationship quality
        confidence = min(100, match_percentage * 100 + (alternative_count * 5) + (domain_count * 3))
        
        return match_percentage * 100, confidence

    def generate_intelligent_response(self, user_skills: List[str], required_skills: List[str], 
                                    relationships: Dict[str, List[str]], 
                                    match_score: float, confidence: float) -> str:
        """Generate intelligent response with MeTTa reasoning."""
        
        response = f"""🎯 **Intelligent Skill Match Analysis**

**Match Score:** {match_score:.0f}%
**Confidence:** {confidence:.0f}%

✅ **Exact Matches ({len(relationships['exact_matches'])}):**
{', '.join(relationships['exact_matches']) if relationships['exact_matches'] else '  None'}

🔄 **Related Skills ({len(relationships['alternatives'])}):**"""
        
        for alt in relationships['alternatives']:
            response += f"\n  • You have {alt['user_has']} (alternative to {alt['required']})"
        
        if relationships['prerequisites']:
            response += f"\n\n📚 **Prerequisites Met ({len(relationships['prerequisites'])}):**"
            for prereq in relationships['prerequisites']:
                response += f"\n  • You have {prereq['user_has']} (prerequisite for {prereq['required']})"
        
        if relationships['domain_matches']:
            response += f"\n\n🌐 **Domain Expertise ({len(relationships['domain_matches'])}):**"
            for domain in relationships['domain_matches']:
                response += f"\n  • You have {domain['user_has']} (same domain as {domain['required']} - {domain['domain']})"
        
        # Missing skills
        all_covered = (relationships['exact_matches'] + 
                      [alt['required'] for alt in relationships['alternatives']] +
                      [prereq['required'] for prereq in relationships['prerequisites']] +
                      [domain['required'] for domain in relationships['domain_matches']])
        
        missing_skills = [skill for skill in required_skills if skill not in all_covered]
        
        if missing_skills:
            response += f"\n\n❌ **Missing Skills ({len(missing_skills)}):**\n"
            response += '\n'.join([f"  • {skill}" for skill in missing_skills])
        
        # Intelligent recommendation
        response += f"\n\n💡 **AI Recommendation:** "
        if confidence >= 80:
            response += "HIGHLY RECOMMENDED - Excellent skill alignment!"
        elif confidence >= 60:
            response += "RECOMMENDED - Good match with some learning opportunities"
        elif confidence >= 40:
            response += "CONSIDER - Moderate match, significant learning needed"
        else:
            response += "CHALLENGING - Major skill gap, consider prerequisites first"
        
        response += f"\n\n🧠 **MeTTa Reasoning:** Analyzed {len(user_skills)} user skills against {len(required_skills)} requirements using symbolic AI"
        
        return response
