import sys
major = sys.version_info[0]
minor = sys.version_info[1]
if major != 2 or minor < 5:
    print >>sys.stderr, 'Python too old (version 2.5 or newer) required'
    sys.exit(1)
try:
    import numpy
except:
    print >>sys.stderr, 'Cannot import numpy'
    sys.exit(1)
try:
    import scipy
except:
    print >>sys.stderr, 'Cannot import scipy'
    sys.exit(1)

