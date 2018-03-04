from gurobipy import *

# Quarter	Brisbane	Melbourne	Adelaide	Cost
table = """
Q1	1800	2400	3200	$873
Q2	2100	3400	1800	$901
Q3	2500	2800	1700	$1010
Q4	2400	2200	2400	$992
Q5	1750	2500	2500	$1025
Q6	1950	3600	2200	$906
Q7	2600	2950	1850	$1011
Q8	2700	1350	1950	$1013
"""

parsed = [ i.split() for i in table.split('\n')[1:-1]]
# slicing `1:` because we have a newline on the first and last lines of the table

Quarter     = [     i[0]      for i in parsed ]
Brisbane    = [ int(i[1])     for i in parsed ]
Melbourne   = [ int(i[2])     for i in parsed ]
Adelaide    = [ int(i[3])     for i in parsed ]
Cost        = [ int(i[4][1:]) for i in parsed ]
# slicing `1:` to remove the dollar sign

assert(len(Quarter) == 8)
Q = range(len(Quater))

