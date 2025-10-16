"""
Extract function-level chunks from parsed code.
"""
from typing import List
from tree_sitter import Tree

# Avoid relative imports for standalone usage
try:
    from ..core.types import CodeChunk, ChunkType, Language
except ImportError:
    from core.types import CodeChunk, ChunkType, Language


class FunctionChunker:
    """Chunk code by functions and classes."""

    def extract_chunks(
        self,
        tree: Tree,
        content: str,
        repo: str,
        file_path: str,
        language: Language,
    ) -> List[CodeChunk]:
        """
        Extract function/class chunks from a Tree-sitter tree.

        Args:
            tree: Parsed tree
            content: Original source code
            repo: Repository name (owner/name)
            file_path: Relative file path
            language: Programming language

        Returns:
            List of CodeChunk objects
        """
        chunks = []

        # Extract all functions and classes
        all_nodes = self._get_all_definitions(tree.root_node)

        for node in all_nodes:
            chunk = self._node_to_chunk(
                node=node,
                content=content,
                repo=repo,
                file_path=file_path,
                language=language,
            )

            if chunk:
                chunks.append(chunk)

        return chunks

    def _get_all_definitions(self, root_node) -> list:
        """Recursively find all function/class/method definitions."""
        definitions = []

        # Node types that represent code structures
        definition_types = {
            # Functions
            "function_definition",  # Python
            "function_declaration",  # JS, Java, C++
            "function_item",  # Rust
            "method_declaration",  # Java
            "method_definition",  # Python
            # Classes
            "class_definition",  # Python
            "class_declaration",  # Java, C++
            "impl_item",  # Rust
            "struct_item",  # Rust, Go
            "interface_declaration",  # Java, TypeScript
        }

        def traverse(node):
            if node.type in definition_types:
                definitions.append(node)

            for child in node.children:
                traverse(child)

        traverse(root_node)
        return definitions

    def _node_to_chunk(
        self,
        node,
        content: str,
        repo: str,
        file_path: str,
        language: Language,
    ) -> CodeChunk:
        """Convert a Tree-sitter node to a CodeChunk."""
        # Extract name
        name = self._get_node_name(node)
        if not name:
            name = f"<anonymous_{node.type}>"

        # Extract code
        code = content[node.start_byte : node.end_byte]

        # Determine chunk type
        chunk_type = self._get_chunk_type(node.type)

        # Extract signature (first line usually)
        signature = code.split("\n")[0] if code else None

        # Extract docstring
        docstring = self._extract_docstring(node, content)

        # Create chunk ID
        chunk_id = f"{repo}_{file_path}_{name}_{node.start_point.row}".replace("/", "_").replace(" ", "_")

        # Count lines
        lines_of_code = node.end_point.row - node.start_point.row + 1

        return CodeChunk(
            id=chunk_id,
            code=code,
            repo=repo,
            file_path=file_path,
            language=language,
            chunk_type=chunk_type,
            name=name,
            signature=signature,
            docstring=docstring,
            start_line=node.start_point.row,
            end_line=node.end_point.row,
            start_byte=node.start_byte,
            end_byte=node.end_byte,
            lines_of_code=lines_of_code,
        )

    def _get_node_name(self, node) -> str:
        """Extract name from a node."""
        # Try 'name' field first
        name_node = node.child_by_field_name("name")
        if name_node:
            return name_node.text.decode("utf8")

        # Fallback: search for identifier
        for child in node.children:
            if child.type == "identifier":
                return child.text.decode("utf8")

        return None

    def _get_chunk_type(self, node_type: str) -> ChunkType:
        """Map Tree-sitter node type to ChunkType."""
        if "function" in node_type:
            return ChunkType.FUNCTION
        elif "method" in node_type:
            return ChunkType.METHOD
        elif "class" in node_type:
            return ChunkType.CLASS
        else:
            return ChunkType.FUNCTION  # Default

    def _extract_docstring(self, node, content: str) -> str:
        """Extract docstring/comment if present."""
        # Python: first statement in function body
        if node.type in ["function_definition", "method_definition"]:
            body = node.child_by_field_name("body")
            if body and body.child_count > 1:
                first_stmt = body.child(1)  # Skip ':'
                if first_stmt and first_stmt.type == "expression_statement":
                    expr = first_stmt.child(0)
                    if expr and expr.type == "string":
                        docstring_text = content[expr.start_byte : expr.end_byte]
                        # Remove quotes
                        return docstring_text.strip('"""').strip("'''").strip('"').strip("'")

        # TODO: JSDoc, Javadoc, Rustdoc

        return None
