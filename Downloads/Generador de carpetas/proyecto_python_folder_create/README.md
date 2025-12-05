# 🗂️ Compresor de Carpetas CT/INV

Aplicación desktop moderna para crear y comprimir estructuras de carpetas CT (Central de Transformación) con INV (Inversores) de forma rápida y eficiente.

## ✨ Características

### 🎨 Interfaz Moderna
- **Tema claro/oscuro** - Toggle en tiempo real con persistencia
- **Responsive design** - Se adapta a cualquier tamaño de ventana
- **Logo Cathaleia** - Imagen prominente de 150x150 px
- **Animaciones suaves** - Transiciones elegantes en botones

### 📁 Gestión de Carpetas
- ✅ Crear estructura CT/INV/String automáticamente
- ✅ Seleccionar carpeta destino personalizadamente
- ✅ Soporte para dispositivos PVPM y METREL
- ✅ Crear múltiples strings (1-100) en una operación

### 📦 Compresión
- ✅ Comprimir carpetas INV en archivos ZIP
- ✅ Progreso detallado en tiempo real
- ✅ Soporte para compresión DEFLATED
- ✅ Numeración automática de archivos duplicados

### 📊 Validación y Feedback
- ✅ Validación visual de campos (error highlighting en rojo)
- ✅ Progreso detallado mostrando nombre de carpeta y porcentaje
- ✅ Notificaciones sonoras al completar operaciones
- ✅ Mensajes de estado claros y descriptivos

### 📋 Historial y Configuración
- ✅ Historial de últimas 50 operaciones
- ✅ Visualización de últimas 5 en la UI (Ctrl+H para ver todas)
- ✅ Guardado automático en `config.json`
- ✅ Persistencia de tema, ruta destino e historial

### ⌨️ Accesibilidad
- ✅ Atajos de teclado:
  - `Ctrl+T` - Cambiar tema oscuro/claro
  - `Ctrl+H` - Ver historial completo

## 📋 Requisitos

- **Python 3.8+** (recomendado 3.14.0)
- **tkinter** - Incluido en Python
- **PIL/Pillow** - Para procesamiento de imágenes
- **winsound** - Notificaciones sonoras (solo Windows)

## 🚀 Instalación

### Desde el ejecutable (Recomendado)
```bash
# Descargar Compresor_CT_INV.exe desde dist/
./Compresor_CT_INV.exe
```

### Desde el código fuente
```bash
# Clonar repositorio
git clone https://github.com/Alejandro-846/Folder_Create.git
cd proyecto_python_folder_create

# Instalar dependencias
pip install pillow

# Ejecutar
python creador_carpetas.py
```

## 📖 Guía de Uso

### 1️⃣ Crear Carpetas
1. Haz clic en "Seleccionar carpeta" para elegir destino
2. Ingresa:
   - **Número CT**: Identificador de la Central (ej: 1, 10, 100)
   - **Número Inversor**: 1-50
   - **Cantidad de Strings**: 1-100
   - **Dispositivo**: PVPM o METREL
3. Haz clic en "✓ Crear carpetas"
4. Verás progreso en tiempo real
5. 🔔 Se reproducirá un sonido al completar

### 2️⃣ Comprimir Carpetas
1. Haz clic en "📦 Comprimir carpeta CT"
2. Selecciona la carpeta CT que deseas comprimir
3. Se crearán archivos ZIP para cada INV-*
4. El progreso se mostrará en detalle
5. 🔔 Sonido de finalización

### 3️⃣ Cambiar Tema
- Haz clic en "🌙 Oscuro" o "☀️ Claro"
- O presiona **Ctrl+T**
- El tema se guarda automáticamente

### 4️⃣ Ver Historial
- Haz clic en la sección "Historial" para ver las últimas 5
- Presiona **Ctrl+H** para ver el historial completo

## 📁 Estructura del Proyecto

```
proyecto_python_folder_create/
├── creador_carpetas.py          # Código principal
├── cathaleia.png                # Logo (150x150 px)
├── cathaleia.svg                # Logo vector
├── config.json                  # Configuración guardada
├── dist/
│   └── Compresor_CT_INV.exe    # Ejecutable compilado
├── build/                       # Archivos de compilación
└── README.md                    # Este archivo
```

## 🎯 Estructura de Carpetas Generadas

```
CT-1/
├── INV-1-PVPM/
│   ├── String-1/
│   ├── String-2/
│   └── ...
├── INV-2-PVPM/
│   └── String-*/
└── INV-*.zip (después de comprimir)
```

## 🔧 Configuración

La aplicación guarda automáticamente en `config.json`:

```json
{
  "theme": "dark",
  "last_path": "C:\\Users\\usuario\\carpeta",
  "history": [
    {
      "timestamp": "2025-11-19 10:30:45",
      "tipo": "CREATE",
      "descripcion": "CT-1 (50 strings)",
      "estado": "ÉXITO"
    }
  ]
}
```

## 🐛 Solución de Problemas

### La aplicación no inicia
- Verifica que tengas Python 3.8+ instalado
- Instala dependencias: `pip install pillow`
- En Linux/Mac, instala tkinter: `sudo apt install python3-tk`

### La imagen de Cathaleia no aparece
- Asegúrate de que `cathaleia.png` esté en la misma carpeta que `creador_carpetas.py`
- Reconstruye el .exe: `pyinstaller --add-data "cathaleia.png:."`

### No hay sonido en las notificaciones
- En Windows, asegúrate que el volumen no esté silenciado
- En Linux/Mac, la función de sonido no está disponible (solo muestra mensajes)

### Los temas no se guardan
- Verifica permisos de escritura en la carpeta del programa
- Revisa que `config.json` se pueda crear

## 🛠️ Compilación del Ejecutable

```bash
# Instalar PyInstaller
pip install pyinstaller

# Compilar
pyinstaller --clean --onefile --windowed \
  --add-data "cathaleia.png:." \
  --name "Compresor_CT_INV" \
  creador_carpetas.py

# El .exe estará en dist/
```

## 📊 Validaciones

- **Número CT**: Cualquier valor (sin límite)
- **Número Inversor**: 1-50
- **Cantidad de Strings**: 1-100
- **Dispositivo**: PVPM o METREL
- Los campos inválidos se muestran en **rojo**

## 🎨 Temas Disponibles

### Tema Oscuro (Predeterminado)
- Fondo: #0f1419
- Acento: #9b6dd1 (Púrpura)
- Texto: #ffffff

### Tema Claro
- Fondo: #f5f5f5
- Acento: #8b5fbf (Púrpura oscuro)
- Texto: #1a1a1a

## 📈 Historial de Cambios

### v2.0.0 - Mejoras Completas (19/11/2025)
- ✨ Temas claro/oscuro con toggle
- 🔴 Validación visual mejorada
- 📊 Progreso detallado
- 📋 Historial de operaciones
- 🔔 Notificaciones sonoras
- 💾 Persistencia de configuración
- ⌨️ Atajos de teclado
- 🎨 Interface responsiva

### v1.0.0 - Versión Inicial
- Crear carpetas CT/INV/String
- Comprimir en ZIP

## 👨‍💻 Desarrollo

Creado por **Alejandro-846** para optimizar la gestión de estructuras de carpetas en sistemas de energía renovable.

## 📄 Licencia

Este proyecto está disponible bajo licencia MIT. Ver LICENSE para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 💡 Ideas Futuras

- [ ] Exportar/Importar configuraciones
- [ ] Drag & drop para seleccionar carpetas
- [ ] Búsqueda avanzada en historial
- [ ] Estadísticas de uso
- [ ] Soporte multi-idioma
- [ ] Copiar rutas al portapapeles
- [ ] Integración con OneDrive/Google Drive
- [ ] Plantillas personalizadas de carpetas

## 📞 Soporte

¿Encontraste un bug? ¿Tienes una sugerencia?
- Abre un Issue en GitHub
- Contacta a través del repositorio

## 🙏 Agradecimientos

- **Cathaleia** - Por el logo y diseño de referencia
- **Python tkinter** - Framework GUI
- **PIL/Pillow** - Procesamiento de imágenes
- **PyInstaller** - Compilación a ejecutable

---

**Hecho con ❤️ por Alejandro-846**

⭐ Si te fue útil, considera dejar una estrella en GitHub!
