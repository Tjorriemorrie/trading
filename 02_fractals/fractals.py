from __future__ import division
from random import shuffle
from matplotlib import pyplot


class FractalFactory():
    graph = set()
    def make_graph(self, diepte, start, end, turns):
        # add points to graph
        self.graph.add(start)
        self.graph.add(end)

        if diepte > 0:
            # unpack input values
            fromtime, fromvalue = start
            totime, tovalue = end

            # calcualte differences between points
            diffs = []
            last_time, last_val = fromtime, fromvalue
            for t, v in turns:
                new_time = fromtime + (totime - fromtime) * t
                new_val = fromvalue + (tovalue - fromvalue) * v
                diffs.append((new_time - last_time, new_val - last_val))
                last_time, last_val = new_time, new_val

            # add 'brownian motion' by reordering the segments
            # shuffle(diffs)

            # calculate actual intermediate points and recurse
            last = start
            for segment in diffs:
                p = last[0] + segment[0], last[1] + segment[1]
                self.make_graph(diepte - 1, last, p, turns)
                last = p
            self.make_graph(diepte - 1, last, end, turns)


if __name__ == '__main__':
    depth = 1
    ff = FractalFactory()
    ff.make_graph(depth, (0, 0), (1, 1), [(1/9, 2/3), (5/9, 1/3)])
    graph = ff.graph
    pyplot.plot(*zip(*sorted(graph)))
    pyplot.show()