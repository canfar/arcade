#!bash

# Decend into subdirectories that contain scriptForPI.py and run those
# this script expects to be run in the apropriate CASA container

for script in `find ./ -naem scriptForPI.py`
do
   cd ${script%/*}
   casa --nogui --pipeline -c scriptForPI.py
done
   
