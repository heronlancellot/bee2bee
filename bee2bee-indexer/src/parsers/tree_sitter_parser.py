"""
Tree-sitter based code parser for multiple languages.
"""
from pathlib import Path
from typing import Optional
from tree_sitter import Language, Parser, Tree

# Import language bindings
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_typescript as tstypescript
import tree_sitter_rust as tsrust
import tree_sitter_go as tsgo
import tree_sitter_java as tsjava
import tree_sitter_cpp as tscpp

# Avoid relative imports for standalone usage
try:
    from ..core.types import Language as LangEnum
except ImportError:
    from core.types import Language as LangEnum


class TreeSitterParser:
    """Multi-language code parser using Tree-sitter."""

    def __init__(self):
        # Initialize languages
        self.languages = {
            LangEnum.PYTHON: Language(tspython.language()),
            LangEnum.JAVASCRIPT: Language(tsjavascript.language()),
            LangEnum.TYPESCRIPT: Language(tstypescript.language_typescript()),
            LangEnum.RUST: Language(tsrust.language()),
            LangEnum.GO: Language(tsgo.language()),
            LangEnum.JAVA: Language(tsjava.language()),
            LangEnum.CPP: Language(tscpp.language()),  # Fixed: just language() for cpp
            LangEnum.C: Language(tscpp.language()),    # Fixed: just language() for c
        }

        # Extension to language mapping
        self.ext_to_lang = {
            ".py": LangEnum.PYTHON,
            ".js": LangEnum.JAVASCRIPT,
            ".jsx": LangEnum.JAVASCRIPT,
            ".ts": LangEnum.TYPESCRIPT,
            ".tsx": LangEnum.TYPESCRIPT,
            ".rs": LangEnum.RUST,
            ".go": LangEnum.GO,
            ".java": LangEnum.JAVA,
            ".cpp": LangEnum.CPP,
            ".cc": LangEnum.CPP,
            ".cxx": LangEnum.CPP,
            ".c": LangEnum.C,
            ".h": LangEnum.C,
            ".hpp": LangEnum.CPP,
        }

    def parse(self, content: str, file_extension: str) -> Optional[Tree]:
        """
        Parse source code into an AST.

        Args:
            content: Source code content
            file_extension: File extension (e.g., '.py', '.js')

        Returns:
            Tree-sitter Tree object or None if language not supported
        """
        lang = self.get_language(file_extension)
        if lang == LangEnum.UNKNOWN:
            return None

        language = self.languages.get(lang)
        if not language:
            return None

        parser = Parser(language)
        tree = parser.parse(bytes(content, "utf8"))

        return tree

    def get_language(self, file_extension: str) -> LangEnum:
        """Get language enum from file extension."""
        return self.ext_to_lang.get(file_extension, LangEnum.UNKNOWN)

    def get_functions(self, tree: Tree) -> list:
        """Extract function definitions from the tree."""
        functions = []

        def traverse(node):
            # Function definitions vary by language
            if node.type in ["function_definition", "function_declaration", "function_item", "method_declaration"]:
                functions.append(node)

            for child in node.children:
                traverse(child)

        traverse(tree.root_node)
        return functions

    def get_classes(self, tree: Tree) -> list:
        """Extract class definitions from the tree."""
        classes = []

        def traverse(node):
            if node.type in ["class_definition", "class_declaration", "impl_item", "struct_item"]:
                classes.append(node)

            for child in node.children:
                traverse(child)

        traverse(tree.root_node)
        return classes

    def get_node_name(self, node) -> Optional[str]:
        """Extract the name from a function/class node."""
        # Look for 'name' field
        name_node = node.child_by_field_name("name")
        if name_node:
            return name_node.text.decode("utf8")

        # Fallback: look for identifier child
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode("utf8")

        return None

    def get_docstring(self, node, content: str) -> Optional[str]:
        """Extract docstring/comment for a node."""
        # Python docstrings
        if node.type == "function_definition":
            for child in node.children:
                if child.type == "block":
                    first_stmt = child.child(1) if child.child_count > 1 else None  # Skip colon
                    if first_stmt and first_stmt.type == "expression_statement":
                        expr = first_stmt.child(0)
                        if expr and expr.type == "string":
                            text = content[expr.start_byte:expr.end_byte]
                            # Remove quotes
                            return text.strip('"""').strip("'''").strip('"').strip("'")

        # TODO: Add support for JSDoc, Rustdoc, etc.

        return None
