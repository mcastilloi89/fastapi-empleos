# API Empleos

Proyecto desarrollado como parte del examen final del curso.  
La aplicación implementa una API REST con FastAPI y SQLite, que permite realizar operaciones CRUD (crear, leer, actualizar y eliminar) sobre ofertas de empleo.

---

# Requisitos previos

Antes de ejecutar el proyecto, asegúrate de tener instalado:

- **Python 3.11** o superior  
- **Github** (para clonar el repositorio)  

---

## Instrucciones de instalación

1. **Clonar el repositorio desde GitHub**

   ```bash
   git clone https://github.com/mcastilloi89/fastapi-empleos.git






III. PARTE TEÓRICA


1. ¿Para qué se puede usar Python en temas de datos?

Python se usa un montón cuando se trabaja con datos.
Algunos ejemplos claros:

Para analizar información, por ejemplo datos de ventas, encuestas o rendimiento de una empresa.

Para hacer gráficos o reportes y mostrar resultados de forma visual.

Para crear modelos de predicción, como estimar cuántos clientes se pueden perder o cuánto se va a vender.

Para automatizar tareas que antes se hacían a mano, como generar reportes o limpiar archivos.

Para conectarse a bases de datos, leer y modificar información directamente desde el código.

2. ¿Cómo se diferencian Flask de Django?

Flask es más simple y rápido de aprender.
Te da solo lo necesario para empezar y tú vas armando el resto.
Django en cambio ya viene con muchas cosas listas (login, base de datos, panel de administración).
En pocas palabras:

Flask es más libre y liviano.

Django es más completo y estructurado.

3. ¿Qué es un API?

Un API es básicamente una forma de conectar sistemas entre sí.
Por ejemplo, una app de celular puede pedirle datos a un servidor mediante una API.
Tú mandas una solicitud y el servidor responde con información, normalmente en formato JSON.
Es como un “puente” entre dos programas.

4. ¿Cuál es la diferencia entre REST y WebSockets?

REST funciona por peticiones.
El cliente pide algo y el servidor responde; si quieres más datos, tienes que volver a pedirlos.
En cambio, WebSockets mantiene la conexión abierta todo el tiempo, así el servidor puede enviar datos en vivo.
REST se usa para consultas normales, WebSockets para cosas en tiempo real (como chats o notificaciones).

5. Ejemplo de API comercial y cómo funciona

Un buen ejemplo es la API del clima de OpenWeather.
Le mandas una solicitud con el nombre de una ciudad, y te devuelve la temperatura, humedad, etc.
Por ejemplo, si mandas “Lima”, te responde con un JSON con el clima actual.
Así los desarrolladores pueden mostrar esa info en sus apps sin tener que medir el clima ellos mismos.