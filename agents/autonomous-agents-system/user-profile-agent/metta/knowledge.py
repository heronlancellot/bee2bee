# knowledge.py - MeTTa Knowledge Base for User Profile Analysis
from hyperon import MeTTa, E, S, ValueAtom

def initialize_profile_knowledge_graph(metta: MeTTa):
    """Initialize MeTTa knowledge graph for intelligent user profile analysis."""

    # Experience level thresholds
    metta.space().add_atom(E(S("experience-level"), ValueAtom(0), ValueAtom("beginner")))
    metta.space().add_atom(E(S("experience-level"), ValueAtom(1), ValueAtom("beginner")))
    metta.space().add_atom(E(S("experience-level"), ValueAtom(2), ValueAtom("intermediate")))
    metta.space().add_atom(E(S("experience-level"), ValueAtom(3), ValueAtom("intermediate")))
    metta.space().add_atom(E(S("experience-level"), ValueAtom(4), ValueAtom("intermediate")))
    metta.space().add_atom(E(S("experience-level"), ValueAtom(5), ValueAtom("advanced")))
    metta.space().add_atom(E(S("experience-level"), ValueAtom(7), ValueAtom("advanced")))
    metta.space().add_atom(E(S("experience-level"), ValueAtom(10), ValueAtom("expert")))

    # Skill proficiency levels
    metta.space().add_atom(E(S("proficiency-level"), ValueAtom(1), ValueAtom("novice")))
    metta.space().add_atom(E(S("proficiency-level"), ValueAtom(3), ValueAtom("intermediate")))
    metta.space().add_atom(E(S("proficiency-level"), ValueAtom(5), ValueAtom("proficient")))
    metta.space().add_atom(E(S("proficiency-level"), ValueAtom(7), ValueAtom("expert")))
    metta.space().add_atom(E(S("proficiency-level"), ValueAtom(10), ValueAtom("master")))

    # Career path recommendations based on skills
    metta.space().add_atom(E(S("career-path"), S("Python"), ValueAtom("backend-developer")))
    metta.space().add_atom(E(S("career-path"), S("JavaScript"), ValueAtom("frontend-developer")))
    metta.space().add_atom(E(S("career-path"), S("React"), ValueAtom("frontend-developer")))
    metta.space().add_atom(E(S("career-path"), S("Node.js"), ValueAtom("fullstack-developer")))
    metta.space().add_atom(E(S("career-path"), S("Go"), ValueAtom("systems-engineer")))
    metta.space().add_atom(E(S("career-path"), S("Rust"), ValueAtom("systems-engineer")))
    metta.space().add_atom(E(S("career-path"), S("Java"), ValueAtom("enterprise-developer")))
    metta.space().add_atom(E(S("career-path"), S("Swift"), ValueAtom("mobile-developer")))
    metta.space().add_atom(E(S("career-path"), S("Kotlin"), ValueAtom("mobile-developer")))

    # Skill complementarity (what skills work well together)
    metta.space().add_atom(E(S("skill-complement"), S("Python"), S("FastAPI")))
    metta.space().add_atom(E(S("skill-complement"), S("Python"), S("Django")))
    metta.space().add_atom(E(S("skill-complement"), S("JavaScript"), S("React")))
    metta.space().add_atom(E(S("skill-complement"), S("JavaScript"), S("Node.js")))
    metta.space().add_atom(E(S("skill-complement"), S("TypeScript"), S("React")))
    metta.space().add_atom(E(S("skill-complement"), S("TypeScript"), S("Angular")))

    # Learning path recommendations
    metta.space().add_atom(E(S("next-skill"), S("JavaScript"), S("React")))
    metta.space().add_atom(E(S("next-skill"), S("JavaScript"), S("TypeScript")))
    metta.space().add_atom(E(S("next-skill"), S("Python"), S("FastAPI")))
    metta.space().add_atom(E(S("next-skill"), S("Python"), S("Django")))
    metta.space().add_atom(E(S("next-skill"), S("React"), S("Next.js")))
    metta.space().add_atom(E(S("next-skill"), S("Node.js"), S("Express")))

    # Profile strength indicators
    metta.space().add_atom(E(S("profile-strength"), ValueAtom(1), ValueAtom("weak")))
    metta.space().add_atom(E(S("profile-strength"), ValueAtom(3), ValueAtom("moderate")))
    metta.space().add_atom(E(S("profile-strength"), ValueAtom(5), ValueAtom("strong")))
    metta.space().add_atom(E(S("profile-strength"), ValueAtom(7), ValueAtom("very-strong")))
    metta.space().add_atom(E(S("profile-strength"), ValueAtom(10), ValueAtom("exceptional")))

    return metta
