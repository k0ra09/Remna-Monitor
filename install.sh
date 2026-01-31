#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/k0ra09/Remna-Monitor"
DIR="Remna-Monitor"

echo "🧠 Remna Monitor installer"
echo "=========================="

# ---------- helpers ----------
read_tty() {
  local var
  read -rp "$1" var </dev/tty
  echo "$var"
}

ensure_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "❌ Required command not found: $1"
    exit 1
  fi
}

# ---------- checks ----------
ensure_cmd git
ensure_cmd docker

if ! docker compose version >/dev/null 2>&1; then
  echo "❌ docker compose plugin not found"
  exit 1
fi

# ---------- mode selection ----------
if [[ -n "${INSTALL_MODE:-}" ]]; then
  case "$INSTALL_MODE" in
    agent) MODE="1" ;;
    bot) MODE="2" ;;
    all) MODE="3" ;;
    *)
      echo "❌ INSTALL_MODE must be: agent | bot | all"
      exit 1
      ;;
  esac
else
  while true; do
    echo
    echo "What do you want to install?"
    echo "1) Agent only"
    echo "2) Bot only"
    echo "3) Agent + Bot"
    MODE=$(read_tty "> ")

    case "$MODE" in
      1|2|3) break ;;
      *) echo "❌ Invalid choice, please enter 1, 2 or 3" ;;
    esac
  done
fi

# ---------- clone ----------
if [[ ! -d "$DIR" ]]; then
  echo "📦 Cloning repository..."
  git clone "$REPO_URL"
fi

cd "$DIR"

# ---------- env ----------
if [[ ! -f .env ]]; then
  echo "📝 Creating .env"
  cp .env.example .env
fi

set_env() {
  local key="$1"
  local val="$2"
  if grep -q "^$key=" .env; then
    sed -i "s|^$key=.*|$key=$val|" .env
  else
    echo "$key=$val" >> .env
  fi
}

# ---------- agent config ----------
if [[ "$MODE" == "1" || "$MODE" == "3" ]]; then
  if [[ -z "${AGENT_NAME:-}" ]]; then
    AGENT_NAME=$(read_tty "Agent name: ")
  fi

  if [[ -z "${AGENT_TOKEN:-}" ]]; then
    AGENT_TOKEN=$(read_tty "Agent token: ")
  fi

  set_env AGENT_NAME "$AGENT_NAME"
  set_env AGENT_TOKEN "$AGENT_TOKEN"
fi

# ---------- bot config ----------
if [[ "$MODE" == "2" || "$MODE" == "3" ]]; then
  if [[ -z "${BOT_TOKEN:-}" ]]; then
    BOT_TOKEN=$(read_tty "Telegram BOT_TOKEN: ")
  fi

  if [[ -z "${AGENTS:-}" ]]; then
    AGENTS=$(read_tty "Agents list (comma separated, http://ip:8000): ")
  fi

  set_env BOT_TOKEN "$BOT_TOKEN"
  set_env AGENTS "$AGENTS"
fi

# ---------- run ----------
echo
echo "🚀 Starting services..."

case "$MODE" in
  1)
    docker compose up -d --build agent
    echo "📡 Agent installed and running"
    ;;
  2)
    docker compose up -d --build bot
    echo "🤖 Bot installed and running"
    ;;
  3)
    docker compose up -d --build
    echo "🤖 Bot + 📡 Agent installed and running"
    ;;
esac

echo
echo "✅ Installation complete"
