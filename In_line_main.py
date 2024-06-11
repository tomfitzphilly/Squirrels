# Complete project details at https://RandomNerdTutorials.com/raspberry-pi-pico-web-server-micropython/

# Import necessary modules to control the microcontroller
import network
import socket
import time
import random
from machine import Pin

# Create an pin object on pin '9' to control the squirter pump
sq = Pin(9, Pin.OUT)

# Wi-Fi credentials using mine from work.
ssid = '********'
password = '*******'

# HTML template for the webpage - this is pretty basic and is formatted using f-strings
def webpage(state):  #State is used to 
    html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Squirrel Squirter #1</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
        </head>
        <body>
            <h1>Squirt the Squirrel</h1>
            <h2>Squirt Control</h2>
            <form action="./squirt">
                <input type="submit" value="SQUIRT" />
            </form>
            <br>
            <p>Squirt state: {state}</p>
        </body>
        </html>
        """
    return str(html)

# Connect to WLAN. set up an IP address 
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Wait for Wi-Fi connection
connection_timeout = 10
while connection_timeout > 0:
    if wlan.status() >= 3:
        break
    connection_timeout -= 1
    print('Waiting for Wi-Fi connection...')
    time.sleep(1)

# Check if connection is successful
if wlan.status() != 3:
    raise RuntimeError('Failed to establish a network connection')
else:
    print('Connection successful!')
    network_info = wlan.ifconfig()
    print('IP address:', network_info[0])

# Set up socket and start listening.  I don't really understand this 
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen()

print('Listening on', addr)

# Initialize and set up initial variables
state = "OFF"
random_value = 0

# Main loop to listen for connections
while True:
    try:
        conn, addr = s.accept()
        print('Got a connection from', addr)
        
        # Receive and parse the request
        request = conn.recv(1024)
        request = str(request)
#         print('Request content = %s' % request)

        try:
            request = request.split()[1]
            print('Request:', request)
        except IndexError:
            pass
        
        # Process the request and update variables
        if request == '/squirt?':
            print("squirting!!!")
            sq.value(1)
            state = "ON"
            time.sleep(2)
            sq.value(0)
            state = "OFF"
            response = webpage(state)
            conn.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
            conn.send(response)
            conn.close()

    except OSError as e:
        conn.close()
        print('Connection closed')
