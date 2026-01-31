#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/k0ra09/Remna-Monitor"
DIR="Remna-Monitor"

echo "🧠 Remna Monitor installer"
echo "=========================="
echo

# ---- sanity check: must have TTY ----
if [[ ! -t 0 ]]; then
  echo "❌ This installer requires an interactive terminal (TTY)"
  echo "Run it like this:"
  echo "  curl -fsSL $REPO_URL/raw/main/install.sh -o install.sh"
  echo "  bash install.sh"
  exit 1
fi

# ---- deps ----
for cmd in git docker; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "❌ Required command not found: $cmd"
    exit 1
  fi
done

if ! docker compose version >/dev/null 2>&1; then
  echo "❌ docker compose plugin not found"
  exit 1
fi

# ---- menu ----
while true; do
  echo
  echo "What do you want to install?"
  echo "1) Agent only"
  echo "2) Bot only"
  echo "3) Agent + Bot"
  read -rp "> " MODE

  case "$MODE" in
    1|2|3) break ;;
    *) echo "❌ Invalid choice, enter 1, 2 or 3" ;;
  esac
done

# ---- clone ----
if [[ ! -d "$DIR" ]]; then
  echo "📦 Cloning repository..."
  git clone "$REPO_URL"
fi

cd "$DIR"

# ---- env ----
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

# ---- agent ----
if [[ "$MODE" == "1" || "$MODE" == "3" ]]; then
  read -rp "Agent name: " AGENT_NAME
  read -rp "Agent token: " AGENT_TOKEN

  set_env AGENT_NAME "$AGENT_NAME"
  set_env AGENT_TOKEN "$AGENT_TOKEN"
fi

# ---- bot ----
if [[ "$MODE" == "2" || "$MODE" == "3" ]]; then
  read -rp "Telegram BOT_TOKEN: " BOT_TOKEN
  read -rp "Agents list (comma separated, http://ip:8000): " AGENTS

  set_env BOT_TOKEN "$BOT_TOKEN"
  set_env AGENTS "$AGENTS"

  if ! grep -q "^AGENT_TOKEN=" .env; then
    read -rp "Agent token (for bot → agent auth): " AGENT_TOKEN
    set_env AGENT_TOKEN "$AGENT_TOKEN"
  fi
fi

# ---- run ----
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
