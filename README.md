# Ejercicio ESP32

## Correspondiente a la asignatura "IC511 Internet de las cosas, sensores y redes"

### Consigna:
    Crear un termostato con un esp32 que puede funcionar de modo manual o automático y que cumpla con las siguientes especificaciones:

    - Programado en micropython utilizando asyncio
    - Sensor dht22.
    - Se comunica mediante mqtts.
    - Publica periódicamente en el tópico "ID del dispositivo" los siguientes parámetros: temperatura, humedad, setpoint, periodo y modo.
    - Se envía en una sola publicación en un JSON
    - Se suscriba a setpoint, periodo, destello, modo y relé.
    - Almacenará de manera no volátil los parámetros de setpoint, periodo, modo y relé (ver btree).
    - Contará con relé que se accionará cuando se supere la temperatura de setpoint. (modo automático)
    - Si se encuentra en modo manual el relé se activará según la orden "relé" enviada por mqtt.
    - Destellará por unos segundos cuando reciba la orden "destello" por mqtt.
    - Cuando recibe un mensaje con nuevos parámetros deberá actualizar los almacenados y actuar si es necesario.
    - El código del programa deberá estar en un repositorio git cuya dirección debe figurar en la entrega del trabajo.

### Manejo de datos:
Los datos recibidos por el ESP32 estarán en formato JSON. Ejemplos:

**Asignar setpoint a 30:**

    - Tópico: iot2024/{ID_DEVICE}/setpoint
    - JSON: {"setpoint": 30} 

**Asignar periodo a 30:**

    - Tópico: iot2024/{ID_DEVICE}/periodo
    - JSON: {"periodo": 30}

**Encender rele:**

    - Tópico: iot2024/{ID_DEVICE}/rele
    - JSON: {"rele": 1}

**Apagar rele:**

    - Tópico: iot2024/{ID_DEVICE}/rele
    - JSON: {"rele": 0}

**Modo Manual**

    - Tópico: iot2024/{ID_DEVICE}/modo
    - JSON: {"modo": "manual"}

**Modo Automático**

    - Tópico: iot2024/{ID_DEVICE}/modo
    - JSON: {"modo": "automatico}
    
**Destello:**

    - Tópico: iot2024/{ID_DEVICE}/destello
    - JSON: {"destello": 1}

### Configuración:
Se realiza a través de `settings.py`. El mismo contiene:

    - SSID=''
    - PASS=''
    - BROKER='x.duckdns.org'
    - USR_MQTT=''
    - PASS_MQTT=''
    - PORT=''