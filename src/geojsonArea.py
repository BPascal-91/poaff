#!/usr/bin/env python3
from copy import deepcopy

import bpaTools
import poaffCst
import aixmReader
import aixm2json
import airspacesCatalog
from airspacesCatalog import AsCatalog
import geoRefArea

cstFreeFlightZoneExt    = "zoneExt"
cstDeltaExtended        = "deltaExtended"
cstWithoutLocation      = "withoutGeoLocation"

class GeojsonArea:

    def __init__(self, oLog:bpaTools.Logger, oAsCat:AsCatalog, partialConstruct:bool)-> None:
        bpaTools.initEvent(__file__, oLog)
        self.oLog:bpaTools.Logger       = oLog                      #Log file
        self.oAsCat:AsCatalog           = oAsCat                    #Catalogue des zones
        self.oIdxGeoJSON:dict           = {}                        #Index de construction GeoJSON
        self.oGlobalGeoJSON:dict        = {}                        #Liste globale des zones
        self.oOutGeoJSON:dict           = {}                        #Sortie finale GeoJSON
        self.oGeoRefArea                = geoRefArea.GeoRefArea(partialConstruct)
        return

    def saveGeoJsonAirspacesFile4Area(self, sFile:str, sContext="ff") -> None:
        for sAreaKey in self.oGeoRefArea.AreasRef.keys():
            self.saveGeoJsonAirspacesFile(sFile, sContext, sAreaKey)
        #self.saveGeoJsonAirspacesFile(sFile, sContext, cstWithoutLocation)
        #self.saveGeoJsonAirspacesFile(sFile, "all", cstWithoutLocation)
        #self.saveGeoJsonAirspacesFile(sFile, "all", cstDeltaExtended)
        #self.saveGeoJsonAirspacesFile(sFile, "ff", cstFreeFlightZoneExt)
        return

    def saveGeoJsonAirspacesFile(self, sFile:str, sContext:str="all", sAreaKey:str=None) -> None:
        oGeoFeatures:list = []
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
                bIsInclude = bIsInclude or oGlobalCat.get("vfrZoneExt", False)		#Exporter l'extension de vol possible en VFR de 0m jusqu'au FL195/5944m
                sContent = "vfrZone"
                sFile = sFile.replace("-all", "-vfr")
            elif sContext == "ff":
                bIsIncludeLoc:bool = True
                if sAreaKey!=None:
                    sKey4Find:str = sAreaKey.replace("geo","ExtOf")
                    if sAreaKey[:9]=="geoFrench":                      #Spec for all french territories
                        sKey4Find = "ExtOfFrench"
                    if sKey4Find in oGlobalCat:
                        bIsIncludeLoc = not oGlobalCat[sKey4Find]       #Exclusion de zone
                bIsInclude = bIsIncludeLoc and oGlobalCat["freeFlightZone"]
                #Relevage du plafond de carte pour certaines zones situées en France
                if bIsIncludeLoc and ("freeFlightZoneExt" in oGlobalCat):
                    aFrLocation = ["geoFrenchAlps", "geoFrenchVosgesJura", "geoFrenchPyrenees"]
                    bIsExtAlt4Loc:bool = False
                    for sLoc in aFrLocation:
                        if oGlobalCat.get(sLoc, False):
                            bIsExtAlt4Loc = True
                            break
                    if bIsExtAlt4Loc:
                        bIsInclude = bIsInclude or (bIsIncludeLoc and oGlobalCat["freeFlightZoneExt"])
                sContent = "freeflightZone"
                sFile = sFile.replace("-all", "-freeflight")
            elif sContext == "cfd":
                bIsIncludeLoc:bool = True
                if "ExtOfFrench" in oGlobalCat:
                    bIsIncludeLoc = not oGlobalCat["ExtOfFrench"]      						#Pour Exclure toutes zones hors de France
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
                oSingleCat.update({"alt":"{0} {1}".format(aixmReader.getSerializeAlt(oGlobalCat), aixmReader.getSerializeAltM(oGlobalCat))})
                oSingleCat.update({"bottom":aixmReader.getSerializeAlt(oGlobalCat,"Low")})
                oSingleCat.update({"top":aixmReader.getSerializeAlt(oGlobalCat,"Upp")})
                oSingleCat.update({"bottom_m":oGlobalCat["lowerM"]})
                oSingleCat.update({"top_m":oGlobalCat["upperM"]})
                oSingleCat.update({"Ids":"GUId={0} UId={1} Id={2}".format(oGlobalCat.get("GUId","!"), oGlobalCat["UId"], oGlobalCat["id"])})
                if "exceptSAT" in oGlobalCat:       oSingleCat.update({"exceptSAT":oGlobalCat["exceptSAT"]})
                if "exceptSUN" in oGlobalCat:       oSingleCat.update({"exceptSUN":oGlobalCat["exceptSUN"]})
                if "exceptHOL" in oGlobalCat:       oSingleCat.update({"exceptHOL":oGlobalCat["exceptHOL"]})
                if "seeNOTAM" in oGlobalCat:        oSingleCat.update({"seeNOTAM":oGlobalCat["seeNOTAM"]})
                if "activationCode" in oGlobalCat:  oSingleCat.update({"activationCode":oGlobalCat["activationCode"]})
                if "activationDesc" in oGlobalCat:  oSingleCat.update({"activationDesc":oGlobalCat["activationDesc"]})
                if "timeScheduling" in oGlobalCat:  oSingleCat.update({"timeScheduling":oGlobalCat["timeScheduling"]})
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
                bIsArea = oGlobalCat.get("geoFrenchAll", False)        #Filtrage sur la totalité des territoires Français

            #Maintenir ou Supprimer la LTA-France1 (originale ou spécifique) des cartes non-concernées par le territoire Français --> [D] LTA FRANCE 1 (Id=LTA13071) [FL115-FL195]
            elif oGlobalCat["id"] in ["LTA13071","BpFrenchSS"]:
                if not sAreaKey in [None, "geoFrench","geoFrenchAll"]:
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
                    bIsArea = oGlobalCat.get("deltaExt", False)
                elif sAreaKey == cstFreeFlightZoneExt:
                    bIsArea = oGlobalCat.get("freeFlightZoneExt", False)
                elif sAreaKey in oGlobalCat:
                    bIsArea = oGlobalCat[sAreaKey]
                else:
                    bIsArea = False

            if not bIsArea:
                sKey4Find:str = sAreaKey.replace("geo","IncOf")         #test d'inclusion volontaire de la zone ?
                bIsArea = oGlobalCat.get(sKey4Find, False)

            if bIsArea and bIsInclude and (sGlobalKey in self.oGlobalGeoJSON):
                if sContext != "cfd":
                    aixm2json.addColorProperties(oFinalCat, self.oLog)      #Ajout des propriétés pour colorisation de la zone
                oAs = self.oGlobalGeoJSON[sGlobalKey]
                oArea = {poaffCst.cstGeoType:poaffCst.cstGeoFeature, poaffCst.cstGeoProperties:oFinalCat, poaffCst.cstGeoGeometry:oAs}
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
            self.oOutGeoJSON = {}  #Output reset
            self.oOutGeoJSON.update({poaffCst.cstGeoType:poaffCst.cstGeoFeatureCol, poaffCst.cstGeoHeaderFile:oNewHeader, poaffCst.cstGeoFeatures:oGeoFeatures})
            bpaTools.writeJsonFile(sFile, self.oOutGeoJSON)                                             #Sérialisation du fichier
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
        if poaffCst.cstGeoFeatures in ofileGeoJSON:
            oFeatures = ofileGeoJSON[poaffCst.cstGeoFeatures]
            barre = bpaTools.ProgressBar(len(oFeatures), 20, title=sTitle)
            idx = 0
            for oAs in oFeatures:
                idx+=1
                oAsProp = oAs[poaffCst.cstGeoProperties]
                sUId = oAsProp["UId"]
                #Depuis le 06/10 ; Préserver les zones particulières de type Point
                if oAs.get("excludeAirspaceNotFfArea", False)==True and oAs.get("geometryType", "")!="Point":
                   None     #Ne pas inclure cette zone sans bordure
                else:
                    #self.oLog.debug("!!! Load index {0}".format(sUId), outConsole=False)
                    oAsGeo = oAs[poaffCst.cstGeoGeometry]
                    self.oIdxGeoJSON.update({sUId:oAsGeo})
                barre.update(idx)
            barre.reset()
        return

