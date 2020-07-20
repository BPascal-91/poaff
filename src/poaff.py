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
globalHeader        = "global"
referentialPath     = "referentials/"
poaffOutPath        = outPath + "_POAFF/"
poaffWebPath        = outPath + "_POAFF_www/"
cfdWebPath          = outPath + "_CFD_www/"
bpaTools.createFolder(outPath)                                      #Init dossier de sortie

callingContext      = "Paragliding-OpenAir-FrenchFiles"             #Your app calling context
linkContext         = "http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/"


####  Constantes de paramétrage des catalogues  ####
cstDeduplicateSeparator = "@@-"
cstKeyCatalogType = "type"
cstKeyCatalogHeaderFile = "headerFile"
cstKeyCatalogCatalog = "catalog"
cstKeyCatalogSoftware = "software"
cstKeyCatalogCreated = "created"
cstKeyCatalogContent = "content"
cstKeyCatalogSrcFiles = "srcFiles"
cstKeyCatalogSrcAixmFile = "srcAixmFile"
cstKeyCatalogSrcAixmOrigin = "srcAixmOrigin"
cstKeyCatalogSrcAixmVersion = "srcAixmVersion"
cstKeyCatalogSrcAixmCreated = "srcAixmCreated"
cstKeyCatalogOrgFile = "orgFile"

####  Constantes de paramétrage et liste des fichiers a traiter  ####
cstTestMode = True                                  #True or  False
cstExecute      = "Execute"                         #Identification du Flag d'execution des traitements
cstSrcFile      = "srcFile"                         #Identification du fichier source
cstOutPath      = "outPath"                         #Identification du dossier de sorties
cstProcessType  = "processType"                     #Typage du processus de consolidation des données
cstPtAdd        = "processType-AppendData"          #Consolidation des données par simple ajout (empilage des données sans contrôle de présence)
cstPtAddDelta   = "processType-AppendIfNotExist"    #Consolidation des données par ajout des données qui ne sont pas déjà présentes dans la consolidation
scriptProcessing = {
    "BPa-Test4Clean":       {cstExecute:    cstTestMode , cstProcessType:cstPtAdd,      cstOutPath:"../output/Tests/",  cstSrcFile:"../input/BPa/99999999_BPa_Test4CleaningCatalog_aixm45.xml"},
    "BPa-Test4AppDelta":    {cstExecute:    cstTestMode , cstProcessType:cstPtAddDelta, cstOutPath:"../output/Tests/",  cstSrcFile:"../input/BPa/99999999_BPa_Test4AppendDelta_aixm45.xml"},
    "EuCtrl":               {cstExecute:not(cstTestMode), cstProcessType:cstPtAdd,      cstOutPath:"../output/EuCtrl/", cstSrcFile:"../input/EuCtrl/20200618_aixm4.5_Eurocontrol-FR.xml"},
    "SIA":                  {cstExecute:not(cstTestMode), cstProcessType:cstPtAddDelta, cstOutPath:"../output/SIA/",    cstSrcFile:"../input/SIA/20200618_aixm4.5_SIA-FR.xml"},
    "FFVP-Parcs":           {cstExecute:not(cstTestMode), cstProcessType:cstPtAdd,      cstOutPath:"../output/FFVP/",   cstSrcFile:"../input/FFVP/20200704_FFVP_ParcsNat_BPa_aixm45.xml"},
    "FFVP-Birds":           {cstExecute:not(cstTestMode), cstProcessType:cstPtAdd,      cstOutPath:"../output/FFVP/",   cstSrcFile:"../input/FFVP/20191214_FFVP_BirdsProtect_aixm45.xml"},
    "BPa-ParcCevennes":     {cstExecute:not(cstTestMode), cstProcessType:cstPtAdd,      cstOutPath:"../output/BPa/",    cstSrcFile:"../input/BPa/20190401_WPa_ParcCevennes_aixm45.xml"},
    "BPa-ParcChampagne":    {cstExecute:not(cstTestMode), cstProcessType:cstPtAdd,      cstOutPath:"../output/BPa/",    cstSrcFile:"../input/BPa/20200704_BPa_ParcsNat_ChampagneBourgogne_RegisF_aixm45.xml"},
    "BPa-Birds":            {cstExecute:not(cstTestMode), cstProcessType:cstPtAdd,      cstOutPath:"../output/BPa/",    cstSrcFile:"../input/BPa/20200510_BPa_FR-ZSM_Protection-des-rapaces_aixm45.xml"},
    "BPa-ZonesComp":        {cstExecute:not(cstTestMode), cstProcessType:cstPtAdd,      cstOutPath:"../output/BPa/",    cstSrcFile:"../input/BPa/20200705_BPa_ZonesComplementaires_aixm45.xml"}
}


####  Options d'appels pour création des fichiers  ####
#aArgs = [appName, "-Fall", "-Tall", aixmReader.CONST.optALL, aixmReader.CONST.optIFR, aixmReader.CONST.optVFR, aixmReader.CONST.optFreeFlight, aixmReader.CONST.optCleanLog]
aArgs = [appName, "-Fall", aixmReader.CONST.typeAIRSPACES, aixmReader.CONST.optALL, aixmReader.CONST.optIFR, aixmReader.CONST.optVFR, aixmReader.CONST.optFreeFlight, aixmReader.CONST.optCleanLog]


####  Membres pour globalisation des traitements ####
globalCatalog = poaffOutPath + referentialPath + globalHeader + "@airspacesCatalog.json"
oGlobalCatalog:dict = {}


def makeNewKey(sKey:str="", oCat:dict={}) -> str:
    lIdx:int = 1
    aKey = sKey.split(cstDeduplicateSeparator)
    if len(aKey)>1: sKey = aKey[0]
    while True:
        sNewKey = sKey + cstDeduplicateSeparator + str(lIdx)
        if not(sNewKey in oCat):
            break
        lIdx+=1
    return sNewKey

def isValidArea(sKeyFile:str, oAs:dict) -> bool:
    ret:bool = True                     #Default value
    if oAs["groupZone"]:                #Exclure les zones de regroupement
        return False
    
    if sKeyFile=="BPa-Test4Clean":
        #Test de suppression manuel d'une zone en mer - [Q] 18 B1 (id=LFD18B1)
        if oAs["id"] in ["LFD18B1"]: ret = False
    if sKeyFile=="EuCtrl":
        #Supprimer les zones
        #   [D] ALBERT BRAY (CTR / id=LFAQ) - car mauvais tracé et récupération via le fichier SIA
        #   [R] BRUSSELS FIR (RMZ / EQUIPMENT / id=EBBU RMZ)
        #   [P] BRUSSELS FIR (TMZ / EQUIPMENT / id=EBBU TMZ)
        if oAs["id"] in ["LFAQ","EBBU RMZ","EBBU TMZ"]: ret = False
    #elif sKeyFile=="SIA":
        # ../..
    
    if not(ret):
        oLog.info("Ignored area by manual filter - ({0}){1}".format(sKeyFile, oAs["id"], outConsole=False))
    return ret

def mergeCatalogFiles(sKeyFile:str, oFile:dict) -> bool:
    fileCatalog = oFile[cstOutPath] + referentialPath + sKeyFile + "@airspacesCatalog.json"
    oLog.info("Consolidation file {0}: {1} -->({2})--> {3}".format(sKeyFile, fileCatalog, oFile[cstProcessType], globalCatalog), outConsole=True)
    ofileCatalog = bpaTools.readJsonFile(fileCatalog)                                       #Chargement du catalogue du fichier analysé
    #oLog.info("ofileCatalog:\n{0}".format(ofileCatalog, outConsole=False))

    oHeadFile = ofileCatalog[cstKeyCatalogHeaderFile]                                           #Entête concernant le fichier analysé
    
    oGlobalCatalogHeader:dict = {}                                                              #Entête du catalogue gloabal
    if oGlobalCatalog=={}:                                                                      #Catalogue vde, donc initialisation du catalogue gloabal
        oGlobalCatalog.update({cstKeyCatalogType:ofileCatalog[cstKeyCatalogType]})              #Typage du catalogue
        oGlobalCatalogHeader.update({cstKeyCatalogSoftware:oHeadFile[cstKeyCatalogSoftware]})   #Référence au soft de construction
        oGlobalCatalogHeader.update({cstKeyCatalogCreated:oHeadFile[cstKeyCatalogCreated]})     #Heurodatage de la construction
        oGlobalCatalogHeader.update({cstKeyCatalogContent:oHeadFile[cstKeyCatalogContent]})     #Déclaration du contenu
        oGlobalCatalog.update({cstKeyCatalogHeaderFile:oGlobalCatalogHeader})                   #Ajout de l'entête de catalogue
    else:
        oGlobalCatalogHeader = oGlobalCatalog[cstKeyCatalogHeaderFile]                          #Entête du catalogue gloabal
    
    oCatalogFile:dict = {}                                                                      #Description du fichier analysé
    oCatalogFile.update({cstKeyCatalogSrcAixmFile:oHeadFile[cstKeyCatalogSrcAixmFile]})         #Nom du fichier analysé
    oCatalogFile.update({cstKeyCatalogSrcAixmOrigin:oHeadFile[cstKeyCatalogSrcAixmOrigin]})     #Origine du fichier analysé
    oCatalogFile.update({cstKeyCatalogSrcAixmVersion:oHeadFile[cstKeyCatalogSrcAixmVersion]})   #Version du fichier analysé
    oCatalogFile.update({cstKeyCatalogSrcAixmCreated:oHeadFile[cstKeyCatalogSrcAixmCreated]})   #Horodatage de la création du fichier analysé
    
    if cstKeyCatalogSrcFiles in oGlobalCatalogHeader:
        oGlobalCatalogFiles = oGlobalCatalogHeader[cstKeyCatalogSrcFiles]                       #Récupération de la liste des fichiers sources
    else:
        oGlobalCatalogFiles:dict = {}                                                           #Création de la liste des fichiers sources
    oGlobalCatalogFiles.update({sKeyFile:oCatalogFile})                                         #Enregistrement de la description du fichier analysé
    oGlobalCatalogHeader.update({cstKeyCatalogSrcFiles:oGlobalCatalogFiles})                    #Enregistrement de la nouvelle liste des fichiers sources
    
    if cstKeyCatalogCatalog in oGlobalCatalog:
        oGlobalAreas = oGlobalCatalog[cstKeyCatalogCatalog]                                     #Récupération de la liste des zones consolidés
    else:
        oGlobalAreas:dict = {}                                                                  #Création d'une liste des zones a consolider

    oAsAreas = ofileCatalog[cstKeyCatalogCatalog]                                             #Catalogue des Espace-aériens contenus dans le fichier analysé
    for sAsKey, oAs in oAsAreas.items():
        if isValidArea(sKeyFile, oAs):                                  #Exclure certaines zones
            oAs.update({cstKeyCatalogOrgFile:sKeyFile})                 #Ajout de la réfénce au fichier source
            sNewKey = str(oAs["id"]).strip()                            #Nouvelle identifiant de référence pour le catalogue global
            if sNewKey=="": sNewKey = makeNewKey()                      #Initialisation d'une clé non vide
            if   oFile[cstProcessType]==cstPtAdd:                       #Ajout systématique des zones (avec débloublonnage des 'id' automatisé)
                if sNewKey in oGlobalAreas:
                    sNewKey2 = makeNewKey(sNewKey, oGlobalAreas)        #Identification d'une nouvelle clé unique
                    oLog.info("Deduplication area for global catalog - orgId={0} --> newId={1}".format(sNewKey, sNewKey2, outConsole=False))
                    sNewKey = sNewKey2
                oGlobalAreas.update({sNewKey:oAs})                      #Ajoute la zone au catalogue global
                oLog.info("Add area in global catalog - ({0}){1}".format(sKeyFile, sNewKey, outConsole=False))
            elif oFile[cstProcessType]==cstPtAddDelta:                  #Ajout des zones qui ne sont pas déjà existante
                if sNewKey in oGlobalAreas:                             #Controle prealable de presence
                    oLog.info("Ignored area (existing in global catalog) - ({0}){1}".format(sKeyFile, sNewKey, outConsole=False))
                else:
                    oGlobalAreas.update({sNewKey:oAs})                  #Ajoute la zone au catalogue global
                    oLog.info("Add area in global catalog - ({0}){1}".format(sKeyFile, sNewKey, outConsole=False))
            else:
                oLog.error("Process type error - {0}".format(oFile[cstProcessType], outConsole=True))
    
    oGlobalCatalog.update({cstKeyCatalogCatalog:oGlobalAreas})                    #Enregistrement de la nouvelle liste des fichiers sources
    return

def poaffMergeFiles() -> None:
    bpaTools.createFolder(poaffOutPath)                             #Initialisation
    bpaTools.createFolder(poaffOutPath + referentialPath)           #Initialisation
    bpaTools.deleteFile(globalCatalog)                              #Purge du fichier
        
    for sKey, oFile in scriptProcessing.items():                    #Traitement des fichiers
        if oFile[cstExecute]:                                       #Flag prise en compte du fichier
            mergeCatalogFiles(sKey, oFile)                                  #Consolidation des fichiers

    #oLog.info("oGlobalCatalog:\n{0}".format(oGlobalCatalog, outConsole=False))
    bpaTools.writeJsonFile(globalCatalog, oGlobalCatalog)           #Sérialisation du fichier
    return

def parseFile(sKey:str, oFile:dict) -> bool:
    bpaTools.createFolder(oFile[cstOutPath])                        #Init dossier de sortie
    aixmCtrl = aixmReader.AixmControler(oFile[cstSrcFile], oFile[cstOutPath], sKey, oLog)     #Init controler
    ret = aixmCtrl.execParser(oOpts)                                #Execution des traitements
    return ret

def updateReferentials(sKey:str, oFile:dict) -> None:
    oGEH = GroundEstimatedHeight(oLog, oFile[cstOutPath], oFile[cstOutPath] + referentialPath, sKey + "@")
    oGEH.parseUnknownGroundHeightRef()                              #Execution des traitements
    return

def poaffGenerateFiles(sMsg:str=None) -> None:
    if sMsg!=None:
        oLog.warning("{0}".format(sMsg), outConsole=True)
    oLog.writeCommandLine(aArgs)                                    #Trace le contexte d'execution
    oLog.info("Loading module - {0}".format(aixmParserId), outConsole=True)

    for sKey, oFile in scriptProcessing.items():                    #Traitement des fichiers
        if oFile[cstExecute]:                                       #Flag prise en compte du fichier
            iPrevErr = oLog.CptCritical + oLog.CptError             #Nombre d'erreurs en pré-traitements
            parseFile(sKey, oFile)                                  #Creation des fichiers
            iActErr = oLog.CptCritical + oLog.CptError              #Nombre d'erreurs en post-traitements
            if iActErr!=iPrevErr:                                   #Si écart constaté
                updateReferentials(sKey, oFile)                     #Forcer mise à jour des référentiels d'altitudes
    return

def moveFile(sSrcPath:str, sSrcFile:str, sCpyFileName:str, sPoaffWebPageBuffer, sToken:str) -> None:
    sCpyFile = "{0}{1}{2}".format(poaffWebPath, "files/", sCpyFileName)
    shutil.copyfile(sSrcPath + sSrcFile, sCpyFile)
    oLog.info("Move file : {0} --> {1}".format(sSrcFile, sCpyFileName), outConsole=False)
    return sPoaffWebPageBuffer.replace(sToken, sCpyFileName)

def createPoaffWebPage(sHeadFileDate:str=None) -> None:
    sTemplateWebPage:str = "__template__Index-Main.htm"
    sNewWebPage:str = "index.htm"
    if sHeadFileDate==None:
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
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/" + referentialPath, "EuCtrl@airspacesCatalog.csv", sHeadFileDate + "airspacesCatalog.csv", sPoaffWebPageBuffer, "@@file@@CSV-airspacesCatalog@@")
    sPoaffWebPageBuffer = moveFile(outPath + "EuCtrl/" + referentialPath, "EuCtrl@airspacesCatalog.json", sHeadFileDate + "airspacesCatalog.json", sPoaffWebPageBuffer, "@@file@@JSON-airspacesCatalog@@")
    fVerionCatalog.write(sHeadFileDate + "airspacesCatalog.csv;" + sHeadFileDate[:-1] + ";" + sHeadFileDate[:-1] + ";Catalogue des espaces-aériens au format CSV\n")
    fVerionCatalog.write(sHeadFileDate + "airspacesCatalog.json;" + sHeadFileDate[:-1] + ";" + sHeadFileDate[:-1] + ";Catalogue des espaces-aériens au format JSON\n")

    fVerionCatalog.close()


    #### 2/ repository for CFD
    # GeoJSON and Catalog files
    shutil.copyfile(outPath + "EuCtrl/EuCtrl@airspaces-all.geojson", cfdWebPath + "/airspaces-all.geojson")
    shutil.copyfile(outPath + "EuCtrl/EuCtrl@airspaces-ifr.geojson", cfdWebPath + "/airspaces-ifr.geojson")
    shutil.copyfile(outPath + "EuCtrl/EuCtrl@airspaces-vfr.geojson", cfdWebPath + "/airspaces-vfr.geojson")
    shutil.copyfile(outPath + "EuCtrl/EuCtrl@airspaces-freeflight.geojson", cfdWebPath + "/airspaces-freeflight.geojson")
    shutil.copyfile(outPath + "EuCtrl/" + referentialPath + "EuCtrl@airspacesCatalog.csv", cfdWebPath + "/airspacesCatalog.csv")
    shutil.copyfile(outPath + "EuCtrl/" + referentialPath + "EuCtrl@airspacesCatalog.json", cfdWebPath + "/airspacesCatalog.json")


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
    sCallingContext = None

    oOpts = bpaTools.getCommandLineOptions(aArgs)                   #Arguments en dictionnaire
    oLog = bpaTools.Logger(appId, logFile, callingContext, linkContext, isSilent=bool(aixmReader.CONST.optSilent in oOpts))
    if aixmReader.CONST.optCleanLog in oOpts:
        oLog.resetFile()                                            #Clean du log si demandé

    #--------- creation des fichiers unitaires ----------
    poaffGenerateFiles()                                            #Creation des fichiers
    if (oLog.CptCritical + oLog.CptError) > 0:
        oLog.resetFile()                                            #Clean du log
        sCallingContext = "Forced reload by second phase"
        poaffGenerateFiles(sCallingContext)                         #Seconde tentative de creation des fichiers

    if (oLog.CptCritical + oLog.CptError) > 0:
        print()
        oLog.critical("Abort treatment - Show errors in log file", outConsole=True)
    else:
        poaffMergeFiles()                                           #Consolidation des fichiers
        if not(cstTestMode):
            createPoaffWebPage(None)                                #Preparation pour publication
            #createPoaffWebPage("20200715_")                        #Pour révision d'une publication

    print()
    if sCallingContext!=None:
        oLog.warning("{0}".format(sCallingContext), outConsole=True)
    oLog.Report()
    oLog.closeFile()

