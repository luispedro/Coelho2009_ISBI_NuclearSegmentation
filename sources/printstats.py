from statistics import *
print 'Cover GNF:', np.mean([c.result for c in covers_gnf])
print 'Cover IC100:', np.mean([c.result for c in covers_ic100])

