import customtkinter as ctk
from PIL import Image
import tkinter.filedialog as filedialog
import time
import threading
from tkinter import END, Toplevel
import json 
import random 
import socket 

# --- CONFIGURACIÓN BASE Y CONSTANTES GLOBALES ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Constantes de Colores para Teclado Virtual
COLOR_REQUERIDO = "green"  
COLOR_PRESIONADO = "yellow" 
COLOR_DEFECTO = "gray40"   

# V 13.25: Mapeo de Símbolos a Teclas Base (Configuración INGLÉS US)
SHIFT_MAP_TO_KEY = {
    # Carácter Requerido : Tecla Base (sin Shift)
    '!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '^': '6', '&': '7', 
    '*': '8', '(': '9', ')': '0', '_': '-', '+': '=', '{': '[', '}': ']', 
    '|': '\\', ':': ';', '"': "'", '<': ',', '>': '.', '?': '/' 
}

# --- DATOS DE CLIENTES SIMULADOS ---
# Almacén de datos que el servidor usa para mostrar en el monitor. 
SimulatedClientData = {
    "Alumno_A": {"Leccion": "Básico 3/30", "PPM": 25, "Precision": 95.2, "Errores": 3},
    "Alumno_B": {"Leccion": "Intermedio 10/30", "PPM": 42, "Precision": 98.9, "Errores": 0},
    "Alumno_C": {"Leccion": "Avanzado 1/20", "PPM": 15, "Precision": 88.0, "Errores": 7},
}

# --- GESTOR DE DATOS (SERVICE CLASS) ---
class LeccionManager:
    """Clase de servicio para gestionar lecciones, progreso y autenticación."""
    
    # Lecciones de prueba con volumen variable (AUMENTADO EN V 13.24)
    DATOS_LECCIONES = {
        # Lecciones más largas y más cantidad (30 lecciones en total)
        "Básico": [
            "def saludo():\n  return 'Hola mundo'",
            "x = 10\ny = 20\nprint(x + y)",
            "for i in range(5):\n  print(i)",
            "a = True; b = False; print(a and b)",
            "if x > 5: y = 10 else: y = 0",
            "while n > 0: n -= 1",
            "lista = [1, 2, 3]",
            "tuple = (4, 5)",
            "dict = {'k': 'v'}",
            "set = {1, 2, 3}"
        ] * 3, # Multiplicado por 3 (30 lecciones)

        # Lecciones de longitud media y más cantidad (30 lecciones en total)
        "Intermedio": [
            "class Coche:\n  def __init__(self, color):\n    self.color = color\n\nmi_coche = Coche('rojo')\nprint(mi_coche.color)",
            "def factorial(n):\n  if n == 0:\n    return 1\n  else:\n    return n * factorial(n-1)",
            "try:\n  resultado = 10 / 0\nexcept ZeroDivisionError:\n  print('Error de división.')",
            "import os\n\nfile_path = 'data.txt'\nif os.path.exists(file_path): print('Existe')",
            "def fib(n):\n  a, b = 0, 1\n  while a < n:\n    print(a)\n    a, b = b, a+b",
            "data = [x**2 for x in range(10) if x % 2 == 0]",
            "from math import sqrt\n\nprint(sqrt(16))",
            "async def fetch_data(url):\n  pass",
            "class Persona:\n  pass\np1 = Persona()",
            "with open('temp.txt', 'w') as f:\n  f.write('prueba')"
        ] * 3, # Multiplicado por 3 (30 lecciones)

        # Lecciones largas y más cantidad (20 lecciones en total)
        "Avanzado": [
            "def quick_sort(arr):\n  if len(arr) <= 1:\n    return arr\n  pivot = arr[len(arr) // 2]\n  left = [x for x in arr if x < pivot]\n  middle = [x for x in arr if x == pivot]\n  right = [x for x in arr if x > pivot]\n  return quick_sort(left) + middle + quick_sort(right)\n\nlista = [3, 6, 8, 1, 4, 7]\nprint(quick_sort(lista))",
            "def process_data(data): return [item * 2 for item in data if item > 5] * 10 # Esta es una línea de código deliberadamente muy, muy larga. Debe requerir desplazamiento horizontal. Esto prueba que el parámetro 'wrap=\"none\"' está funcionando correctamente en el CTkTextbox, permitiendo que las líneas de código de una sola línea se extiendan fuera del campo de visión, tal como en un IDE profesional, forzando al usuario a utilizar el scroll para ver el resto de la lección de tipificación. ¡Esto es genial para practicar la continuidad en código extenso! Las lecciones más largas deben ser copiadas con precisión para obtener 3 estrellas. [Fin de la línea larga]",
            "import requests\n\ndef obtener_datos(url):\n  try:\n    response = requests.get(url)\n    response.raise_for_status()\n    return response.json()\n  except requests.exceptions.RequestException as e:\n    return f'Error: {e}'",
            "class Singleton:\n  _instance = None\n  def __new__(cls):\n    if cls._instance is None:\n      cls._instance = super(Singleton, cls).__new__(cls)\n    return cls._instance",
            "def merge_sort(arr):\n  if len(arr) > 1:\n    mid = len(arr) // 2\n    L = arr[:mid]\n    R = arr[mid:]\n    merge_sort(L)\n    merge_sort(R)\n  return arr",
            "from collections import defaultdict\n\nd = defaultdict(int)\nd['a'] += 1\nprint(d)",
            "lambda x: x + 10",
            "def generator_func():\n  for i in range(5):\n    yield i * 2",
            "import time\n\nstart = time.perf_counter()\ntime.sleep(0.1)\nend = time.perf_counter()\nprint(f'{end - start}')",
            "def recursive_sum(n):\n  if n <= 1:\n    return n\n  return n + recursive_sum(n-1)"
        ] * 2, # Multiplicado por 2 (20 lecciones)
    }
    
    def __init__(self):
        self.usuario_actual = None
        self.archivo_datos = "users_data.json"
        
        self.USUARIOS = {}
        self.progreso_usuario = {}
        
        self._cargar_datos_usuarios()
        
    # --- Métodos de Persistencia ---
    def _cargar_datos_usuarios(self):
        """Carga usuarios y progreso desde JSON, inicializando si es necesario."""
        try:
            with open(self.archivo_datos, 'r') as f:
                data = json.load(f)
                self.USUARIOS = data.get("usuarios", {"Admin": "12345"}) 
                self.progreso_usuario = data.get("progreso", {})
        except FileNotFoundError:
            self.USUARIOS = {"Admin": "12345"}
            self.progreso_usuario = {}
        except json.JSONDecodeError:
            print("Error: Archivo de datos de usuario corrupto. Restaurando valores por defecto.")
            self.USUARIOS = {"Admin": "12345"}
            self.progreso_usuario = {}

    def _guardar_datos_usuarios(self):
        """Guarda usuarios y progreso en JSON."""
        data = {
            "usuarios": self.USUARIOS,
            "progreso": self.progreso_usuario
        }
        with open(self.archivo_datos, 'w') as f:
            json.dump(data, f, indent=4)
            
    # --- Métodos de Autenticación/Registro ---
    def autenticar(self, user, password):
        """Verifica las credenciales y establece el usuario actual."""
        if self.USUARIOS.get(user) == password:
            self.usuario_actual = user
            print(f"Usuario {user} autenticado.")
            return True
        return False
    
    def registrar_usuario(self, user, password):
        """Crea un nuevo usuario con progreso inicial."""
        if user in self.USUARIOS:
            return False, "El nombre de usuario ya existe."
        if not user or not password:
            return False, "El usuario y la contraseña no pueden estar vacíos."
        
        self.USUARIOS[user] = password
        self.progreso_usuario[user] = {
            "Básico": 0,    
            "Intermedio": 0,
            "Avanzado": 0
        }
        self._guardar_datos_usuarios()
        return True, "Registro exitoso. Puede iniciar sesión."
    
    # --- Métodos de Progreso ---
    def get_progreso_actual(self):
        """Devuelve el progreso del usuario actual."""
        if self.usuario_actual and self.usuario_actual in self.progreso_usuario:
            return self.progreso_usuario[self.usuario_actual]
        return {"Básico": 0, "Intermedio": 0, "Avanzado": 0}

    def get_leccion(self, nivel, indice):
        num_lecciones = len(self.DATOS_LECCIONES[nivel])
        if 0 <= indice < num_lecciones:
            return self.DATOS_LECCIONES[nivel][indice]
        return "Nivel Completo"

    def avanzar_progreso(self, nivel):
        """Avanza la lección del usuario actual en el nivel especificado."""
        if not self.usuario_actual:
            return False
            
        progreso = self.get_progreso_actual().get(nivel, 0)
        num_lecciones = len(self.DATOS_LECCIONES[nivel])
        
        if progreso < num_lecciones: # Usar el número total de lecciones
            if self.usuario_actual not in self.progreso_usuario:
                self.progreso_usuario[self.usuario_actual] = {"Básico": 0, "Intermedio": 0, "Avanzado": 0}
                
            self.progreso_usuario[self.usuario_actual][nivel] = progreso + 1
            self._guardar_datos_usuarios()
            return True
        return False
    
    def get_progreso(self, nivel):
        return self.get_progreso_actual().get(nivel, 0)

    def get_total_lecciones(self, nivel):
        return len(self.DATOS_LECCIONES.get(nivel, []))

    def calcular_estrellas(self, ppm, precision):
        if precision >= 98 and ppm >= 40:
            return 3
        elif precision >= 95 and ppm >= 30:
            return 2
        elif precision >= 90 and ppm >= 20:
            return 1
        return 0

# --- FUNCIÓN DE UTILIDAD ---
def get_local_ip():
    """Obtiene la dirección IP local de la máquina usando sockets."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Usa una dirección externa (como Google DNS) para determinar la IP de la interfaz local
        s.connect(("8.8.8.8", 80)) 
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1' # Fallback a localhost
    finally:
        s.close()
    return IP

# --- CLASE PRINCIPAL DE LA APLICACIÓN ---
class App(ctk.CTk):
    """Ventana principal y gestor de navegación."""
    
    def __init__(self):
        super().__init__()
        
        # Título de la aplicación ajustado en el pulido anterior
        self.title("Master Code Typist - Entrenamiento de Programación") 
        self.geometry("1000x800")
        self.resizable(True, True) 
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.manager = LeccionManager()
        
        # --- Variables de Estado de Red ---
        self.active_client_socket = None # Socket del cliente activo
        self.client_username = "Estudiante" # Nombre de usuario asignado por el servidor
        # ----------------------------------

        try:
            # Note: Assuming 'img/logo.png' exists
            self.logo_image = ctk.CTkImage(
                Image.open("img/logo.png"), 
                size=(50, 50)
            )
        except FileNotFoundError:
            self.logo_image = None
        
        self.container = ctk.CTkFrame(self)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        self.current_frame = None

        self._load_frames()
        self.show_frame("VistaRed")

    def _load_frames(self):
        """Inicializa y almacena todas las vistas (CTkFrames)."""
        for F in (VistaRed, VistaAuth, VistaMenu, VistaLeccion):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self, manager=self) # Se pasa el objeto App completo como manager
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_name, **kwargs):
        """Muestra una vista y oculta la anterior."""
        frame = self.frames[page_name]
        
        if hasattr(self.current_frame, "on_hide"):
             self.current_frame.on_hide() 
        
        if hasattr(frame, "on_show"):
            frame.on_show(**kwargs)
            
        frame.tkraise()
        self.current_frame = frame

    def place_logo(self, frame):
        """Coloca el logo en la esquina superior izquierda de cualquier vista."""
        if self.logo_image:
            logo_label = ctk.CTkLabel(frame, image=self.logo_image, text="")
            logo_label.place(x=10, y=10)


# --- VISTAS MODULARES (CTkFrame) ---

class BaseView(ctk.CTkFrame):
    # BaseView ahora recibe el objeto App completo
    def __init__(self, parent, controller, manager):
        super().__init__(parent)
        self.controller = controller
        # Redirigir el manager interno al manager de lecciones real
        self.manager = manager.manager 
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        self.controller.place_logo(self)
        
    def on_hide(self):
        """Se llama antes de que esta vista sea reemplazada."""
        pass

class VistaRed(BaseView):
    def __init__(self, parent, controller, manager):
        super().__init__(parent, controller, manager)
        
        # --- Variables de Red REALES ---
        self.server_ip = get_local_ip()
        self.server_port = 12345
        self.server_socket = None
        self.is_server_running = False
        self.clients = {} # {socket: 'username'}
        self.client_threads = []
        self.listen_thread = None
        self.client_socket = None # Socket del cliente
        # --- Fin Variables de Red ---

        self.monitor_window = None 
        
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=1, column=1, padx=50, pady=50, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(main_frame, text="JEM Master Code - Modo de Operación", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20, padx=20)
        
        # Modo Independiente
        ctk.CTkButton(main_frame, text="Modo Independiente (Entrenamiento Local)", 
                      command=lambda: controller.show_frame("VistaAuth"),
                      height=50, font=ctk.CTkFont(size=16)).pack(pady=10, padx=50, fill="x")
        
        # Botones de Red (Instanciación)
        self.server_btn = ctk.CTkButton(main_frame, text="Iniciar Servidor (Profesor)", 
                                        command=self._toggle_server,
                                        height=40)
        self.server_btn.pack(pady=5, padx=50, fill="x")
                      
        self.client_btn = ctk.CTkButton(main_frame, text="Conectar como Cliente", 
                                        command=self._iniciar_cliente, # FUNCIÓN DE CLIENTE REAL
                                        height=40)
        self.client_btn.pack(pady=5, padx=50, fill="x")
                      
        self.ip_label = ctk.CTkLabel(main_frame, text=f"IP Local: {self.server_ip}", text_color="gray")
        self.ip_label.pack(pady=(20, 10))


    # --- LÓGICA DEL SERVIDOR ---

    def _toggle_server(self):
        """Inicia/detiene el servidor real usando sockets."""
        
        if not self.is_server_running:
            # --- Lógica de INICIO ---
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            try:
                if self.monitor_window and self.monitor_window.winfo_exists():
                    self.monitor_window.destroy()

                self.server_socket.bind(('', self.server_port)) # '' para escuchar en todas las interfaces
                self.server_socket.listen(5) # Máximo de 5 conexiones en cola
                self.server_socket.settimeout(1.0) # Permite que el hilo se verifique y se detenga
                self.is_server_running = True
                
                # Iniciar la ventana de monitoreo 
                self.monitor_window = MonitorClientesWindow(self.controller)
                self.controller.after(0, self.monitor_window.update_table, SimulatedClientData)

                # Crear e iniciar el hilo de escucha de conexiones
                self.listen_thread = threading.Thread(target=self._server_listen_thread, daemon=True)
                self.listen_thread.start()
                
                self.server_btn.configure(text=f"Servidor ACTIVO en {self.server_ip}", fg_color="green", hover_color="dark green")
                self.client_btn.configure(state="disabled")
                self.ip_label.configure(text=f"Comparta esta IP con sus alumnos: {self.server_ip}", text_color="yellow")
                
                print(f"SERVIDOR INICIADO: Escuchando en {self.server_ip}:{self.server_port} y monitor activo.")
            
            except Exception as e:
                self.is_server_running = False
                self.server_btn.configure(text=f"Error: {e}", fg_color="red", hover_color="dark red")
                print(f"ERROR al iniciar el servidor: {e}")
                
        else:
            # --- Lógica de DETENCIÓN ---
            print("SERVIDOR DETENIDO.")
            self.is_server_running = False
            self.server_socket.close()
            
            # 1. Cerrar sockets de clientes activos y limpiar
            for client_socket in list(self.clients.keys()):
                try:
                    client_socket.close()
                except:
                    pass
            self.clients.clear() 
            
            # 2. Detener y cerrar el monitor
            if self.monitor_window and self.monitor_window.winfo_exists():
                self.monitor_window.destroy()
            self.monitor_window = None

            # 3. Restaurar UI
            self.server_btn.configure(text="Iniciar Servidor (Profesor)", fg_color="#3A7DB8", hover_color="#2D639C")
            self.client_btn.configure(state="normal")
            self.ip_label.configure(text=f"IP Local: {self.server_ip}", text_color="gray")


    def _server_listen_thread(self):
        """Hilo principal del servidor para aceptar nuevas conexiones."""
        while self.is_server_running:
            try:
                client_socket, client_address = self.server_socket.accept()
                
                print(f"NUEVA CONEXIÓN de cliente: {client_address[0]}:{client_address[1]}")
                
                handler_thread = threading.Thread(target=self._handle_client, args=(client_socket, client_address), daemon=True)
                self.client_threads.append(handler_thread)
                handler_thread.start()
                
            except socket.timeout:
                pass 
            except Exception as e:
                if self.is_server_running:
                    print(f"SERVIDOR ERROR en el hilo de escucha: {e}")
                break

    def _handle_client(self, client_socket, client_address):
        """Maneja la comunicación bidireccional con un único cliente."""
        
        username = f"Cliente_{client_address[1]}" 
        self.clients[client_socket] = username 
        
        # Inicializar datos en la tabla del servidor
        self.controller.after(0, lambda: SimulatedClientData.__setitem__(username, {"Leccion": "Conectado", "PPM": 0, "Precision": 0, "Errores": 0}))
        if self.monitor_window and self.monitor_window.winfo_exists():
            self.controller.after(0, self.monitor_window.update_table, SimulatedClientData)
        
        try:
            # Enviar el nombre asignado
            client_socket.sendall(f"NOMBRE_ASIGNADO:{username}".encode('utf-8'))
        except:
             pass
        
        # Bucle de recepción de datos
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break 
                    
                message = data.decode('utf-8')
                print(f"DATOS DE {username}: {message}")
                
                if message.startswith("DATOS_LECCION:"):
                    try:
                        json_data = message[len("DATOS_LECCION:"):].strip()
                        lesson_data = json.loads(json_data)
                        
                        self.controller.after(0, 
                            lambda: SimulatedClientData.__setitem__(username, lesson_data)
                        )
                        
                        if self.monitor_window and self.monitor_window.winfo_exists():
                            self.controller.after(0, self.monitor_window.update_table, SimulatedClientData) 
                        
                    except json.JSONDecodeError:
                        print(f"SERVIDOR: Error al decodificar JSON de {username}")
                        
            except ConnectionResetError:
                break 
            except Exception as e:
                if self.is_server_running:
                    print(f"SERVIDOR ERROR con {username}: {e}")
                break
        
        # Limpieza (Desconexión)
        print(f"CLIENTE DESCONECTADO: {username}")
        if client_socket in self.clients:
            del self.clients[client_socket] 
            
        if username in SimulatedClientData:
            del SimulatedClientData[username]
            
        if self.monitor_window and self.monitor_window.winfo_exists():
             self.controller.after(0, self.monitor_window.update_table, SimulatedClientData) 
        client_socket.close()

    # --- LÓGICA DEL CLIENTE ---
    
    def _iniciar_cliente(self):
        """Intenta conectarse al servidor en un hilo separado."""
        SERVER_IP = self.server_ip 
        SERVER_PORT = 12345
        
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.settimeout(5) # 5 segundos de timeout
        
        try:
            print(f"CLIENTE CONECTADO: Intentando conexión con {SERVER_IP}:{SERVER_PORT}...")
            self.client_socket.connect((SERVER_IP, SERVER_PORT))
            
            # Si la conexión es exitosa:
            self.controller.active_client_socket = self.client_socket 
            self.client_btn.configure(text=f"Conectado a {SERVER_IP}", fg_color="green", hover_color="dark green", state="disabled")
            self.server_btn.configure(state="disabled")
            
            self._client_receive_thread = threading.Thread(target=self._recibir_datos_cliente, daemon=True)
            self._client_receive_thread.start()
            
            self.controller.show_frame("VistaAuth") 
            
        except ConnectionRefusedError:
            self.client_btn.configure(text="Conexión Rechazada", fg_color="red", hover_color="dark red")
            print("CLIENTE: Conexión rechazada. Asegúrese de que el servidor esté activo.")
            self.controller.after(3000, lambda: self.client_btn.configure(text="Conectar como Cliente", fg_color="#3A7DB8", hover_color="#2D639C", state="normal"))
        except TimeoutError:
            self.client_btn.configure(text="Tiempo de espera agotado", fg_color="red", hover_color="dark red")
            print("CLIENTE: Tiempo de espera agotado.")
            self.controller.after(3000, lambda: self.client_btn.configure(text="Conectar como Cliente", fg_color="#3A7DB8", hover_color="#2D639C", state="normal"))
        except Exception as e:
             self.client_btn.configure(text=f"Error de Conexión", fg_color="red", hover_color="dark red")
             print(f"CLIENTE ERROR: {e}")
             self.controller.after(3000, lambda: self.client_btn.configure(text="Conectar como Cliente", fg_color="#3A7DB8", hover_color="#2D639C", state="normal"))


    def _recibir_datos_cliente(self):
        """Hilo dedicado a recibir y procesar datos del servidor."""
        while self.controller.active_client_socket:
            try:
                data = self.controller.active_client_socket.recv(1024) 
                if not data:
                    print("CLIENTE DESCONECTADO: El servidor cerró la conexión.")
                    break
                    
                mensaje = data.decode('utf-8')

                if mensaje.startswith("NOMBRE_ASIGNADO:"):
                    username = mensaje.split(':')[1]
                    self.controller.client_username = username.strip()
                    print(f"CLIENTE: Nombre asignado: {self.controller.client_username}")
                
            except ConnectionResetError:
                print("CLIENTE DESCONECTADO: Conexión terminada por el servidor.")
                break
            except Exception as e:
                print(f"CLIENTE ERROR de recepción: {e}")
                break
                
        # Limpieza de la conexión
        if self.controller.active_client_socket:
            self.controller.active_client_socket.close()
        self.controller.active_client_socket = None
        
        self.controller.after(0, self.server_btn.configure, {"state": "normal"})
        self.controller.after(0, self.client_btn.configure, {"text": "Conectar como Cliente", "fg_color": "#3A7DB8", "hover_color": "#2D639C", "state": "normal"})


class VistaAuth(BaseView):
    def __init__(self, parent, controller, manager):
        super().__init__(parent, controller, manager)

        auth_frame = ctk.CTkFrame(self, width=400, height=350)
        auth_frame.grid(row=1, column=1, padx=50, pady=50)
        auth_frame.pack_propagate(False) 
        
        ctk.CTkLabel(auth_frame, text="INICIO / REGISTRO", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        self.user_entry = ctk.CTkEntry(auth_frame, placeholder_text="Usuario", width=250)
        self.user_entry.pack(pady=10)
        
        self.pass_entry = ctk.CTkEntry(auth_frame, placeholder_text="Contraseña", show="*", width=250)
        self.pass_entry.pack(pady=10)
        
        self.error_label = ctk.CTkLabel(auth_frame, text="", text_color="red")
        self.error_label.pack(pady=5)
        
        button_frame = ctk.CTkFrame(auth_frame, fg_color="transparent")
        button_frame.pack(pady=10)
        
        ctk.CTkButton(button_frame, text="Acceder", command=self.login, width=120).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Registrarse", command=self.register, width=120, fg_color="#3A7DB8", hover_color="#2D639C").pack(side="left", padx=5)


    def login(self):
        user = self.user_entry.get()
        password = self.pass_entry.get()
        
        if self.manager.autenticar(user, password):
            self.error_label.configure(text="")
            self.controller.show_frame("VistaMenu")
            self.user_entry.delete(0, END)
            self.pass_entry.delete(0, END)
        else:
            self.error_label.configure(text="Usuario o contraseña incorrectos.")
            
    def register(self):
        user = self.user_entry.get()
        password = self.pass_entry.get()
        
        success, message = self.manager.registrar_usuario(user, password)
        
        if success:
            self.error_label.configure(text=message, text_color="green")
            self.pass_entry.delete(0, END)
            self.user_entry.focus_set()
        else:
            self.error_label.configure(text=message, text_color="red")

class VistaMenu(BaseView):
    def __init__(self, parent, controller, manager):
        super().__init__(parent, controller, manager)
        
        self.grid_rowconfigure(1, weight=3)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self, text="MENÚ PRINCIPAL Y PROGRESO", font=ctk.CTkFont(size=28, weight="bold")).grid(row=0, column=1, pady=(20, 0), sticky="n")
        
        self.niveles_frame = ctk.CTkFrame(self)
        self.niveles_frame.grid(row=1, column=1, padx=50, pady=20, sticky="nsew")
        
        self.niveles_frame.grid_columnconfigure(0, weight=1)
        self.niveles_frame.grid_columnconfigure(1, weight=1)
        self.niveles_frame.grid_columnconfigure(2, weight=1)
        
        self.nivel_frames = {}
        self._create_nivel_cards()
        
        # Contenedor para la parte inferior (Práctica Personalizada e Información)
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.grid(row=2, column=1, padx=50, pady=(0, 30), sticky="s")
        footer_frame.grid_columnconfigure(0, weight=1) # Columna central para centrar

        # Práctica Personalizada (Fila 0 del footer)
        personal_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        personal_frame.grid(row=0, column=0, pady=(0, 10))
        ctk.CTkLabel(personal_frame, text="Práctica Personalizada:", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left", padx=10)
        ctk.CTkButton(personal_frame, text="Cargar Archivo de Código", command=self.cargar_leccion_personal, width=250).pack(side="left", padx=10)
        
        # Botón de Información y Soporte (Fila 1 del footer) - AGREGADO
        ctk.CTkButton(footer_frame, 
                      text="Información y Soporte", 
                      command=self._show_info_window, 
                      width=250,
                      fg_color="#3A7DB8", 
                      hover_color="#2D639C").grid(row=1, column=0, pady=(10, 0))


    def _create_nivel_cards(self):
        niveles = ["Básico", "Intermedio", "Avanzado"]
        for i, nivel in enumerate(niveles):
            card = ctk.CTkFrame(self.niveles_frame, corner_radius=10)
            card.grid(row=0, column=i, padx=20, pady=20, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)
            
            ctk.CTkLabel(card, text=nivel.upper(), font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(15, 5))
            
            progreso_label = ctk.CTkLabel(card, text="")
            progreso_label.pack(pady=5)
            
            progreso_bar = ctk.CTkProgressBar(card, orientation="horizontal", width=200)
            progreso_bar.set(0)
            progreso_bar.pack(pady=5)
            
            continue_btn = ctk.CTkButton(card, text="Continuar", 
                                         command=lambda n=nivel: self.iniciar_leccion(n))
            continue_btn.pack(pady=(10, 15))
            
            self.nivel_frames[nivel] = {
                "label": progreso_label,
                "bar": progreso_bar,
                "button": continue_btn,
            }

    def on_show(self):
        user = self.manager.usuario_actual if self.manager.usuario_actual else "Invitado"
        print(f"Menú cargado para el usuario: {user}") 
        
        for nivel in ["Básico", "Intermedio", "Avanzado"]:
            self._update_card(nivel)

    def _update_card(self, nivel):
        progreso = self.manager.get_progreso(nivel)
        total_lecciones = self.manager.get_total_lecciones(nivel)
        
        if total_lecciones == 0:
            text = "SIN LECCIONES"
            bar_value = 0.0
            state = "disabled"
        elif progreso >= total_lecciones:
            text = "NIVEL COMPLETO"
            bar_value = 1.0
            state = "disabled"
        else:
            text = f"Lección {progreso + 1} / {total_lecciones}"
            bar_value = progreso / total_lecciones
            state = "normal"
            
        self.nivel_frames[nivel]["label"].configure(text=text)
        self.nivel_frames[nivel]["bar"].set(bar_value)
        self.nivel_frames[nivel]["button"].configure(state=state)

    def iniciar_leccion(self, nivel):
        progreso = self.manager.get_progreso(nivel)
        leccion_text = self.manager.get_leccion(nivel, progreso)
        
        self.controller.show_frame("VistaLeccion", 
                                   nivel=nivel, 
                                   leccion_indice=progreso, 
                                   leccion_text=leccion_text)

    def cargar_leccion_personal(self):
        filetypes = [
            ("Archivos de Código", "*.txt *.py *.html *.java *.js *.c *.cpp *.cs *.php *.rb"), 
            ("Todos los archivos", "*.*")
        ]
        filepath = filedialog.askopenfilename(defaultextension=".txt", filetypes=filetypes)
        
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    leccion_text = f.read()
                
                if leccion_text.startswith('\ufeff'):
                    leccion_text = leccion_text[1:]
                leccion_text = leccion_text.strip()
                
                if not leccion_text:
                    raise ValueError("El archivo cargado está vacío o solo contiene espacios.")
                
                self.controller.show_frame("VistaLeccion", 
                                           nivel="Personalizado", 
                                           leccion_indice=0, 
                                           leccion_text=leccion_text)
            except Exception as e:
                print(f"Error al cargar archivo: {e}")
                
    def _show_info_window(self):
        """Muestra la ventana emergente con la guía rápida, licencia y donaciones."""
        InfoWindow(self.controller)


class VistaLeccion(BaseView):
    def __init__(self, parent, controller, manager):
        super().__init__(parent, controller, manager)
        
        self.leccion_text = ""
        self.entrada_usuario = ""
        self.current_index = 0
        self.errores = 0
        self.start_time = 0
        self.caracteres_correctos = 0
        self.nivel = None
        self.leccion_indice = 0 
        
        self.bloqueo_activo = False
        self.anulacion_id = None 

        # --- GRID CONFIGURATION ---
        self.grid_rowconfigure(0, weight=0) 
        self.grid_rowconfigure(1, weight=3) 
        self.grid_rowconfigure(2, weight=0) 
        self.grid_rowconfigure(3, weight=3) 
        self.grid_rowconfigure(4, weight=0) 
        
        # Columna 0: Vacía, Columna 1: Contenido Principal, Columna 2: Botón Menú
        self.grid_columnconfigure(0, weight=0) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_columnconfigure(2, weight=0) 

        # --- RETURN TO MENU BUTTON ---
        self.return_btn = ctk.CTkButton(self, 
                                        text="< Menú Principal", 
                                        command=lambda: controller.show_frame("VistaMenu"),
                                        width=150)
        self.return_btn.grid(row=0, column=2, padx=20, pady=10, sticky="ne") 
        
        # --- STATS FRAME ---
        stats_frame = ctk.CTkFrame(self)
        stats_frame.grid(row=0, column=1, padx=20, pady=10, sticky="n") 
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        
        self.ppm_label = ctk.CTkLabel(stats_frame, text="PPM: 0", font=ctk.CTkFont(size=18))
        self.ppm_label.grid(row=0, column=0, padx=20, pady=10)
        self.precision_label = ctk.CTkLabel(stats_frame, text="Precisión: 100%", font=ctk.CTkFont(size=18))
        self.precision_label.grid(row=0, column=1, padx=20, pady=10)
        self.errores_label = ctk.CTkLabel(stats_frame, text="Errores: 0", font=ctk.CTkFont(size=18))
        self.errores_label.grid(row=0, column=2, padx=20, pady=10)
        
        # --- CODE TEXTBOX ---
        self.code_text = ctk.CTkTextbox(self, state="disabled", font=ctk.CTkFont(family="Consolas", size=16), wrap="word") 
        self.code_text.grid(row=1, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")

        # --- INPUT ENTRY ---
        self.input_entry = ctk.CTkEntry(self, font=ctk.CTkFont(family="Consolas", size=16))
        self.input_entry.grid(row=2, column=0, columnspan=3, padx=20, pady=10, sticky="ew")
        self.input_entry.bind("<Key>", self.manejar_pulsacion)
        self.input_entry.bind("<KeyRelease>", self.manejar_liberacion)
        self.input_entry.focus_set()
        
        # --- INDICADOR DE BLOQUEO ---
        self.bloqueo_label = ctk.CTkLabel(self.input_entry, text="", text_color="red", font=ctk.CTkFont(size=12))
        self.bloqueo_label.place(relx=1.0, rely=0.5, anchor="e", x=-10) 

        # --- TECLADO FRAME ---
        self.teclado_frame = ctk.CTkFrame(self)
        self.teclado_frame.grid(row=3, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")
        self.teclas_map = {}
        self._create_keyboard_layout()
        
        # --- ACTION FRAME (Repetir / Siguiente) ---
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=4, column=1, pady=20)
        action_frame.grid_columnconfigure((0, 1), weight=1)

        self.repeat_btn = ctk.CTkButton(action_frame, text="🔁 Repetir Lección", 
                                        command=self.reiniciar_leccion, 
                                        state="disabled", width=180)
        self.repeat_btn.grid(row=0, column=0, padx=10)
        
        self.next_btn = ctk.CTkButton(action_frame, text="Siguiente Lección", 
                                      command=self.avanzar_leccion, 
                                      state="disabled", width=180)
        self.next_btn.grid(row=0, column=1, padx=10)
        
        self.update_stats_id = None

    def on_hide(self):
        """Cancela la actualización automática de estadísticas al cambiar de vista."""
        if self.update_stats_id:
            self.after_cancel(self.update_stats_id)
            self.update_stats_id = None

    def _create_keyboard_layout(self):
        # V 13.23: Ajuste de layout a QWERTY estándar (incluyendo Backspace, Tab, Caps Lock)
        layout = [
            # Fila numérica
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "BackSpace"],
            # Fila QWERTY
            ["Tab", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]"],
            # Fila ASDF
            ["Caps_Lock", "a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'", "\\"],
            # Fila ZXC, con Enter/Return
            ["Shift_L", "z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "Return"],
            # Fila de espacio
            ["space"]
        ]
        
        # Ajustar el número de columnas para que se ajusten las filas más largas
        max_cols = max(len(row) for row in layout)
        for col in range(max_cols):
            self.teclado_frame.grid_columnconfigure(col, weight=1)
        
        for row_idx, row in enumerate(layout):
            self.teclado_frame.grid_rowconfigure(row_idx, weight=1)
            
            for col_idx, key in enumerate(row):
                btn = None
                span = 1 # Columnas que ocupa la tecla
                
                # Definiciones especiales para teclas largas
                if key == "BackSpace":
                    btn_text = "BACKSPACE"
                    span = 2
                elif key == "Tab":
                    btn_text = "TAB"
                    span = 1
                elif key == "Caps_Lock":
                    btn_text = "CAPS LOCK"
                    span = 2
                elif key == "Return":
                    # Tecla ENTER
                    btn_text = "ENTER"
                    span = 2 
                elif key == "Shift_L":
                    btn_text = "SHIFT"
                    span = 3 
                elif key == "space":
                    # La tecla SPACE se maneja de forma especial al final
                    btn_text = "SPACE"
                    span = max_cols
                    col_idx = 0 
                else:
                    # Teclas normales
                    btn_text = key.upper()
                    span = 1
                
                # Crear el botón y mapear su posición
                if key == "space":
                    btn = ctk.CTkButton(self.teclado_frame, text=btn_text, fg_color=COLOR_DEFECTO, text_color="white", height=50)
                    btn.grid(row=row_idx, column=col_idx, columnspan=span, padx=2, pady=2, sticky="ew")
                    # FIX: Mapeo de la tecla 'space' más robusto
                    self.teclas_map[' '] = btn 
                else:
                    # Usar col_idx de enumerate
                    btn = ctk.CTkButton(self.teclado_frame, text=btn_text, 
                                        fg_color=COLOR_DEFECTO, text_color="white", width=40, height=40)
                    btn.grid(row=row_idx, column=col_idx, columnspan=span, padx=2, pady=2, sticky="nsew")
                    
                    self.teclas_map[key] = btn
                    
                    # Mapear Shift_R al mismo botón Shift_L
                    if key == "Shift_L":
                        self.teclas_map["Shift_R"] = btn
                        self.teclas_map["Shift"] = btn
                    
                    # Mapeo especial para Backspace (manejo de evento)
                    if key == "BackSpace":
                        # Mapeo a la clave interna del evento
                        self.teclas_map['BackSpace'] = btn 
                    
    def on_show(self, nivel, leccion_indice, leccion_text):
        self.nivel = nivel
        self.leccion_indice = leccion_indice
        self.leccion_text = leccion_text
        
        self.entrada_usuario = ""
        self.current_index = 0
        self.errores = 0
        self.caracteres_correctos = 0
        self.start_time = time.time()
        self.input_entry.configure(state="normal")
        self.input_entry.delete(0, END)
        self.next_btn.configure(state="disabled")
        self.repeat_btn.configure(state="disabled")
        self.bloqueo_activo = False
        self.bloqueo_label.configure(text="")
        
        self.update_code_visualization()
        self.update_stats()
        self._reset_teclado_virtual()
        self.update_required_key()
        self.input_entry.focus_set()
        
        if self.update_stats_id:
            self.after_cancel(self.update_stats_id)
        self.update_stats_id = self.after(1000, self._auto_update_stats)

    def _auto_update_stats(self):
        self.update_stats()
        if self.current_index < len(self.leccion_text):
            self.update_stats_id = self.after(1000, self._auto_update_stats)

    def _reset_teclado_virtual(self):
        # Reiniciar todos los colores a COLOR_DEFECTO
        for key, btn in self.teclas_map.items():
            btn.configure(fg_color=COLOR_DEFECTO)
            
    # --- FUNCIÓN CORREGIDA ---
    def highlight_pressed_key(self, event_keysym, event_char=None):
        """Resalta la tecla presionada y programa la restauración del color."""
        key_id = None
        
        # 1. Mapeo de teclas especiales usando event_keysym
        if event_keysym == 'BackSpace':
            key_id = 'BackSpace'
        elif event_keysym in ('Shift_L', 'Shift_R'): 
            key_id = 'Shift_L'
        elif event_keysym == 'Return': 
            key_id = 'Return'
        elif event_keysym == 'Tab':
            key_id = 'Tab'
        elif event_keysym == 'space':
            key_id = ' ' 
        elif event_keysym == 'Caps_Lock':
            key_id = 'Caps_Lock'
        
        # 2. Mapeo de teclas normales/caracteres usando event_char
        elif event_char: 
            key_id = event_char.lower()
            
            # Si el carácter es un símbolo que requiere Shift (ej: '{'), 
            # buscamos su tecla base ('[').
            if key_id in SHIFT_MAP_TO_KEY:
               key_id = SHIFT_MAP_TO_KEY.get(key_id)
            
            # Si el carácter es una letra mayúscula, usamos su versión minúscula 
            # (la tecla base) para el resaltado, ya que el shift fue manejado por keysym.
            elif len(key_id) == 1 and key_id.isalpha():
                key_id = key_id.lower()


        # 3. Resaltar la tecla si se encuentra en el mapa
        btn = self.teclas_map.get(key_id)
        if btn:
            btn.configure(fg_color=COLOR_PRESIONADO)
            # Llama a _restore_key_color después de 100ms para restaurar el color
            self.after(100, lambda: self._restore_key_color(btn))
    # -------------------------


    def update_required_key(self):
        self._reset_teclado_virtual()
        
        if self.bloqueo_activo:
            self.bloqueo_label.configure(text="ERROR. Use BACKSPACE.", text_color="red")
            # Resaltar Backspace si el bloqueo está activo
            if 'BackSpace' in self.teclas_map:
                self.teclas_map['BackSpace'].configure(fg_color="red")
            return

        if self.current_index >= len(self.leccion_text):
            return

        required_char = self.leccion_text[self.current_index]
        key_base = required_char
        needs_shift = False
        
        self.bloqueo_label.configure(text="") 

        if required_char.isalpha():
            if required_char.isupper():
                key_base = required_char.lower()
                needs_shift = True
            
        elif required_char == ' ':
            key_base = ' ' # Usar el carácter de espacio para el mapeo
            
        elif required_char == '\n':
            key_base = 'Return'
            
        elif required_char in SHIFT_MAP_TO_KEY:
            key_base = SHIFT_MAP_TO_KEY.get(required_char, required_char)
            needs_shift = True
        
        # Caracteres sin Shift (ej: coma, punto, guion, igual, corchetes)
        elif key_base in (',', '.', '-', '=', '[', ']', ';', "'", '\\', '/'):
            needs_shift = False
            
        # 1. Resaltar la tecla base
        if key_base in self.teclas_map:
            self.teclas_map[key_base].configure(fg_color=COLOR_REQUERIDO)
        elif key_base == ' ': # Manejo especial para el espacio
            self.teclas_map[' '].configure(fg_color=COLOR_REQUERIDO)
            
        # 2. Resaltar SHIFT si es necesario
        if needs_shift and "Shift_L" in self.teclas_map:
            self.teclas_map["Shift_L"].configure(fg_color=COLOR_REQUERIDO)
        elif not needs_shift and "Shift_L" in self.teclas_map:
             self.teclas_map["Shift_L"].configure(fg_color=COLOR_DEFECTO)


    def _restore_key_color(self, btn):
        """Restaura los colores del teclado llamando a update_required_key."""
        self.update_required_key()


    def manejar_pulsacion(self, event):
        """Controla la lógica de bloqueo, avance y feedback."""
        
        # 1. Manejo INCONDICIONAL del Backspace (Debe ir primero)
        if event.keysym == 'BackSpace':
            self.highlight_pressed_key(event.keysym)
            if self.current_index > 0:
                self.current_index -= 1
                self.entrada_usuario = self.entrada_usuario[:-1]
                self.bloqueo_activo = False 
                self.update_code_visualization()
                self.update_required_key()
                self.update_stats()
            return "break"
        
        # 2. Consumir eventos Shift, Control, Alt, etc. (No caracteres de entrada)
        if event.keysym in ('Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R', 'Tab', 'Caps_Lock', 'Win_L', 'Win_R'):
            self.highlight_pressed_key(event.keysym)
            return "break" 

        # 3. Si estamos al final, salir
        if self.current_index >= len(self.leccion_text):
            return "break"

        required_char = self.leccion_text[self.current_index]
        char_ingresado = event.char
        
        # 4. Bloqueo de Error: Si está activo, ignora todo (excepto Backspace, ya manejado)
        if self.bloqueo_activo:
            return "break"
        
        # 5. Ignorar pulsaciones sin carácter asociado 
        if not char_ingresado and event.keysym not in ('Return', 'space'): 
             pass

        # 6. Mapear teclas especiales a sus caracteres (Enter/Space)
        if event.keysym == 'Return':
            char_ingresado = '\n'
        elif event.keysym == 'space':
            char_ingresado = ' '
        
        # 7. Resaltar la tecla presionada
        self.highlight_pressed_key(event.keysym, event.char)


        # 8. Evaluación de la tecla
        if char_ingresado:
            if char_ingresado == required_char:
                self.entrada_usuario += char_ingresado
                self.current_index += 1
                self.caracteres_correctos += 1
                self.bloqueo_activo = False
            else:
                # Carácter INCORRECTO
                self.errores += 1
                self.bloqueo_activo = True
            
            self.update_stats() 

            # 9. Fin de la lección
            if self.current_index >= len(self.leccion_text):
                self.finalizar_leccion()

            self.update_code_visualization()
            self.update_required_key()
        
        # Detener la propagación incondicionalmente
        return "break" 

    def manejar_liberacion(self, event):
        """Consume el evento de liberación de Shift para eliminar el pop-up de Teclas Especiales."""
        if event.keysym in ('Shift_L', 'Shift_R'):
            return "break" 
        pass

    # --- VISUALIZACIÓN Y ESTADÍSTICAS ---
    def update_code_visualization(self):
        self.code_text.configure(state="normal")
        self.code_text.delete("1.0", END)
        
        self.code_text.tag_config("correcto", foreground="gray70") 
        self.code_text.tag_config("incorrecto", foreground="red", background="gray10") 
        self.code_text.tag_config("requerido", background="#2a5a2a", foreground="white") 
        
        i = 0
        for char in self.leccion_text:
            tag = "correcto"
            if i < len(self.entrada_usuario):
                if self.entrada_usuario[i] != char:
                    tag = "incorrecto"
            elif i == self.current_index:
                tag = "requerido"

            display_char = char
            
            if tag == "requerido" and char == '\n':
                display_char = '¶' # Símbolo visible para salto de línea
                    
            self.code_text.insert(END, display_char, tag)
            i += 1
            
        self.code_text.configure(state="disabled")
        
        if self.current_index < len(self.leccion_text):
            index = f"1.0 + {self.current_index} chars"
            self.code_text.see(index)


    def update_stats(self):
        elapsed_time = time.time() - self.start_time
        
        if elapsed_time > 0:
            ppm = round((self.caracteres_correctos / 5) / (elapsed_time / 60))
        else:
            ppm = 0
            
        total_pulsaciones = self.caracteres_correctos + self.errores
        if total_pulsaciones > 0:
            precision = round((self.caracteres_correctos / total_pulsaciones) * 100)
        else:
            precision = 100
            
        self.ppm_label.configure(text=f"PPM: {ppm}")
        self.precision_label.configure(text=f"Precisión: {precision}%")
        self.errores_label.configure(text=f"Errores: {self.errores}")
        
        self.current_ppm = ppm
        self.current_precision = precision

    def finalizar_leccion(self):
        if self.update_stats_id:
            self.after_cancel(self.update_stats_id)
            self.update_stats_id = None
            
        self.input_entry.configure(state="disabled")
        self.bloqueo_label.configure(text="")
        self.update_stats()
        
        estrellas = self.manager.calcular_estrellas(self.current_ppm, self.current_precision)
        
        # --- Lógica de Red (Envío de Resultados) ---
        if self.controller.active_client_socket and self.nivel != "Personalizado":
            # 1. Crear el paquete de datos
            leccion_text = f"{self.nivel} {self.leccion_indice + 1}/{self.manager.get_total_lecciones(self.nivel)}"
            
            lesson_results = {
                "Usuario": self.controller.client_username,
                "Leccion": leccion_text,
                "PPM": int(self.current_ppm), 
                "Precision": int(self.current_precision),
                "Errores": self.errores
            }
            # 2. Intentar enviar si hay un socket de cliente activo
            self._enviar_resultados_servidor(lesson_results) 
        # ---------------------------------------------

        if self.nivel != "Personalizado":
            self.manager.avanzar_progreso(self.nivel) 
            
            total_lecciones = self.manager.get_total_lecciones(self.nivel)
            if self.manager.get_progreso(self.nivel) >= total_lecciones:
                self.next_btn.configure(text="Nivel Completo", state="disabled")
            else:
                self.next_btn.configure(text="Siguiente Lección", state="normal")
        else:
            self.next_btn.configure(text="Volver al Menú", command=lambda: self.controller.show_frame("VistaMenu"), state="normal")
            
        self.repeat_btn.configure(state="normal")
        
        print(f"Lección Finalizada. Estrellas: {estrellas}, PPM: {self.current_ppm}, Precisión: {self.current_precision}%")

    def _enviar_resultados_servidor(self, data):
        """Envía los datos de la lección al servidor si el cliente está conectado."""
        client_socket = self.controller.active_client_socket
        
        if client_socket:
            try:
                json_data = json.dumps(data)
                message = f"DATOS_LECCION: {json_data}"
                client_socket.sendall(message.encode('utf-8'))
                print(f"CLIENTE: Resultados de lección enviados al servidor.")
                
            except BrokenPipeError:
                print("CLIENTE ERROR: Conexión con el servidor perdida. No se enviaron los resultados.")
                self.controller.active_client_socket = None
            except Exception as e:
                print(f"CLIENTE ERROR al enviar datos: {e}")
                
        else:
            print("CLIENTE: No conectado a un servidor. Resultados guardados localmente.")

    def reiniciar_leccion(self):
        """Reinicia la lección actual cargando la misma lección desde el principio."""
        # Llama a on_show con los mismos parámetros de la lección actual
        self.on_show(nivel=self.nivel, 
                     leccion_indice=self.leccion_indice, 
                     leccion_text=self.leccion_text)

    def avanzar_leccion(self):
        self.controller.show_frame("VistaMenu")


# --- NUEVA VENTANA DE INFORMACIÓN Y SOPORTE (InfoWindow) - MODIFICADO ---
class InfoWindow(ctk.CTkToplevel):
    """Ventana emergente para mostrar guía, licencia y contacto."""

    def __init__(self, master_controller):
        super().__init__(master_controller)
        self.title("Información y Soporte")
        self.geometry("500x450") # Ajuste de tamaño para el nuevo botón
        self.resizable(True, True) 
        
        self.grab_set() 
        self.focus_force() 
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) 
        self.grid_rowconfigure(1, weight=0) # Fila para el botón

        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.pack_propagate(False)

        ctk.CTkLabel(content_frame, text="Información del Programa", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)
        
        # Guía Rápida
        ctk.CTkLabel(content_frame, text="GUÍA RÁPIDA", font=ctk.CTkFont(weight="bold"), text_color="cyan").pack(pady=(10, 0))
        ctk.CTkLabel(content_frame, text="1. Selecciona un nivel (Básico, Intermedio, Avanzado).\n2. Escribe el código exactamente como se muestra.\n3. Presiona BACKSPACE para corregir errores.", justify="left").pack(padx=20)
        
        # Licencia
        ctk.CTkLabel(content_frame, text="LICENCIA DE CÓDIGO ABIERTO", font=ctk.CTkFont(weight="bold"), text_color="cyan").pack(pady=(15, 0))
        ctk.CTkLabel(content_frame, text="Este software es de código abierto. Consulte el repositorio para más detalles.", justify="left").pack(padx=20)

        # Donaciones (Correo de PayPal CORREGIDO)
        ctk.CTkLabel(content_frame, text="GMAIL DE DONACIONES (PayPal)", font=ctk.CTkFont(weight="bold"), text_color="cyan").pack(pady=(15, 0))
        ctk.CTkLabel(content_frame, text="jemmasterdc@gmail.com", text_color="yellow").pack() 
        
        # Botón de Volver/Cerrar (AÑADIDO)
        ctk.CTkButton(self, 
                      text="Cerrar / Volver al Menú", 
                      command=self.destroy,
                      width=200,
                      fg_color="red",
                      hover_color="#AA0000").grid(row=1, column=0, pady=(0, 20))
                      
        # Protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self.destroy)


# --- NUEVA VENTANA DE MONITOREO ---
class MonitorClientesWindow(ctk.CTkToplevel):
    """Ventana emergente que monitorea a los clientes conectados al servidor."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Monitor de Clientes (Servidor)")
        self.geometry("750x450")
        self.resizable(False, False)
        
        self.grab_set()
        self.focus_force()
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Estadísticas de Clientes en Tiempo Real", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=10)
        
        self.table_frame = ctk.CTkFrame(self)
        self.table_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        self.header_labels = {}
        self.data_labels = {}
        self._create_table_headers()
        
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _create_table_headers(self):
        """Crea los encabezados fijos de la tabla."""
        headers = ["Usuario", "Lección Actual", "PPM", "Precisión (%)", "Errores"]
        
        for i, header_text in enumerate(headers):
            self.table_frame.grid_columnconfigure(i, weight=1)
            label = ctk.CTkLabel(self.table_frame, text=header_text, 
                                 font=ctk.CTkFont(weight="bold"), 
                                 fg_color="gray20", 
                                 corner_radius=5)
            label.grid(row=0, column=i, padx=5, pady=5, sticky="ew")
            self.header_labels[header_text] = label
            
    def update_table(self, client_data):
        """Actualiza la tabla con los datos más recientes."""
        row_idx = 1
        
        # Obtener la lista actual de widgets en la tabla (filas de datos)
        current_rows = [w for w in self.table_frame.winfo_children() if int(w.grid_info()['row']) >= 1]
        for widget in current_rows:
            widget.grid_forget()
            
        self.data_labels = {} # Resetear el mapeo
        
        # Ordenar clientes para consistencia visual
        sorted_clients = sorted(client_data.keys())

        for client in sorted_clients:
            data = client_data[client]
            self.data_labels[client] = {}
            col_idx = 0
            
            # Nombre del Cliente
            name_label = ctk.CTkLabel(self.table_frame, text=client, font=ctk.CTkFont(weight="bold"))
            name_label.grid(row=row_idx, column=col_idx, padx=5, pady=2, sticky="ew")
            self.data_labels[client]["Usuario"] = name_label
            col_idx += 1
            
            # Datos de la Lección
            for key in ["Leccion", "PPM", "Precision", "Errores"]:
                value = data.get(key, "-")
                
                # Formato y Color para PPM
                if key == "PPM":
                    color = "green" if value >= 40 else ("yellow" if value >= 20 else "red")
                    value_text = str(value)
                # Formato y Color para Precisión
                elif key == "Precision":
                    color = "green" if value >= 95 else ("yellow" if value >= 90 else "red")
                    value_text = f"{value}%"
                # Formato y Color para Errores
                elif key == "Errores":
                    color = "red" if value > 0 else "gray"
                    value_text = str(value)
                else: # Leccion
                    color = "gray"
                    value_text = str(value)
                    
                data_label = ctk.CTkLabel(self.table_frame, text=value_text, text_color=color)
                data_label.grid(row=row_idx, column=col_idx, padx=5, pady=2, sticky="ew")
                self.data_labels[client][key] = data_label
                col_idx += 1
            
            row_idx += 1


if __name__ == "__main__":
    import os
    if not os.path.exists("img"):
        os.makedirs("img")
        print("Carpeta 'img' creada. Coloque 'logo.png' dentro.")
        
    app = App()
    app.mainloop()