#!/usr/bin/env python3

import os
import sys
import shutil

try:
    import bpaTools
except ImportError:    
    ### Include local modules/librairies  ##
    aixmParserLocalSrc  = "../../aixmParser/src/"
    module_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(module_dir, aixmParserLocalSrc))
    import bpaTools

import poaffCst
import geoRefArea

###  Context applicatif  ####
appName                 = bpaTools.getFileName(__file__)
appPath                 = bpaTools.getFilePath(__file__)
appVersion              = bpaTools.getVersionFile()
appId                   = appName + " v" + appVersion
outPath                 = appPath + "../output/"
logFile                 = outPath + "_" + appName + ".log"

###  Environnement applicatif  ###
cstTemplateMoveTo:str       = "__template__Index-MoveP2P.htm"
cstFinalIndexFile:str       = "index.htm"
cstTemplateWebPage:str      = "__template__Index-Main.htm"

aTypeFiles:list =   [ ["-all"       , "Cartographie complète de l'espace aérien (IFR + VFR)"], \
                      ["-ifr"       , "Cartographie de l'espace aérien IFR (zones majoritairement situées au dessus du niveau FL115)"], \
                      ["-vfr"       , "Cartographie de l'espace aérien VFR (zones situées en dessous le niveau FL115)"], \
                      ["-ffvl-cfd"  , "Cartographie spécifique pour injection dans l'outillage de la CFD FFVL"], \
                      ["-freeflight", "Cartographie de l'espace aérien dédiée Vol-Libre (VFR dessous FL115)"]]

class PoaffWebPage:
    
    def __init__(self, oLog, outPath:str)-> None:
        bpaTools.initEvent(__file__, oLog)
        self.oLog:bpaTools.Logger   = oLog
        self.outPath:str            = outPath
        self.sourcesPath:str        = self.outPath + poaffCst.cstPoaffOutPath
        self.publishPath:str        = self.outPath + poaffCst.cstPoaffWebPath
        self.publishPathFiles:str   = self.publishPath + poaffCst.cstPoaffWebPathFiles
        self.publishPathCfd:str     = self.outPath + poaffCst.cstCfdWebPath
        self.sWebPageBuffer:str     = None
        self.sHeadFileDate:str      = "{0}_".format(bpaTools.getDateNow())
        self.aCatalogFiles:list     = None
        return

    def createPoaffWebPage(self, sHeadFileDate:str=None) -> None:
        self.aCatalogFiles = []
        
        if sHeadFileDate!=None:
            self.sHeadFileDate = sHeadFileDate
    
        #### 1/ Recup du modèle page Web
        fTemplate = open(self.publishPath + cstTemplateWebPage, "r", encoding="utf-8", errors="ignore")   #or encoding="cp1252"
        self.sWebPageBuffer = fTemplate.read()
        fTemplate.close()

        #### 2/ Calalog files
        srcPath = self.sourcesPath + poaffCst.cstReferentialPath
        srcFileName = poaffCst.cstGlobalHeader + poaffCst.cstSeparatorFileName + poaffCst.cstCatalogFileName
        dstFileName = self.sHeadFileDate + poaffCst.cstCatalogFileName
        sTitle = "Catalogue des espaces-aériens au format JSON"
        if self.copyFile(srcPath, srcFileName, self.publishPathFiles, dstFileName):
            self.publishFile(dstFileName, "@@file@@JSON-airspacesCatalog@@", sTitle)
            #Duplication du fichier dans le repo pour export CFD
            #self.copyFile(srcPath, srcFileName, self.publishPathCfd, dstFileName)
            #Duplication du fichier "LastVersion"
            dstFileName2 = dstFileName.replace(self.sHeadFileDate, poaffCst.cstLastVersionFileName)
            if self.copyFile(srcPath, srcFileName, self.publishPathFiles, dstFileName2):
                self.aCatalogFiles.append(dstFileName2 + ";" + self.sHeadFileDate[:-1] + ";" + self.sHeadFileDate[:-1] + ";" + sTitle)
        sTitle = "Catalogue des espaces-aériens au format CSV"
        srcFileName = srcFileName.replace(".json", ".csv")
        dstFileName = self.sHeadFileDate + str(poaffCst.cstCatalogFileName).replace(".json", ".csv")
        if self.copyFile(srcPath, srcFileName, self.publishPathFiles, dstFileName):
            self.publishFile(dstFileName, "@@file@@CSV-airspacesCatalog@@", sTitle)
            #Duplication du fichier dans le repo pour export CFD
            #self.copyFile(srcPath, srcFileName, self.publishPathCfd, dstFileName)
            #Duplication du fichier "LastVersion"
            dstFileName2 = dstFileName.replace(self.sHeadFileDate, poaffCst.cstLastVersionFileName)
            if self.copyFile(srcPath, srcFileName, self.publishPathFiles, dstFileName2):
                self.aCatalogFiles.append(dstFileName2 + ";" + self.sHeadFileDate[:-1] + ";" + self.sHeadFileDate[:-1] + ";" + sTitle)
        
        #### 3/ GeoJSON files
        sComplementaryFiles:str = ""
        #Déclinaison de toutes les typologies de fichier racine
        for aTypeFile in aTypeFiles:
            srcFileName = poaffCst.cstGlobalHeader + poaffCst.cstSeparatorFileName + str(poaffCst.cstAsAllGeojsonFileName).replace("-all", aTypeFile[0])
            dstFileName = str(self.sHeadFileDate + poaffCst.cstAsAllGeojsonFileName).replace("-all", aTypeFile[0])
            if self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName):
                sToken = str("@@file@@GeoJSON-airspaces-all@@").replace("-all", aTypeFile[0])
                self.publishFile(dstFileName, sToken, aTypeFile[1])
                if aTypeFile[0]=="-ffvl-cfd":
                    #Duplication du fichier dans le repo pour export CFD
                    #self.copyFile(self.sourcesPath, srcFileName, self.publishPathCfd, dstFileName)
                    #Duplication du fichier "LastVersion"
                    dstFileName2 = dstFileName.replace(self.sHeadFileDate, poaffCst.cstLastVersionFileName)
                    if self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName2):
                        self.aCatalogFiles.append(dstFileName2 + ";" + self.sHeadFileDate[:-1] + ";" + self.sHeadFileDate[:-1] + ";" + aTypeFile[1])
                elif aTypeFile[0]=="-freeflight":
                    #Déclinaison de toutes les régionalisations
                    for sAreaKey, oAreaRef in geoRefArea.GeoRefArea().AreasRef.items():
                        srcFileName2 = str(srcFileName).replace(aTypeFile[0], aTypeFile[0] + "-" + sAreaKey)
                        dstFileName2 = str(dstFileName).replace(aTypeFile[0], aTypeFile[0] + "-" + sAreaKey)
                        if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2):
                            sComplementaryFiles += self.makeLink4File(dstFileName2, aTypeFile[1] + " / " + oAreaRef[2]) + " | "
                else:
                    sComplementaryFiles += self.makeLink4File(dstFileName, aTypeFile[1]) + " | "
        self.sWebPageBuffer = self.sWebPageBuffer.replace("@@file@@GeoJSON-airspaces-othersfileslist@@", sComplementaryFiles)


        #### 4a/ Openair files au format "-gpsWithTopo"
        sComplementaryFiles:str = ""
        #Déclinaison de toutes les typologies de fichier racine
        for aTypeFile in aTypeFiles:
            srcFileName = poaffCst.cstGlobalHeader + poaffCst.cstSeparatorFileName + str(poaffCst.cstAsAllOpenairFileName).replace("-all", aTypeFile[0])
            dstFileName = str(self.sHeadFileDate + poaffCst.cstAsAllOpenairFileName).replace("-all", aTypeFile[0])
            if self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName):
                sToken = str("@@file@@Openair-airspaces-all"+ poaffCst.cstWithTopo + "@@").replace("-all", aTypeFile[0])
                sDescription:str = aTypeFile[1] + " [" + poaffCst.cstWithTopo[1:] + "]"
                self.publishFile(dstFileName, sToken, sDescription)
                self.publishFilesExeptDays(sToken, srcFileName, dstFileName, aTypeFile[1], poaffCst.cstWithTopo[1:])
                if aTypeFile[0]=="-ffvl-cfd":
                    #Duplication du fichier dans le repo pour export CFD
                    #self.copyFile(self.sourcesPath, srcFileName, self.publishPathCfd, dstFileName)
                    #Duplication du fichier "LastVersion"
                    dstFileName2b = dstFileName.replace(self.sHeadFileDate, poaffCst.cstLastVersionFileName)
                    if self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName2b):
                        self.aCatalogFiles.append(dstFileName2b + ";" + self.sHeadFileDate[:-1] + ";" + self.sHeadFileDate[:-1] + ";" + aTypeFile[1])
                elif aTypeFile[0]=="-freeflight":
                    #Déclinaison de toutes les régionalisations
                    for sAreaKey, oAreaRef in geoRefArea.GeoRefArea().AreasRef.items():
                        srcFileName2 = str(srcFileName).replace(".txt", "-" + sAreaKey + ".txt")
                        dstFileName2 = str(dstFileName).replace(".txt", "-" + sAreaKey + ".txt")
                        if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2):
                            #Duplication du fichier "LastVersion" de la France étendue
                            if sAreaKey == "geoFrenchExt":
                                dstFileName2b = dstFileName2.replace(self.sHeadFileDate, poaffCst.cstLastVersionFileName)
                                if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2b):
                                    self.aCatalogFiles.append(dstFileName2b + ";" + self.sHeadFileDate[:-1] + ";" + self.sHeadFileDate[:-1] + ";" + aTypeFile[1])
                            sToken2 = str("@@file@@Openair-airspaces-all"+ poaffCst.cstWithTopo).replace("-all", aTypeFile[0])
                            sToken2 += "-" + sAreaKey + "@@"
                            sDescription2:str = aTypeFile[1] + " / " + oAreaRef[2] + " [" + poaffCst.cstWithTopo[1:] + "]"
                            self.publishFile(dstFileName2, sToken2, sDescription2)
                            self.publishFilesExeptDays(sToken2, srcFileName2, dstFileName2, aTypeFile[1], poaffCst.cstWithTopo[1:], sAreaKey, oAreaRef[2])
                else:
                    sDescription4:str = aTypeFile[1] +  " [" + poaffCst.cstWithTopo[1:] + "]"
                    sComplementaryFiles += self.makeLink4File(dstFileName, sDescription4) + " | "
        self.sWebPageBuffer = self.sWebPageBuffer.replace("@@file@@Openair-airspaces" + poaffCst.cstWithTopo + "-othersfileslist@@", sComplementaryFiles)

        #### 4b/ Openair files au format "-gpsWithoutTopo"
        sComplementaryFiles:str = ""
        #Déclinaison de toutes les typologies de fichier racine
        for aTypeFile in aTypeFiles:
            if aTypeFile[0]!="-ffvl-cfd":
                srcFileName = poaffCst.cstGlobalHeader + poaffCst.cstSeparatorFileName + str(poaffCst.cstAsAllOpenairFileName).replace("-all", aTypeFile[0])
                srcFileName = srcFileName.replace(poaffCst.cstWithTopo, poaffCst.cstWithoutTopo)
                dstFileName = str(self.sHeadFileDate + poaffCst.cstAsAllOpenairFileName).replace("-all", aTypeFile[0])
                dstFileName = dstFileName.replace(poaffCst.cstWithTopo, poaffCst.cstWithoutTopo)
                if self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName):
                    sToken = str("@@file@@Openair-airspaces-all"+ poaffCst.cstWithoutTopo + "@@").replace("-all", aTypeFile[0])
                    sDescription:str = aTypeFile[1] + " [" + poaffCst.cstWithoutTopo[1:] + "]"
                    self.publishFile(dstFileName, sToken, sDescription)
                    self.publishFilesExeptDays(sToken, srcFileName, dstFileName, aTypeFile[1], poaffCst.cstWithoutTopo[1:])
                    if aTypeFile[0]=="-freeflight":
                        #Déclinaison de toutes les régionalisations
                        for sAreaKey, oAreaRef in geoRefArea.GeoRefArea().AreasRef.items():
                            srcFileName2 = str(srcFileName).replace(".txt", "-" + sAreaKey + ".txt")
                            dstFileName2 = str(dstFileName).replace(".txt", "-" + sAreaKey + ".txt")
                            if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2):
                                #Duplication du fichier "LastVersion" de la France étendue
                                if sAreaKey == "geoFrenchExt":
                                    dstFileName2b = dstFileName2.replace(self.sHeadFileDate, poaffCst.cstLastVersionFileName)
                                    if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2b):
                                        self.aCatalogFiles.append(dstFileName2b + ";" + self.sHeadFileDate[:-1] + ";" + self.sHeadFileDate[:-1] + ";" + aTypeFile[1])
                                sToken2 = str("@@file@@Openair-airspaces-all"+ poaffCst.cstWithoutTopo).replace("-all", aTypeFile[0])
                                sToken2 += "-" + sAreaKey + "@@"
                                sDescription2:str = aTypeFile[1] + " / " + oAreaRef[2] + " [" + poaffCst.cstWithoutTopo[1:] + "]"
                                self.publishFile(dstFileName2, sToken2, sDescription2)
                                self.publishFilesExeptDays(sToken2, srcFileName2, dstFileName2, aTypeFile[1], poaffCst.cstWithoutTopo[1:], sAreaKey, oAreaRef[2])
                    else:
                        sDescription4:str = aTypeFile[1] +  " [" + poaffCst.cstWithoutTopo[1:] + "]"
                        sComplementaryFiles += self.makeLink4File(dstFileName, sDescription4) + " | "
        self.sWebPageBuffer = self.sWebPageBuffer.replace("@@file@@Openair-airspaces" + poaffCst.cstWithoutTopo + "-othersfileslist@@", sComplementaryFiles)

        #### 5/ Securisation des accès sur site (avec routage vers la racine)
        self.copyFile(self.publishPath, cstTemplateMoveTo, self.publishPathFiles                , cstFinalIndexFile)
        self.copyFile(self.publishPath, cstTemplateMoveTo, self.publishPathFiles + "res/"       , cstFinalIndexFile)
        self.copyFile(self.publishPath, cstTemplateMoveTo, self.publishPath + "img/"            , cstFinalIndexFile)
        self.copyFile(self.publishPath, cstTemplateMoveTo, self.publishPath + "palette01/"      , cstFinalIndexFile)
        self.copyFile(self.publishPath, cstTemplateMoveTo, self.publishPath + "palette01/img/"  , cstFinalIndexFile)
        
        #### Pre-final/ Creating the global files catalog
        dstFileName = str(poaffCst.cstLastVersionFileName).replace("_", "s") + "Catalog_BPa.txt"
        fVerionCatalog = open(self.publishPathFiles + dstFileName, "w", encoding="utf-8", errors="ignore")
        fVerionCatalog.write("Fichier;Date de transformation;Date d'origine de la source;Description\n")
        for sLine in self.aCatalogFiles:
            fVerionCatalog.write(sLine + "\n")
        fVerionCatalog.close()

        #### Final/ Creating the html main page
        if self.sWebPageBuffer != None:
            sNewWebPage:str = "index.htm"
            sMsg = "Creating Web file - {}".format(sNewWebPage)
            self.oLog.info(sMsg, outConsole=True)
            fWebPageIndex = open(self.publishPath + sNewWebPage, "w", encoding="utf-8", errors="ignore")	#or encoding="cp1252"
            fWebPageIndex.write(self.sWebPageBuffer)
            fWebPageIndex.close()
            self.copyFile(self.publishPath, sNewWebPage, self.publishPath, self.sHeadFileDate + sNewWebPage)
        return

    #Traitement de tous les fichiers  complémentaires épurés par jour d'activité
    def publishFilesExeptDays(self, sToken:str, sSrcFile:str, sDstFile:str, sTypeFile:str, sGpsType:str, sAreaKey:str="", sAreaDesc:str="") -> None:
        aExeptDays:list =   [ ["-forSAT", "Fichier spécifiquement utilisable les 'SATerday/Samedis' (dépourvu des zones non-activables 'exceptSAT')"], \
                              ["-forSUN", "Fichier spécifiquement utilisable les 'SUNday/Dimanches' (dépourvu des zones non-activables 'exceptSUN')"], \
                              ["-forHOL", "Fichier spécifiquement utilisable les 'HOLiday/Jours-Fériés' (dépourvu des zones non-activables 'exceptHOL')"]]
        sDayFiles:str=""
        for sDayKey, sDayDesc in aExeptDays:
            srcFileName = str(sSrcFile).replace(".txt", sDayKey + ".txt")
            dstFileName = str(sDstFile).replace(".txt", sDayKey + ".txt")
            if self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName):
                if sAreaDesc:
                    sDescription:str = sTypeFile + " / " + sAreaDesc + " / " + sDayDesc + " [" + sGpsType + "/" + sDayKey[1:] + "]"
                else:
                    sDescription:str = sTypeFile + " / " + sDayDesc + " [" + sGpsType + "/" + sDayKey[1:] + "]"
                sDayFiles += "<li>" + self.makeLink4File(dstFileName, sDescription) + "</li>"

                #Duplication du fichier "LastVersion" de la France étendue
                if sAreaKey == "geoFrenchExt":
                    dstFileName2 = dstFileName.replace(self.sHeadFileDate, poaffCst.cstLastVersionFileName)
                    if self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName2):
                        self.aCatalogFiles.append(dstFileName2 + ";" + self.sHeadFileDate[:-1] + ";" + self.sHeadFileDate[:-1] + ";" + sTypeFile)

        if sAreaKey:
            sToken2 = sToken.replace(sAreaKey, sAreaKey + "-forDAYS")
        else:
            sToken2 = sToken.replace(sGpsType, sGpsType + "-forDAYS")
            
        self.sWebPageBuffer = self.sWebPageBuffer.replace(sToken2, sDayFiles)
        return

    def makeLink4File(self, sFile:str, sTitle:str) -> str:
        cstStdLync:str  = '<a title="@@title@@" target="newPage" href="files/@@file@@">@@file@@</a>'
        sNewLink:str    = cstStdLync.replace("@@title@@", sTitle)
        sNewLink        = sNewLink.replace("@@file@@", sFile)
        return sNewLink

    def publishFile(self, sDstFile:str, sToken:str, sTitle:str, sHtml:str=None) -> None:
        if not sHtml:
            sHtml = self.makeLink4File(sDstFile, sTitle)
        self.sWebPageBuffer = self.sWebPageBuffer.replace(sToken, sHtml)
        
    def copyFile(self, sSrcPath:str, sSrcFile:str, sDstPath:str, sDstFile:str) -> bool:
        if os.path.exists(sSrcPath + sSrcFile):
            shutil.copyfile(sSrcPath + sSrcFile, sDstPath + sDstFile)
            self.oLog.info("Copy file : {0} --> {1}".format(sSrcFile, sDstFile), outConsole=False)
            return True
        else:
            self.oLog.info("Uncopy file (not exist): {0}".format(sSrcFile), outConsole=False)
            return False
            
if __name__ == '__main__':
    oLog = bpaTools.Logger(appId, logFile)
    oLog.resetFile()
    oWeb = PoaffWebPage(oLog, outPath)
    oWeb.createPoaffWebPage(None)                                   #Preparation pour publication
    #oWeb.createPoaffWebPage("20200715_")                           #Pour révision d'une publication

    print()
    oLog.Report()
    oLog.closeFile()
