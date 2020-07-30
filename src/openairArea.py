#!/usr/bin/env python3

from copy import deepcopy

import bpaTools
import aixmReader
import poaffCst
import airspacesCatalog
from airspacesCatalog import AsCatalog
import geoRefArea

errLocalisationPoint:list = ["DP 45:00:00 N 005:00:00 W"]

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
        self.lUpper:int = None
        self.sLower:str = None
        self.lLower:int = None

        #Complementary data (Openair extended format include by 'aixmParser' software)
        self.sGUId:str = None
        self.sUId:str = None
        self.sId:str = None
        self.sAlt:str = None
        self.sDescr:int = None
        self.sActiv:str = None
        self.AExSAT:str = None
        self.AExSUN:str = None
        self.AExHOL:str = None
        self.ASeeNOTAM:str = None

        #---Abd--- Airspace Borders
        self.oBorder:list = list()
        return

    def isCorrectHeader(self) -> bool:
        ret = self.sClass  != None and \
              self.sName   != None and \
              self.sUpper  != None and \
              self.sLower  != None
        return ret

    def serializeArea(self, gpsType:str="") -> str:
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
        if self.AExSAT:     area += self.AExSAT + "\n"
        if self.AExSUN:     area += self.AExSUN + "\n"
        if self.AExHOL:     area += self.AExHOL + "\n"
        if self.ASeeNOTAM:  area += self.ASeeNOTAM + "\n"

        if gpsType=="-gpsWithoutTopo" and self.lUpper!=None:
            altM = self.lUpper
            altFT = int(float(altM+100) / aixmReader.CONST.ft)      #Surélévation du plafond de 100 mètres pour marge d'altitude
            area += "AH {0}FT AMSL\n".format(altFT)
        else:
            area += self.sUpper + "\n"

        if gpsType=="-gpsWithoutTopo" and self.lLower!=None:
            altM = self.lLower
            altFT = int(float(altM-100) / aixmReader.CONST.ft)      #Abaissement du plancher de 100 mètres pour marge d'altitude
            if altFT <= 0:
                area += "SFC\n"
            else:
                area += "AL {0}FT AMSL\n".format(altFT)
        else:
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
            self.saveOpenairAirspacesFile2(sFile, sContext, "-gpsWithTopo",    None,        sAreaKey)
            self.saveOpenairAirspacesFile2(sFile, sContext, "-gpsWithTopo", "exceptSAT",    sAreaKey)
            self.saveOpenairAirspacesFile2(sFile, sContext, "-gpsWithTopo", "exceptSUN",    sAreaKey)
            self.saveOpenairAirspacesFile2(sFile, sContext, "-gpsWithTopo", "exceptHOL",    sAreaKey)
            self.saveOpenairAirspacesFile2(sFile, sContext, "-gpsWithoutTopo", None,        sAreaKey)
            self.saveOpenairAirspacesFile2(sFile, sContext, "-gpsWithoutTopo", "exceptSAT", sAreaKey)
            self.saveOpenairAirspacesFile2(sFile, sContext, "-gpsWithoutTopo", "exceptSUN", sAreaKey)
            self.saveOpenairAirspacesFile2(sFile, sContext, "-gpsWithoutTopo", "exceptHOL", sAreaKey)
        else:    #context == "all", "ifr" or "vfr"
            self.saveOpenairAirspacesFile2(sFile, sContext, "-gpsWithTopo",    None,        sAreaKey)
            self.saveOpenairAirspacesFile2(sFile, sContext, "-gpsWithoutTopo", None,        sAreaKey)
        return

    def saveOpenairAirspacesFile2(self, sFile:str, sContext:str="all", gpsType:str="", exceptDay:str="", sAreaKey:str=None) -> None:
        oOutOpenair:list = []
        sContent:str = ""

        oGlobalHeader = self.oAsCat.oGlobalCatalog[airspacesCatalog.cstKeyCatalogHeaderFile]    #Récupération de l'entete du catalogue global
        oNewHeader:dict = deepcopy(self.oAsCat.oGlobalCatalogHeader)

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

            if bIsInclude==True and exceptDay:
                if exceptDay in oGlobalCat:               bIsInclude = False

            #Filtrage des zones par régionalisation
            bIsArea:bool = True
            if sAreaKey:
                if sAreaKey in oGlobalCat:
                    bIsArea = oGlobalCat[sAreaKey]
                else:
                    bIsArea = False

            if bIsArea and bIsInclude and (sGlobalKey in self.oGlobalOpenair):
                oAs:OpenairZone = self.oGlobalOpenair[sGlobalKey]
                if len(oAs.oBorder)==1:
                   None                     #Exclure tout les points fixes - or (oAs.oBorder[0]!=errLocalisationPoint)
                elif len(oAs.oBorder)==2 and oAs.oBorder[0][:4]!="V X=":
                   None                     #Exclure les doubles points fixes (DP.. + DP..) mais autoriser les cercles (V X=.. + DP..)
                else:
                    oOutOpenair.append(oAs)

        if gpsType=="-gpsWithTopo":
            sContent += " / " + gpsType[1:]
        elif gpsType=="-gpsWithoutTopo":
            sContent += " / " + gpsType[1:]
            sFile = sFile.replace("-gpsWithTopo", "-gpsWithoutTopo")
        else:
            sFile += "_err"

        if sAreaKey:
            sContent += " / " + sAreaKey
            sFile = sFile.replace(".txt", "-" + sAreaKey + ".txt")

        if exceptDay:
            ext4exceptDay = exceptDay.replace("except","for")
            sContent += " / " + ext4exceptDay
            sFile = sFile.replace(".txt", "-" + ext4exceptDay + ".txt")

        sMsg:str = " file {0} - {1} areas in map".format(sFile, len(oOutOpenair))
        if len(oOutOpenair) == 0:
            self.oLog.info("Unwritten" + sMsg, outConsole=False)
            bpaTools.deleteFile(sFile)
        else:
            self.oLog.info("Write" + sMsg, outConsole=False)
            oOp:OpenairArea = None
            sOutOpenair:str = ""
            oNewHeader.update({airspacesCatalog.cstKeyCatalogContent:sContent})
            oSrcFiles = oNewHeader.pop(airspacesCatalog.cstKeyCatalogSrcFiles)
            oNewHeader.update({airspacesCatalog.cstKeyCatalogNbAreas:len(oOutOpenair)})
            oNewHeader.update({airspacesCatalog.cstKeyCatalogSrcFiles:oSrcFiles})
            oTools = aixmReader.AixmTools(None)
            sHeader = oTools.makeHeaderOpenairFile(oNewHeader, oOutOpenair, sContext, gpsType, exceptDay, sAreaKey)
            sOutOpenair += sHeader
            for oOp in oOutOpenair:
                sOutOpenair += oOp.serializeArea(gpsType)

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
            self.oZone.sDescr = line
            return

        elif aLine[0] == "*AActiv":
            self.oZone.sActiv = line
            return

        elif aLine[0] == "*AExSAT":
            self.oZone.AExSAT = line
            return

        elif aLine[0] == "*AExSUN":
            self.oZone.AExSUN = line
            return

        elif aLine[0] == "*AExHOL":
            self.oZone.AExHOL = line
            return

        elif aLine[0] == "*ASeeNOTAM":
            self.oZone.ASeeNOTAM = line
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
        #print()
        #self.oLog.info("--> {} Openair parsing zones".format(len(self.oOpenair)), outConsole=False)
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
               #self.oLog.info("  --> Openair airspace consolidation {0}".format(sGlobalKey), outConsole=False)
               sUId = oGlobalCat["UId"]
               if "excludeAirspaceNotFfArea" in oGlobalCat:
                   None     #Ne pas inclure cette zone sans bordure
               elif sUId in self.oOpenair:
                   oAs:OpenairZone = self.oOpenair[sUId]
                   oAs.sGUId = sGlobalKey
                   if "ordinalUpperM" in oGlobalCat:
                       oAs.lUpper = oGlobalCat["upperM"]
                   if "ordinalLowerM" in oGlobalCat:
                       oAs.lLower = oGlobalCat["lowerM"]
                   self.oGlobalOpenair.update({sGlobalKey:oAs})
               else:
                   self.oLog.error("Openair airspace not found in file - {0}".format(sUId), outConsole=False)
        return

