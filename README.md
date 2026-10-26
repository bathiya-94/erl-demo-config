# DMT ERL demo public configuration

Independent Git repository for the ERL JSON-LD context and the issuer's public
Ed25519 signing keys. The context is copied unchanged from
`inji-certify/erl-dataprovider-plugin/examples/erl-context.json`.

## Public addresses

The files are prepared for `bathiya-94/erl-demo-config`:

| Resource | Address |
| --- | --- |
| Context | `https://bathiya-94.github.io/erl-demo-config/contexts/erl.json` |
| DID document | `https://bathiya-94.github.io/erl-demo-config/issuer/did.json` |
| Issuer DID | `did:web:bathiya-94.github.io:erl-demo-config:issuer` |

The GitHub repository name is part of the DID. Choose it before issuing credentials.

## Export the actual signing public key

`issuer/did.json` contains the actual public signing key read from the running
pre-auth Certify instance on 2026-10-26. Its DID and controller use the Pages
address; its key material and key ID fragment match Certify. No private key is
included. This prepares the files locally; it does not publish them or change the
issuer's current LAN DID.

To refresh the key from the running instance, execute from this repository:

```sh
curl --fail --silent --show-error \
  http://127.0.0.1:18090/v1/certify/.well-known/did.json \
  --output /tmp/erl-source-did.json
python3 scripts/export_did.py /tmp/erl-source-did.json --owner bathiya-94
```

The script copies only Ed25519 public verification fields, preserves key ID
fragments, sets the Pages DID and controllers, and adds `assertionMethod` references.
If the repository name differs, pass `--repository YOUR_REPOSITORY`.
Review the exported keys against the running issuer before publishing.

## Publish with GitHub Pages

1. Create an empty public GitHub repository named `erl-demo-config`.
2. Add its URL as this repository's `origin`, commit these public files, and push `main`.
3. In GitHub Settings → Pages, select **Deploy from a branch**, **main**, **/(root)**.
4. Open both JSON URLs and confirm HTTP 200, valid JSON, and HTTPS. For a browser
   verifier, also check cross-origin fetches from the verifier's origin.

The `.nojekyll` file keeps the site as plain static files. Only these public files
belong here; never add private keys, keystores, access tokens, or issued credentials.
GitHub Pages hosts these files; the Certify APIs continue running separately.

## Connect the issuer and verifier

Before issuing fresh credentials, update the lab preparation configuration:

- Set the credential configuration `didUrl` and the issuer's
  `mosip.certify.data-provider-plugin.did-url` to the Pages DID.
- Set `mosip.certify.data-provider-plugin.issuer-public-key-uri` to the Pages DID
  document URL where that property is consumed.
- Set `contextURLs` and the embedded VC template's context URL to the Pages
  `contexts/erl.json` URL. Update preparation inputs so rerunning preparation
  preserves these choices.
- If using the existing SVG viewer, update its expected issuer, document URL
  allowlist, and TLS configuration to resolve Pages using public certificate trust.
  Its current local origin settings couple the issuer API and document hosting.

This repository does not change the running lab configuration. Existing signed
credentials still refer to their original addresses: issue fresh credentials after
changing the DID or context URL. Keep published context definitions stable, retain
public keys needed by existing credentials, and refresh the DID document whenever
the issuer's signing keys change.

Validate with a fresh credential in the intended verifier, then confirm that
altering a credential claim causes signature verification to fail.
