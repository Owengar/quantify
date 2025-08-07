import pstats
p = pstats.Stats('stat.txt')
p.sort_stats("cumulative").print_stats(30)