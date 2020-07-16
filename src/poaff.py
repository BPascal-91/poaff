#!/usr/bin/env python3

import os
import sys
import shutil

### Include local modules/librairies
aixmParserLocalSrc  = "../../aixmParser/src/"
module_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(module_dir, aixmParserLocalSrc))
import bpaTools
import aixmReader
from groundEstimatedHeight import GroundEstimatedHeight


### Context applicatif
aixmParserAppName   = "aixmParser"
aixmParserVersion   = bpaTools.getVersionFile(aixmParserLocalSrc)
aixmParserId        = aixmParserAppName + " v" + aixmParserVersion
appName             = bpaTools.getFileName(__file__)
appPath             = bpaTools.getFilePath(__file__)
appVersion          = bpaTools.getVersionFile()
appId               = appName + " v" + appVersion
outPath             = appPath + "../output/"
logFile             = outPath + "_" + appName + ".log"
poaffWebPath        = outPath + "_POAFF_www/"
cfdWebPath          = outPath + "_CFD_www/"
bpaTools.createFolder(outPath)                                      #Init dossier de sortie

callingContext      = "Paragliding-OpenAir-FrenchFiles"             #Your app calling context
linkContext         = "http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/"


####  Liste des fichiers disponibles  ####
cstID = "ID"
cstSrcFile = "srcFile"
cstOutPath = "outPath"
scriptProcessing = {
    "BPa-ParcCevennes": {cstOutPath:"../output/BPa/", cstSrcFile:"../input/BPa/20190401_WPa_ParcCevennes_aixm45.xml"},
    "BPa-ParcChampagne": {cstOutPath:"../output/BPa/", cstSrcFile:"../input/BPa/20200704_BPa_ParcsNat_ChampagneBourgogne_RegisF_aixm45.xml"},
    "BPa-Birds":        {cstOutPath:"../output/BPa/", cstSrcFile:"../input/BPa/20200510_BPa_FR-ZSM_Protection-des-rapaces_aixm45.xml"},
    "BPa-ZonesComp":    {cstOutPath:"../output/BPa/", cstSrcFile:"../input/BPa/20200705_BPa_ZonesComplementaires_aixm45.xml"},
    "FFVP-Parcs":       {cstOutPath:"../output/FFVP/", cstSrcFile:"../input/FFVP/20200704_FFVP_ParcsNat_BPa_aixm45.xml"},
    "FFVP-Birds":       {cstOutPath:"../output/FFVP/", cstSrcFile:"../input/FFVP/20191214_FFVP_BirdsProtect_aixm45.xml"},
    #"SIA":              {cstOutPath:"../output/SIA/", cstSrcFile:"../input/SIA/20200618_aixm4.5_SIA-FR.xml"},
    "EuCtrl":           {cstOutPath:"../output/EuCtrl/", cstSrcFile:"../input/EuCtrl/20200618_aixm4.5_Eurocontrol-FR.xml"}
}
    

####  Options d'appels  ####
#aArgs = [appName, "-Fall", "-Tall", aixmReader.CONST.optALL, aixmReader.CONST.optIFR, aixmReader.CONST.optVFR, aixmReader.CONST.optFreeFlight, aixmReader.CONST.optCleanLog]
aArgs = [appName, "-Fall", aixmReader.CONST.typeAIRSPACES, aixmReader.CONST.optALL, aixmReader.CONST.optIFR, aixmReader.CONST.optVFR, aixmReader.CONST.optFreeFlight, aixmReader.CONST.optCleanLog]


def parseFile(sKey:str, oFile:dict) -> bool:
    bpaTools.createFolder(oFile["outPath"])                         #Init dossier de sortie
    aixmCtrl = aixmReader.AixmControler(oFile["srcFile"], oFile["outPath"], sKey, oLog)     #Init controler
    ret = aixmCtrl.execParser(oOpts)                                #Execution des traitements
    return ret

def updateReferentials(sKey:str, oFile:dict) -> None:
    oGEH = GroundEstimatedHeight(oLog, oFile["outPath"], oFile["outPath"] + "referentials/", sKey + "@")
    oGEH.parseUnknownGroundHeightRef()                              #Execution des traitements
    return

def poaffGenerateFiles(sMsg:str=None) -> None:
    if sMsg!=None:
        oLog.warning("{0}".format(sMsg), outConsole=True)
    oLog.writeCommandLine(aArgs)                                    #Trace le contexte d'execution
    oLog.info("Loading module - {0}".format(aixmParserId), outConsole=True)
    
    #### Traitement des fichiers  ####
    for sKey, oFile in scriptProcessing.items():
        iPrevErr = oLog.CptCritical + oLog.CptError
        parseFile(sKey, oFile)
        iActErr = oLog.CptCritical + oLog.CptError
        if iActErr!=iPrevErr:
            updateReferentials(sKey, oFile)    
    return

def moveFile(sSrcPath:str, sSrcFile:str, sCpyFileName:str, sPoaffWebPageBuffer, sToken:str) -> None:
    sCpyFile = "{0}{1}{2}".format(poaffWebPath, "files/", sCpyFileName)
    shutil.copyfile(sSrcPath + sSrcFile, sCpyFile)
    oLog.info("Move file : {0} --> {1}".format(sSrcFile, sCpyFileName), outConsole=False)
    return sPoaffWebPageBuffer.replace(sToken, sCpyFileName)
    
def createPoaffWebPage() -> None:   
    sTemplateWebPage:str = "__template__Index-Main.htm"
    sNewWebPage:str = "index.htm"
    sHeadFileDate:str = "{0}_".format(bpaTools.getDateNow())
    
    #### 1/ repository for POAFF
    fTemplate = open(poaffWebPath + sTemplateWebPage, "r", encoding="utf-8", errors="ignore")
    sPoaffWebPageBuffer = fTemplate.read()
    fTemplate.close()

    fVerionCatalog = open(poaffWebPath + "files/LastVersionsCatalog_BPa.txt", "w", encoding="utf-8", errors="ignore")
    fVerionCatalog.write("Fichier;Date de transformation;Date d'origine de la source;Description\n")
    
    # Openair gpsWithTopo files 
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/", "EuCtrl@airspaces-all-gpsWithTopo.txt", sHeadFileDate + "airspaces-all-gpsWithTopo.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-all-gpsWithTopo@@")
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/", "EuCtrl@airspaces-ifr-gpsWithTopo.txt", sHeadFileDate + "airspaces-ifr-gpsWithTopo.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-ifr-gpsWithTopo@@")
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/", "EuCtrl@airspaces-vfr-gpsWithTopo.txt", sHeadFileDate + "airspaces-vfr-gpsWithTopo.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-vfr-gpsWithTopo@@")
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithTopo.txt", sHeadFileDate + "airspaces-freeflight-gpsWithTopo.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-freeflight-gpsWithTopo@@")
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithTopo-forSAT.txt", sHeadFileDate + "airspaces-freeflight-gpsWithTopo-forSAT.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-freeflight-gpsWithTopo-forSAT@@")
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithTopo-forSUN.txt", sHeadFileDate + "airspaces-freeflight-gpsWithTopo-forSUN.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-freeflight-gpsWithTopo-forSUN@@")
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithTopo-forHOL.txt", sHeadFileDate + "airspaces-freeflight-gpsWithTopo-forHOL.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-freeflight-gpsWithTopo-forHOL@@")
    
    # LastVersion - (similar files of Openair gpsWithTopo files)
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithTopo.txt", "LastVersion_FR-BPa4XCsoar.txt", sPoaffWebPageBuffer, "@@file@@Openair-LastVersion-gpsWithTopo@@")
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithTopo-forSAT.txt", "LastVersion_FR-BPa4XCsoar-forSAT.txt", sPoaffWebPageBuffer, "@@file@@Openair-LastVersion-gpsWithTopo-forSAT@@")
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithTopo-forSUN.txt", "LastVersion_FR-BPa4XCsoar-forSUN.txt", sPoaffWebPageBuffer, "@@file@@Openair-LastVersion-gpsWithTopo-forSUN@@")
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithTopo-forHOL.txt", "LastVersion_FR-BPa4XCsoar-forHOL.txt", sPoaffWebPageBuffer, "@@file@@Openair-LastVersion-gpsWithTopo-forHOL@@")
    fVerionCatalog.write("LastVersion_FR-BPa4XCsoar.txt;" + sHeadFileDate[:-1] + ";" + sHeadFileDate[:-1] + ";OpenAir France spécifique pour XCsoar, LK8000, XCTrack, FlyMe, Compass ou Syride\n")
    fVerionCatalog.write("LastVersion_FR-BPa4XCsoar-forSAT.txt;" + sHeadFileDate[:-1] + ";" + sHeadFileDate[:-1] + ";OpenAir France spécifiquement utilisable les SAMEDIs ; pour XCsoar, LK8000, XCTrack, FlyMe, Compass ou Syride\n")
    fVerionCatalog.write("LastVersion_FR-BPa4XCsoar-forSUN.txt;" + sHeadFileDate[:-1] + ";" + sHeadFileDate[:-1] + ";OpenAir France spécifiquement utilisable les DIMANCHEs ; pour XCsoar, LK8000, XCTrack, FlyMe, Compass ou Syride\n")
    fVerionCatalog.write("LastVersion_FR-BPa4XCsoar-forHOL.txt;" + sHeadFileDate[:-1] + ";" + sHeadFileDate[:-1] + ";OpenAir France spécifiquement utilisable les Jours-Fériés ; pour XCsoar, LK8000, XCTrack, FlyMe, Compass ou Syride\n")

    # Openair gpsWithoutTopo files 
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithoutTopo.txt", sHeadFileDate + "airspaces-freeflight-gpsWithoutTopo.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-freeflight-gpsWithoutTopo@@")
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithoutTopo-forSAT.txt", sHeadFileDate + "airspaces-freeflight-gpsWithoutTopo-forSAT.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-freeflight-gpsWithoutTopo-forSAT@@")
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithoutTopo-forSUN.txt", sHeadFileDate + "airspaces-freeflight-gpsWithoutTopo-forSUN.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-freeflight-gpsWithoutTopo-forSUN@@")
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithoutTopo-forHOL.txt", sHeadFileDate + "airspaces-freeflight-gpsWithoutTopo-forHOL.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-freeflight-gpsWithoutTopo-forHOL@@")

    # GeoJSON files
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/", "EuCtrl@airspaces-all.geojson", sHeadFileDate + "airspaces-all.geojson", sPoaffWebPageBuffer, "@@file@@GeoJSON-airspaces-all@@")
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/", "EuCtrl@airspaces-ifr.geojson", sHeadFileDate + "airspaces-ifr.geojson", sPoaffWebPageBuffer, "@@file@@GeoJSON-airspaces-ifr@@")
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/", "EuCtrl@airspaces-vfr.geojson", sHeadFileDate + "airspaces-vfr.geojson", sPoaffWebPageBuffer, "@@file@@GeoJSON-airspaces-vfr@@")
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight.geojson", sHeadFileDate + "airspaces-freeflight.geojson", sPoaffWebPageBuffer, "@@file@@GeoJSON-airspaces-freeflight@@")
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight.geojson", "LastVersion_airspaces-freeflight.geojson", sPoaffWebPageBuffer, "@@file@@GeoJSON-LastVersion-freeflight@@")
    fVerionCatalog.write("LastVersion_airspaces-freeflight.geojson;" + sHeadFileDate[:-1] + ";" + sHeadFileDate[:-1] + ";GeoJSON spécifiquement utilisable pour la CFD\n")

    # Calalog files
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/referentials/", "EuCtrl@airspacesCatalog.csv", sHeadFileDate + "airspacesCatalog.csv", sPoaffWebPageBuffer, "@@file@@CSV-airspacesCatalog@@")
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/referentials/", "EuCtrl@airspacesCatalog.json", sHeadFileDate + "airspacesCatalog.json", sPoaffWebPageBuffer, "@@file@@JSON-airspacesCatalog@@")
    fVerionCatalog.write(sHeadFileDate + "airspacesCatalog.csv;" + sHeadFileDate[:-1] + ";" + sHeadFileDate[:-1] + ";Catalogue des espaces-aériens au format CSV\n")
    fVerionCatalog.write(sHeadFileDate + "airspacesCatalog.json;" + sHeadFileDate[:-1] + ";" + sHeadFileDate[:-1] + ";Catalogue des espaces-aériens au format JSON\n")
    
    fVerionCatalog.close()


    #### 2/ repository for CFD
    # GeoJSON and Catalog files
    shutil.copyfile(outPath + "EuCtrl/EuCtrl@airspaces-all.geojson", cfdWebPath + "/airspaces-all.geojson")
    shutil.copyfile(outPath + "EuCtrl/EuCtrl@airspaces-ifr.geojson", cfdWebPath + "/airspaces-ifr.geojson")
    shutil.copyfile(outPath + "EuCtrl/EuCtrl@airspaces-vfr.geojson", cfdWebPath + "/airspaces-vfr.geojson")
    shutil.copyfile(outPath + "EuCtrl/EuCtrl@airspaces-freeflight.geojson", cfdWebPath + "/airspaces-freeflight.geojson")
    shutil.copyfile(outPath + "EuCtrl/referentials/EuCtrl@airspacesCatalog.csv", cfdWebPath + "/airspacesCatalog.csv")
    shutil.copyfile(outPath + "EuCtrl/referentials/EuCtrl@airspacesCatalog.json", cfdWebPath + "/airspacesCatalog.json")
    
    
    #### 3/ creating html main page
    sMsg = "Creating Web file - {}".format(sNewWebPage)
    oLog.info(sMsg, outConsole=True)
    fWebPageIndex = open(poaffWebPath + sNewWebPage, "w", encoding="utf-8", errors="ignore")
    fWebPageIndex.write(sPoaffWebPageBuffer)
    fWebPageIndex.close()
    shutil.copyfile(poaffWebPath + sNewWebPage, poaffWebPath + sHeadFileDate + sNewWebPage)
    
    #### 4/ securisation and move to html main page
    sFileMoveTo = poaffWebPath + "/__template__Index-MoveP2P.htm"
    shutil.copyfile(sFileMoveTo, poaffWebPath + "files/index.htm")
    shutil.copyfile(sFileMoveTo, poaffWebPath + "files/res/index.htm")
    shutil.copyfile(sFileMoveTo, poaffWebPath + "img/index.htm")
    shutil.copyfile(sFileMoveTo, poaffWebPath + "palette01/index.htm")
    shutil.copyfile(sFileMoveTo, poaffWebPath + "palette01/img/index.htm")
    
    return


if __name__ == '__main__':
    ####  Préparation d'appel ####
    oOpts = bpaTools.getCommandLineOptions(aArgs)                   #Arguments en dictionnaire
    oLog = bpaTools.Logger(appId, logFile, callingContext, linkContext, isSilent=bool(aixmReader.CONST.optSilent in oOpts))
    if aixmReader.CONST.optCleanLog in oOpts:
        oLog.resetFile()                                            #Clean du log si demandé

    #--------- creation des fichiers ----------
    sCallingContext = None
    """
    poaffGenerateFiles()
    if (oLog.CptCritical + oLog.CptError) > 0:
        oLog.resetFile()                                            #Clean du log
        sCallingContext = "Forced reload by second phase"
        poaffGenerateFiles(sCallingContext)
    """
    
    #--------- preparation de la mise a jour du site Web ----------
    createPoaffWebPage()

    print()
    if sCallingContext!=None:
        oLog.warning("{0}".format(sCallingContext), outConsole=True)
    oLog.Report()
    oLog.closeFile()

