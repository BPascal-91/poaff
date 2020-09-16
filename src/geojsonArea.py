#!/usr/bin/env python3

from copy import deepcopy

import bpaTools
import poaffCst
import aixmReader
import airspacesCatalog
from airspacesCatalog import AsCatalog
import geoRefArea

cstGeoFeatures          = "features"
cstGeoProperties        = "properties"
cstGeoGeometry          = "geometry"
cstDeltaExtended        = "deltaExtended"
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
        self.saveGeoJsonAirspacesFile(sFile, "all", cstDeltaExtended)
        return

    def saveGeoJsonAirspacesFile(self, sFile:str, sContext:str="all", sAreaKey:str=None) -> None:
        oGeoFeatures:list = []
        oGeojson:dict = {}
        sContent:str = ""
        oNewHeader:dict = deepcopy(self.oAsCat.oGlobalCatalogHeader)

        #bpaTools.writeJsonFile(sFile + "-tmp.json", self.oGlobalGeoJSON)                       #Sérialisation pour mise au point
        oGlobalCats = self.oAsCat.oGlobalCatalog[airspacesCatalog.cstKeyCatalogCatalog]         #Récupération de la liste des zones consolidés
        sTitle = "GeoJSON save airspaces file - {0} / {1}".format(sContext, sAreaKey)
        barre = bpaTools.ProgressBar(len(oGlobalCats), 20, title=sTitle)
        idx = 0
        for sGlobalKey, oGlobalCat in oGlobalCats.items():                                      #Traitement du catalogue global complet
            idx+=1
            
            #if oGlobalCat["id"] in ["TMA16169","TMA16170"]:
            #    print(oGlobalCat["id"])
            
            #Filtrage des zones par typologie de sorties
            bIsInclude:bool = False
            oFinalCat:dict = oGlobalCat
            if   sContext == "ifr":
                bIsInclude = (not oGlobalCat["vfrZone"]) and (not oGlobalCat["groupZone"])
                sContent = "ifrZone"
                sFile = sFile.replace("-all", "-ifr")
            elif sContext == "vfr":
                bIsInclude = oGlobalCat["vfrZone"]
                #bIsInclude = bIsInclude or oGlobalCat.get("vfrZoneExt", False)		#Ne pas exporter l'extension de vol possible en VFR de 0m jusqu'au FL175/5334m
                sContent = "vfrZone"
                sFile = sFile.replace("-all", "-vfr")
            elif sContext == "ff":
                bIsIncludeLoc:bool = True
                if (sAreaKey == "geoFrench") and ("ExtOfFrensh" in oGlobalCat):
                    bIsIncludeLoc = not oGlobalCat["ExtOfFrensh"]      						#Pour Exclure toutes zones hors de France
                bIsInclude = bIsIncludeLoc and oGlobalCat["freeFlightZone"]
                #Relevage du plafond de carte pour certaines zones situées en France
                if "freeFlightZoneExt" in oGlobalCat:
                    aFrLocation = ["geoFrenchAlps", "geoFrenchVosgesJura", "geoFrenchPyrenees"]
                    bIsExtAlt4Loc:bool = False
                    for sLoc in aFrLocation:
                        if oGlobalCat[sLoc]:
                            bIsExtAlt4Loc = True
                            break
                    if bIsExtAlt4Loc:
                        bIsInclude = bIsInclude or (bIsIncludeLoc and oGlobalCat["freeFlightZoneExt"])
                sContent = "freeflightZone"
                sFile = sFile.replace("-all", "-freeflight")
            elif sContext == "cfd":
                bIsIncludeLoc:bool = True
                if "ExtOfFrensh" in oGlobalCat:
                    bIsIncludeLoc = not oGlobalCat["ExtOfFrensh"]      						#Pour Exclure toutes zones hors de France
                bIsInclude = bIsIncludeLoc and oGlobalCat["freeFlightZone"]
                if "use4cfd" in oGlobalCat:
                    bIsInclude = bIsInclude or oGlobalCat["use4cfd"]
                #Relevage systématique du plafond de la carte
                elif "freeFlightZoneExt" in oGlobalCat:
                    bIsInclude = bIsInclude or (bIsIncludeLoc and oGlobalCat["freeFlightZoneExt"])
                sContent = "freeflightZone for FFVL-CFD"
                sFile = sFile.replace("-all", "-ffvl-cfd")
                sAreaKey = ""
                #Single properties for CFD or FlyXC - {"name":"Agen1 119.15","category":"E","bottom":"2000F MSL","bottom_m":0,"top":"FL 65","color":"#bfbf40"}
                oSingleCat:dict = {}
                oSingleCat.update({"name":oGlobalCat["nameV"]})
                oSingleCat.update({"category":oGlobalCat["class"]})
                oSingleCat.update({"type":oGlobalCat["type"]})
                if "codeActivity" in oGlobalCat:    oSingleCat.update({"codeActivity":oGlobalCat["codeActivity"]})				
                oSingleCat.update({"bottom":aixmReader.getSerializeAlt(oGlobalCat,"Upp")})
                oSingleCat.update({"top":aixmReader.getSerializeAlt(oGlobalCat,"Low")})
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
            if sContext == "cfd":
                #06/08/2020, demande de Martin pour la sortie "CFD". Besoin d'une vision mondiale avec les zones interne située exclusivement en France métropole
                None   #Aucun filtrage geographique
            elif sAreaKey in ["geoFrenchNESW","geoCorse"] and oGlobalCat["id"]=="LTA13071":
                #Supprimer cett zone de la carte Corse --> [D] FRANCE 1 (LTA / id=LTA13071) [FL115-FL195]
                bIsArea = False
            elif bIsInclude and sAreaKey:
                if sAreaKey == cstWithoutLocation:
                    #Identification des zones non-retenues dans aucun des filtrages géographique paramétrés
                    bIsArea = False
                    for sAreaKey2 in self.oGeoRefArea.AreasRef.keys():
                        if sAreaKey2 in oGlobalCat:
                            bIsArea = bIsArea or oGlobalCat[sAreaKey2]
                        if bIsArea: break
                    bIsArea = not bIsArea
                elif sAreaKey == cstDeltaExtended:
                    if "deltaExt" in oGlobalCat:
                        bIsArea = oGlobalCat["deltaExt"]
                    else:
                        bIsArea = False
                elif sAreaKey in oGlobalCat:
                    bIsArea = oGlobalCat[sAreaKey]
                else:
                    bIsArea = False

            if bIsArea and bIsInclude and (sGlobalKey in self.oGlobalGeoJSON):
               oAs = self.oGlobalGeoJSON[sGlobalKey]
               oArea = {"type":"Feature", "properties":oFinalCat, "geometry":oAs}
               oGeoFeatures.append(oArea)
            barre.update(idx)
        barre.reset()

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
        sTitle = "GeoJSON airspaces consolidation - {0}".format(sKeyFile)
        self.oLog.info(sTitle + ": {0} --> {1}".format(fileGeoJSON, oFile[poaffCst.cstSpProcessType]), outConsole=False)
        self.makeGeojsonIndex(fileGeoJSON, sKeyFile)
        oGlobalCats = self.oAsCat.oGlobalCatalog[airspacesCatalog.cstKeyCatalogCatalog]          #Récupération de la liste des zones consolidés

        barre = bpaTools.ProgressBar(len(oGlobalCats), 20, title=sTitle)
        idx = 0
        for sGlobalKey, oGlobalCat in oGlobalCats.items():                                       #Traitement du catalogue global complet
            if oGlobalCat[airspacesCatalog.cstKeyCatalogKeySrcFile]==sKeyFile:
                idx+=1
                #self.oLog.info("  --> GeoJSON airspace consolidation {0}".format(sGlobalKey), outConsole=False)
                sUId = oGlobalCat["UId"]
                if sUId in self.oIdxGeoJSON:
                    oAs = self.oIdxGeoJSON[sUId]
                    oRet = self.oGeoRefArea.evalAreasRefInclusion(sGlobalKey, oAs)
                    oGlobalCat.update(oRet)
                    self.oGlobalGeoJSON.update({sGlobalKey:oAs})
                else:
                    self.oLog.error("GeoJSON airspace not found in file - {0}".format(sUId), outConsole=False)
            barre.update(idx)
        barre.reset()
        self.oAsCat.saveCatalogFiles()
        return

    def makeGeojsonIndex(self, fileGeoJSON:str, sKeyFile:str) -> None:
        sTitle = "GeoJSON airspaces make index - {0}".format(sKeyFile)
        self.oIdxGeoJSON = {}                                                                   #Clean previous data
        ofileGeoJSON:dict = bpaTools.readJsonFile(fileGeoJSON)                                  #Chargement des zones
        if cstGeoFeatures in ofileGeoJSON:
            oFeatures = ofileGeoJSON[cstGeoFeatures]
            barre = bpaTools.ProgressBar(len(oFeatures), 20, title=sTitle)
            idx = 0
            for oAs in oFeatures:
                oAsProp = oAs[cstGeoProperties]
                sUId = oAsProp["UId"]
                if "excludeAirspaceNotFfArea" in oAsProp:
                   None     #Ne pas inclure cette zone sans bordure
                else:
                    #self.oLog.debug("!!! Load index {0}".format(sUId), outConsole=False)
                    oAsGeo = oAs[cstGeoGeometry]
                    self.oIdxGeoJSON.update({sUId:oAsGeo})
            barre.update(idx)
        barre.reset()
        return

