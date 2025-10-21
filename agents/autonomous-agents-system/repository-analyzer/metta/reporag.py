# reporag.py
from hyperon import MeTTa, E, S, ValueAtom
from typing import List, Dict

class RepoRAG:
    def __init__(self, metta_instance: MeTTa):
        self.metta = metta_instance

    def get_complexity_tier(self, loc: int) -> str:
        """Determine complexity tier based on lines of code."""
        try:
            query_str = '!(match &self (complexity-threshold $tier $threshold) ($tier $threshold))'
            results = self.metta.run(query_str)

            if not results:
                return "simple"

            # Convert results to list of (tier, threshold) tuples
            thresholds = []
            for r in results:
                if r and len(r) > 0:
                    if len(r) == 1 and hasattr(r[0], 'get_children'):
                        children = r[0].get_children()
                        if len(children) >= 2:
                            tier = str(children[0]).strip()
                            threshold = children[1].get_object().value if hasattr(children[1], 'get_object') else 0
                            thresholds.append((tier, threshold))
                    else:
                        tier = str(r[0]).strip()
                        threshold = r[1].get_object().value if hasattr(r[1], 'get_object') else 0
                        thresholds.append((tier, threshold))

            # Sort by threshold descending
            thresholds.sort(key=lambda x: x[1], reverse=True)

            # Find highest threshold that LOC meets or exceeds
            for tier, threshold in thresholds:
                if loc >= threshold:
                    return tier

            return "simple"
        except Exception as e:
            print(f"Error in get_complexity_tier: {e}")
            return "simple"

    def get_repo_size_category(self, file_count: int) -> str:
        """Categorize repository size based on file count."""
        try:
            query_str = '!(match &self (file-count-threshold $category $threshold) ($category $threshold))'
            results = self.metta.run(query_str)

            if not results:
                return "small"

            thresholds = []
            for r in results:
                if r and len(r) > 0:
                    if len(r) == 1 and hasattr(r[0], 'get_children'):
                        children = r[0].get_children()
                        if len(children) >= 2:
                            category = str(children[0]).strip()
                            threshold = children[1].get_object().value if hasattr(children[1], 'get_object') else 0
                            thresholds.append((category, threshold))
                    else:
                        category = str(r[0]).strip()
                        threshold = r[1].get_object().value if hasattr(r[1], 'get_object') else 0
                        thresholds.append((category, threshold))

            thresholds.sort(key=lambda x: x[1], reverse=True)

            for category, threshold in thresholds:
                if file_count >= threshold:
                    return category

            return "small"
        except Exception as e:
            print(f"Error in get_repo_size_category: {e}")
            return "small"

    def get_language_domain(self, language: str) -> str:
        """Get domain expertise for a programming language."""
        try:
            query_str = f'!(match &self (language-domain {language} $domain) $domain)'
            results = self.metta.run(query_str)

            if results and len(results) > 0 and results[0]:
                return results[0][0].get_object().value

            return "general-programming"
        except Exception as e:
            print(f"Error in get_language_domain for {language}: {e}")
            return "general-programming"

    def get_difficulty_tier(self, complexity_score: int) -> str:
        """Get difficulty tier for contributors based on complexity score."""
        try:
            query_str = '!(match &self (difficulty-tier $tier $threshold) ($tier $threshold))'
            results = self.metta.run(query_str)

            if not results:
                return "beginner"

            thresholds = []
            for r in results:
                if r and len(r) > 0:
                    if len(r) == 1 and hasattr(r[0], 'get_children'):
                        children = r[0].get_children()
                        if len(children) >= 2:
                            tier = str(children[0]).strip()
                            threshold = children[1].get_object().value if hasattr(children[1], 'get_object') else 0
                            thresholds.append((tier, threshold))
                    else:
                        tier = str(r[0]).strip()
                        threshold = r[1].get_object().value if hasattr(r[1], 'get_object') else 0
                        thresholds.append((tier, threshold))

            thresholds.sort(key=lambda x: x[1], reverse=True)

            for tier, threshold in thresholds:
                if complexity_score >= threshold:
                    return tier

            return "beginner"
        except Exception as e:
            print(f"Error in get_difficulty_tier: {e}")
            return "beginner"

    def infer_project_type(self, file_structure: Dict[str, bool]) -> str:
        """Infer project type from file structure indicators."""
        try:
            has_api = file_structure.get("has_api", False)
            has_ui = file_structure.get("has_ui", False)
            has_ml = file_structure.get("has_ml", False)
            has_blockchain = file_structure.get("has_blockchain", False)

            if has_blockchain:
                return "web3-project"
            if has_ml:
                return "ml-project"
            if has_api and has_ui:
                return "fullstack-app"
            if has_ui:
                return "frontend-app"
            if has_api:
                return "backend-api"

            return "general-project"
        except Exception as e:
            print(f"Error in infer_project_type: {e}")
            return "general-project"
