# knowledge.py - MeTTa Knowledge Base for Skill Matching
from hyperon import MeTTa, E, S, ValueAtom

def initialize_skill_knowledge_graph(metta: MeTTa):
    """Initialize MeTTa knowledge graph for intelligent skill matching."""
    
    # Language → Domain mapping (expanded)
    metta.space().add_atom(E(S("language-domain"), S("Python"), ValueAtom("backend-data-science")))
    metta.space().add_atom(E(S("language-domain"), S("JavaScript"), ValueAtom("frontend-fullstack")))
    metta.space().add_atom(E(S("language-domain"), S("TypeScript"), ValueAtom("frontend-fullstack")))
    metta.space().add_atom(E(S("language-domain"), S("React"), ValueAtom("frontend-ui")))
    metta.space().add_atom(E(S("language-domain"), S("Vue"), ValueAtom("frontend-ui")))
    metta.space().add_atom(E(S("language-domain"), S("Angular"), ValueAtom("frontend-ui")))
    metta.space().add_atom(E(S("language-domain"), S("Node.js"), ValueAtom("backend-web")))
    metta.space().add_atom(E(S("language-domain"), S("Express"), ValueAtom("backend-web")))
    metta.space().add_atom(E(S("language-domain"), S("FastAPI"), ValueAtom("backend-api")))
    metta.space().add_atom(E(S("language-domain"), S("Django"), ValueAtom("backend-web")))
    metta.space().add_atom(E(S("language-domain"), S("Flask"), ValueAtom("backend-api")))
    metta.space().add_atom(E(S("language-domain"), S("Go"), ValueAtom("backend-systems")))
    metta.space().add_atom(E(S("language-domain"), S("Rust"), ValueAtom("systems-performance")))
    metta.space().add_atom(E(S("language-domain"), S("Java"), ValueAtom("backend-enterprise")))
    metta.space().add_atom(E(S("language-domain"), S("C++"), ValueAtom("systems-performance")))
    metta.space().add_atom(E(S("language-domain"), S("C#"), ValueAtom("backend-enterprise")))
    metta.space().add_atom(E(S("language-domain"), S("Ruby"), ValueAtom("backend-web")))
    metta.space().add_atom(E(S("language-domain"), S("PHP"), ValueAtom("backend-web")))
    metta.space().add_atom(E(S("language-domain"), S("Swift"), ValueAtom("mobile-ios")))
    metta.space().add_atom(E(S("language-domain"), S("Kotlin"), ValueAtom("mobile-android")))
    
    # Skill relationships (prerequisites and alternatives)
    metta.space().add_atom(E(S("skill-prerequisite"), S("React"), S("JavaScript")))
    metta.space().add_atom(E(S("skill-prerequisite"), S("Vue"), S("JavaScript")))
    metta.space().add_atom(E(S("skill-prerequisite"), S("Angular"), S("TypeScript")))
    metta.space().add_atom(E(S("skill-prerequisite"), S("Express"), S("Node.js")))
    metta.space().add_atom(E(S("skill-prerequisite"), S("FastAPI"), S("Python")))
    metta.space().add_atom(E(S("skill-prerequisite"), S("Django"), S("Python")))
    metta.space().add_atom(E(S("skill-prerequisite"), S("Flask"), S("Python")))
    
    # Skill alternatives (similar skills)
    metta.space().add_atom(E(S("skill-alternative"), S("React"), S("Vue")))
    metta.space().add_atom(E(S("skill-alternative"), S("Vue"), S("React")))
    metta.space().add_atom(E(S("skill-alternative"), S("Express"), S("FastAPI")))
    metta.space().add_atom(E(S("skill-alternative"), S("FastAPI"), S("Express")))
    metta.space().add_atom(E(S("skill-alternative"), S("Django"), S("Flask")))
    metta.space().add_atom(E(S("skill-alternative"), S("Flask"), S("Django")))
    
    # Difficulty levels for skills
    metta.space().add_atom(E(S("skill-difficulty"), S("JavaScript"), ValueAtom("beginner")))
    metta.space().add_atom(E(S("skill-difficulty"), S("Python"), ValueAtom("beginner")))
    metta.space().add_atom(E(S("skill-difficulty"), S("HTML"), ValueAtom("beginner")))
    metta.space().add_atom(E(S("skill-difficulty"), S("CSS"), ValueAtom("beginner")))
    metta.space().add_atom(E(S("skill-difficulty"), S("React"), ValueAtom("intermediate")))
    metta.space().add_atom(E(S("skill-difficulty"), S("Vue"), ValueAtom("intermediate")))
    metta.space().add_atom(E(S("skill-difficulty"), S("Node.js"), ValueAtom("intermediate")))
    metta.space().add_atom(E(S("skill-difficulty"), S("TypeScript"), ValueAtom("intermediate")))
    metta.space().add_atom(E(S("skill-difficulty"), S("Go"), ValueAtom("advanced")))
    metta.space().add_atom(E(S("skill-difficulty"), S("Rust"), ValueAtom("advanced")))
    metta.space().add_atom(E(S("skill-difficulty"), S("C++"), ValueAtom("advanced")))
    
    # Match confidence thresholds
    metta.space().add_atom(E(S("match-threshold"), S("exact"), ValueAtom(100)))
    metta.space().add_atom(E(S("match-threshold"), S("related"), ValueAtom(70)))
    metta.space().add_atom(E(S("match-threshold"), S("domain"), ValueAtom(50)))
    metta.space().add_atom(E(S("match-threshold"), S("prerequisite"), ValueAtom(30)))
    
    return metta
