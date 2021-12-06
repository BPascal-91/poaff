#!/usr/bin/env python3
import os, sys
#import zipfile

aixmParserLocalSrc  = "../../aixmParser/src/"
try:
    import bpaTools
except ImportError:
    ### Include local modules/librairies  ##
    module_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(module_dir, aixmParserLocalSrc))
    import bpaTools

import aixmReader
from groundEstimatedHeight import GroundEstimatedHeight

import poaffCst
import geoRefArea
from airspacesCatalog import AsCatalog
from geojsonArea import GeojsonArea
from geojsonTruncature import GeojsonTrunc
from geojson2kml import Geojson2Kml
from openairArea import OpenairArea
from xmlSIA import XmlSIA


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
poaffOutPath            = outPath + poaffCst.cstPoaffOutPath
globalCatalog           = poaffOutPath + poaffCst.cstReferentialPath + poaffCst.cstGlobalHeader + poaffCst.cstSeparatorFileName + poaffCst.cstCatalogFileName
globalAsGeojson         = poaffOutPath + poaffCst.cstGlobalHeader + poaffCst.cstSeparatorFileName + poaffCst.cstAsAllGeojsonFileName
globalAsOpenair         = poaffOutPath + poaffCst.cstGlobalHeader + poaffCst.cstSeparatorFileName + poaffCst.cstAsAllOpenairFileName


###################################
###  Configuration d'execution  ###
###################################
debugLevel:bool         = 0         #Normaly = 0 for silent; 1 for generate % of RDP-optimization in openair files; 2 in openair and log files
epsilonReduce:bool      = True      #Normaly = True  or False for generate without optimization
aixmPaserConstruct:bool = True      #Normaly = True
geojsonConstruct:bool   = True      #Normaly = True
openairConstruct:bool   = True      #Normaly = True
kmlConstruct:bool       = True      #Normaly = True
catalogConstruct:bool   = False     #Normaly = False or True for only catalog construct files
partialConstruct:bool   = False     #Normaly = False or True for limited construct files (geoFrenchNorth + geoFrenchSouth)
testMode:bool           = False     #Normaly = False or True for generate with tests files

####  Liste des fichiers a traiter  ####
scriptProcessing = {
    "BPa-TestXmlSIA":       {poaffCst.cstSpExecute:None         , poaffCst.cstSpProcessType:None,                     poaffCst.cstSpOutPath:"../output/Tests/",  poaffCst.cstSpSrcFile:"../input/Tests/99999999_BPa_TestFrequency_xml_SIA-FR.xml"                   ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "SIA-XML":              {poaffCst.cstSpExecute:None         , poaffCst.cstSpProcessType:None,                     poaffCst.cstSpOutPath:"../output/SIA/",    poaffCst.cstSpSrcFile:"../input/SIA/20211202-20211229_AIRAC-1221_xml_SIA-FR_BPa.xml"               ,poaffCst.cstSpSrcOwner:"https://www.sia.aviation-civile.gouv.fr"},
    "SIA-SUPAIP":           {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/BPa/",    poaffCst.cstSpSrcFile:"../input/BPa/20211204_BPa_FR-SIA-SUPAIP_aixm45.xml"                         ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "BPa-TestRefAlt":       {poaffCst.cstSpExecute:    testMode , poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/Tests/",  poaffCst.cstSpSrcFile:"../input/Tests/99999999_BPa_TestReferentielAltitude_aixm45.xml"             ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "BPa-Test4Clean":       {poaffCst.cstSpExecute:    testMode , poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/Tests/",  poaffCst.cstSpSrcFile:"../input/Tests/99999999_BPa_Test4CleaningCatalog_aixm45.xml"                ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "BPa-Test4AppDelta1":   {poaffCst.cstSpExecute:    testMode , poaffCst.cstSpProcessType:poaffCst.cstSpPtAddDelta, poaffCst.cstSpOutPath:"../output/Tests/",  poaffCst.cstSpSrcFile:"../input/Tests/99999999_BPa_Test4AppendDelta1_aixm45.xml"                   ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "BPa-Test4AppDelta2":   {poaffCst.cstSpExecute:    testMode , poaffCst.cstSpProcessType:poaffCst.cstSpPtAddDelta, poaffCst.cstSpOutPath:"../output/Tests/",  poaffCst.cstSpSrcFile:"../input/Tests/99999999_BPa_Test4AppendDelta2_aixm45.xml"                   ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "BPa-Test4AppDelta3":   {poaffCst.cstSpExecute:    testMode , poaffCst.cstSpProcessType:poaffCst.cstSpPtAddDelta, poaffCst.cstSpOutPath:"../output/Tests/",  poaffCst.cstSpSrcFile:"../input/Tests/99999999_BPa_Test4kml_aixm45.xml"                            ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "SIA-AIXM":             {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAddDelta, poaffCst.cstSpOutPath:"../output/SIA/",    poaffCst.cstSpSrcFile:"../input/SIA/20211202-20211229_AIRAC-1221_aixm4.5_SIA-FR.xml"               ,poaffCst.cstSpSrcOwner:"https://www.sia.aviation-civile.gouv.fr"},
    "EuCtrl":               {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAddDelta, poaffCst.cstSpOutPath:"../output/EuCtrl/", poaffCst.cstSpSrcFile:"../input/EuCtrl/20211202_aixm4.5_Eurocontrol-Euro.xml"                      ,poaffCst.cstSpSrcOwner:"https://www.eurocontrol.int"},
    "FFVL-Protocoles":      {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/FFVL/",   poaffCst.cstSpSrcFile:"../input/FFVL/20210518_FFVL_ProtocolesParticuliers_BPa_aixm45.xml"          ,poaffCst.cstSpSrcOwner:"https://federation.ffvl.fr"},
    "BPa-FrenchSS":         {poaffCst.cstSpExecute:True         , poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/BPa/",    poaffCst.cstSpSrcFile:"../input/BPa/20210302_LTA-French1-HR_BPa_aixm45.xml"                        ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "BPa-ZonesComp":        {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/BPa/",    poaffCst.cstSpSrcFile:"../input/BPa/20210304_BPa_ZonesComplementaires_aixm45.xml"                  ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "BPa-Parcs":            {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/Parcs/",  poaffCst.cstSpSrcFile:"../input/Parcs/__All-Parcs/20211204_All-Parcs_aixm45.xml"                   ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "BPa-Birds":            {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/BPa/",    poaffCst.cstSpSrcFile:"../input/BPa/20210614_BPa_FR-ZSM_Protection-des-rapaces_aixm45.xml"         ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "FFVP-Birds":           {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/FFVP/",   poaffCst.cstSpSrcFile:"../input/FFVP/20191214_FFVP_BirdsProtect_aixm45.xml"                        ,poaffCst.cstSpSrcOwner:"https://www.ffvp.fr"}
}

#### Paramétrage de l'optimisation des tracés ####
def setConfEpsilonReduce(epsilonReduce:bool=None) -> None:
    poaffCst.cstGeojsonCfdEpsilonReduce  = 0.0    if epsilonReduce else -1        #0.0    - Suppression de doublons pour tracés GeoJSON en sortie CFD
    poaffCst.cstGeojsonEpsilonReduce     = 0.0001 if epsilonReduce else -1        #0.0001 - Simplification des tracés GeoJSON standard
    poaffCst.cstKmlCfdEpsilonReduce      = 0.0001 if epsilonReduce else -1        #0.0001 - Faible simplification des tracés KML en sortie CFD
    poaffCst.cstKmlEpsilonReduce         = 0.0005 if epsilonReduce else -1        #0.0005 - Réduction importante des tracés KML
    poaffCst.cstOpenairCfdEpsilonReduce  = 0.0    if epsilonReduce else -1        #0.0    - Suppression de doublons pour tracés Openair standards
    poaffCst.cstOpenairEpsilonReduce     = 0.0    if epsilonReduce else -1        #0.0    - Suppression de doublons pour tracés Openair standards
    poaffCst.cstOpenairEpsilonReduceMR   = 0.001  if epsilonReduce else -1        #0.001  - Base de réduction imporytante des tracés Openair pour les zones régionnales "ISO_Perimeter=Partial" (gpsWithTopo or gpsWithoutTopo)[geoFrenchNorth, geoFrenchSouth, geoFrenchNESW, geoFrenchVosgesJura, geoFrenchPyrenees, geoFrenchAlps]
    poaffCst.cstOpenairDigitOptimize     = 0      if epsilonReduce else -1        #openairDigitOptimize=-1 / 0 / 2
    return
setConfEpsilonReduce(epsilonReduce)

####  Options d'appels pour création des fichiers  ####
#aArgs = [appName, "-Fall", "-Tall", aixmReader.CONST.optALL, aixmReader.CONST.optIFR, aixmReader.CONST.optVFR, aixmReader.CONST.optFreeFlight, aixmReader.CONST.optCleanLog]
#aArgs = [appName, aixmReader.CONST.frmtALL, aixmReader.CONST.typeAIRSPACES, aixmReader.CONST.optALL, aixmReader.CONST.optIFR, aixmReader.CONST.optVFR, aixmReader.CONST.optFreeFlight, aixmReader.CONST.optCleanLog]
aArgs = [appName, aixmReader.CONST.frmtALL, aixmReader.CONST.typeAIRSPACES, aixmReader.CONST.optALL, aixmReader.CONST.optCleanLog]
aArgs += [aixmReader.CONST.optOpenairDigitOptimize + "=" + str(poaffCst.cstOpenairDigitOptimize)]
aArgs += [aixmReader.CONST.optEpsilonReduce + "=" + str(poaffCst.cstOpenairEpsilonReduce)]


def poaffMergeFiles() -> None:
    sModuleTitle = "..oooOOOO  Step 2 - Execution by - {0}  OOOOooo..".format(appId)
    oLog.info("\n" + sModuleTitle, outConsole=True)
    print(u"\u2594"*len(sModuleTitle))

    oAsCat = AsCatalog(oLog)    #Gestion des catalogues

    #A1/ Consolidation des catalogues (avec premier pré-filtrage qd nécessaire)
    for sKey, oFile in scriptProcessing.items():                            #Traitement des fichiers
        oAsCat.mergeJsonCatalogFile(sKey, oFile)                            #Consolidation des fichiers catalogues

    if not catalogConstruct:
        #A2a/ Chargement du fichier contenant les Fréquences radio
        oFreq = XmlSIA(oLog)
        if testMode:
            sKey = "BPa-TestXmlSIA"
        else:
            sKey = "SIA-XML"
        sFile = scriptProcessing[sKey][poaffCst.cstSpSrcFile]
        oFreq.openFile(appPath + sFile, sKey)
        oAsCat.addSrcFile(sKey, sFile, scriptProcessing[sKey][poaffCst.cstSpSrcOwner], oFreq.srcOrigin, oFreq.srcVersion, oFreq.srcCreated)
        #A2b/ Consolidation des Fréquences radio dans le catalogue global
        oFreq.loadFrequecies()
        oFreq.syncFrequecies(oAsCat.getContent())
        oFreq.findFrequecies(oAsCat.getContent())
    oAsCat.saveCatalogFiles(globalCatalog)                                  #Sérialisation du catalogue global

    if catalogConstruct:                                                    #Abandon des traitements
        return

    if geojsonConstruct:
        #B1/ Consolidation des espaces-aériens GeoJSON
        oJsArea = GeojsonArea(oLog, oAsCat, partialConstruct)                   #Gestion des zones
        for sKey, oFile in scriptProcessing.items():                            #Traitement des fichiers
            oJsArea.mergeGeoJsonAirspacesFile(sKey, oFile)                      #Consolidation des fichiers GeoJSON

        #B2/ Construction des sorties GeoJSON
        if not partialConstruct:
            #oJsArea.saveGeoJsonAirspacesFile(globalAsGeojson, "all", epsilonReduce=poaffCst.cstGeojsonEpsilonReduce)     #Sortie complète des zones
            oJsArea.saveGeoJsonAirspacesFile(globalAsGeojson, "ifr", epsilonReduce=poaffCst.cstGeojsonEpsilonReduce)      #Sortie des zones IFR
            oJsArea.saveGeoJsonAirspacesFile(globalAsGeojson, "vfr", epsilonReduce=poaffCst.cstGeojsonEpsilonReduce)      #Sortie des zones VFR
            oJsArea.saveGeoJsonAirspacesFile(globalAsGeojson, "cfd", epsilonReduce=poaffCst.cstGeojsonCfdEpsilonReduce)   #Sortie spécifique vol-libre pour affichage dans la CFD (VictorB et https://flyxc.app)
            oJsArea.saveGeoJsonAirspacesFile(globalAsGeojson, "ff" , epsilonReduce=poaffCst.cstGeojsonEpsilonReduce)      #Sortie globale vol-libre sans zonage géographique
            oJsArea.saveGeoJsonAirspacesFile(globalAsGeojson, "wrn", epsilonReduce=poaffCst.cstGeojsonEpsilonReduce)      #Sortie globale warning sans zonage géographique
        oJsArea.saveGeoJsonAirspacesFile4Area(globalAsGeojson, epsilonReduce=poaffCst.cstGeojsonEpsilonReduce)            #Sorties par zonage géographique

    if openairConstruct:
        #C1/ Consolidation des espaces-aériens Openair
        oOpArea = OpenairArea(oLog, oAsCat, partialConstruct)                   #Gestion des zones
        for sKey, oFile in scriptProcessing.items():                            #Traitement des fichiers
            oOpArea.mergeOpenairAirspacesFile(sKey, oFile)                      #Consolidation des fichiers Openair

        #C2/ Construction des sorties Openair
        if not partialConstruct:
            #oOpArea.saveOpenairAirspacesFile(globalAsOpenair, "all")           #Sortie complète des zones
            oOpArea.saveOpenairAirspacesFile(globalAsOpenair, "ifr")            #Sortie des zones IFR
            oOpArea.saveOpenairAirspacesFile(globalAsOpenair, "vfr")            #Sortie des zones VFR
            oOpArea.saveOpenairAirspacesFile(globalAsOpenair, "cfd")            #Sortie spécifique vol-libre pour validation des traces CFD (KevinB et https://flyxc.app)
            oOpArea.saveOpenairAirspacesFile(globalAsOpenair, "ff")             #Sorties globales vol-libre + warning sans zonage géographique
        oOpArea.saveOpenairAirspacesFile4Area(globalAsOpenair)                  #Sorties par zonage géographique
    return


def makeKmlFiles() -> None:
    if not kmlConstruct:
        return
    makeKml(None, "-ffvl-cfd")                                              #Sortie du ficher en KML
    makeKml(None, "-vfr")                                                   #Sortie du ficher en KML
    makeKml(None, "-ifr")                                                   #Sortie du ficher en KML
    aTypeFiles:list = ["-freeflight"]
    for sTypFile in aTypeFiles:
        for sAreaKey, oAreaRef in geoRefArea.GeoRefArea(False).AreasRef.items():
            #if sAreaKey in ["geoFrenchNorth","geoFrenchSouth","geoFrenchNESW","geoFrenchVosgesJura","geoFrenchPyrenees","geoFrenchAlps"]:
            #    continue
            #Fichier principal régionalisé (ex: global@airspaces-freeflight-geoFrench.geojson)
            sContext:str = sTypFile + "-" + sAreaKey                        #sample "-freeflight-geoFrench"
            makeKml(None, sContext)                                         #Sortie du ficher standard en KMLs
            makeKml(None, sContext + "-warning")                            #Sortie du ficher warning en KMLs
    return

def makeKml(oGeo, sContext:str) -> None:
    oLog.info("makeKml() {0}".format(sContext), outConsole=True)
    sSrcFile:str = globalAsGeojson      #Default = '-all'
    sSrcFile:str = sSrcFile.replace("-all", sContext)
    sKmlFile:str = sSrcFile.replace(".geojson", ".kml")

    oKml = Geojson2Kml(oLog=oLog)
    oKml.readGeojsonFile(sSrcFile)
    sTilte:str = "Paragliding Openair Frensh Files " + sContext + " map"
    sDesc:str  = "Created at: " + bpaTools.getNowISO() + "<br/>http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/"
    oKml.createKmlDocument(sTilte, sDesc)
    er:float = poaffCst.cstKmlEpsilonReduce     #Param d'optimisation standard de KML
    if sSrcFile.find("ffvl-cfd")>0:
        er = poaffCst.cstKmlCfdEpsilonReduce    #Imposer l'optimisation pour les sorties KML CFD
    oKml.makeAirspacesKml(epsilonReduce=er)     #epsilonReduce=0 / epsilonReduce=0.0001 or 0.0005
    oKml.writeKmlFile(sKmlFile, bExpand=0)
    oKml = None     #Free and clean file

    #BPascal le 02/02/2021 - Suppression des KMZ suite à optimisation des tracé GeoJSON & KML
    #D3/ Construction du KMZ avec compression de données
    #if os.path.exists(sKmlFile):
    #    sKmzFile = sKmlFile.replace(".kml", ".kmz")
    #    oZip = zipfile.ZipFile(sKmzFile, 'w', zipfile.ZIP_DEFLATED)
    #    oZip.write(sKmlFile)
    #    oZip.close()
    return

def parseFile(sKey:str, oFile:dict) -> bool:
    oLog.info(aixmParserId+" --> parseFile() by aixmReader.AixmControler()", outConsole=True)
    bpaTools.createFolder(oFile[poaffCst.cstSpOutPath])                     #Init dossier de sortie
    aixmCtrl = aixmReader.AixmControler(oFile[poaffCst.cstSpSrcFile], oFile[poaffCst.cstSpOutPath], sKey, oLog)     #Init controler
    ret = aixmCtrl.execParser(oOpts, catalogConstruct)                                        #Execution des traitements
    return ret

def updateReferentials(sKey:str, oFile:dict) -> None:
    oLog.info(aixmParserId + " --> UpdateReferentials() by aixmParser.GroundEstimatedHeight()", outConsole=True)
    oGEH = GroundEstimatedHeight(oLog, oFile[poaffCst.cstSpOutPath], oFile[poaffCst.cstSpOutPath] + poaffCst.cstReferentialPath, sKey + "@")
    oGEH.parseUnknownGroundHeightRef()                                      #Execution des traitements
    return

def poaffGenerateFiles(sMsg:str=None) -> None:
    sModuleTitle = "..oooOOOO  Step 1 - Execution by - {0}  OOOOooo..".format(aixmParserId)
    oLog.info("\n" + sModuleTitle, outConsole=True)
    print(u"\u2594"*len(sModuleTitle))
    if sMsg!=None:
        oLog.info("{0}".format(sMsg), outConsole=True)
    oLog.writeCommandLine(aArgs)                                            #Trace le contexte d'execution
    for sKey, oFile in scriptProcessing.items():                            #Traitement des fichiers
        if oFile[poaffCst.cstSpExecute]:                                    #Flag prise en compte du fichier
            oLog.info("..oooOOOO  poaffGenerateFiles() --> {0}".format(oFile[poaffCst.cstSpSrcFile]), outConsole=False)
            iPrevErr = oLog.CptCritical + oLog.CptError                     #Nombre d'erreurs en pré-traitements
            parseFile(sKey, oFile)                                          #Creation des fichiers
            iPostErr = oLog.CptCritical + oLog.CptError                     #Nombre d'erreurs en post-traitements
            if iPostErr!=iPrevErr:                                          #Si écart constaté
                updateReferentials(sKey, oFile)                             #Forcer mise à jour des référentiels d'altitudes
                parseFile(sKey, oFile)                                      #Regénération des fichiers après maj des référentiels
    return


if __name__ == '__main__':
    sCallingContext = None

    bpaTools.createFolder(outPath)                                          #Initialisation
    bpaTools.createFolder(poaffOutPath)                                     #Initialisation
    bpaTools.createFolder(poaffOutPath + poaffCst.cstReferentialPath)       #Initialisation

    oOpts = bpaTools.getCommandLineOptions(aArgs)                           #Arguments en dictionnaire
    oLog = bpaTools.Logger(appId, logFile, poaffCst.callingContext, poaffCst.linkContext, debugLevel=debugLevel, isSilent=bool(aixmReader.CONST.optSilent in oOpts))

    if aixmReader.CONST.optCleanLog in oOpts:
        oLog.resetFile()                                                    #Clean du log si demandé

    #--------- creation des fichiers unitaires ----------
    if aixmPaserConstruct:
        poaffGenerateFiles()                                                #Creation des fichiers
    poaffMergeFiles()                                                       #Consolidation des fichiers
    makeKmlFiles()                                                          #Sortie du ficher en KMLs

    print()
    oLog.Report()
    iPostErr = oLog.CptCritical + oLog.CptError                             #Nombre d'erreurs en post-traitements
    if iPostErr>0:
        print()
        sMsg = "Show errors in log file ! - "
        oLog.critical(sMsg, outConsole=True)
    oLog.closeFile()
    #if iPostErr>0:
    #    bpaTools.sysExitError(sMsg)

