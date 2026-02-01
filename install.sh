#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/k0ra09/Remna-Monitor.git"
APP_DIR="$HOME/Remna-Monitor"

echo "🧠 Remna Monitor installer"
echo "=========================="
echo ""

# ---------- helpers ----------
need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "❌ Required command '$1' not found"
    exit 1
  }
}

prompt() {
  local text="$1"
  read -r -p "$text" REPLY </dev/tty
  echo "$REPLY"
}

# ---------- checks ----------
need_cmd git
need_cmd curl

if ! command -v docker >/dev/null 2>&1; then
  echo "❌ Docker is not installed"
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "❌ docker compose plugin not found"
  exit 1
fi

# ---------- clone or update ----------
if [ ! -d "$APP_DIR/.git" ]; then
  echo "📦 Cloning repository..."
  git clone "$REPO_URL" "$APP_DIR"
else
  echo "📦 Updating repository..."
  cd "$APP_DIR"
  git pull
fi

cd "$APP_DIR"

# ---------- choose mode ----------
echo ""
echo "What do you want to install?"
echo "1) Agent only"
echo "2) Bot only"
echo "3) Agent + Bot"
echo ""

MODE="$(prompt 'Enter choice [1-3]: ')"

if [[ ! "$MODE" =~ ^[123]$ ]]; then
  echo "❌ Invalid choice, please enter 1, 2 or 3"
  exit 1
fi

# ---------- env ----------
ENV_FILE=".env"
cp .env.example "$ENV_FILE"

echo ""
echo "📝 Configuration"

if [[ "$MODE" == "1" || "$MODE" == "3" ]]; then
  AGENT_NAME="$(prompt 'Agent name (e.g. node-FIN-1): ')"
  AGENT_TOKEN="$(prompt 'Agent token: ')"
fi

if [[ "$MODE" == "2" || "$MODE" == "3" ]]; then
  BOT_TOKEN="$(prompt 'Telegram BOT token: ')"
fi

if [[ "$MODE" == "1" || "$MODE" == "3" ]]; then
  BOT_URL="$(prompt 'Bot URL (e.g. http://1.2.3.4:9000): ')"
fi

# ---------- write env ----------
sed -i "s|AGENT_NAME=.*|AGENT_NAME=${AGENT_NAME}|g" "$ENV_FILE"
sed -i "s|AGENT_TOKEN=.*|AGENT_TOKEN=${AGENT_TOKEN}|g" "$ENV_FILE"
sed -i "s|BOT_TOKEN=.*|BOT_TOKEN=${BOT_TOKEN}|g" "$ENV_FILE"
sed -i "s|BOT_URL=.*|BOT_URL=${BOT_URL}|g" "$ENV_FILE"

echo ""
echo "📦 Starting services..."

case "$MODE" in
  1)
    docker compose up -d agent
    ;;
  2)
    docker compose up -d bot
    ;;
  3)
    docker compose up -d
    ;;
esac

echo ""
echo "✅ Installation complete"

if [[ "$MODE" == "1" ]]; then
  echo "📡 Agent started and will auto-register in the bot"
fi

if [[ "$MODE" == "2" || "$MODE" == "3" ]]; then
  echo "🤖 Bot is running"
fi

echo ""
