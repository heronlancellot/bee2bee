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
            # MeTTa returns: [[expr1, expr2, expr3, ...]] where each expr is (tier threshold)
            thresholds = []

            if results and len(results) > 0:
                # results[0] is a list of expressions
                expressions = results[0] if isinstance(results[0], list) else results

                for expr in expressions:
                    if hasattr(expr, 'get_children'):
                        children = expr.get_children()
                        if len(children) >= 2:
                            # Extract tier name from first child
                            tier_atom = children[0]
                            if hasattr(tier_atom, 'get_name'):
                                tier = tier_atom.get_name()
                            else:
                                tier = str(tier_atom).strip()

                            # Extract threshold value from second child
                            threshold_atom = children[1]
                            if hasattr(threshold_atom, 'get_object'):
                                threshold = threshold_atom.get_object().value
                            else:
                                threshold = int(str(threshold_atom))

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
            import traceback
            traceback.print_exc()
            return "simple"

    def get_repo_size_category(self, file_count: int) -> str:
        """Categorize repository size based on file count."""
        try:
            query_str = '!(match &self (file-count-threshold $category $threshold) ($category $threshold))'
            results = self.metta.run(query_str)

            if not results:
                return "small"

            thresholds = []

            if results and len(results) > 0:
                expressions = results[0] if isinstance(results[0], list) else results

                for expr in expressions:
                    if hasattr(expr, 'get_children'):
                        children = expr.get_children()
                        if len(children) >= 2:
                            category_atom = children[0]
                            if hasattr(category_atom, 'get_name'):
                                category = category_atom.get_name()
                            else:
                                category = str(category_atom).strip()

                            threshold_atom = children[1]
                            if hasattr(threshold_atom, 'get_object'):
                                threshold = threshold_atom.get_object().value
                            else:
                                threshold = int(str(threshold_atom))

                            thresholds.append((category, threshold))

            thresholds.sort(key=lambda x: x[1], reverse=True)

            for category, threshold in thresholds:
                if file_count >= threshold:
                    return category

            return "small"
        except Exception as e:
            print(f"Error in get_repo_size_category: {e}")
            import traceback
            traceback.print_exc()
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

            if results and len(results) > 0:
                expressions = results[0] if isinstance(results[0], list) else results

                for expr in expressions:
                    if hasattr(expr, 'get_children'):
                        children = expr.get_children()
                        if len(children) >= 2:
                            tier_atom = children[0]
                            if hasattr(tier_atom, 'get_name'):
                                tier = tier_atom.get_name()
                            else:
                                tier = str(tier_atom).strip()

                            threshold_atom = children[1]
                            if hasattr(threshold_atom, 'get_object'):
                                threshold = threshold_atom.get_object().value
                            else:
                                threshold = int(str(threshold_atom))

                            thresholds.append((tier, threshold))

            thresholds.sort(key=lambda x: x[1], reverse=True)

            for tier, threshold in thresholds:
                if complexity_score >= threshold:
                    return tier

            return "beginner"
        except Exception as e:
            print(f"Error in get_difficulty_tier: {e}")
            import traceback
            traceback.print_exc()
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
