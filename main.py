from mqtt_as import MQTTClient
from mqtt_local import config
import uasyncio as asyncio
import dht, machine
from settings import SSID, PASS, BROKER, USR_MQTT, PASS_MQTT, PORT
import json
import btree

ID_DEVICE = "mdr"

# Configuracion pines
DHT_PIN = 25
RELAY_PIN = 14
LED_PIN = 2

# Configuracion dispositivos
d = dht.DHT22(machine.Pin(DHT_PIN))
r = machine.Pin(RELAY_PIN, machine.Pin.OUT)
led = machine.Pin(LED_PIN, machine.Pin.OUT)

# Configuracion local
config['server'] = BROKER
#config['port'] = 1883 # utilizara cuando config['ssl'] = False
config['ssid'] = SSID
config['wifi_pw'] = PASS

config['port'] = PORT
config['user'] = USR_MQTT
config['password'] = PASS_MQTT

# Función para verificar la existencia de la base de datos y cargar los valores si existe
def load_params_from_db():
    
    try:
        f = open("mydb", "r+b")
    except OSError:
        f = open("mydb", "w+b")

    try:
        db = btree.open(f)
        global setpoint, periodo, modo, rele
        setpoint = int(db.get(b'setpoint', b'30'))
        periodo = int(db.get(b'periodo', b'30'))
        modo = db.get(b'modo', b'automatico').decode()
        rele = int(db.get(b'rele', b'0').decode())
        db.close()
    except OSError as e:
        print("Error al cargar los parámetros desde la base de datos")

def control_relay():
    global temperatura, setpoint
        
    if modo == 'automatico':
        r.value(temperatura > setpoint)
    elif modo == 'manual':
        r.value(rele)

def sub_cb(topic, msg, retained):
    global setpoint, periodo, modo, rele

    print('Topic = {} -> Valor = {}'.format(topic.decode(), msg.decode()))

    topic = topic.decode().split('/')[2]

    value = json.loads(msg.decode())[topic]

    if topic != 'destello':
        update_btree(topic, value)

    if topic == "setpoint":
        setpoint = value
        control_relay()

    elif topic == "periodo":
        periodo = value
    
    elif topic == "destello":
        asyncio.create_task(flash_led())
    
    elif topic == "modo":
        modo = value
        control_relay()

    elif topic == "rele":
        rele = value
        control_relay()

async def wifi_han(state):
    print('Wifi is', 'UP' if state else 'DOWN')
    await asyncio.sleep(1)

# If you connect with clean_session True, must re-subscribe (MQTT spec 3.1.2.4)
async def conn_han(client):
    await client.subscribe(f"iot2024/{ID_DEVICE}/setpoint", 1)
    await client.subscribe(f"iot2024/{ID_DEVICE}/periodo", 1)
    await client.subscribe(f"iot2024/{ID_DEVICE}/modo", 1)
    await client.subscribe(f"iot2024/{ID_DEVICE}/rele", 1)
    await client.subscribe(f"iot2024/{ID_DEVICE}/destello", 1)

# Función para manejar el destello del LED
async def flash_led():
    for _ in range(10):
        led.value(1)
        await asyncio.sleep(0.25)
        led.value(0)
        await asyncio.sleep(0.25)

# Función para actualizar los parámetros almacenados en la base de datos BTree
def update_btree(topic, value):

    f = open("mydb", "r+b")

    #Abrir base de datos
    db = btree.open(f)
    print("Actualizando base de datos")
    dato = db[b"{}".format(topic)] = b"{}".format(value)
    #print("dato ", dato) #Debug

    db.flush()
    db.close()
    f.close()

async def main(client):
    global temperatura
    
    await client.connect()
    await asyncio.sleep(5)  # Give broker time
    
    while True:
        try:
            d.measure()

            try:
                temperatura = d.temperature()
            except OSError as e:
                print("Sin sensor de temperatura")
            
            try:
                humedad = d.humidity()
            except OSError as e:
                print("Sin sensor de humedad")
            
            data = {
                "temperatura": temperatura,
                "humedad": humedad,
                "setpoint": setpoint,
                "periodo": periodo,
                "modo": modo
            }

            # Convertir el diccionario a JSON
            json_data = json.dumps(data)

            # Publicar el JSON en un solo mensaje
            await client.publish(f'iot2024/{ID_DEVICE}/', json_data, qos=0)

            control_relay()

        except OSError as e:
            print("Error al publicar")

        await asyncio.sleep(periodo)  # Broker is slow

# Define configuration
config['subs_cb'] = sub_cb
config['connect_coro'] = conn_han
config['wifi_coro'] = wifi_han
config['ssl'] = True

# Verificar y cargar parámetros de la base de datos
load_params_from_db()

# Set up client MQTT
MQTTClient.DEBUG = True  # Optional
client = MQTTClient(config)

try:
    asyncio.run(main(client))
finally:
    client.close()
    asyncio.new_event_loop()