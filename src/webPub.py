#!/usr/bin/env python3

import os, sys, shutil, datetime


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

###  Contruction dynamique HTML  ###
cstTableRow:str             = '<tr>{0}</tr>'
cstCellStd:str              = '<td class="CelluleNormal1">{0}</td>'
cstCellCenter:str           = '<td class="CelluleNormal1" align="center">{0}</td>'
cstSpanLeft:str             = '<span style="float:left">{0}</span>'
cstSpanRight:str            = '<span style="float:right">{0}</span>'
cstSpanCentert:str          = '<span style="text-align:center; display:block;">{0}</span>'
cstTextBold:str             = '<b>{0}</b>'
cstTextItalic:str           = '<i>{0}</i>'
cstTextUnderlined:str       = '<u>{0}</u>'


aTypeFiles:list =   [ ["-all"       , "Cartographie complète de l'espace aérien (IFR + VFR)"],
                      ["-ifr"       , "Cartographie de l'espace aérien IFR (secteurs d'information radio et zones de haute altitude)"],
                      ["-vfr"       , "Cartographie de l'espace aérien VFR (zones situées de la surface jusqu'au FL175/5334m)"],
                      ["-ffvl-cfd"  , "Cartographie spécifique pour injection dans l'outillage de la CFD FFVL"],
                      ["-freeflight", "Cartographie de l'espace aérien dédiée Vol-Libre (VFR dessous FL175 + filtres et compléments)"]]


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

    def addFile2Catalog(self, bPartial:bool, sFileName:str, sCreaDate:str, sDesc:str, sLocation:str="") -> None:
        """
        if len(oAreaRef)==4 and oAreaRef[3]:
        sCellContent += '<br/>' + str(oAreaRef[3]).replace("\n", "<br/>")
        """
        aFile = [bPartial, sFileName, sCreaDate, sLocation, sDesc]
        self.aCatalogFiles.append(aFile)
        return

    def createFileCatalog(self, bPartial:bool) -> str:
        aHeaderLine:list = []
        sCreatedAt = bpaTools.getNowISO()

        #Context for bPartial=True
        dstFileName:str = str(poaffCst.cstLastVersionFileName) + "filesCatalog.csv"
        aHeaderLine = ["Fichier", "Date de transformation", "Type", "Localisation", "Description", "url"]

        if not bPartial:
            #Add LastVersion catalog of files
            aLastFileCat = [False, dstFileName,
                                  self.aCatalogFiles[0][2],
                                  "", "Reference Catalog of Last Versions Data / Catalogue partiel décrivant les dernières versions des fichiers conseillées"]

            #dstFileName:str     = dstBaseFileName + bpaTools.getDateNow(frmt="%Y%m%d-%H%M%S") + ".csv"
            dstFileName:str    = poaffCst.cstLastVersionFileName + "allExportDataset_poaff-fr.csv"
            aHeaderLine = ["id", "type", "title", "slug", "url", "organization", "organization_id", "description", "frequency", "license", "temporal_coverage.start", "temporal_coverage.end", "spatial.granularity", "spatial.zones", "private", "featured", "created_at", "last_modified", "tags", ] #"metric.discussions", "metric.issues", "metric.reuses", "metric.followers", "metric.views"]

            #Add Global catalog of files
            aGlobFileCat  = [True, dstFileName,
                                  self.aCatalogFiles[0][2],
                                  "", "Reference Data Catalog (" + str(len(self.aCatalogFiles)+2) + " files) / Catalogue complet décrivant l'ensemble des fichiers publiés"]
            self.aCatalogFiles = [aGlobFileCat] + [aLastFileCat] + self.aCatalogFiles

        fCatalog = open(self.publishPathFiles + dstFileName, "w", encoding="cp1252", errors="replace")

        #Colonnes header
        sLine:str = ""
        for sCol in aHeaderLine:
            sLine += '"{0}";'.format(sCol)
        fCatalog.write(sLine + "\n")

        #File contents
        for aLine in self.aCatalogFiles:
            sLine:str = ""
            sFileExt:str = bpaTools.getFileExt(aLine[1])
            if (sFileExt in [".json",".csv"]) and (str(aLine[1]).find("airspaces")>0):
                sFileType:str = "Airspaces Catalog"
            elif sFileExt in [".json",".csv"]:
                sFileType:str = "Files Catalog"
            elif sFileExt in [".kml",".kmz"]:
                sFileType:str = "KML"
            elif sFileExt == ".txt":
                sFileType:str = "Openair"
            elif sFileExt == ".geojson":
                sFileType:str = "GeoJSON"
            else:
                sFileType:str = "?"

            if bPartial and aLine[0]:
                sLine += '"{0}";'.format(aLine[1])                      #Fichier
                sLine += '"{0}";'.format(aLine[2])                      #Date de transformation
                sLine += '"{0}";'.format(sFileType)                     #Type
                sLine += '"{0}";'.format(aLine[3])                      #Localisation
                sLine += '"{0}";'.format(aLine[4])                      #Description
                sLine += '"http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/files/{0}";'.format(aLine[1])   #url
                fCatalog.write(sLine + "\n")

            if (not bPartial):
                sLine += '"{0}";'.format(aLine[1])                      #id
                sLine += '"{0}";'.format(sFileType)                     #Type
                sLine += '"{0}";'.format(aLine[4])                      #title
                sLine += ";"                                            #slug
                sLine += '"http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/files/{0}";'.format(aLine[1])   #url
                sLine += '"pascal-bazile";'                             #organization
                sLine += ";"                                            #organization_id
                sLine += '"See details - http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/";'     #description
                sLine += '"monthly";'                                                                       #frequency
                sLine += '"Licence Ouverte / Open Licence version 2.0";'                                    #license
                sLine += '"{0}";'.format(aLine[2])                              #temporal_coverage.start
                sLine += '"{0}";'.format(bpaTools.getDate(bpaTools.addMonths(
                                datetime.date(int(aLine[2][0:4]), int(aLine[2][4:6]), int(aLine[2][6:8])), 1)))       #temporal_coverage.end
                sLine += ";"                                                    #spatial.granularity
                sLine += '"{0}";'.format(aLine[3])                              #spatial.zones
                sLine += '"False";'                                     #private
                sLine += ";"                                            #featured
                sLine += '"{0}";'.format(sCreatedAt)                    #created_at
                sLine += ";"                                           #last_modified
                sLine += '"' + sFileExt[1:] + ',aixm,openair,eurocontrol,sia-france,espace-aerien,carte-aerienne,airspace,map,3d,sports-aeriens,air-sports,delta,deltaplane,hangliding,parapente,paragliding";'  #tags
                fCatalog.write(sLine + "\n")

        fCatalog.close()
        return dstFileName

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
        sTitle:str = "Catalogue des espaces-aériens [format JSON]"
        if self.copyFile(srcPath, srcFileName, self.publishPathFiles, dstFileName):
            self.addFile2Catalog(False, dstFileName, self.sHeadFileDate[:-1], sTitle)
            self.publishFile(dstFileName, "@@file@@JSON-airspacesCatalog@@", sTitle)
            #Duplication du fichier "LastVersion"
            dstFileName2 = dstFileName.replace(self.sHeadFileDate, poaffCst.cstLastVersionFileName)
            if self.copyFile(srcPath, srcFileName, self.publishPathFiles, dstFileName2):
                self.addFile2Catalog(True, dstFileName2, self.sHeadFileDate[:-1], sTitle)
        sTitle = "Catalogue des espaces-aériens [format CSV]"
        srcFileName = srcFileName.replace(".json", ".csv")
        dstFileName = self.sHeadFileDate + str(poaffCst.cstCatalogFileName).replace(".json", ".csv")
        if self.copyFile(srcPath, srcFileName, self.publishPathFiles, dstFileName):
            self.addFile2Catalog(False, dstFileName, self.sHeadFileDate[:-1], sTitle)
            self.publishFile(dstFileName, "@@file@@CSV-airspacesCatalog@@", sTitle)
            #Duplication du fichier "LastVersion"
            dstFileName2 = dstFileName.replace(self.sHeadFileDate, poaffCst.cstLastVersionFileName)
            if self.copyFile(srcPath, srcFileName, self.publishPathFiles, dstFileName2):
                self.addFile2Catalog(True, dstFileName2, self.sHeadFileDate[:-1], sTitle)

        #### 2/ KML files
        #Déclinaison de toutes les typologies de fichier racine
        for aTypeFile in aTypeFiles:
            if aTypeFile[0] in ["-freeflight"]:
                sLocalization:str = "-geoFrench"
                #the KML file
                sFormat:str = " [format KML]"
                srcFileName = poaffCst.cstGlobalHeader + poaffCst.cstSeparatorFileName + str(poaffCst.cstAsAllGeojsonFileName).replace("-all", aTypeFile[0])
                dstFileName = str(poaffCst.cstLastVersionFileName + poaffCst.cstAsAllGeojsonFileName).replace("-all", aTypeFile[0])
                srcFileName = srcFileName.replace(".geojson", sLocalization + ".kml")
                dstFileName = dstFileName.replace(".geojson", sLocalization+ ".kml")
                if self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName):
                    sTitle:str = aTypeFile[1] + " / " + sLocalization[1:] + sFormat
                    self.addFile2Catalog(True, dstFileName, self.sHeadFileDate[:-1], sTitle, sLocalization[1:])
                    self.publishFile(dstFileName, "@@file@@KML-airspaces-freeflight-geoFrench@@", sTitle)
                #the KMZ file
                sFormat:str = " [format KMZ]"
                srcFileName = poaffCst.cstGlobalHeader + poaffCst.cstSeparatorFileName + str(poaffCst.cstAsAllGeojsonFileName).replace("-all", aTypeFile[0])
                dstFileName = str(poaffCst.cstLastVersionFileName + poaffCst.cstAsAllGeojsonFileName).replace("-all", aTypeFile[0])
                srcFileName = srcFileName.replace(".geojson", sLocalization + ".kmz")
                dstFileName = dstFileName.replace(".geojson", sLocalization + ".kmz")
                if self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName):
                    sTitle:str = aTypeFile[1] + " / " + sLocalization[1:] + sFormat
                    self.addFile2Catalog(True, dstFileName, self.sHeadFileDate[:-1], sTitle, sLocalization[1:])
                    self.publishFile(dstFileName, "@@file@@KMZ-airspaces-freeflight-geoFrench@@", sTitle)

        #### 3/ GeoJSON files
        sFormat:str = " [format GeoJSON]"
        sComplementaryFiles:str = ""
        #Déclinaison de toutes les typologies de fichier racine
        for aTypeFile in aTypeFiles:
            srcFileName = poaffCst.cstGlobalHeader + poaffCst.cstSeparatorFileName + str(poaffCst.cstAsAllGeojsonFileName).replace("-all", aTypeFile[0])
            dstFileName = str(self.sHeadFileDate + poaffCst.cstAsAllGeojsonFileName).replace("-all", aTypeFile[0])
            bCopyFile:bool = self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName)
            if bCopyFile:
                sTitle:str = aTypeFile[1] + sFormat
                if aTypeFile[0]=="-ffvl-cfd":
                    self.addFile2Catalog(False, dstFileName, self.sHeadFileDate[:-1], sTitle, "geoFrenchAll")
                else:
                    self.addFile2Catalog(False, dstFileName, self.sHeadFileDate[:-1], sTitle)
                sToken = str("@@file@@GeoJSON-airspaces-all@@").replace("-all", aTypeFile[0])
                self.publishFile(dstFileName, sToken, aTypeFile[1])

            if aTypeFile[0]=="-ffvl-cfd":
                #Duplication du fichier "LastVersion"
                dstFileName2 = dstFileName.replace(self.sHeadFileDate, poaffCst.cstLastVersionFileName)
                if self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName2):
                    sTitle:str = aTypeFile[1] + sFormat
                    self.addFile2Catalog(True, dstFileName2, self.sHeadFileDate[:-1], sTitle, "geoFrenchAll")

            elif aTypeFile[0]=="-freeflight":
                #Déclinaison de toutes les régionalisations
                sNewTableRows:str = ""
                for sAreaKey, oAreaRef in geoRefArea.GeoRefArea(False).AreasRef.items():
                    srcFileName2 = str(srcFileName).replace(aTypeFile[0], aTypeFile[0] + "-" + sAreaKey)
                    dstFileName2 = str(dstFileName).replace(aTypeFile[0], aTypeFile[0] + "-" + sAreaKey)
                    if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2):
                        sTitle:str = aTypeFile[1] + " / " + oAreaRef[2] + sFormat
                        self.addFile2Catalog(False, dstFileName2, self.sHeadFileDate[:-1], sTitle, sAreaKey)
                        sToken2 = str("@@file@@GeoJSON-airspaces-all").replace("-all", aTypeFile[0])
                        sToken2 += "-" + sAreaKey + "@@"
                        if sAreaKey=="geoFrenchAll":
                            self.publishFile(dstFileName2, sToken2, sTitle)
                        else:
                            sNewTableRows += self.makeTableRow("GeoJSON", None, sAreaKey, oAreaRef, dstFileName2, sTitle)
                if sNewTableRows:
                    self.sWebPageBuffer = self.sWebPageBuffer.replace("<tr><td></td><td>@@TR@@GeoJSON-DynamicTableRow@@</td></tr>", sNewTableRows)

            elif bCopyFile:
                sComplementaryFiles += self.makeLink4File("files", dstFileName, aTypeFile[1]) + " | "

            if aTypeFile[0]=="-freeflight":
                #Complément du fichier optimisé 'global@airspaces-freeflight-geoFrench-optimized.geojson'
                srcFileName2 = str(srcFileName).replace(aTypeFile[0], aTypeFile[0] + "-geoFrench-optimized")
                dstFileName2 = str(dstFileName).replace(aTypeFile[0], aTypeFile[0] + "-geoFrench-optimized")
                if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2):
                    sTitle:str = aTypeFile[1] + sFormat.replace("]", "/Vecteurs optimisés]")
                    self.addFile2Catalog(False, dstFileName2, self.sHeadFileDate[:-1], sTitle, "geoFrench")
                    sToken = str("@@file@@GeoJSON-airspaces-freeflight-optimized@@")
                    self.publishFile(dstFileName2, sToken, sTitle)

        self.sWebPageBuffer = self.sWebPageBuffer.replace("@@file@@GeoJSON-airspaces-othersfileslist@@", sComplementaryFiles)

        #### 4a/ Openair files "-gpsWithTopo" for XCsoar / LK8000 / XCTrack etc...
        sFormat:str = " [format Openair/" + poaffCst.cstWithTopo[1:] + "]"
        sComplementaryFiles:str = ""
        #Déclinaison de toutes les typologies de fichier racine
        for aTypeFile in aTypeFiles:
            srcFileName = poaffCst.cstGlobalHeader + poaffCst.cstSeparatorFileName + str(poaffCst.cstAsAllOpenairFileName).replace("-all", aTypeFile[0])
            dstFileName = str(self.sHeadFileDate + poaffCst.cstAsAllOpenairFileName).replace("-all", aTypeFile[0])
            bCopyFile:bool = self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName)
            if bCopyFile:
                sTitle:str = aTypeFile[1] + sFormat
                if aTypeFile[0]=="-ffvl-cfd":
                    self.addFile2Catalog(False, dstFileName, self.sHeadFileDate[:-1], sTitle, "geoFrenchAll")
                else:
                    self.addFile2Catalog(False, dstFileName, self.sHeadFileDate[:-1], sTitle)
                sToken = str("@@file@@Openair-airspaces-all"+ poaffCst.cstWithTopo + "@@").replace("-all", aTypeFile[0])
                self.publishFile(dstFileName, sToken, sTitle)

            if aTypeFile[0]=="-ffvl-cfd":
                #Duplication du fichier "LastVersion"
                dstFileName2b = dstFileName.replace(self.sHeadFileDate, poaffCst.cstLastVersionFileName)
                if self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName2b):
                    sTitle:str = aTypeFile[1] + sFormat
                    self.addFile2Catalog(True, dstFileName2b, self.sHeadFileDate[:-1], sTitle, "geoFrenchAll")

            elif aTypeFile[0]=="-freeflight":
                #Déclinaison de toutes les régionalisations
                sNewTableRows:str = ""
                for sAreaKey, oAreaRef in geoRefArea.GeoRefArea(False).AreasRef.items():
                    srcFileName2 = str(srcFileName).replace(".txt", "-" + sAreaKey + ".txt")
                    dstFileName2 = str(dstFileName).replace(".txt", "-" + sAreaKey + ".txt")
                    if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2):
                        sTitle:str = aTypeFile[1] + " / " + oAreaRef[2] + sFormat
                        self.addFile2Catalog(False, dstFileName2, self.sHeadFileDate[:-1], sTitle, sAreaKey)

                        sToken2 = str("@@file@@Openair-airspaces-all" + poaffCst.cstWithTopo).replace("-all", aTypeFile[0])
                        sToken2 += "-" + sAreaKey + "@@"
                        if sAreaKey=="geoFrenchAll":
                            self.publishFile(dstFileName2, sToken2, sTitle)
                        else:
                            sNewTableRows += self.makeTableRow("Openair", sToken2, sAreaKey, oAreaRef, dstFileName2, sTitle)

                        #Duplication des fichiers "LastVersion" de la France
                        if sAreaKey in ["geoFrench","geoCorse","geoLaReunion","geoPolynesieFr"]:
                            dstFileName2b = dstFileName2.replace(self.sHeadFileDate, poaffCst.cstLastVersionFileName)
                            if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2b):
                                self.addFile2Catalog(True, dstFileName2b, self.sHeadFileDate[:-1], sTitle, sAreaKey)

                        #Traitement de tous les fichiers complémentaires épurés par jour d'activité
                        sLinks, sFind = self.publishFilesExeptDays(sToken2, srcFileName2, dstFileName2, aTypeFile[1], poaffCst.cstWithTopo[1:], sAreaKey, oAreaRef[2])
                        if sAreaKey=="geoFrenchAll":
                            self.sWebPageBuffer = self.sWebPageBuffer.replace(sFind, sLinks)
                        else:
                            sNewTableRows= sNewTableRows.replace(sFind, sLinks)

                if sNewTableRows:
                    self.sWebPageBuffer = self.sWebPageBuffer.replace("<tr><td></td><td>@@TR@@Openair-gpsWithTopo-DynamicTableRow@@</td></tr>", sNewTableRows)

            elif bCopyFile:
                sTitle:str = aTypeFile[1] + sFormat
                sComplementaryFiles += self.makeLink4File("files", dstFileName, sTitle) + " | "

        self.sWebPageBuffer = self.sWebPageBuffer.replace("@@file@@Openair-airspaces" + poaffCst.cstWithTopo + "-othersfileslist@@", sComplementaryFiles)

        #### 4b/ Openair files "-gpsWithoutTopo" for Flytec / Brauniger
        sFormat:str = " [format Openair/" + poaffCst.cstWithoutTopo[1:] + "]"
        sComplementaryFiles:str = ""
        #Déclinaison de toutes les typologies de fichier racine
        for aTypeFile in aTypeFiles:
            srcFileName = poaffCst.cstGlobalHeader + poaffCst.cstSeparatorFileName + str(poaffCst.cstAsAllOpenairFileName).replace("-all", aTypeFile[0])
            dstFileName = str(self.sHeadFileDate + poaffCst.cstAsAllOpenairFileName).replace("-all", aTypeFile[0])
            srcFileName = srcFileName.replace(poaffCst.cstWithTopo, poaffCst.cstWithoutTopo)
            dstFileName = dstFileName.replace(poaffCst.cstWithTopo, poaffCst.cstWithoutTopo)
            bCopyFile:bool = self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName)
            if bCopyFile:
                sTitle:str = aTypeFile[1] + sFormat
                if aTypeFile[0]=="-ffvl-cfd":
                    self.addFile2Catalog(False, dstFileName, self.sHeadFileDate[:-1], sTitle, "geoFrenchAll")
                else:
                    self.addFile2Catalog(False, dstFileName, self.sHeadFileDate[:-1], sTitle)
                sToken = str("@@file@@Openair-airspaces-all"+ poaffCst.cstWithoutTopo + "@@").replace("-all", aTypeFile[0])
                self.publishFile(dstFileName, sToken, sTitle)

            if aTypeFile[0]=="-freeflight":
                #Déclinaison de toutes les régionalisations
                sNewTableRows:str = ""
                for sAreaKey, oAreaRef in geoRefArea.GeoRefArea(False).AreasRef.items():
                    if sAreaKey in ["geoFrenchNorth","geoFrenchSouth","geoFrenchNESW","geoFrenchVosgesJura","geoFrenchPyrenees","geoFrenchAlps"]:
                        continue
                    srcFileName2 = str(srcFileName).replace(".txt", "-" + sAreaKey + ".txt")
                    dstFileName2 = str(dstFileName).replace(".txt", "-" + sAreaKey + ".txt")
                    if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2):
                        sTitle:str = aTypeFile[1] + " / " + oAreaRef[2] + sFormat
                        self.addFile2Catalog(False, dstFileName2, self.sHeadFileDate[:-1], sTitle, sAreaKey)

                        sToken2 = str("@@file@@Openair-airspaces-all"+ poaffCst.cstWithoutTopo).replace("-all", aTypeFile[0])
                        sToken2 += "-" + sAreaKey + "@@"
                        if sAreaKey=="geoFrenchAll":
                            self.publishFile(dstFileName2, sToken2, sTitle)
                        else:
                            sNewTableRows += self.makeTableRow("Openair", sToken2, sAreaKey, oAreaRef, dstFileName2, sTitle, True)

                        #Duplication des fichiers "LastVersion" de la France
                        if sAreaKey in ["geoFrench"]:
                            dstFileName2b = dstFileName2.replace(self.sHeadFileDate, poaffCst.cstLastVersionFileName)
                            if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2b):
                                self.addFile2Catalog(True, dstFileName2b, self.sHeadFileDate[:-1], sTitle, sAreaKey)

                        #Traitement de tous les fichiers complémentaires épurés par jour d'activité
                        sLinks, sFind = self.publishFilesExeptDays(sToken2, srcFileName2, dstFileName2, aTypeFile[1], poaffCst.cstWithoutTopo[1:], sAreaKey, oAreaRef[2])
                        if sAreaKey=="geoFrenchAll":
                            self.sWebPageBuffer = self.sWebPageBuffer.replace(sFind, sLinks)
                        else:
                            sNewTableRows= sNewTableRows.replace(sFind, sLinks)

                if sNewTableRows:
                    self.sWebPageBuffer = self.sWebPageBuffer.replace("<tr><td></td><td>@@TR@@Openair-gpsWithoutTopo-DynamicTableRow@@</td></tr>", sNewTableRows)

            elif bCopyFile:
                sTitle:str = aTypeFile[1] + sFormat
                sComplementaryFiles += self.makeLink4File("files", dstFileName, sTitle) + " | "

        self.sWebPageBuffer = self.sWebPageBuffer.replace("@@file@@Openair-airspaces" + poaffCst.cstWithoutTopo + "-othersfileslist@@", sComplementaryFiles)

        #### 4c/ Openair files "-gpsWithoutTopo" for Flymaster or LimitedMemory
        sFormat:str = " [format Openair/" + poaffCst.cstWithoutTopo[1:] + "]"
        sComplementaryFiles:str = ""
        #Déclinaison de toutes les typologies de fichier racine
        for aTypeFile in aTypeFiles:
            srcFileName = poaffCst.cstGlobalHeader + poaffCst.cstSeparatorFileName + str(poaffCst.cstAsAllOpenairFileName).replace("-all", aTypeFile[0])
            dstFileName = str(self.sHeadFileDate + poaffCst.cstAsAllOpenairFileName).replace("-all", aTypeFile[0])
            srcFileName = srcFileName.replace(poaffCst.cstWithTopo, poaffCst.cstWithoutTopo)
            dstFileName = dstFileName.replace(poaffCst.cstWithTopo, poaffCst.cstWithoutTopo)
            bCopyFile:bool = self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName)
            if bCopyFile:
                sTitle:str = aTypeFile[1] + sFormat
                self.addFile2Catalog(False, dstFileName, self.sHeadFileDate[:-1], sTitle)
                sToken = str("@@file@@Openair-airspaces-all"+ poaffCst.cstWithoutTopo + "@@").replace("-all", aTypeFile[0])
                self.publishFile(dstFileName, sToken, sTitle)

            if aTypeFile[0]=="-freeflight":
                #Déclinaison de toutes les régionalisations
                sNewTableRows:str = ""
                for sAreaKey, oAreaRef in geoRefArea.GeoRefArea(False).AreasRef.items():
                    if not sAreaKey in ["geoFrenchNorth","geoFrenchSouth","geoFrenchNESW","geoFrenchVosgesJura","geoFrenchPyrenees","geoFrenchAlps"]:
                        continue
                    srcFileName2 = str(srcFileName).replace(".txt", "-" + sAreaKey + ".txt")
                    dstFileName2 = str(dstFileName).replace(".txt", "-" + sAreaKey + ".txt")
                    if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2):
                        sTitle:str = aTypeFile[1] + " / " + oAreaRef[2] + sFormat
                        self.addFile2Catalog(False, dstFileName2, self.sHeadFileDate[:-1], sTitle, sAreaKey)

                        sToken2 = str("@@file@@Openair-airspaces-all"+ poaffCst.cstWithoutTopo).replace("-all", aTypeFile[0])
                        sToken2 += "-" + sAreaKey + "@@"
                        sNewTableRows += self.makeTableRow("Openair", sToken2, sAreaKey, oAreaRef, dstFileName2, sTitle)

                        #Traitement de tous les fichiers complémentaires épurés par jour d'activité
                        sLinks, sFind = self.publishFilesExeptDays(sToken2, srcFileName2, dstFileName2, aTypeFile[1], poaffCst.cstWithoutTopo[1:], sAreaKey, oAreaRef[2])
                        sNewTableRows= sNewTableRows.replace(sFind, sLinks)

                if sNewTableRows:
                    self.sWebPageBuffer = self.sWebPageBuffer.replace("<tr><td></td><td>@@TR@@Openair-gpsWithoutTopo-LimitedMemory-DynamicTableRow@@</td></tr>", sNewTableRows)

            elif bCopyFile:
                sTitle:str = aTypeFile[1] + sFormat
                sComplementaryFiles += self.makeLink4File("files", dstFileName, sTitle) + " | "

        self.sWebPageBuffer = self.sWebPageBuffer.replace("@@file@@Openair-airspaces" + poaffCst.cstWithoutTopo + "-othersfileslist@@", sComplementaryFiles)

        #### 5/ Securisation des accès sur site (avec routage vers la racine)
        self.copyFile(self.publishPath, cstTemplateMoveTo, self.publishPathFiles                , cstFinalIndexFile)
        self.copyFile(self.publishPath, cstTemplateMoveTo, self.publishPathFiles + "res/"       , cstFinalIndexFile)
        self.copyFile(self.publishPath, cstTemplateMoveTo, self.publishPath + "img/"            , cstFinalIndexFile)
        self.copyFile(self.publishPath, cstTemplateMoveTo, self.publishPath + "palette01/"      , cstFinalIndexFile)
        self.copyFile(self.publishPath, cstTemplateMoveTo, self.publishPath + "palette01/img/"  , cstFinalIndexFile)

        #### Pré-Final/ Creating the files catalog
        sReferenceDataCatalog:str = self.createFileCatalog(False)   #Creating the global files catalog
        self.createFileCatalog(True)                                #Creating the partial files catalog
        self.sWebPageBuffer = self.sWebPageBuffer.replace("@@file@@csv-ReferenceDataCatalog@@", sReferenceDataCatalog)

        #### Final/ Creating the html main page
        if self.sWebPageBuffer != None:
            sFilePubDates:str = "__webPublications.json"
            sParamPubDates:str = "webPublicationDates"
            oJsonParam = bpaTools.readJsonFile(self.publishPath + sFilePubDates)
            aPubDates:list = oJsonParam.get(sParamPubDates, list([]))
            sFrDate:str = bpaTools.getDateNow(frmt="dmy", sep="/")
            if not sFrDate in aPubDates:
                aPubDates.append(sFrDate)
                oJsonParam.update({sParamPubDates:aPubDates})
                bpaTools.writeJsonFile(self.publishPath + sFilePubDates, oJsonParam)
            sBuffStr:str = "; ".join(aPubDates[0:-1])
            sBuffStr += "; <b>" + aPubDates[-1] + "</b>"
            self.sWebPageBuffer = self.sWebPageBuffer.replace("@@DatesList@@webPublicationDates@@", sBuffStr)
            self.sWebPageBuffer = self.sWebPageBuffer.replace("@@DatesList@@webPublicationLastDate@@", str(aPubDates[-1]))

            sNewWebPage:str = "index.htm"
            sMsg = "Creating Web file - {}".format(sNewWebPage)
            self.oLog.info(sMsg, outConsole=True)
            fWebPageIndex = open(self.publishPath + sNewWebPage, "w", encoding="utf-8", errors="ignore")	#or encoding="cp1252"
            fWebPageIndex.write(self.sWebPageBuffer)
            fWebPageIndex.close()
            self.copyFile(self.publishPath, sNewWebPage, self.publishPath, self.sHeadFileDate + sNewWebPage)
        return

    #Traitement de tous les fichiers complémentaires épurés par jour d'activité
    def publishFilesExeptDays(self, sToken:str, sSrcFile:str, sDstFile:str, sTypeFile:str, sGpsType:str, sAreaKey:str="", sAreaDesc:str="") -> str:
        aExeptDays:list =   [ ["-forSAT", "Fichier spécifiquement utilisable les 'SATerday/Samedis' (dépourvu des zones non-activables 'exceptSAT')"], \
                              ["-forSUN", "Fichier spécifiquement utilisable les 'SUNday/Dimanches' (dépourvu des zones non-activables 'exceptSUN')"], \
                              ["-forHOL", "Fichier spécifiquement utilisable les 'HOLiday/Jours-Fériés' (dépourvu des zones non-activables 'exceptHOL')"]]
        sDayFiles:str=""
        for sDayKey, sDayDesc in aExeptDays:
            srcFileName = str(sSrcFile).replace(".txt", sDayKey + ".txt")
            dstFileName = str(sDstFile).replace(".txt", sDayKey + ".txt")
            if self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName):
                sFormat:str = " [format Openair/"
                if sAreaDesc:
                    sTitle:str = sTypeFile + " / " + sAreaDesc + " / " + sDayDesc + sFormat + sGpsType + "/" + sDayKey[1:] + "]"
                else:
                    sTitle:str = sTypeFile + " / " + sDayDesc + sFormat + sGpsType + "/" + sDayKey[1:] + "]"
                self.addFile2Catalog(False, dstFileName, self.sHeadFileDate[:-1], sTitle, sAreaKey)
                sDayFiles += "<li>" + self.makeLink4File("files", dstFileName, sTitle) + "</li>"

                #Duplication du fichier "LastVersion" de la France
                if sAreaKey in ["geoFrench"]:
                    dstFileName2 = dstFileName.replace(self.sHeadFileDate, poaffCst.cstLastVersionFileName)
                    if self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName2):
                        self.addFile2Catalog(True, dstFileName2, self.sHeadFileDate[:-1], sTitle, sAreaKey)

        if sAreaKey:
            sToken2 = sToken.replace(sAreaKey, sAreaKey + "-forDAYS")
        else:
            sToken2 = sToken.replace(sGpsType, sGpsType + "-forDAYS")

        #old - self.sWebPageBuffer = self.sWebPageBuffer.replace(sToken2, sDayFiles)
        return sDayFiles, sToken2

    def makeTableRow(self, sFileType:str, sToken:str, sAreaKey:str, oAreaRef:list, dstFileName:str, sTitle:str, bFAF:bool=False) -> str:
        aTableCols:list = []
        #--Colonne 1--
        sCellContent:str = cstTextBold.format(oAreaRef[2])
        if (sAreaKey[:9]=="geoFrench") or (sAreaKey in ["geoPWCFrenchAlps"]):
            sCellContent += '<br/>avec ZSM (Zone de Sensibilité Majeure)'
        aTableCols.append(cstCellStd.format(sCellContent))
        #--Colonne 2-- - bloc images-a-gauche
        sCellContent:str = ''
        sContent:str = ''
        sImgFile = 'img/' + sAreaKey + '_localization.jpg'
        if os.path.exists(self.publishPath + sImgFile):
            sContent:str = '<a title="Localisation..." target="map" href="' + sImgFile + '"><img height="50" src="' + sImgFile + '" /></a>'
            sContent += ' / '
        sImgFile = 'img/' + sAreaKey + '_border.jpg'
        if os.path.exists(self.publishPath + sImgFile):
            sContent += '<a title="Découpage..." target="map" href="' + sImgFile + '"><img height="50" src="' + sImgFile + '" /></a>'
        if sContent:
            sCellContent:str = cstSpanLeft.format(sContent)
        #--Colonne 2-- - bloc images-a-droite
        sImgFile = 'img/' + sAreaKey + '_sample_' + sFileType + '.jpg'
        if os.path.exists(self.publishPath + sImgFile):
            sContent:str = '<a title="Exemple de représentation..." target="map" href="' + sImgFile + '"><img height="50" src="' + sImgFile + '" /></a>'
            sCellContent += cstSpanRight.format(sContent)
        sMsg:str = ""
        if (sAreaKey[:9]!="geoFrench") and (not sAreaKey in ["geoPWCFrenchAlps","geoCorse","geoLaReunion","geoGuyaneFr","geoStPierreEtMiquelon","geoAntillesFr","geoMayotte","geoPolynesieFr","geoNouvelleCaledonie"]):
            sMsg = "(i) Complétude des données non garantie..."
            sContent:str = '<a title="' + sMsg + '"><img height="50" src="img/travaux.png" /></a>'
            sCellContent += cstSpanRight.format(sContent)
        #--Colonne 2-- - bloc contenu
        sCellContent += cstTextBold.format(oAreaRef[2])
        if len(oAreaRef)==4 and oAreaRef[3]:
            sCellContent += '<br/>' + str(oAreaRef[3]).replace("\n", "<br/>")
        sCellContent += '<br/>'
        if sMsg:
            sCellContent += '<br/>' + cstTextItalic.format(sMsg)
        else:
            sCellContent += '<br/>'
        if sFileType=="GeoJSON":
            sPath:str = 'files/geoRef/'
            sFile:str =  sAreaKey + '_border.geojson'
            if os.path.exists(self.publishPath + sPath + sFile):
                sCellContent += cstSpanLeft.format(' (' + self.makeLink4File(sPath[:-1], sFile, "GeoJSON Border...") + ')')
        if sToken:
            sToken2:str = sToken.replace(sAreaKey, sAreaKey + "-forDAYS")
            #sCellContent += '<br/><br/>' + sToken2
            sCellContent += sToken2
        aTableCols.append(cstCellCenter.format(sCellContent))
        #--Colonne 3--
        sContent:str = sFileType
        if bFAF:
            sContent += ' et FAF'
        sContent += ' - ' + oAreaRef[2] + ' - Vol-libre'
        sCellContent:str = cstTextBold.format(cstTextUnderlined.format(sContent))
        sCellContent += '<ul>'
        sCellContent += '<li>' + self.makeLink4File("files", dstFileName, sTitle) + '</li>'
        if bFAF:
            sCellContent += '<li><b>FAF</b> - <i>non disponible</i></li>'
        sCellContent += '</ul>'
        aTableCols.append(cstCellStd.format(sCellContent))
        #--Colonne 4--
        sCellContent:str = cstTextItalic.format("(idem que ci-dessus)")
        aTableCols.append(cstCellCenter.format(sCellContent))
        sNewRow:str = ""
        for sCol in aTableCols:
            sNewRow += sCol
        sNewRow += chr(10)
        return cstTableRow.format(sNewRow)

    def makeLink4File(self, sPath:str, sFile:str, sTitle:str) -> str:
        cstStdLync:str  = '<a title="@@title@@" target="newPage" href="download.php?file=@@path@@/@@file@@">@@file@@</a>'
        sNewLink:str    = cstStdLync.replace("@@title@@", sTitle)
        sNewLink        = sNewLink.replace("@@path@@", sPath)
        sNewLink        = sNewLink.replace("@@file@@", sFile)
        return sNewLink

    def publishFile(self, sDstFile:str, sToken:str, sTitle:str, sHtml:str=None) -> None:
        if not sHtml:
            sHtml = self.makeLink4File("files", sDstFile, sTitle)
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
