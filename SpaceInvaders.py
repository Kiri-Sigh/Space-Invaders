import RPi.GPIO as GPIO
import smbus
import time
from random import randint
import pygame
import math

# Setup for GPIO and MPU6050
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# MPU6050 setup
MPU6050_ADDR = 0x68
GYRO_XOUT_H = 0x43


# GPIO pin setup for buttons=
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Normal Bullet Button
#GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Special Bullet Button

# GPIO setup for LEDs
LED_PINS = [17, 27, 22, 5]  # 4 LEDs connected to GPIO 17, 27, 22, 5
for pin in LED_PINS:
    GPIO.setup(pin, GPIO.OUT)

# GPIO setup for passive buzzers with PWM
BUZZER_PINS = [6, 13]  # 2 passive buzzers connected to GPIO 6 and 13
buzzers = []
for pin in BUZZER_PINS:
    GPIO.setup(pin, GPIO.OUT)
    buzzers.append(GPIO.PWM(pin, 1000))  # Initialize PWM with a f of 1000

def activate_buzzer(i, duration=0.1, frequency=1000):
    buzzers[i].ChangeFrequency(frequency)
    buzzers[i].start(50) 
    time.sleep(duration)
    buzzers[i].stop()

# Initialize MPU6050
bus = smbus.SMBus(1)
bus.write_byte_data(MPU6050_ADDR, 0x6B, 0)

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 650, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invader")
clock = pygame.time.Clock()

# variables
player_x = WIDTH // 2
player_y = HEIGHT - 50
player_speed = 8
bullets = []
#special_bullets = []
enemies = [{"x": randint(0, WIDTH - 40), "y": 20, "color": (255, 0, 0)} for _ in range(5)]  # Red enemies
#yellow_enemy = {"x": randint(0, WIDTH - 40), "y": 20, "color": (255, 255, 0)}  # Yellow enemy
enemy_speed = 1
bullet_speed = 7
#special_bullet_speed = 7
gyro_threshold = 3000
#special_bullet_ready = False  

# Calibration offsets
gyro_x_offset = 0

def read_gyro():
    # Read the raw data 
    high_x = bus.read_byte_data(MPU6050_ADDR, GYRO_XOUT_H)
    low_x = bus.read_byte_data(MPU6050_ADDR, GYRO_XOUT_H + 1)

    # Combine the high and low bytes
    x = (high_x << 8) | low_x

    # Convert to signed 16-bit values
    if x > 32767:
        x -= 65536

    return x


def calibrate_gyro():
    global gyro_x_offset
    sum_x = 0
    num_samples = 100

    for _ in range(num_samples):
        x = read_gyro()
        sum_x += x
        time.sleep(0.01)

    gyro_x_offset = sum_x // num_samples

#x axis movement of player
def move_player():
    global player_x
    gyro_x = read_gyro()

    # Apply calibration offset
    gyro_x -= gyro_x_offset

    if gyro_x > gyro_threshold:
        player_x += player_speed * 2
    elif gyro_x < -gyro_threshold:
        player_x -= player_speed * 2
    player_x = max(0, min(WIDTH - 40, player_x))  # Boundary check

def fire_bullet():
    bullets.append({"x": player_x + 15, "y": player_y})
    activate_buzzer(0)  # Play sound on the first buzzer

#def fire_special_bullets():
    #special_bullets.append({"x": player_x + 15, "y": player_y, "angle": 0})
    #special_bullets.append({"x": player_x + 15, "y": player_y, "angle": -30})
    #special_bullets.append({"x": player_x + 15, "y": player_y, "angle": 30})
    #activate_buzzer(1)

#move up bullets
def move_bullets():
    global bullets, special_bullets
    for bullet in bullets:
        bullet["y"] -= bullet_speed
    bullets = [b for b in bullets if b["y"] > 0]

    #for bullet in special_bullets:
        #bullet["y"] -= special_bullet_speed * math.cos(math.radians(bullet["angle"]))
        #bullet["x"] += special_bullet_speed * math.sin(math.radians(bullet["angle"]))
    #special_bullets = [b for b in special_bullets if 0 <= b["x"] <= WIDTH and b["y"] > 0]

#move down enemies
def move_enemies():
    for enemy in enemies:
        enemy["y"] += enemy_speed
        if enemy["y"] > HEIGHT:
            enemy["x"] = randint(0, WIDTH - 40)
            enemy["y"] = 20

    #yellow_enemy["y"] += enemy_speed
    #if yellow_enemy["y"] > HEIGHT:
        #yellow_enemy["x"] = randint(0, WIDTH - 40)
        #yellow_enemy["y"] = 20

#check if bullet hit enemy
def check_collision():
    #global special_bullet_ready
    for enemy in enemies[:]:
        for bullet in bullets:
            if abs(bullet["x"] - enemy["x"]) < 20 and abs(bullet["y"] - enemy["y"]) < 20:
                enemies.remove(enemy)
                bullets.remove(bullet)
                activate_buzzer(1,0.1,2000)
                for pin in LED_PINS:
                    GPIO.output(pin, GPIO.HIGH)

                time.sleep(0.5)
                for pin in LED_PINS:
                    GPIO.output(pin, GPIO.LOW)

        #for bullet in bullets:
            #if abs(bullet["x"] - yellow_enemy["x"]) < 20 and abs(bullet["y"] - yellow_enemy["y"]) < 20:
                #special_bullet_ready = True
                #bullets.remove(bullet)
                #yellow_enemy.clear()
                
                #activate_buzzer(1)
                #for pin in LED_PINS:
                    #GPIO.output(pin, GPIO.HIGH)
                #time.sleep(0.1)
                #for pin in LED_PINS:
                    #GPIO.output(pin, GPIO.LOW)

# Main loop
def game_loop():
    global player_x, player_y
    calibrate_gyro()

    running = True
    while running:
        screen.fill((0, 0, 0))  # Clear screen
        move_player() 
        move_bullets()
        move_enemies()
        check_collision()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Check button inputs for firing
        if GPIO.input(18) == GPIO.HIGH:  # Normal Bullet
            fire_bullet()
            time.sleep(0.2)  # delay

        #if GPIO.input(25) == GPIO.HIGH:  # Special Bullet
            #fire_special_bullets()
            #special_bullet_ready = True
            #time.sleep(0.2)  

        # Drawing enemies
        pygame.draw.rect(screen, (0, 0, 255), (player_x, player_y, 40, 20))  # Player
        for bullet in bullets:
            pygame.draw.rect(screen, (255, 255, 0), (bullet["x"], bullet["y"], 5, 10))  # Regular Bullets
        #for bullet in special_bullets:
            #pygame.draw.circle(screen, (0, 255, 0), (int(bullet["x"]), int(bullet["y"])), 5)  # Special Bullets
        for enemy in enemies:
            pygame.draw.rect(screen, enemy["color"], (enemy["x"], enemy["y"], 40, 20))  # Enemies
        #pygame.draw.rect(screen, yellow_enemy["color"], (yellow_enemy["x"], yellow_enemy["y"], 40, 20))  # Yellow Enemy

        pygame.display.flip()
        clock.tick(30)

# Run the game loop
game_loop()

# Clean up GPIO
GPIO.cleanup()
