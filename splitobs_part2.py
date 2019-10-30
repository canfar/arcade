# """This script splits out different observations in a single measurement set based on 
# name of the fields observed.  Additionally, spectral windows are split if they 
# correspond to different frequency resolutions (continuum data versus line observations). """
            
## This is now a 2-part script.  This is part 2, which runs the splitting, and must be run
## in the same version of CASA as was originally used for the calibration in scriptForPI.py
## Part 1 generates the necessary lists of components to be split out, and relies on 
## msmd tools which are only available in more recent versions of CASA.


import numpy as np
import glob
from os import path

# This script should be run after running scriptForPI.py to generate calibrated 
# measurement sets.


####################### Start of the script #####################

# NB: The file name structure should imply that the measurement sets selected 
# have been split after calibration, implying that we wish to keep information
# in the 'data' column for our additional splitting per target
# If we need to include files that instead end in .ms, they might have the calibrated info 
# stored in the 'corrected' column instead.  This subtlety is used for the 'split' command
# used below.


# Read in the lists of components to be split out and then run the split 


def split_ms(filename):
    """
    split out the CALIBRATE and OBSERVE_TARGET observations from given ALMA measurement set
    """
    print("Split out observations found in {}".format(filename))
    ms_name = filename.rstrip("ms.split.cal")
        
    # science fields
    #(Newly coded for the new 2part version)
    with open(ms_name+'_scifields.txt') as f:
        sci_field_names = f.read().splitlines()

    # all fields
    with open(ms_name+'_allfields.txt') as f:
        field_names = f.read().splitlines()
        
    
    # Loop through each of these fields and split out measurement set    
    for field_name in field_names:
        
        #read in the types of spws (line or continuum) if they exist
        cont_spws=[]
        line_spws=[]
        #cont_spws:
        if os.path.exists(ms_name+'_'+field_name+'_contspws.txt'):
                with open(ms_name+'_'+field_name+'_contspws.txt') as f:
                    cont_spws = f.read().splitlines()
        #line_spws:
        if os.path.exists(ms_name+'_'+field_name+'_linespws.txt'):
                with open(ms_name+'_'+field_name+'_linespws.txt') as f:
                    line_spws = f.read().splitlines()
        

        # if this is in the science target list call it science, else its a calibrator
        obs_type = field_name in sci_field_names and "SCI" or "CAL"


        #HK added: split by spw: continuum all goes together, line spws are each separate

        #Continuum: only run if there are any entries in cont_spws
        if cont_spws:
            split_cont_dir = "{}.{}.{}.cont.ms.split.cal".format(ms_name, obs_type, field_name)
            print("Splitting {} into {}".format(field_name, split_cont_dir))
            # Remove the subdirectory, if it exists
            shutil.rmtree(split_cont_dir, ignore_errors=True)
            #split continuum field using casa split command
            #NB: messy bit directly below is to convert the formatting of cont_spws.  CASA's split 
            # command needs it to look like this: '0,1,5'  while cont_spws is in a form like this [0,1,5]
            #   NB: A simple str(cont_spws) does not work because CASA does not like the square braces [ ]  
            cont_spws_str = ','.join(str(num) for num in cont_spws)
            split(vis=filename,
                    outputvis=split_cont_dir,
                    field=field_name,
                    datacolumn='data',
                    spw=cont_spws_str)

        #line spws: one at a time (and only if there are any entries in line_spws)
        if line_spws:
            for spws in line_spws:
                #define name & delete if already exists
                split_line_dir = "{}.{}.{}.line_spw{}.ms.split.cal".format(ms_name, obs_type, field_name,spws)
                print("Splitting {} into {}".format(field_name, split_line_dir))
                shutil.rmtree(split_line_dir, ignore_errors=True)
                #run the split
                split(vis=filename,
                    outputvis=split_line_dir,
                    field=field_name,
                    datacolumn='data',
                    spw=str(spws))



    #Final step: remove the txt files associated with this dataset (only)
    os.system('rm -f '+ms_name+'*fields.txt')
    os.system('rm -f '+ms_name+'*spws.txt')
        
    #end of HK adds to the splitting by spw component

        
            
if __name__ == "__main__":
    BASE_FILENAME = "*.ms.split.cal" # Types of files to process
    for filename in glob.glob(BASE_FILENAME):
        split_ms(filename)

