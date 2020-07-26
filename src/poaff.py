#!/usr/bin/env python3

import os
import sys

### Include local modules/librairies  ##
aixmParserLocalSrc  = "../../aixmParser/src/"
module_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(module_dir, aixmParserLocalSrc))
import bpaTools
import aixmReader
from groundEstimatedHeight import GroundEstimatedHeight

from airspacesCatalog import AsCatalog
from airspacesArea import AsArea
import poaffCst

###  Context applicatif  ####
aixmParserVersion       = bpaTools.getVersionFile(aixmParserLocalSrc)
aixmParserId            = poaffCst.aixmParserAppName + " v" + aixmParserVersion
appName                 = bpaTools.getFileName(__file__)
appPath                 = bpaTools.getFilePath(__file__)
appVersion              = bpaTools.getVersionFile()
appId                   = appName + " v" + appVersion
outPath                 = appPath + "../output/"
logFile                 = outPath + "_" + appName + ".log"

###  Environnement applicatif  ###
poaffOutPath            = outPath + "_POAFF/"
globalCatalog           = poaffOutPath + poaffCst.cstReferentialPath + poaffCst.cstGlobalHeader + poaffCst.cstSeparatorFileName + poaffCst.cstCatalogFileName
globalAsGeojson         = poaffOutPath + poaffCst.cstGlobalHeader + poaffCst.cstSeparatorFileName +  poaffCst.cstAsAllGeojsonFileName

####  Liste des fichiers a traiter  ####
testMode = False     #True or  False
scriptProcessing = {
    "BPa-Test4Clean":       {poaffCst.cstSpExecute:    testMode , poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/Tests/",  poaffCst.cstSpSrcFile:"../input/BPa/99999999_BPa_Test4CleaningCatalog_aixm45.xml"},
    "BPa-Test4AppDelta":    {poaffCst.cstSpExecute:    testMode , poaffCst.cstSpProcessType:poaffCst.cstSpPtAddDelta, poaffCst.cstSpOutPath:"../output/Tests/",  poaffCst.cstSpSrcFile:"../input/BPa/99999999_BPa_Test4AppendDelta_aixm45.xml"},
    "EuCtrl":               {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/EuCtrl/", poaffCst.cstSpSrcFile:"../input/EuCtrl/20200618_aixm4.5_Eurocontrol-FR.xml"},
    "SIA":                  {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAddDelta, poaffCst.cstSpOutPath:"../output/SIA/",    poaffCst.cstSpSrcFile:"../input/SIA/20200618_aixm4.5_SIA-FR.xml"},
    "FFVP-Parcs":           {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/FFVP/",   poaffCst.cstSpSrcFile:"../input/FFVP/20200704_FFVP_ParcsNat_BPa_aixm45.xml"},
    "FFVP-Birds":           {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/FFVP/",   poaffCst.cstSpSrcFile:"../input/FFVP/20191214_FFVP_BirdsProtect_aixm45.xml"},
    "BPa-ParcCevennes":     {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/BPa/",    poaffCst.cstSpSrcFile:"../input/BPa/20190401_WPa_ParcCevennes_aixm45.xml"},
    "BPa-ParcChampagne":    {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/BPa/",    poaffCst.cstSpSrcFile:"../input/BPa/20200704_BPa_ParcsNat_ChampagneBourgogne_RegisF_aixm45.xml"},
    "BPa-Birds":            {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/BPa/",    poaffCst.cstSpSrcFile:"../input/BPa/20200510_BPa_FR-ZSM_Protection-des-rapaces_aixm45.xml"},
    "BPa-ZonesComp":        {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/BPa/",    poaffCst.cstSpSrcFile:"../input/BPa/20200705_BPa_ZonesComplementaires_aixm45.xml"}
}


####  Options d'appels pour création des fichiers  ####
#aArgs = [appName, "-Fall", "-Tall", aixmReader.CONST.optALL, aixmReader.CONST.optIFR, aixmReader.CONST.optVFR, aixmReader.CONST.optFreeFlight, aixmReader.CONST.optCleanLog]
#aArgs = [appName, "-Fall", aixmReader.CONST.typeAIRSPACES, aixmReader.CONST.optALL, aixmReader.CONST.optIFR, aixmReader.CONST.optVFR, aixmReader.CONST.optFreeFlight, aixmReader.CONST.optCleanLog]
aArgs = [appName, "-Fall", aixmReader.CONST.typeAIRSPACES, aixmReader.CONST.optALL, aixmReader.CONST.optCleanLog]


def poaffMergeFiles() -> None:

    #A/ Consolidation des catalogues (avec premier pré-filtrage qd nécessaire)
    bpaTools.deleteFile(globalCatalog)                                      #Purge du fichier
    oAsCat = AsCatalog(oLog)                                                #Gestion des catalogues
    for sKey, oFile in scriptProcessing.items():                            #Traitement des fichiers
        oAsCat.mergeJsonCatalogFile(sKey, oFile)                            #Consolidation des fichiers catalogues
    oAsCat.saveCatalogFiles(globalCatalog)                                  #Sérialisations du fichier

    #B/ Consolidation des espaces-éeriens
    bpaTools.deleteFile(globalAsGeojson)                                    #Purge du fichier
    oAsArea = AsArea(oLog, oAsCat)                                          #Gestion des zones
    for sKey, oFile in scriptProcessing.items():                            #Traitement des fichiers
        oAsArea.mergeGeoJsonAirspacesFile(sKey, oFile)                      #Consolidation des fichiers catalogues

    #Construction des sorties GeoJSON
    oAsArea.saveGeoJsonAirspacesFile(globalAsGeojson, "all")
    oAsArea.saveGeoJsonAirspacesFile(globalAsGeojson, "ifr")
    oAsArea.saveGeoJsonAirspacesFile(globalAsGeojson, "vfr")
    oAsArea.saveGeoJsonAirspacesFile(globalAsGeojson, "cfd")
    oAsArea.saveGeoJsonAirspacesFile(globalAsGeojson, "ff")
    oAsArea.saveGeoJsonAirspacesFile4Area(globalAsGeojson)
    
    return

def parseFile(sKey:str, oFile:dict) -> bool:
    bpaTools.createFolder(oFile[poaffCst.cstSpOutPath])                     #Init dossier de sortie
    aixmCtrl = aixmReader.AixmControler(oFile[poaffCst.cstSpSrcFile], oFile[poaffCst.cstSpOutPath], sKey, oLog)     #Init controler
    ret = aixmCtrl.execParser(oOpts)                                        #Execution des traitements
    return ret

def updateReferentials(sKey:str, oFile:dict) -> None:
    oGEH = GroundEstimatedHeight(oLog, oFile[poaffCst.cstSpOutPath], oFile[poaffCst.cstSpOutPath] + poaffCst.cstReferentialPath, sKey + "@")
    oGEH.parseUnknownGroundHeightRef()                                      #Execution des traitements
    return

def poaffGenerateFiles(sMsg:str=None) -> None:
    if sMsg!=None:
        oLog.warning("{0}".format(sMsg), outConsole=True)
    oLog.writeCommandLine(aArgs)                                            #Trace le contexte d'execution
    oLog.info("Loading module - {0}".format(aixmParserId), outConsole=True)

    for sKey, oFile in scriptProcessing.items():                            #Traitement des fichiers
        if oFile[poaffCst.cstSpExecute]:                                    #Flag prise en compte du fichier
            iPrevErr = oLog.CptCritical + oLog.CptError                     #Nombre d'erreurs en pré-traitements
            parseFile(sKey, oFile)                                          #Creation des fichiers
            iActErr = oLog.CptCritical + oLog.CptError                      #Nombre d'erreurs en post-traitements
            if iActErr!=iPrevErr:                                           #Si écart constaté
                updateReferentials(sKey, oFile)                             #Forcer mise à jour des référentiels d'altitudes
    return


if __name__ == '__main__':
    sCallingContext = None

    bpaTools.createFolder(outPath)                                          #Initialisation
    bpaTools.createFolder(poaffOutPath)                                     #Initialisation
    bpaTools.createFolder(poaffOutPath + poaffCst.cstReferentialPath)       #Initialisation

    oOpts = bpaTools.getCommandLineOptions(aArgs)                           #Arguments en dictionnaire
    oLog = bpaTools.Logger(appId, logFile, poaffCst.callingContext, poaffCst.linkContext, isSilent=bool(aixmReader.CONST.optSilent in oOpts))
    if aixmReader.CONST.optCleanLog in oOpts:
        oLog.resetFile()                                                    #Clean du log si demandé

    #--------- creation des fichiers unitaires ----------
    poaffGenerateFiles()                                                    #Creation des fichiers
    if (oLog.CptCritical + oLog.CptError) > 0:
        oLog.resetFile()                                                    #Clean du log
        sCallingContext = "Forced reload by second phase"
        poaffGenerateFiles(sCallingContext)                                 #Seconde tentative de creation des fichiers

    if (oLog.CptCritical + oLog.CptError) > 0:
        print()
        oLog.critical("Abort treatment - Show errors in log file", outConsole=True)
    else:
        poaffMergeFiles()                                                   #Consolidation des fichiers
        #if not(testMode):
        #    oWeb = PoaffWebPage(oLog, outPath)
        #    oWeb.createPoaffWebPage(None)                                   #Preparation pour publication
        #    #oWeb.createPoaffWebPage("20200715_")                           #Pour révision d'une publication

    print()
    if sCallingContext!=None:
        oLog.warning("{0}".format(sCallingContext), outConsole=True)
    oLog.Report()
    oLog.closeFile()

