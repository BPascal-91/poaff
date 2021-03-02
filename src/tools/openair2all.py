#!/usr/bin/env python3
import os, sys, shutil

try:
    import OpenairReader
except ImportError:
    sLocalSrc:str = "../../../openairParser/src/"               #Include local modules/librairies
    module_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(module_dir, sLocalSrc))
    import OpenairReader

try:
    import aixmReader
except ImportError:
    sLocalSrc:str = "../../../aixmParser/src/"                  #Include local modules/librairies
    module_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(module_dir, sLocalSrc))
    import aixmReader
from groundEstimatedHeight import GroundEstimatedHeight
import bpaTools                                                 #tools module of aixmParser software

try:
    from geojson2kml import Geojson2Kml
except ImportError:
    sLocalSrc:str = "../"                                       #Include local modules/librairies
    module_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(module_dir, sLocalSrc))
    from geojson2kml import Geojson2Kml

import xmlSIA

def copyFile(sSrcPath:str, sSrcFile:str, sDstPath:str, sDstFile:str) -> bool:
    if os.path.exists(sSrcPath + sSrcFile):
        shutil.copyfile(sSrcPath + sSrcFile, sDstPath + sDstFile)
        oLog.info("Copy file : {0} --> {1}".format(sSrcFile, sDstFile), outConsole=False)
        return True
    else:
        oLog.warning("Uncopy file (not exist): {0}".format(sSrcPath + sSrcFile), outConsole=False)
        return False

def renameFile(sSrcPath:str, sSrcFile:str, sDstPath:str, sDstFile:str) -> bool:
    if str(sSrcPath + sSrcFile) == str(sDstPath + sDstFile):
        oLog.ctricical("renameFile() Error file source must be different from the target: {0}".format(sSrcPath + sSrcFile), outConsole=False)
    if os.path.exists(sSrcPath + sSrcFile):
        if os.path.exists(sDstPath + sDstFile):
            os.remove(sDstPath + sDstFile)
        os.rename(sSrcPath + sSrcFile, sDstPath + sDstFile)
        oLog.info("Rename file : {0} --> {1}".format(sSrcFile, sDstFile), outConsole=False)
        return True
    else:
        oLog.warning("Unrename file (not exist): {0}".format(sSrcFile), outConsole=False)
        return False


def makeOpenair2Aixm(sSrcPath:str, sSrcFile:str, sDstPath:str, sDstFile:str) -> None:
    oParser = OpenairReader.OpenairReader(oLog)
    oParser.setFilters(sFilterClass, sFilterType, sFilterName)
    oParser.parseFile(sSrcPath + sSrcFile)
    oParser.oAixm.schemaLocation = sRootSchemaLocation + "_aixm_xsd-4.5b/AIXM-Snapshot.xsd"     #Set the dictionary
    oParser.oAixm.parse2Aixm4_5(sDstPath, sSrcFile, sDstFile)
    return

def makeAixm2Geojson(sSrcPath:str, sSrcFile:str, sDstPath:str, sDstFile:str) -> None:
    aArgs = [appName, aixmReader.CONST.frmtGEOJSON, aixmReader.CONST.typeAIRSPACES, aixmReader.CONST.optALL, aixmReader.CONST.optCleanLog]
    aArgs += [aixmReader.CONST.optEpsilonReduce + "=0.0001"]
    oOpts = bpaTools.getCommandLineOptions(aArgs)
    aixmCtrl = aixmReader.AixmControler(sSrcPath + sSrcFile, sDstPath, "", oLog)        #Init controler
    aixmCtrl.execParser(oOpts)                                                          #Execution des traitements
    renameFile(sDstPath, "airspaces-all.geojson", sDstPath, sDstFile)
    return

def makeAixm2Openair(sSrcPath:str, sSrcFile:str, sDstPath:str, sDstFile:str) -> None:
    aArgs = [appName, aixmReader.CONST.frmtOPENAIR, aixmReader.CONST.typeAIRSPACES, aixmReader.CONST.optALL, aixmReader.CONST.optCleanLog]
    oOpts = bpaTools.getCommandLineOptions(aArgs)
    aixmCtrl = aixmReader.AixmControler(sSrcPath + sSrcFile, sDstPath, "", oLog)        #Init controler
    aixmCtrl.bOpenairOptimizePoint = False
    #aixmCtrl.bOpenairOptimizeArc = False        #--> Ne pas optimiser l'Arc car l'alignement du 1er point de l'arc de cercle ne coincide souvent pas avec le point théorique du départ de l'arc !?
    aixmCtrl.execParser(oOpts)                                                          #Execution des traitements
    renameFile(sDstPath, "airspaces-all-gpsWithTopo.txt", sDstPath, sDstFile)
    return

def makeGeojson2Kml(sSrcPath:str, sSrcFile:str, sDstPath:str, sDstFile:str) -> None:
    oKml = Geojson2Kml()
    oKml.readGeojsonFile(sSrcPath + sSrcFile)
    sTilte:str = "Paragliding Openair Frensh Files"
    sDesc:str  = "Created at: " + bpaTools.getNowISO() + "<br/>http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/"
    oKml.createKmlDocument(sTilte, sDesc)
    oKml.makeAirspacesKml(epsilonReduce=0.005)                     #epsilonReduce=0 / epsilonReduce=0.005
    oKml.writeKmlFile(sDstPath + sDstFile, bExpand=1)
    oKml = None     #Free and clean file
    return

def makeAllFiles(sSrcPath:str, sSrcOpenairFile:str, sDstPath:str) -> None:
    bpaTools.createFolder(sDstPath)        #Init dossier
    if not copyFile(sSrcPath, sSrcOpenairFile, sDstPath, sSrcOpenairFile):
        None
    else:
        #Files names
        sSrcOriginFile:str  = sSrcOpenairFile.replace(".txt", "_org.txt")
        sSrcFinalFile:str   = sSrcOpenairFile.replace(".txt", "_final.txt")
        sAixmFile:str       = sSrcOpenairFile.replace(".txt", "_aixm45.xml")
        sGeojsonFile:str    = sSrcOpenairFile.replace(".txt", ".geojson")
        sKmlFile:str        = sSrcOpenairFile.replace(".txt", ".kml")

        #Aixm generator
        makeOpenair2Aixm(sDstPath, sSrcOpenairFile, sDstPath, sAixmFile)

        #Rename original file with "_org" flag
        renameFile(sDstPath, sSrcOpenairFile, sDstPath, sSrcOriginFile)

        #GeoJSON generator
        iPrevErr:int = oLog.CptCritical + oLog.CptError         #Nombre d'erreurs en pré-traitements
        makeAixm2Geojson(sDstPath, sAixmFile, sDstPath, sGeojsonFile)
        iActErr:int = oLog.CptCritical + oLog.CptError          #Nombre d'erreurs en post-traitements
        if iActErr!=iPrevErr:                                   #Si écart constaté
            #Mise à jour des référentiels d'altitudes
            oGEH = GroundEstimatedHeight(oLog, sDstPath, sDstPath + "referentials/", "")
            oGEH.parseUnknownGroundHeightRef(sDstPath + sGeojsonFile)       #Execution des traitements

            #Nouvelle tentative de regénération des fichiers
            oLog.resetFile()                                    #Clean du log
            sMsg:str = "Forced reload by second phase"
            oLog.warning("{0}".format(sMsg), outConsole=True)
            makeAixm2Geojson(sDstPath, sAixmFile, sDstPath, sGeojsonFile)

        iActErr:int = oLog.CptCritical + oLog.CptError
        if iActErr > 0:
            print()
            sMsg:str = "Abort treatment - Show errors in log file !"
            oLog.critical(sMsg, outConsole=True)
            return                                              #Abort treatments

        #Openair generator
        makeAixm2Openair(sDstPath, sAixmFile, sDstPath, sSrcFinalFile)

        #KML generator
        makeGeojson2Kml(sDstPath, sGeojsonFile, sDstPath, sKmlFile)
    return


if __name__ == '__main__':
    ### Context applicatif
    callingContext:str  = "Paragliding-OpenAir-FrenchFiles"         #Your app calling context
    appName:str         = bpaTools.getFileName(__file__)
    appPath:str         = bpaTools.getFilePath(__file__)            #or your app path
    appVersion:str      = "1.0.0"                                   #or your app version
    appId:str           = appName + " v" + appVersion
    cstPoaffInPath:str  = "../../input/"
    cstPoaffOutPath:str = "../../output/"
    logFile:str         = cstPoaffOutPath + "_" + appName + ".log"
    sFilterClass:list=None; sFilterType:list=None; sFilterName:list=None

    oLog = bpaTools.Logger(appId,logFile)
    oLog.resetFile()


    sInPath:str         = cstPoaffInPath  + "Tests/"
    sPOutPath:str       = cstPoaffOutPath + "Tests/map/"
    sRootSchemaLocation:str = cstPoaffInPath
    #sSrcOpenairFile:str  = "99999999_BPa_TestOpenair-RTBA.txt"
    #sSrcOpenairFile:str  = "99999999_BPa_Test4Circles_Arcs.txt"  #99999999_BPa_Test4Circles.txt
    #sSrcOpenairFile:str  = "99999999_BPa_Test4Circles_AlignArcs.txt"
    sSrcOpenairFile:str  = "99999999_ComplexArea.txt"
    makeAllFiles(sInPath, sSrcOpenairFile, sPOutPath)


    """
    sInPath:str         = cstPoaffInPath  + "BPa/"
    sPOutPath:str       = cstPoaffOutPath + "Tests/map/"
    sRootSchemaLocation:str = cstPoaffInPath
    #sSrcOpenairFile:str  = "20210208_BPa_FR-ZSM_Protection-des-rapaces.txt"
    sSrcOpenairFile:str  = "20210116_BPa_FR-SIA-SUPAIP.txt"
    #sFilterClass=["ZSM", "GP"]
    #sFilterName=["LaDaille", "LeFornet", "Bonneval", "Termignon", "PERCNOPTERE", "LeVillaron"]
    makeAllFiles(sInPath, sSrcOpenairFile, sPOutPath)
    """

    """
    sInPath:str         = cstPoaffInPath  + "FFVL/"
    sPOutPath:str       = cstPoaffOutPath + "Tests/map/"
    sRootSchemaLocation:str = cstPoaffInPath
    #sSrcOpenairFile:str  = "20200120_FFVL_ParcAnnecyMaraisBoutDuLac.txt"
    #sSrcOpenairFile:str  = "20210202_BPa_ParcsNat_ChampagneBourgogne.txt"
    #sSrcOpenairFile:str   = "20210202_PascalW_ParcCevennes.txt"
    sSrcOpenairFile:str  = "20210214_FFVL_ProtocolesParticuliers_BPa.txt"
    makeAllFiles(sInPath, sSrcOpenairFile, sPOutPath)
    """


    """
    ###--- Ctrl with all french area --
    sPoaffPublicationPathName:str    = "_POAFF_www/files/"
    sInPath:str         = cstPoaffOutPath  + sPoaffPublicationPathName
    sPOutPath:str       = cstPoaffOutPath + "Tests/map/"
    sRootSchemaLocation:str = cstPoaffInPath
    sSrcOpenairFile:str  = "20210111_airspaces-freeflight-gpsWithTopo-geoFrenchAll.txt"
    #### Strat - Samples of specific filters ###
    #sFilterClass=["ZSM"]
    #sFilterClass=["ZSM", "GP"]
    #sFilterType=["TMA"]
    #sFilterName=["LYON"]
    #sFilterName=["Faucon Pelerin","Megeve"]
    #sFilterClass=["C"]; sFilterType=["TMA"]; sFilterName=["LYON"]
    #### End - Samples of specific filters ###
    makeAllFiles(sInPath, sSrcOpenairFile, sPOutPath)
    """


    """
    ###--- PWC-FrenchAlps --
    sPwcPathName:str    = "FFVL/PWC-FrenchAlps/"
    sInPath:str         = cstPoaffInPath  + sPwcPathName
    sPOutPath:str       = cstPoaffOutPath + sPwcPathName
    sRootSchemaLocation:str = "../" + cstPoaffInPath
    sSrcOpenairFile:str  = "20210120_PWC-FrenchAlps_Airspace-mondiaux_BPa-20210120.txt"
    #sFilterClass=["ZSM", "GP"]
    makeAllFiles(sInPath, sSrcOpenairFile, sPOutPath)
    """



    #Clotures
    print()
    oLog.Report()
    oLog.closeFile
