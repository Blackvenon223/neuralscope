"""Tests for documentation feature."""

import json

from neuralscope.features.documentation.domain.entities.document import (
    ClassDoc,
    FunctionDoc,
    GeneratedDoc,
)
from neuralscope.features.documentation.data.datasource.llm_documenter.implementation import (
    LlmDocumenterDatasource,
)


def test_generated_doc_item_count():
    doc = GeneratedDoc(
        file_path="app.py",
        module_docstring="Main app",
        classes=[ClassDoc(name="Server", docstring="HTTP server")],
        functions=[
            FunctionDoc(name="main", signature="def main()", docstring="Entry point"),
            FunctionDoc(name="helper", signature="def helper()", docstring="Utility"),
        ],
    )
    assert doc.item_count == 3


def test_parse_valid_doc_response():
    raw = json.dumps({
        "module_docstring": "Auth module",
        "classes": [
            {
                "name": "AuthService",
                "docstring": "Handles authentication",
                "bases": ["BaseService"],
                "methods": [
                    {
                        "name": "login",
                        "signature": "async def login(email: str, password: str) -> Token",
                        "docstring": "Authenticates user",
                        "params": ["email: str - user email", "password: str - user password"],
                        "returns": "JWT token",
                    }
                ],
            }
        ],
        "functions": [
            {
                "name": "hash_password",
                "signature": "def hash_password(pw: str) -> str",
                "docstring": "Hashes password with bcrypt",
                "params": ["pw: str - raw password"],
                "returns": "hashed string",
            }
        ],
    })

    ds = LlmDocumenterDatasource.__new__(LlmDocumenterDatasource)
    doc = ds._parse("auth.py", raw)
    assert doc.module_docstring == "Auth module"
    assert len(doc.classes) == 1
    assert doc.classes[0].name == "AuthService"
    assert len(doc.classes[0].methods) == 1
    assert len(doc.functions) == 1
    assert doc.functions[0].name == "hash_password"


def test_parse_malformed_doc_response():
    ds = LlmDocumenterDatasource.__new__(LlmDocumenterDatasource)
    doc = ds._parse("test.py", "not json")
    assert doc.file_path == "test.py"
    assert doc.item_count == 0
