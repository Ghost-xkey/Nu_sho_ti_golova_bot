#!/bin/bash

echo "🔄 Updating bot on server..."

# Подключаемся к серверу и обновляем бота
ssh root@92.63.100.172 << 'EOF'
cd ~/Nu_sho_ti_golova_bot

echo "📥 Pulling latest changes..."
git pull origin main

echo "🐳 Stopping bot..."
docker-compose down

echo "🚀 Starting bot with new environment..."
docker-compose up -d

echo "⏳ Waiting for bot to start..."
sleep 5

echo "🧪 Testing environment variables..."
docker exec nu_sho_ti_golova_bot python -c "
import os
print('✅ Hugging Face token:', 'SET' if os.getenv('HUGGINGFACE_API_TOKEN') else 'NOT SET')
print('✅ Yandex API key:', 'SET' if os.getenv('YANDEX_API_KEY') else 'NOT SET')
"

echo "🎉 Bot updated successfully!"
EOF

echo "✅ Update completed!"
