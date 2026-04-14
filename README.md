# Sistema de Diagnóstico de Repositorios en GitHub (ISSBC)

**Autor:** [Elías Martínez López]  
**Asignatura:** Ingeniería de Sistemas Basados en Conocimiento (ISSBC) - Universidad de Córdoba  

---

## 1. Descripción del Dominio
Este proyecto se enmarca en el ámbito de la ingeniería de software, centrándose específicamente en la plataforma de control de versiones GitHub. El objetivo principal de la herramienta es ejecutar tareas de diagnóstico relativas al estado y la viabilidad de los repositorios de código, identificando deficiencias de gestión, niveles de actividad y dinámicas de colaboración comunitaria.

Para llevar a cabo dicho análisis, el sistema plantea la integración de dos aproximaciones metodológicas:
* **CommonKADS:** Evaluación basada en la aplicación de reglas lógicas sobre métricas cuantitativas concretas (por ejemplo, días transcurridos desde la última confirmación de código o carencia de documentación técnica).
* **Ollama (MLL):** Inferencia cualitativa simulada mediante Modelos de Lenguaje, orientada a la detección de problemáticas de interacción humana que las métricas estructuradas convencionales no logran identificar (por ejemplo, toxicidad en la comunidad o falta de cohesión en el equipo de desarrollo).

---

## 2. Arquitectura del Proyecto (MVC)
El desarrollo de la aplicación cumple estrictamente con el patrón de diseño arquitectónico Modelo-Vista-Controlador (MVC), asegurando una alta cohesión y un bajo acoplamiento. La estructura organizativa del código fuente es la siguiente:

    /proyecto_diagnostico/
    ├── main.py                   # Punto de entrada principal de la aplicación.
    ├── README.md                 # Documentación del proyecto.
    ├── modelo/
    │   ├── __init__.py
    │   └── model.py              # Definición del estado, observables y estructuras de datos.
    ├── controlador/
    │   ├── __init__.py
    │   └── controller.py         # Lógica de negocio y simulación de inferencia del modelo.
    └── vista/
        ├── __init__.py
        ├── view.py               # Interfaz gráfica desarrollada en PyQt5.
        └── github_logo.png       # Recursos gráficos de la interfaz.

---

## 3. Características Principales de la Interfaz Gráfica (GUI)
* **Panel de Control Central:** Interfaz de entrada para registrar la URL del repositorio a analizar y los síntomas observados, categorizados en parámetros cuantitativos y cualitativos.
* **Gestión de Base de Conocimiento Local:** Módulo integrado para la importación y eliminación de documentos (archivos PDF) que alimentan el contexto del motor de inferencia.
* **Configuración del Motor de Inferencia:** Selector que permite al usuario determinar si el análisis debe restringirse al conocimiento local proporcionado o extenderse a fuentes de conocimiento externas (web).
* **Presentación Estructurada de Resultados:** Cuadros de diálogo dedicados para la exposición jerárquica de Hipótesis (tablas de probabilidad y estado) y la presentación del Diagnóstico final (incluyendo justificación explícita del razonamiento seguido por el LLM).
* **Accesibilidad Visual:** Implementación de un modo oscuro y claro dinámico, optimizado para garantizar el contraste y la legibilidad de todos los elementos interactivos.

---

## 4. Instrucciones de Ejecución

### 4.1. Requisitos Previos
Es indispensable disponer de un entorno con Python 3.x instalado en el sistema. Asimismo, el proyecto requiere la biblioteca gráfica `PyQt5`.

### 4.2. Instalación de Dependencias
Abra una sesión de terminal en el directorio raíz del proyecto y ejecute el siguiente comando para instalar automáticamente todas las librerías necesarias:

    pip install -r requirements.txt

*(Nota para sistemas basados en Debian/Ubuntu: Por normativas de seguridad del sistema operativo, se recomienda operar dentro de un entorno virtual).*

### 4.3. Inicio de la Aplicación
Para iniciar el sistema de diagnóstico, asegúrese de estar situado en el directorio raíz (donde se ubica el archivo `main.py`) e introduzca el siguiente comando:

    python main.py

*(Dependiendo de la configuración de las variables de entorno, el comando requerido puede ser `python3 main.py`).*