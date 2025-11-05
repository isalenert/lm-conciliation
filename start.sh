#!/bin/bash

echo "🐳 Iniciando LM Conciliation com Docker..."
echo ""

# Parar containers antigos
echo "🛑 Parando containers existentes..."
docker-compose down

# Limpar volumes antigos (opcional - comente se quiser manter dados)
# echo "🗑️  Limpando volumes antigos..."
# docker-compose down -v

# Build das imagens
echo "🏗️  Construindo imagens Docker..."
docker-compose build

# Iniciar serviços
echo "🚀 Iniciando serviços..."
docker-compose up -d

# Aguardar serviços ficarem prontos
echo ""
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 10

# Verificar status
echo ""
echo "📊 Status dos containers:"
docker-compose ps

echo ""
echo "✅ Sistema iniciado!"
echo ""
echo "📍 Acesse:"
echo "   Frontend: http://localhost"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Logs: docker-compose logs -f"
echo "🛑 Parar: docker-compose down"
