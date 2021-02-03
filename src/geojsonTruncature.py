#!/usr/bin/env python3
import numpy as np
from copy import deepcopy

try:
    import bpaTools
except ImportError:
    ### Include local modules/librairies  ##
    import os
    import sys
    aixmParserLocalSrc  = "../../aixmParser/src/"
    module_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(module_dir, aixmParserLocalSrc))
    import bpaTools

import poaffCst

class GeojsonTrunc:

    def __init__(self, oLog=None, oGeo:dict=None)-> None:
        self.oLog:bpaTools.Logger = None
        if oLog:
            bpaTools.initEvent(__file__, oLog)
            self.oLog = oLog
        self.iDecimal = 3
        self.oInpGeo:dict = None                    #GeoJSON input data
        self.oOutGeo:dict = None                    #GeoJSON output data
        if oGeo:
            self.setGeo(oGeo)
            self.truncateGeojsonFeature()
        return

    def setGeo(self, oGeo:dict=None)-> None:
        if oGeo:
            #if self.oLog:
            #    self.oLog.info("setGeo()", outConsole=True)
            self.oInpGeo:dict = oGeo
            self.oOutGeo:dict = deepcopy(oGeo)
        return

    def truncateGeojsonFile(self, fileSrc:str, fileDst:str, iDecimal=3) -> None:
        if self.oLog:
            self.oLog.info("truncateGeojsonFile() - Read file - " + fileSrc, outConsole=False)
        oGeoJSON:dict = bpaTools.readJsonFile(fileSrc)
        if not oGeoJSON:
            self.oLog.warning("truncateGeojsonFile() - Empty source file - " + fileSrc, outConsole=False)
            return
        self.setGeo(oGeoJSON)
        self.iDecimal = iDecimal
        self.truncateGeojsonFeature()
        bpaTools.writeJsonFile(fileDst, self.oOutGeo)
        if self.oLog:
            self.oLog.info("truncateGeojsonFile() - Write file - " + fileDst, outConsole=False)
        return

    def truncateGeojsonFeature(self, oGeoJSON:dict=None) -> None:
        sTitle = "GeoJSON airspaces truncate"
        if not oGeoJSON:
            oGeoJSON = self.oOutGeo
        #if self.oLog:
        #    self.oLog.info(sTitle, outConsole=False)

        if poaffCst.cstGeoFeatures in oGeoJSON:
            oFeatures:dict = oGeoJSON[poaffCst.cstGeoFeatures]
            barre = bpaTools.ProgressBar(len(oFeatures), 20, title=sTitle)
            idx = 0
            for oAs in oFeatures:
                idx+=1
                oAsGeo = oAs[poaffCst.cstGeoGeometry]       #get geometry
                self.truncateCoordinates(oAsGeo)            #define the new coordinates of this geometry
                barre.update(idx)
            barre.reset()
        lSizeSrc:int = len(str(self.oInpGeo))
        lSizeDst:int = len(str(self.oOutGeo))
        lCompress:int = int((1-(lSizeDst/lSizeSrc))*100)
        sCompress:str = "GeoJSON compressed at {0}%".format(lCompress)
        if self.oLog:
            self.oLog.info(sCompress, outConsole=True)
        else:
            print("(i)Info: " + sCompress)
        return

    def truncateCoordinates(self, oGeo:dict) -> list:
        if oGeo[poaffCst.cstGeoType].lower()==(poaffCst.cstGeoPoint).lower():
            return                                                  #Don't change this feature
        elif oGeo[poaffCst.cstGeoType].lower()==(poaffCst.cstGeoLine).lower():
            oCoords:list = oGeo[poaffCst.cstGeoCoordinates]         #get coordinates of geometry
        elif oGeo[poaffCst.cstGeoType].lower()==(poaffCst.cstGeoPolygon).lower():
            oCoords:list = oGeo[poaffCst.cstGeoCoordinates][0]      #get coordinates of geometry

        if len(oCoords)>1:
            oTruncCoords:list = np.around(oCoords, decimals=self.iDecimal)
            oNewCoords:list = []
            oPrevPoint:list = [-999,-999]                           #Default value
            for oPt in oTruncCoords:
                if (oPt[0]!=oPrevPoint[0]) or (oPt[1]!=oPrevPoint[1]):
                    oNewCoords.append([oPt[0],oPt[1]])
                oPrevPoint = oPt

            if oGeo[poaffCst.cstGeoType].lower()==(poaffCst.cstGeoLine).lower():
                oGeo[poaffCst.cstGeoCoordinates] = oNewCoords
            elif oGeo[poaffCst.cstGeoType].lower()==(poaffCst.cstGeoPolygon).lower():
                oGeo[poaffCst.cstGeoCoordinates][0] = oNewCoords
        return


if __name__ == '__main__':
    sPath = "../output/Tests/"
    oTrunc = GeojsonTrunc()
    oTrunc.truncateGeojsonFile(sPath + "__testAirspaces.geojson",               sPath + "___truncateFile1.geojson")
    #oTrunc.truncateGeojsonFile(sPath + "__testAirspaces-freeflight.geojson",   sPath + "___truncateFile5.geojson",  iDecimal=5)
    #oTrunc.truncateGeojsonFile(sPath + "__testAirspaces-freeflight.geojson",   sPath + "___truncateFile4.geojson",  iDecimal=4)
    oTrunc.truncateGeojsonFile(sPath + "__testAirspaces-freeflight.geojson",   sPath + "___truncateFile3.geojson",  iDecimal=3)
    oTrunc.truncateGeojsonFile(sPath + "__testAirspaces-freeflight.geojson",   sPath + "___truncateFile2.geojson",  iDecimal=2)
