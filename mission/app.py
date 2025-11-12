#!/usr/bin/env python3
"""
Sistema de Controle de Missão - Empilhadeira Autônoma
Servidor Flask com WebSockets para controle em tempo real
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import logging
from datetime import datetime
import threading
import time

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicialização do Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'empilhadeira-iot-secret-2025'

# Inicialização do SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Estado global do sistema
system_state = {
    'mode': 'IDLE',  # IDLE, TELEOP, AUTONOMOUS
    'robot_pose': {'x': 0.0, 'y': 0.0, 'theta': 0.0},
    'fork_height': 0.0,
    'connected_clients': 0,
    'last_update': None
}


# ============================================================================
# ROTAS HTTP
# ============================================================================

@app.route('/')
def index():
    """Página principal da interface web"""
    logger.info("Servindo página principal")
    return render_template('index.html')


@app.route('/api/status')
def api_status():
    """Endpoint REST para status do sistema"""
    return jsonify({
        'status': 'online',
        'system_state': system_state,
        'timestamp': datetime.now().isoformat()
    })


# ============================================================================
# EVENTOS WEBSOCKET
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Cliente conectou via WebSocket"""
    system_state['connected_clients'] += 1
    logger.info(f"Cliente conectado. Total: {system_state['connected_clients']}")
    
    # Envia estado inicial para o cliente
    emit('system_status', system_state)


@socketio.on('disconnect')
def handle_disconnect():
    """Cliente desconectou"""
    system_state['connected_clients'] -= 1
    logger.info(f"Cliente desconectado. Total: {system_state['connected_clients']}")


@socketio.on('ping')
def handle_ping(data):
    """
    Evento de teste: Recebe 'ping' e responde 'pong'
    Este é o teste básico de comunicação WebSocket
    """
    timestamp = datetime.now().isoformat()
    logger.info(f"[PING] Recebido ping do cliente: {data}")
    
    # Responde com pong
    response = {
        'message': 'pong',
        'timestamp': timestamp,
        'received_data': data
    }
    
    logger.info(f"[PONG] Enviando pong de volta")
    emit('pong', response)


@socketio.on('teleop_command')
def handle_teleop_command(data):
    """
    Recebe comandos de teleoperação
    Formato esperado: {'linear': float, 'angular': float}
    """
    logger.info(f"[TELEOP] Comando recebido: {data}")
    
    # TODO: Integrar com navigation.py
    # robot_chassis.set_velocity(data['linear'], data['angular'])
    
    emit('command_ack', {'status': 'received', 'data': data})


@socketio.on('set_fork_height')
def handle_fork_height(data):
    """
    Comanda altura do garfo
    Formato esperado: {'height_cm': float}
    """
    logger.info(f"[FORK] Altura solicitada: {data['height_cm']} cm")
    
    # TODO: Integrar com navigation.py
    # robot_chassis.move_fork(data['height_cm'])
    
    system_state['fork_height'] = data['height_cm']
    emit('fork_status', {'height': data['height_cm']})


@socketio.on('request_video_stream')
def handle_video_request():
    """Cliente solicitou stream de vídeo"""
    logger.info("[VIDEO] Cliente solicitou stream de vídeo")
    
    # TODO: Implementar streaming de vídeo em issue futura
    emit('video_status', {'status': 'not_implemented'})


# ============================================================================
# LOOP PRINCIPAL DO ROBÔ (Background Thread)
# ============================================================================

def robot_control_loop():
    """
    Thread principal que atualiza o estado do robô
    Aqui chamaremos robot_chassis.update() e vision.detect_*()
    """
    logger.info("[LOOP] Thread de controle iniciada")
    
    while True:
        try:
            # TODO: Integrar módulos de navegação e visão
            # robot_chassis.update()
            # pose = robot_chassis.get_pose()
            # system_state['robot_pose'] = {'x': pose[0], 'y': pose[1], 'theta': pose[2]}
            
            system_state['last_update'] = datetime.now().isoformat()
            
            # Emite estado atualizado para todos os clientes conectados
            socketio.emit('system_status', system_state)
            
            # Controle de frequência do loop (50Hz = 20ms)
            time.sleep(0.02)
            
        except Exception as e:
            logger.error(f"[LOOP] Erro no loop de controle: {e}")
            time.sleep(1.0)  # Espera mais tempo em caso de erro


# ============================================================================
# INICIALIZAÇÃO DO SERVIDOR
# ============================================================================

def initialize_system():
    """Inicializa todos os módulos do robô"""
    logger.info("=" * 60)
    logger.info("SISTEMA DE CONTROLE DE MISSÃO - EMPILHADEIRA AUTÔNOMA")
    logger.info("=" * 60)
    
    # TODO: Inicializar módulos quando estiverem prontos
    # global robot_chassis, vision_system
    # robot_chassis = RobotChassis()
    # vision_system = VisionSystem()
    
    logger.info("[OK] Módulos inicializados (simulação)")
    
    # Inicia thread de controle do robô
    control_thread = threading.Thread(target=robot_control_loop, daemon=True)
    control_thread.start()
    logger.info("[OK] Thread de controle iniciada")


if __name__ == '__main__':
    try:
        # Inicializa o sistema
        initialize_system()
        
        # Inicia o servidor Flask com SocketIO
        logger.info("Iniciando servidor Flask na porta 5000...")
        logger.info("Acesse: http://0.0.0.0:5000")
        
        socketio.run(
            app,
            host='0.0.0.0',  # Permite conexões externas (importante para o RPi)
            port=5000,
            debug=False,  # True apenas para desenvolvimento
            use_reloader=False  # Desabilita reloader para evitar duplicação de threads
        )
        
    except KeyboardInterrupt:
        logger.info("Servidor encerrado pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
