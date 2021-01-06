#!/usr/bin/env python3
import os
import zipfile

aixmParserLocalSrc  = "../../aixmParser/src/"
try:
    import bpaTools
except ImportError:
    ### Include local modules/librairies  ##
    #import os
    import sys
    module_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(module_dir, aixmParserLocalSrc))
    import bpaTools

import aixmReader
from groundEstimatedHeight import GroundEstimatedHeight

import poaffCst
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


####  Liste des fichiers a traiter  ####
testMode:bool           = False      #Normaly = False or True for generate with tests files
partialConstruct:bool   = False      #Normaly = False or True for limited construction files
scriptProcessing = {
    "BPa-TestRefAlt":       {poaffCst.cstSpExecute:    testMode , poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/Tests/",  poaffCst.cstSpSrcFile:"../input/Tests/99999999_BPa_TestReferentielAltitude_aixm45.xml"     ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "BPa-Test4Clean":       {poaffCst.cstSpExecute:    testMode , poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/Tests/",  poaffCst.cstSpSrcFile:"../input/Tests/99999999_BPa_Test4CleaningCatalog_aixm45.xml"        ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "BPa-Test4AppDelta1":   {poaffCst.cstSpExecute:    testMode , poaffCst.cstSpProcessType:poaffCst.cstSpPtAddDelta, poaffCst.cstSpOutPath:"../output/Tests/",  poaffCst.cstSpSrcFile:"../input/Tests/99999999_BPa_Test4AppendDelta1_aixm45.xml"           ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "BPa-Test4AppDelta2":   {poaffCst.cstSpExecute:    testMode , poaffCst.cstSpProcessType:poaffCst.cstSpPtAddDelta, poaffCst.cstSpOutPath:"../output/Tests/",  poaffCst.cstSpSrcFile:"../input/Tests/99999999_BPa_Test4AppendDelta2_aixm45.xml"           ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "BPa-Test4AppDelta3":   {poaffCst.cstSpExecute:    testMode , poaffCst.cstSpProcessType:poaffCst.cstSpPtAddDelta, poaffCst.cstSpOutPath:"../output/Tests/",  poaffCst.cstSpSrcFile:"../input/Tests/99999999_BPa_Test4kml_aixm45.xml"                    ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "BPa-TestXmlSIA":       {poaffCst.cstSpExecute:None         , poaffCst.cstSpProcessType:None,                     poaffCst.cstSpOutPath:"../output/Tests/",  poaffCst.cstSpSrcFile:"../input/Tests/99999999_BPa_TestFrequency_xml_SIA-FR.xml"           ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "xmlSIA":               {poaffCst.cstSpExecute:None         , poaffCst.cstSpProcessType:None,                     poaffCst.cstSpOutPath:"../output/SIA/",    poaffCst.cstSpSrcFile:"../input/SIA/20201231-20210127_AIRAC-1420_xml_SIA-FR_BPa.xml"       ,poaffCst.cstSpSrcOwner:"https://www.sia.aviation-civile.gouv.fr"},
    "SIA":                  {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/SIA/",    poaffCst.cstSpSrcFile:"../input/SIA/20201231-20210127_AIRAC-1420_aixm4.5_SIA-FR.xml"       ,poaffCst.cstSpSrcOwner:"https://www.sia.aviation-civile.gouv.fr"},
    "EuCtrl":               {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAddDelta, poaffCst.cstSpOutPath:"../output/EuCtrl/", poaffCst.cstSpSrcFile:"../input/EuCtrl/20201231_aixm4.5_Eurocontrol-Euro_BPa.xml"          ,poaffCst.cstSpSrcOwner:"https://www.eurocontrol.int"},
    "FFVP-Parcs":           {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/FFVP/",   poaffCst.cstSpSrcFile:"../input/FFVP/20201204_FFVP_ParcsNat_BPa_aixm45.xml"                ,poaffCst.cstSpSrcOwner:"https://www.ffvp.fr"},
    "FFVL-ZonesComp":       {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/FFVL/",   poaffCst.cstSpSrcFile:"../input/FFVL/20201204_FFVL_ZonesComplementaires_aixm45.xml"        ,poaffCst.cstSpSrcOwner:"https://federation.ffvl.fr/"},
    "BPa-Birds":            {poaffCst.cstSpExecute:True         , poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/BPa/",    poaffCst.cstSpSrcFile:"../input/BPa/20201216_BPa_FR-ZSM_Protection-des-rapaces_aixm45.xml" ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "BPa-FrenchSS":         {poaffCst.cstSpExecute:True         , poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/BPa/",    poaffCst.cstSpSrcFile:"../input/BPa/20210106_LTA-French1-HR_BPa_aixm45.xml"                ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "FFVP-Birds":           {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/FFVP/",   poaffCst.cstSpSrcFile:"../input/FFVP/20191214_FFVP_BirdsProtect_aixm45.xml"                ,poaffCst.cstSpSrcOwner:"https://www.ffvp.fr"},
    "FFVL-ParcBauges":      {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/FFVL/",   poaffCst.cstSpSrcFile:"../input/FFVL/20210104_FFVL_ParcBauges_BPa_aixm45.xml"              ,poaffCst.cstSpSrcOwner:"https://federation.ffvl.fr/"},
    "FFVL-ParcPassy":       {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/FFVL/",   poaffCst.cstSpSrcFile:"../input/FFVL/20191129_FFVL_ParcPassy_aixm45.xml"                   ,poaffCst.cstSpSrcOwner:"https://federation.ffvl.fr/"},
    "FFVL-ParcAnnecyMarais":{poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/FFVL/",   poaffCst.cstSpSrcFile:"../input/FFVL/20200120_FFVL_ParcAnnecyMaraisBoutDuLac_aixm45.xml"   ,poaffCst.cstSpSrcOwner:"https://federation.ffvl.fr/"},
    "BPa-ParcCevennes":     {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/BPa/",    poaffCst.cstSpSrcFile:"../input/BPa/20190401_PascalW_ParcCevennes_aixm45.xml"              ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "BPa-ParcChampagne":    {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/BPa/",    poaffCst.cstSpSrcFile:"../input/BPa/20200810_BPa_ParcsNat_ChampagneBourgogne_aixm45.xml"   ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "BPa-ParcBaieDeSomme":  {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/BPa/",    poaffCst.cstSpSrcFile:"../input/BPa/20200729_SergeR_ParcNat_BaieDeSomme_aixm45.xml"        ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "BPa-ParcHourtin":      {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/BPa/",    poaffCst.cstSpSrcFile:"../input/BPa/20200729_SergeR_ParcNat_Hourtin_aixm45.xml"            ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"},
    "BPa-ZonesComp":        {poaffCst.cstSpExecute:not(testMode), poaffCst.cstSpProcessType:poaffCst.cstSpPtAdd,      poaffCst.cstSpOutPath:"../output/BPa/",    poaffCst.cstSpSrcFile:"../input/BPa/20201210_BPa_ZonesComplementaires_aixm45.xml"          ,poaffCst.cstSpSrcOwner:"http://pascal.bazile.free.fr"}
}


####  Options d'appels pour création des fichiers  ####
#aArgs = [appName, "-Fall", "-Tall", aixmReader.CONST.optALL, aixmReader.CONST.optIFR, aixmReader.CONST.optVFR, aixmReader.CONST.optFreeFlight, aixmReader.CONST.optCleanLog]
#aArgs = [appName, aixmReader.CONST.frmtALL, aixmReader.CONST.typeAIRSPACES, aixmReader.CONST.optALL, aixmReader.CONST.optIFR, aixmReader.CONST.optVFR, aixmReader.CONST.optFreeFlight, aixmReader.CONST.optCleanLog]
aArgs = [appName, aixmReader.CONST.frmtALL, aixmReader.CONST.typeAIRSPACES, aixmReader.CONST.optALL, aixmReader.CONST.optCleanLog]
#aArgs = [appName, aixmReader.CONST.frmtGEOJSON, aixmReader.CONST.typeAIRSPACES, aixmReader.CONST.optALL, aixmReader.CONST.optCleanLog]


def poaffMergeFiles() -> None:
    sModuleTitle = "..oooOOOO  Execution by - {0}  OOOOooo..".format(appId)
    oLog.info("\n" + sModuleTitle, outConsole=True)
    print(u"\u2594"*len(sModuleTitle))

    oAsCat = AsCatalog(oLog)    #Gestion des catalogues

    #A1/ Consolidation des catalogues (avec premier pré-filtrage qd nécessaire)
    for sKey, oFile in scriptProcessing.items():                            #Traitement des fichiers
        oAsCat.mergeJsonCatalogFile(sKey, oFile)                            #Consolidation des fichiers catalogues

    #A2a/ Chargement du fichier contenant les Fréquences radio
    oFreq = XmlSIA(oLog)
    if testMode:
        sKey = "BPa-TestXmlSIA"
    else:
        sKey = "xmlSIA"
    sFile = scriptProcessing[sKey][poaffCst.cstSpSrcFile]
    oFreq.openFile(appPath + sFile, sKey)
    oAsCat.addSrcFile(sKey, sFile, scriptProcessing[sKey][poaffCst.cstSpSrcOwner], oFreq.srcOrigin, oFreq.srcVersion, oFreq.srcCreated)
    #A2b/ Consolidation des Fréquences radio dans le catalogue global
    oFreq.loadFrequecies()
    oFreq.syncFrequecies(oAsCat.getContent())
    oAsCat.saveCatalogFiles(globalCatalog)                                  #Sérialisation du catalogue global

    #B1/ Consolidation des espaces-aériens GeoJSON
    oJsArea = GeojsonArea(oLog, oAsCat, partialConstruct)                   #Gestion des zones
    for sKey, oFile in scriptProcessing.items():                            #Traitement des fichiers
        oJsArea.mergeGeoJsonAirspacesFile(sKey, oFile)                      #Consolidation des fichiers GeoJSON

    #B2/ Construction des sorties GeoJSON
    if not partialConstruct:
        #oJsArea.saveGeoJsonAirspacesFile(globalAsGeojson, "all")           #Sortie complète des zones
        oJsArea.saveGeoJsonAirspacesFile(globalAsGeojson, "ifr")            #Sortie des zones IFR
        oJsArea.saveGeoJsonAirspacesFile(globalAsGeojson, "vfr")            #Sortie des zones VFR
        oJsArea.saveGeoJsonAirspacesFile(globalAsGeojson, "cfd")            #Sortie spécifique vol-libre pour affichage dans la CFD (VictorB et https://flyxc.app)
        #oJsArea.saveGeoJsonAirspacesFile(globalAsGeojson, "ff")            #Sortie spécifique vol-libre
    oJsArea.saveGeoJsonAirspacesFile4Area(globalAsGeojson)                  #Sorties par zonage géographique

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
        #oOpArea.saveOpenairAirspacesFile(globalAsOpenair, "ff")            #Sortie spécifique vol-libre
    oOpArea.saveOpenairAirspacesFile4Area(globalAsOpenair)                  #Sorties par zonage géographique
    return

def makeKml(oGeo, sContext:str) -> None:
    oLog.info("makeKml() {0}".format(sContext), outConsole=True)
    sSrcFile:str = globalAsGeojson      #Default = '-all'
    sSrcFile:str = sSrcFile.replace("-all", sContext)
    sTrcFile:str = sSrcFile.replace(".geojson", "-optimized.geojson")
    sKmlFile:str = sSrcFile.replace(".geojson", ".kml")

    #D1/ Simplification du GeoJSON par optimisation du tracé
    oTrunc:GeojsonTrunc = None
    if oGeo==None:
        oTrunc = GeojsonTrunc(oLog=oLog)
        oTrunc.truncateGeojsonFile(sSrcFile, sTrcFile, iDecimal=3)          #iDecimal=2 for Low resolution map; 3 for standard quality or 4 for higth quility)
    else:
        oTrunc = GeojsonTrunc(oLog=oLog, oGeo=oGeo)

    #D2/ Construction d'une sortie KML sur la base d'un GeoJSON
    oKml:Geojson2Kml = None
    if oGeo==None:
        oKml = Geojson2Kml(oLog=oLog)
        oKml.readGeojsonFile(sTrcFile)
    else:
        oKml = Geojson2Kml(oLog=oLog, oGeo=oTrunc.oOutGeo)
    oKml.createKmlDocument("Paragliding Openair Frensh Files", "Cartographies aériennes France - http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/")
    oKml.makeAirspacesKml()
    oKml.writeKmlFile(sKmlFile, bExpand=0)
    oKml = None     #Free
    oTrunc = None   #Free

    #D3/ Construction du KMZ avec compression de données
    if os.path.exists(sKmlFile):
        sKmzFile = sKmlFile.replace(".kml", ".kmz")
        oZip = zipfile.ZipFile(sKmzFile, 'w', zipfile.ZIP_DEFLATED)
        oZip.write(sKmlFile)
        oZip.close()
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
    sModuleTitle = "..oooOOOO  Execution by - {0}  OOOOooo..".format(aixmParserId)
    oLog.info("\n" + sModuleTitle, outConsole=True)
    print(u"\u2594"*len(sModuleTitle))
    if sMsg!=None:
        oLog.warning("{0}".format(sMsg), outConsole=True)
    oLog.writeCommandLine(aArgs)                                            #Trace le contexte d'execution

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
    if not partialConstruct:
        poaffGenerateFiles()                                                #Creation des fichiers
    if (oLog.CptCritical + oLog.CptError) > 0:
        oLog.resetFile()                                                    #Clean du log
        sCallingContext = "Forced reload by second phase"
        poaffGenerateFiles(sCallingContext)                                 #Seconde tentative de creation des fichiers

    lAbortTreatment:int = oLog.CptCritical + oLog.CptError
    if lAbortTreatment > 0:
        print()
        sAbortTreatment = "Abort treatment - Show errors in log file !"
        oLog.critical(sAbortTreatment, outConsole=True)
    else:
        poaffMergeFiles()                                                   #Consolidation des fichiers
        makeKml(None, "-freeflight-geoFrench")                              #Sortie du ficher en KML
        #if not(testMode):
        #    oWeb = PoaffWebPage(oLog, outPath)
        #    oWeb.createPoaffWebPage(None)                                   #Preparation pour publication
        #    #oWeb.createPoaffWebPage("20200715_")                           #Pour révision d'une publication

    print()
    if sCallingContext!=None:
        oLog.warning("{0}".format(sCallingContext), outConsole=True)
    oLog.Report()
    oLog.closeFile()
    if lAbortTreatment > 0:
        bpaTools.sysExitError(sAbortTreatment)
