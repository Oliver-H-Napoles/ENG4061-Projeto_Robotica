# ===================================================================
# NOTAS DE DESENVOLVIMENTO
# ===================================================================

## 📋 Checklist de Integração

### Módulo de Navegação
- [ ] Classe `RobotChassis` implementada em `navigation/navigation.py`
- [ ] Método `update()` não-bloqueante
- [ ] Método `set_velocity(linear_cm_s, angular_deg_s)`
- [ ] Método `get_pose()` retornando `(x_cm, y_cm, theta_graus)`
- [ ] Método `reset_pose(x, y, theta)` para correção por visão
- [ ] Método `move_fork(height_cm)`

### Módulo de Visão
- [ ] Classe `VisionSystem` implementada em `vision/vision.py`
- [ ] Método `detect_floor_marker(frame)` para QR Codes do chão
- [ ] Método `detect_pallet_marker(frame)` para alinhamento
- [ ] Método `draw_debug(frame, detection_data)` opcional

## 🔧 Pontos de Integração no Código

### app.py - Linhas a modificar:

1. **Importar módulos (linha ~15):**
```python
from navigation.navigation import RobotChassis
from vision.vision import VisionSystem
```

2. **Inicializar no `initialize_system()` (linha ~180):**
```python
global robot_chassis, vision_system
robot_chassis = RobotChassis()
vision_system = VisionSystem()
```

3. **Loop de controle `robot_control_loop()` (linha ~150):**
```python
robot_chassis.update()
pose = robot_chassis.get_pose()
system_state['robot_pose'] = {'x': pose[0], 'y': pose[1], 'theta': pose[2]}
```

4. **Handler de teleoperação (linha ~95):**
```python
robot_chassis.set_velocity(data['linear'], data['angular'])
```

5. **Handler do garfo (linha ~105):**
```python
robot_chassis.move_fork(data['height_cm'])
```

## 🎥 Streaming de Vídeo (Próxima Issue)

Opções de implementação:
1. **MJPEG Stream:** Simples, baixa latência, mas usa mais banda
2. **WebRTC:** Baixa latência, mais complexo
3. **HLS/DASH:** Alta latência, mas robusto

Recomendação: Começar com MJPEG para prototipagem rápida.

## 🤖 Máquina de Estados (Próxima Issue)

Estados planejados:
- `IDLE`: Esperando comando
- `TELEOP`: Controle manual ativo
- `NAVIGATING`: Indo para waypoint
- `ALIGNING`: Alinhando com palete
- `LOADING`: Subindo garfo
- `UNLOADING`: Descendo garfo
- `ERROR`: Estado de erro

## 📊 Métricas de Performance

Alvos de desempenho:
- Loop de controle: 50 Hz (20ms)
- WebSocket latência: < 50ms
- Video FPS: 15-30 fps
- CPU usage: < 70% (deixar margem para visão)

## 🐛 Debugging Tips

### Ver logs do servidor:
```bash
sudo journalctl -u empilhadeira-iot.service -f
```

### Testar sem systemd:
```bash
python3 app.py
```

### Monitorar uso de CPU:
```bash
htop
```

### Verificar portas abertas:
```bash
sudo netstat -tulpn | grep :5000
```

## 🔐 Segurança

Para produção, considerar:
- [ ] HTTPS (certificado SSL)
- [ ] Autenticação de usuários
- [ ] Rate limiting para evitar spam
- [ ] Validação de inputs
- [ ] Firewall configurado

## 📝 Convenções de Código

- **Unidades:** Sempre cm e graus (nunca pixels ou radianos na interface)
- **Nomes de variáveis:** snake_case para Python
- **Nomes de funções:** Verbos descritivos (get_pose, set_velocity)
- **Comentários:** Explicar o "porquê", não o "o quê"
- **Logging:** Usar níveis apropriados (INFO, WARNING, ERROR)

## 🚀 Otimizações Futuras

1. **Compressão de vídeo:** H.264 hardware encoding no RPi
2. **Threading avançado:** Separar cada câmera em thread própria
3. **Cache:** Redis para estado compartilhado
4. **Mensagens:** MQTT para comunicação assíncrona
5. **Database:** SQLite para log de missões

## 📞 Contatos da Equipe

- **Full Stack (RPi):** [Nome]
- **Navegação:** [Nome]
- **Visão:** [Nome]
- **Hardware:** [Nome]
