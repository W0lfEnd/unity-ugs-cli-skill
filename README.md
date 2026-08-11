# Unity UGS CLI Skill

> A safety-first Codex skill for operating the [Unity Gaming Services CLI](https://services.docs.unity.com/guides/ugs-cli/latest/general/overview/).

Use this skill when you need to inspect, configure, deploy, fetch, automate, or troubleshoot Unity Gaming Services from the command line. It favors live CLI help, explicit targets, JSON output, dry runs, and verification over guesses.

## Get the UGS CLI

Install the CLI from Unity's [official installation guide](https://services.docs.unity.com/guides/ugs-cli/latest/general/get-started/install-the-cli/). Choose the method that fits your environment:

1. **npm** — with Node.js and npm installed, run `npm install -g ugs`.
2. **Release binary** — download the correct operating-system asset from the [official GitHub Releases](https://github.com/Unity-Technologies/unity-gaming-services-cli/releases) page. On macOS or Linux, mark the downloaded executable as runnable with `chmod +x <path-to-executable>`.
3. **macOS/Linux installer** — use the Bash installer and version-pinning options published in Unity's installation guide.

Verify any installation before using it:

```text
ugs --version
ugs --help
```

If the executable is not on `PATH`, pass its location to the skill, for example: `UGS CLI: <absolute-path-to-executable>`. State explicitly if Codex is authorized to install the CLI; the skill will not make a persistent installation by default.

## Use it in Codex

Invoke the skill directly in your prompt:

```text
Use $unity-ugs-cli to <describe the task>.
```

For the best result, state the target, the intended operation, and whether Codex may make changes. Give credentials through Unity Hub, your shell environment, or a CI secret store — **never paste a service-account secret into the prompt**.

## What to provide with a prompt

| Provide | Why it matters | Example |
| --- | --- | --- |
| CLI location, if it is not on `PATH` | Lets Codex verify the exact installed command surface. | `UGS CLI: C:\\tools\\ugs.exe` |
| Unity project and environment | Prevents changes against the wrong target. | `Project: <project-id>; environment: staging` |
| Service and resource scope | Keeps commands narrow and reviewable. | `Remote Config, file config/live.rc` |
| Desired action | Separates inspection, local file writes, and remote mutations. | `Dry-run deploy only; do not apply it yet.` |
| Source files or request body | Allows validation before an operation. | `Use the attached .ddef and its directory.` |
| Constraints | Captures safety, CI, or rollback requirements. | `Use JSON output and do not change stored CLI config.` |

Do not include service-account secrets, access tokens, `.env` contents, or private keys. Refer to a secret by its environment-variable name instead, such as `UGS_CLI_SERVICE_SECRET_KEY`.

## Prompt recipes

### Inspect without changing anything

```text
Use $unity-ugs-cli to inspect the UGS CLI and list the Remote Config resources
for project <project-id> in the staging environment. Do not change any local
configuration or remote resource. Return JSON-derived findings and the exact
help path you used.
```

### Validate a deployment

```text
Use $unity-ugs-cli to dry-run deployment of <path-to-config-directory> for
Remote Config and Economy to project <project-id>, environment <environment>.
First validate the files and confirm the target. Do not run the real deploy;
summarize every proposed create, update, skip, and deletion.
```

### Apply an approved change

```text
Use $unity-ugs-cli to deploy <path> to project <project-id>, environment
<environment>, for the <service> service. A reviewed dry run has been approved.
Do not use --reconcile. Verify the resulting state after deployment and redact
all credentials in the report.
```

### Prepare CI/CD automation

```text
Use $unity-ugs-cli to add a GitHub Actions validation workflow for UGS config
in <path>. Pin the CLI version, use the existing secret names
UGS_CLI_SERVICE_KEY_ID and UGS_CLI_SERVICE_SECRET_KEY, run a dry run on pull
requests, and never put secret values in the workflow file.
```

## Safety defaults

- Inspect the CLI version and hierarchical `--help` before relying on syntax.
- Confirm project, environment, service, and path before any write.
- Prefer `--json` for automation and keep stdout separate from diagnostics.
- Run `deploy --dry-run` before an authorized real deployment when supported.
- Treat `--reconcile`, deletion, reset, purge, and environment removal as destructive actions that need explicit approval.
- Verify a completed deployment with a relevant list, get, fetch, or status operation.

## Included resources

```text
SKILL.md                         # Agent workflow and safety rules
agents/openai.yaml               # Codex UI metadata
scripts/find_ugs.py              # Session-local UGS CLI resolver
references/ugs-cli-reference.md  # Version notes, command map, and links
```

`SKILL.md` is the canonical instruction set for Codex; this README is the GitHub-facing guide for people using the skill.
