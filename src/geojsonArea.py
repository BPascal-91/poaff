#!/usr/bin/env python3

from copy import deepcopy

import bpaTools
import poaffCst
import airspacesCatalog
from airspacesCatalog import AsCatalog
import geoRefArea

cstGeoFeatures          = "features"
cstGeoProperties        = "properties"
cstGeoGeometry          = "geometry"
cstWithoutLocation      = "withoutGeoLocation"

class GeojsonArea:

    def __init__(self, oLog, oAsCat)-> None:
        bpaTools.initEvent(__file__, oLog)
        self.oLog:bpaTools.Logger       = oLog      #Log file
        self.oAsCat:AsCatalog           = oAsCat    #Catalogue des zones
        self.oIdxGeoJSON:dict           = {}
        self.oGlobalGeoJSON:dict        = {}        #Liste globale des zones
        self.oGeoRefArea                = geoRefArea.GeoRefArea()
        return

    def saveGeoJsonAirspacesFile4Area(self, sFile:str, sContext="ff") -> None:
        for sAreaKey in self.oGeoRefArea.AreasRef.keys():
            self.saveGeoJsonAirspacesFile(sFile, sContext, sAreaKey)
        self.saveGeoJsonAirspacesFile(sFile, sContext, cstWithoutLocation)
        self.saveGeoJsonAirspacesFile(sFile, "all", cstWithoutLocation)
        return

    def saveGeoJsonAirspacesFile(self, sFile:str, sContext:str="all", sAreaKey:str=None) -> None:
        oGeoFeatures:list = []
        oGeojson:dict = {}
        sContent:str = ""
        oNewHeader:dict = deepcopy(self.oAsCat.oGlobalCatalogHeader)

        #bpaTools.writeJsonFile(sFile + "-tmp.json", self.oGlobalGeoJSON)                       #Sérialisation pour mise au point
        oGlobalCats = self.oAsCat.oGlobalCatalog[airspacesCatalog.cstKeyCatalogCatalog]         #Récupération de la liste des zones consolidés
        for sGlobalKey, oGlobalCat in oGlobalCats.items():                                      #Traitement du catalogue global complet

            #Filtrage des zones par typologie de sorties
            bIsInclude:bool = False
            oFinalCat:dict = oGlobalCat
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
            elif sContext == "cfd":
                bIsInclude = oGlobalCat["freeFlightZone"]
                sContent = "freeflightZone for FFVL-CFD"
                sAreaKey = ""                          #31/07/2020, demande de Martin - old "geoFrench"
                sFile = sFile.replace("-all", "-ffvl-cfd")
                aAlt = str(oGlobalCat["alt"]).split("/")
                sLow = aAlt[0][1:]
                sUpp = aAlt[1][:-1]
                #Single properties for CFD or FlyXC - {"name":"Agen1 119.15","category":"E","bottom":"2000F MSL","bottom_m":0,"top":"FL 65","color":"#bfbf40"}
                oSingleCat:dict = {}
                oSingleCat.update({"name":oGlobalCat["nameV"]})
                oSingleCat.update({"category":oGlobalCat["class"]})
                oSingleCat.update({"type":oGlobalCat["type"]})
                if "codeActivity" in oGlobalCat:    oSingleCat.update({"codeActivity":oGlobalCat["codeActivity"]})
                oSingleCat.update({"alt":oGlobalCat["alt"]})
                oSingleCat.update({"bottom":sLow})
                oSingleCat.update({"top":sUpp})
                oSingleCat.update({"bottom_m":oGlobalCat["lowerM"]})
                oSingleCat.update({"top_m":oGlobalCat["upperM"]})
                if "exceptSAT" in oGlobalCat:       oSingleCat.update({"exceptSAT":oGlobalCat["exceptSAT"]})
                if "exceptSUN" in oGlobalCat:       oSingleCat.update({"exceptSUN":oGlobalCat["exceptSUN"]})
                if "exceptHOL" in oGlobalCat:       oSingleCat.update({"exceptHOL":oGlobalCat["exceptHOL"]})
                if "seeNOTAM" in oGlobalCat:        oSingleCat.update({"seeNOTAM":oGlobalCat["seeNOTAM"]})
                if "activationCode" in oGlobalCat:  oSingleCat.update({"activationCode":oGlobalCat["activationCode"]})
                if "activationDesc" in oGlobalCat:  oSingleCat.update({"activationDesc":oGlobalCat["activationDesc"]})
                if "desc" in oGlobalCat:            oSingleCat.update({"desc":oGlobalCat["desc"]})
                oFinalCat = oSingleCat
            else:
                sContext = "all"
                sContent = "allZone"
                bIsInclude = True

            #Exclude area if unkwown coordonnees
            if bIsInclude and sContext!="all" and "excludeAirspaceNotCoord" in oGlobalCat:
                if oGlobalCat["excludeAirspaceNotCoord"]: bIsInclude = False

            #Filtrage des zones par régionalisation
            bIsArea:bool = True
            if sAreaKey:
                if sAreaKey == cstWithoutLocation:
                    #Identification des zones non-retenues dans aucun des filtrages géographique paramétrés
                    bIsArea = False
                    for sAreaKey2 in self.oGeoRefArea.AreasRef.keys():
                        if sAreaKey2 in oGlobalCat:
                            bIsArea = bIsArea or oGlobalCat[sAreaKey2]
                        if bIsArea: break
                    bIsArea = not bIsArea
                elif sAreaKey in oGlobalCat:
                    bIsArea = oGlobalCat[sAreaKey]
                else:
                    bIsArea = False

            if bIsArea and bIsInclude and (sGlobalKey in self.oGlobalGeoJSON):
               oAs = self.oGlobalGeoJSON[sGlobalKey]
               oArea = {"type":"Feature", "properties":oFinalCat, "geometry":oAs}
               oGeoFeatures.append(oArea)

        if sAreaKey:
            sContent += " / " + sAreaKey
            sFile = sFile.replace(".geojson", "-" + sAreaKey + ".geojson")

        sMsg:str = " file {0} - {1} areas in map"
        if len(oGeoFeatures) == 0:
            self.oLog.info("Unwritten" + sMsg.format(sFile, len(oGeoFeatures)), outConsole=False)
            bpaTools.deleteFile(sFile)
        else:
            self.oLog.info("Write" + sMsg.format(sFile, len(oGeoFeatures)), outConsole=False)
            oSrcFiles = oNewHeader.pop(airspacesCatalog.cstKeyCatalogSrcFiles)
            oNewHeader.update({airspacesCatalog.cstKeyCatalogContent:sContent})
            if sAreaKey in self.oGeoRefArea.AreasRef:
                sAreaDesc:str = self.oGeoRefArea.AreasRef[sAreaKey][2]
                oNewHeader.update({airspacesCatalog.cstKeyCatalogKeyAreaDesc:sAreaDesc})            
            del oNewHeader[airspacesCatalog.cstKeyCatalogNbAreas]
            oNewHeader.update({airspacesCatalog.cstKeyCatalogNbAreas:len(oGeoFeatures)})
            oNewHeader.update({airspacesCatalog.cstKeyCatalogSrcFiles:oSrcFiles})
            oGeojson.update({"type":"FeatureCollection", "headerFile":oNewHeader, "features":oGeoFeatures})
            bpaTools.writeJsonFile(sFile, oGeojson)                                             #Sérialisation du fichier
        return

    def mergeGeoJsonAirspacesFile(self, sKeyFile:str, oFile:dict) -> None:
        if len(self.oAsCat.oGlobalCatalog)==0:                                                  #Ctrl ../..
            return
        if not oFile[poaffCst.cstSpExecute]:                                                    #Flag pour prise en compte du traitement de fichier
            return

        fileGeoJSON = oFile[poaffCst.cstSpOutPath] + sKeyFile + poaffCst.cstSeparatorFileName +  poaffCst.cstAsAllGeojsonFileName                  #Fichier comportant toutes les bordures de zones
        self.oLog.info("GeoJSON airspaces consolidation file {0}: {1} --> {2}".format(sKeyFile, fileGeoJSON, oFile[poaffCst.cstSpProcessType]), outConsole=False)
        self.makeGeojsonIndex(fileGeoJSON)
        oGlobalCats = self.oAsCat.oGlobalCatalog[airspacesCatalog.cstKeyCatalogCatalog]          #Récupération de la liste des zones consolidés

        for sGlobalKey, oGlobalCat in oGlobalCats.items():                                       #Traitement du catalogue global complet
           if oGlobalCat[airspacesCatalog.cstKeyCatalogKeySrcFile]==sKeyFile:
               #self.oLog.info("  --> GeoJSON airspace consolidation {0}".format(sGlobalKey), outConsole=False)
               sUId = oGlobalCat["UId"]
               if sUId in self.oIdxGeoJSON:
                   oAs = self.oIdxGeoJSON[sUId]
                   oRet = self.oGeoRefArea.evalAreasRefInclusion(sGlobalKey, oAs)
                   if "externalOfFrench" in oGlobalCat:
                       sToken="geoFrench"
                       for sKey, oVal in oRet.items():
                           if sKey[:len(sToken)]==sToken:   
                               oRet.update({sKey:False})  #Exclusion forcée de certaines zones (très/trop proche) du territoire Français
                   oGlobalCat.update(oRet)
                   self.oGlobalGeoJSON.update({sGlobalKey:oAs})
               else:
                   self.oLog.error("GeoJSON airspace not found in file - {0}".format(sUId), outConsole=False)
        self.oAsCat.saveCatalogFiles()
        return

    def makeGeojsonIndex(self, fileGeoJSON:str) -> None:
        self.oIdxGeoJSON = {}                                                                   #Clean previous data
        ofileGeoJSON:dict = bpaTools.readJsonFile(fileGeoJSON)                                  #Chargement des zones
        if cstGeoFeatures in ofileGeoJSON:
            oFeatures = ofileGeoJSON[cstGeoFeatures]
            for oAs in oFeatures:
                oAsProp = oAs[cstGeoProperties]
                sUId = oAsProp["UId"]
                #self.oLog.debug("!!! Load index {0}".format(sUId), outConsole=False)
                oAsGeo = oAs[cstGeoGeometry]
                self.oIdxGeoJSON.update({sUId:oAsGeo})
        return

