#!/usr/bin/env python3
from copy import deepcopy

aixmParserLocalSrc  = "../../../aixmParser/src/"
try:
    import bpaTools
except ImportError:
    ### Include local modules/librairies  ##
    import os, sys
    module_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(module_dir, aixmParserLocalSrc))
    import bpaTools

import poaffCst
import airspacesCatalog
from airspacesCatalog import AsCatalog
from openairArea import OpenairZone, OpenairArea



###  Context applicatif  ####
appName                 = bpaTools.getFileName(__file__)
appPath                 = bpaTools.getFilePath(__file__)
appVersion              = "1.0.0"
appId                   = appName + " v" + appVersion
outPath                 = appPath + "../../output/"
inPath                  = appPath + "../../input/"
logFile                 = outPath + "_" + appName + ".log"

###  Environnement applicatif  ###
poaffOutPath            = outPath + poaffCst.cstPoaffOutPath


if __name__ == '__main__':
    oLog = bpaTools.Logger(appId, logFile, poaffCst.callingContext, poaffCst.linkContext, isSilent=False)                                                   #Clean du log si demandé
    oLog.resetFile()

    sHeadFileDate:str      = "{0}_".format(bpaTools.getDateNow())
    #sSrcFile = inPath + "BPa/French-LTA/20201214_airspaces-freeflight-gpsWithTopo-geoFrench.txt"
    sSrcFile = inPath + "BPa/French-LTA/20210103_LTA-gpsWithTopo-geoFrench.txt"
    sDstFile = inPath + "BPa/French-LTA/"+ sHeadFileDate + "LTA-FrenchSurfaceS_BPa.txt"

    oAsCat:AsCatalog = airspacesCatalog.AsCatalog(oLog)             #Catalogue de zone vide
    oOpArea = OpenairArea(oLog, oAsCat, False)                      #Gestion des zones
    oOpArea.parseFile(sSrcFile, "BPa-French-LTA")                   #Analyse du contenu Openair

    oZone:OpenairZone = None      #Zone
    #for sUId, oZone in oOpArea.oOpenair.items():
    #    oLog.info("(sUId={0}) {1} - {2}".format(sUId, oZone.sClass, oZone.sName), outConsole=False)

    #Extraction complète de la surface S couvrant de la France métropolitaine
    oFrenchSurfaceS:OpenairZone = deepcopy(oOpArea.oOpenair["1566267"])
    oLog.info("frenchSurfaceS (sUId={0}) {1} - {2}".format(oFrenchSurfaceS.sUId, oFrenchSurfaceS.sClass, oFrenchSurfaceS.sName), outConsole=True)
    sFirstPointSS:str = oFrenchSurfaceS.oBorder[0]
    sLastPointSS:str  = oFrenchSurfaceS.oBorder[-1]
    if sFirstPointSS != sLastPointSS:                   #Garantir que la surface S initiale est pleinement refermée
        oFrenchSurfaceS.oBorder.append("**** (BPa) Close 'Surface S area'")
        oFrenchSurfaceS.oBorder.append(sFirstPointSS)

    #Traitement de toutes les zones 'E' afin de supprimer leurs surfaces de la zone initiale 'oFrenchSurfaceS'
    sTokenName:str = "AN LTA FRANCE"
    for sUId, oZone in oOpArea.oOpenair.items():
        #Ne filtrer que les LTA France classifiées en 'E'
        if (oZone.sName[:len(sTokenName)]==sTokenName) and (oZone.sClass=="AC E"):
            oLog.info("suppress area - (sUId={0}) {1} - {2}".format(sUId, oZone.sClass, oZone.sName), outConsole=True)
            oFrenchSurfaceS.oBorder.append("**** (BPa) Suppress area - (sUId={0}) {1} - {2}".format(sUId, oZone.sClass, oZone.sName))
            sFirstPoint:str = oZone.oBorder[0]
            sLastPoint:str  = oZone.oBorder[-1]
            if sFirstPointSS != sLastPointSS:            #Garantir que la zone est pleinement refermée
                #oZone.oBorder.append("**** (BPa) Close area")
                oZone.oBorder.append(sFirstPoint)
            #Ne filtrer que les POINTs (exclure les Cercles et/ou Arcs)
            sTokenLineType:str = "DP "
            if oZone.sUId=="7997009":       #(sUId=7997009) AC E - AN LTA FRANCE 4.20 Lower(3000FT AGL-FL115)
                oList:list = oZone.oBorder
            else:
                oList:list = reversed(oZone.oBorder)
            for sPt in oList:
                if sPt[:len(sTokenLineType)]==sTokenLineType:
                    oFrenchSurfaceS.oBorder.append(sPt)
            oFrenchSurfaceS.oBorder.append("**** (BPa) Return start of 'Surface S area'")
            oFrenchSurfaceS.oBorder.append(sFirstPointSS)

    #Construction de la nouvelle 'Surface S France' avec suppression des zones d'extentions de vols (au delà du FL115)
    sDescription:str = "(Pascal Bazile) Tracé spécifique de la 'Surface S en France', construit sur la base de l'ensemble des tracés officiels des 'LTA FRANCE'"
    sNewFrenchSurfaceS:str = ""
    sNewFrenchSurfaceS += "*" * 50 + "\n"
    sNewFrenchSurfaceS += "*   software - (" + appId + ")\n"
    sNewFrenchSurfaceS += "*   created - " + bpaTools.getNowISO() + "\n"
    sNewFrenchSurfaceS += "*   content - freeflightZone / gpsWithTopo / geoFrench" + "\n"
    sNewFrenchSurfaceS += "*   areaDescription - LTA - Surface 'S' de la France métropolitaine" + "\n"
    sNewFrenchSurfaceS += "*   srcFile:" + "\n"
    sNewFrenchSurfaceS += "*      " + sSrcFile + "\n"
    sNewFrenchSurfaceS += "*   (i)Information - " + sDescription + "\n"
    sNewFrenchSurfaceS += "*   /!\Warning - 'gpsWithTopo' - Cartographie pour XCsoar / LK8000 / XCTrack / FlyMe / Compass / Syride ; et tout autres appareils/logiciels AVEC Carte-Topographique (en capacité de connaître les altitudes terrain)" + "\n"
    sNewFrenchSurfaceS += "*" * 50 + "\n"
    sNewFrenchSurfaceS += "\n"
    sNewFrenchSurfaceS += oFrenchSurfaceS.sClass + "\n"
    sNewFrenchSurfaceS += "AN LTA FRANCE 1 [BPa - 'Surface S' en France]" + "\n"
    sNewFrenchSurfaceS += "*AUID GUId=! UId=! Id=BpFrenchSS" + "\n"
    sNewFrenchSurfaceS += "*ADescr " + sDescription + "\n"
    sNewFrenchSurfaceS += "*AActiv [H24]" + "\n"
    sNewFrenchSurfaceS += oFrenchSurfaceS.sUpper + "\n"
    sNewFrenchSurfaceS += oFrenchSurfaceS.sLower + "\n"
    for sPt in oFrenchSurfaceS.oBorder:
        sNewFrenchSurfaceS += "{0}\n".format(sPt)
    bpaTools.writeTextFile(sDstFile, sNewFrenchSurfaceS)  #Sérialisation du fichier

    oLog.Report()
    oLog.closeFile()

