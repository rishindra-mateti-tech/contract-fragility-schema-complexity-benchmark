#!/usr/bin/env python3
"""OpenAPI Local Reference Resolver.

Implements bounded, provenance-preserving, fail-closed resolution of local
OpenAPI $ref references under OPENAPI_REFERENCE_RESOLUTION_POLICY_001.

Enforces:
1. Local repository confinement (prevents path-traversal attacks escaping root).
2. Strict prohibition of network/remote schemes (http, https, ftp, file).
3. Prohibition of absolute filesystem paths.
4. Reference cycle detection (fail-closed on recursion loops).
5. Configurable maximum depth limit (default d <= 8).
6. Bidirectional lineage preservation (declared pointer, resolved file, resolved pointer).
7. Transitive reference closure tracking with cryptographic SHA-256 verification.
"""

import copy
import hashlib
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Set, Tuple
import yaml

POLICY_ID = "OPENAPI_REFERENCE_RESOLUTION_POLICY_001"
DEFAULT_MAX_DEPTH = 8

# Pinned Policy Error Codes
ERR_REMOTE_REF_PROHIBITED = "ERR_REMOTE_REF_PROHIBITED"
ERR_ABSOLUTE_PATH_PROHIBITED = "ERR_ABSOLUTE_PATH_PROHIBITED"
ERR_PATH_TRAVERSAL_DETECTED = "ERR_PATH_TRAVERSAL_DETECTED"
ERR_LOCAL_REF_FILE_NOT_FOUND = "ERR_LOCAL_REF_FILE_NOT_FOUND"
ERR_REFERENCE_CYCLE_DETECTED = "ERR_REFERENCE_CYCLE_DETECTED"
ERR_REF_DEPTH_EXCEEDED = "ERR_REF_DEPTH_EXCEEDED"
ERR_FRAGMENT_NOT_FOUND = "ERR_FRAGMENT_NOT_FOUND"
ERR_UNSUPPORTED_DOC_FORMAT = "ERR_UNSUPPORTED_DOC_FORMAT"


class ReferenceResolutionError(Exception):
    """Base exception for local reference resolution failures."""

    def __init__(self, code: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
        self.details = details or {}


def compute_sha256(content: bytes) -> str:
    """Compute hex SHA-256 hash."""
    return hashlib.sha256(content).hexdigest()


def compute_git_blob_sha(content: bytes) -> str:
    """Compute Git blob SHA-1 hash."""
    header = f"blob {len(content)}\0".encode("utf-8")
    return hashlib.sha1(header + content).hexdigest()


def resolve_json_pointer_in_doc(doc: Any, pointer: str) -> Any:
    """Resolve standard JSON pointer within an in-memory document."""
    if not pointer or pointer == "#" or pointer == "#/":
        return doc

    clean_ptr = pointer
    if clean_ptr.startswith("#/"):
        clean_ptr = clean_ptr[2:]
    elif clean_ptr.startswith("#"):
        clean_ptr = clean_ptr[1:]
    elif clean_ptr.startswith("/"):
        clean_ptr = clean_ptr[1:]

    tokens = clean_ptr.split("/")
    current = doc
    for tok in tokens:
        unescaped = tok.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and unescaped in current:
            current = current[unescaped]
        elif isinstance(current, list) and unescaped.isdigit():
            idx = int(unescaped)
            if 0 <= idx < len(current):
                current = current[idx]
            else:
                return None
        else:
            return None
    return current


class LocalReferenceResolver:
    """Bounded, fail-closed resolver for OpenAPI multi-file local references."""

    def __init__(
        self,
        bundle_root_dir: str,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ):
        self.bundle_root_dir = os.path.realpath(os.path.abspath(bundle_root_dir))
        self.max_depth = max_depth
        self.doc_cache: Dict[str, Tuple[Any, bytes, str, str]] = {}
        self.resolution_log: List[Dict[str, Any]] = []
        self.accessed_files: Dict[str, Dict[str, Any]] = {}

    def _load_document(self, file_path: str) -> Tuple[Any, bytes, str, str]:
        """Load and parse JSON or YAML document, caching parsed structure and hashes."""
        real_path = os.path.realpath(os.path.abspath(file_path))
        if real_path in self.doc_cache:
            return self.doc_cache[real_path]

        if not os.path.exists(real_path):
            raise ReferenceResolutionError(
                ERR_LOCAL_REF_FILE_NOT_FOUND,
                f"Referenced local file does not exist: {real_path}",
                {"file_path": real_path},
            )

        with open(real_path, "rb") as f:
            raw_bytes = f.read()

        file_sha256 = compute_sha256(raw_bytes)
        blob_sha = compute_git_blob_sha(raw_bytes)

        ext = os.path.splitext(real_path)[1].lower()
        try:
            if ext == ".json":
                parsed = json.loads(raw_bytes.decode("utf-8"))
            elif ext in [".yaml", ".yml"]:
                parsed = yaml.safe_load(raw_bytes.decode("utf-8"))
            else:
                raise ReferenceResolutionError(
                    ERR_UNSUPPORTED_DOC_FORMAT,
                    f"Unsupported reference document format '{ext}' for file: {real_path}",
                    {"file_path": real_path, "extension": ext},
                )
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ReferenceResolutionError(
                ERR_UNSUPPORTED_DOC_FORMAT,
                f"Failed to parse document {real_path}: {str(e)}",
                {"file_path": real_path, "parse_error": str(e)},
            )

        self.doc_cache[real_path] = (parsed, raw_bytes, file_sha256, blob_sha)
        
        # Track in accessed files
        rel_to_root = os.path.relpath(real_path, self.bundle_root_dir).replace("\\", "/")
        if real_path not in self.accessed_files:
            self.accessed_files[real_path] = {
                "absolute_path": real_path,
                "relative_path": rel_to_root,
                "file_size_bytes": len(raw_bytes),
                "file_sha256": file_sha256,
                "git_blob_sha": blob_sha,
            }

        return self.doc_cache[real_path]

    def register_root_document(self, root_file_path: str, root_doc: Optional[Any] = None) -> None:
        """Register the primary root document of the bundle."""
        real_path = os.path.realpath(os.path.abspath(root_file_path))
        if root_doc is not None and real_path not in self.doc_cache:
            raw_bytes = json.dumps(root_doc, sort_keys=True).encode("utf-8")
            self.doc_cache[real_path] = (
                root_doc,
                raw_bytes,
                compute_sha256(raw_bytes),
                compute_git_blob_sha(raw_bytes),
            )
            rel_to_root = os.path.relpath(real_path, self.bundle_root_dir).replace("\\", "/")
            self.accessed_files[real_path] = {
                "absolute_path": real_path,
                "relative_path": rel_to_root,
                "file_size_bytes": len(raw_bytes),
                "file_sha256": compute_sha256(raw_bytes),
                "git_blob_sha": compute_git_blob_sha(raw_bytes),
            }
        else:
            self._load_document(real_path)

    def resolve_reference(
        self,
        ref_string: str,
        current_file_path: str,
        call_path: Optional[List[Tuple[str, str]]] = None,
        depth: int = 0,
    ) -> Tuple[Any, str, str]:
        """Resolve a reference string ($ref) relative to current_file_path.
        
        Returns:
            Tuple of (resolved_schema_node, resolved_file_path, resolved_pointer)
        """
        if call_path is None:
            call_path = []

        if depth > self.max_depth:
            raise ReferenceResolutionError(
                ERR_REF_DEPTH_EXCEEDED,
                f"Maximum reference depth limit ({self.max_depth}) exceeded at '{ref_string}'",
                {"ref_string": ref_string, "depth": depth, "max_depth": self.max_depth},
            )

        # 1. Prohibit remote schemes
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", ref_string):
            raise ReferenceResolutionError(
                ERR_REMOTE_REF_PROHIBITED,
                f"Remote reference schemes are prohibited under Policy 001: '{ref_string}'",
                {"ref_string": ref_string},
            )

        # Parse file path part and fragment part
        if "#" in ref_string:
            file_part, fragment_part = ref_string.split("#", 1)
            fragment_pointer = "#" + fragment_part
        else:
            file_part = ref_string
            fragment_pointer = "#"

        # 2. Prohibit absolute filesystem paths
        if file_part.startswith("/") or (len(file_part) > 1 and file_part[1] == ":"):
            raise ReferenceResolutionError(
                ERR_ABSOLUTE_PATH_PROHIBITED,
                f"Absolute filesystem paths are prohibited in references: '{ref_string}'",
                {"ref_string": ref_string, "file_part": file_part},
            )

        # Determine target file
        real_current_file = os.path.realpath(os.path.abspath(current_file_path))
        if not file_part:
            target_file = real_current_file
        else:
            current_dir = os.path.dirname(real_current_file)
            candidate_target = os.path.join(current_dir, file_part)
            target_file = os.path.realpath(os.path.abspath(candidate_target))

        # 3. Path traversal detection: ensure target is within bundle_root_dir
        # Allow target_file if it is within or equal to bundle_root_dir
        try:
            rel = os.path.relpath(target_file, self.bundle_root_dir)
            if rel.startswith("..") or os.path.isabs(rel):
                raise ReferenceResolutionError(
                    ERR_PATH_TRAVERSAL_DETECTED,
                    f"Reference '{ref_string}' traverses outside bundle root '{self.bundle_root_dir}'",
                    {
                        "ref_string": ref_string,
                        "target_file": target_file,
                        "bundle_root": self.bundle_root_dir,
                    },
                )
        except ValueError:
            raise ReferenceResolutionError(
                ERR_PATH_TRAVERSAL_DETECTED,
                f"Reference '{ref_string}' is on a different drive or invalid path relative to bundle root",
                {"ref_string": ref_string, "target_file": target_file},
            )

        # 4. Cycle detection
        current_target_token = (target_file, fragment_pointer)
        if current_target_token in call_path:
            cycle_desc = " -> ".join(f"{f}{ptr}" for f, ptr in call_path + [current_target_token])
            raise ReferenceResolutionError(
                ERR_REFERENCE_CYCLE_DETECTED,
                f"Reference cycle detected: {cycle_desc}",
                {"cycle": call_path + [current_target_token], "ref_string": ref_string},
            )

        # 5. Load document
        doc, raw_bytes, sha256_hash, blob_sha = self._load_document(target_file)

        # 6. Resolve JSON Pointer fragment
        resolved_node = resolve_json_pointer_in_doc(doc, fragment_pointer)
        if resolved_node is None:
            raise ReferenceResolutionError(
                ERR_FRAGMENT_NOT_FOUND,
                f"JSON Pointer '{fragment_pointer}' not found in document '{target_file}'",
                {
                    "ref_string": ref_string,
                    "target_file": target_file,
                    "fragment_pointer": fragment_pointer,
                },
            )

        # Log resolution step
        log_entry = {
            "declared_ref": ref_string,
            "origin_file": real_current_file,
            "resolved_file": target_file,
            "resolved_pointer": fragment_pointer,
            "depth": depth,
            "status": "RESOLVED",
        }
        self.resolution_log.append(log_entry)

        # If resolved node itself has a $ref, resolve transitively
        if isinstance(resolved_node, dict) and "$ref" in resolved_node:
            transitive_call_path = call_path + [current_target_token]
            return self.resolve_reference(
                resolved_node["$ref"],
                current_file_path=target_file,
                call_path=transitive_call_path,
                depth=depth + 1,
            )

        return resolved_node, target_file, fragment_pointer

    def get_reference_closure_manifest(self) -> Dict[str, Any]:
        """Generate machine-readable reference closure manifest."""
        files_list = []
        for abs_p, finfo in sorted(self.accessed_files.items()):
            files_list.append({
                "relative_path": finfo["relative_path"],
                "file_sha256": finfo["file_sha256"],
                "git_blob_sha": finfo["git_blob_sha"],
                "file_size_bytes": finfo["file_size_bytes"],
            })

        closure_hash_input = "".join(f"{f['relative_path']}:{f['file_sha256']};" for f in files_list)
        closure_sha256 = hashlib.sha256(closure_hash_input.encode("utf-8")).hexdigest()

        return {
            "policy_id": POLICY_ID,
            "bundle_root_dir": self.bundle_root_dir,
            "closure_sha256": closure_sha256,
            "accessed_files_count": len(files_list),
            "accessed_files": files_list,
            "resolution_steps_count": len(self.resolution_log),
            "resolution_log": copy.deepcopy(self.resolution_log),
        }
