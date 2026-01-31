#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/k0ra09/Remna-Monitor"
DIR="Remna-Monitor"

echo "🧠 Remna Monitor installer"
echo "=========================="

# -------- helpers --------
fail() {
  echo "❌ $1"
  exit 1
}

require() {
  command -v "$1" >/dev/null 2>&1 || fail "Required command not found: $1"
}

set_env() {
  local key="$1"
  local val="$2"

  if grep -q "^$key=" .env 2>/dev/null; then
    sed -i "s|^$key=.*|$key=$val|" .env
  else
    echo "$key=$val" >> .env
  fi
}

# -------- checks --------
require git
require docker

docker compose version >/dev/null 2>&1 || fail "docker compose plugin not found"

INSTALL_MODE="${INSTALL_MODE:-}"

[[ -z "$INSTALL_MODE" ]] && fail "INSTALL_MODE is required (agent | bot | all)"

case "$INSTALL_MODE" in
  agent|bot|all) ;;
  *) fail "INSTALL_MODE must be: agent | bot | all" ;;
esac

# -------- clone --------
if [[ ! -d "$DIR" ]]; then
  echo "📦 Cloning repository..."
  git clone "$REPO_URL"
fi

cd "$DIR"

# -------- env --------
[[ ! -f .env ]] && cp .env.example .env

# -------- agent --------
if [[ "$INSTALL_MODE" == "agent" || "$INSTALL_MODE" == "all" ]]; then
  [[ -z "${AGENT_NAME:-}" ]] && fail "AGENT_NAME is required"
  [[ -z "${AGENT_TOKEN:-}" ]] && fail "AGENT_TOKEN is required"

  set_env AGENT_NAME "$AGENT_NAME"
  set_env AGENT_TOKEN "$AGENT_TOKEN"
fi

# -------- bot --------
if [[ "$INSTALL_MODE" == "bot" || "$INSTALL_MODE" == "all" ]]; then
  [[ -z "${BOT_TOKEN:-}" ]] && fail "BOT_TOKEN is required"
  [[ -z "${AGENTS:-}" ]] && fail "AGENTS is required"

  set_env BOT_TOKEN "$BOT_TOKEN"
  set_env AGENTS "$AGENTS"

  # bot тоже использует AGENT_TOKEN
  [[ -z "${AGENT_TOKEN:-}" ]] && fail "AGENT_TOKEN is required for bot"
  set_env AGENT_TOKEN "$AGENT_TOKEN"
fi

# -------- run --------
echo "🚀 Starting services..."

case "$INSTALL_MODE" in
  agent)
    docker compose up -d --build agent
    echo "📡 Agent installed and running"
    ;;
  bot)
    docker compose up -d --build bot
    echo "🤖 Bot installed and running"
    ;;
  all)
    docker compose up -d --build
    echo "🤖 Bot + 📡 Agent installed and running"
    ;;
esac

echo "✅ Installation complete"
