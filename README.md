# Squirrels
Software for a Squirrel Squirter
Devin, there are two files here: a simple web page in HTML without any CSS, and a micropython file to control the RPi picoWH.
The run file can look for a json dictionary to get the wifi credentials.
Then it logs into your router, gets an address and presents the web page at the address, pulses the squirter for N seconds and then goes to sleep waiting for an input and checking for one every 5 seconds.  If there is a request wash rinse repeat.
I basically stole this from Ruiz Santos at RandomNerds, which is OK since I sent him some software he adapted and put up on his website.
