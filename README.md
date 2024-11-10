# Space-Invaders
hardware requirements
-2 PASSIVE buzzers
-RPI
-1 breadboard
-1 button
-1 10k resistor, 4 220 resisters
-1 mpu6050
-4 leds
-jumper wires


connect what to which GPIO
pin 1 (3.3V)

->mpu6050 VCC
->button

pin 3 (GPIO 2)
->mpu6050 SDA
pin 5 (GPIO3)
->mpu6050 SCL
pin 0 (GND)
-> 1 10k resistor ->button
->mpu6050 GND
-> 4 220 resistor -> 4 LEDs
-> 2 buzzers 
pin (GPIO 18)
->button
pin 11,13,15,29(GPIO 17,27,22,5)
->4 LEDs
pin 31,33 (GPIO 6,13)
->2 passive buzzers

