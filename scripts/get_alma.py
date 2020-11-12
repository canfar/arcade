#!python
"""Given an ALMA project code on the commandline download all the associated Member observations sets"""

from astroquery.alma import Alma
import sys, os
import numpy as np

a = Alma()
a.cache_location=os.curdir

q = a.query(payload={"project_code": sys.argv[1]})
uids =  np.unique(q['Member ous id'])
print("Found {} sets to download".format(len(uids)))
print(uids)


for uid in uids:
   print("Getting UID: {}".format(uid))
   a.retrieve_data_from_uid([uid,], cache=False)

