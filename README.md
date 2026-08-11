# Unity UGS CLI Skill

> A safety-first Codex skill for operating the [Unity Gaming Services CLI](https://services.docs.unity.com/guides/ugs-cli/latest/general/overview/).

Use this skill when you need to inspect, configure, deploy, fetch, automate, or troubleshoot Unity Gaming Services from the command line. It favors live CLI help, explicit targets, JSON output, dry runs, and verification over guesses.

## Quick start

### 1. Install and verify the CLI

Follow [Get the UGS CLI](#get-the-ugs-cli), then confirm the executable available to your shell:

```text
ugs --version
ugs --help
```

### 2. Configure a safe session

Most UGS commands need a project ID and environment name. Prefer session-only environment variables, which leave no persistent target configuration behind:

```powershell
$env:UGS_CLI_PROJECT_ID = "<project-id>"
$env:UGS_CLI_ENVIRONMENT_NAME = "staging"
ugs status --json
```

Create the project ID and environment values from the Unity dashboard as described in Unity's [common configuration guide](https://services.docs.unity.com/guides/ugs-cli/latest/general/get-started/setup-a-common-configuration/).

### 3. Keep the service-account secret out of the skill

UGS uses a **Service Account key ID** and a **Service Account secret key**; it does not require an SSH private-key file. Create the service account and grant only its required project roles in the Unity dashboard, following Unity's [authentication guide](https://services.docs.unity.com/guides/ugs-cli/latest/general/get-started/get-authenticated/).

| Data | Store it in | Never put it in |
| --- | --- | --- |
| Service Account key ID | Session environment variable or CI secret store | The skill, committed config, or a prompt |
| Service Account secret key | OS or cloud secret manager; inject it into the current process or CI job | A file in the repository, `.env` committed to Git, shell history, command line, logs, or a prompt |

For a local PowerShell session, inject the secret only after a secure prompt and clear it when finished:

```powershell
$env:UGS_CLI_SERVICE_KEY_ID = "<service-key-id>"
$secret = Read-Host "UGS service secret" -AsSecureString
$env:UGS_CLI_SERVICE_SECRET_KEY = [System.Net.NetworkCredential]::new("", $secret).Password
ugs status --json
Remove-Item Env:\UGS_CLI_SERVICE_SECRET_KEY
Remove-Variable secret
```

For a local macOS or Linux shell session, use the same session-only pattern:

```bash
export UGS_CLI_PROJECT_ID="<project-id>"
export UGS_CLI_ENVIRONMENT_NAME="staging"
export UGS_CLI_SERVICE_KEY_ID="<service-key-id>"
read -r -s -p "UGS service secret: " UGS_CLI_SERVICE_SECRET_KEY
printf '\n'
export UGS_CLI_SERVICE_SECRET_KEY
ugs status --json
unset UGS_CLI_SERVICE_SECRET_KEY
```

For CI, use the platform's secret store rather than literal values in the workflow:

```yaml
env:
  UGS_CLI_PROJECT_ID: ${{ vars.UGS_CLI_PROJECT_ID }}
  UGS_CLI_ENVIRONMENT_NAME: ${{ vars.UGS_CLI_ENVIRONMENT_NAME }}
  UGS_CLI_SERVICE_KEY_ID: ${{ secrets.UGS_CLI_SERVICE_KEY_ID }}
  UGS_CLI_SERVICE_SECRET_KEY: ${{ secrets.UGS_CLI_SERVICE_SECRET_KEY }}
```

### 4. Start with a read-only prompt

```text
Use $unity-ugs-cli to inspect UGS CLI status without changing anything.
OS: <Windows/macOS/Linux and architecture>
UGS CLI: <absolute path, or "on PATH">
Target: project <project-id>, environment <environment>
Authentication: service-account variables are already injected into this session.
Do not persist CLI configuration or mutate remote resources.
```

Only after reviewing the result, authorize a dry run or a real operation explicitly. Never paste the service-account secret into the prompt.

## Codex plugin

This skill is also packaged as the personal Codex plugin `unity-ugs-cli`.

- [Open the plugin in Codex](codex://plugins/unity-ugs-cli?marketplacePath=C%3A%5CUsers%5CW0lfEnd%5C.agents%5Cplugins%5Cmarketplace.json)
- [Share the plugin from Codex](codex://plugins/unity-ugs-cli?marketplacePath=C%3A%5CUsers%5CW0lfEnd%5C.agents%5Cplugins%5Cmarketplace.json&mode=share)

> These links use this machine's personal marketplace path. Other users should open the repository and install the plugin from their own Codex marketplace configuration.

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

### Platform notes

| Platform | Binary notes | What to tell the skill |
| --- | --- | --- |
| Windows | Use npm or the Windows release binary. No `chmod` step is needed. | `OS: Windows; UGS CLI: C:\\tools\\ugs.exe` |
| macOS | Use npm, Unity's Bash installer, or a macOS release binary that matches Apple Silicon or Intel. Mark a downloaded binary executable. | `OS: macOS (Apple Silicon); UGS CLI: /opt/ugs/ugs` |
| Linux | Use npm, Unity's Bash installer, or the Linux release binary that matches the runner or host architecture. Mark a downloaded binary executable. | `OS: Linux x64; UGS CLI: /opt/ugs/ugs` |

If the executable is not on `PATH`, pass its absolute location to the skill. State explicitly if Codex is authorized to install the CLI; the skill will not make a persistent installation by default.

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
| Operating system and CPU architecture | Selects the correct binary and shell conventions. | `OS: macOS (Apple Silicon)` |
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
