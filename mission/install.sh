#!/bin/bash
# ===================================================================
# Script de Instalação - Empilhadeira Autônoma
# Configura automaticamente o ambiente no Raspberry Pi
# ===================================================================

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   EMPILHADEIRA AUTÔNOMA - INSTALAÇÃO AUTOMÁTICA          ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verifica se está rodando no Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model; then
    echo -e "${YELLOW}⚠ Aviso: Este script foi projetado para Raspberry Pi${NC}"
    echo "Continuando mesmo assim..."
fi

# Atualizar sistema
echo -e "${GREEN}[1/6]${NC} Atualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar Python e dependências
echo -e "${GREEN}[2/6]${NC} Instalando Python 3 e pip..."
sudo apt install -y python3 python3-pip python3-venv

# Criar ambiente virtual (opcional mas recomendado)
echo -e "${GREEN}[3/6]${NC} Criando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
echo -e "${GREEN}[4/6]${NC} Instalando dependências Python..."
pip3 install -r requirements.txt

# Configurar serviço systemd
echo -e "${GREEN}[5/6]${NC} Configurando serviço systemd..."

# Obter diretório atual
CURRENT_DIR=$(pwd)
SERVICE_FILE="/etc/systemd/system/empilhadeira-iot.service"

# Criar arquivo de serviço com caminhos corretos
sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Empilhadeira Autônoma - Sistema de Controle de Missão
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$CURRENT_DIR/venv/bin/python3 $CURRENT_DIR/app.py
Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=empilhadeira-iot

[Install]
WantedBy=multi-user.target
EOF

# Recarregar systemd e habilitar serviço
sudo systemctl daemon-reload
sudo systemctl enable empilhadeira-iot.service

echo -e "${GREEN}[6/6]${NC} Finalizando instalação..."

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   INSTALAÇÃO CONCLUÍDA COM SUCESSO!                       ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Próximos Passos:"
echo ""
echo "1. Testar servidor manualmente:"
echo "   $ source venv/bin/activate"
echo "   $ python3 app.py"
echo ""
echo "2. Acessar interface web:"
echo "   http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "3. Iniciar serviço systemd:"
echo "   $ sudo systemctl start empilhadeira-iot.service"
echo ""
echo "4. Verificar status:"
echo "   $ sudo systemctl status empilhadeira-iot.service"
echo ""
echo "5. Ver logs:"
echo "   $ sudo journalctl -u empilhadeira-iot.service -f"
echo ""
echo -e "${GREEN}✅ Sistema pronto para uso!${NC}"
