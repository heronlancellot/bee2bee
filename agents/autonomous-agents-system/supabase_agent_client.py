# supabase_agent_client.py - Supabase Agent Client (Working Version)
"""
Supabase client adapted for existing agent_knowledge table
Uses the actual working Supabase setup
"""

import asyncio
import json
import hashlib
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

@dataclass
class SupabaseAgentConfig:
    """Configuration for Supabase agent connection"""
    url: str
    key: str
    use_local: bool = False

class SupabaseAgentClient:
    """Supabase client adapted for existing agent_knowledge table"""
    
    def __init__(self, config: SupabaseAgentConfig):
        self.config = config
        self.supabase: Client = create_client(config.url, config.key)
    
    async def store_agent_knowledge(
        self, 
        agent_id: str, 
        topic: str, 
        content: str,
        tags: List[str] = None,
        confidence: float = 0.7
    ) -> Optional[str]:
        """Store agent knowledge in the existing agent_knowledge table"""
        try:
            knowledge_data = {
                'agent_id': agent_id,
                'topic': topic,
                'content': content,
                'tags': tags or [],
                'confidence': confidence,
                'access_count': 0
            }
            
            result = self.supabase.table('agent_knowledge').insert(knowledge_data).execute()
            
            if result.data:
                return result.data[0]['id']
            return None
            
        except Exception as e:
            print(f"Error storing agent knowledge: {e}")
            return None
    
    async def search_agent_knowledge(
        self, 
        query: str = None,
        agent_id: str = None,
        topic: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search agent knowledge using text matching"""
        try:
            query_builder = self.supabase.table('agent_knowledge').select('*')
            
            if agent_id:
                query_builder = query_builder.eq('agent_id', agent_id)
            
            if topic:
                query_builder = query_builder.eq('topic', topic)
            
            if query:
                # Simple text search in content
                query_builder = query_builder.ilike('content', f'%{query}%')
            
            result = query_builder.limit(limit).execute()
            
            return result.data
            
        except Exception as e:
            print(f"Error searching agent knowledge: {e}")
            return []
    
    async def get_agent_insights(self, agent_id: str) -> Dict[str, Any]:
        """Get insights about an agent's knowledge"""
        try:
            # Get knowledge count
            knowledge_result = self.supabase.table('agent_knowledge').select('id', count='exact').eq('agent_id', agent_id).execute()
            
            # Get recent knowledge
            recent_result = self.supabase.table('agent_knowledge').select('*').eq('agent_id', agent_id).order('created_at', desc=True).limit(5).execute()
            
            # Get topics
            topics_result = self.supabase.table('agent_knowledge').select('topic').eq('agent_id', agent_id).execute()
            topics = list(set([item['topic'] for item in topics_result.data]))
            
            return {
                "agent_id": agent_id,
                "total_knowledge": knowledge_result.count,
                "recent_knowledge": recent_result.data,
                "topics": topics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting agent insights: {e}")
            return {}
    
    async def store_skill_match_pattern(
        self, 
        agent_id: str,
        user_skills: List[str],
        required_skills: List[str],
        match_score: float,
        confidence: float,
        relationships: Dict[str, Any]
    ) -> Optional[str]:
        """Store skill match pattern as knowledge"""
        
        # Create semantic content
        semantic_content = f"""
        Skill Match Pattern:
        User Skills: {', '.join(user_skills)}
        Required Skills: {', '.join(required_skills)}
        Match Score: {match_score}%
        Confidence: {confidence}%
        Exact Matches: {', '.join(relationships.get('exact_matches', []))}
        Related Skills: {', '.join(relationships.get('related_skills', []))}
        Missing Skills: {', '.join(relationships.get('missing_skills', []))}
        
        This pattern shows how skills relate to each other and what combinations work well for matching.
        """
        
        # Create tags
        tags = ['skill_match', 'pattern'] + user_skills + required_skills
        
        return await self.store_agent_knowledge(
            agent_id=agent_id,
            topic='skill_matching',
            content=semantic_content.strip(),
            tags=tags,
            confidence=confidence/100
        )
    
    async def find_similar_skill_patterns(
        self,
        user_skills: List[str],
        required_skills: List[str],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar skill patterns using tag-based search"""
        try:
            # Search by topic first
            query_builder = self.supabase.table('agent_knowledge').select('*').eq('topic', 'skill_matching')

            # Build search tags from both user and required skills
            search_tags = user_skills + required_skills + ['skill_match']

            # Get all skill patterns with matching topic
            all_results = query_builder.limit(100).execute()

            # Filter results that have matching tags
            filtered_results = []
            for result in all_results.data:
                result_tags = result.get('tags', [])
                # Check if any of our search tags are in the result tags
                if any(tag in result_tags for tag in search_tags):
                    filtered_results.append(result)

            # Limit results
            filtered_results = filtered_results[:limit]

            print(f"🔍 RAG RETRIEVAL: Found {len(filtered_results)} similar skill patterns")

            return filtered_results

        except Exception as e:
            print(f"Error finding similar skill patterns: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def increment_access_count(self, knowledge_id: str):
        """Increment access count for knowledge"""
        try:
            # Get current count
            result = self.supabase.table('agent_knowledge').select('access_count').eq('id', knowledge_id).execute()

            if result.data:
                current_count = result.data[0]['access_count']

                # Update count
                self.supabase.table('agent_knowledge').update({
                    'access_count': current_count + 1
                }).eq('id', knowledge_id).execute()

        except Exception as e:
            print(f"Error incrementing access count: {e}")

    async def search_similar_user_profiles(
        self,
        skills: List[str],
        years_experience: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        RAG RETRIEVAL: Search for similar user profiles in knowledge base
        Returns historical profiles that match skills and experience level
        """
        try:
            # Determine experience level
            if years_experience < 2:
                exp_level = 'beginner'
            elif years_experience < 5:
                exp_level = 'intermediate'
            elif years_experience < 10:
                exp_level = 'advanced'
            else:
                exp_level = 'expert'

            # Search by topic first
            query_builder = self.supabase.table('agent_knowledge').select('*').eq('topic', 'user_profiles')

            # Filter by tags (skills + experience level)
            # Use contains to match any of the skills or experience level in tags
            search_tags = skills + [exp_level]

            # Get all profiles with matching topic
            all_results = query_builder.limit(100).execute()

            # Filter results that have matching tags
            filtered_results = []
            for result in all_results.data:
                result_tags = result.get('tags', [])
                # Check if any of our search tags are in the result tags
                if any(tag in result_tags for tag in search_tags):
                    filtered_results.append(result)

            # Limit results
            filtered_results = filtered_results[:limit]

            print(f"🔍 RAG RETRIEVAL: Found {len(filtered_results)} similar user profiles")

            return filtered_results

        except Exception as e:
            print(f"Error searching similar user profiles: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def store_user_profile_pattern(
        self,
        agent_id: str,
        user_id: str,
        skills: List[str],
        years_experience: int,
        skill_level: str,
        preferences: Dict[str, Any] = None
    ) -> Optional[str]:
        """Store user profile pattern as knowledge"""

        semantic_content = f"""
        User Profile Pattern:
        User ID: {user_id}
        Skills: {', '.join(skills)}
        Experience: {years_experience} years ({skill_level})
        Preferences: {json.dumps(preferences or {})}

        This profile shows the user's capabilities and helps match them with suitable projects.
        """

        tags = ['user_profile', 'skills', skill_level] + skills + [user_id]

        return await self.store_agent_knowledge(
            agent_id=agent_id,
            topic='user_profiles',
            content=semantic_content.strip(),
            tags=tags,
            confidence=0.9
        )

    async def search_similar_bounty_estimates(
        self,
        complexity_score: int,
        required_skills: List[str],
        estimated_hours: int = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        RAG RETRIEVAL: Search for similar bounty estimates in knowledge base
        Returns historical estimates with similar complexity and skills
        """
        try:
            # Search by topic first
            query_builder = self.supabase.table('agent_knowledge').select('*').eq('topic', 'bounty_estimation')

            # Build search tags
            complexity_tag = f'complexity_{complexity_score}'
            search_tags = required_skills + [complexity_tag, 'bounty_estimation']

            # Get all estimates with matching topic
            all_results = query_builder.limit(100).execute()

            # Filter results that have matching tags
            filtered_results = []
            for result in all_results.data:
                result_tags = result.get('tags', [])
                # Check if any of our search tags are in the result tags
                if any(tag in result_tags for tag in search_tags):
                    filtered_results.append(result)

            # Limit results
            filtered_results = filtered_results[:limit]

            print(f"🔍 RAG RETRIEVAL: Found {len(filtered_results)} similar bounty estimates")

            return filtered_results

        except Exception as e:
            print(f"Error searching similar bounty estimates: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def store_bounty_estimation_pattern(
        self,
        agent_id: str,
        complexity_score: int,
        required_skills: List[str],
        estimated_hours: int,
        estimated_value: int,
        hourly_rate: float,
        tier: str,
        repo_stars: int = 0
    ) -> Optional[str]:
        """Store bounty estimation pattern as knowledge"""

        semantic_content = f"""
        Bounty Estimation Pattern:
        Complexity: {complexity_score}/10
        Required Skills: {', '.join(required_skills)}
        Estimated Time: {estimated_hours} hours
        Estimated Value: ${estimated_value}
        Hourly Rate: ${hourly_rate:.2f}/hour
        Tier: {tier}
        Repository Stars: {repo_stars}

        This pattern helps estimate bounty values based on complexity, skills, and market rates.
        """

        tags = ['bounty_estimation', 'pricing', tier, f'complexity_{complexity_score}'] + required_skills

        return await self.store_agent_knowledge(
            agent_id=agent_id,
            topic='bounty_estimation',
            content=semantic_content.strip(),
            tags=tags,
            confidence=0.85
        )

# Global client instance
def create_supabase_agent_client() -> SupabaseAgentClient:
    """Create Supabase agent client with environment configuration"""
    
    # Determine if using local or remote Supabase
    use_local = os.getenv("NEXT_PUBLIC_USE_LOCAL_SUPABASE", "false").lower() == "true"
    
    if use_local:
        url = "http://127.0.0.1:54321"
        key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", "sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH")
    else:
        url = os.getenv("NEXT_PUBLIC_SUPABASE_URL", "")
        key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", "")
    
    config = SupabaseAgentConfig(
        url=url,
        key=key,
        use_local=use_local
    )
    
    return SupabaseAgentClient(config)

# Example usage
async def main():
    """Example usage of Supabase agent client"""
    
    client = create_supabase_agent_client()
    
    # Store skill match pattern
    pattern_id = await client.store_skill_match_pattern(
        agent_id="skill_matcher_001",
        user_skills=["Python", "React"],
        required_skills=["JavaScript", "FastAPI"],
        match_score=75.0,
        confidence=82.0,
        relationships={
            "exact_matches": ["JavaScript"],
            "related_skills": ["Python", "React"],
            "missing_skills": ["FastAPI"]
        }
    )
    
    print(f"Stored pattern: {pattern_id}")
    
    # Search for similar patterns
    results = await client.find_similar_skill_patterns(
        user_skills=["Python"],
        required_skills=["JavaScript"],
        limit=3
    )
    
    print(f"Found {len(results)} similar patterns")
    
    # Get agent insights
    insights = await client.get_agent_insights("skill_matcher_001")
    print(f"Agent insights: {insights}")

if __name__ == "__main__":
    asyncio.run(main())
