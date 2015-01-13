for i in xrange(1000):
    val = i
    while len(str(val)) > 1:
        vals = list(str(val))
        vals = map(int, vals)
        val = sum(vals)
    if val in [3, 6, 9]:
        print str(i) + " [" + str(len(str(i))) + "] = " + str(val)