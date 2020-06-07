#!/usr/bin/env python3

### Local reference of modules or librairies
aixmParserAppName   = "aixmParser"
aixmParserLocalSrc  = "../../aixmParser/src/"

### For reference local libraries
import os
import sys
module_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(module_dir, aixmParserLocalSrc))

### Include local modules/librairies
import bpaTools
import aixmReader
from groundEstimatedHeight import GroundEstimatedHeight


### Context applicatif
aixmParserVersion   = bpaTools.getVersionFile(aixmParserLocalSrc)
aixmParserId        = aixmParserAppName + " v" + aixmParserVersion
appName             = bpaTools.getFileName(__file__)
appPath             = bpaTools.getFilePath(__file__)
appVersion          = bpaTools.getVersionFile()
appId               = appName + " v" + appVersion
outPath             = appPath + "../output/"
logFile             = outPath + "_" + appName + ".log"
bpaTools.createFolder(outPath)                                      #Init dossier de sortie

callingContext      = "Paragliding-OpenAir-FrenchFiles"             #Your app calling context
linkContext         = "http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/"


####  Liste des fichiers disponibles  ####
cstID = "ID"
cstSrcFile = "srcFile"
cstOutPath = "outPath"
scriptProcessing = {
    "BPa-ParcCevennes": {cstOutPath:"../output/BPa/", cstSrcFile:"../input/BPa/20190401_WPa_ParcCevennes_aixm45.xml"},
    "BPa-Birds":        {cstOutPath:"../output/BPa/", cstSrcFile:"../input/BPa/20200510_BPa_FR-ZSM_Protection-des-rapaces_aixm45.xml"},
    "BPa-ZonesComp":    {cstOutPath:"../output/BPa/", cstSrcFile:"../input/BPa/20191210_BPa_ZonesComplementaires_aixm45.xml"},
    "FFVP-Parcs":       {cstOutPath:"../output/FFVP/", cstSrcFile:"../input/FFVP/20191214_FFVP_ParcsNat_aixm45.xml"},
    "FFVP-Birds":       {cstOutPath:"../output/FFVP/", cstSrcFile:"../input/FFVP/20191214_FFVP_BirdsProtect_aixm45.xml"},
    #"SIA":              {cstOutPath:"../output/SIA/", cstSrcFile:"../input/SIA/20200618_aixm4.5_SIA-FR.xml"},
    #"EuCtrl":           {cstOutPath:"../output/EuCtrl/", cstSrcFile:"../input/EuCtrl/20200326_aixm4.5_Eurocontrol-FR.xml"}
}
    

####  Options d'appels  ####
#aArgs = [appName, "-Fall", "-Tall", aixmReader.CONST.optALL, aixmReader.CONST.optIFR, aixmReader.CONST.optVFR, aixmReader.CONST.optFreeFlight, aixmReader.CONST.optCleanLog]
aArgs = [appName, "-Fall", aixmReader.CONST.typeAIRSPACES, aixmReader.CONST.optFreeFlight, aixmReader.CONST.optCleanLog]


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


if __name__ == '__main__':
    ####  Préparation d'appel ####
    oOpts = bpaTools.getCommandLineOptions(aArgs)                   #Arguments en dictionnaire
    oLog = bpaTools.Logger(appId, logFile, callingContext, linkContext, isSilent=bool(aixmReader.CONST.optSilent in oOpts))
    if aixmReader.CONST.optCleanLog in oOpts:
        oLog.resetFile()                                            #Clean du log si demandé

    sCallingContext = None
    poaffGenerateFiles()
    if (oLog.CptCritical + oLog.CptError) > 0:
        oLog.resetFile()                                            #Clean du log
        sCallingContext = "Forced reload by second phase"
        poaffGenerateFiles(sCallingContext)

    print()
    if sCallingContext!=None:
        oLog.warning("{0}".format(sCallingContext), outConsole=True)
    oLog.Report()
    oLog.closeFile()

