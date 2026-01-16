"""
OSV.dev API Client

Queries OSV.dev (Open Source Vulnerabilities) database for security advisories.
API Docs: https://google.github.io/osv.dev/api/
"""

import requests
from typing import List, Dict


async def check_vulnerabilities(dependencies: List[Dict]) -> List[Dict]:
    """
    Check dependencies for vulnerabilities using OSV.dev API.

    Args:
        dependencies: List of {package, version, ecosystem}

    Returns:
        List of vulnerabilities with details
    """
    vulnerabilities = []

    for dep in dependencies[:50]:  # Limit to 50 to avoid rate limits
        try:
            vulns = await query_osv(dep['package'], dep['version'], dep['ecosystem'])
            vulnerabilities.extend(vulns)
        except Exception as e:
            print(f"Error checking {dep['package']}: {e}")
            continue

    return vulnerabilities


async def query_osv(package: str, version: str, ecosystem: str) -> List[Dict]:
    """
    Query OSV.dev API for a specific package/version.

    Args:
        package: Package name
        version: Package version
        ecosystem: npm, PyPI, Go, crates.io, etc.

    Returns:
        List of vulnerability details
    """
    try:
        response = requests.post(
            "https://api.osv.dev/v1/query",
            json={
                "package": {
                    "name": package,
                    "ecosystem": ecosystem
                },
                "version": version
            },
            timeout=10
        )

        if response.status_code != 200:
            return []

        data = response.json()
        vulns = data.get('vulns', [])

        results = []

        for vuln in vulns:
            # Extract severity
            severity = "UNKNOWN"
            if 'severity' in vuln:
                if isinstance(vuln['severity'], list) and len(vuln['severity']) > 0:
                    severity = vuln['severity'][0].get('type', 'UNKNOWN')
            elif 'database_specific' in vuln:
                severity = vuln.get('database_specific', {}).get('severity', 'UNKNOWN')

            # Try to find fixed version
            fixed_version = None
            if 'affected' in vuln:
                for affected in vuln['affected']:
                    if 'ranges' in affected:
                        for range_info in affected['ranges']:
                            if 'events' in range_info:
                                for event in range_info['events']:
                                    if 'fixed' in event:
                                        fixed_version = event['fixed']
                                        break

            results.append({
                'package': package,
                'version': version,
                'id': vuln.get('id', 'UNKNOWN'),
                'severity': severity.upper(),
                'description': vuln.get('summary', vuln.get('details', 'No description')[:200]),
                'fixed_version': fixed_version
            })

        return results

    except Exception as e:
        print(f"OSV API error for {package}: {e}")
        return []
