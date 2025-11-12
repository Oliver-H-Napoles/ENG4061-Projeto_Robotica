# 🤖 Empilhadeira Autônoma - Sistema de Controle de Missão

Sistema de controle de alto nível ("Full Stack") para robô empilhadeira autônomo baseado em Raspberry Pi 4. Este projeto implementa a interface HMI, máquina de estados e orquestração dos módulos de Navegação e Visão Computacional.

## 📋 Características

- **Interface Web:** HMI leve e responsiva para teleoperação e monitoramento
- **WebSockets:** Comunicação em tempo real via Flask-SocketIO
- **Arquitetura Modular:** Separação clara entre controle, navegação e visão
- **Auto-inicialização:** Script systemd para boot automático no RPi
- **Multithreading:** Processos separados para vídeo, controle e servidor web

## 🛠️ Stack de Tecnologia

- **Hardware:** Raspberry Pi 4 (OS: Raspberry Pi OS Lite)
- **Backend:** Python 3.x + Flask + Flask-SocketIO
- **Frontend:** HTML5 + CSS3 + JavaScript (Vanilla)
- **Concorrência:** `threading` para separação de processos

## 📂 Estrutura do Projeto

```
empilhadeira-iot/
├── app.py                      # Servidor Flask principal
├── requirements.txt            # Dependências Python
├── empilhadeira-iot.service   # Script systemd
├── navigation/                 # Módulo de navegação (a ser integrado)
│   ├── __init__.py
│   └── navigation.py
├── templates/                  # Templates HTML
│   └── index.html
└── static/                     # Arquivos estáticos
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## 🚀 Instalação

### 1. Clonar o repositório (ou copiar arquivos para o RPi)

```bash
cd ~
git clone [URL_DO_REPOSITORIO]
cd empilhadeira-iot
```

### 2. Instalar dependências

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3 e pip (se necessário)
sudo apt install python3 python3-pip -y

# Instalar dependências Python
pip3 install -r requirements.txt
```

### 3. Testar servidor

```bash
python3 app.py
```

Acesse `http://[IP_DO_RPI]:5000` no navegador.

### 4. Configurar auto-inicialização (systemd)

```bash
# Copiar arquivo de serviço para systemd
sudo cp empilhadeira-iot.service /etc/systemd/system/

# IMPORTANTE: Editar o arquivo para ajustar caminhos se necessário
sudo nano /etc/systemd/system/empilhadeira-iot.service

# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar serviço para iniciar no boot
sudo systemctl enable empilhadeira-iot.service

# Iniciar serviço agora
sudo systemctl start empilhadeira-iot.service

# Verificar status
sudo systemctl status empilhadeira-iot.service

# Ver logs em tempo real
sudo journalctl -u empilhadeira-iot.service -f
```

## 🎮 Usando a Interface

### Teste de Comunicação (Ping/Pong)

1. Acesse a interface web
2. Clique no botão "Enviar Ping"
3. Observe o log mostrando a comunicação WebSocket funcionando

### Teleoperação

1. Ajuste os sliders de velocidade linear e angular
2. Os comandos são enviados em tempo real para o servidor
3. Use o botão "PARAR" para emergência

### Controle do Garfo

1. Digite a altura desejada (em cm)
2. Clique em "Definir Altura"
3. O sistema comandará o garfo para a posição

## 🔌 Integração com Módulos

### Módulo de Navegação

O sistema espera uma classe `RobotChassis` em `navigation/navigation.py`:

```python
from navigation.navigation import RobotChassis

# No app.py:
robot_chassis = RobotChassis()
robot_chassis.set_velocity(linear_cm_s, angular_deg_s)
pose = robot_chassis.get_pose()  # Retorna (x, y, theta)
```

### Módulo de Visão

O sistema espera uma classe `VisionSystem` em `vision/vision.py`:

```python
from vision.vision import VisionSystem

# No app.py:
vision = VisionSystem()
marker = vision.detect_floor_marker(frame)
pallet = vision.detect_pallet_marker(frame)
```

## 📡 API WebSocket

### Eventos do Cliente → Servidor

- `ping`: Teste de comunicação
- `teleop_command`: Comando de teleoperação `{linear, angular}`
- `set_fork_height`: Define altura do garfo `{height_cm}`
- `request_video_stream`: Solicita stream de vídeo

### Eventos do Servidor → Cliente

- `pong`: Resposta ao ping
- `system_status`: Estado atualizado do sistema
- `command_ack`: Confirmação de comando
- `fork_status`: Status do garfo

## 🐛 Troubleshooting

### Servidor não inicia

```bash
# Verificar logs
sudo journalctl -u empilhadeira-iot.service -n 50

# Verificar permissões
ls -la /home/pi/empilhadeira-iot/app.py

# Testar manualmente
python3 /home/pi/empilhadeira-iot/app.py
```

### Não consigo acessar de outro dispositivo

```bash
# Verificar IP do RPi
hostname -I

# Verificar firewall (se aplicável)
sudo ufw status

# Testar conectividade
ping [IP_DO_RPI]
```

### WebSocket não conecta

- Verifique se está usando `http://` e não `https://`
- Confirme que a porta 5000 está acessível
- Verifique o console do navegador (F12) para erros

## 📝 Comandos Úteis

```bash
# Reiniciar serviço
sudo systemctl restart empilhadeira-iot.service

# Parar serviço
sudo systemctl stop empilhadeira-iot.service

# Ver logs em tempo real
sudo journalctl -u empilhadeira-iot.service -f

# Verificar status
sudo systemctl status empilhadeira-iot.service

# Desabilitar auto-inicialização
sudo systemctl disable empilhadeira-iot.service
```

## 🔮 Próximos Passos

- [ ] Integração com módulo de navegação
- [ ] Integração com módulo de visão
- [ ] Implementação de streaming de vídeo
- [ ] Máquina de estados para missões autônomas
- [ ] Sistema de mapeamento e localização
- [ ] Interface de planejamento de missões

## 📄 Licença

[Definir licença]

## 👥 Contribuidores

[Adicionar nomes da equipe]

---

**Desenvolvido para o projeto ENG4061 - Projeto de Robótica**
