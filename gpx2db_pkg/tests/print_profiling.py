import pstats
import os
print(os.getcwd())
p = pstats.Stats('gpx2db_pkg/prof/combined.prof')
p.strip_dirs()
p.sort_stats('cumtime')
p.print_stats(250)
