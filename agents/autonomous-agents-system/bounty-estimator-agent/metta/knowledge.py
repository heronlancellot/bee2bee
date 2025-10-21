# knowledge.py - MeTTa Knowledge Base for Bounty Estimation
from hyperon import MeTTa, E, S, ValueAtom

def initialize_bounty_knowledge_graph(metta: MeTTa):
    """Initialize MeTTa knowledge graph for intelligent bounty estimation."""

    # Complexity levels
    metta.space().add_atom(E(S("complexity-level"), ValueAtom(1), ValueAtom("trivial")))
    metta.space().add_atom(E(S("complexity-level"), ValueAtom(2), ValueAtom("trivial")))
    metta.space().add_atom(E(S("complexity-level"), ValueAtom(3), ValueAtom("easy")))
    metta.space().add_atom(E(S("complexity-level"), ValueAtom(4), ValueAtom("easy")))
    metta.space().add_atom(E(S("complexity-level"), ValueAtom(5), ValueAtom("moderate")))
    metta.space().add_atom(E(S("complexity-level"), ValueAtom(6), ValueAtom("moderate")))
    metta.space().add_atom(E(S("complexity-level"), ValueAtom(7), ValueAtom("hard")))
    metta.space().add_atom(E(S("complexity-level"), ValueAtom(8), ValueAtom("hard")))
    metta.space().add_atom(E(S("complexity-level"), ValueAtom(9), ValueAtom("very-hard")))
    metta.space().add_atom(E(S("complexity-level"), ValueAtom(10), ValueAtom("very-hard")))

    # Base rates by complexity
    metta.space().add_atom(E(S("base-rate"), ValueAtom("trivial"), ValueAtom(25)))
    metta.space().add_atom(E(S("base-rate"), ValueAtom("easy"), ValueAtom(50)))
    metta.space().add_atom(E(S("base-rate"), ValueAtom("moderate"), ValueAtom(100)))
    metta.space().add_atom(E(S("base-rate"), ValueAtom("hard"), ValueAtom(200)))
    metta.space().add_atom(E(S("base-rate"), ValueAtom("very-hard"), ValueAtom(400)))

    # Premium skills (worth more)
    metta.space().add_atom(E(S("premium-skill"), S("Rust"), ValueAtom(1.5)))
    metta.space().add_atom(E(S("premium-skill"), S("Go"), ValueAtom(1.3)))
    metta.space().add_atom(E(S("premium-skill"), S("Solidity"), ValueAtom(2.0)))
    metta.space().add_atom(E(S("premium-skill"), S("Kotlin"), ValueAtom(1.3)))
    metta.space().add_atom(E(S("premium-skill"), S("Swift"), ValueAtom(1.3)))
    metta.space().add_atom(E(S("premium-skill"), S("Scala"), ValueAtom(1.4)))
    metta.space().add_atom(E(S("premium-skill"), S("Haskell"), ValueAtom(1.5)))

    # Repository popularity multipliers
    metta.space().add_atom(E(S("repo-multiplier"), ValueAtom(100), ValueAtom(1.0)))
    metta.space().add_atom(E(S("repo-multiplier"), ValueAtom(500), ValueAtom(1.1)))
    metta.space().add_atom(E(S("repo-multiplier"), ValueAtom(1000), ValueAtom(1.2)))
    metta.space().add_atom(E(S("repo-multiplier"), ValueAtom(5000), ValueAtom(1.3)))
    metta.space().add_atom(E(S("repo-multiplier"), ValueAtom(10000), ValueAtom(1.5)))
    metta.space().add_atom(E(S("repo-multiplier"), ValueAtom(50000), ValueAtom(1.7)))

    # Bounty tiers
    metta.space().add_atom(E(S("bounty-tier"), ValueAtom(25), ValueAtom("Micro")))
    metta.space().add_atom(E(S("bounty-tier"), ValueAtom(50), ValueAtom("Small")))
    metta.space().add_atom(E(S("bounty-tier"), ValueAtom(200), ValueAtom("Medium")))
    metta.space().add_atom(E(S("bounty-tier"), ValueAtom(500), ValueAtom("Large")))
    metta.space().add_atom(E(S("bounty-tier"), ValueAtom(1000), ValueAtom("XLarge")))
    metta.space().add_atom(E(S("bounty-tier"), ValueAtom(5000), ValueAtom("Enterprise")))

    # Fair hourly rates
    metta.space().add_atom(E(S("fair-rate"), ValueAtom("junior"), ValueAtom(15)))
    metta.space().add_atom(E(S("fair-rate"), ValueAtom("mid"), ValueAtom(25)))
    metta.space().add_atom(E(S("fair-rate"), ValueAtom("senior"), ValueAtom(50)))
    metta.space().add_atom(E(S("fair-rate"), ValueAtom("expert"), ValueAtom(100)))

    # Urgency multipliers
    metta.space().add_atom(E(S("urgency-multiplier"), ValueAtom("low"), ValueAtom(1.0)))
    metta.space().add_atom(E(S("urgency-multiplier"), ValueAtom("normal"), ValueAtom(1.2)))
    metta.space().add_atom(E(S("urgency-multiplier"), ValueAtom("high"), ValueAtom(1.5)))
    metta.space().add_atom(E(S("urgency-multiplier"), ValueAtom("urgent"), ValueAtom(2.0)))

    return metta
