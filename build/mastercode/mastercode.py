# -*- coding: utf-8 -*-
import customtkinter as ctk
from PIL import Image
import tkinter as tk
import tkinter.filedialog as filedialog
import time
import threading
import json
import socket
import queue
import os
import sys

# --- FUNCIÓN PARA COMPATIBILIDAD CON PYINSTALLER ---
def resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso, funciona para desarrollo y para PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- CONFIGURACIÓN Y CONSTANTES GLOBALES ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Constantes de Colores y Estilo para Teclado Virtual
COLOR_REQUERIDO = "#52C41A"
COLOR_PRESIONADO = "#FAAD14"
COLOR_DEFECTO = "#333333"
KEY_CORNER_RADIUS = 5

# Mapeo de Símbolos a Teclas Base (Configuración INGLÉS US)
SHIFT_MAP_TO_KEY = {
    '!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '^': '6', '&': '7',
    '*': '8', '(': '9', ')': '0', '_': '-', '+': '=', '{': '[', '}': ']',
    '|': '\\', ':': ';', '"': "'", '<': ',', '>': '.', '?': '/'
}

# --- INFORMACIÓN DE AYUDA Y SOPORTE (ACTUALIZADO) ---
AUTOR_CODIGO = "José Espinoza"
PAYPAL_DONACION = "jemmasterdc@gmail.com"

LICENCIA_INFO = """
Licencia de Atribución (Inspirada en MIT)

Copyright (c) 2024, José Espinoza

Por la presente se concede permiso, de forma gratuita, a cualquier persona que obtenga una copia de este software y de los archivos de documentación asociados (el "Software").

El Software se puede usar, copiar, modificar, fusionar, publicar, distribuir, sublicenciar y/o vender sin ninguna restricción.

La única condición es la siguiente:
Cualquier copia o parte sustancial del Software deberá incluir una atribución visible al autor original de la idea y del código base.

Ejemplo de atribución:
"Basado en el Master Code Typist original de José Espinoza."

EL SOFTWARE SE PROPORCIONA "TAL CUAL", SIN GARANTÍA DE NINGÚN TIPO.
"""

GUIA_RAPIDA_INFO = """
¡Bienvenido a Master Code Typist!

Esta guía te ayudará a entender cómo funciona el programa.

---

### 1. MODOS DE OPERACIÓN

Al iniciar, tienes tres opciones:

- **Modo Independiente:**
  Ideal para practicar solo. Inicia sesión con tu usuario o registra uno nuevo. Tu progreso y lecciones completadas se guardarán localmente en tu equipo.

- **Iniciar Servidor (Profesor):**
  Si eres profesor, esta opción convierte tu PC en un servidor. Se abrirá una ventana de "Monitor de Clientes" donde verás en tiempo real el progreso de todos los estudiantes que se conecten (PPM, precisión, errores). Debes compartir tu dirección IP (que aparecerá en pantalla) con tus estudiantes.

- **Conectar como Cliente (Estudiante):**
  Si eres estudiante, tu profesor te dará una dirección IP. Usa esta opción para conectarte a su sesión. Una vez conectado, deberás iniciar sesión con tu usuario para que el profesor pueda ver tu progreso asociado a tu nombre.

---

### 2. MENÚ PRINCIPAL

Una vez que inicies sesión, verás:

- **Niveles (Básico, Intermedio, Avanzado):**
  Haz clic en un nivel para comenzar la siguiente lección disponible. Tu progreso se muestra en las barras. Si completas un nivel, el botón se desactivará.

- **Cargar Archivo de Código:**
  ¿Quieres practicar con tu propio código? Usa este botón para cargar un archivo (.py, .js, .txt, etc.) y usarlo como una lección personalizada.

---

### 3. PANTALLA DE LECCIÓN

Aquí es donde ocurre la magia:

- **Escritura:** Escribe el texto que aparece en el panel superior. El sistema es estricto: no podrás avanzar hasta que escribas el carácter correcto.
  
- **Teclado Virtual:** Te muestra visualmente qué tecla debes presionar. La tecla requerida se ilumina en verde. Si necesitas usar Shift (para mayúsculas o símbolos), las teclas Shift también se iluminarán.

- **Métricas en Tiempo Real:** A tu derecha, puedes ver tus Palabras Por Minuto (PPM), Precisión y Errores mientras escribes.

- **Resultados:** Al terminar, una ventana te mostrará tu puntuación final. Si lo hiciste bien, aparecerá un botón para ir a la "Siguiente Lección".
"""


# =======================================================================
# --- GESTOR DE DATOS (SERVICE CLASS) ---
# =======================================================================
class LeccionManager:
    """Clase de servicio para gestionar lecciones, progreso y autenticación."""
    DATOS_LECCIONES = {
        "Básico": [
            "nombre = \"Mundo\"\nprint(f\"Hola, {nombre}!\")",
            "numeros = [1, 2, 3, 4, 5]\nsuma = sum(numeros)",
            "edad = 18\nif edad >= 18:\n  print(\"Es mayor de edad\")",
            "for letra in \"python\":\n  print(letra)",
            "punto = {\"x\": 10, \"y\": 20}\nprint(punto[\"x\"])",
            "def restar(a, b):\n  return a - b\nresultado = restar(10, 3)",
            "i = 0\nwhile i < 3:\n  print(\"ciclo while\")\n  i += 1",
            "colores = (\"rojo\", \"verde\", \"azul\")\nprimer_color = colores[0]",
            "es_valido = True\nif not es_valido:\n  print(\"No es válido\")",
            "frutas = [\"manzana\", \"banana\"]\nfrutas.append(\"naranja\")"
        ],
        "Intermedio": [
            "def calcular_area(base, altura):\n  return (base * altura) / 2\narea = calcular_area(10, 5)",
            "cuadrados = [x**2 for x in range(10)]\nprint(cuadrados)",
            "with open(\"archivo.txt\", \"w\") as f:\n  f.write(\"Hola, archivo!\")",
            "class Mascota:\n  def __init__(self, nombre):\n    self.nombre = nombre\nmi_perro = Mascota(\"Fido\")",
            "try:\n  valor = int(\"abc\")\nexcept ValueError:\n  print(\"No es un número válido\")",
            "import math\n\nraiz_cuadrada = math.sqrt(81)\nprint(f\"La raíz es {raiz_cuadrada}\")",
            "numeros = [1, 2, 3, 4, 5, 6]\npares = list(filter(lambda x: x % 2 == 0, numeros))",
            "puntos = [10, 20, 30]\nfor indice, valor in enumerate(puntos):\n  print(f\"Índice {indice}: {valor}\")",
            "def saludar(nombre, saludo=\"Hola\"):\n  return f\"{saludo}, {nombre}.\"\nprint(saludar(\"Ana\"))",
            "import datetime\n\nhoy = datetime.date.today()\nprint(f\"La fecha de hoy es: {hoy}\")"
        ],
        "Avanzado": [
            "def mi_decorador(funcion):\n  def envoltorio():\n    print(\"Inicio\")\n    funcion()\n    print(\"Fin\")\n  return envoltorio",
            "def generador_pares(limite):\n  num = 0\n  while num < limite:\n    yield num\n    num += 2",
            "from functools import reduce\n\nproducto = reduce(lambda x, y: x * y, [1, 2, 3, 4])",
            "import asyncio\n\nasync def tarea_larga():\n  print(\"Iniciando...\")\n  await asyncio.sleep(1)\n  print(\"...Finalizado\")",
            "class ContextoArchivo:\n  def __init__(self, fname):\n    self.fname = fname\n  def __enter__(self):\n    self.f = open(self.fname, 'w')\n    return self.f\n  def __exit__(self, t, v, tb):\n    self.f.close()",
            "import json\n\ndatos = {\"id\": 101, \"activo\": True, \"tags\": [\"python\", \"json\"]}\njson_string = json.dumps(datos, indent=2)",
            "import re\n\ntexto = \"Mi email es test@example.com\"\nmatch = re.search(r\"\\S+@\\S+\", texto)\nif match:\n  print(match.group())",
            "lista_anidada = [[1, 2], [3, 4], [5, 6]]\nplana = [item for sublista in lista_anidada for item in sublista]",
            "from collections import Counter\n\nconteo = Counter(\"parangaricutirimicuaro\")\nprint(conteo.most_common(3))",
            "import threading\n\ndef trabajador():\n  print(\"Trabajando en un hilo paralelo.\")\nhilo = threading.Thread(target=trabajador)\nhilo.start()\nhilo.join()"
        ],
    }

    def __init__(self):
        self.usuario_actual = None
        self.archivo_datos = resource_path("users_data.json")
        self.USUARIOS = {}
        self.progreso_usuario = {}
        self._cargar_datos_usuarios()

    def _cargar_datos_usuarios(self):
        # --- CORRECCIÓN: Lógica mejorada para asegurar que el usuario Admin siempre exista ---
        try:
            with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.USUARIOS = data.get("usuarios", {})
                self.progreso_usuario = data.get("progreso", {})
        except (FileNotFoundError, json.JSONDecodeError):
            # Si el archivo no existe o está corrupto, empezamos de cero.
            self.USUARIOS = {}
            self.progreso_usuario = {}

        # Asegurarse de que el usuario Admin siempre exista.
        if "Admin" not in self.USUARIOS:
            self.USUARIOS["Admin"] = "12345"
            if "Admin" not in self.progreso_usuario:
                self.progreso_usuario["Admin"] = {"Básico": 0, "Intermedio": 0, "Avanzado": 0}
            # Guardar los cambios para que el Admin quede registrado permanentemente.
            self._guardar_datos_usuarios()

    def _guardar_datos_usuarios(self):
        with open(self.archivo_datos, 'w', encoding='utf-8') as f:
            json.dump({"usuarios": self.USUARIOS, "progreso": self.progreso_usuario}, f, indent=4)

    def autenticar(self, user, password):
        if self.USUARIOS.get(user) == password:
            self.usuario_actual = user
            return True
        return False

    def registrar_usuario(self, user, password):
        if user in self.USUARIOS:
            return False, "El nombre de usuario ya existe."
        if not user or not password:
            return False, "El usuario y la contraseña no pueden estar vacíos."
        self.USUARIOS[user] = password
        self.progreso_usuario[user] = {"Básico": 0, "Intermedio": 0, "Avanzado": 0}
        self._guardar_datos_usuarios()
        return True, "Registro exitoso. Puede iniciar sesión."

    def get_progreso_actual(self):
        return self.progreso_usuario.get(self.usuario_actual, {"Básico": 0, "Intermedio": 0, "Avanzado": 0})

    def get_leccion(self, nivel, indice):
        if nivel in self.DATOS_LECCIONES and 0 <= indice < len(self.DATOS_LECCIONES[nivel]):
            return self.DATOS_LECCIONES[nivel][indice]
        return "Nivel Completo"

    def avanzar_progreso(self, nivel):
        if not self.usuario_actual: return False
        
        if self.usuario_actual not in self.progreso_usuario:
            self.progreso_usuario[self.usuario_actual] = {"Básico": 0, "Intermedio": 0, "Avanzado": 0}

        progreso = self.progreso_usuario[self.usuario_actual].get(nivel, 0)
        num_lecciones = self.get_total_lecciones(nivel)
        
        if progreso < num_lecciones:
            self.progreso_usuario[self.usuario_actual][nivel] = progreso + 1
            self._guardar_datos_usuarios()
            return True
        return False

    def get_progreso(self, nivel):
        return self.get_progreso_actual().get(nivel, 0)

    def get_total_lecciones(self, nivel):
        return len(self.DATOS_LECCIONES.get(nivel, []))

    def calcular_estrellas(self, ppm, precision):
        if precision >= 98 and ppm >= 40: return 3
        if precision >= 95 and ppm >= 30: return 2
        if precision >= 90 and ppm >= 20: return 1
        return 0


# =======================================================================
# --- CLASES DE RED REFACTORIZADAS ---
# =======================================================================
class NetworkServer:
    """Maneja toda la lógica del servidor en hilos separados."""
    def __init__(self, host, port, gui_queue):
        self.host = host
        self.port = port
        self.gui_queue = gui_queue
        self.server_socket = None
        self.clients = {}
        self.running = False
        self.lock = threading.Lock()
        self.client_data = {}

    def start(self):
        if self.running: return
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            threading.Thread(target=self._accept_clients, daemon=True).start()
            self.gui_queue.put(("server_started", get_local_ip()))
        except Exception as e:
            self.running = False
            self.gui_queue.put(("server_error", str(e)))

    def stop(self):
        if not self.running: return
        self.running = False
        with self.lock:
            for client_socket in self.clients:
                try: client_socket.close()
                except: pass
            self.clients.clear()
        try:
            self.server_socket.close()
        except:
            pass
        time.sleep(0.1)
        self.gui_queue.put(("server_stopped", None))

    def _accept_clients(self):
        while self.running:
            try:
                self.server_socket.settimeout(1)
                client_socket, address = self.server_socket.accept()
                username = f"Cliente_{address[1]}"
                with self.lock:
                    self.clients[client_socket] = username
                
                self.gui_queue.put(("client_connected", username))
                
                threading.Thread(target=self._handle_client, args=(client_socket, username), daemon=True).start()
            except socket.timeout:
                continue
            except OSError:
                break

    def _handle_client(self, client_socket, username):
        temp_username = username
        try:
            while self.running:
                data = client_socket.recv(2048)
                if not data: break
                
                message = data.decode('utf-8')
                if message.startswith("USERNAME:"):
                    new_username = message.split(":", 1)[1].strip()
                    with self.lock:
                        self.clients[client_socket] = new_username
                    self.gui_queue.put(("client_renamed", (temp_username, new_username)))
                    temp_username = new_username

                elif message.startswith("DATOS_LECCION:"):
                    try:
                        lesson_data = json.loads(message[len("DATOS_LECCION:"):])
                        self.gui_queue.put(("client_data_update", (temp_username, lesson_data)))
                    except json.JSONDecodeError:
                        pass
        finally:
            with self.lock:
                if client_socket in self.clients:
                    del self.clients[client_socket]
            self.gui_queue.put(("client_disconnected", temp_username))
            try: client_socket.close()
            except: pass

class NetworkClient:
    """Maneja la lógica del cliente en hilos separados."""
    def __init__(self, gui_queue):
        self.socket = None
        self.gui_queue = gui_queue
        self.connected = False

    def connect(self, host, port):
        if self.connected: return
        threading.Thread(target=self._connect_thread, args=(host, port), daemon=True).start()

    def _connect_thread(self, host, port):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((host, port))
            self.connected = True
            self.gui_queue.put(("client_connected_to_server", host))
        except Exception as e:
            self.connected = False
            self.socket = None
            self.gui_queue.put(("client_connection_failed", str(e)))

    def disconnect(self):
        if not self.connected: return
        self.connected = False
        try: self.socket.close()
        except: pass
        self.socket = None
        self.gui_queue.put(("client_disconnected_from_server", None))

    def send_data(self, data):
        if self.connected and self.socket:
            try:
                self.socket.sendall(data.encode('utf-8'))
                return True
            except (ConnectionResetError, BrokenPipeError, OSError):
                self.disconnect()
                return False
        return False
        
# =======================================================================
# --- UTILIDADES ---
# =======================================================================
def get_local_ip():
    """Obtiene la dirección IP local de la máquina."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return '127.0.0.1'

# =======================================================================
# --- VENTANAS EMERGENTES (Toplevels) ---
# =======================================================================
class ClientIPWindow(ctk.CTkToplevel):
    def __init__(self, master, callback_connect):
        super().__init__(master)
        self.title("Ingresar IP del Servidor")
        self.geometry("350x180")
        self.resizable(False, False)
        self.grab_set()
        self.callback_connect = callback_connect
        
        ctk.CTkLabel(self, text="Dirección IP del Servidor:", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 5))
        self.ip_entry = ctk.CTkEntry(self, placeholder_text=get_local_ip(), width=250)
        self.ip_entry.pack(pady=5)
        self.ip_entry.bind("<Return>", lambda event: self._connect_and_destroy())
        ctk.CTkButton(self, text="Conectar", command=self._connect_and_destroy, width=150).pack(pady=20)
        self.after(100, self.ip_entry.focus_force)

    def _connect_and_destroy(self):
        ip = self.ip_entry.get().strip()
        self.grab_release()
        self.destroy()
        self.callback_connect(ip or get_local_ip())

class InfoWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Ayuda, Soporte y Licencia")
        self.geometry("750x650")
        self.resizable(False, False)
        self.grab_set()
        self.focus_force()

        tabview = ctk.CTkTabview(self, width=730, height=630)
        tabview.pack(padx=10, pady=10, fill="both", expand=True)
        tabview.add("Guía Rápida")
        tabview.add("Licencia")
        tabview.add("Soporte")

        guia_text = ctk.CTkTextbox(tabview.tab("Guía Rápida"), wrap="word", font=ctk.CTkFont(size=14))
        guia_text.insert("0.0", GUIA_RAPIDA_INFO.strip())
        guia_text.configure(state="disabled")
        guia_text.pack(fill="both", expand=True, padx=10, pady=10)

        licencia_text = ctk.CTkTextbox(tabview.tab("Licencia"), wrap="word", font=ctk.CTkFont(size=13))
        licencia_text.insert("0.0", LICENCIA_INFO.strip())
        licencia_text.configure(state="disabled")
        licencia_text.pack(fill="both", expand=True, padx=10, pady=10)

        support_frame = ctk.CTkFrame(tabview.tab("Soporte"), fg_color="transparent")
        support_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        ctk.CTkLabel(support_frame, text="Apoya el Proyecto", font=ctk.CTkFont(size=26, weight="bold")).pack(pady=(10, 20))
        
        ctk.CTkLabel(support_frame, text="Master Code Typist es un proyecto de código abierto creado por:",
                     wraplength=500, justify="center", font=ctk.CTkFont(size=16)).pack(pady=(10, 5))
        
        ctk.CTkLabel(support_frame, text=AUTOR_CODIGO, font=ctk.CTkFont(size=20, weight="bold"), text_color="#1F93F6").pack()

        ctk.CTkLabel(support_frame, text="\nSi esta herramienta te resulta útil para aprender o enseñar,\nconsidera hacer una donación para apoyar su futuro desarrollo.",
                     wraplength=500, justify="center", font=ctk.CTkFont(size=16)).pack(pady=(30, 15))

        ctk.CTkLabel(support_frame, text="Puedes enviar tu apoyo vía PayPal a:",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 5))
        
        ctk.CTkLabel(support_frame, text=PAYPAL_DONACION, font=ctk.CTkFont(size=18, weight="bold"), text_color="cyan").pack()

        ctk.CTkLabel(support_frame, text="\n¡Muchas gracias por tu apoyo!", font=ctk.CTkFont(size=18, slant="italic")).pack(pady=(40, 10))

class MonitorClientesWindow(ctk.CTkToplevel):
    """Ventana para mostrar en tiempo real el progreso de los clientes."""
    def __init__(self, master, stop_server_callback):
        super().__init__(master)
        self.stop_server_callback = stop_server_callback
        self.title("Monitor de Clientes")
        self.geometry("800x600")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(self, text="Clientes Conectados", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.table_frame = ctk.CTkScrollableFrame(self)
        self.table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.headers = ["Usuario", "Lección", "PPM", "Precisión", "Errores"]
        self.data_labels = {}
        
        self._setup_headers()
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def _setup_headers(self):
        self.table_frame.grid_columnconfigure(0, weight=3)
        for i in range(1, len(self.headers)): self.table_frame.grid_columnconfigure(i, weight=1)

        for col, header in enumerate(self.headers):
            label = ctk.CTkLabel(self.table_frame, text=header, font=ctk.CTkFont(weight="bold"), fg_color=("gray70", "gray25"))
            label.grid(row=0, column=col, padx=5, pady=5, sticky="ew")

    def _on_closing(self):
        self.stop_server_callback()
        self.destroy()
        
    def update_table(self, clients_data):
        all_clients = set(clients_data.keys())
        ui_clients = set(self.data_labels.keys())

        for client in ui_clients - all_clients:
            for label in self.data_labels[client].values(): label.destroy()
            del self.data_labels[client]

        for row, (client, data) in enumerate(clients_data.items(), 1):
            if client not in self.data_labels:
                self.data_labels[client] = {}
                for col, header in enumerate(self.headers):
                    label = ctk.CTkLabel(self.table_frame, text="")
                    label.grid(row=row, column=col, padx=5, pady=2, sticky="w")
                    self.data_labels[client][header] = label

            self.data_labels[client]["Usuario"].configure(text=client)
            ppm = data.get("PPM", 0)
            self.data_labels[client]["PPM"].configure(text=str(ppm), text_color="green" if ppm >= 40 else ("yellow" if ppm >= 20 else "red"))
            precision = data.get("Precision", 0)
            self.data_labels[client]["Precisión"].configure(text=f"{precision}%", text_color="green" if precision >= 95 else ("yellow" if precision >= 90 else "red"))
            errores = data.get("Errores", 0)
            self.data_labels[client]["Errores"].configure(text=str(errores), text_color="red" if errores > 0 else "gray")
            self.data_labels[client]["Lección"].configure(text=data.get("Leccion", "-"), text_color="gray")


# =======================================================================
# --- VISTAS DE LA APLICACIÓN (Frames) ---
# =======================================================================
class BaseView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.manager = controller.manager
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        if self.controller.logo_image:
            logo_label = ctk.CTkLabel(self, image=self.controller.logo_image, text="")
            logo_label.place(x=10, y=10)

    def on_show(self, **kwargs): pass
    def on_hide(self): pass

class VistaRed(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.monitor_window = None

        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=1, column=1)
        
        ctk.CTkLabel(main_frame, text="Master Code Typist", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20, padx=40)
        ctk.CTkButton(main_frame, text="Modo Independiente", command=lambda: controller.show_frame("VistaAuth"), height=50).pack(pady=10, padx=50, fill="x")
        self.server_btn = ctk.CTkButton(main_frame, text="Iniciar Servidor", command=self._toggle_server, height=40)
        self.server_btn.pack(pady=5, padx=50, fill="x")
        self.client_btn = ctk.CTkButton(main_frame, text="Conectar como Cliente", command=self._open_ip_prompt, height=40)
        self.client_btn.pack(pady=5, padx=50, fill="x")
        self.ip_label = ctk.CTkLabel(main_frame, text=f"IP Local: {get_local_ip()}", text_color="gray")
        self.ip_label.pack(pady=20)

    def _toggle_server(self):
        if self.controller.server and self.controller.server.running:
            self.controller.server.stop()
        else:
            self.controller.server = NetworkServer('', 12345, self.controller.gui_queue)
            self.controller.server.start()

    def _open_ip_prompt(self):
        self.client_btn.configure(state="disabled")
        ClientIPWindow(self.controller, self._start_client_connection)

    def _start_client_connection(self, ip_address):
        self.client_btn.configure(text="Conectando...", state="disabled", fg_color="orange")
        self.controller.client = NetworkClient(self.controller.gui_queue)
        self.controller.client.connect(ip_address, 12345)

    def handle_server_started(self, ip_address):
        self.server_btn.configure(text=f"Servidor ACTIVO", fg_color="green", hover_color="dark green")
        self.client_btn.configure(state="disabled")
        self.ip_label.configure(text=f"Comparta esta IP: {ip_address}", text_color="yellow")
        if not self.monitor_window or not self.monitor_window.winfo_exists():
            self.monitor_window = MonitorClientesWindow(self.controller, self._toggle_server)
            self.monitor_window.wm_attributes("-topmost", True)

    def handle_server_stopped(self):
        self.server_btn.configure(text="Iniciar Servidor", fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"], hover_color=ctk.ThemeManager.theme["CTkButton"]["hover_color"])
        self.client_btn.configure(state="normal")
        self.ip_label.configure(text=f"IP Local: {get_local_ip()}", text_color="gray")
        if self.monitor_window and self.monitor_window.winfo_exists():
            self.monitor_window.destroy()
        self.monitor_window = None
    
    def handle_client_connection_to_server(self, host):
        self.client_btn.configure(text=f"Conectado a {host}", fg_color="green", state="disabled")
        self.server_btn.configure(state="disabled")
        self.controller.show_frame("VistaAuth")
        
    def handle_client_connection_failure(self):
        self.client_btn.configure(text="Error de Conexión", fg_color="red")
        self.after(3000, lambda: self.client_btn.configure(text="Conectar como Cliente", state="normal", fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"]))

class VistaAuth(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        center_frame = ctk.CTkFrame(self)
        center_frame.grid(row=1, column=1)
        
        ctk.CTkLabel(center_frame, text="Autenticación", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20, padx=40)
        
        widget_width = 280
        padding_x = 30
        
        self.username_entry = ctk.CTkEntry(center_frame, placeholder_text="Usuario", width=widget_width)
        self.username_entry.pack(pady=10, padx=padding_x)
        
        self.password_entry = ctk.CTkEntry(center_frame, placeholder_text="Contraseña", show="*", width=widget_width)
        self.password_entry.pack(pady=10, padx=padding_x)
        self.password_entry.bind("<Return>", lambda event: self._login_clicked())
        
        self.login_btn = ctk.CTkButton(center_frame, text="Iniciar Sesión", command=self._login_clicked, width=widget_width)
        self.login_btn.pack(pady=20, padx=padding_x)
        
        self.register_btn = ctk.CTkButton(center_frame, text="Registrar Nuevo Usuario", command=self._register_clicked, width=widget_width)
        self.register_btn.pack(pady=10, padx=padding_x)
        
        self.status_label = ctk.CTkLabel(center_frame, text="", text_color="red")
        self.status_label.pack(pady=(10, 0))
        
        ctk.CTkButton(center_frame, text="Volver", command=self._go_back, width=widget_width, fg_color="gray").pack(pady=(40, 20), padx=padding_x)

    def _go_back(self):
        if self.controller.client and self.controller.client.connected:
            self.controller.client.disconnect()
        self.controller.show_frame("VistaRed")

    def on_show(self, **kwargs):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.status_label.configure(text="")

    def _login_clicked(self):
        user, password = self.username_entry.get().strip(), self.password_entry.get().strip()
        if self.manager.autenticar(user, password):
            if self.controller.client and self.controller.client.connected:
                self.controller.client.send_data(f"USERNAME:{user}")
            self.controller.show_frame("VistaMenu")
        else:
            self.status_label.configure(text="Credenciales incorrectas.", text_color="red")
    
    def _register_clicked(self):
        user, password = self.username_entry.get().strip(), self.password_entry.get().strip()
        success, message = self.manager.registrar_usuario(user, password)
        self.status_label.configure(text=message, text_color="green" if success else "red")

class VistaMenu(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=1, column=1, padx=20, pady=20)

        self.title_label = ctk.CTkLabel(main_frame, text="Menú Principal", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.pack(pady=(20, 20), padx=100)
        
        levels_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        levels_frame.pack(pady=10, padx=40, fill="x", expand=True)
        
        self.level_buttons = {}
        for level in ["Básico", "Intermedio", "Avanzado"]:
            btn = ctk.CTkButton(levels_frame, text=f"Nivel {level}", command=lambda l=level: self._start_leccion_nivel(l), height=40)
            btn.pack(pady=5, fill="x")
            self.level_buttons[level] = btn
            
        ctk.CTkButton(main_frame, text="Cargar Archivo de Código", command=self._load_custom_file, height=40).pack(pady=15, padx=40, fill="x")

        self.prog_bar_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.prog_bar_frame.pack(pady=(10, 20), padx=40, fill="x")
        
        ctk.CTkButton(main_frame, text="Ayuda e Info", command=lambda: InfoWindow(self.controller), height=30).pack(pady=10, padx=40, fill="x")
        ctk.CTkButton(main_frame, text="Cerrar Sesión", command=self._logout, fg_color="red", hover_color="dark red", height=30).pack(pady=(10, 20), padx=40, fill="x")

    def on_show(self, **kwargs):
        user = self.manager.usuario_actual
        self.title_label.configure(text=f"Menú - Usuario: {user}")
        self._update_progreso_ui()
        
    def _update_progreso_ui(self):
        for widget in self.prog_bar_frame.winfo_children():
            widget.destroy()
            
        progreso_data = self.manager.get_progreso_actual()
        
        for level in ["Básico", "Intermedio", "Avanzado"]:
            current = progreso_data.get(level, 0)
            total = self.manager.get_total_lecciones(level)
            
            prog_frame = ctk.CTkFrame(self.prog_bar_frame, fg_color="transparent")
            prog_frame.pack(pady=5, fill="x")
            
            ctk.CTkLabel(prog_frame, text=f"{level}: {current}/{total}", width=120, anchor="w").pack(side="left", padx=(0, 10))
            
            progress = ctk.CTkProgressBar(prog_frame, orientation="horizontal")
            progress.pack(side="left", fill="x", expand=True)
            
            if total > 0:
                progress.set(current / total)
                is_complete = current >= total
                self.level_buttons[level].configure(state="disabled" if is_complete else "normal", text=f"Nivel {level}" + (" (COMPLETO)" if is_complete else ""))
            else:
                progress.set(0)

    def _start_leccion_nivel(self, nivel):
        indice = self.manager.get_progreso(nivel)
        leccion_text = self.manager.get_leccion(nivel, indice)
        if leccion_text != "Nivel Completo":
            self.controller.show_frame("VistaLeccion", nivel=nivel, leccion_indice=indice, leccion_text=leccion_text)

    def _load_custom_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Archivos de Código", "*.py *.js *.html *.css"), ("Texto", "*.txt"), ("Todos", "*.*")])
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    custom_text = f.read()
                    filename = os.path.basename(filepath)
                    self.controller.show_frame("VistaLeccion", nivel=f"Personalizado ({filename})", leccion_indice=0, leccion_text=custom_text)
            except Exception as e:
                print(f"Error al cargar el archivo: {e}")
                
    def _logout(self):
        if self.controller.client and self.controller.client.connected:
            self.controller.client.disconnect()
        self.manager.usuario_actual = None
        self.controller.show_frame("VistaAuth")

class VistaLeccion(BaseView):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        self.key_objects = {} 
        self.is_lesson_active = False
        self.nivel = "" 
        self.leccion_text = ""
        self.typed_text = ""
        self.start_time = 0
        self.total_errors_count = 0

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)

        info_frame = ctk.CTkFrame(main_frame)
        info_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        info_frame.grid_columnconfigure(0, weight=1)

        self.info_label = ctk.CTkLabel(info_frame, text="Nivel:", font=ctk.CTkFont(size=18, weight="bold"))
        self.info_label.pack(pady=5, padx=10, anchor="w")

        self.leccion_display = ctk.CTkTextbox(info_frame, height=200, wrap="none", font=("Consolas", 15))
        self.leccion_display.pack(pady=5, padx=10, fill="x", expand=True)
        self.leccion_display.configure(state="disabled")

        self.input_entry = ctk.CTkEntry(info_frame, placeholder_text="Empieza a escribir aquí...", font=("Consolas", 15))
        self.input_entry.pack(pady=5, padx=10, fill="x")
        self.input_entry.bind("<Key>", self._handle_keypress)
        self.input_entry_original_color = self.input_entry.cget("fg_color")
        
        self.keyboard_frame = ctk.CTkFrame(main_frame)
        self.keyboard_frame.grid(row=2, column=0, pady=10, sticky="ew")
        self._setup_keyboard_layout(self.keyboard_frame)

        metrics_frame = ctk.CTkFrame(main_frame)
        metrics_frame.grid(row=0, column=1, rowspan=3, sticky="ns", padx=(10, 0))
        ctk.CTkLabel(metrics_frame, text="Métricas", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10, padx=20)
        self.ppm_label = ctk.CTkLabel(metrics_frame, text="PPM: 0", font=ctk.CTkFont(size=16))
        self.ppm_label.pack(pady=5, padx=20, anchor="w")
        self.accuracy_label = ctk.CTkLabel(metrics_frame, text="Precisión: 100.0%", font=ctk.CTkFont(size=16))
        self.accuracy_label.pack(pady=5, padx=20, anchor="w")
        self.errors_label = ctk.CTkLabel(metrics_frame, text="Errores: 0", font=ctk.CTkFont(size=16))
        self.errors_label.pack(pady=5, padx=20, anchor="w")
        ctk.CTkButton(metrics_frame, text="Volver al Menú", command=self.go_to_menu, fg_color="red", hover_color="dark red").pack(side="bottom", pady=20, padx=20)

    def on_show(self, nivel, leccion_indice, leccion_text):
        self.nivel = nivel
        self.leccion_text = leccion_text.replace('\r\n', '\n')
        self.restart_leccion()

    def restart_leccion(self):
        self.typed_text = ""
        self.total_errors_count = 0
        self.is_lesson_active = True
        self.start_time = time.perf_counter()
        
        self.leccion_display.configure(state="normal")
        self.leccion_display.delete("1.0", tk.END)
        self.leccion_display.insert("1.0", self.leccion_text)
        
        self.info_label.configure(text=f"Nivel: {self.nivel}")
        self.input_entry.delete(0, tk.END)
        self.input_entry.configure(state="normal")
        self.input_entry.focus_set()
        
        self._update_metrics()
        self._update_display_and_keyboard()

    def _handle_keypress(self, event):
        if not self.is_lesson_active:
            return "break"

        if event.keysym in ('Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R', 'Caps_Lock', 'Tab',
                             'Super_L', 'Super_R', 'Menu', 'Escape'):
            return "break"

        self.input_entry.delete(0, tk.END)

        if event.keysym == 'BackSpace':
            if len(self.typed_text) > 0:
                self.typed_text = self.typed_text[:-1]
                self._update_display_and_keyboard()
                self._update_metrics()
            return "break"

        if len(self.typed_text) >= len(self.leccion_text):
            return "break"

        typed_char = '\n' if event.keysym == 'Return' else event.char
        expected_char = self.leccion_text[len(self.typed_text)]

        if typed_char and (typed_char.isprintable() or typed_char in ['\n', '\t']):
            if typed_char == expected_char:
                self.typed_text += typed_char
            else:
                self.total_errors_count += 1
                self._flash_error_feedback()
        
        self._update_display_and_keyboard()
        self._update_metrics()

        if len(self.typed_text) >= len(self.leccion_text):
            self.is_lesson_active = False
            self.input_entry.configure(state="disabled")
            self._update_display_and_keyboard()
            self.after(250, self._show_results)

        return "break"

    def _flash_error_feedback(self):
        self.input_entry.configure(fg_color="#D32F2F")
        self.after(150, lambda: self.input_entry.configure(fg_color=self.input_entry_original_color))
    
    def _update_display_and_keyboard(self):
        self.leccion_display.configure(state="normal")
        self.leccion_display.tag_remove("correct", "1.0", tk.END)
        self.leccion_display.tag_remove("current", "1.0", tk.END)

        self.leccion_display.tag_config("correct", foreground="#00FF00", background=COLOR_DEFECTO)
        self.leccion_display.tag_config("current", background=COLOR_PRESIONADO, foreground="#000000")

        if self.typed_text:
            end_correct_index = self.leccion_display.index(f"1.0 + {len(self.typed_text)} chars")
            self.leccion_display.tag_add("correct", "1.0", end_correct_index)
        
        current_pos_idx = len(self.typed_text)
        if current_pos_idx < len(self.leccion_text):
            start_current_index = self.leccion_display.index(f"1.0 + {current_pos_idx} chars")
            end_current_index = self.leccion_display.index(f"{start_current_index} + 1 char")
            self.leccion_display.tag_add("current", start_current_index, end_current_index)
            self.leccion_display.see(start_current_index)
        
        self.leccion_display.configure(state="disabled")
        self._highlight_required_keys()

    def _highlight_required_keys(self):
        for key in self.key_objects:
            self.key_objects[key].configure(fg_color=COLOR_DEFECTO)
        
        current_pos_idx = len(self.typed_text)
        if not self.is_lesson_active or current_pos_idx >= len(self.leccion_text):
            return

        required_char = self.leccion_text[current_pos_idx]
        base_key_name = None
        needs_shift = False

        if required_char in SHIFT_MAP_TO_KEY:
            needs_shift = True
            base_key_name = SHIFT_MAP_TO_KEY[required_char]
        elif required_char.isupper():
            needs_shift = True
            base_key_name = required_char.lower()
        elif required_char == '\n':
            base_key_name = 'ENTER'
        elif required_char == ' ':
            base_key_name = 'SPACE'
        elif required_char == '\t':
            base_key_name = 'TAB'
        else:
            base_key_name = required_char
            
        if base_key_name and base_key_name in self.key_objects:
            self.key_objects[base_key_name].configure(fg_color=COLOR_REQUERIDO)

        if needs_shift:
            if 'SHIFT_L' in self.key_objects: self.key_objects['SHIFT_L'].configure(fg_color=COLOR_REQUERIDO)
            if 'SHIFT_R' in self.key_objects: self.key_objects['SHIFT_R'].configure(fg_color=COLOR_REQUERIDO)

    def _update_metrics(self):
        if not self.is_lesson_active and len(self.typed_text) == 0:
            self.errors_label.configure(text=f"Errores: 0")
            self.accuracy_label.configure(text=f"Precisión: 100.0%")
            return

        time_elapsed = time.perf_counter() - self.start_time
        correct_chars = len(self.typed_text)
        total_presses = correct_chars + self.total_errors_count
        
        ppm = (correct_chars / 5) / (time_elapsed / 60) if time_elapsed > 1 else 0
        accuracy = (correct_chars / total_presses) * 100 if total_presses > 0 else 100

        self.ppm_label.configure(text=f"PPM: {int(ppm)}")
        self.accuracy_label.configure(text=f"Precisión: {accuracy:.1f}%")
        self.errors_label.configure(text=f"Errores: {self.total_errors_count}")

        self._send_progress_to_server(int(ppm), accuracy)

    def _send_progress_to_server(self, ppm, accuracy):
        if self.controller.client and self.controller.client.connected:
            lesson_data = {
                "Leccion": self.nivel.split('(')[0].strip(),
                "PPM": ppm, "Precision": round(accuracy, 1), "Errores": self.total_errors_count
            }
            message = f"DATOS_LECCION:{json.dumps(lesson_data)}"
            self.controller.client.send_data(message)

    def _show_results(self):
        time_elapsed = time.perf_counter() - self.start_time
        correct_chars = len(self.leccion_text)
        total_presses = correct_chars + self.total_errors_count
        
        ppm = int((correct_chars / 5) / (time_elapsed / 60)) if time_elapsed > 1 else 0
        accuracy = (correct_chars / total_presses) * 100 if total_presses > 0 else 100
        estrellas = self.manager.calcular_estrellas(ppm, accuracy)
        
        message = (f"¡Lección Completada!\n\n"
                   f"PPM Final: {ppm}\n"
                   f"Precisión Final: {accuracy:.1f}%\n"
                   f"Errores Totales: {self.total_errors_count}\n\n"
                   f"Puntuación: {'★' * estrellas}{'☆' * (3 - estrellas)}")

        next_leccion_text = None
        next_leccion_indice = 0
        if self.nivel in ["Básico", "Intermedio", "Avanzado"]:
            self.manager.avanzar_progreso(self.nivel)
            next_leccion_indice = self.manager.get_progreso(self.nivel)
            next_leccion_text = self.manager.get_leccion(self.nivel, next_leccion_indice)
        
        self._create_result_window(message, next_leccion_text, next_leccion_indice)

    def _create_result_window(self, message, next_leccion_text, next_leccion_indice):
        result_window = ctk.CTkToplevel(self.controller)
        result_window.title("Resultados")
        result_window.geometry("450x350")
        result_window.grab_set()
        result_window.focus_force()
        result_window.resizable(False, False)

        ctk.CTkLabel(result_window, text=message, font=ctk.CTkFont(size=16), justify="left").pack(pady=20, padx=20)
        
        btn_frame = ctk.CTkFrame(result_window, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Reiniciar", command=lambda: (result_window.destroy(), self.restart_leccion())).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Menú", command=lambda: (result_window.destroy(), self.go_to_menu())).pack(side="left", padx=10)
        
        if next_leccion_text and next_leccion_text != "Nivel Completo":
             ctk.CTkButton(btn_frame, text="Siguiente", command=lambda: (result_window.destroy(), self.controller.show_frame("VistaLeccion", nivel=self.nivel, leccion_indice=next_leccion_indice, leccion_text=next_leccion_text)), fg_color="green", hover_color="dark green").pack(side="left", padx=10)
    
    def go_to_menu(self):
        self.is_lesson_active = False
        self.controller.show_frame("VistaMenu")

    def _get_key_name(self, char):
        return char.upper() if len(char) > 1 else char

    def _setup_keyboard_layout(self, parent_frame):
        keyboard_container = ctk.CTkFrame(parent_frame, fg_color="transparent")
        keyboard_container.pack(padx=10, pady=5, anchor="center")
        
        KEYBOARD_LAYOUT = [
            ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'BACKSPACE'],
            ['TAB', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
            ['CAPS', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", 'ENTER'],
            ['SHIFT_L', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'SHIFT_R'],
            ['CTRL_L', 'Super_L', 'ALT_L', 'SPACE', 'ALT_R', 'Super_R', 'MENU', 'CTRL_R']
        ]
        KEY_WIDTHS = {'BACKSPACE': 2, 'TAB': 1.5, 'CAPS': 1.75, 'ENTER': 2.25, 'SHIFT_L': 2.5, 
                      'SHIFT_R': 2.5, 'SPACE': 8, 'CTRL_L': 1.5, 'CTRL_R': 1.5, 'ALT_L': 1.25, 
                      'ALT_R': 1.25, 'Super_L': 1.25, 'Super_R': 1.25, 'MENU': 1.25}

        for row in KEYBOARD_LAYOUT:
            row_frame = ctk.CTkFrame(keyboard_container, fg_color="transparent")
            row_frame.pack(fill="x", pady=2, anchor="center")
            for key_char in row:
                key_name = self._get_key_name(key_char)
                width = int(KEY_WIDTHS.get(key_name, 1) * 45)
                btn = ctk.CTkButton(row_frame, text=key_name, width=width, height=40, fg_color=COLOR_DEFECTO, corner_radius=KEY_CORNER_RADIUS)
                btn.pack(side="left", padx=2)
                self.key_objects[key_name] = btn


# =======================================================================
# --- CLASE PRINCIPAL DE LA APLICACIÓN ---
# =======================================================================
class App(ctk.CTk):
    """Ventana principal y gestor de navegación."""
    def __init__(self):
        super().__init__()
        self.title("Master Code Typist (Corregido)")
        self.geometry("1200x800")
        
        self.manager = LeccionManager()
        self.gui_queue = queue.Queue()
        self.server = None
        self.client = None
        
        try:
            self.logo_image = ctk.CTkImage(Image.open(resource_path("img/logo.png")), size=(50, 50))
        except:
            self.logo_image = None
        
        container = ctk.CTkFrame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        for F in (VistaRed, VistaAuth, VistaMenu, VistaLeccion):
            frame = F(parent=container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.current_frame_name = None
        self.show_frame("VistaRed")
        
        self.after(100, self._process_gui_queue)

    def show_frame(self, page_name, **kwargs):
        if self.current_frame_name:
            self.frames[self.current_frame_name].on_hide()
        
        self.current_frame_name = page_name
        frame = self.frames[page_name]
        frame.on_show(**kwargs)
        frame.tkraise()

    def _process_gui_queue(self):
        """Procesa mensajes de la cola de red de forma segura."""
        try:
            while not self.gui_queue.empty():
                msg_type, data = self.gui_queue.get_nowait()
                vista_red = self.frames["VistaRed"]
                
                if msg_type == "server_started":
                    vista_red.handle_server_started(data)
                elif msg_type == "server_stopped":
                    vista_red.handle_server_stopped()
                elif msg_type == "client_connected":
                    if self.server: self.server.client_data[data] = {}
                    self._update_monitor()
                elif msg_type == "client_disconnected":
                    if self.server and data in self.server.client_data:
                        del self.server.client_data[data]
                    self._update_monitor()
                elif msg_type == "client_renamed":
                    old, new = data
                    if self.server and old in self.server.client_data:
                        self.server.client_data[new] = self.server.client_data.pop(old)
                    self._update_monitor()
                elif msg_type == "client_data_update":
                    user, lesson_data = data
                    if self.server: self.server.client_data[user] = lesson_data
                    self._update_monitor()
                elif msg_type == "client_connected_to_server":
                    vista_red.handle_client_connection_to_server(data)
                elif msg_type == "client_connection_failed":
                    vista_red.handle_client_connection_failure()
                elif msg_type == "client_disconnected_from_server":
                    self.client = None
                    if self.current_frame_name not in ["VistaRed", "VistaAuth"]:
                        self.show_frame("VistaRed")
                    vista_red.handle_server_stopped()
        finally:
            self.after(100, self._process_gui_queue)

    def _update_monitor(self):
        monitor = self.frames["VistaRed"].monitor_window
        if monitor and monitor.winfo_exists() and self.server:
            monitor.update_table(self.server.client_data)

    def on_closing(self):
        if self.server: self.server.stop()
        if self.client: self.client.disconnect()
        self.destroy()

if __name__ == "__main__":
    if not os.path.exists("img"):
        os.makedirs("img")
        print("Carpeta 'img' creada. Asegúrate de poner tu 'logo.png' dentro.")
        
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()