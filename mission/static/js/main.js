/**
 * ===================================================================
 * EMPILHADEIRA AUTÔNOMA - CLIENTE WEBSOCKET
 * Sistema de Controle de Missão
 * ===================================================================
 */

// Estado da aplicação
const appState = {
    socket: null,
    connected: false,
    systemState: null
};

// ===================================================================
// INICIALIZAÇÃO
// ===================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Iniciando aplicação...');
    initializeWebSocket();
    setupEventListeners();
    updateConnectionStatus(false);
});

// ===================================================================
// WEBSOCKET
// ===================================================================

function initializeWebSocket() {
    // Conecta ao servidor SocketIO
    appState.socket = io();

    // Evento: Conectado
    appState.socket.on('connect', () => {
        console.log('✅ Conectado ao servidor');
        appState.connected = true;
        updateConnectionStatus(true);
        addLogEntry('Sistema conectado ao servidor', 'received');
    });

    // Evento: Desconectado
    appState.socket.on('disconnect', () => {
        console.log('❌ Desconectado do servidor');
        appState.connected = false;
        updateConnectionStatus(false);
        addLogEntry('Conexão perdida com o servidor', 'sent');
    });

    // Evento: Resposta de Pong
    appState.socket.on('pong', (data) => {
        console.log('🏓 PONG recebido:', data);
        const message = `PONG recebido em ${data.timestamp}`;
        addLogEntry(message, 'received');
    });

    // Evento: Status do Sistema
    appState.socket.on('system_status', (data) => {
        console.log('📊 Status do sistema:', data);
        appState.systemState = data;
        updateSystemInfo(data);
    });

    // Evento: Confirmação de Comando
    appState.socket.on('command_ack', (data) => {
        console.log('✔ Comando reconhecido:', data);
    });

    // Evento: Status do Garfo
    appState.socket.on('fork_status', (data) => {
        console.log('🔧 Status do garfo:', data);
        document.getElementById('fork-height').textContent = `${data.height} cm`;
    });

    // Evento: Status do Vídeo
    appState.socket.on('video_status', (data) => {
        console.log('📹 Status do vídeo:', data);
    });
}

// ===================================================================
// HANDLERS DE EVENTOS
// ===================================================================

function setupEventListeners() {
    // Botão de Ping
    document.getElementById('btn-ping').addEventListener('click', sendPing);

    // Botão de Limpar Log
    document.getElementById('btn-clear-log').addEventListener('click', clearLog);

    // Controles de Teleoperação
    const linearSpeed = document.getElementById('linear-speed');
    const angularSpeed = document.getElementById('angular-speed');

    linearSpeed.addEventListener('input', (e) => {
        document.getElementById('linear-value').textContent = e.target.value;
        sendTeleopCommand();
    });

    angularSpeed.addEventListener('input', (e) => {
        document.getElementById('angular-value').textContent = e.target.value;
        sendTeleopCommand();
    });

    // Botão de Parar
    document.getElementById('btn-stop').addEventListener('click', stopRobot);

    // Controle do Garfo
    document.getElementById('btn-set-fork').addEventListener('click', setForkHeight);
}

// ===================================================================
// FUNÇÕES DE COMUNICAÇÃO
// ===================================================================

function sendPing() {
    if (!appState.connected) {
        alert('Não conectado ao servidor!');
        return;
    }

    const timestamp = new Date().toISOString();
    const data = {
        message: 'ping',
        timestamp: timestamp,
        client: 'web_interface'
    };

    console.log('🏓 Enviando PING:', data);
    appState.socket.emit('ping', data);
    addLogEntry(`PING enviado em ${timestamp}`, 'sent');
}

function sendTeleopCommand() {
    if (!appState.connected) return;

    const linear = parseFloat(document.getElementById('linear-speed').value);
    const angular = parseFloat(document.getElementById('angular-speed').value);

    const command = {
        linear: linear,
        angular: angular,
        timestamp: new Date().toISOString()
    };

    appState.socket.emit('teleop_command', command);
}

function stopRobot() {
    if (!appState.connected) {
        alert('Não conectado ao servidor!');
        return;
    }

    // Reseta os sliders
    document.getElementById('linear-speed').value = 0;
    document.getElementById('angular-speed').value = 0;
    document.getElementById('linear-value').textContent = '0';
    document.getElementById('angular-value').textContent = '0';

    // Envia comando de parada
    const command = {
        linear: 0,
        angular: 0,
        timestamp: new Date().toISOString()
    };

    appState.socket.emit('teleop_command', command);
    addLogEntry('Comando de PARADA enviado', 'sent');
}

function setForkHeight() {
    if (!appState.connected) {
        alert('Não conectado ao servidor!');
        return;
    }

    const height = parseFloat(document.getElementById('fork-height-input').value);

    const command = {
        height_cm: height,
        timestamp: new Date().toISOString()
    };

    appState.socket.emit('set_fork_height', command);
    addLogEntry(`Altura do garfo definida: ${height} cm`, 'sent');
}

// ===================================================================
// FUNÇÕES DE INTERFACE
// ===================================================================

function updateConnectionStatus(connected) {
    const indicator = document.getElementById('status-indicator');
    const text = document.getElementById('status-text');

    if (connected) {
        indicator.classList.remove('disconnected');
        indicator.classList.add('connected');
        text.textContent = 'Conectado';
    } else {
        indicator.classList.remove('connected');
        indicator.classList.add('disconnected');
        text.textContent = 'Desconectado';
    }
}

function updateSystemInfo(state) {
    // Atualiza modo do sistema
    const modeElement = document.getElementById('system-mode');
    modeElement.textContent = state.mode;

    // Atualiza pose do robô
    document.getElementById('pose-x').textContent = `${state.robot_pose.x.toFixed(1)} cm`;
    document.getElementById('pose-y').textContent = `${state.robot_pose.y.toFixed(1)} cm`;
    document.getElementById('pose-theta').textContent = `${state.robot_pose.theta.toFixed(1)}°`;

    // Atualiza altura do garfo
    document.getElementById('fork-height').textContent = `${state.fork_height.toFixed(1)} cm`;

    // Atualiza contagem de clientes
    document.getElementById('clients-count').textContent = state.connected_clients;

    // Atualiza timestamp
    if (state.last_update) {
        const date = new Date(state.last_update);
        document.getElementById('last-update').textContent = 
            `Última atualização: ${date.toLocaleTimeString('pt-BR')}`;
    }
}

function addLogEntry(message, type) {
    const logContainer = document.getElementById('ping-log');
    
    // Remove mensagem de "vazio" se existir
    const emptyMessage = logContainer.querySelector('.log-empty');
    if (emptyMessage) {
        emptyMessage.remove();
    }

    // Cria nova entrada
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    
    const timestamp = new Date().toLocaleTimeString('pt-BR');
    const icon = type === 'sent' ? '📤' : '📥';
    
    entry.innerHTML = `
        <span class="log-timestamp">[${timestamp}]</span>
        ${icon} ${message}
    `;

    logContainer.appendChild(entry);

    // Auto-scroll para o final
    logContainer.scrollTop = logContainer.scrollHeight;

    // Limita número de entradas (mantém apenas as últimas 50)
    const entries = logContainer.querySelectorAll('.log-entry');
    if (entries.length > 50) {
        entries[0].remove();
    }
}

function clearLog() {
    const logContainer = document.getElementById('ping-log');
    logContainer.innerHTML = '<p class="log-empty">Log limpo. Aguardando novos eventos...</p>';
}

// ===================================================================
// UTILITÁRIOS
// ===================================================================

// Previne zoom indesejado em dispositivos móveis ao dar duplo clique
let lastTouchEnd = 0;
document.addEventListener('touchend', (event) => {
    const now = (new Date()).getTime();
    if (now - lastTouchEnd <= 300) {
        event.preventDefault();
    }
    lastTouchEnd = now;
}, false);

// Log de inicialização
console.log(`
╔═══════════════════════════════════════════════════════════╗
║   EMPILHADEIRA AUTÔNOMA - SISTEMA DE CONTROLE DE MISSÃO  ║
║   Versão: 1.0.0                                           ║
║   Cliente WebSocket inicializado                          ║
╚═══════════════════════════════════════════════════════════╝
`);
