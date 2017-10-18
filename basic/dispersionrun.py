# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import numpy as np
import datetime

"""
PRGMMR: Alice Crawford  ORG: CICS-MD
PYTHON 2.7
ABSTRACT: Classes and functions for creating HYSPLIT control and setup files.

   CLASSES
   HycsControl class for reading / writing a HYSPLIT dispersion run  control file
   Helper Classes for HycsControl class
           Species class representing pollutant properties as defined in CONTROL file
           ConcGrid class representing concentration grid as defined in CONTROL file
           ControlLoc class representing a release location in HYSPLIT CONTROL file
   NameList():  class for writing a SETUP.CFG file
   FUNCTIONS
   writelanduse - writes ASCDATA.CFG file which is needed to run HYSPLIT.

"""
def writelanduse(landusedir, outdir='./'):
    with  open(outdir + "ASCDATA.CFG", "w") as fid:
          fid.write("-90.0  -180.0 \n")
          fid.write("1.0    1.0    \n")
          fid.write("180    360    \n")
          fid.write("2 \n")
          fid.write("0.2 \n")
          fid.write(landusedir + "/bdyfiles/ \n")
#-----------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------#
#Following classes used for reading and writing HYSPLIT control and setup files.


class ConcGrid():
    """concentration grid as defined by 10 lines in the HYSPLIT concentration CONTROL file.
       """
    def __init__(self, name, levels=[50] , centerlat = 0, centerlon= 0, latdiff=0.1, londiff=0.1, 
                 latspan=90, lonspan=360, outdir='./', outfile='cdump', nlev=-1, 
                 sample_start='00 00 00 00 00', sample_stop='00 00 00 00 00',
                 sampletype=0 , interval = (1,0)):


       """sample type can be 0 (average), 1 (snapshot), 2 (max value), (-x) average over x hours.
          inteval is (hour, minutes) interval to create output. If the sample type is positive then
          this is also the interval over which to create the average (or find the max value).
       """
       self.name = name
       self.levels=levels
       self.centerlat = centerlat
       self.centerlon = centerlon
       self.latdiff = latdiff
       self.londiff = londiff
       self.latspan = latspan
       self.lonspan = lonspan
       self.outdir = outdir
       self.outfile = outfile
       self.nlev = nlev
       self.sample_start = sample_start
       self.sample_stop = sample_stop
       self.sampletype = sampletype
       self.interval = interval
       self.get_nlev()
       self.annotate=False

    def set_annotate(self, on=True):
        if on:
           self.annotate=True
        else:
           self.annotate=False
           
    def get_nlev(self):
       if self.nlev == -1:
          self.nlev = len(self.levels)
       else:
          if self.nlev != len(self.levels):
             print 'WARNING nlev not equal to number of leves in levels array'

          
    def __str__(self):
        """string method will output ten lines suitable for inserting into a HYSPLIT control file"""
        pnotes = self.annotate
        note = ''
        if pnotes:
           note = '  #Concentration Grid Center (latitude longitude)'
        returnstr =  str(self.centerlat) + ' ' + str(self.centerlon) + note + '\n'
        if pnotes:
           note = '  #Concentration grid spacing (degrees latitude longitude)'
        returnstr += str(self.latdiff) + ' ' + str(self.londiff) + note + '\n'
        if pnotes:
           note = '  #Concentration grid span (degrees latitude longitude)'
        returnstr += "{:.2f}".format(self.latspan) + ' ' + "{:.2f}".format(self.lonspan) + note + '\n'
        if pnotes:
           note = '  #Directory to write concentration output file'
        returnstr += self.outdir + note + '\n'
        if pnotes:
           note = '  #Filename for concentration output file'
        returnstr += self.outfile.strip() + note + '\n'
        if pnotes:
           note = '  #Number of vertical levels for concentration grid'
        returnstr += str(self.nlev) + note + '\n'
        if pnotes:
           note = '  #List of vertical levels for concentration grid'
        for lev in self.levels:
            returnstr += str(lev) + ' '
        returnstr += note + '\n'
        if pnotes:
           note = '  #Sampling start time of concentration grid'
        returnstr += self.sample_start + note + '\n'
        if pnotes:
           note = '  #Sampling stop time of concentration grid'
        returnstr += self.sample_stop  + note + '\n' 
        if pnotes:
           note = '  # ' + self.typestr()
        returnstr += "{:02.0f}".format(self.sampletype) + ' '
        returnstr += "{:02.0f}".format(self.interval[0]) + ' ' + "{:02.0f}".format(self.interval[1])  + \
                       note + '\n'
        return returnstr
          

    def describe(self):
        """describe prints out a description of what the lines in the control file mean"""
        returnstr =  "Center of Lat and Lon: " + str(self.centerlat) + ' ' + str(self.centerlon) + '\n'
        returnstr += "Spacing (deg) Lat, Lon: " + str(self.latdiff) + ' ' + str(self.londiff) + '\n'
        returnstr += "Span (deg Lat, Lon: " + str(self.latspan) + ' ' + str(self.lonspan) + '\n'
        returnstr += "Output grid directory: " + self.outdir + '\n'
        returnstr += "Output grid file name: " + self.outfile + '\n'
        returnstr += "Num of vertical levels: " + str(self.nlev) + '\n'
        returnstr += "Height of levels (M Agl) : " 
        for lev in self.levels:
            returnstr += str(lev) + ' '
        returnstr += '\n'
        returnstr += "Sampling start (yy mm dd hh min) : " + self.sample_start + '\n'
        returnstr += "Sampling stop (yy mm dd hh min) : " + self.sample_stop  + '\n'
        #returnstr +=  self.typstr() + ' ' + str(self.sampletype) + ' '
        returnstr +=  "Interval (hh min) " + str(self.interval[0]) + ' ' + str(self.interval[1]) + '\n'
        return returnstr
           


    def typestr(self):
       """returns a string describing what kind of sampling interval is used"""
       print self.interval[0], self.interval[1]
       tmstr = str(self.interval[0]).zfill(2) + ':' + str(self.interval[1]).zfill(2)
       if self.sampletype == 0:
          return 'Average over  ' + tmstr + ' with output every ' + tmstr
       elif self.sampletype == 1:
          return 'Snapshot every ' + tmstr
       elif self.sampletype == 2:
          return 'Maximum every ' + tmstr
       elif self.sampletype < 0:
          returnstr = 'Average over ' + str(abs(self.sampletype)) + ' hours with output every ' + tmstr
          return returnstr
       

    def definition(self, lines):
       """input list of 10 lines of the control file which define a concentration grid"""
       temp = lines[0].split()
       try:
           self.centerlat = float(temp[0])
       except:
           print 'warning: center latitude not a float' , temp[0]
           return False
       try:
           self.centerlon = float(temp[1])
       except:
           print 'warning: center longitude not a float' , temp[1]
           return False

       temp = lines[1].split()
       try:
           self.latdiff = float(temp[0])
       except:
           print 'warning: spacing of latitude not a float' , temp[0]
           return False
       try:
           self.londiff = float(temp[1])
       except:
           print 'warning: spacing of longitude not a float' , temp[1]
           return False

       temp = lines[2].split()
       try:
           self.latspan = float(temp[0])
       except:
           print 'warning: span of latitude not a float' , temp[0]
           return False
       try:
           self.lonspan = float(temp[1])
       except:
           print 'warning: span of longitude not a float' , temp[1]
           return False

       self.outdir = lines[3].strip()
       self.outfile = lines[4].strip()

       try:
           self.nlev = int(lines[5])
       except:
           print 'warning: number of levels not an integer' , lines[5]
           self.nlev = 0
           return False

       temp = lines[6].split()
       for lev in temp:
           try:
              lev = float(lev)
           except:
              print 'warning: level not a float' , lev
              lev = -1
           self.levels.append(lev)
       
       temp = lines[7].strip()
       self.sample_start = temp  
       temp = lines[8].strip()
       self.sample_stop = temp  

       temp = lines[9].strip().split()
       try:
           self.sampletype = int(temp[0])
       except:
           print 'warning: sample type is not an integer' , temp[0]
       try:
           self.interval = (int(temp[1]), int(temp[2]))
       except:
          print 'interval not integers' , temp[1], temp[2] 
       return True



class Species():
    """Class which contains information to define a species or pollutant in a HYSPLIT control file.
       methods:
       definition - input 3 lines from control file for defining a pollutant
       define_dep - input 5 lines from control file for defining deposition"""
    total = 0

    @staticmethod
    def status():
        return Species.total
       
    def __init__(self, name, psize=99, rate=1, duration=-1, density=2.5, shape=1, date="00 00 00 00 00", wetdep = 1,
                 vel = '0.0 0.0 0.0 0.0 0.0' , decay = '0.0' , resuspension='0.0'):
        self.name = name
        self.rate = rate
        self.duration = duration
        self.psize = psize           #should be float or nothing.
        self.density=density
        self.shape = shape
        self.date = date
        self.wetdep = wetdep
        self.wetdepstr=''
        self.vel = vel
        self.decay = decay
        self.resuspension = resuspension
        Species.total += 1

    def definition(self, lines):
        """input 3 lines from HYSPLIT CONTROL file which define a pollutant/species"""
        try:
           self.rate = float(lines[0])
        except:
           print "warning: rate is not a float" , lines[0]
           return  False
        try:
           self.duration = float(lines[1])
        except:
           print "warning: duration is not a float" , lines[1]
           return  False
        if lines[2].strip()[0:2] == "00":
              self.date = lines[2].strip()
        else:
            try:
               self.date = datetime.datetime.strptime(lines[2].strip(), "%y %m %d %H %M")
            except:
               print "warning: date not valid" , lines[2]
               self.date = lines[2].strip()
           
        return True

    def define_dep(self, lines):
        """input list of 5 lines in CONTROL file that define deposition for pollutant"""
        temp = lines[0].strip().split()
        try:
           self.psize = float(temp[0])
        except:
           print 'warning: diameter not a float ', temp[0]
        try:
           self.density = float(temp[1])
        except:
           print 'warning: density not a float ', temp[1]
        try:
           self.shape = float(temp[2])
        except:
           print 'warning: shape not a float ', temp[2]
        ##To do - read these in as floats 
        self.vel = lines[1].strip()
        self.wetdepstr = lines[2].strip()
        self.wetdep=1
        self.decay = lines[3].strip()
        self.resuspension = lines[4].strip()
        return -1

    def strpollutant(self, annotate=False):
        """Prints out three lines which define a species/pollutant in HYSPLIT control file"""
        note = ''
        spc = ' ' * 20
        if annotate:
           note=spc + '#Species identifier'
        returnval = self.name + note + '\n' 
        if annotate:
           note=spc + '#Rate of emission'
        returnval += str(self.rate) + note + '\n' 
        if annotate:
           note=spc + '#Duration of emission'
        returnval +=  "%0.2f"%self.duration + note + '\n' 
        if annotate:
           note=spc + '#Start date of emission'
        returnval +=  self.date.strip() + note  +'\n'
        return returnval

    def strdep(self, annotate=True):
        """Prints out five lines which define deposition and gravitational settling for species/pollutant in HYSPLIT control file"""
        note = ''
        spc = ' ' * 20
        if annotate:
           if self.shape < 0:
              shapstr = 'Ganser Formulation'
           if self.shape >= 0:
              shapstr = 'Stokes Formulation'
           shapstr=''
           note=spc + '#Particle diameter(um)   Density (g/cc),  Shape ' + shapstr
        returnval = "%05.1f"%self.psize + ' ' + "%02.1f"%self.density + ' ' + "%04.1f"%self.shape + note + '\n'
        if annotate:
           note=spc + '#Dry Deposition for gas or using resistance method '
        returnval += self.vel + note + '\n'
        if annotate:
           note=spc + '#Wet deposition parameters'
        if self.wetdep==1:
            if self.wetdepstr =='':
                returnval += '0.0 4.0E+04 5.0E-06' + note + '\n'
            else:
                returnval += self.wetdepstr  + note + '\n'
        else:
            returnval += '0.0 0.0 0.0' + note + '\n'
        if annotate:
           note=spc + '#radioactive decay parameters'
        returnval += str(self.decay) + note + '\n'  #line for radioactive decay half life
        if annotate:
           note=spc + '#resuspension from deposit'
        returnval += self.resuspension + note + '\n'  #line for resuspension factor

        return returnval

class NameList():
    """class which represents HYSPLIT SETUP.CFG file,
       This class can also be used to write GENPARM.CFG file for hycs_gem.
       In write method set gem=True"""

 
    def __init__(self, fname='SETUP.CFG', working_directory='./'):
        self.fname = fname 
        self.nlist = {}
        self.descrip = {}
        self._load_descrip()
        if working_directory[-1] != '/':
           working_directory += '/'
        self.wdir=working_directory

    def add_n(self, nlist):
        self.nlist = nlist

    def _load_descrip(self):
        self.descrip['ichem'] = 'Chemistry conversion modules. 0:none, 1:matrix , 2:convert, 3:dust' 
        self.descrip['qcycle'] = 'Cycling of emission hours'
        self.descrip['delt'] = 'integration time step (0=autoset, >0= constant ,<0=minimum)'
        self.descrip['kmixd'] = 'mixed layer obtained from 0:input, 1:temperature, 2: TKE'
        self.descrip['kmix0'] = 'mixing depth. 250 minimum'
        self.descrip['kzmis'] = 'Vertical mixing profile. 0:No adjustments. 1: vertical diffusivity in PBL single average value'
        self.descrip['kbls'] = 'Stability computed by (1) Heat and momentum fluxes, 2: Wind and temperature profiles'
        self.descrip['kblt'] = 'Flag to set vertical turbulence computational method. 1:Beljaars/Holtslag (2):Kanthar/Clayson 3:TKE field 4:Velocity Variances'
        self.descrip['initd'] = 'defines particle or puff mode'

    
    def summary(self):
       if 'initd' in self.nlist.keys():
           test = int(self.nlist['initd'])
           if test== 0:
              print '3D particle horizontal and vertical'    
           elif test==1:
              print 'Gaussian horizontal and Top-Hat vertical puff'
           elif test==2:
              print 'Top-Hat horizontal and vertical puff'
           elif test==3:
              print 'Gaussian horizontal puff and vertical particle distribution'
           elif test==4:
              print 'Top-Hat horizontal puff and vertical particle distribution'
           else:
              print '3D particle horizontal and vertical'    
           

    def set_dust(self):
        self.nlist['ichem'] = '3'
        self.nlist['qcycle']='3'
         

    def read(self):
        with  open(self.wdir + self.fname, "r") as fid:
            content = fid.readlines()
        for line in content:
            if '=' in line:
                temp = line.strip().split('=')
                self.nlist[temp[0].strip()] = temp[1].strip(',')

    def write(self, order=[-1], gem=False, verbose=False):
        """ if gem=True then will write &GENPARM at beginning of file rather than &SETUP"""
        with  open(self.wdir + self.fname, "w") as fid:
            if gem:
                fid.write('&GEMPARM \n')
            else:
                fid.write('&SETUP\n')
            if order ==[-1]:
               order = self.nlist.keys()
            for key in order:
                fid.write(key + '=' + str(self.nlist[key]) + ',\n')
                if verbose: print key, str(self.nlist[key])
            fid.write('/\n')
#    def describe(self):


    

   
class ControlLoc():
    """represents a Release location in HYSPLIT CONTROL file"""
    total=0

    @staticmethod
    def status():
        return ControlLoc.total
       
    def __init__(self, line=-99, latlon=(-1,-1), alt=10.0, rate=False, area=False):
        """ Can either input a string (line from HYSPLIT CONTROL file) or can enter
            latlon = tuple (default(-1,-1))
            altitude= real (default (10.0))
            rate 
            area """

        if line != -99:
           self.definition(line)
        else:
           self.latlon = latlon
           self.alt = alt
           self.rate = rate
           self.area = area

        ControlLoc.total+=1 
        
 
    def definition(self, line):
        temp = line.split(' ')
        try:
            self.lat = float(temp[0])
        except:
            self.lat = -1
        try:
            self.lon = float(temp[1])
        except:
            self.lon = -1
        try:
            self.alt = float(temp[2])
        except:
            self.alt = 10.0
        try:
            self.rate = float(temp[3])
        except:
            self.rate = False
        try:
            self.area = float(temp[4])
        except:
            self.area = False
        self.latlon = (self.lat, self.lon)
 
    def __str__(self):
        spc = " "
        returnstr = "{:.2f}".format(self.latlon[0]) 
        returnstr += spc 
        returnstr +=  "{:.2f}".format(self.latlon[1]) 
        returnstr += spc 
        returnstr +=  "{:.1f}".format(self.alt) 
        if self.rate:
           returnstr += spc 
           returnstr +=  "{:.0f}".format(self.rate) 
        if self.area:
           returnstr += spc 
           returnstr +=  "{:.2E}".format(self.area) 
        return returnstr


class HycsControl():
    """class which represents the HYSPLIT control file and all the information in it"""

    def __init__(self, fname='CONTROL', working_directory='./'):
        self.fname = fname        
        if working_directory[-1] != '/':
           working_directory += '/'
        self.wdir = working_directory
        self.species = []
        self.concgrids=[]
        self.locs=[]
        self.metfiles=[]
        self.metdirs=[]
        self.nlocs = 0      #number of locations
        self.num_grids = 0  #number of concentration grids.
        self.num_sp = 0     #number of pollutants / species
        self.num_met = 0    #number of met files
    
    def rename(self,name, working_directory='./'):
        self.fname=name
        if working_directory[-1] != '/':
           working_directory += '/'
        self.wdir = working_directory
  
 
    def add_sdate(self, sdate):
        self.date = sdate
 
    def add_species(self, species):
        self.num_sp +=1
        self.species.append(species) 

    def add_cgrid(self, cgrid):
        self.num_grids +=1
        self.concgrids.append(cgrid) 


    def add_location(self, line=-99, latlon = (0,0), alt= 10.0 , rate=False, area=False):
        self.nlocs +=1
        self.locs.append(ControlLoc(line=line, latlon=latlon, alt=alt, rate=rate, area=area))
         
    def add_ztop(self, ztop):
        self.ztop=ztop

    def add_vmotion(self, vmotion):
        self.vertical_motion=vmotion
       
    def add_metfile(self, metdir, metfile):
        self.num_met +=1
        self.metfiles.append(metfile)
        self.metdirs.append(metdir) 

    def add_duration(self, duration):
        self.run_duration= duration


    def write(self, verbose=True, annotate=False, adderr=False):
        ##if adderr=True deliberately writes file incorrectly. This is
        ##to help catch error handling in downstream applications..
        note = ''
        sp28 = ' ' * 28
        with open(self.wdir + self.fname, "w") as fid:
            fid.write(self.date.strftime("%y %m %d %H"))
            if annotate:
               note = ' '*18 + '#Start date of simulation'
            fid.write(note + '\n')
            if annotate:
               note = ' '*28 + '#Number of source locations'
            if adderr:
                fid.write(str(self.nlocs+1) + note + "\n")
            else:
                fid.write(str(self.nlocs) + note + "\n")
            iii=0
            if annotate:  note = ' '*15 + '#Lat Lon Altitude'
            for source in self.locs:
                fid.write(str(source) )
                if iii>0: note=''
                fid.write( note )
                iii+=1
                fid.write('\n')
 
            if annotate:
               note = sp28 +  '#Duration of run'
            fid.write(str(int(self.run_duration)) + note + '\n')
            if annotate:
               note = sp28 + '#Vertical Motion'
            fid.write(str(self.vertical_motion) + note +  '\n')
            if annotate:
               note = sp28 + '#Top of Model Domain'
            fid.write(str(self.ztop) + note + '\n')
            if annotate:
               note = sp28 + '#Number of Meteorological Data Files'
            fid.write(str(self.num_met) + note + "\n")
            iii=0
            for met in self.metfiles:
                if annotate: note = '  #Meteorological Data Directory'
                if iii > 0 : note = ''
                fid.write(self.metdirs[iii])
                fid.write(note + "\n")
                if annotate: note = '  #Meteorological Data Filename'
                if iii > 0 : note = ''
                fid.write(met)
                fid.write(note + "\n")
                iii+=1

            if annotate: note = sp28 + '#Number of Pollutant Species'
            fid.write(str(self.num_sp) + note + "\n")
            iii=0
            for sp in self.species:
                if iii==0 and annotate:
                   fid.write(sp.strpollutant(annotate=True))
                else: 
                   fid.write(sp.strpollutant(annotate=False))
                iii+=1
            fid.write(str(self.num_grids) + "\n")
            for cg in self.concgrids:
                if annotate:
                   cg.set_annotate()
                fid.write(str(cg))
    
            if annotate: note = sp28 + '#Number of Pollutant Species'
            fid.write(str(self.num_sp) + note + "\n")
            iii=0
            for sp in self.species:
                if iii==0:
                    fid.write(sp.strdep(annotate=annotate))
                else:
                    fid.write(sp.strdep(annotate=False))
                iii+=1

        return False

    def summary(self):
       print 'CONTROL FILE'
       print 'release start date', self.date
       print 'number of release locations' , self.nlocs
       print 'run time'          , self.run_duration
       print 'Num of met grids ' , self.num_met
       print 'Num of species ' ,   self.num_sp
       return True    

    def readlocs(self, fname):
        with  open(self.fname, "r") as fid:
            for line in fid:
                temp = line.strip().split(' ')
                #latlon = (temp[0], temp[1])
                self.locs.append(line.strip())
                 
                self.nlocs+=1


    def read(self, verbose=True):
        with  open(self.wdir + self.fname, "r") as fid:
        #fid = open(self.fname, "r")
            content = fid.readlines()
            self.date = datetime.datetime.strptime(content[0].strip(), "%y %M %d %H")
            self.nlocs = int(content[1].strip())
            #self.locs = []
            zz=2
            for ii in range(zz, zz+self.nlocs):
                self.locs.append(content[ii].strip()) 
            zz+=self.nlocs
            self.run_duration = content[zz].strip()
            self.vertical_motion = content[zz+1].strip()
            self.ztop = content[zz+2].strip()
            self.num_met = int(content[zz+3].strip())
            zz=zz+4
            for ii in range(zz, zz+2*self.num_met, 2):
                self.metdirs.append(content[ii].strip()) 
                self.metfiles.append(content[ii+1].strip()) 
            zz = zz + 2*self.num_met
            self.num_sp = int(content[zz])
            print 'num species' , self.num_sp
            zz+=1
            for ii in range(zz, zz+4*self.num_sp, 4):
                lines = []
                spname = content[ii].strip()
                lines.append(content[ii+1])
                lines.append(content[ii+2])
                lines.append(content[ii+3])
                sptemp = Species(spname) 
                if sptemp.definition(lines):
                   self.species.append(sptemp)
            zz += 4*self.num_sp
            self.num_grids = int(content[zz])
            self.concgrids=[]
            for ii in range(zz, zz+10*self.num_grids, 10):
                lines = []
                spname = content[ii].strip()
                for kk in range(1,11):
                    lines.append(content[ii+kk])
                sptemp = ConcGrid(spname) 
                if sptemp.definition(lines):
                   self.concgrids.append(sptemp)
            zz += 10*self.num_grids 
            zz += 1
            temp = int(content[zz])
            if temp != self.num_sp:
               print 'warning: number of species for deposition not equal to number of species'
            nn=0
            for ii in range(zz, zz+5*self.num_sp, 5):
                lines = []
                for kk in range(1,6):
                    lines.append(content[ii+kk])
                self.species[nn].define_dep(lines)
                nn+=1
            if verbose:
               print '---------------------------'
               print 'CONTROL FILE'
               print 'release start date', self.date
               print 'release locations' , self.locs
               print 'run time'          , self.run_duration
               print 'vertical motion'   , self.vertical_motion
               print 'Top of model domain' , self.ztop
               print 'Num of met grids ' , self.num_met
               print 'Met directories ' , self.metdirs
               print 'Met files ' ,       self.metfiles
               print 'Num of species ' , self.num_sp
               kk = 1
               for sp in self.species:
                   print '-----Species ' , str(kk) , '---------'
                   print sp.strpollutant()
                   print sp.strdep()
                   kk+=1
                   print '--------------'
               kk = 1
               for grid in self.concgrids:
                   print '-----Concentration Grid ' , str(kk) , '---------'
                   print grid
                   kk+=1
                   print '--------------'
               print '---------------------------'
        return True

 




