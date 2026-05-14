<p align="center">
  <h1 align="center">Process Proof Assertion</h1>
  <p align="center">A CAWG assertion for cryptographically verifiable authorship evidence</p>
</p>

## Overview

The process proof assertion extends C2PA content provenance with cryptographic evidence that sequential work occurred during content creation. Instead of asking "was this AI-generated?" it lets an author show "here is the verifiable evidence of how I created this."

The assertion binds authoring activity to a hardware-attested attestation chain and external time anchor, making existing `c2pa.created` and `c2pa.actions` claims independently verifiable.

## Key Properties

- **Sequential proof**: Each computation step depends on prior state; skipping steps is cryptographically impossible
- **Time bounded**: Claimed duration is verifiable against an external time authority
- **Hardware attested**: Proof generation is attested to a hardware root of trust
- **Privacy preserving**: No raw behavioral data (keystroke timing, mouse movement, etc.) enters the manifest
- **Profile extensible**: POSME is the initial proof system; alternative profiles can be registered

## Confidence Tiers

| Tier | Attestation | Use Case |
|------|------------|----------|
| 1 | Software-only | Self-attestation |
| 2 | Hardware TEE (Secure Enclave, TPM) | Platform/publisher use |
| 3 | Hardware + external time anchor | Legal, regulatory, high-stakes |

## Specification

The full specification is in [docs/modules/ROOT/pages/index.adoc](docs/modules/ROOT/pages/index.adoc).

## Related Work

| Resource | Description |
|----------|-------------|
| [POSME Internet-Draft](https://github.com/dcondrey/posme-draft) | The cryptographic primitive (IETF CRWG) |
| [C2PA Specification](https://c2pa.org/specifications/) | Content provenance standard |
| [CAWG Identity Assertion](https://cawg.io/identity/) | Complements process proof with identity binding |

## Contributing

Contributions are welcome via pull requests. See the specification for the profile registration process.

## License

This specification is made available under the terms of the [W3C Community Contributor License Agreement](https://www.w3.org/community/about/agreements/cla/).
