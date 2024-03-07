
"""
import python-chess and stockfish to play chess
"""

import platform
import subprocess
from time import sleep
import socket
import json
import math
import rtde_io
import rtde_receive
import rtde_control
import keyboard

"""import chess
import chess.svg
from stockfish import Stockfish
from colorama import Fore"""

HOSTNAME = "192.168.2.81"  # Replace with the IP address of your Universal Robot
HOST_PORT = 30002  # The port to send commands to the robot

class Board:
    # f = open("setup.json", encoding="utf-8")
    def __init__(self, 
                 host_info, 
                 origin, 
                 TCP_orientation, 
                 rest_position, 
                 height, 
                 trns_angle):
        
        self.controller = rtde_control.RTDEControlInterface(host_info[0])       # receiving TCP information
        self.receiver = rtde_receive.RTDEReceiveInterface(host_info[0])         # controlling TCP
        self.origin = origin        # origin of coordinate system
        self.trns_angle= trns_angle # angle which coordinate system is rotated by
        self.host_info = host_info  # host name and port
        
        # TCP State Variables
        self.position = origin              # (m)
        self.velocity = 0.5                 # (m/s)
        self.acceleration = 0.3             # (m/s^2)
        self.orientation = TCP_orientation  # (rad)
        self.rest_position = rest_position  # (m)
        self.isMagnetized = False

        # Board State Variables
        self.height = height                # (m)
        f = open("ur10 arm\setup.json", encoding="utf-8")
        self.board_data = json.load(f)
        
        # Initialization
        self.controller.moveL(
            [self.origin[0], 
             self.origin[1], 
             self.height + 0.1,
             self.orientation[0],
             self.orientation[1],
             self.orientation[2]],
             0.5,
             0.3
        )
        

    def translate(self, pos):
        # Takes a position in the board's coordinate space, then translates
        # it into the arm's coordinate space.
        x_1 = pos[1] * math.cos(self.trns_angle) - pos[0] * math.sin(self.trns_angle)
        y_1 = pos[1] * math.sin(self.trns_angle) + pos[0] * math.cos(self.trns_angle)
        # new_pos = A * pos, Givens Rotation

        return [x_1, y_1]

    def move_to(self, square_name):
        # Takes a square name (e.g "a1", "g4"), then moves the TCP to hover 
        # over that square.
        new_pos = [self.board_data[square_name]["x"], self.board_data[square_name]["y"]]
        
        self.robot_position = self.translate(new_pos)
        print(self.robot_position)
        self.controller.moveL(
            [
                self.robot_position[0],
                self.robot_position[1],
                self.height + 0.1, 
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
        sleep(0.2)

    def connect(self, type):
        # Lowers TCP to square space, turns magnet either off and on,
        # then raises back off.
        self.controller.moveL(
            [
                self.robot_position[0],
                self.robot_position[1],
                self.height + 0.078, 
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
                self.height + 0.1, 
                self.orientation[0],
                self.orientation[1],
                self.orientation[2]
            ],
            self.velocity,
            self.acceleration
        )

    def display_board(self):
        pass
    



ANGLE = 44.785  # angle between the robot base and the chess board (in radians)
DX = 0.401  # Home TCP position relative to base (in mm)
DY = -0.564

BOARD_HEIGHT = 0.021  # height for the electromagnet to attach to pieces (in meters), measured as TCP Z relative to base
LIFT_HEIGHT = 0.40  # height of the lift (in meters)

TCP_RX = 1.393  # rx (x rotation of TCP in radians)
TCP_RY = -2.770  # ry (y rotation of TCP in radians)
TCP_RZ = -0.085  # rz (z rotation of TCP in radians)
REST_LOCATION = [-0.11676, -0.3524, 0.133]

board = Board([HOSTNAME, HOST_PORT], 
              [DX, DY], 
              [TCP_RX, TCP_RY, TCP_RZ],
              REST_LOCATION, 
              BOARD_HEIGHT,
              ANGLE)

board.move_to("h8")
board.connect("1")


"""
osSystem = platform.system()  # Get the OS
if osSystem == "Darwin" or "Linux":
    stockfishPath = subprocess.run(
        ["which", "stockfish"], capture_output=True, text=True, check=True
    ).stdout.strip("\n")  # noqa: E501
elif osSystem == "Windows":
    stockfishPath = input("Please enter the full path to the stockfish executable:")
else:
    exit("No binary or executable found for stockfish")

stockfish = Stockfish(path=stockfishPath)
stockfish.set_depth(20)  # How deep the AI looks
stockfish.set_skill_level(20)  # Highest rank stockfish
stockfish.get_parameters()  # Get all the parameters

board = chess.Board()  # Create a new board


def translate(x, y):
    # Rotate a point by a given angle in a 2d space
    x1 = x * math.cos(ANGLE) - y * math.sin(ANGLE)
    y1 = x * math.sin(ANGLE) + y * math.cos(ANGLE)
    return x1 + DX, y1 + DY


def move_to_square(pos, height):
    robot_position = translate(pos["x"], pos["y"])
    control_interface.moveL(
        [
            robot_position[0] / 1000,  # x
            robot_position[1] / 1000,  # y
            height,  # z (height of the chess board)
            TCP_RX,  # rx (x rotation of TCP in radians)
            TCP_RY,  # ry (y rotation of TCP in radians)
            TCP_RZ,  # rz (z rotation of TCP in radians)
        ],
        0.5,  # speed: speed of the tool [m/s]
        0.3,  # acceleration: acceleration of the tool [m/s^2]
    )


def lift_piece(pos):
    robot_position = translate(pos["x"], pos["y"])
    control_interface.moveL(
        [
            robot_position[0] / 1000,  # x
            robot_position[1] / 1000,  # y
            LIFT_HEIGHT,  # z (height to lift piece)
            TCP_RX,  # rx (x rotation of TCP in radians)
            TCP_RY,  # ry (y rotation of TCP in radians)
            TCP_RZ,  # rz (z rotation of TCP in radians)
        ],
        0.5,  # speed: speed of the tool [m/s]
        0.3,  # acceleration: acceleration of the tool [m/s^2]
    )


def lower_piece(pos):
    robot_position = translate(pos["x"], pos["y"])
    control_interface.moveL(
        [
            robot_position[0] / 1000,  # x
            robot_position[1] / 1000,  # y
            BOARD_HEIGHT,  # z (height to lift piece)
            TCP_RX,  # rx (x rotation of TCP in radians)
            TCP_RY,  # ry (y rotation of TCP in radians)
            TCP_RZ,  # rz (z rotation of TCP in radians)
        ],
        0.5,  # speed: speed of the tool [m/s]
        0.3,  # acceleration: acceleration of the tool [m/s^2]
    )


def send_command_to_robot(command):
    # Connect to the robot
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOSTNAME, HOST_PORT))

    # Send the command to the robot
    sock.send(bytes(command, "utf-8"))

    # Receive and print the response from the robot
    # response = sock.recv(1024)
    # print("Response from robot:", response)

    # Close the connection
    sock.close()
    sleep(0.2)  # Allow the piece to attach to the electromagnet


OUTPUT_24 = "sec myProg():\n\
    set_tool_voltage(24)\n\
end\n\
myProg()\n"

OUTPUT_0 = "sec myProg():\n\
    set_tool_voltage(0)\n\
end\n\
myProg()\n"


def display_board():
    # Display the chess board by writing it to a SVG file.
    with open(
        "chess.svg", "w", encoding="utf-8"
    ) as file_obj:  # Open a file to write to with explicit encoding
        file_obj.write(chess.svg.board(board))  # Write the board to the file


# Opening UR10 head positions JSON file
f = open("setup.json", encoding="utf-8")
data = json.load(f)


def direct_move_piece(from_pos, to_pos, board_height, lift_height):
    print("Moving piece from", move_from, "to", move_to)
    move_to_square(from_pos, board_height)
    print("Energizing electromagnet...")
    send_command_to_robot(OUTPUT_24)  # energize the electromagnet
    print("Lifting piece...")
    lift_piece(from_pos)
    print("Moving piece to", move_to)
    if (
        move_to == "ex"
    ):  # TODO rename move_to ex in this case to some other variable (currently causes "string indices must be integers" error)
        move_to_square(to_pos, lift_height)
        print("De-energizing electromagnet...")
        send_command_to_robot(OUTPUT_0)  # de-energize the electromagnet
        print("Piece removed successfully!")
    else:
        move_to_square(to_pos, lift_height)
        print("Lowering piece...")
        lower_piece(to_pos)
        print("De-energizing electromagnet...")
        send_command_to_robot(OUTPUT_0)  # de-energize the electromagnet
        print("Piece moved successfully!")


display_board()  # Display the board

while not board.is_game_over():
    print(Fore.WHITE + "Legal moves:", [move.uci() for move in board.legal_moves])
    inputmove = input(
        "Input move from the following legal moves (SAN format):"
    )  # Get the move from the user

    user_confirmation = input("Are you sure you want to make this move? (y/n)")
    if user_confirmation != "y":
        print(
            Fore.RED + "Move not confirmed, please try again"
        )  # If the user doesn't confirm the move, ask for a new move
        continue  # Skip the rest of the loop and start from the beginning

    valid_move = (
        chess.Move.from_uci(inputmove) in board.legal_moves
    )  # Check if the move is valid

    if valid_move is True:
        board.push_san(inputmove)  # Push the move to the board

        display_board()  # Display the board

        stockfish.set_fen_position(board.fen())  # Set the position of the board
        bestMove = stockfish.get_top_moves(1)  # Get the best move
        target_square = chess.Move.from_uci(bestMove[0]["Move"]).to_square

        if board.piece_at(target_square) is None:
            print(Fore.CYAN + "Space not occupied")

            move = bestMove[0]["Move"]  # e.g. "e2e4" or "e7e5"
            move_from = move[:2]  # from square
            move_to = move[-2:]  # to square
            print(move_from, move_to)
            from_position = data[move_from]
            to_position = data[move_to]
            direct_move_piece(from_position, to_position, BOARD_HEIGHT, LIFT_HEIGHT)

        else:
            print(
                Fore.CYAN + "Space occupied by",
                board.piece_at(target_square),
                "removing piece...",
            )

            move = bestMove[0]["Move"]  # e.g. "e2e4" or "e7e5"
            move_from = move[:2]  # from square
            move_to = move[-2:]  # to square
            print(move_from, move_to)
            from_position = data[move_from]
            to_position = "ex"
            direct_move_piece(from_position, to_position, BOARD_HEIGHT, LIFT_HEIGHT)

        print(
            Fore.GREEN + "Stockfish moves:", board.push_san(bestMove[0]["Move"])
        )  # Push the best move to the board

        display_board()  # Display the board

    else:
        print(Fore.RED + "Not a legal move, Please try again")"""
