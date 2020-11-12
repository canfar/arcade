
import glob
import math
import sys
import pickle


def get_info(filename):
   info = {}
   msmd.open(filename)
   info['band'] = int(msmd.namesforspws(0)[0].split("#")[1].split("_")[2])
   position = msmd.phasecenter()
   info['ra'] = math.degrees(position['m0']['value'])
   info['dec'] = math.degrees(position['m1']['value'])
   fields = msmd.fieldnames()
   if len(fields) > 1 :
      raise ValueError("Expectedra ms with just one target")
   if msmd.nobservations() > 1:
      raise ValueError("Exepected ms with just one observation")
   info['field']=fields[0]
   spws = msmd.spwsforfield(fields[0])
   spectral_windows = []
   for idx in spws:
      spectral_windows.append((min(msmd.chanfreqs(idx)), max(msmd.chanfreqs(idx))))
   info['spectral_windows'] = spectral_windows
   dates = msmd.timerangeforobs(0)
   info['start_date'] = dates['begin']['m0']['value']
   info['end_date'] = dates['end']['m0']['value']
   info['project'] = msmd.projects()[0]
   scans = msmd.scansforfield(info['field'])
   itime = 0
   for scan in scans:
      itime += len(msmd.timesforscan(scan)) * msmd.exposuretime(scan)['value']
   info['itime'] = itime
   return info
   

if __name__ == '__main__':
   project = sys.argv[-1]
   pk_file = "/home/jkavelaars/{}_md.pk".format(project)
   md = {}
   if os.access(pk_file, os.F_OK):
     with open(pk_file, 'r') as pk:
        md = pickle.load(pk)
        print md
   for filename in glob.glob('uid__*.ms.split.cal'):
       try:
          md[filename] = get_info(filename)
       except Exception as ex:
          sys.stderr.write(str(filename)+":  "+str(ex)+"\n")
   with open(pk_file, 'w') as pkl:
       pickle.dump(md, pkl)
   for key in md.keys():
      print key, md[key]['project']

