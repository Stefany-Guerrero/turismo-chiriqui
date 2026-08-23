# Turismo Chiriquí

Plataforma web para la gestión de tours y servicios turísticos en la provincia de Chiriquí, Panamá. Permite a los clientes reservar tours, a los proveedores gestionar sus servicios y a los administradores controlar toda la operación.

## Funcionalidades

### Clientes
- Explorar tours disponibles con calendario de disponibilidad en tiempo real
- Reservar tours con selección de fecha, personas y transporte
- Pago con tarjeta de crédito/débito o Yappy
- Solicitudes de viaje personalizadas con asistente inteligente
- Consultar estado de reservas y cancelar pendientes
- Recibir notificaciones por correo electrónico

### Proveedores
- Gestionar tours (crear, editar, eliminar)
- Definir disponibilidad, precios y especificaciones del vehículo
- Gestionar promociones y descuentos

### Administradores
- Dashboard con estadísticas de reservas e ingresos
- Gestión completa de tours, proveedores, clientes y promociones
- Administrar solicitudes de viaje personalizadas
- Gestión de transacciones y pagos
- Registro de auditoría de todas las acciones

## Tecnologías

| Componente | Tecnología |
|------------|-----------|
| Backend | Flask 2.3 (Python) |
| Base de datos | MariaDB 11.4 (MySQL) |
| ORM | SQLAlchemy + Flask-SQLAlchemy |
| Frontend | Bootstrap 5, Jinja2 |
| Autenticación | Flask-Login + Flask-Bcrypt |
| Seguridad | Flask-WTF (CSRF), hashing bcrypt |
| Correo | Flask-Mail (SMTP Gmail) |
| PDF | ReportLab, xhtml2pdf |
| QR | zxing-cpp |
| Base de datos NoSQL | MongoDB (sincronización secundaria) |

## Requisitos Previos

- **Python 3.10+**
- **MariaDB 11.4** (o MySQL 8.0+)
- **Git** (para clonar el repositorio)
- **MongoDB** (opcional, para sincronización secundaria)

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Stefany-Guerrero/turismo-chiriqui.git
cd turismo-chiriqui
```

Si descargaste el ZIP, extrae la carpeta y ábrela en terminal:
```bash
cd turismo-chiriqui
```

### 2. Crear el entorno virtual

```bash
python -m venv venv
```

Activarlo:

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar la base de datos

Asegúrate de que MariaDB/MySQL esté corriendo. Luego crea la base de datos:

```sql
CREATE DATABASE turismo_chiriqui CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

O restaura desde un backup si tienes uno disponible:
```bash
mysql -u root -p turismo_chiriqui < backup_completo.sql
```

### 5. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto con estas variables:

```env
# Base de datos
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=3306
DB_NAME=turismo_chiriqui

# Clave secreta para sesiones (genera una propia)
SECRET_KEY=tu_clave_secreta_aqui

# Correo electrónico (opcional)
MAIL_USERNAME=tu_correo@gmail.com
MAIL_PASSWORD=tu_contraseña_de_aplicacion
MAIL_DEFAULT_SENDER=tu_correo@gmail.com

# URL base
BASE_URL=http://localhost:5000
```

> **Nota:** Si no configuras `SECRET_KEY`, se generará una automáticamente cada vez que inicie el servidor (las sesiones se perderán al reiniciar).

### 6. Iniciar el servidor

```bash
python run.py
```

El servidor estará disponible en:
- Local: `http://127.0.0.1:5000`
- Red local: `http://tu_ip:5000`

La primera vez se creará automáticamente:
- Todas las tablas de la base de datos
- Un usuario administrador con contraseña aleatoria (se muestra en consola)

## Credenciales por Defecto

### Administrador
| Campo | Valor |
|-------|-------|
| Email | `admin@turismo.com` |
| Contraseña | Se genera automáticamente la primera vez (revisar consola) |

### Base de Datos
| Campo | Valor |
|-------|-------|
| Usuario | `root` |
| Contraseña | La que configures en `.env` |
| Base de datos | `turismo_chiriqui` |
| Puerto | `3306` |

## Estructura del Proyecto

```
turismo_chiriqui/
├── app/
│   ├── __init__.py          # Creación de la app Flask
│   ├── config.py            # Configuración general
│   ├── forms.py             # Formularios WTForms
│   ├── email_utils.py       # Utilidades de correo
│   ├── models/              # Modelos de base de datos
│   │   ├── usuario.py       # Usuarios y autenticación
│   │   ├── cliente.py       # Clientes
│   │   ├── servicio.py      # Tours/servicios
│   │   ├── reserva.py       # Reservas y solicitudes
│   │   ├── promocion.py     # Promociones y descuentos
│   │   ├── proveedor.py     # Proveedores de tours
│   │   ├── transaccion.py   # Transacciones de pago
│   │   ├── notificacion.py  # Notificaciones
│   │   └── auditoria.py     # Registro de auditoría
│   ├── routes/              # Rutas (controladores)
│   │   ├── auth.py          # Login, registro, recuperación
│   │   ├── main.py          # Página principal, tours, pagos
│   │   ├── reservas.py      # Gestión de reservas
│   │   ├── solicitudes.py   # Solicitudes personalizadas
│   │   ├── servicios.py     # CRUD de servicios
│   │   ├── promociones.py   # CRUD de promociones
│   │   ├── proveedores.py   # CRUD de proveedores
│   │   ├── transacciones.py # Historial de transacciones
│   │   └── planificador.py  # Asistente de viajes
│   ├── templates/           # Plantillas HTML (Jinja2)
│   │   ├── base.html        # Layout principal
│   │   ├── tour_detalle.html
│   ├── static/              # CSS, JS, imágenes
│   └── utils/               # Utilidades (backups, MongoDB sync)
├── scripts/                 # Scripts de backup y mantenimiento
├── storage/                 # Backups y datos generados
├── uploads/                 # Archivos subidos por usuarios
├── requirements.txt         # Dependencias de Python
├── run.py                   # Punto de entrada
└── .env                     # Variables de entorno (no subir a Git)
```

## Comandos Útiles

```bash
# Iniciar servidor
python run.py

# Backup de la base de datos
.\venv\Scripts\python.exe -m scripts.backup

# Restaurar backup
.\venv\Scripts\python.exe -m scripts.restore

# Verificar integridad
.\venv\Scripts\python.exe -m scripts.verify
```

## Seguridad

- Protección CSRF en todos los formularios (Flask-WTF)
- Contraseñas hasheadas con bcrypt
- Headers de seguridad configurados (CSP, X-Frame-Options, HSTS)
- Rate limiting en intentos de login (5 intentos / 15 min bloqueo)
- Sesiones con cookies HttpOnly y SameSite=Lax
- Rutas administrativas protegidas con `@login_required` y `@admin_required`
- Registro de auditoría de acciones sensibles


