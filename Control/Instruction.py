"""
This file contains the class Board_Movement, which is used to control the movement of the robot arm.
"""
import math
import rtde_receive
import rtde_control
import keyboard


class Board_Movement:
    def __init__(self, origin, rotation_angle, velocity=0.05):
        self.position = origin  # array containing (x, y, z, rx, ry, rz),
        # with (x, y, z) being the origin and
        # and (rx, ry, rz) is a rotation vector describing orientation of tool head.

        self.origin = origin

        self.phi = rotation_angle  # rotation between native arm coordinate space to chess coordinate space
        self.velocity = velocity

        self.controller = rtde_control.RTDEControlInterface("192.168.2.81")
        self.receiver = rtde_receive.RTDEReceiveInterface("192.168.2.81")

        self.x_displacement = self.velocity * math.cos(self.phi)
        self.y_displacement = self.velocity * math.sin(self.phi)
        self.z_displacement = self.velocity

    board_map = {"H": 0, "G": 1, "F": 2, "E": 3, "D": 4, "C": 5, "B": 6, "A": 7}
    print(board_map)

    def move_to(self, boardPosition):
        # WIP
        row = self.board_map.get(boardPosition[0])
        col = 8 - int(boardPosition[1])
        print(f"row: {row}, column: {col}")

        self.position[0] = self.origin[0] - col * self.x_displacement
        self.controller.moveL(self.position)
        self.position[1] = self.origin[1] - row * self.y_displacement
        self.controller.moveL(self.position)

    def remote_move(self):
        print(self.position[0:3])

        if keyboard.is_pressed("a") or keyboard.is_pressed("d"):
            if keyboard.is_pressed("d"):
                self.position[0] += self.x_displacement
                self.position[1] += self.y_displacement
            else:
                self.position[0] -= self.x_displacement
                self.position[1] -= self.y_displacement
        elif keyboard.is_pressed("w") or keyboard.is_pressed("s"):
            if keyboard.is_pressed("s"):
                self.position[0] += self.x_displacement
                self.position[1] -= self.y_displacement
            else:
                self.position[0] -= self.x_displacement
                self.position[1] += self.y_displacement
        elif keyboard.is_pressed("up") or keyboard.is_pressed("down"):
            if keyboard.is_pressed("up"):
                self.position[2] += self.z_displacement
            else:
                self.position[2] -= self.z_displacement

        self.controller.moveL(self.position)


# origin
x = 0.54952
y = -0.38494
z = 0.15

rx = 0
ry = 135
rz = 0

chessbot = Board_Movement([x, y, z, rx, ry, rz], math.radians(45), 0.044)
chessbot.remote_move()

loc = input("chess move: ")
chessbot.move_to(loc)
