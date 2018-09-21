#!python

from astroquery.alma import Alma
import sys

a = Alma()
a.cache_location="/home/cache/"

q = a.query(payload={"project_code": sys.argv[1]})

for uid in q['Member ous id']:
   a.retrieve_data_from_uid([uid,], cache=False)

