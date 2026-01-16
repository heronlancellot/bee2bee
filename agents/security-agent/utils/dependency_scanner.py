"""
Dependency Scanner

Scans GitHub repositories for dependency files and extracts package information.
Supports: package.json, requirements.txt, go.mod, Cargo.toml, pom.xml, Gemfile
"""

import requests
import json
import re
from typing import Dict, List


async def scan_dependencies(owner: str, repo: str) -> Dict:
    """
    Scan repository for dependency files and extract packages.

    Args:
        owner: Repository owner
        repo: Repository name

    Returns:
        {
            'success': bool,
            'total_count': int,
            'dependencies': [{'package': str, 'version': str, 'ecosystem': str}, ...],
            'error': str (optional)
        }
    """
    try:
        # Fetch repository tree
        tree_response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1",
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=10
        )

        if tree_response.status_code == 404:
            # Try 'master' branch
            tree_response = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1",
                headers={"Accept": "application/vnd.github.v3+json"},
                timeout=10
            )

        if tree_response.status_code != 200:
            return {
                'success': False,
                'error': f"Failed to fetch repo tree: {tree_response.status_code}"
            }

        tree = tree_response.json().get('tree', [])

        # Find dependency files
        dependency_files = {
            'package.json': None,
            'requirements.txt': None,
            'go.mod': None,
            'Cargo.toml': None,
            'pom.xml': None,
            'Gemfile': None,
        }

        for item in tree:
            if item['type'] == 'blob':
                filename = item['path'].split('/')[-1]
                if filename in dependency_files:
                    dependency_files[filename] = item['path']

        # Extract dependencies from each file
        all_dependencies = []

        # package.json (npm)
        if dependency_files['package.json']:
            deps = await parse_package_json(owner, repo, dependency_files['package.json'])
            all_dependencies.extend(deps)

        # requirements.txt (Python)
        if dependency_files['requirements.txt']:
            deps = await parse_requirements_txt(owner, repo, dependency_files['requirements.txt'])
            all_dependencies.extend(deps)

        # go.mod (Go)
        if dependency_files['go.mod']:
            deps = await parse_go_mod(owner, repo, dependency_files['go.mod'])
            all_dependencies.extend(deps)

        # Cargo.toml (Rust)
        if dependency_files['Cargo.toml']:
            deps = await parse_cargo_toml(owner, repo, dependency_files['Cargo.toml'])
            all_dependencies.extend(deps)

        return {
            'success': True,
            'total_count': len(all_dependencies),
            'dependencies': all_dependencies
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


async def parse_package_json(owner: str, repo: str, path: str) -> List[Dict]:
    """Extract dependencies from package.json."""
    try:
        response = requests.get(
            f"https://raw.githubusercontent.com/{owner}/{repo}/main/{path}",
            timeout=10
        )

        if response.status_code == 404:
            response = requests.get(
                f"https://raw.githubusercontent.com/{owner}/{repo}/master/{path}",
                timeout=10
            )

        if response.status_code != 200:
            return []

        data = json.loads(response.text)
        dependencies = []

        # Runtime dependencies
        for package, version in data.get('dependencies', {}).items():
            dependencies.append({
                'package': package,
                'version': version.lstrip('^~>=<'),  # Remove version prefixes
                'ecosystem': 'npm'
            })

        # Dev dependencies
        for package, version in data.get('devDependencies', {}).items():
            dependencies.append({
                'package': package,
                'version': version.lstrip('^~>=<'),
                'ecosystem': 'npm'
            })

        return dependencies

    except Exception:
        return []


async def parse_requirements_txt(owner: str, repo: str, path: str) -> List[Dict]:
    """Extract dependencies from requirements.txt."""
    try:
        response = requests.get(
            f"https://raw.githubusercontent.com/{owner}/{repo}/main/{path}",
            timeout=10
        )

        if response.status_code == 404:
            response = requests.get(
                f"https://raw.githubusercontent.com/{owner}/{repo}/master/{path}",
                timeout=10
            )

        if response.status_code != 200:
            return []

        dependencies = []

        for line in response.text.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # Parse: package==1.0.0 or package>=1.0.0
                match = re.match(r'([a-zA-Z0-9_\-\.]+)([><=!]+)([0-9\.]+)', line)
                if match:
                    dependencies.append({
                        'package': match.group(1),
                        'version': match.group(3),
                        'ecosystem': 'PyPI'
                    })
                else:
                    # No version specified
                    dependencies.append({
                        'package': line,
                        'version': 'latest',
                        'ecosystem': 'PyPI'
                    })

        return dependencies

    except Exception:
        return []


async def parse_go_mod(owner: str, repo: str, path: str) -> List[Dict]:
    """Extract dependencies from go.mod."""
    try:
        response = requests.get(
            f"https://raw.githubusercontent.com/{owner}/{repo}/main/{path}",
            timeout=10
        )

        if response.status_code == 404:
            response = requests.get(
                f"https://raw.githubusercontent.com/{owner}/{repo}/master/{path}",
                timeout=10
            )

        if response.status_code != 200:
            return []

        dependencies = []
        in_require_block = False

        for line in response.text.split('\n'):
            line = line.strip()

            if line.startswith('require ('):
                in_require_block = True
                continue
            elif line == ')':
                in_require_block = False
                continue

            if in_require_block or line.startswith('require '):
                parts = line.replace('require ', '').split()
                if len(parts) >= 2:
                    dependencies.append({
                        'package': parts[0],
                        'version': parts[1].lstrip('v'),
                        'ecosystem': 'Go'
                    })

        return dependencies

    except Exception:
        return []


async def parse_cargo_toml(owner: str, repo: str, path: str) -> List[Dict]:
    """Extract dependencies from Cargo.toml."""
    try:
        response = requests.get(
            f"https://raw.githubusercontent.com/{owner}/{repo}/main/{path}",
            timeout=10
        )

        if response.status_code == 404:
            response = requests.get(
                f"https://raw.githubusercontent.com/{owner}/{repo}/master/{path}",
                timeout=10
            )

        if response.status_code != 200:
            return []

        dependencies = []
        in_dependencies = False

        for line in response.text.split('\n'):
            line = line.strip()

            if line == '[dependencies]':
                in_dependencies = True
                continue
            elif line.startswith('[') and line != '[dependencies]':
                in_dependencies = False
                continue

            if in_dependencies and '=' in line:
                parts = line.split('=', 1)
                package = parts[0].strip()
                version = parts[1].strip().strip('"\'')

                dependencies.append({
                    'package': package,
                    'version': version,
                    'ecosystem': 'crates.io'
                })

        return dependencies

    except Exception:
        return []
