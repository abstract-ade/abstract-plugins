# Review policy

The registry helps authors publish useful plugins and helps Abstract users install
reviewed ones. A reviewer completes the listing work they can do themselves and checks
the package for malicious, deceptive or seriously unsafe behaviour. Ordinary submissions
should move to approval once the concrete requirements below are met.

Adapted from Paseo's [REVIEW.md](https://github.com/getpaseo/plugins/blob/main/REVIEW.md)
(Apache-2.0).

## The package is the product

Review exactly what the entry installs: the tree at `commit` in `repository`, under
`path` when there is one. Confirm the commit exists and that its `manifest.json` carries
`pluginId`.

**Never run the plugin.** Don't open its pages, load its scripts or run anything it
ships. Fetching, extracting, reading and comparing files, and looking at its images,
are fine. Run this repository's own validation, never scripts from the plugin or from
the pull request.

For an update, compare the old and the new commit and review what changed and the
behaviour those changes affect. Don't present existing behaviour as new.

## Concrete requirements

- The package passes Abstract's checks: `manifest.json` at the folder's root, no
  executable files, no symbolic links, nothing outside the folder, under 25 MB.
- `name` and `description` are accurate, and the description is one plain sentence.
- A plugin with a screen, a panel tab, a Home card or a theme has at least one screenshot
  showing it, with sample data and nothing private.
- The submitter owns the repository or has the owner's permission to list it.

## Security review

Judge what it asks for against what it does. Read:

- **Capabilities.** Each one in the manifest, and whether the plugin uses it for its
  stated purpose. Actions (starting chats, sending messages, answering for you) need a
  reason the description makes obvious.
- **Network.** Every host in `network.hosts`, what is sent there and what triggers it.
  Secrets (`secrets`) go only to the hosts that need them.
- **Command line.** For `cli`, the binary and each command, and that write commands are
  marked as writes.
- **Background and agent tools.** What runs without a screen open, and what agents can
  call.
- **Readability.** Whether the scripts can be read. Minified or generated code needs its
  source available at the same commit.

Record concrete harmful behaviour, such as sending chats or secrets somewhere the
description doesn't say, hiding what it does, or acting outside its purpose, with the
input that triggers it and its effect. Ordinary network requests, settings reads and
command-line use are judged in context; their presence alone is not a finding.

## Completing the listing

Reviewers may edit the entry, its name, description and screenshots on the pull request,
using verified information. Do the routine work rather than handing it back to the
author; ask the author only for what's outside your reach, such as a screenshot or a
change to the package.

## Outcomes

Approve and merge once the package is reviewed and the requirements are met. Request
changes only for a concrete blocker, saying exactly what to change and where. Leave one
short outcome comment on every reviewed pull request, approvals included, with the
review data (commit, scope inspected, capabilities, hosts, findings) in a collapsed block.

Close a clearly malicious submission with the evidence. Hold anything seriously unsafe
for the maintainers with the specific question to decide.
