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

        # Fetch contributors (first page only - 30 contributors max to avoid rate limits)
        contributors_response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/contributors?per_page=30",
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=10
        )

        contributors_data = contributors_response.json() if contributors_response.status_code == 200 else []
        contributors_count = len(contributors_data) if isinstance(contributors_data, list) else 0

        # Fetch commit activity (last 52 weeks)
        participation_response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/stats/participation",
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=10
        )

        participation_data = participation_response.json() if participation_response.status_code == 200 else {}

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
            "repo_url": repo_data['html_url'],
            "contributors_count": contributors_count,
            "commit_activity": participation_data.get('all', [])  # Commits per week (52 weeks)
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
        "test_coverage": None,
        "complexity_score": None,
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

        # Test coverage analysis
        test_analysis = analyze_tests(tree)
        insights["test_coverage"] = test_analysis
        insights["reasoning"].append(f"Test Coverage: {test_analysis['coverage_rating']} ({test_analysis['test_file_count']} test files, {test_analysis['test_ratio']:.1%} ratio)")

        # Calculate weighted complexity score
        complexity_result = calculate_complexity_score(
            loc=estimated_loc,
            file_count=file_count,
            test_analysis=test_analysis,
            doc_analysis=doc_analysis,
            contributors_count=repo_data.get('contributors_count', 0),
            commit_activity=repo_data.get('commit_activity', [])
        )

        insights["complexity_score"] = complexity_result
        insights["difficulty_tier"] = complexity_result['tier']

        # Add reasoning about contributors
        contributors_count = repo_data.get('contributors_count', 0)
        commit_activity = repo_data.get('commit_activity', [])

        if contributors_count > 0 or commit_activity:
            contributor_info = f"Contributors: {contributors_count} developers"
            if commit_activity and len(commit_activity) >= 12:
                recent_commits = commit_activity[-12:]
                avg_commits = sum(recent_commits) / 12
                contributor_info += f", {avg_commits:.1f} commits/week avg"
            insights["reasoning"].append(contributor_info)

        insights["reasoning"].append(f"Final Complexity Score: {complexity_result['final_score']}/100 ({complexity_result['tier'].title()})")

        return insights

    except Exception as e:
        print(f"MeTTa analysis error: {e}")
        return insights


def calculate_complexity_score(
    loc: int,
    file_count: int,
    test_analysis: Dict,
    doc_analysis: Dict,
    contributors_count: int,
    commit_activity: List[int]
) -> Dict[str, Any]:
    """
    Calculate weighted complexity score (0-100) based on multiple factors.

    Formula:
    - LOC: 30%
    - File count: 25%
    - Tests: 20%
    - Docs: 15%
    - Contributors: 10%

    Returns dict with score, breakdown, and tier classification.
    """

    # 1. LOC Score (0-100) - 30% weight
    # Thresholds: 0-1k (beginner), 1k-10k (intermediate), 10k-50k (advanced), 50k+ (expert)
    if loc < 1000:
        loc_score = (loc / 1000) * 30  # 0-30 points
    elif loc < 10000:
        loc_score = 30 + ((loc - 1000) / 9000) * 30  # 30-60 points
    elif loc < 50000:
        loc_score = 60 + ((loc - 10000) / 40000) * 25  # 60-85 points
    else:
        loc_score = 85 + min(((loc - 50000) / 50000) * 15, 15)  # 85-100 points

    # 2. File Count Score (0-100) - 25% weight
    # Thresholds: 0-50 (small), 50-200 (medium), 200-1000 (large), 1000+ (very large)
    if file_count < 50:
        file_score = (file_count / 50) * 30
    elif file_count < 200:
        file_score = 30 + ((file_count - 50) / 150) * 30
    elif file_count < 1000:
        file_score = 60 + ((file_count - 200) / 800) * 25
    else:
        file_score = 85 + min(((file_count - 1000) / 1000) * 15, 15)

    # 3. Test Score (0-100) - 20% weight
    test_score = test_analysis.get('coverage_score', 0) if test_analysis else 0

    # 4. Documentation Score (0-100) - 15% weight
    doc_score = doc_analysis.get('score', 0) if doc_analysis else 0

    # 5. Contributor Score (0-100) - 10% weight
    # Based on: contributor count + commit activity (last 12 weeks avg)
    contributor_score = 0

    # Contributor count (0-50 points)
    if contributors_count >= 100:
        contributor_score += 50
    elif contributors_count >= 50:
        contributor_score += 40
    elif contributors_count >= 20:
        contributor_score += 30
    elif contributors_count >= 10:
        contributor_score += 20
    elif contributors_count >= 5:
        contributor_score += 10
    elif contributors_count > 0:
        contributor_score += 5

    # Commit activity (0-50 points) - average commits per week in last 12 weeks
    if commit_activity and len(commit_activity) >= 12:
        recent_commits = commit_activity[-12:]  # Last 12 weeks
        avg_commits_per_week = sum(recent_commits) / 12

        if avg_commits_per_week >= 50:
            contributor_score += 50
        elif avg_commits_per_week >= 20:
            contributor_score += 40
        elif avg_commits_per_week >= 10:
            contributor_score += 30
        elif avg_commits_per_week >= 5:
            contributor_score += 20
        elif avg_commits_per_week >= 1:
            contributor_score += 10
        elif avg_commits_per_week > 0:
            contributor_score += 5

    contributor_score = min(contributor_score, 100)  # Cap at 100

    # Calculate weighted total
    final_score = (
        loc_score * 0.30 +
        file_score * 0.25 +
        test_score * 0.20 +
        doc_score * 0.15 +
        contributor_score * 0.10
    )

    final_score = min(100, max(0, int(final_score)))  # Clamp to 0-100

    # Determine tier
    if final_score >= 85:
        tier = "expert"
    elif final_score >= 60:
        tier = "advanced"
    elif final_score >= 30:
        tier = "intermediate"
    else:
        tier = "beginner"

    return {
        'final_score': final_score,
        'tier': tier,
        'breakdown': {
            'loc_score': round(loc_score, 1),
            'file_score': round(file_score, 1),
            'test_score': round(test_score, 1),
            'doc_score': round(doc_score, 1),
            'contributor_score': round(contributor_score, 1),
        },
        'weights': {
            'loc': 0.30,
            'files': 0.25,
            'tests': 0.20,
            'docs': 0.15,
            'contributors': 0.10,
        }
    }


def analyze_tests(tree: List[Dict]) -> Dict[str, Any]:
    """
    Analyze test coverage and quality.

    Detects:
    - Test file patterns (*.test.*, *.spec.*, /test/, /tests/)
    - Test frameworks (pytest, jest, junit, mocha, etc)
    - CI/CD configs (.github/workflows, .gitlab-ci.yml)
    - Test ratio (test_files / code_files)
    """
    test_files = []
    code_files = []
    frameworks = set()
    ci_configs = []

    # Test file patterns
    test_patterns = {
        'name_patterns': [
            'test_',      # test_*.py
            '_test.',     # *_test.py, *_test.go
            '.test.',     # *.test.js, *.test.ts
            '.spec.',     # *.spec.js, *.spec.ts
            'Test.java',  # *Test.java
            'Tests.java', # *Tests.java
        ],
        'dir_patterns': [
            '/test/',
            '/tests/',
            '/__tests__/',
            '/spec/',
            '/e2e/',
        ]
    }

    # Framework detection patterns
    framework_files = {
        'pytest': ['pytest.ini', 'pyproject.toml', 'conftest.py'],
        'unittest': [],  # Python builtin
        'jest': ['jest.config.js', 'jest.config.ts', 'jest.config.json'],
        'mocha': ['.mocharc.js', '.mocharc.json', 'mocha.opts'],
        'vitest': ['vitest.config.ts', 'vitest.config.js'],
        'junit': ['pom.xml'],
        'go test': ['go.mod'],
        'cargo test': ['Cargo.toml'],
        'rspec': ['.rspec'],
        'phpunit': ['phpunit.xml'],
    }

    # CI/CD patterns
    ci_patterns = [
        '.github/workflows/',
        '.gitlab-ci.yml',
        '.circleci/config.yml',
        '.travis.yml',
        'Jenkinsfile',
        'azure-pipelines.yml',
    ]

    # Analyze tree
    for item in tree:
        if item['type'] == 'blob':
            path = item['path'].lower()
            name = path.split('/')[-1]

            # Check if it's a test file
            is_test = False
            for pattern in test_patterns['name_patterns']:
                if pattern in name:
                    is_test = True
                    break

            if not is_test:
                for pattern in test_patterns['dir_patterns']:
                    if pattern in path:
                        is_test = True
                        break

            if is_test:
                test_files.append(item)
            else:
                # Check if it's a code file (not config/docs)
                ext = name.split('.')[-1] if '.' in name else ''
                code_extensions = ['py', 'js', 'ts', 'jsx', 'tsx', 'go', 'rs', 'java', 'kt',
                                 'swift', 'c', 'cpp', 'h', 'hpp', 'rb', 'php', 'cs', 'sol', 'vy']
                if ext in code_extensions:
                    code_files.append(item)

            # Check for framework config files
            for framework, config_files in framework_files.items():
                if any(config_file in path for config_file in config_files):
                    frameworks.add(framework)

            # Check for CI/CD
            for ci_pattern in ci_patterns:
                if ci_pattern in path:
                    ci_configs.append(item['path'])

    # Calculate metrics
    test_count = len(test_files)
    code_count = len(code_files)
    test_ratio = test_count / code_count if code_count > 0 else 0

    # Calculate coverage score (0-100)
    score = 0

    # Test ratio (0-50 points)
    if test_ratio >= 0.5:
        score += 50
    elif test_ratio >= 0.3:
        score += 40
    elif test_ratio >= 0.2:
        score += 30
    elif test_ratio >= 0.1:
        score += 20
    else:
        score += int(test_ratio * 100)

    # Has tests (0-30 points)
    if test_count > 0:
        if test_count >= 50:
            score += 30
        elif test_count >= 20:
            score += 20
        elif test_count >= 10:
            score += 15
        else:
            score += 10

    # CI/CD (0-20 points)
    if len(ci_configs) > 0:
        score += 20

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
        'test_file_count': test_count,
        'code_file_count': code_count,
        'test_ratio': round(test_ratio, 3),
        'coverage_score': score,
        'coverage_rating': rating,
        'test_frameworks': sorted(list(frameworks)) if frameworks else [],
        'has_ci': len(ci_configs) > 0,
        'ci_configs': ci_configs,
    }


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
    response += f"- 💾 Size: {repo_data.get('size', 0)} KB\n"

    # Contributors info
    contributors_count = repo_data.get('contributors_count', 0)
    commit_activity = repo_data.get('commit_activity', [])

    if contributors_count > 0:
        response += f"- 👥 Contributors: {contributors_count}\n"

    if commit_activity and len(commit_activity) >= 12:
        recent_commits = commit_activity[-12:]  # Last 12 weeks
        avg_commits = sum(recent_commits) / 12
        total_commits_last_12w = sum(recent_commits)
        response += f"- 📈 Recent Activity: {total_commits_last_12w} commits (last 12 weeks, avg {avg_commits:.1f}/week)\n"

    response += "\n"

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

    # Complexity Score (NEW - weighted)
    if insights.get('complexity_score'):
        complexity = insights['complexity_score']
        tier_emoji = "🔥" if complexity['tier'] == "expert" else "⚡" if complexity['tier'] == "advanced" else "⭐" if complexity['tier'] == "intermediate" else "🌱"

        response += f"\n{tier_emoji} **Overall Complexity: {complexity['final_score']}/100** ({complexity['tier'].title()})\n"
        response += f"  📊 **Score Breakdown:**\n"
        breakdown = complexity['breakdown']
        response += f"    • LOC: {breakdown['loc_score']:.1f}/100 (30% weight)\n"
        response += f"    • Files: {breakdown['file_score']:.1f}/100 (25% weight)\n"
        response += f"    • Tests: {breakdown['test_score']:.1f}/100 (20% weight)\n"
        response += f"    • Docs: {breakdown['doc_score']:.1f}/100 (15% weight)\n"
        response += f"    • Contributors: {breakdown['contributor_score']:.1f}/100 (10% weight)\n\n"

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

    # Test coverage
    if insights.get('test_coverage'):
        test = insights['test_coverage']
        test_emoji = "🧪" if test['coverage_rating'] == "Excellent" else "🔬" if test['coverage_rating'] == "Good" else "⚗️" if test['coverage_rating'] == "Fair" else "🧫"
        response += f"{test_emoji} **Test Coverage:** {test['coverage_rating']} ({test['coverage_score']}/100)\n"

        response += f"  📊 Test Ratio: {test['test_ratio']:.1%} ({test['test_file_count']} test files / {test['code_file_count']} code files)\n"

        if test.get('test_frameworks'):
            response += f"  🛠️ Frameworks: {', '.join(test['test_frameworks'])}\n"

        if test.get('has_ci'):
            ci_count = len(test.get('ci_configs', []))
            response += f"  ✅ CI/CD: {ci_count} configuration(s) found\n"
        else:
            response += f"  ❌ No CI/CD detected\n"

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
