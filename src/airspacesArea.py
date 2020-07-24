#!/usr/bin/env python3

import bpaTools
import poaffCst
import airspacesCatalog
import geoRefArea

cstGeoFeatures      = "features"
cstGeoProperties    = "properties"
cstGeoGeometry      = "geometry"


class AsArea:
    
    def __init__(self, oLog, oAsCat)-> None:
        bpaTools.initEvent(__file__, oLog)
        self.oLog                       = oLog
        self.oAsCat                     = oAsCat
        self.oIdxGeoJSON:dict           = {}
        self.oGlobalGeoJSON:dict        = {}
        self.oGeoRefArea                = geoRefArea.GeoRefArea()
        return
    
    def saveGeoJsonAirspacesFile(self, sFile:str) -> bool:
        oGeoFeatures:list = []
        oGeojson:dict = {}
        
        #bpaTools.writeJsonFile(sFile + "-tmp.json", self.oGlobalGeoJSON)                       #Sérialisation pour mise au point
        oGlobalCats = self.oAsCat.oGlobalCatalog[airspacesCatalog.cstKeyCatalogCatalog]         #Récupération de la liste des zones consolidés
        for sGlobalKey, oGlobalCat in oGlobalCats.items():                                      #Traitement du catalogue global complet
           if sGlobalKey in self.oGlobalGeoJSON:
               oAs = self.oGlobalGeoJSON[sGlobalKey]
               oArea = {"type":"Feature", "properties":oGlobalCat, "geometry":oAs}
               oGeoFeatures.append(oArea)

        oGeojson.update({"type":"FeatureCollection", "headerFile":self.oAsCat.oGlobalCatalogHeader, "features":oGeoFeatures})
        bpaTools.writeJsonFile(sFile, oGeojson)                                                 #Sérialisation du fichier
        return

    def mergeGeoJsonAirspacesFile(self, sKeyFile:str, oFile:dict) -> bool:
        if len(self.oAsCat.oGlobalCatalog)==0:                                                  #Ctrl ../..
            return
        if not oFile[poaffCst.cstSpExecute]:                                                    #Flag pour prise en compte du traitement de fichier
            return
        
        fileGeoJSON = oFile[poaffCst.cstSpOutPath] + sKeyFile + poaffCst.cstSeparatorFileName +  poaffCst.cstAsGeojsonFileName                  #Fichier comportant toutes les bordures de zones
        self.oLog.info("Airspaces consolidation file {0}: {1} --> {2}".format(sKeyFile, fileGeoJSON, oFile[poaffCst.cstSpProcessType]), outConsole=False)
        self.makeGeojsonIndex(fileGeoJSON)
        oGlobalCats = self.oAsCat.oGlobalCatalog[airspacesCatalog.cstKeyCatalogCatalog]          #Récupération de la liste des zones consolidés
    
        for sGlobalKey, oGlobalCat in oGlobalCats.items():                                       #Traitement du catalogue global complet
           if oGlobalCat[airspacesCatalog.cstKeyCatalogKeySrcFile]==sKeyFile:
               self.oLog.info("!!! Airspace consolidation {0}".format(sGlobalKey), outConsole=False)
               sUId = oGlobalCat["UId"]
               if sUId in self.oIdxGeoJSON:
                   oAs = self.oIdxGeoJSON[sUId]
                   oRet = self.oGeoRefArea.evalAreasRefInclusion(sGlobalKey, oAs)
                   #print(sGlobalKey, oRet)
                   oGlobalCat.update(oRet)
                   self.oGlobalGeoJSON.update({sGlobalKey:oAs})
               else:
                   self.oLog.error("Airspace not found in file - {0}".format(sUId), outConsole=False)
        return

    def makeGeojsonIndex(self, fileGeoJSON:str) -> bool:
        self.oIdxGeoJSON = {}                                                                   #Clean previous data
        ofileGeoJSON:dict = bpaTools.readJsonFile(fileGeoJSON)                                  #Chargement des zones
        if cstGeoFeatures in ofileGeoJSON:
            oFeatures = ofileGeoJSON[cstGeoFeatures]
            for oAs in oFeatures:
                oAsProp = oAs[cstGeoProperties]
                sUId = oAsProp["UId"]
                self.oLog.debug("!!! Load index {0}".format(sUId), outConsole=False)
                oAsGeo = oAs[cstGeoGeometry]
                self.oIdxGeoJSON.update({sUId:oAsGeo})
        return

