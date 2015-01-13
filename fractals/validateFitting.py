from fractals import FractalFactory
from matplotlib import pyplot


if __name__ == '__main__':
    depth = 1

    ff = FractalFactory()
    ff.make_graph(depth, (0, 0), (1, 1), [(1/9, 2/3), (5/9, 1/3)])
    graph = ff.graph
    pyplot.plot(*zip(*sorted(graph)))
    pyplot.show()