---
name: use-ugs-cli
description: Operate Unity Gaming Services through the UGS CLI. Use when Codex needs to discover or install the CLI, inspect its version and help, configure a Unity project or environment, authenticate with Unity Hub or a service account, manage UGS resources, create deployable configuration files, run deploy/fetch with dry-run or reconcile, build CI/CD automation, parse JSON output, work with .ddef/.rc/.js/.sln/.csproj/.cs/.ecc/.eci/.ecr/.ecv/.lb/.ac/.mmq/.ucat/.catalog.csv/.sched/.tr files, or troubleshoot UGS CLI permissions, credentials, configuration, and version differences.
---

# Use UGS CLI

Treat the installed executable and its hierarchical `--help` output as the command authority. Keep executable locations session-local; never write a user-provided binary path into this skill, a repository, or persistent project configuration.

## Apply the safety rules

- Inspect before mutating. Run version, help, status, target, and relevant list/get commands first.
- Do not install the CLI, log in persistently, change stored configuration, write fetched files, or mutate remote UGS resources unless the user's request authorizes that action.
- Never print, echo, log, commit, or place a service-account secret on a command line. Use a CI secret store, environment injection, or `--secret-key-stdin`.
- Prefer `--json` for automation and parse stdout separately from stderr.
- Run `deploy --dry-run` before a real deploy whenever the installed command supports it.
- Treat `--reconcile`, delete, purge, reset, import-with-reconcile, and environment deletion as destructive. Confirm the exact project, environment, service, and scope immediately before execution. Require explicit user intent for deletion.
- Preserve unrelated local changes. Before `fetch`, inspect the destination and use version-control status or a backup strategy appropriate to the workspace.
- Redact credential values from reports. Project IDs and environment names are targeting data, not authentication secrets, but avoid exposing them beyond the requested scope.

## Resolve the executable per session

1. Prefer a path explicitly supplied for the current task.
2. Otherwise run the bundled `scripts/find_ugs.py`, resolved relative to this `SKILL.md`; it checks the skill-local `UGS_CLI_EXECUTABLE` override and common UGS command names on `PATH` without scanning arbitrary directories.
3. If unresolved, check the current shell's command lookup. Ask for the executable location or, when installation is in scope, use an official installation method.
4. Store the resolved invocation only in a task-specific shell variable such as `$ugsCli` or `ugs_cli`. Do not assume the executable is named exactly `ugs`.

Examples:

```powershell
$ugsCli = & python '<skill-dir>/scripts/find_ugs.py' --cli '<current-path-from-user>'
& $ugsCli --version
& $ugsCli --help
```

```bash
ugs_cli="$(python3 '<skill-dir>/scripts/find_ugs.py' --cli '<current-path-from-user>')"
"$ugs_cli" --version
"$ugs_cli" --help
```

Use `python <skill-dir>/scripts/find_ugs.py --cli <path> --verify --json` when a machine-readable discovery result is useful.

## Follow the operating workflow

### 1. Pin the live command surface

Run:

```text
<ugs> --version
<ugs> --help
<ugs> <module> --help
<ugs> <module> <command> --help
```

Repeat help at every nested command level needed to expose arguments and options. Do this even when a command appears in the bundled reference: UGS CLI releases can add, remove, or reorder commands and configuration precedence.

Read [references/ugs-cli-reference.md](references/ugs-cli-reference.md) when choosing a module, deployable file type, authentication mode, CI pattern, or version-specific behavior.

### 2. Establish the target

Inspect the effective targeting inputs before authenticated calls:

```text
<ugs> config get project-id
<ugs> config get environment-name
<ugs> status --json
```

Use `env list --json` when authentication is already available and the environment needs verification. Select one targeting strategy:

- Pass `--project-id` and `--environment-name` for explicit one-off operations.
- Inject `UGS_CLI_PROJECT_ID` and `UGS_CLI_ENVIRONMENT_NAME` in CI.
- Use `config set project-id ...` and `config set environment-name ...` for an intentionally persistent local default.
- Use `env use <environment-name>` only after confirming the project and desired persistent context.

For UGS CLI 2.x, expect command arguments to override environment variables, which override stored configuration. For older versions, verify behavior with `status`, current help, and official versioned documentation.

### 3. Choose authentication deliberately

- For an interactive workstation with Unity Hub, prefer `login --unity-hub` when supported by the installed version.
- For CI, prefer the `UGS_CLI_SERVICE_KEY_ID` and `UGS_CLI_SERVICE_SECRET_KEY` variables injected from the platform's secret store. Never bake them into images or workflow files.
- For non-interactive local login, send the secret through stdin and pass only the key ID as an argument:

```text
<secret-provider> | <ugs> login --service-key-id <key-id> --secret-key-stdin
```

- Do not run `login` merely to test whether credentials exist; run `status --json` first.
- If multiple credential sources exist, report the active source and remove ambiguity before a mutation.

### 4. Classify the operation

- Read-only: `status`, `config get`, `env list`, service `list`, `get`, `info`, and observability queries.
- Local generation: service `new-file`; inspect the generated extension, `$schema`, defaults, and diff before use.
- Local write: `fetch`, exports, downloads, and new-file creation.
- Remote mutation: deploy, create, update, upsert, publish, import, sync, promote, replay, and player or policy changes.
- Destructive: reconcile, delete, purge, reset, discard, logout, config deletion, and environment deletion.

Inspect the exact leaf help before executing any local write or remote operation.

### 5. Deploy configuration as code

1. Inspect the candidate files and their service-specific extensions.
2. Validate JSON and referenced `$schema` documents where available. Do not hand-convert `.ccm` archives.
3. Confirm project, environment, services, and paths.
4. Run a narrow dry run with explicit service filtering when supported:

```text
<ugs> deploy <path> --services <service> --project-id <project-id> --environment-name <environment> --dry-run --json
```

5. Review every proposed create, update, failure, skip, and deletion.
6. Run the same command without `--dry-run` only when authorized.
7. Add `--reconcile` only when the user explicitly intends remote content outside the local deployment set to be reconciled. Re-check leaf help because reconcile behavior and service support vary by version.

For `.ddef`, inspect its directory boundary, nested definitions, and `excludePaths`. A definition owns files below its directory until another definition boundary. Do not combine `.ddef` and `--reconcile` unless the installed version explicitly supports the intended behavior.

### 6. Fetch configuration safely

1. Use a dedicated, inspected destination.
2. Run `fetch ... --dry-run --json` when supported.
3. Review proposed local changes and service filters.
4. Fetch without dry-run only when local writes are authorized.
5. Inspect the resulting diff and report created, updated, skipped, and failed files.

Do not assume fetch supports every deployable service or artifact. Confirm with current help and the service documentation.

### 7. Operate individual services

Use the root help to select the installed module, then descend to leaf help. Prefer long command names in scripts and aliases for interactive use only. Pass request bodies as files rather than shell-embedded JSON when the command supports file paths; this reduces quoting errors and secret leakage.

For bulk or risky service operations:

1. List or get the current resource.
2. Save or summarize the current state when rollback would matter.
3. Validate the request body or config file.
4. Execute against explicit project/environment flags.
5. Re-read the resource and verify the intended state.

### 8. Automate in CI/CD

- Pin a CLI version for reproducibility unless the user explicitly wants latest.
- Verify the downloaded artifact by the strongest official checksum/signature mechanism available for that release.
- Inject secrets at runtime from the CI secret store; do not use literal `ENV` values in a Dockerfile.
- Run `--version`, `status --json`, and a non-secret target check before deployment.
- Use `--json`; capture stdout as machine data and stderr as diagnostics.
- Run dry-run in validation or pull-request jobs. Gate the real deploy to an approved branch/environment.
- Scope the service account to only the required project roles.

## Troubleshoot systematically

1. Capture the CLI version, full leaf command, exit code, stdout, and stderr without secrets.
2. Run `status --json` and check for competing credential sources.
3. Verify the effective project and environment; on 2.x remember `ARGS > ENV > CONFIG`.
4. For 401/authentication failures, verify the credential source and secret injection without displaying values.
5. For 403, verify the service account's project-specific roles and the targeted project/environment.
6. For an unknown command or option, inspect hierarchical help and release notes; do not guess from another version.
7. For deploy/fetch issues, inspect extensions, schema validation, `.ddef` boundaries, excludes, service filters, and dry-run results.
8. For automation parsing, separate stdout from stderr and request JSON output.

Consult the troubleshooting and version sections in [references/ugs-cli-reference.md](references/ugs-cli-reference.md) for the compact matrix and official source links.

## Report the result

Include:

- CLI version and resolved command source, but omit disposable absolute paths unless the user needs them.
- Target project/environment and credential source with all secrets redacted.
- Exact command shape with secret-bearing values replaced by placeholders.
- Exit status and a structured summary of stdout/stderr.
- Local files or remote resources created, updated, skipped, deleted, or failed.
- Whether dry-run was used and whether the final state was verified.

Do not claim a successful deploy from process exit alone; inspect per-item statuses and, when proportionate, verify with a subsequent list/get/fetch operation.
