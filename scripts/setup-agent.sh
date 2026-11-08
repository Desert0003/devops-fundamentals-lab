#!/usr/bin/env bash
# Install and run a self-hosted Azure Pipelines agent inside this Codespace.
# Usage: bash scripts/setup-agent.sh https://dev.azure.com/<your-org> <PAT>
set -euo pipefail
ORG_URL="${1:?Azure DevOps organization URL, e.g. https://dev.azure.com/myorg}"
PAT="${2:?Personal Access Token with Agent Pools (Read & manage) scope}"
AGENT_VERSION="${AGENT_VERSION:-5.277.0}"
POOL="${POOL:-Default}"
AGENT_NAME="${AGENT_NAME:-codespace-$(hostname | cut -c1-12)}"
AGENT_DIR="${AGENT_DIR:-$HOME/azagent}"

mkdir -p "$AGENT_DIR" && cd "$AGENT_DIR"
if [ ! -f ./config.sh ]; then
  echo ">> Downloading agent $AGENT_VERSION"
  curl -fsSL -o agent.tar.gz "https://download.agent.dev.azure.com/agent/${AGENT_VERSION}/vsts-agent-linux-x64-${AGENT_VERSION}.tar.gz"
  tar -xzf agent.tar.gz && rm agent.tar.gz
  sudo ./bin/installdependencies.sh >/dev/null
fi
if [ ! -f .agent ]; then
  echo ">> Registering agent '$AGENT_NAME' in pool '$POOL'"
  ./config.sh --unattended --url "$ORG_URL" --auth pat --token "$PAT" \
    --pool "$POOL" --agent "$AGENT_NAME" --acceptTeeEula --replace
fi
echo ">> Agent is running. Keep this terminal open (Ctrl+C to stop)."
./run.sh
