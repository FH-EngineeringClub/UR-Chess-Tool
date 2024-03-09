from time import sleep
import socket
import json
import math
import rtde_receive
import rtde_control

HOSTNAME = "192.168.2.81"  # IP address assigned to arm
HOST_PORT = 30002  # Port associated with IP

ANGLE = 44.785  # Angle measured between the y-axis in the TCP's coordinate space 
                # and the vector parallel to the side of the board (rad)

ORIGIN_X = 0.401  # x coordinate of the origin in the TCP's coordinate space (m)
ORIGIN_Y = -0.564 # y coordinate of the origin in the TCP's coordinate space (m)

TCP_RX = 1.393  # Rotation of TCP about its x axis (rad)
TCP_RY = -2.770  # Rotation of TCP about its y axis (rad) 
TCP_RZ = -0.085  # Rotation of TCP about its z axis (rad)

BOARD_HEIGHT = 0.014  # Height of the board relative to the base of the robot in the TCP's coordinate space (m)

REST_LOCATION = [-0.11676, -0.3524, 0.133]  # Position TCP comes to rest at (m)
DISPENSE_LOCATION = [.0087, -.6791]         # Position TCP will dispense pieces at (m)

class Board:
    def __init__(self, 
                 host_info = [HOSTNAME, HOST_PORT], 
                 origin = [ORIGIN_X, ORIGIN_Y], 
                 TCP_orientation = [TCP_RX, TCP_RY, TCP_RZ], 
                 rest_position = REST_LOCATION,
                 dispense_position = DISPENSE_LOCATION,
                 height = BOARD_HEIGHT, 
                 trns_angle = ANGLE):
        
        self.controller = rtde_control.RTDEControlInterface(host_info[0])       # Receiving TCP information
        self.receiver = rtde_receive.RTDEReceiveInterface(host_info[0])         # Controlling TCP
        self.origin = origin        # Origin of coordinate system
        self.trns_angle = trns_angle # Angle which coordinate system is 'rotated' by
        self.host_info = host_info  # Host name and port
        
        # TCP State Variables
        self.position = origin              # (m)
        self.velocity = 0.5                 # (m/s)
        self.acceleration = 0.3             # (m/s^2)
        self.orientation = TCP_orientation  # (rad)
        self.rest_position = rest_position  # (m)
        self.dispense_position = dispense_position # (m)
        self.isMagnetized = False

        # Board State Variables
        self.height = height                # (m)

        f = open("ur10 arm\setup.json", encoding="utf-8")  
        self.board_data = json.load(f)                     # Location of each chess square in board's coordinate space

        self.piece_heights = {                             # Heights of each piece (m)
            "king" : 0.0762,                                  
            "pawn" : 0.0356,                                  
            "rook" : 0.04,                                    
            "knight" : 0.0457,                                  
            "bishop" : 0.0559,                                  
            "queen" : 0.0686                                   
        }

        # Initialization
        self.controller.moveL(                                                            # Moves to board's origin.
            [self.origin[0], 
             self.origin[1], 
             self.height + 0.15,
             self.orientation[0],
             self.orientation[1],
             self.orientation[2]],
             0.5,
             0.3
        )
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host_info[0], self.host_info[1]))
        sock.send(bytes("sec myProg():\n\tset_tool_voltage(0)\nend\nmyProg()\n", "utf-8")) # Ensures magnet is off. 
        sock.close()
        sleep(0.2)
        
        
    def translate(self, pos):
        # Takes a position in the board's coordinate space, then translates
        # it into the arm's coordinate space.
        x_1 = pos[1] * math.cos(self.trns_angle) - pos[0] * math.sin(self.trns_angle)
        y_1 = pos[1] * math.sin(self.trns_angle) + pos[0] * math.cos(self.trns_angle)
        # we don't know why this works, very complex Nick Algebra

        return [x_1 + self.origin[0], y_1 + self.origin[1]]

    def move_to(self, square_name):
        # Takes a square name (e.g "a1", "g4"), then moves the TCP to hover 
        # over that square.
        new_pos = [self.board_data[square_name]["x"] / 1000, self.board_data[square_name]["y"] / 1000]
        
        self.robot_position = self.translate(new_pos)
        self.controller.moveL(
            [
                self.robot_position[0],
                self.robot_position[1],
                self.height + 0.15, 
                self.orientation[0],
                self.orientation[1],
                self.orientation[2]
            ],
            self.velocity,
            self.acceleration
        )

    def magnetize(self):
        # Turns the electromagnet off and on.
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host_info[0], self.host_info[1]))

        if not self.isMagnetized:
            command = "sec myProg():\n\tset_tool_voltage(24)\nend\nmyProg()\n"
            self.isMagnetized = True
        else:
            command = "sec myProg():\n\tset_tool_voltage(0)\nend\nmyProg()\n"
            self.isMagnetized = False
        
        sock.send(bytes(command, "utf-8"))
        sock.close()
        sleep(0.3)

    def connect(self, piece):
        # Lowers TCP to square space, turns magnet either off and on,
        # then raises back off.
        self.controller.moveL(
            [
                self.robot_position[0],
                self.robot_position[1],
                self.height + self.piece_heights[piece], 
                self.orientation[0],
                self.orientation[1],
                self.orientation[2],
            ],
            self.velocity,
            self.acceleration
        )

        self.magnetize()

        self.controller.moveL(
            [
                self.robot_position[0],
                self.robot_position[1],
                self.height + 0.15, 
                self.orientation[0],
                self.orientation[1],
                self.orientation[2]
            ],
            self.velocity,
            self.acceleration
        )
    
    def rest(self):
        # Moves TCP to the rest position.
        self.controller.moveL(
            [
                self.rest_position[0],
                self.rest_position[1],
                self.height + 0.15, 
                self.orientation[0],
                self.orientation[1],
                self.orientation[2]
            ],
            self.velocity,
            self.acceleration
        )
    
    def dispense(self):
        # Magnet is already on, moves TCP to dispense location, then demagnetizes magnet, dropping the piece.
        self.controller.moveL(
            [
                self.dispense_position[0],
                self.dispense_position[1],
                self.height + 0.15, 
                self.orientation[0],
                self.orientation[1],
                self.orientation[2]
            ],
            self.velocity,
            self.acceleration
        )
        self.magnetize()
        

board = Board()

board.move_to("a5")
board.connect("pawn")
board.dispense()
