"""Publish only Ed25519 public verification material from a Certify DID document."""
import argparse
import json
import re
from pathlib import Path


def export_document(source, owner, repository):
    for value in (owner, repository):
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", value):
            raise ValueError("Owner and repository must be GitHub names, without URL syntax.")
    did = f"did:web:{owner.lower()}.github.io:{repository}:issuer"
    methods = []
    for entry in source.get("verificationMethod", []):
        if entry.get("type") != "Ed25519VerificationKey2020":
            continue
        key = entry.get("publicKeyMultibase", "")
        identifier = entry.get("id", "")
        if not isinstance(key, str) or not key.startswith("z6Mk"):
            raise ValueError("Expected a multibase Ed25519 public key.")
        if not isinstance(identifier, str) or "#" not in identifier or not identifier.split("#", 1)[1]:
            raise ValueError("Verification method must have a key ID fragment.")
        methods.append({
            "id": did + "#" + identifier.split("#", 1)[1],
            "type": "Ed25519VerificationKey2020",
            "controller": did,
            "publicKeyMultibase": key,
        })
    if not methods:
        raise ValueError("Source has no Ed25519VerificationKey2020 signing keys.")
    if len({method["id"] for method in methods}) != len(methods):
        raise ValueError("Duplicate signing key IDs in source.")
    return {
        "@context": ["https://www.w3.org/ns/did/v1", "https://w3id.org/security/suites/ed25519-2020/v1"],
        "id": did,
        "verificationMethod": methods,
        "assertionMethod": [method["id"] for method in methods],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Public DID JSON exported from the running Certify instance")
    parser.add_argument("--owner", required=True, help="GitHub Pages account")
    parser.add_argument("--repository", default="erl-demo-config")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "issuer/did.json")
    args = parser.parse_args()
    try:
        document = export_document(json.loads(args.source.read_text()), args.owner, args.repository)
    except (ValueError, AttributeError, TypeError) as error:
        parser.error(str(error))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n")
    print(f"Exported public signing keys to {args.output}")
    print(f"Issuer DID: {document['id']}")


if __name__ == "__main__":
    main()
