#!/usr/bin/env python3
import numpy as np

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


def truncateCoordinates(oGeo:dict, iDecimal=4) -> list:
    if oGeo[poaffCst.cstGeoType].lower()=="point":
        return                                      #Don't change this feature
    elif oGeo[poaffCst.cstGeoType].lower()=="linestring":
        oCoords:list = oGeo[poaffCst.cstGeoCoordinates]      #get coordinates of geometry
    elif oGeo[poaffCst.cstGeoType].lower()=="polygon":
        oCoords:list = oGeo[poaffCst.cstGeoCoordinates][0]   #get coordinates of geometry

    if len(oCoords)>1:
        oTruncCoords:list = np.around(oCoords, decimals=iDecimal)
        oNewCoords:list = []
        oPrevPoint:list = [-999,-999]                   #○Default value
        for oPt in oTruncCoords:
            if (oPt[0]!=oPrevPoint[0]) or (oPt[1]!=oPrevPoint[1]):
                oNewCoords.append([oPt[0],oPt[1]])
            oPrevPoint = oPt
        
        #print(oNewCoords)
        if oGeo[poaffCst.cstGeoType].lower()=="linestring":
            oGeo[poaffCst.cstGeoCoordinates] = oNewCoords
        elif oGeo[poaffCst.cstGeoType].lower()=="polygon":
            oGeo[poaffCst.cstGeoCoordinates][0] = oNewCoords

    return

def truncateGeojsonFeature(oGeoJSON:dict, iDecimal=4) -> None:
    sTitle = "GeoJSON airspaces truncate feature"
    if poaffCst.cstGeoFeatures in oGeoJSON:
        oFeatures:dict = oGeoJSON[poaffCst.cstGeoFeatures]
        barre = bpaTools.ProgressBar(len(oFeatures), 20, title=sTitle)
        idx = 0
        for oAs in oFeatures:
            idx+=1
            oAsGeo = oAs[poaffCst.cstGeoGeometry]                #get geometry
            truncateCoordinates(oAsGeo, iDecimal)       #define the new coordinates of this geometry
            barre.update(idx)
        barre.reset()
    return

def truncateGeojson(fileSrc:str, fileDst:str, iDecimal=4) -> None:
    oGeoJSON:dict = bpaTools.readJsonFile(fileSrc)
    truncateGeojsonFeature(oGeoJSON, iDecimal)
    bpaTools.writeJsonFile(fileDst, oGeoJSON)
    return    


if __name__ == '__main__':
    sPath = "../output/Tests/"
    #truncateGeojson(sPath + "__testAirspaces.geojson",             sPath + "___truncateFile1.geojson")
    #truncateGeojson(sPath + "__testAirspaces-ffvl-cfd.geojson",     sPath + "___truncateFile2.geojson")
    truncateGeojson(sPath + "__testAirspaces-freeflight.geojson",   sPath + "___truncateFile5.geojson",  iDecimal=5)
    truncateGeojson(sPath + "__testAirspaces-freeflight.geojson",   sPath + "___truncateFile4.geojson",  iDecimal=4)
    truncateGeojson(sPath + "__testAirspaces-freeflight.geojson",   sPath + "___truncateFile3.geojson",  iDecimal=3)
    truncateGeojson(sPath + "__testAirspaces-freeflight.geojson",   sPath + "___truncateFile2.geojson",  iDecimal=2)
    