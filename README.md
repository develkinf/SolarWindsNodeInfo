# Bot de Telegram para Obtener Información de SolarWinds

Este bot de Telegram permite obtener información sobre el TOP 5 de uso de CPU y memoria de los nodos de SolarWinds y generar gráficas con los datos obtenidos.

## Características
- Consulta información de nodos en SolarWinds.
- Obtiene el top 5 de nodos con mayor uso de CPU o memoria.
- Genera gráficos de barras con los datos.
- Interfaz conversacional en Telegram.

## Requisitos
- Python 3.8+
- Un bot de Telegram registrado con un token válido.
- Credenciales de acceso a SolarWinds.
- Dependencias de Python:
  ```sh
  pip install matplotlib python-telegram-bot requests
  ```

## Configuración
### Variables de Entorno
Define las siguientes variables de entorno:
```sh
export DASH_USERNAME="tu_usuario"
export DASH_PASSWORD="tu_contraseña"
```

### Token del Bot de Telegram
Reemplaza `YOURTOKEN` en el archivo principal por el token de tu bot de Telegram.

## Uso
1. Inicia el bot en Telegram con el comando `/start`.
2. Selecciona "CPU" o "Memoria" para ver los datos.
3. El bot responderá con un gráfico mostrando el top 5 de nodos con mayor uso.
4. Puedes cancelar la operación con `/cancel`.

## Ejecución
Para ejecutar el bot, usa:
```sh
python nombre_del_archivo.py
```

## Seguridad
- **No compartas tu token de Telegram ni credenciales de SolarWinds.**
- Usa un archivo `.env` para manejar variables de entorno de forma segura.

## Mejoras Futuras
- Soporte para más métricas.
- Integración con bases de datos para almacenamiento de históricos.
- Implementación con webhooks en lugar de polling para mayor eficiencia.

## Licencia
Este proyecto está bajo la licencia MIT.

