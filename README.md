# Axie Lens - Despliegue en Hugging Spaces

## 🚀 Despliegue Rápido

### Requisitos Previos

1. Cuenta en [Hugging Face](https://huggingface.co/)
2. Repositorio Git con el código
3. API Key de [Sky Mavis](https://developers.skymavis.com/)

### Pasos para Desplegar

1. **Sube tu código a GitHub/GitLab**

2. **Crea un nuevo Space en Hugging Face**
   - Ve a https://huggingface.co/spaces/new
   - Selecciona "Create a new Space"
   - Elige "Docker" como SDK
   - Configura el nombre y visibilidad

3. **Configura las Variables de Entorno**
   - En la configuración del Space, añade los secrets:
     - `SKYMAVIS_API_KEY`: Tu API key de Sky Mavis
     - `TELEGRAM_TOKEN`: (Opcional) Token de tu bot de Telegram
     - `TELEGRAM_CHAT_ID`: (Opcional) ID de chat autorizado

4. **Despliegue Automático**
   - Cada push a main activará un nuevo build
   - El contenedor se construirá automáticamente

### Archivos de Configuración

| Archivo | Descripción |
|---------|-------------|
| `Dockerfile` | Imagen Docker de la aplicación |
| `app.yaml` | Configuración de Hugging Spaces |
| `requirements.txt` | Dependencias Python |
| `.env.example` | Plantilla de variables de entorno |

### Puerto y URL

- **Puerto**: 5000
- **URL**: `https://tu-usuario-axielens.hf.space`

### Limitaciones en Hugging Spaces

⚠️ **Nota Importante**: Algunas funcionalidades no están disponibles en el entorno de Hugging Spaces:

- ❌ Bot de Telegram (requiere polling largo)
- ❌ Menú de consola interactivo
- ✅ Servidor web (disponible)
- ✅ API de Axies (funcional)

### Uso en Producción

La aplicación en Hugging Spaces funcionará como una **API web**:
- Interfaz web disponible en la URL del Space
- Endpoints Flask sirviendo templates HTML
- Consultas a la API de Sky Mavis

### Desarrollo Local

```bash
# Con Docker
docker build -t axielens .
docker run -p 5000:5000 -e SKYMAVIS_API_KEY=tu_key axielens

# Sin Docker (requiere Node.js)
pip install -r requirements.txt
python -c "from interfaces.server import run_server; run_server()"
```

### Estructura del Proyecto

```
AxieLens/
├── app.py                    # Orquestador principal
├── Dockerfile                # Imagen Docker
├── app.yaml                 # Configuración Hugging Spaces
├── requirements.txt         # Dependencias Python
├── .env.example            # Variables de entorno
├── core/                    # Lógica de negocio
│   ├── endpoint.js         # API Sky Mavis (Node.js)
│   ├── endpoint.py        # Wrapper Python
│   ├── logic.py           # Capa de lógica
│   └── utils.py           # Utilidades
├── interfaces/             # Interfaces de usuario
│   ├── server.py          # Servidor web Flask
│   ├── bot.py            # Bot Telegram
│   └── menu.py           # Menú consola
└── templates/             # Plantillas HTML
```

### Solución de Problemas

**Error: SKYMAVIS_API_KEY no configurada**
- Añade la variable en la configuración del Space

**Error: Puerto en uso**
- Hugging Spaces usa el puerto 5000 por defecto

**Build falla**
- Verifica que Node.js esté disponible en el Dockerfile
- Revisa los logs en la pestaña "Logs" del Space
