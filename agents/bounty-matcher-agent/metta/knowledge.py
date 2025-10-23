# knowledge.py
"""
MeTTa Knowledge Graph for Bounty Matching
Defines rules for matching developers with bounties/issues
"""

from hyperon import MeTTa, E, S, ValueAtom


def initialize_bounty_knowledge(metta: MeTTa):
    """Initialize the MeTTa knowledge graph with bounty matching rules."""

    # Skill level thresholds (years of experience)
    metta.space().add_atom(E(S("skill-level"), S("beginner"), ValueAtom(0)))
    metta.space().add_atom(E(S("skill-level"), S("intermediate"), ValueAtom(1)))
    metta.space().add_atom(E(S("skill-level"), S("advanced"), ValueAtom(3)))
    metta.space().add_atom(E(S("skill-level"), S("expert"), ValueAtom(5)))

    # Bounty value tiers (in USD)
    metta.space().add_atom(E(S("bounty-tier"), S("micro"), ValueAtom(10)))
    metta.space().add_atom(E(S("bounty-tier"), S("small"), ValueAtom(50)))
    metta.space().add_atom(E(S("bounty-tier"), S("medium"), ValueAtom(200)))
    metta.space().add_atom(E(S("bounty-tier"), S("large"), ValueAtom(500)))
    metta.space().add_atom(E(S("bounty-tier"), S("xlarge"), ValueAtom(1000)))

    # Complexity scores (0-10 scale)
    metta.space().add_atom(E(S("complexity-level"), S("trivial"), ValueAtom(1)))
    metta.space().add_atom(E(S("complexity-level"), S("easy"), ValueAtom(3)))
    metta.space().add_atom(E(S("complexity-level"), S("moderate"), ValueAtom(5)))
    metta.space().add_atom(E(S("complexity-level"), S("hard"), ValueAtom(7)))
    metta.space().add_atom(E(S("complexity-level"), S("very-hard"), ValueAtom(9)))

    # Time estimates (hours)
    metta.space().add_atom(E(S("time-estimate"), S("quick"), ValueAtom(2)))
    metta.space().add_atom(E(S("time-estimate"), S("short"), ValueAtom(8)))
    metta.space().add_atom(E(S("time-estimate"), S("medium"), ValueAtom(20)))
    metta.space().add_atom(E(S("time-estimate"), S("long"), ValueAtom(40)))
    metta.space().add_atom(E(S("time-estimate"), S("very-long"), ValueAtom(80)))

    # Language → Skill domain mapping
    metta.space().add_atom(E(S("language-skill"), S("Python"), ValueAtom("backend-scripting")))
    metta.space().add_atom(E(S("language-skill"), S("JavaScript"), ValueAtom("frontend-web")))
    metta.space().add_atom(E(S("language-skill"), S("TypeScript"), ValueAtom("frontend-web")))
    metta.space().add_atom(E(S("language-skill"), S("Java"), ValueAtom("backend-enterprise")))
    metta.space().add_atom(E(S("language-skill"), S("Go"), ValueAtom("backend-systems")))
    metta.space().add_atom(E(S("language-skill"), S("Rust"), ValueAtom("systems-programming")))
    metta.space().add_atom(E(S("language-skill"), S("C++"), ValueAtom("systems-programming")))
    metta.space().add_atom(E(S("language-skill"), S("C#"), ValueAtom("backend-enterprise")))
    metta.space().add_atom(E(S("language-skill"), S("Ruby"), ValueAtom("backend-web")))
    metta.space().add_atom(E(S("language-skill"), S("PHP"), ValueAtom("backend-web")))
    metta.space().add_atom(E(S("language-skill"), S("Swift"), ValueAtom("mobile-ios")))
    metta.space().add_atom(E(S("language-skill"), S("Kotlin"), ValueAtom("mobile-android")))
    metta.space().add_atom(E(S("language-skill"), S("Solidity"), ValueAtom("blockchain-smart-contracts")))

    # Issue type → Skill requirements
    metta.space().add_atom(E(S("issue-type-skill"), S("bug-fix"), ValueAtom("debugging")))
    metta.space().add_atom(E(S("issue-type-skill"), S("feature"), ValueAtom("development")))
    metta.space().add_atom(E(S("issue-type-skill"), S("documentation"), ValueAtom("writing")))
    metta.space().add_atom(E(S("issue-type-skill"), S("refactoring"), ValueAtom("architecture")))
    metta.space().add_atom(E(S("issue-type-skill"), S("performance"), ValueAtom("optimization")))
    metta.space().add_atom(E(S("issue-type-skill"), S("security"), ValueAtom("security-audit")))
    metta.space().add_atom(E(S("issue-type-skill"), S("testing"), ValueAtom("qa-testing")))

    # Match confidence thresholds
    metta.space().add_atom(E(S("confidence-level"), S("low"), ValueAtom(30)))
    metta.space().add_atom(E(S("confidence-level"), S("medium"), ValueAtom(60)))
    metta.space().add_atom(E(S("confidence-level"), S("high"), ValueAtom(80)))
    metta.space().add_atom(E(S("confidence-level"), S("perfect"), ValueAtom(95)))

    # Repository size preferences
    metta.space().add_atom(E(S("repo-size"), S("tiny"), ValueAtom(100)))
    metta.space().add_atom(E(S("repo-size"), S("small"), ValueAtom(500)))
    metta.space().add_atom(E(S("repo-size"), S("medium"), ValueAtom(2000)))
    metta.space().add_atom(E(S("repo-size"), S("large"), ValueAtom(10000)))
    metta.space().add_atom(E(S("repo-size"), S("huge"), ValueAtom(50000)))

    return metta
