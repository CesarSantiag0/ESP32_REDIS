from machine import Pin
import network
import time
import urequests
import dht

# Conexión a la red Wi-Fi
ssid = "Chilaquil_2349_2.4Gnormal"
password = "Chilaquil183818"
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)
while not station.isconnected():
    pass
print("Conexión a la red Wi-Fi establecida")

# Configuración del sensor PIR
pir_sensor = Pin(35, Pin.IN)  # Usa el pin que hayas configurado para el PIR

# Configuración del sensor DHT11
dht_sensor = dht.DHT11(Pin(4))

# Define el pin de la alarma
alarm_pin = Pin(2, Pin.OUT)  # Usa el pin que hayas configurado para la alarma

# Función para enviar datos (temperatura, humedad y detección de movimiento) a la API Flask
def update_sensor_data(temperature, humidity, motion_detected):
    server_url = "http://192.168.100.155:5001/api/plantitas/update_humidity_temperature"  # Reemplaza con tu dirección IP
    data = {
        "temperatura": temperature,
        "humedad": humidity,
        "motion_detected": motion_detected,
    }
    try:
        response = urequests.patch(server_url, json=data)
        response.close()
        return response.status_code
    except Exception as e:
        print('Error al actualizar los datos en la API Flask:', e)
        return None

# Función para obtener el estado de la alarma desde la API Flask
def get_alarm_status():
    server_url = "http://192.168.100.155:5001/api/alarma"  # Reemplaza con tu dirección IP
    try:
        response = urequests.get(server_url)
        data = response.json()
        response.close()
        return data.get("estado_alarma", 0)
    except Exception as e:
        print('Error al obtener el estado de la alarma:', e)
        return 0

print("Leyendo valores del sensor PIR, DHT11 y controlando la alarma...")
while True:
    try:
        # Leer valores de temperatura y humedad del sensor DHT11
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        print('Temperatura:', temperature, '°C')
        print('Humedad:', humidity, '%')
        
        # Leer el estado del sensor PIR
        motion_detected = pir_sensor.value()
        print('Movimiento detectado:', motion_detected)

        # Enviar los datos a la API Flask
        status_code = update_sensor_data(temperature, humidity, motion_detected)
        if status_code is not None:
            if status_code == 200:
                print('Datos actualizados correctamente en la API Flask.')
            else:
                print('Error al actualizar los datos. Código de estado:', status_code)

        # Obtener el estado de la alarma desde la API Flask
        alarm_status = get_alarm_status()
        print('Estado de la alarma:', alarm_status)

        # Controlar la alarma según el estado del sensor PIR
        if motion_detected == 1:
            alarm_pin.on()  # Encender la alarma
            print('Movimiento detectado. Alarma encendida.')
        else:
            alarm_pin.off()  # Apagar la alarma
            print('No hay movimiento. Alarma apagada.')

        time.sleep(10)
    except Exception as e:
        print('Error en el bucle principal:', e)

