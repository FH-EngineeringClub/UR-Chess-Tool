# UR-Chess-Tool

Repurposed Universal Robots cobot which utilizes AI to play chess with both itself and against another player.

## Requirements

- [stockfish](https://pypi.org/project/stockfish/), [python-chess](https://pypi.org/project/chess/), and [ur_rtde](https://pypi.org/project/ur-rtde/)
  - Installable with `pip install -r requirements.txt`
  - ur_rtde requires additional setup for installation, see [ur_rtde Installation](#ur_rtde-installation) for details
- Install the stockfish binary with `brew install stockfish` on macOS or by downloading [here](https://stockfishchess.org/download/) on windows

  - It may be helpful to add [stockfish to PATH](https://medium.com/@kevinmarkvi/how-to-add-executables-to-your-path-in-windows-5ffa4ce61a53) on windows
  - For linux, download the latest 64-bit version of stockfish [here](https://stockfishchess.org/download/linux/), open with `tar -xvf stockfish-ubuntu-x86-64.tar`, and place the binary in path with `mv stockfish-ubuntu-x86-64 /usr/bin/stockfish`

- Install [svg preview for VS code](https://marketplace.visualstudio.com/items?itemName=jock.svg)

## [ur_rtde Installation](https://sdurobotics.gitlab.io/ur_rtde/installation/installation.html)

### Windows

[Install boost](https://www.geeksforgeeks.org/how-to-install-c-boost-libraries-on-windows/)  
[Install cmake](https://cmake.org/download/)  
`pip install ur-rtde`

### MacOS

`brew install cmake`  
`brew install boost`  
`pip install ur-rtde --use-pep517`

### Linux

_(Ubuntu 22.04 recommended for compatibility)_:  
`sudo apt-get install libboost-all-dev`  
`sudo add-apt-repository ppa:sdurobotics/ur-rtde`  
`sudo apt-get update`  
`sudo apt install librtde librtde-dev`  
`sudo apt install cmake`  
`pip install ur-rtde --use-pep517`

## Resources

[Project Notion Page (Documentation)](https://splendid-eel-64f.notion.site/UR10-Chess-Robot-eca1ce190f8b4982b52d836f1d4e0b59?pvs=4) 

[UR Real-Time Communication Guide](https://www.universal-robots.com/articles/ur/interface-communication/real-time-data-exchange-rtde-guide/)

[ur_rtde Documentation](https://sdurobotics.gitlab.io/ur_rtde/index.html)

[Python Stockfish](https://github.com/zhelyabuzhsky/stockfish)

[python-chess documentation](https://python-chess.readthedocs.io/en/latest/index.html)

[Stockfish and python-chess tutorial](https://github.com/rogerfitz/tutorials/blob/master/python_chess/0_Chess_Basics.ipynb)
