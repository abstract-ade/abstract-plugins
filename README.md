# Abstract plugins

The reviewed plugin registry behind Settings › Plugins in
[Abstract](https://github.com/endeken-com/abstract). Each listing pins one
GitHub folder to one commit. Merging a listing approves that exact commit.

Abstract reads `registry.json` from this repository's `main` branch. Its own first-party
plugins are listed here too, from their repositories `abstract-ade/abstract-plugin-<name>`.
The process is copied in spirit from Paseo's registry,
[getpaseo/plugins](https://github.com/getpaseo/plugins) (Apache-2.0).

## Installing

A listed plugin installs its approved commit:

```sh
abstract plugin add abstract-ade/kanban
```

or **Add from GitHub…** in Settings › Plugins with the same `owner/slug`. The
gallery lists every entry here, marked **Reviewed**.

Any repository installs without a listing, marked **Not reviewed**:

```sh
abstract plugin add acme/abstract-review
abstract plugin add acme/monorepo/plugins/review@v1.2
```

Either way Abstract checks the package before anything is installed (no executables,
links or paths outside it) and shows what it can access before you turn it on.

## Submitting a plugin

1. Push the plugin to a **public GitHub repository**: `manifest.json` at the root of
   the plugin's folder, with its pages, scripts and assets beside it. Abstract packages
   are static: there is no build step and nothing is installed when it runs.
2. Open a pull request here that adds one entry to `registry.json` (see below). Use the
   plugin's name as the title, and say what it does, what it needs (accounts, tokens,
   command-line tools) and, for a plugin with a screen, include a screenshot.
3. A person reviews the package at that commit under [REVIEW.md](REVIEW.md), without
   running it, completes the listing, and merges it or says exactly what's missing.

The commit is optional when you open the pull request; the reviewer resolves `main` if
you leave it out, and records the exact commit reviewed before merging.

**Updates are manual.** Open a pull request that changes `commit` to the new one. People
who installed the listing are offered the newly approved commit when they check for
updates; one that asks for more access stays off until they review it.

**Removal.** Open an issue or a pull request naming your listing and why. The reviewer
checks the request comes from the listing's author. Removing a listing leaves your
repository and existing installs alone.

## registry.json

```json
{
  "format": 1,
  "plugins": [
    {
      "owner": "acme",
      "slug": "review",
      "name": "Review helper",
      "description": "One sentence on what it does.",
      "pluginId": "dev.acme.review",
      "repository": "acme/abstract-plugins",
      "path": "plugins/review",
      "commit": "0123456789abcdef0123456789abcdef01234567",
      "screenshots": ["https://raw.githubusercontent.com/acme/abstract-plugins/0123456789abcdef0123456789abcdef01234567/plugins/review/screenshot.png"],
      "reviewedAt": "2026-11-05T12:00:00Z"
    }
  ]
}
```

| Field | Meaning |
|---|---|
| `owner`, `slug` | The listing's id, `owner/slug`, what people type. `owner` is the GitHub account that owns the repository. |
| `name`, `description` | Shown in the gallery. One plain sentence. |
| `pluginId` | The `id` in the plugin's `manifest.json`. A commit holding another id is refused. |
| `repository` | `owner/repo` on GitHub. |
| `path` | The plugin's folder in the repository; leave it out for the root. |
| `commit` | The reviewed commit, all 40 lowercase characters. Never a branch or tag. |
| `screenshots` | `https` image URLs, best pinned to the same commit. Required for a plugin with a screen. |
| `reviewedAt` | When this commit was approved, in UTC. |

Abstract refuses the whole file when one entry is malformed, so the checks below run on
every pull request.

## Checks

CI (`.github/check-registry.py`) validates `registry.json` the way Abstract reads it
(format, unique ids, GitHub `owner/repo`, full lowercase commits, clean paths, `https`
screenshots) and, for every entry, fetches that one commit and checks the package as
Abstract does before installing: `manifest.json` carrying `pluginId`, no executables,
links or paths outside the folder, under 25 MB. It reads files only; nothing runs.
