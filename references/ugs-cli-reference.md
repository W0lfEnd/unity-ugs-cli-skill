# UGS CLI reference

This compact reference supplements live `--help`. It is not a substitute for checking the installed executable.

## Contents

- [Source-of-truth order](#source-of-truth-order)
- [Version-sensitive behavior](#version-sensitive-behavior)
- [Core context and variables](#core-context-and-variables)
- [Top-level command map](#top-level-command-map)
- [Deployable configuration types](#deployable-configuration-types)
- [Deploy, fetch, and deployment definitions](#deploy-fetch-and-deployment-definitions)
- [Authentication and CI](#authentication-and-ci)
- [Troubleshooting matrix](#troubleshooting-matrix)
- [Official sources](#official-sources)

## Source-of-truth order

Use this order when sources disagree:

1. Installed `<ugs> --version` plus hierarchical `<ugs> ... --help`.
2. Official Unity documentation for the matching CLI version.
3. Official GitHub release notes and changelog.
4. This bundled snapshot.

The snapshot was researched on 2026-08-11 against Unity's `latest` documentation, the official repository, and a local `2.0.0-exp.1` Windows binary. It intentionally contains no machine-specific executable path.

## Version-sensitive behavior

The official `v2.0.0-exp.1` notes identify these breaking or notable changes:

- Remove Multiplay Hosting / Game Server Hosting commands: `multiplay-hosting`, `mh`, `gsh`, and `game-server-hosting`.
- Resolve targeting configuration in the order command arguments, environment variables, stored config: `ARGS > ENV > CONFIG`.
- Skip Matchmaker pools that still use Multiplay hosting during deploy/fetch and report them as errors.
- Generate Matchmaker templates with Match ID hosting.
- Add Unity Hub authentication via `login --unity-hub` and `UGS_CLI_USE_HUB_AUTH`.
- Add `UGS_CLI_CONFIG_DIR` to relocate CLI configuration.
- Add Purchasing config-as-code and catalog listing.
- Add Leaderboards score/bucket operations, Cloud Code module OpenAPI retrieval, Matchmaker inspection commands, and Triggers DLQ operations.

Unity's latest login page can still describe older credential precedence. For 2.x, rely on the release notes and `status`; for 1.x, consult its versioned docs.

## Core context and variables

### Base commands

| Need | Command shape | Notes |
|---|---|---|
| Version | `<ugs> --version` | Always capture first. |
| Root discovery | `<ugs> --help` | Lists modules installed in this binary. |
| Authentication source | `<ugs> status --json` | Warns about multiple configured sources. |
| Stored project | `<ugs> config get project-id` | Read-only. |
| Stored environment | `<ugs> config get environment-name` | Read-only. |
| Persist project | `<ugs> config set project-id <id>` | Changes local CLI config. |
| Persist environment | `<ugs> config set environment-name <name>` | Changes local CLI config. |
| Environments | `<ugs> env list --json` | Authenticated service call. |
| Select environment | `<ugs> env use <name>` | Changes persistent local context. |
| Deploy | `<ugs> deploy <paths...> [options]` | Multiple files/directories; `.` means current directory. |
| Fetch | `<ugs> fetch <path> [options]` | One destination directory; `.` means current directory. |

The tested 2.0 help also exposes a `bucket-name` stored configuration key for CCD workflows. Check `config --help` before relying on it in another version.

### Official environment variables

| Variable | Purpose |
|---|---|
| `UGS_CLI_PROJECT_ID` | Target Unity Cloud project. |
| `UGS_CLI_ENVIRONMENT_NAME` | Target services environment. |
| `UGS_CLI_SERVICE_KEY_ID` | Service account key ID. |
| `UGS_CLI_SERVICE_SECRET_KEY` | Service account secret; treat as a secret. |
| `UGS_CLI_TELEMETRY_DISABLED` | Disable CLI telemetry when set. |
| `UGS_CLI_USE_HUB_AUTH` | Select Unity Hub authentication in supported 2.x builds. |
| `UGS_CLI_CONFIG_DIR` | Override the CLI configuration directory in supported 2.x builds. |

`UGS_CLI_EXECUTABLE` is not a Unity option. It is an optional session-only convention used by this skill's resolver script.

## Top-level command map

The tested `2.0.0-exp.1` binary exposes:

| Area | Module/alias | Main command groups seen in help |
|---|---|---|
| Access Control | `access`, `ac` | project/player policy get, upsert, statement delete, `new-file` |
| Cloud Content Delivery | `ccd` | `buckets`, `entries`, `releases`, `badges` |
| Cloud Code | `cloud-code`, `cc` | `scripts`, `modules` |
| Cloud Save | `cloud-save`, `cs` | `data player`, `data custom`, `data index` |
| Economy | `economy`, `ec` | currencies, inventory, virtual/real-money purchases, list/delete/publish |
| Environments | `env` | add, delete, list, use |
| Leaderboards | `leaderboards`, `lb` | config create/update/get/list/import/export/reset; scores; buckets |
| Lobby | `lobby` | lobby CRUD/query/join; player; config; import/export |
| Matchmaker | `matchmaker` | `new-file`, queue list, environment config, restrictions |
| Observability | `observability`, `obs` | logs list |
| Player Authentication | `player` | create, delete, disable, enable, get, list |
| In-App Purchasing | `purchasing`, `iap` | catalog list, `new-file`; deploy/fetch through root |
| Remote Config | `remote-config`, `rc` | import, export, `new-file`; deploy/fetch through root |
| Scheduler | `scheduler`, `sched` | list, `new-file`; deploy/fetch through root |
| Triggers | `triggers`, `tr` | get/list/delete, `new-file`, DLQ get/list/replay/discard |

Useful nested surfaces from tested help:

- CCD: bucket permissions; entry copy/download/info/list/sync/update/delete; releases create/info/list/promote/update; badges create/delete/list.
- Cloud Code scripts: create/update/get/list/delete/publish/import/export/new-file.
- Cloud Code modules: get/get-spec/list/delete/import/export/new-file.
- Leaderboards scores: list/get/get-range/get-by-player-ids/delete/purge. Buckets: list and scores.
- Triggers DLQ: list/get/replay/replay-all/discard/discard-all.

Always inspect leaf help for required bodies, pagination, identifiers, player impersonation, bucket selection, and destructive flags.

## Deployable configuration types

The tested `new-file --help` output reports:

| Service/config | Extension or source | Generator |
|---|---|---|
| Access project policy | `.ac` | `access new-file` |
| Cloud Code JavaScript | `.js` | `cloud-code scripts new-file` |
| Cloud Code C# module | `.sln`, `.csproj`, `.cs`; packaged `.ccm` | `cloud-code modules new-file` |
| Economy currency | `.ecc` | `economy currency new-file` |
| Economy inventory item | `.eci` | `economy inventory new-file` |
| Economy real-money purchase | `.ecr` | `economy real-money-purchase new-file` |
| Economy virtual purchase | `.ecv` | `economy virtual-purchase new-file` |
| Leaderboard | `.lb` | `leaderboards new-file` |
| Matchmaker queue | `.mmq` | `matchmaker new-file` |
| Purchasing item | `.ucat` | `purchasing new-file` |
| Purchasing catalog CSV | `.catalog.csv` | `purchasing new-file --csv` |
| Remote Config | `.rc` | `remote-config new-file` |
| Scheduler | `.sched` | `scheduler new-file` |
| Trigger | `.tr` | `triggers new-file` |
| Deployment definition | `.ddef` | Create JSON manually from the documented structure. |

Most JSON config templates include a Unity-hosted `$schema`. Preserve it and validate before deployment. Do not edit `.ccm` as text; it is a packaged module artifact.

Root deploy support in current Unity documentation includes Access, Cloud Code scripts/modules, Economy, Leaderboards, Matchmaker, Remote Config, Scheduler, and Triggers. The tested 2.0 release adds Purchasing. Root fetch support can be narrower, notably Cloud Code JavaScript rather than all Cloud Code artifacts. Confirm service support with current help.

## Deploy, fetch, and deployment definitions

Common options from tested help:

- `-p, --project-id`
- `-e, --environment-name`
- `-s, --services`
- `--dry-run`
- `--reconcile`
- `-j, --json`
- `-q, --quiet`

Use service filters to minimize the permission and change surface. Reconcile is service- and version-sensitive; inspect the proposed changes and current leaf help.

A `.ddef` file is JSON:

```json
{
  "name": "example",
  "excludePaths": ["**/Tests/**"]
}
```

Rules from Unity's documentation:

- Group files by the `.ddef` directory and descendants.
- Stop ownership at a nested `.ddef` boundary.
- Allow only one definition in a directory.
- Apply `excludePaths` as glob-like patterns relative to the definition's directory.
- Support deploy and fetch.
- Historically, reconcile does not apply to a definition because the definition itself has no server representation. Re-check on the installed version.
- In 2.x, targeting a folder can load definitions found under it.

## Authentication and CI

For local interactive work:

- Prefer Unity Hub auth on supported 2.x builds when appropriate.
- Otherwise use interactive `login` or secret-through-stdin.
- Run `status --json` after login and before mutations.

For CI:

1. Pin and verify the CLI artifact.
2. Inject project, environment, key ID, and secret at runtime.
3. Mask secret variables and avoid shell tracing.
4. Grant the service account only required project roles.
5. Run `--version`, `status --json`, target checks, then dry-run.
6. Gate the real deploy behind the intended branch/environment approval.
7. Use JSON stdout for parsing and preserve stderr as diagnostics.

Unity documentation shows GitHub Actions, Docker, Jenkins, and Unity Build Automation examples. Replace any literal example credentials with the platform's secret-store syntax. Never bake service secrets into a Docker `ENV` layer.

## Troubleshooting matrix

| Symptom | Checks | Likely resolution |
|---|---|---|
| Command/option missing | `--version`; help at each parent command; release notes | Use the installed syntax, install the required version only if authorized. |
| Wrong project/environment | Explicit flags, `UGS_CLI_*`, stored config, `env list` | Remove competing context; on 2.x use `ARGS > ENV > CONFIG`. |
| Authentication failure / 401 | `status --json`; Hub availability; service key injection | Select one valid credential source; rotate/reinject without exposing secrets. |
| Authorization failure / 403 | Target project/environment; project-specific roles | Add only required roles to the service account or use the correct account. |
| Deploy file ignored | Extension, schema, service filter, `.ddef` ownership/excludes | Correct the type/scope and rerun dry-run. |
| Unexpected deletions proposed | `--reconcile`, wrong service/target/path | Stop; correct scope; require explicit approval before proceeding. |
| Fetch overwrites local work | Destination status/diff, dry-run support | Use a clean destination or preserve changes before fetching. |
| JSON parser fails | Was `--json` used? Are stderr and stdout separate? | Parse stdout only; retain stderr as logs. |
| Cloud Code JS tooling fails | Installed Node.js and version-specific requirements | Inspect Cloud Code help/docs and install dependencies only when authorized. |
| Matchmaker pool skipped on 2.x | Hosting type in `.mmq` | Migrate from removed Multiplay hosting to a supported host type. |

## Official sources

- Overview: <https://services.docs.unity.com/guides/ugs-cli/latest/general/overview/>
- Installation: <https://services.docs.unity.com/guides/ugs-cli/latest/general/get-started/install-the-cli/>
- Common configuration: <https://services.docs.unity.com/guides/ugs-cli/latest/general/get-started/setup-a-common-configuration/>
- Login: <https://services.docs.unity.com/guides/ugs-cli/latest/general/base-commands/login/>
- Deploy: <https://services.docs.unity.com/guides/ugs-cli/latest/general/base-commands/deploy/>
- Fetch: <https://services.docs.unity.com/guides/ugs-cli/latest/general/base-commands/fetch/>
- Deployment definitions: <https://services.docs.unity.com/guides/ugs-cli/latest/general/deployment-definition/what-is-deployment-definition/>
- Deployment-definition commands: <https://services.docs.unity.com/guides/ugs-cli/latest/general/deployment-definition/commands-for-deployment-definition/>
- Project roles: <https://services.docs.unity.com/guides/ugs-cli/latest/general/troubleshooting/project-roles/>
- 403 troubleshooting: <https://services.docs.unity.com/guides/ugs-cli/latest/general/troubleshooting/unauthorized-error-403/>
- Stdout/stderr piping: <https://services.docs.unity.com/guides/ugs-cli/latest/general/samples/stdout-stderr-piping/>
- GitHub Actions sample: <https://services.docs.unity.com/guides/ugs-cli/latest/general/samples/ci-cd-pipeline-usage/github-actions/>
- Official repository: <https://github.com/Unity-Technologies/unity-gaming-services-cli>
- Official releases: <https://github.com/Unity-Technologies/unity-gaming-services-cli/releases>
- Changelog: <https://github.com/Unity-Technologies/unity-gaming-services-cli/blob/main/CHANGELOG.md>
