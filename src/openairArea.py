#!/usr/bin/env python3

from copy import deepcopy

import bpaTools
import poaffCst
import airspacesCatalog
from airspacesCatalog import AsCatalog
import geoRefArea

def cleanLine(line:str) -> str:
    ret = line.strip()
    ret = ret.replace("\n","")
    ret = ret.replace("  "," ")
    return ret

#Sample content of Openair file   
#   AC R
#   AN [R] 12 (id=LFR12)
#   *AAlt [SFC/3000FT AMSL] [0m/914m]
#   *AUID UId=1563127 - Id=LFR12
#   *ADescr Administrator: NIL. Avoidance mandatory except for exemption granted by the prefect of la Manche, after West DSAC consultation.
#   *AActiv [H24] H24
#   AH 3000FT AMSL
#   AL SFC
#   V X=48:38:11 N 001:30:40 W
#   DC 1.6
    

class OpenairZone:
    
    def __init__(self) -> None:
        self.bBorderInProcess:bool = False
        self.localIndex:int = -1

        #---Airspace Header---
        self.sClass:str = None
        self.sName:str = None
        self.sUpper:str = None
        self.sLower:str = None
        
        #Complementary data (Openair extended format include by 'aixmParser' software)
        self.sGUId:str = None
        self.sUId:str = None
        self.sId:str = None
        self.sAlt:str = None
        self.sDescr:int = None
        self.sActiv:str = None

        #---Abd--- Airspace Borders
        self.oBorder:list = list()
        return

    def isCorrectHeader(self) -> bool:
        ret = self.sClass  != None and \
              self.sName   != None and \
              self.sUpper  != None and \
              self.sLower  != None
        return ret

    def serializeArea(self) -> str:
        if len(self.oBorder) == 0:
            return ""
        area:str = "\n"
        area += self.sClass + "\n"
        area += self.sName + "\n"
        area += self.sAlt + "\n"
        area += "*AUID" + \
                    " GUId=" + self.sGUId + \
                     " UId=" + self.sUId  + \
                      " Id=" + self.sId + "\n"
        if self.sDescr:     area += self.sDescr + "\n"
        if self.sActiv:     area += self.sActiv + "\n"
        area += self.sUpper + "\n"
        area += self.sLower + "\n"
        for oBd in self.oBorder:
            area += oBd + "\n"
        return area
        
    
class OpenairArea:

    def __init__(self, oLog, oAsCat) -> None:
        bpaTools.initEvent(__file__, oLog)
        self.oLog:bpaTools.Logger       = oLog      #Log file
        self.oAsCat:AsCatalog           = oAsCat    #Catalogue des zones
        self.oGlobalOpenair:dict        = {}        #Liste globale des zones
        self.oOpenair:dict              = {}        #Liste temporaire des zones
        self.oZone:OpenairZone          = None      #Zone active
        self.oGeoRefArea                = geoRefArea.GeoRefArea()
        self.newZone()
        return

    def saveOpenairAirspacesFile4Area(self, sFile:str, sContext:str="ff") -> None:
        for sAreaKey in self.oGeoRefArea.AreasRef.keys():
            self.saveOpenairAirspacesFile(sFile, sContext, sAreaKey)
        #NoUse - self.saveOpenairAirspacesFile(sFile, sContext, cstWithoutLocation)
        return

    def saveOpenairAirspacesFile(self, sFile:str, sContext:str="all", sAreaKey:str=None) -> None:
        if sContext=="ff":
            self.saveOpenairAirspacesFile2(sFile, sContext, "-gpsWithTopo")
            #self.saveOpenairAirspacesFile2(sFile, sContext, "-gpsWithTopo", "exceptSAT")
            #self.saveOpenairAirspacesFile2(sFile, sContext, "-gpsWithTopo", "exceptSUN")
            #self.saveOpenairAirspacesFile2(sFile, sContext, "-gpsWithTopo", "exceptHOL")
            #self.saveOpenairAirspacesFile2(sFile, sContext, "-gpsWithoutTopo")
            #self.saveOpenairAirspacesFile2(sFile, sContext, "-gpsWithoutTopo", "exceptSAT")
            #self.saveOpenairAirspacesFile2(sFile, sContext, "-gpsWithoutTopo", "exceptSUN")
            #self.saveOpenairAirspacesFile2(sFile, sContext, "-gpsWithoutTopo", "exceptHOL")
        else:    #context == "all", "ifr" or "vfr"
            self.saveOpenairAirspacesFile2(sFile, sContext, "-gpsWithTopo")
        return

    def saveOpenairAirspacesFile2(self, sFile:str, sContext:str="all", gpsType:str="", exceptDay:str="", sAreaKey:str=None) -> None:
        oOutOpenair:list = []
        sContent:str = ""

        #bpaTools.writeJsonFile(sFile + "-tmp.json", self.oGlobalGeoJSON)                       #Sérialisation pour mise au point
        oGlobalCats = self.oAsCat.oGlobalCatalog[airspacesCatalog.cstKeyCatalogCatalog]         #Récupération de la liste des zones consolidés
        for sGlobalKey, oGlobalCat in oGlobalCats.items():                                      #Traitement du catalogue global complet

            #Filtrage des zones par typologie de sorties
            bIsInclude:bool = False
            if   sContext == "ifr":
                bIsInclude = (not oGlobalCat["vfrZone"]) and (not oGlobalCat["groupZone"])
                sContent = "ifrZone"
                sFile = sFile.replace("-all", "-ifr")
            elif sContext == "vfr":
                bIsInclude = oGlobalCat["vfrZone"]
                sContent = "vfrZone"
                sFile = sFile.replace("-all", "-vfr")
            elif sContext == "ff":
                bIsInclude = oGlobalCat["freeFlightZone"]
                sContent = "freeflightZone"
                sFile = sFile.replace("-all", "-freeflight")
            else:
                sContext = "all"
                sContent = "allZone"
                bIsInclude = True

            #Exclude area if unkwown coordonnees
            if bIsInclude and "excludeAirspaceNotCoord" in oGlobalCat:
                if oGlobalCat["excludeAirspaceNotCoord"]: bIsInclude = False

            #Filtrage des zones par régionalisation
            bIsArea:bool = True
            if sAreaKey!=None:
                if sAreaKey in oGlobalCat:
                    bIsArea = oGlobalCat[sAreaKey]
                else:
                    bIsArea = False

            if bIsArea and bIsInclude and (sGlobalKey in self.oGlobalOpenair):
               oAs:OpenairZone = self.oGlobalOpenair[sGlobalKey]
               oOutOpenair.append(oAs)

        if sAreaKey!=None:
            sContent += " / " + sAreaKey
            sFile = sFile.replace(".txt", "-" + sAreaKey + ".txt")
        sMsg:str = " file {0} - {1} areas in map"
        if len(oOutOpenair) == 0:
            self.oLog.info("Unwritten" + sMsg.format(sFile, len(oOutOpenair)), outConsole=False)
            bpaTools.deleteFile(sFile)
        else:
            self.oLog.info("Write" + sMsg.format(sFile, len(oOutOpenair)), outConsole=False)
            #     oNewHeader.update({airspacesCatalog.cstKeyCatalogContent:sContent})
            #     oNewHeader.update({airspacesCatalog.cstKeyCatalogNbAreas:len(oOutOpenair)})
            sOutOpenair:str = ""
            oOp:OpenairArea = None
            for oOp in oOutOpenair:
                sOutOpenair += oOp.serializeArea()
                
            bpaTools.writeTextFile(sFile, sOutOpenair)  #Sérialisation du fichier
        return


    def newZone(self) -> None:
        self.oZone = OpenairZone()
        return

    def parseLine(self, line:str) -> None:
        if line == "":
            return
        
        line = line.replace(","," ")     #Cleaning
        line = line.replace("\t"," ")    #Cleaning
        line = line.replace("  "," ")    #Cleaning
        aLine = line.split(" ")          #Tokenize
        if "" in aLine:                  #Supression d'éventuels éléments vides
            aLine = list(filter(None, aLine))
        
        #### Header - Traitement des entêtes de zones
        if aLine[0] == "AC":
            if self.oZone.bBorderInProcess:
                self.newZone()
            self.oZone.sClass = line
            return
            
        elif aLine[0] == "AN":
            if self.oZone.bBorderInProcess:
                self.newZone()
            self.oZone.sName = line
            return
            
        elif aLine[0] == "AH":
            if self.oZone.bBorderInProcess:
                self.newZone()
            self.oZone.sUpper = line
            return

        elif aLine[0] == "AL":
            if self.oZone.bBorderInProcess:
                self.newZone()
            self.oZone.sLower = line
            return

        elif aLine[0] == "*AAlt":
            self.oZone.sAlt = line
            return
        
        elif aLine[0] == "*ADescr":
            self.oZone.sDesc = line
            return
        
        elif aLine[0] == "*AActiv":
            self.oZone.sActiv = line
            return        
        
        elif aLine[0] == "*AUID":           #Sample - *AUID GUIg=! UId=1563127 Id=LFR12
            self.oZone.sUId = aLine[2].split("=")[1]
            self.oZone.sId = aLine[3].split("=")[1]
            return

        elif aLine[0] in ["SP","SB","AT","AY"]:
            return    #Pas besoin de récupération...

        elif aLine[0][0] == "*":
            return    #Ignorer ligne de commentaire

        else:
            if not self.oZone.isCorrectHeader():
                self.oLog.critical("Header error before line {}".format(line), outConsole=True)
                return

        #### Airspace - Enregistrement de la zone
        if self.oZone.localIndex < 0:
            self.oZone.bBorderInProcess = True
            self.oOpenair.update({self.oZone.sUId:self.oZone})
            self.oZone.localIndex = len(self.oOpenair)
        
        #### Border - Traitement des bordures géographiques de zones
        if aLine[0] in ["AC","AN","AH","AL","SP","SB","AT","AY"]:
            None    #Traité plus haut dans la parties 'header'
        
        else:
            self.oZone.oBorder.append(line)
        return
    
    
    def parseFile(self, sSrcFile:str) -> None:   
        fopen = open(sSrcFile, "rt", encoding="utf-8", errors="ignore")
        lines = fopen.readlines()
        sMsg = "Parsing Openair file - {}".format(sSrcFile)
        self.oLog.info(sMsg, outConsole=False)
        barre = bpaTools.ProgressBar(len(lines), 20, title=sMsg)
        idx = 0
        for line in lines:
            idx+=1
            lig = cleanLine(line)
            self.parseLine(lig)
            barre.update(idx)
            
        barre.reset()
        print()
        self.oLog.info("--> {} Openair parsing zones".format(len(self.oOpenair)), outConsole=False)
        return


    def mergeOpenairAirspacesFile(self, sKeyFile:str, oFile:dict) -> None:
        if len(self.oAsCat.oGlobalCatalog)==0:                                                  #Ctrl ../..
            return
        if not oFile[poaffCst.cstSpExecute]:                                                    #Flag pour prise en compte du traitement de fichier
            return
        
        self.oOpenair:dict = {}     #Clean temporary dict
        fileOpenair = oFile[poaffCst.cstSpOutPath] + sKeyFile + poaffCst.cstSeparatorFileName +  poaffCst.cstAsAllOpenairFileName                  #Fichier comportant toutes les bordures de zones
        self.oLog.info("Openair airspaces consolidation file {0}: {1} --> {2}".format(sKeyFile, fileOpenair, oFile[poaffCst.cstSpProcessType]), outConsole=False)
        self.parseFile(fileOpenair)
        oGlobalCats = self.oAsCat.oGlobalCatalog[airspacesCatalog.cstKeyCatalogCatalog]          #Récupération de la liste des zones consolidés

        for sGlobalKey, oGlobalCat in oGlobalCats.items():                                       #Traitement du catalogue global complet
           if oGlobalCat[airspacesCatalog.cstKeyCatalogKeySrcFile]==sKeyFile:
               #not ("excludeAirspaceNotFfArea" in oGlobalCat):
               self.oLog.info("  --> Openair airspace consolidation {0}".format(sGlobalKey), outConsole=False)
               sUId = oGlobalCat["UId"]
               if sUId in self.oOpenair:
                   oAs:OpenairZone = self.oOpenair[sUId]
                   oAs.sGUId = sGlobalKey
                   #print(sGlobalKey, oRet)
                   self.oGlobalOpenair.update({sGlobalKey:oAs})
               else:
                   self.oLog.error("Openair airspace not found in file - {0}".format(sUId), outConsole=False)
        return
    
    