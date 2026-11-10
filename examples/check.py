# /// script
# requires-python = ">=3.11"
# dependencies = ["cbor2==5.7.1"]
# ///

import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import cbor2


ROOT = Path(__file__).resolve().parent
SCHEMA = ROOT.parent / "docs/modules/ROOT/partials/process-proof.cddl"
TEXT = b"A short example.\n"
EVIDENCE = b"Illustrative bytes, not a process proof."


def digest(value):
    return hashlib.sha256(value).digest()


def envelope():
    return {
        "version": 1,
        "profile": "https://example.org/process-evidence/demo",
        "profileVersion": "discussion-1",
        "subject": {
            "representation": "utf8-exact",
            "sha256": digest(TEXT),
            "byteLength": len(TEXT),
        },
        "context": bytes(range(16)),
        "evidenceHash": digest(EVIDENCE),
        "evidence": {"bytes": EVIDENCE},
    }


def external_envelope():
    value = envelope()
    value["evidence"] = {
        "externalAssertion": {
            "url": "self#jumbf=c2pa.assertions/c2pa.external-reference",
            "alg": "sha256",
            "hash": bytes(32),
        }
    }
    return value


def display(value):
    if isinstance(value, bytes):
        return {"hex": value.hex()}
    if isinstance(value, dict):
        return {key: display(item) for key, item in value.items()}
    return value


def write_examples():
    for name, value in (("inline", envelope()), ("external", external_envelope())):
        (ROOT / f"{name}.cbor").write_bytes(cbor2.dumps(value, canonical=True))
        (ROOT / f"{name}.display.json").write_text(
            json.dumps(display(value), indent=2) + "\n"
        )


def check_schema():
    count = 0
    with tempfile.TemporaryDirectory(prefix="process-proof-schema-") as temp:
        path = Path(temp) / "case.cbor"

        def check(name, value, valid):
            nonlocal count
            path.write_bytes(cbor2.dumps(value, canonical=True))
            result = subprocess.run(
                ["cddl", "--ci", "validate", "--cddl", str(SCHEMA), "--cbor", str(path)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if (result.returncode == 0) != valid:
                raise AssertionError(f"{name}: unexpected schema result: {result.stderr[:1000]}")
            count += 1

        for name, expected in (("inline", envelope()), ("external", external_envelope())):
            actual = cbor2.loads((ROOT / f"{name}.cbor").read_bytes())
            assert actual == expected
            assert json.loads((ROOT / f"{name}.display.json").read_text()) == display(actual)
            check(name, actual, True)

        for field, limit in (("profile", 2048), ("profileVersion", 128)):
            for length in (0, 1, 2, limit - 1, limit, limit + 1):
                value = envelope()
                value[field] = "x" * length
                check(f"{field} length {length}", value, 1 <= length <= limit)

        for length in (15, 16, 17, 63, 64, 65):
            value = envelope()
            value["context"] = bytes(length)
            check(f"context length {length}", value, 16 <= length <= 64)

        for field in ("subject", "evidenceHash", "external"):
            for length in (31, 32, 33):
                value = external_envelope() if field == "external" else envelope()
                if field == "subject":
                    value["subject"]["sha256"] = bytes(length)
                elif field == "external":
                    value["evidence"]["externalAssertion"]["hash"] = bytes(length)
                else:
                    value["evidenceHash"] = bytes(length)
                check(f"{field} digest length {length}", value, length == 32)

        for length in (0, 1, 2, 16777215, 16777216, 16777217):
            value = envelope()
            value["evidence"]["bytes"] = bytes(length)
            check(f"inline evidence length {length}", value, 1 <= length <= 16777216)

        for version in (0, 1, 2):
            value = envelope()
            value["version"] = version
            check(f"version {version}", value, version == 1)

        for length in (-1, 0, 1):
            value = envelope()
            value["subject"]["byteLength"] = length
            check(f"subject byte length {length}", value, length >= 0)

        value = envelope()
        value["evidence"].update(external_envelope()["evidence"])
        check("both evidence sources", value, False)
        value = envelope()
        value["evidence"] = {}
        check("neither evidence source", value, False)
        value = envelope()
        value["zeroDataCommitment"] = True
        check("removed privacy field", value, False)
        value = envelope()
        value["subject"]["representation"] = "rtf-rendered-text"
        check("unsupported subject mapping", value, False)
        value = external_envelope()
        value["evidence"]["externalAssertion"]["alg"] = "unknown"
        check("unsupported reference hash", value, False)
        for field in envelope():
            value = envelope()
            del value[field]
            check(f"missing {field}", value, False)

        report = json.loads((ROOT / "writersproof/reader-report.json").read_text())
        manifest = report["manifests"][report["active_manifest"]]
        check("existing application assertion is not this envelope",
              manifest["assertion_store"]["com.writerslogic.process-proof"], False)

    return count


def check_writer_fixture():
    folder = ROOT / "writersproof"
    source = json.loads((folder / "source.json").read_text())
    document = (folder / "document.txt").read_bytes()
    manifest = (folder / "manifest.c2pa").read_bytes()
    assert digest(document).hex() == source["source_sha256"]
    assert digest(manifest).hex() == source["manifest_sha256"]
    block = document.split(b"-----BEGIN WRITERSPROOF PROOF-----", 1)[1]
    body = block.split(b"\n\n", 1)[1].split(b"-----END WRITERSPROOF PROOF-----", 1)[0]
    assert base64.b64decode(b"".join(body.split()), validate=True) == manifest

    report = json.loads((folder / "reader-report.json").read_text())
    assertions = report["manifests"][report["active_manifest"]]["assertion_store"]
    binding = assertions["c2pa.hash.data"]
    assert binding["alg"] == "sha256"
    assert len(binding["exclusions"]) == 1
    exclusion = binding["exclusions"][0]
    start, length = exclusion["start"], exclusion["length"]
    assert start > 0 and start + length == len(document)
    covered = document[:start] + document[start + length:]
    expected = base64.b64decode(binding["hash"], validate=True)
    assert digest(covered) == expected
    assert digest(b"X" + covered[1:]) != expected
    assert digest(covered + b"X") != expected
    assert assertions["com.writerslogic.evidence-chain"]["checkpointCount"] == 0
    statuses = report["validation_results"]["activeManifest"]
    assert "claimSignature.validated" in {item["code"] for item in statuses["success"]}
    assert report["validation_state"] == "Invalid"
    assert {item["code"] for item in statuses["failure"]} == {
        "claim.malformed", "signingCredential.untrusted", "assertion.dataHash.mismatch"
    }
    return {"covered_bytes": len(covered), "covered_sha256": digest(covered).hex(),
            "process_evidence": "unavailable", "reader_result": "Invalid"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-examples", action="store_true")
    args = parser.parse_args()
    if args.write_examples:
        write_examples()
    count = check_schema()
    result = check_writer_fixture()
    print(json.dumps({"schema_cases": count, "writersproof_fixture": result}, indent=2))
    print("Schema and fixture checks only; no new proof or enclosing-credential conformance claim.")


if __name__ == "__main__":
    main()
