import sys

from computer_club_simulator import ComputerClubSimulator

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("The algorithm filename was not given!")
    else:
        computer_club_simulator = ComputerClubSimulator()
        computer_club_simulator.simulate(sys.argv[1])
