# knowledge.py
from hyperon import MeTTa, E, S, ValueAtom

def initialize_knowledge_graph(metta: MeTTa):
    """Initialize the MeTTa knowledge graph with repository analysis rules."""

    # Complexity thresholds (based on LOC)
    metta.space().add_atom(E(S("complexity-threshold"), S("simple"), ValueAtom(1000)))
    metta.space().add_atom(E(S("complexity-threshold"), S("moderate"), ValueAtom(5000)))
    metta.space().add_atom(E(S("complexity-threshold"), S("complex"), ValueAtom(20000)))
    metta.space().add_atom(E(S("complexity-threshold"), S("very-complex"), ValueAtom(50000)))

    # File count thresholds
    metta.space().add_atom(E(S("file-count-threshold"), S("small"), ValueAtom(10)))
    metta.space().add_atom(E(S("file-count-threshold"), S("medium"), ValueAtom(50)))
    metta.space().add_atom(E(S("file-count-threshold"), S("large"), ValueAtom(200)))
    metta.space().add_atom(E(S("file-count-threshold"), S("very-large"), ValueAtom(500)))

    # Language → Domain mapping
    metta.space().add_atom(E(S("language-domain"), S("Python"), ValueAtom("backend-data-science")))
    metta.space().add_atom(E(S("language-domain"), S("JavaScript"), ValueAtom("frontend-fullstack")))
    metta.space().add_atom(E(S("language-domain"), S("TypeScript"), ValueAtom("frontend-fullstack")))
    metta.space().add_atom(E(S("language-domain"), S("Java"), ValueAtom("backend-enterprise")))
    metta.space().add_atom(E(S("language-domain"), S("Go"), ValueAtom("backend-systems")))
    metta.space().add_atom(E(S("language-domain"), S("Rust"), ValueAtom("systems-performance")))
    metta.space().add_atom(E(S("language-domain"), S("C++"), ValueAtom("systems-performance")))
    metta.space().add_atom(E(S("language-domain"), S("C#"), ValueAtom("backend-enterprise")))
    metta.space().add_atom(E(S("language-domain"), S("Ruby"), ValueAtom("backend-web")))
    metta.space().add_atom(E(S("language-domain"), S("PHP"), ValueAtom("backend-web")))
    metta.space().add_atom(E(S("language-domain"), S("Swift"), ValueAtom("mobile-ios")))
    metta.space().add_atom(E(S("language-domain"), S("Kotlin"), ValueAtom("mobile-android")))

    # Framework detection patterns
    metta.space().add_atom(E(S("framework-indicator"), S("package.json"), S("react"), ValueAtom("React")))
    metta.space().add_atom(E(S("framework-indicator"), S("package.json"), S("next"), ValueAtom("Next.js")))
    metta.space().add_atom(E(S("framework-indicator"), S("package.json"), S("vue"), ValueAtom("Vue.js")))
    metta.space().add_atom(E(S("framework-indicator"), S("requirements.txt"), S("django"), ValueAtom("Django")))
    metta.space().add_atom(E(S("framework-indicator"), S("requirements.txt"), S("flask"), ValueAtom("Flask")))
    metta.space().add_atom(E(S("framework-indicator"), S("requirements.txt"), S("fastapi"), ValueAtom("FastAPI")))
    metta.space().add_atom(E(S("framework-indicator"), S("go.mod"), S("gin"), ValueAtom("Gin")))
    metta.space().add_atom(E(S("framework-indicator"), S("Cargo.toml"), S("actix"), ValueAtom("Actix")))

    # Project type classification (based on file patterns)
    metta.space().add_atom(E(S("project-type"), S("has-api"), ValueAtom("backend-api")))
    metta.space().add_atom(E(S("project-type"), S("has-ui"), ValueAtom("frontend-app")))
    metta.space().add_atom(E(S("project-type"), S("has-both"), ValueAtom("fullstack-app")))
    metta.space().add_atom(E(S("project-type"), S("has-ml"), ValueAtom("ml-project")))
    metta.space().add_atom(E(S("project-type"), S("has-blockchain"), ValueAtom("web3-project")))

    # Difficulty tier (for contributors)
    metta.space().add_atom(E(S("difficulty-tier"), S("beginner"), ValueAtom(0)))
    metta.space().add_atom(E(S("difficulty-tier"), S("intermediate"), ValueAtom(30)))
    metta.space().add_atom(E(S("difficulty-tier"), S("advanced"), ValueAtom(60)))
    metta.space().add_atom(E(S("difficulty-tier"), S("expert"), ValueAtom(85)))

    return metta
