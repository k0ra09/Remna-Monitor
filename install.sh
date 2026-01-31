#!/usr/bin/env bash
set -e

REPO_URL="https://github.com/k0ra09/Remna-Monitor"
DIR="Remna-Monitor"

echo "🧠 Remna Monitor installer"
echo "=========================="
echo
echo "What do you want to install?"
echo "1) Agent only"
echo "2) Bot only"
echo "3) Agent + Bot"
read -rp "> " MODE

if [[ "$MODE" != "1" && "$MODE" != "2" && "$MODE" != "3" ]]; then
  echo "❌ Invalid choice"
  exit 1
fi

# --- Check docker ---
if ! command -v docker >/dev/null 2>&1; then
  echo "❌ Docker not found. Install Docker first."
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "❌ docker compose not found."
  exit 1
fi

# --- Clone repo ---
if [[ ! -d "$DIR" ]]; then
  echo "📦 Cloning repository..."
  git clone "$REPO_URL"
fi

cd "$DIR"

# --- ENV ---
if [[ ! -f .env ]]; then
  echo "📝 Creating .env file"
  cp .env.example .env
fi

# --- Configure AGENT ---
if [[ "$MODE" == "1" || "$MODE" == "3" ]]; then
  read -rp "Agent name: " AGENT_NAME
  read -rp "Agent token: " AGENT_TOKEN

  sed -i "s/^AGENT_NAME=.*/AGENT_NAME=$AGENT_NAME/" .env || echo "AGENT_NAME=$AGENT_NAME" >> .env
  sed -i "s/^AGENT_TOKEN=.*/AGENT_TOKEN=$AGENT_TOKEN/" .env || echo "AGENT_TOKEN=$AGENT_TOKEN" >> .env
fi

# --- Configure BOT ---
if [[ "$MODE" == "2" || "$MODE" == "3" ]]; then
  read -rp "Telegram BOT_TOKEN: " BOT_TOKEN
  read -rp "Agents list (comma separated, http://ip:8000): " AGENTS

  sed -i "s/^BOT_TOKEN=.*/BOT_TOKEN=$BOT_TOKEN/" .env || echo "BOT_TOKEN=$BOT_TOKEN" >> .env
  sed -i "s/^AGENTS=.*/AGENTS=$AGENTS/" .env || echo "AGENTS=$AGENTS" >> .env
fi

# --- Run ---
echo
echo "🚀 Starting services..."

if [[ "$MODE" == "1" ]]; then
  docker compose up -d --build agent
elif [[ "$MODE" == "2" ]]; then
  docker compose up -d --build bot
else
  docker compose up -d --build
fi

echo
echo "✅ Installation complete"

if [[ "$MODE" == "1" ]]; then
  echo "📡 Agent is running"
elif [[ "$MODE" == "2" ]]; then
  echo "🤖 Bot is running"
else
  echo "🤖 Bot + 📡 Agent are running"
fi
