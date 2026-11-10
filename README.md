### Process Proof Assertion

A proposal for interoperable evidence of content creation and revision.

## Status

**Discussion draft 0.2, 9 November 2026.** This is an independently authored proposal for CAWG discussion. It is not an adopted CAWG specification or an allocated assertion label. No implementation is claimed to produce the proposed envelope.

## What this adds

A reader should be able to identify the evidence accompanying a document, determine exactly which content it covers, and understand what a verifier checked. C2PA already provides signatures, content bindings and references to process evidence. The proposed addition is a common verification contract across evidence producers.

The [draft](docs/modules/ROOT/pages/index.adoc) describes a profile identifier, an exact content binding, a context, and inline or referenced evidence. A profile defines the evidence's meaning and complete verification procedure. The group should decide whether this needs a new assertion or can be expressed as a profile of existing mechanisms.

**A checked history does not establish human authorship.** Automation can construct a valid edit history. A signature identifies a key holder's statement; hardware key protection does not by itself attest the capture application. Time anchors and privacy properties need their own evidence and assumptions.

## Candidate profiles

| Candidate | What it could establish | Current boundary |
|---|---|---|
| CPoE / WritersProof | Integrity and content/context binding of a captured-process evidence packet, with explicitly selected checkpoint and proof checks | The application's existing assertion has a different schema. A documented adapter and independent validation are still required. |
| ECHO, Execution and Composition History Object | A declared editing computation agrees with signed checkpoint commitments and reaches the public final text | Experimental r8 research. Complete security arguments and the WritersProof adapter remain open. No human-origin or production privacy guarantee. |

The draft treats evidence integrity, content matching, computation checks, signer trust, capture assurance and time evidence separately. It removes the blanket confidence ladder and the `zeroDataCommitment` flag.

## Evidence and examples

[Examples and checks](examples/README.md) include a real producer-generated **synthetic** WritersProof fixture, its source digests, and the output of an independent C2PA reader. That reader reports validation failures; the fixture is a migration case, not a conformance claim. Its zero-checkpoint record cannot establish a writing process even when its signature and content digest are checked.

The proposed [CDDL](docs/modules/ROOT/partials/process-proof.cddl) and envelope examples are separate from that existing format. Schema validation does not validate a proof or establish interoperability.

## Related work

| Resource | Relationship |
|---|---|
| [C2PA 2.5](https://spec.c2pa.org/specifications/specifications/2.5/specs/C2PA_Specification.html) | Enclosing content provenance and existing process-evidence transport |
| [CAWG Identity 1.3](https://cawg.io/identity/1.3/) | Identity binding; separate from process verification |
| [CAWG creative-contribution proposal](https://github.com/decentralized-identity/cawg-identity-assertion/issues/285) | Declared contribution; an open proposal, not an adopted assertion |
| [CAWG delegated-creator proposal](https://github.com/decentralized-identity/cawg-identity-assertion/issues/286) | Declared authority; an open proposal, not an adopted assertion |
| [ToIP Process Attestation 0.1](https://github.com/trustoverip/dtgwg-trust-tasks-tf/tree/main/specs/process-attestation/0.1) | Evidence request/response exchange |
| [CPoE drafts](https://github.com/LF-Decentralized-Trust-labs/proof-of-effort) | Candidate evidence-packet and appraisal specifications |

ECHO is described informatively from the reviewed research checkout. No public distribution or stable profile is assumed.

## Contributing

Contributions are welcome via pull requests. The draft ends with questions about scope, reuse of existing mechanisms, profile admission and verification results. There is no CAWG profile-registration process established by this repository.

## License

This specification is made available under the terms of the [W3C Community Contributor License Agreement](https://www.w3.org/community/about/agreements/cla/).
