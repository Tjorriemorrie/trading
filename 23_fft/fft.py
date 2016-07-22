from copy import deepcopy
from math import pi, sin, ceil
from string import ascii_lowercase
from treelib import Node, Tree
import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)-7s - [%(filename)s:%(funcName)s] %(message)s')

all_bytes = ''
with open('vid.mp4', 'rb') as f:
    for line in f:
        for character in line:
            char_bytes = ''.join(format(ord(b), '08b') for b in character)
            # logger.info('character: {} -> {}'.format(character, char_bytes))
            all_bytes += char_bytes
        break

# logger.info('all bytes: {}'.format(all_bytes))


# sine wave f(t) = A * sin( 2 * pi * f * t + phase )
#    Return the sine of x radians.
def f(A, t, phase):
    P = 18.
    f = 1 / P
    return A * sin(2 * pi * f * (t + phase))

phase = 0
A = 1
t = 0
# for phase in range(19):
#     logger.info('{}@{}: {}'.format(A, t, round(f(A, t, phase), 5)))


wheelmap = {
    'a': (1, 0),
    'b': (2, 0),
    'c': (3, 0),
    'd': (5, 0),
    'e': (8, 0),
    'f': (13, 0),
    'g': (21, 0),
    'h': (34, 0),

    'i': (1, 6),
    'j': (2, 6),
    'k': (3, 6),
    'l': (5, 6),
    'm': (8, 6),
    'n': (13, 6),
    'o': (21, 6),
    'p': (34, 6),

    'q': (1, 12),
    'r': (2, 12),
    's': (3, 12),
    't': (5, 12),
    'u': (8, 12),
    'v': (13, 12),
    'w': (21, 12),
    'x': (34, 12),

    # 'y': (2, 0),
    # 'z': (2, 0),
}
logger.info('wheelmap = {}'.format(wheelmap))


def simulate(tree, wheels, bytes):
    logger.info(tree)
    logger.info(wheels)
    # logger.info(bytes)
    # tree root node holds current state of wheels
    # the wheels might need to be deep copied to new leafs

    # loop till constraint reached
    for bit in bytes:
        logger.info('tree depth = {}'.format(tree.depth()))

        # thus for every bit
        logger.info('current bits = {}'.format(bit))

        for node in tree.expand_tree(mode=Tree.WIDTH):


        break


    return tree


# create tree
tree = Tree()
tree.create_node('root')

# current frequencies will be stored in the wheels
wheels = []

# built compression is string
# z12y5
final = ''

# while bytes remain
while all_bytes:

    # build tree from simulation (till constraint reached)
    tree = simulate(tree, wheels, all_bytes)
    tree.show()

    # take best node
    # set node's action to final string
    # set node as root
    # tick wheels to next state (after last bit wheels must be empty)

    break

