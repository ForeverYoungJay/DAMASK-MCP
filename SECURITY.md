# Security Policy

## Supported Versions

Security fixes are handled on the default branch until a formal release policy is published.

## Reporting a Vulnerability

Please do not open public issues for vulnerabilities.

Report suspected vulnerabilities privately to the project maintainer or repository owner. Include:

- affected version or commit
- steps to reproduce
- expected and observed behavior
- any relevant logs with secrets removed

## Security Model

DAMASK MCP is designed for local or controlled scientific workflows:

- file writes are restricted to `workspaces/`
- runner subprocess calls avoid `shell=True`
- result-mutating tools are restricted to workspace-local paths
- MCP responses summarize large data instead of returning full arrays

Hosted deployments should review which tools are exposed, especially runner tools that execute `DAMASK_grid`.
