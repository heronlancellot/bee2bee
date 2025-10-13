# utils.py
import requests
from typing import Dict, Any, List
import re

def fetch_github_repo(owner: str, repo: str) -> Dict[str, Any]:
    """Fetch GitHub repository data via API."""
    try:
        # Fetch repo data
        repo_response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}",
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=10
        )

        if repo_response.status_code != 200:
            return {"error": f"Failed to fetch repo: {repo_response.status_code}"}

        repo_data = repo_response.json()

        # Fetch languages
        languages_response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/languages",
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=10
        )

        languages_data = languages_response.json() if languages_response.status_code == 200 else {}

        # Fetch file tree (top level)
        tree_response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/git/trees/{repo_data['default_branch']}?recursive=1",
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=10
        )

        tree_data = tree_response.json() if tree_response.status_code == 200 else {}

        # Fetch README
        readme_response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/readme",
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=10
        )

        readme_data = readme_response.json() if readme_response.status_code == 200 else {}

        return {
            "name": repo_data['name'],
            "full_name": repo_data['full_name'],
            "owner": repo_data['owner']['login'],
            "description": repo_data.get('description', 'No description'),
            "stars": repo_data['stargazers_count'],
            "forks": repo_data['forks_count'],
            "open_issues": repo_data['open_issues_count'],
            "languages": languages_data,
            "default_branch": repo_data['default_branch'],
            "size": repo_data['size'],  # KB
            "created_at": repo_data['created_at'],
            "updated_at": repo_data['updated_at'],
            "tree": tree_data.get('tree', []),
            "readme_url": readme_data.get('html_url', ''),
            "repo_url": repo_data['html_url']
        }

    except Exception as e:
        return {"error": str(e)}


def calculate_loc_from_files(tree: List[Dict]) -> int:
    """
    Calculate estimated LOC based on file extensions.
    Uses average LOC per extension similar to Code Index MCP approach.
    """
    # Average lines per file type (conservative estimates)
    avg_loc_by_ext = {
        'py': 100,       # Python
        'js': 80,        # JavaScript
        'ts': 80,        # TypeScript
        'jsx': 80,       # React
        'tsx': 80,       # React TypeScript
        'go': 120,       # Go
        'rs': 100,       # Rust
        'java': 150,     # Java
        'kt': 100,       # Kotlin
        'swift': 100,    # Swift
        'cpp': 120,      # C++
        'cc': 120,       # C++
        'c': 100,        # C
        'h': 50,         # Headers
        'hpp': 50,       # C++ Headers
        'rb': 90,        # Ruby
        'php': 100,      # PHP
        'cs': 120,       # C#
        'sol': 80,       # Solidity
        'vy': 80,        # Vyper
        'sh': 50,        # Shell
        'bash': 50,      # Bash
        'yml': 30,       # YAML
        'yaml': 30,      # YAML
        'json': 20,      # JSON
        'xml': 30,       # XML
        'html': 50,      # HTML
        'css': 50,       # CSS
        'scss': 60,      # SCSS
        'vue': 100,      # Vue
        'md': 40,        # Markdown
        'txt': 20,       # Text
    }

    total_loc = 0
    code_file_count = 0
    ext_breakdown = {}

    for item in tree:
        if item['type'] == 'blob':
            path = item['path']
            if '.' in path:
                ext = path.split('.')[-1].lower()
                if ext in avg_loc_by_ext:
                    loc = avg_loc_by_ext[ext]
                    total_loc += loc
                    code_file_count += 1
                    ext_breakdown[ext] = ext_breakdown.get(ext, {'count': 0, 'loc': 0})
                    ext_breakdown[ext]['count'] += 1
                    ext_breakdown[ext]['loc'] += loc

    print(f"[DEBUG LOC] Total code files: {code_file_count}")
    print(f"[DEBUG LOC] Extension breakdown:")
    for ext, data in sorted(ext_breakdown.items(), key=lambda x: x[1]['loc'], reverse=True):
        print(f"  - .{ext}: {data['count']} files × {avg_loc_by_ext[ext]} avg = {data['loc']} LOC")
    print(f"[DEBUG LOC] Total estimated LOC: {total_loc:,}")

    return total_loc


def analyze_file_structure(tree: List[Dict]) -> Dict[str, Any]:
    """Analyze repository file structure to detect patterns."""
    try:
        file_count = 0
        total_size = 0
        extensions = {}
        has_api = False
        has_ui = False
        has_ml = False
        has_blockchain = False
        frameworks = []

        # Config file patterns
        config_files = {
            "package.json": None,
            "requirements.txt": None,
            "go.mod": None,
            "Cargo.toml": None,
            "pom.xml": None,
            "build.gradle": None
        }

        # Pattern detection
        api_patterns = ['/api/', '/routes/', '/endpoints/', '/controllers/', '/handlers/']
        ui_patterns = ['/components/', '/views/', '/pages/', '/ui/', '/frontend/']
        ml_patterns = ['/models/', '/train', '/dataset', 'ml/', 'tensorflow', 'pytorch']
        blockchain_patterns = ['/contracts/', 'solidity', '.sol', 'web3', 'ethers']

        for item in tree:
            if item['type'] == 'blob':  # file
                file_count += 1
                total_size += item.get('size', 0)

                path = item['path']

                # Extract extension
                if '.' in path:
                    ext = path.split('.')[-1]
                    extensions[ext] = extensions.get(ext, 0) + 1

                # Check config files
                for config_file in config_files:
                    if path.endswith(config_file):
                        config_files[config_file] = path

                # Pattern detection
                if any(pattern in path.lower() for pattern in api_patterns):
                    has_api = True
                if any(pattern in path.lower() for pattern in ui_patterns):
                    has_ui = True
                if any(pattern in path.lower() for pattern in ml_patterns):
                    has_ml = True
                if any(pattern in path.lower() for pattern in blockchain_patterns):
                    has_blockchain = True

        return {
            "file_count": file_count,
            "total_size_bytes": total_size,
            "extensions": extensions,
            "config_files": {k: v for k, v in config_files.items() if v is not None},
            "has_api": has_api,
            "has_ui": has_ui,
            "has_ml": has_ml,
            "has_blockchain": has_blockchain
        }

    except Exception as e:
        print(f"Error analyzing file structure: {e}")
        return {}


def analyze_with_metta(repo_data: Dict[str, Any], file_analysis: Dict[str, Any], rag) -> Dict[str, Any]:
    """Use MeTTa reasoning to analyze repository."""
    if "error" in repo_data:
        return {}

    insights = {
        "complexity_tier": None,
        "size_category": None,
        "difficulty_tier": None,
        "project_type": None,
        "tech_domains": [],
        "documentation": None,
        "reasoning": []
    }

    try:
        # Calculate LOC using file-based estimation
        tree = repo_data.get('tree', [])
        estimated_loc = calculate_loc_from_files(tree)

        # Fallback to old method if no tree data
        if estimated_loc == 0:
            estimated_loc = repo_data.get('size', 0) * 10

        # Complexity tier
        complexity_tier = rag.get_complexity_tier(estimated_loc)
        insights["complexity_tier"] = complexity_tier
        insights["reasoning"].append(f"Complexity: {complexity_tier} (~{estimated_loc:,} LOC)")

        # Size category
        file_count = file_analysis.get("file_count", 0)
        size_category = rag.get_repo_size_category(file_count)
        insights["size_category"] = size_category
        insights["reasoning"].append(f"Repository size: {size_category} ({file_count} files)")

        # Project type
        project_type = rag.infer_project_type({
            "has_api": file_analysis.get("has_api", False),
            "has_ui": file_analysis.get("has_ui", False),
            "has_ml": file_analysis.get("has_ml", False),
            "has_blockchain": file_analysis.get("has_blockchain", False)
        })
        insights["project_type"] = project_type
        insights["reasoning"].append(f"Project type: {project_type}")

        # Tech domains from languages
        for lang in repo_data.get("languages", {}).keys():
            domain = rag.get_language_domain(lang)
            if domain not in insights["tech_domains"]:
                insights["tech_domains"].append(domain)
                insights["reasoning"].append(f"Tech domain: {lang} → {domain}")

        # Documentation analysis
        doc_analysis = analyze_documentation(tree)
        insights["documentation"] = doc_analysis
        insights["reasoning"].append(f"Documentation: {doc_analysis['rating']} ({doc_analysis['score']}/100 points)")

        # Difficulty tier (0-100 score based on complexity)
        complexity_score = min(100, int((estimated_loc / 50000) * 100))
        difficulty_tier = rag.get_difficulty_tier(complexity_score)
        insights["difficulty_tier"] = difficulty_tier
        insights["reasoning"].append(f"Difficulty: {difficulty_tier} (score: {complexity_score}/100)")

        return insights

    except Exception as e:
        print(f"MeTTa analysis error: {e}")
        return insights


def analyze_documentation(tree: List[Dict]) -> Dict[str, Any]:
    """
    Score documentation quality (0-100).

    Scoring:
    - README exists and > 1KB: 30 points
    - LICENSE file exists: 10 points
    - CONTRIBUTING.md exists: 15 points
    - CHANGELOG.md exists: 10 points
    - /docs/ folder exists: 15 points
    - CODE_OF_CONDUCT.md: 5 points
    - SECURITY.md: 5 points
    - .github/ folder (templates): 10 points
    """
    score = 0
    details = {}

    # Helper to find files (case-insensitive)
    def find_file(pattern: str) -> Dict:
        pattern_lower = pattern.lower()
        for item in tree:
            if item['type'] == 'blob':
                if item['path'].lower() == pattern_lower or item['path'].lower().endswith(f"/{pattern_lower}"):
                    return item
        return None

    # Helper to check folder exists
    def has_folder(folder_name: str) -> bool:
        folder_lower = folder_name.lower()
        for item in tree:
            if item['type'] == 'tree' or '/' in item.get('path', ''):
                path_lower = item['path'].lower()
                if path_lower.startswith(f"{folder_lower}/") or f"/{folder_lower}/" in path_lower:
                    return True
        return False

    # README (30 points)
    readme = find_file('README.md') or find_file('README') or find_file('readme.md')
    if readme:
        readme_size = readme.get('size', 0)
        if readme_size > 1024:  # > 1KB
            score += 30
            details['readme'] = {'exists': True, 'size_kb': round(readme_size/1024, 2), 'points': 30}
        else:
            score += 10  # Exists but too small
            details['readme'] = {'exists': True, 'size_kb': round(readme_size/1024, 2), 'points': 10, 'too_small': True}
    else:
        details['readme'] = {'exists': False, 'points': 0}

    # LICENSE (10 points)
    license_file = find_file('LICENSE') or find_file('LICENSE.md') or find_file('license')
    if license_file:
        score += 10
        details['license'] = {'exists': True, 'points': 10}
    else:
        details['license'] = {'exists': False, 'points': 0}

    # CONTRIBUTING.md (15 points)
    contributing = find_file('CONTRIBUTING.md') or find_file('contributing.md')
    if contributing:
        score += 15
        details['contributing'] = {'exists': True, 'points': 15}
    else:
        details['contributing'] = {'exists': False, 'points': 0}

    # CHANGELOG.md (10 points)
    changelog = find_file('CHANGELOG.md') or find_file('changelog.md') or find_file('HISTORY.md')
    if changelog:
        score += 10
        details['changelog'] = {'exists': True, 'points': 10}
    else:
        details['changelog'] = {'exists': False, 'points': 0}

    # /docs/ folder (15 points)
    if has_folder('docs'):
        score += 15
        details['docs_folder'] = {'exists': True, 'points': 15}
    else:
        details['docs_folder'] = {'exists': False, 'points': 0}

    # CODE_OF_CONDUCT.md (5 points)
    coc = find_file('CODE_OF_CONDUCT.md') or find_file('code_of_conduct.md')
    if coc:
        score += 5
        details['code_of_conduct'] = {'exists': True, 'points': 5}
    else:
        details['code_of_conduct'] = {'exists': False, 'points': 0}

    # SECURITY.md (5 points)
    security = find_file('SECURITY.md') or find_file('security.md') or find_file('.github/SECURITY.md')
    if security:
        score += 5
        details['security'] = {'exists': True, 'points': 5}
    else:
        details['security'] = {'exists': False, 'points': 0}

    # .github/ folder (10 points) - for issue/PR templates
    if has_folder('.github'):
        score += 10
        details['github_folder'] = {'exists': True, 'points': 10}
    else:
        details['github_folder'] = {'exists': False, 'points': 0}

    # Rating
    if score >= 80:
        rating = "Excellent"
    elif score >= 60:
        rating = "Good"
    elif score >= 40:
        rating = "Fair"
    else:
        rating = "Poor"

    return {
        'score': score,
        'rating': rating,
        'details': details
    }


def format_repo_response(repo_data: Dict[str, Any], file_analysis: Dict[str, Any]) -> str:
    """Format repository analysis into readable message."""
    if "error" in repo_data:
        return f"❌ Error: {repo_data['error']}"

    response = f"# 📦 Repository: {repo_data['full_name']}\n\n"

    response += f"**Description:** {repo_data.get('description', 'No description')}\n\n"

    response += f"📊 **Stats:**\n"
    response += f"- ⭐ Stars: {repo_data.get('stars', 0)}\n"
    response += f"- 🍴 Forks: {repo_data.get('forks', 0)}\n"
    response += f"- 🐛 Open Issues: {repo_data.get('open_issues', 0)}\n"
    response += f"- 📁 Files: {file_analysis.get('file_count', 0)}\n"
    response += f"- 💾 Size: {repo_data.get('size', 0)} KB\n\n"

    # Languages
    if repo_data.get('languages'):
        response += f"💻 **Languages:**\n"
        total_bytes = sum(repo_data['languages'].values())
        sorted_langs = sorted(repo_data['languages'].items(), key=lambda x: x[1], reverse=True)
        for lang, bytes_count in sorted_langs[:5]:
            percentage = (bytes_count / total_bytes * 100) if total_bytes > 0 else 0
            response += f"- {lang}: {percentage:.1f}%\n"
        response += "\n"

    # MeTTa insights
    insights = repo_data.get('metta_insights', {})

    if insights.get('complexity_tier'):
        response += f"🔧 **Complexity:** {insights['complexity_tier'].replace('-', ' ').title()}\n"

    if insights.get('difficulty_tier'):
        response += f"🎯 **Difficulty:** {insights['difficulty_tier'].title()}\n"

    if insights.get('project_type'):
        response += f"🏗️ **Project Type:** {insights['project_type'].replace('-', ' ').title()}\n\n"

    if insights.get('tech_domains'):
        response += f"🧠 **Tech Domains:**\n"
        for domain in insights['tech_domains']:
            response += f"- {domain.replace('-', ' ').title()}\n"
        response += "\n"

    # Documentation score
    if insights.get('documentation'):
        doc = insights['documentation']
        doc_emoji = "📚" if doc['rating'] == "Excellent" else "📖" if doc['rating'] == "Good" else "📝" if doc['rating'] == "Fair" else "📄"
        response += f"{doc_emoji} **Documentation:** {doc['rating']} ({doc['score']}/100)\n"

        # Show key details
        details = doc.get('details', {})
        if details.get('readme', {}).get('exists'):
            response += f"  ✅ README ({details['readme'].get('size_kb', 0)} KB)\n"
        else:
            response += f"  ❌ No README\n"

        if details.get('license', {}).get('exists'):
            response += f"  ✅ LICENSE\n"
        else:
            response += f"  ❌ No LICENSE\n"

        if details.get('contributing', {}).get('exists'):
            response += f"  ✅ CONTRIBUTING.md\n"

        if details.get('docs_folder', {}).get('exists'):
            response += f"  ✅ /docs/ folder\n"

        response += "\n"

    # File structure
    if file_analysis.get('extensions'):
        response += f"📂 **File Types:**\n"
        sorted_exts = sorted(file_analysis['extensions'].items(), key=lambda x: x[1], reverse=True)
        for ext, count in sorted_exts[:5]:
            response += f"- .{ext}: {count} files\n"
        response += "\n"

    # MeTTa reasoning
    if insights.get('reasoning'):
        response += "🧠 **MeTTa Reasoning:**\n"
        for reason in insights['reasoning']:
            response += f"- {reason}\n"
        response += "\n"

    response += f"🔗 [View Repository]({repo_data.get('repo_url', '')})\n\n"
    response += f"_🔬 Analysis powered by MeTTa reasoning engine_"

    return response
