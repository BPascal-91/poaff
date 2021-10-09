#!/usr/bin/env python3
import os, sys, shutil

try:
    import OpenairReader
except ImportError:
    sLocalSrc: str = "../../../openairParser/src/"               #Include local modules/librairies
    module_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(module_dir, sLocalSrc))
    import OpenairReader

try:
    import aixmReader
except ImportError:
    sLocalSrc: str = "../../../aixmParser/src/"                  #Include local modules/librairies
    module_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(module_dir, sLocalSrc))
    import aixmReader
from groundEstimatedHeight import GroundEstimatedHeight
import bpaTools                                                 #tools module of aixmParser software

try:
    from geojson2kml import Geojson2Kml
except ImportError:
    sLocalSrc: str = "../"                                       #Include local modules/librairies
    module_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(module_dir, sLocalSrc))
    from geojson2kml import Geojson2Kml
import poaffCst
#import xmlSIA


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

def makeOpenair2Aixm(sSrcPath:str, sSrcFile:str, sDstPath:str, sDstFile:str, sRootSchemaLocation:str) -> None:
    oParser = OpenairReader.OpenairReader(oLog)
    oParser.setFilters(sFilterClass, sFilterType, sFilterName)
    oParser.parseFile(sSrcPath + sSrcFile)
    oParser.oAixm.schemaLocation = sRootSchemaLocation + "_aixm_xsd-4.5b/AIXM-Snapshot.xsd"     #Set the dictionary
    oParser.oAixm.parse2Aixm4_5(sDstPath, sSrcFile, sDstFile)
    return

def makeAixm2Geojson(sSrcPath:str, sSrcFile:str, sDstPath:str, sDstFile:str) -> None:
    aArgs = [appName, aixmReader.CONST.frmtGEOJSON, aixmReader.CONST.typeAIRSPACES, aixmReader.CONST.optALL, aixmReader.CONST.optCleanLog]
    aArgs += [aixmReader.CONST.optEpsilonReduce + "=" + str(poaffCst.cstGeojsonEpsilonReduce)]
    oOpts = bpaTools.getCommandLineOptions(aArgs)
    aixmCtrl = aixmReader.AixmControler(sSrcPath + sSrcFile, sDstPath, "", oLog)        #Init controler
    aixmCtrl.execParser(oOpts)                                                          #Execution des traitements
    renameFile(sDstPath, "airspaces-all.geojson", sDstPath, sDstFile)
    return

def makeAixm2Openair(sSrcPath:str, sSrcFile:str, sDstPath:str, sDstFile:str) -> None:
    aArgs = [appName, aixmReader.CONST.frmtOPENAIR, aixmReader.CONST.typeAIRSPACES, aixmReader.CONST.optALL, aixmReader.CONST.optCleanLog]
    aArgs += [aixmReader.CONST.optOpenairDigitOptimize + "=" + str(poaffCst.cstOpenairDigitOptimize)]
    if mOpenairEpsilonReduce!=-1:
        aArgs += [aixmReader.CONST.optEpsilonReduce + "=" + str(mOpenairEpsilonReduce)]
    else:
        aArgs += [aixmReader.CONST.optEpsilonReduce + "=" + str(poaffCst.cstOpenairEpsilonReduce)]
    oOpts = bpaTools.getCommandLineOptions(aArgs)
    aixmCtrl = aixmReader.AixmControler(sSrcPath + sSrcFile, sDstPath, "", oLog)        #Init controler
    aixmCtrl.bOpenairOptimizePoint = True           #False-->'46:23:57 N 006:06:20 E' or True-->'46:23:57N 6:6:2E'
    #aixmCtrl.bOpenairOptimizeArc = False        #--> Ne pas optimiser l'Arc car l'alignement du 1er point de l'arc de cercle ne coincide souvent pas avec le point théorique du départ de l'arc !?
    aixmCtrl.execParser(oOpts)                                                          #Execution des traitements
    renameFile(sDstPath, "airspaces-all-gpsWithTopo.txt", sDstPath, sDstFile)
    return

def makeGeojson2Kml(sSrcPath:str, sSrcFile:str, sDstPath:str, sDstFile:str) -> None:
    oKml = Geojson2Kml(oLog)
    oKml.readGeojsonFile(sSrcPath + sSrcFile)
    sTilte: str = "Paragliding Openair Frensh Files"
    sDesc: str = "Created at: " + bpaTools.getNowISO() + "<br/>http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/"
    oKml.createKmlDocument(sTilte, sDesc)
    oKml.makeAirspacesKml(epsilonReduce=poaffCst.cstKmlEpsilonReduce)
    oKml.writeKmlFile(sDstPath + sDstFile, bExpand=1)
    oKml = None     #Free and clean file
    return

def makeAllFiles(sSrcPath:str, sSrcOpenairFile:str, sDstPath:str, sRootSchemaLocation:str) -> None:
    bpaTools.createFolder(sDstPath)        #Init dossier
    if not copyFile(sSrcPath, sSrcOpenairFile, sDstPath, sSrcOpenairFile):
        None
    else:
        #Files names
        sSrcOriginFile: str = sSrcOpenairFile.replace(".txt", "_org.txt")
        sSrcFinalFile: str = sSrcOpenairFile.replace(".txt", "_final.txt")
        sAixmFile: str = sSrcOpenairFile.replace(".txt", "_aixm45.xml")
        sGeojsonFile: str = sSrcOpenairFile.replace(".txt", ".geojson")
        sKmlFile: str = sSrcOpenairFile.replace(".txt", ".kml")

        #Aixm generator
        makeOpenair2Aixm(sDstPath, sSrcOpenairFile, sDstPath, sAixmFile, sRootSchemaLocation)

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
            #oLog.resetFile()                                   #Clean du log
            oLog.resetCpt()                                     #Reset compteurs sans effacement du log
            sMsg: str = "...oooOOO Forced reload by second phase OOOooo..."
            oLog.info("{0}".format(sMsg), outConsole=True)
            makeAixm2Geojson(sDstPath, sAixmFile, sDstPath, sGeojsonFile)

        iActErr:int = oLog.CptCritical + oLog.CptError
        if iActErr > 0:
            print()
            sMsg: str = "Abort treatment - Show errors in log file !"
            oLog.critical(sMsg, outConsole=True)
            return                                              #Abort treatments

        #Openair generator
        makeAixm2Openair(sDstPath, sAixmFile, sDstPath, sSrcFinalFile)

        #KML generator
        makeGeojson2Kml(sDstPath, sGeojsonFile, sDstPath, sKmlFile)
    return

#### Paramétrage de l'optimisation des tracés ####
def setConfEpsilonReduce(epsilonReduce:bool=None) -> None:
    poaffCst.cstGeojsonCfdEpsilonReduce  = 0.0    if epsilonReduce else -1        #0.0    - Suppression de doublons pour tracés GeoJSON en sortie CFD
    poaffCst.cstGeojsonEpsilonReduce     = 0.0001 if epsilonReduce else -1        #0.0001 - Simplification des tracés GeoJSON standard
    poaffCst.cstKmlCfdEpsilonReduce      = 0.0001 if epsilonReduce else -1        #0.0001 - Faible simplification des tracés KML en sortie CFD
    poaffCst.cstKmlEpsilonReduce         = 0.0005 if epsilonReduce else -1        #0.0005 - Réduction importante des tracés KML
    poaffCst.cstOpenairCfdEpsilonReduce  = 0.0    if epsilonReduce else -1        #0.0    - Suppression de doublons pour tracés Openair standards
    poaffCst.cstOpenairEpsilonReduce     = 0.0001 if epsilonReduce else -1        #0.0001 - Base de réduction des tracés Openair
    poaffCst.cstOpenairEpsilonReduceMR   = 0.0002 if epsilonReduce else -1        #0.0002 - Base de réduction moyenne des tracés Openair pour les zones régionnales "ISO_Perimeter=Partial" (gpsWithTopo or gpsWithoutTopo)[geoFrenchNorth, geoFrenchSouth, geoFrenchNESW, geoFrenchVosgesJura, geoFrenchPyrenees, geoFrenchAlps]
    poaffCst.cstOpenairDigitOptimize     = 0      if epsilonReduce else -1        #openairDigitOptimize=-1 / 0 / 2
    return



### Gestion des Parcs naturels
def parcsConsolidation() -> None:
    sAllOpenair: str = ""
    oParcs:dict = {
        "Jura":             ["Jura", "20210324_Parc-Jura.txt"],
        "Bauges":           ["Bauges", "20210104_FFVL_ParcBauges.txt"],
        "AnnecyMarais":     ["AnnecyMarais", "20200120_FFVL_ParcAnnecyMarais.txt"],
        "Passy":            ["Passy", "20191129_FFVL_ParcPassy.txt"],
        "Sixt-Passy":       ["Sixt-Passy", "20210305_Sixt-Passy.txt"],
        "AiguillesRouges":  ["AiguillesRouges", "20210304_AiguillesRouges.txt"],
        "Contamines":       ["Contamines", "20210304_Contamines.txt"],
        "GrandeSassiere":   ["GrandeSassiere", "20210304_GrandeSassiere.txt"],
        "Vanoise":          ["Vanoise", "20210325_Vanoise.txt"],
        "Vercors":          ["Vercors", "20210305_Vercors.txt"],
        "Ecrins":           ["Ecrins", "20210304_Ecrins.txt"],
        "Mercantour":       ["Mercantour", "20210304_Mercantour.txt"],
        "Champagne":        ["Champagne", "20210202_BPa_ParcsNat_Champagne.txt"],
        "Cevennes":         ["Cevennes", "20210324_PascalW_ParcCevennes.txt"],
        "BaieDeSomme":      ["BaieDeSomme", "20200729_SergeR_ParcNat_BaieDeSomme.txt"],
        "Vauville":         ["Vauville", "20210615_Mare-de-Vauville.txt"],
        "Hourtin":          ["Hourtin", "20200729_SergeR_ParcNat_Hourtin.txt"],
        "Pyrenees":         ["Pyrenees", "20210323_Pyrenees_hr.txt"],
        "Ordessa":          ["Ordessa", "20210304_Ordessa.txt"],
        "Calanques":        ["Calanques", "20210420_Calanques.txt"],
        "PortCros":         ["PortCros", "20210420_PortCros.txt"],
        "Scandola":         ["Scandola", "20210420_Scandola.txt"],
        "Italie":           ["Italie", "20210324_ParcsItaliens.txt"]
    }
    iConstructParc: int = 2                            #Phase de construction des Parcs: 0=Rien, 1=Phase1, 2=Phase2
    if iConstructParc == 1:
        ###(deb) Phase 1 - Construction des fichiers unitaire pour mise au point du tracé d'un unique parc
        aParc = oParcs["Vauville"]
        sInPath: str = cstPoaffInPath + "Parcs/" + aParc[0] + "/"
        sOutPath: str = sInPath + "map/"
        makeAllFiles(sInPath, aParc[1], sOutPath, cstPoaffInPath)
        ###(end) Phase 1 - Construction des fichiers unitaire pour mise au point du tracé d'un unique parc

    if iConstructParc == 2:
        ###(deb) Phase 2a - Consolidation de tous les parcs dans un unique fichier pour traitement automatisé via poaff
        oUniqueKey:dict={}
        for sKey, aParc in oParcs.items():
            sInPath: str = cstPoaffInPath + "Parcs/" + aParc[0] + "/"
            sSrcFile = sInPath + aParc[1]
            sAllOpenair += "*"*(20+len(sSrcFile)) + "\n"
            sAllOpenair += "*"*5 + " source file - " + sSrcFile + "\n"
            sAllOpenair += "*"*(20+len(sSrcFile)) + "\n"
            fopen = open(sSrcFile, "rt", encoding="cp1252", errors="ignore")
            lines = fopen.readlines()
            sMsg = "Parsing openair file - {}".format(sSrcFile)
            oLog.info("{}".format(sMsg), outConsole=True)
            barre = bpaTools.ProgressBar(len(lines), 20, title=sMsg)
            idx = 0
            for line in lines:
                idx+=1
                #Verifications pour qualité des données
                sTocken: str = "*AUID"
                if line[:len(sTocken)] == sTocken:
                    #Ex: '*AUID GUId=! UId=! Id=PJuraNord'
                    aAUID = line.split(" ")
                    #Contrôle que les identifiants ne sont pas renseignés
                    if aAUID[1]!="GUId=!" or aAUID[2]!="UId=!":
                        raise Exception("Error - Identification error in line -" + line)
                    #Contrôle que l'identifiant local est bien unique dans l'ensemble des zones consolidés
                    aAUID[3] = aAUID[3].replace("\n", "")
                    sLocKey: str = aAUID[3].split("=")[1]
                    sFind: str = oUniqueKey.get(sLocKey, "...")
                    if sFind == sLocKey:
                        raise Exception("Error - Duplicate identification " + aAUID[3] + " with " + sFind)
                    else:
                        oUniqueKey.update({sLocKey:aAUID[3] + " in " + sSrcFile})
                sAllOpenair += line
                barre.update(idx)
            sAllOpenair += "\n"*2
            barre.reset()

        sOutPath: str = cstPoaffInPath + "Parcs/__All-Parcs/"
        sOutFile: str = bpaTools.getDate(bpaTools.getNow()) + "_All-Parcs.txt"
        if sAllOpenair:
            sMsg = "Construct consolidated openair file - {}".format(sOutFile)
            oLog.info("{}".format(sMsg), outConsole=True)
            bpaTools.writeTextFile(sOutPath + sOutFile, sAllOpenair)
        ###(end) Phase 2a - Consolidation de tous les parcs dans un unique fichier pour traitement automatisé via poaff

        ###(deb) Phase 2b - Construction de l'aixm et des fichiers assimilés sur la base des parcs consolidés
        sInPath: str = sOutPath
        sOutPath: str = sInPath + "map/"
        makeAllFiles(sInPath, sOutFile, sOutPath, cstPoaffInPath)
        ###(fin) Phase 2b - Construction de l'aixm et des fichiers assimilés sur la base des parcs consolidés
    return



if __name__ == '__main__':
    ### Context applicatif
    callingContext: str = "Paragliding-OpenAir-FrenchFiles"         #Your app calling context
    appName: str = bpaTools.getFileName(__file__)
    appPath: str = bpaTools.getFilePath(__file__)            #or your app path
    appVersion: str = "1.1.2"                                   #or your app version
    appId: str = appName + " v" + appVersion
    cstPoaffInPath: str = "../../input/"
    cstPoaffOutPath: str = "../../output/"
    logFile: str = cstPoaffOutPath + "_" + appName + ".log"
    sFilterClass:list=None; sFilterType:list=None; sFilterName:list=None

    oLog = bpaTools.Logger(appId,logFile)
    oLog.resetFile()

    mOpenairEpsilonReduce:float     = -1
    epsilonReduce:bool              = True      #Normaly = True  or False for generate without optimization
    setConfEpsilonReduce(epsilonReduce)         #### Paramétrage de l'optimisation des tracés ####


    parcsConsolidation()


    """
    sInPath: str = cstPoaffInPath  + "Tests/"
    sPOutPath: str = cstPoaffOutPath + "Tests/map/"
    #sSrcOpenairFile: str = "99999999_BPa_TestOpenair-RTBA.txt"
    #sSrcOpenairFile: str = "99999999_BPa_Test4Circles_Arcs.txt"  #99999999_BPa_Test4Circles.txt
    #sSrcOpenairFile: str = "99999999_BPa_Test4Circles_AlignArcs.txt"
    sSrcOpenairFile: str = "99999999_ComplexArea.txt"
    makeAllFiles(sInPath, sSrcOpenairFile, sPOutPath, cstPoaffInPath)
    """


    """
    sInPath: str = cstPoaffInPath  + "BPa/"
    sPOutPath: str = cstPoaffOutPath + "Tests/map/"
    sSrcOpenairFile: str = "20210528_BPa_FR-ZSM_Protection-des-rapaces.txt"
    #sSrcOpenairFile: str = "20210116_BPa_FR-SIA-SUPAIP.txt"
    #sSrcOpenairFile: str = "20210304_BPa_ZonesComplementaires.txt"
    #sFilterClass=["ZSM", "GP"]
    #sFilterName=["LaDaille", "LeFornet", "Bonneval", "Termignon", "PERCNOPTERE", "LeVillaron"]
    makeAllFiles(sInPath, sSrcOpenairFile, sPOutPath, cstPoaffInPath)
    """


    """
    sInPath: str = cstPoaffInPath  + "FFVL/"
    sPOutPath: str = cstPoaffOutPath + "Tests/map/"
    sSrcOpenairFile: str = "20210214_FFVL_ProtocolesParticuliers_BPa.txt"
    makeAllFiles(sInPath, sSrcOpenairFile, sPOutPath, cstPoaffInPath)
    """


    """
    ###--- Ctrl with all french area --
    sPoaffPublicationPathName: str    = "_POAFF_www/files/"
    sInPath: str = cstPoaffOutPath  + sPoaffPublicationPathName
    sPOutPath: str = cstPoaffOutPath + "Tests/map/"
    sSrcOpenairFile: str = "20210111_airspaces-freeflight-gpsWithTopo-geoFrenchAll.txt"
    #### Strat - Samples of specific filters ###
    #sFilterClass = ["ZSM"]
    #sFilterClass = ["ZSM", "GP"]
    #sFilterType = ["TMA"]
    #sFilterName = ["LYON"]
    #sFilterName = ["Faucon Pelerin","Megeve"]
    #sFilterClass = ["C"]; sFilterType=["TMA"]; sFilterName=["LYON"]
    #### End - Samples of specific filters ###
    makeAllFiles(sInPath, sSrcOpenairFile, sPOutPath, cstPoaffInPath)
    """


    """
    ###--- PWC-FrenchAlps --
    sPwcPathName: str = "FFVL/PWC-FrenchAlps/"
    sInPath: str = cstPoaffInPath  + sPwcPathName
    sPOutPath: str = cstPoaffOutPath + sPwcPathName
    sSrcOpenairFile: str = "20210120_PWC-FrenchAlps_Airspace-mondiaux_BPa-20210120.txt"
    #sFilterClass=["ZSM", "GP"]
    makeAllFiles(sInPath, sSrcOpenairFile, sPOutPath, "../" + cstPoaffInPath)
    """


    #Clotures
    print()
    oLog.Report()
    oLog.closeFile
