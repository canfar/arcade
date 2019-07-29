import glob
from os import path

#This function generates the ms.split.cal file for the special case of Cycle 4 data which was
# both calibrated and imaged using the pipeline.  The default here is to *not* create the
# ms.split.cal file.  Cycle 5 onwards has a switch to override this default behaviour.

def split_cal(filename):
    """
    For cycle 4 data which were pipeline calibrated & imaged, generate the ms.split.cal files
    """
    print("Split out calibrated measurement set from {}".format(filename))
    asdmname = filename.rstrip(".ms")
    #HK notes: the following code is copied from the pipeline script where this issue was first
    # noticed (2016.1.00320.S)
    msmd.open(filename)
    targetspws = msmd.spwsforintent('OBSERVE_TARGET*')
    sciencespws = ''
    outputspws = ''
    i = 0
    for myspw in targetspws:
        if msmd.nchan(myspw)>4:
            sciencespws += str(myspw)+','
            outputspws += str(i)+','
            i += 1
    sciencespws = sciencespws.rstrip(',')
    outputspws = outputspws.rstrip(',')
    msmd.close()
    split(vis=asdmname+'.ms',outputvis=asdmname+'.ms.split.cal', spw=sciencespws)



if __name__ == "__main__":
    #check whether cycle 4 pipeline imaging satisfied & therefore need to generate ms.split.cal files

    splitneeded = False
    # 1) Was the file pipeline calibrated?  (is there a PPR files in /scripts?)
    pprnames = glob.glob('../script/PPR*')
    pprpropcode = []
    if (len(pprnames)>0):
        print("Dataset was pipeline calibrated")
        #2) Is the file from 2016 / Cycle 4?
        for line in open(pprnames[0]):
            if "<ProposalCode>" in line:
                pprpropcode.append(line[line.index('2'):line.index('</')])
                if any('2016.' in tmp for tmp in pprpropcode):
                    print("Project is Cycle 4")
                    #3) Was the imaging pipeline also used?
                    tmppipe = os.popen("grep hif_makeimages "+pprnames[0]+" | wc -l")
                    nummkim = int((tmppipe.readline()).rstrip('\n'))
                    if ( nummkim > 1 ):
                         print("Imaging pipeline was used")
                         splitneeded = True
    #Final sanity check: do ms.split.cal files already exist in the /calibrated directory?
    if os.path.exists('../calibrated*ms.split.cal'):
        splitneeded = False


    BASE_FILENAME="*.ms"
    if splitneeded:
        os.chdir('../calibrated/')
        print("Splitting calibrated measurement sets")
        for filename in glob.glob(BASE_FILENAME):
            print filename
            split_cal(filename)

