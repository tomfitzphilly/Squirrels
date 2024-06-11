# Import necessary modules
import network
import asyncio
#from config import wifi_ssid, wifi_password
import socket
import time
import json
from machine import Pin
adc = machine.ADC(4)
global ssid
global password
# Constant variable to save the HTML file path
HTML_FILE_PATH = "web_page.html"

# Create several LEDs
led_blink = Pin(8, Pin.OUT)
squirt_control = Pin(28, Pin.OUT)
onboard_led = Pin('LED', Pin.OUT)

# Initialize squirt state
state = 'OFF'

# Function to read HTML content from the file
def read_html_file():
    with open(HTML_FILE_PATH, "r") as file:
        return file.read()

# Get sensor readings
def get_readings():
    ADC_voltage = adc.read_u16() * (3.3 / (65536))
    tempC = 27 - (ADC_voltage - 0.706)/0.001721
    tempF=32+(1.8*tempC)
    print("Sensor Voltage", ADC_voltage)
    print("Temperature C:",tempC)
    print("Temperature Fahrenheit",tempF)
    return ADC_voltage, tempC, tempF

# HTML template for the webpage
def webpage(state):
    # Get new sensor readings every time you serve the web page
    ADC_voltage, tempC, tempF = get_readings()
    html_content = read_html_file()
    html = html_content.format(state=state, ADC_voltage=ADC_voltage, tempC=tempC, tempF=tempF)
    print(webpage)
    return html


# Init Wi-Fi Interface
def init_wifi_from_file(file_path="wifi_credentials.json"):
    try:
        with open(file_path, 'r') as file:
            credentials = json.load(file)
            print("JSON file loaded")
    except OSError:
        print(f"Error: unable to read {file_path}.")
        return False
    for cred in credentials:
        ssid = cred.get('ssid')
        password = cred.get('password')
        if ssid and password:
            if init_wifi(ssid,password):
                return True        
    print ("Unable to connect!")
    return False

# Init WiFi interface
def init_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.disconnect()
    print(f"Trying to connect to {ssid}")
    wlan.connect(ssid,password)
    
    connection_timeout = 10
    while connection_timeout>0:
        if wlan.isconnected():
            print("Connected!")
            network_info=wlan.ifconfig()
            print("IP Address is: ",network_info[0])
            return True
        connection_timeout -=1
        print("trying to connect...")
        time.sleep(1)
    print("Connection failed!")
    return False

# Asynchronous functio to handle client's requests
async def handle_client(reader, writer):
    global state
    global ADC_voltage
    global tempC
    global tempF
    
    print("Client connected")
    request_line = await reader.readline()
    print('Request:', request_line)
    
    # Skip HTTP request headers
    while await reader.readline() != b"\r\n":
        pass
    
    request = str(request_line, 'utf-8').split()[1]
    print('Request:', request)
    
    # Process the request and update variables
    N=1
    if request == '/squirt?':
        print('Squirting')
        squirt_control.value(1)
        state = 'ON'
        response = webpage(state)
        time.sleep(N)
        squirt_control.value(0)
        print("Squirting Stopped")
        state = 'OFF'
    if request == '/?':
        get_readings()
        response = webpage(state)

    
    # Generate HTML response
    response = webpage(state)  

    # Send the HTTP response and close the connection
    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    writer.write(response)
    await writer.drain()
    await writer.wait_closed()
    print('Client Disconnected')
    
async def blink_led():
    while True:
        led_blink.toggle()  # Toggle LED state
        await asyncio.sleep(0.5)  # Blink interval

async def main():
    init_wifi_from_file()
#     if not init_wifi(ssid, password):
#         print('Exiting program.')
#         return
#     
    # Start the server and run the event loop
    print('Setting up server')
    wlan = network.WLAN(network.STA_IF)
    network_info=wlan.ifconfig()
    print("IP Address is: ",network_info[0])
    server = asyncio.start_server(handle_client, "0.0.0.0", 80)
    asyncio.create_task(server)
    asyncio.create_task(blink_led())
    print('DONE!')
    
    while True:
        #print('Loop')
        # Add other tasks that you might need to do in the loop
        await asyncio.sleep(5)
        onboard_led.toggle()
        
# Create an Event Loop
loop = asyncio.get_event_loop()
# Create a task to run the main function
loop.create_task(main())

try:
    # Run the event loop indefinitely
    loop.run_forever()
except Exception as e:
    print('Error occured: ', e)
except KeyboardInterrupt:
    print('Program Interrupted by the user')
