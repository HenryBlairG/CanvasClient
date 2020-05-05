#! /usr/bin/python3
'''
Python script to pull through terminal the fileTree
'''
import sys
from src.CanvasBackend import semester_board as bk


if __name__ == '__main__':
    bk.Profile(sys.argv[1])