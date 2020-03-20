# """This script splits out different observations in a single measurement set based on 
# name of the fields observed.  Additionally, spectral windows are split if they 
# correspond to different frequency resolutions (continuum data versus line observations). """

## This is now a 3-part script which supercedes the original splitobs.py .  
## This is part 0, which is used for special cases in which CASA does not
## automatically generate ms.split.cal file(s), but instead leaves the
## calibrated measurement set as the calibrated column within an earlier file.ms
## This situation is the case for a limited number of CASA versions around 4.7,
## and only applies to pipeline scripts.
## Part 1 assumes all files to be processed are ms.split.cal and generates
## appropriate information for our further splitting (by target & spw).  It
## must be run in a more recent version of CASA which includes the msmd tools.
## Part 2 actually runs the splitting, and must be run in the same version of CASA as was
## originally used for the calibration in scriptForPI.py

import numpy as np
import glob
from os import path

# This script should be run after running scriptForPI.py to generate calibrated 
# measurement sets.



####################### Start of the script #####################

# Part 0: check to see if there are any ms.split.cal files, and if not,
# whether it is possible to generate them.

#HK notes on potential issues:
# 1) If there are cases where scriptForPI.py generates [newname.ms.split.cal]
#   while retaining [origname.ms] also in this directory, we are going to
#   get duplicate split measurement sets with different names, using the
#   script below (and subsequent two parts).  I do not know if there are any
#   such cases, and if so, what conditions they are generated under.  There
#   are two possible ways to avoid this issue:
#       a) have this script run only when the calibration script is running
#       the pipeline and the CASA version is the limited set which does not
#       generate the ms.split.cal files automatically.  This would require
#       further investigation to figure out exactly which versions of CASA
#       to search for (roughly 4.7.* I think, but this would need to be 
#       carefully verified).
#       b) have this script run only when there are no ms.split.cal files
#       in the entire directory.   This should be an easier and safer method,
#       but I'm not sure how to code it.  We would need to make sure that this
#       check was applied before anything in the script ran, and wasn't also
#       performed partway through, so that cases where there are multiple
#       .ms files that do require splitting all get done.
#   2) A simpler point: do we want to track which ms files were split by
#   us at this stage for any future de-bugging, etc, uses?

def split_orig_ms(filename):
    """
    Identify all possible components to be split
    """
    print("Examining {}".format(filename))
    #only continue if a corresponding ms.split.cal file does not exist
    if os.path.exists(filename+'.split.cal'):
        print("No action taken - split.cal already exists.")
    else:
        print("Generating split.cal")
        split(vis=filename, outputvis=filename+'.split.cal', 
                datacolumn='corrected')
        #HK notes: the command above will fail if no corrected
        # column exists.  This is what we want to happen, as this
        # would imply that calibrations have not been applied, and
        # we do not want to proceed any further with this ms.
	# In general, we expect that 'semi-pass' measurement sets
	# will not appear in the /calibrated directory at all, so
	# there are no expected cases where there are .ms files in this
	# directory which do not have a 'corrected' column to split.


if __name__ == "__main__":
    BASE_FILENAME = "*.ms" # Types of files to process
    for filename in glob.glob(BASE_FILENAME):
        split_orig_ms(filename)

