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
from geoRefArea import enuAreasRef
import geoRefArea



###################################################################################################
# /!\ Change before generate html page !!! -> Sample - Cycle AIRAC 03/21 (25/03/2021 au 21/04/2021)
# /!\ and cleen folder - poaff/output/_POAFF_www/files/
###################################################################################################
cstPOAFFdateTrait:datetime = datetime.date(2021, 12,  6)      #bpaTools.getDateNow()  ||or||  datetime.date(2021, 5, 25)
cstAIRACdateStart:datetime = datetime.date(2021, 12,  2)
cstAIRACdateEnd:datetime   = datetime.date(2021, 12, 29)
###################################################################################################



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


cstDangersHeader:str = "Dangers sur "
## Namming format -    Nom source   , Nom dest.   , Description
aTypeFiles:list =   [ ["-all"       , "-all"      , "Cartographie complète de l'espace aérien (IFR + VFR)"],
                      ["-ifr"       , "-ifr"      , "Cartographie de l'espace aérien IFR (secteurs d'information radio et zones de haute altitude)"],
                      ["-vfr"       , "-vfr"      , "Cartographie de l'espace aérien VFR (zones situées de la surface jusqu'au FL195/5944m)"],
                      ["-ffvl-cfd"  , "-ffvl-cfd" , "Cartographie spécifique pour injection dans l'outillage de la CFD FFVL"],
                      ["-freeflight", "-ff"       , "Cartographie de l'espace aérien dédiée Vol-Libre (VFR dessous FL195 + filtres et compléments)"]]

class PoaffWebPage:

    def __init__(self, oLog, outPath:str)-> None:
        bpaTools.initEvent(__file__, oLog)
        self.oLog:bpaTools.Logger   = oLog
        self.outPath:str            = outPath
        self.sourcesPath:str        = self.outPath + poaffCst.cstPoaffOutPath
        self.publishPath:str        = self.outPath + poaffCst.cstPoaffWebPath
        self.publishPathFiles:str   = self.publishPath + poaffCst.cstPoaffWebPathFiles
        self.publishPathCfd:str     = self.outPath + poaffCst.cstCfdWebPath
        bpaTools.createFolder(self.publishPath)         #Initialisation
        bpaTools.createFolder(self.publishPathFiles)    #Initialisation
        bpaTools.createFolder(self.publishPathCfd)      #Initialisation
        self.sWebPageBuffer:str     = None
        self.sHeadFileDate:str      = "{0}_".format(bpaTools.getDate(cstPOAFFdateTrait, frmt="ymd", sep=""))
        self.aCatalogFiles:list     = None
        return

    def addFile2Catalog(self, bPartial:bool, sFileName:str, sCreaDate:str, sDesc:str, sLocation:str="", oAreaRef:list=None) -> None:
        aFile = [bPartial, sFileName, sCreaDate, sLocation, sDesc]
        if oAreaRef:
            aFile.append(oAreaRef[enuAreasRef.Iso3.value])
            aFile.append(oAreaRef[enuAreasRef.Iso2.value])
            aFile.append(oAreaRef[enuAreasRef.IsoComp.value])
        else:
            sFileExt:str = bpaTools.getFileExt(sFileName)
            if sFileExt in [".txt",".geojson",".kml"]:
                aFile.append("---")
                aFile.append("--")
                aFile.append("Countries")
            else:
                aFile.append("")
                aFile.append("")
                aFile.append("")

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
                                  "", "Reference Catalog of Last Versions Data / Catalogue partiel décrivant les dernières versions des fichiers conseillées","","",""]

            dstFileName:str    = poaffCst.cstLastVersionFileName + "allExportDataset_poaff-fr.csv"
            aHeaderLine = ["id", "type", "layer", "spatial.granularity", "spatial.zones", "ISO_3166-1_3", "ISO_3166-1_2", "ISO_Perimeter", "title", "slug", "url", "organization", "organization_id", "description", "frequency", "license", "temporal_coverage.start", "temporal_coverage.end", "private", "featured", "created_at", "last_modified", "tags", ] #"metric.discussions", "metric.issues", "metric.reuses", "metric.followers", "metric.views"]

            #Add Global catalog of files
            aGlobFileCat  = [True, dstFileName,
                                  self.aCatalogFiles[0][2],
                                  "", "Reference Data Catalog (" + str(len(self.aCatalogFiles)+2) + " files) / Catalogue complet décrivant l'ensemble des fichiers publiés","","",""]
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

            sFileType:str = "?"
            sFileExt:str = bpaTools.getFileExt(aLine[1])
            if (sFileExt in [".json",".csv"]) and (str(aLine[1]).find("airspaces")>0):
                sFileType = "Airspaces Catalog"
            elif sFileExt in [".json",".csv"]:
                sFileType = "Files Catalog"
            elif sFileExt in [".kml"]:
                sFileType = "KML"
            elif sFileExt in [".kmz"]:
                sFileType = "KMZ"
            elif sFileExt == ".txt":
                sFileType = "Openair"
            elif sFileExt == ".geojson":
                sFileType = "GeoJSON"

            if str(aLine[1]).find("-withT")>0:
                sFileType += " gpsWithTopo"
            if str(aLine[1]).find("-outT")>0:
                sFileType += " gpsWithoutTopo"

            sFileLayer:str = ""
            if str(aLine[1]).find("-all")>0:
                sFileLayer = "VFR+IFR"
            elif str(aLine[1]).find("-ifr")>0:
                sFileLayer = "IFR"
            elif str(aLine[1]).find("-vfr")>0:
                sFileLayer = "VFR"
            elif (str(aLine[1]).find("-ff")>0) or (str(aLine[1]).find("-ffvl-cfd")>0):
                sFileLayer = "FreeFlight"

            if sFileExt in [".kml",".kmz",".txt",".geojson"]:
                if str(aLine[1]).find("-wrn")>0:
                    sFileLayer += " Warning"
                if str(aLine[1]).find("_border")>0:
                    sFileLayer += "Border"
                else:
                    sFileLayer += " Map"

            sUrlSite:str = "http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/"
            sUrlFile:str = sUrlSite + "files/"
            if str(aLine[1]).find("_border")>0:
                sUrlFile += "geoRef/"

            if bPartial and aLine[0]:
                sLine += '"{0}";'.format(aLine[1])                      #Fichier
                sLine += '"{0}";'.format(aLine[2])                      #Date de transformation
                sLine += '"{0}";'.format(sFileType)                     #Type
                sLine += '"{0}";'.format(aLine[3])                      #Localisation
                sLine += '"{0}";'.format(aLine[4])                      #Description
                sLine += '"{0}{1}";'.format(sUrlFile, aLine[1])         #url
                fCatalog.write(sLine + "\n")

            if (not bPartial):
                sLine += '"{0}";'.format(aLine[1])                      #id
                sLine += '"{0}";'.format(sFileType)                     #type
                sLine += '"{0}";'.format(sFileLayer)                    #layer
                sLine += ";"                                            #spatial.granularity
                sLine += '"{0}";'.format(aLine[3])                      #spatial.zones
                sLine += '"{0}";'.format(aLine[5])                      #ISO_3166-1 - 3 chars
                sLine += '"{0}";'.format(aLine[6])                      #ISO_3166-1 - 2 chars
                sLine += '"{0}";'.format(aLine[7])                      #ISO_Perimeter: Countries; All-Territories; Country; Partial; Additional-Territory
                sLine += '"{0}";'.format(aLine[4])                      #title
                sLine += ";"                                            #slug
                sLine += '"{0}{1}";'.format(sUrlFile, aLine[1])         #url
                sLine += '"pascal-bazile";'                             #organization
                sLine += ";"                                            #organization_id
                sLine += '"See details - {0}";'.format(sUrlSite)        #description
                sLine += '"monthly";'                                   #frequency
                sLine += '"Licence Ouverte / Open Licence version 2.0";'#license
                if str(aLine[1]).find("_border")>0:
                    sLine += '"{0}";'.format("")                        #temporal_coverage.start
                    sLine += '"{0}";'.format("")                        #temporal_coverage.end
                else:
                    sLine += '"{0}";'.format(cstAIRACdateStart.strftime("%Y/%m/%d"))         #temporal_coverage.start
                    sLine += '"{0}";'.format(cstAIRACdateEnd.strftime("%Y/%m/%d"))           #temporal_coverage.end
                sLine += '"False";'                                     #private
                sLine += ";"                                            #featured
                sLine += '"{0}";'.format(sCreatedAt)                    #created_at
                sLine += ";"                                            #last_modified
                sLine += '"' + sFileExt[1:] + ',aixm,openair,eurocontrol,sia-france,espace-aerien,carte-aerienne,airspace,map,3d,sports-aeriens,air-sports,delta,deltaplane,hangliding,parapente,paragliding";'  #tags
                fCatalog.write(sLine + "\n")

        fCatalog.close()
        return dstFileName

    def createPoaffWebPage(self) -> None:
        self.aCatalogFiles = []

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
        #Déclinaison de toutes les typologies de fichier racine  (-all, -ifr, -vfr, -ffvl-cfd, -ff)
        sFormat:str = " [format KML]"
        sComplementaryFiles:str = ""
        for aTypeFile in aTypeFiles:
            srcFileName = poaffCst.cstGlobalHeader + poaffCst.cstSeparatorFileName + str(poaffCst.cstAsAllGeojsonFileName).replace("-all", aTypeFile[0])
            dstFileName = str(self.sHeadFileDate + poaffCst.cstAsAllGeojsonFileName).replace("-all", aTypeFile[1])
            dstFileName = dstFileName.replace("airspaces-", "")

            if aTypeFile[0] in ["-ifr","-vfr"]:
                srcFileName2 = str(srcFileName).replace(".geojson", ".kml")
                dstFileName2 = str(dstFileName).replace(".geojson", ".kml")
                bCopyFile:bool = self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2)
                if bCopyFile:
                    sTitle:str = aTypeFile[2] + sFormat
                    sTitle = sTitle.replace("Cartographie spécifique", "Cartographie 3D représentative des cartographies spécifiques")
                    self.addFile2Catalog(False, dstFileName2, self.sHeadFileDate[:-1], sTitle, "geoAll")
                    sToken = str("@@file@@KML-airspaces-all@@").replace("-all", aTypeFile[0])
                    self.publishFile(dstFileName2, sToken, sTitle)
                    sComplementaryFiles += self.makeLink4File("files", dstFileName2, aTypeFile[2]) + " | "

            if aTypeFile[0]=="-ffvl-cfd":
                srcFileName2 = str(srcFileName).replace(".geojson", ".kml")
                dstFileName2 = str(dstFileName).replace(".geojson", ".kml")
                bCopyFile:bool = self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2)
                if bCopyFile:
                    sTitle:str = aTypeFile[2] + sFormat
                    sTitle = sTitle.replace("Cartographie spécifique", "Cartographie 3D représentative des cartographies spécifiques")
                    self.addFile2Catalog(False, dstFileName2, self.sHeadFileDate[:-1], sTitle, "geoFrenchAll", geoRefArea.GeoRefArea(False).AreasRef["geoFrenchAll"])
                    #Duplication du fichier "LastVersion"
                    dstFileName2b = dstFileName2.replace(self.sHeadFileDate, poaffCst.cstLastVersionFileName2)
                    if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2b):
                        self.addFile2Catalog(True, dstFileName2b, self.sHeadFileDate[:-1], sTitle, "geoFrenchAll", geoRefArea.GeoRefArea(False).AreasRef["geoFrenchAll"])
                    sToken = str("@@file@@KML-airspaces-all@@").replace("-all", aTypeFile[0])
                    self.publishFile(dstFileName2, sToken, sTitle)

            if aTypeFile[0] in ["-freeflight"]:
                #Déclinaison de toutes les régionalisations
                for sAreaKey, oAreaRef in geoRefArea.GeoRefArea(False).AreasRef.items():
                    aSpecialization:list = ["","-wrn"]
                    for sFileType in aSpecialization:
                        #Fichier principal régionalisé (ex: 20210131_airspaces-ff-geoFrench.geojson)
                        if sFileType == "-wrn":
                            srcFileName2 = str(srcFileName).replace(".geojson", "-" + sAreaKey + "-warning" + ".kml")
                        else:
                            srcFileName2 = str(srcFileName).replace(".geojson", "-" + sAreaKey + sFileType + ".kml")
                        dstFileName2 = str(dstFileName).replace(".geojson", "-" + sAreaKey + sFileType + ".kml")
                        dstFileName2 = str(dstFileName2).replace("-geo", "-")
                        if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2):
                            sTitle:str = aTypeFile[2] + " / " + sAreaKey[1:] + sFileType + sFormat
                            if sFileType == "-wrn":
                                sTitle = cstDangersHeader + sTitle
                            self.addFile2Catalog(False, dstFileName2, self.sHeadFileDate[:-1], sTitle, sAreaKey, geoRefArea.GeoRefArea(False).AreasRef[sAreaKey])
                            sTocken:str = "@@file@@KML-airspaces-freeflight-" + sAreaKey + sFileType + "@@"
                            self.publishFile(dstFileName2, sTocken, sTitle)

                        #Duplication des fichiers "LastVersion" de la France
                        if sAreaKey in ["geoFrench"]:
                            dstFileName2b = dstFileName2.replace(self.sHeadFileDate, poaffCst.cstLastVersionFileName2)
                            if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2b):
                                self.addFile2Catalog(True, dstFileName2b, self.sHeadFileDate[:-1], sTitle, sAreaKey, oAreaRef)

        self.sWebPageBuffer = self.sWebPageBuffer.replace("@@file@@KML-airspaces-othersfileslist@@", sComplementaryFiles)

        #### 3a/ GeoJSON border files
        #Déclinaison de toutes les régionalisations
        sFormat:str = " [format GeoJSON]"
        for sAreaKey, oAreaRef in geoRefArea.GeoRefArea(False).AreasRef.items():
            sPath:str = 'files/geoRef/'
            sFile:str =  sAreaKey + '_border.geojson'
            if os.path.exists(self.publishPath + sPath + sFile):
                sTitle:str = "Geographic border - Frontière géographique / " + oAreaRef[enuAreasRef.desc.value] + sFormat
                self.addFile2Catalog(False, sFile, bpaTools.getDate(bpaTools.getFileModificationDate(self.publishPath + sPath + sFile)), sTitle, sAreaKey, oAreaRef)


        #### 3b/ GeoJSON map files
        sFormat:str = " [format GeoJSON]"
        sComplementaryFiles:str = ""
        #Déclinaison de toutes les typologies de fichier racine (-all, -ifr, -vfr, -ffvl-cfd, -ff)
        for aTypeFile in aTypeFiles:
            srcFileName = poaffCst.cstGlobalHeader + poaffCst.cstSeparatorFileName + str(poaffCst.cstAsAllGeojsonFileName).replace("-all", aTypeFile[0])
            dstFileName = str(self.sHeadFileDate + poaffCst.cstAsAllGeojsonFileName).replace("-all", aTypeFile[1])
            dstFileName = dstFileName.replace("airspaces-", "")
            bCopyFile:bool = self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName)
            if bCopyFile:
                sTitle:str = aTypeFile[2] + sFormat
                if aTypeFile[0]=="-ffvl-cfd":
                    self.addFile2Catalog(False, dstFileName, self.sHeadFileDate[:-1], sTitle, "geoFrenchAll", geoRefArea.GeoRefArea(False).AreasRef["geoFrenchAll"])
                else:
                    self.addFile2Catalog(False, dstFileName, self.sHeadFileDate[:-1], sTitle, "geoAll")
                sToken = str("@@file@@GeoJSON-airspaces-all@@").replace("-all", aTypeFile[0])
                self.publishFile(dstFileName, sToken, sTitle)

                #Fichier warning non-régionalisé (ex: 20210131_airspaces-ff-wrn.geojson)
                srcFileNameb = str(srcFileName).replace(".geojson", "-warning.geojson")
                dstFileNameb = str(dstFileName).replace(".geojson", "-wrn.geojson")
                bWarningFile:bool = self.copyFile(self.sourcesPath, srcFileNameb, self.publishPathFiles, dstFileNameb)
                if bWarningFile:
                    sTitleb:str = cstDangersHeader + sTitle
                    self.addFile2Catalog(False, dstFileNameb, self.sHeadFileDate[:-1], sTitleb, "geoAll")
                    sTokenb = sToken[:-2] + "-warning@@"
                    self.publishFile(dstFileNameb, sTokenb, sTitleb)

            if aTypeFile[0]=="-ffvl-cfd":
                #Duplication du fichier "LastVersion"
                dstFileName2 = dstFileName.replace(self.sHeadFileDate, poaffCst.cstLastVersionFileName2)
                if self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName2):
                    sTitle:str = aTypeFile[2] + sFormat
                    self.addFile2Catalog(True, dstFileName2, self.sHeadFileDate[:-1], sTitle, "geoFrenchAll", geoRefArea.GeoRefArea(False).AreasRef["geoFrenchAll"])

            elif aTypeFile[0]=="-freeflight":
                #Déclinaison de toutes les régionalisations
                sNewTableRows:str = ""
                for sAreaKey, oAreaRef in geoRefArea.GeoRefArea(False).AreasRef.items():
                    #Fichier principal régionalisé (ex: 20210131_airspaces-ff-geoFrench.geojson)
                    srcFileName2 = str(srcFileName).replace(aTypeFile[0], aTypeFile[0] + "-" + sAreaKey)
                    dstFileName2 = str(dstFileName).replace(aTypeFile[1][1:] + ".", aTypeFile[1][1:] + "-" + sAreaKey + ".")
                    dstFileName2 = str(dstFileName2).replace("-geo", "-")
                    if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2):
                        sTitle:str = aTypeFile[2] + " / " + oAreaRef[enuAreasRef.desc.value] + sFormat
                        self.addFile2Catalog(False, dstFileName2, self.sHeadFileDate[:-1], sTitle, sAreaKey, oAreaRef)

                        #Fichier warning régionalisé (ex: 20210131_airspaces-ff-geoFrench-wrn.geojson)
                        srcFileName2b = str(srcFileName2).replace(".geojson", "-warning.geojson")
                        dstFileName2b = str(dstFileName2).replace(".geojson", "-wrn.geojson")
                        bWarningFile:bool = self.copyFile(self.sourcesPath, srcFileName2b, self.publishPathFiles, dstFileName2b)
                        if bWarningFile:
                            sTitleb:str = cstDangersHeader + sTitle
                            self.addFile2Catalog(False, dstFileName2b, self.sHeadFileDate[:-1], sTitleb, sAreaKey, oAreaRef)

                        sToken2 = str("@@file@@GeoJSON-airspaces-all").replace("-all", aTypeFile[0])
                        sToken2 += "-" + sAreaKey + "@@"
                        if sAreaKey=="geoFrenchAll":
                            self.publishFile(dstFileName2,  sToken2, sTitle)
                            if bWarningFile:
                                sToken2b = sToken2[:-2] + "-warning@@"
                                self.publishFile(dstFileName2b, sToken2b, sTitleb)
                        else:
                            sNewTableRows += self.makeTableRow("GeoJSON", None, sAreaKey, oAreaRef, dstFileName2, sTitle)
                if sNewTableRows:
                    self.sWebPageBuffer = self.sWebPageBuffer.replace("<tr><td></td><td>@@TR@@GeoJSON-DynamicTableRow@@</td></tr>", sNewTableRows)

            elif bCopyFile:
                sComplementaryFiles += self.makeLink4File("files", dstFileName, aTypeFile[2]) + " | "

            if aTypeFile[0]=="-freeflight":
                #Complément du fichier optimisé 'global@airspaces-ff-geoFrench-optimized.geojson'
                srcFileName2 = str(srcFileName).replace(aTypeFile[0], aTypeFile[0] + "-geoFrench-optimized")
                dstFileName2 = str(dstFileName).replace(aTypeFile[1], aTypeFile[1] + "-geoFrench-optimized")
                if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2):
                    sTitle:str = aTypeFile[2] + sFormat.replace("]", "/Vecteurs optimisés]")
                    self.addFile2Catalog(False, dstFileName2, self.sHeadFileDate[:-1], sTitle, "geoFrench", geoRefArea.GeoRefArea(False).AreasRef["geoFrench"])
                    sToken = str("@@file@@GeoJSON-airspaces-freeflight-optimized@@")
                    self.publishFile(dstFileName2, sToken, sTitle)

        self.sWebPageBuffer = self.sWebPageBuffer.replace("@@file@@GeoJSON-airspaces-othersfileslist@@", sComplementaryFiles)


        #### 4a/ Openair files "-gpsWithTopo" for XCsoar / LK8000 / XCTrack etc...
        sFormat:str = " [format Openair/" + poaffCst.cstWithTopo[1:] + "]"
        sComplementaryFiles:str = ""
        #Déclinaison de toutes les typologies de fichier racine  (-all, -ifr, -vfr, -ffvl-cfd, -ff)
        for aTypeFile in aTypeFiles:
            srcFileName = poaffCst.cstGlobalHeader + poaffCst.cstSeparatorFileName + str(poaffCst.cstAsAllOpenairFileName).replace("-all", aTypeFile[0])
            dstFileName = str(self.sHeadFileDate + poaffCst.cstAsAllOpenairFileName).replace("-all", aTypeFile[1])
            dstFileName = dstFileName.replace("airspaces-", "")
            dstFileName = dstFileName.replace(poaffCst.cstWithTopo, "")
            dstFileName = dstFileName.replace(".txt", "-withT.txt")
            bCopyFile:bool = self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName)
            if bCopyFile:
                sTitle:str = aTypeFile[2] + sFormat
                if aTypeFile[0]=="-ffvl-cfd":
                    self.addFile2Catalog(False, dstFileName, self.sHeadFileDate[:-1], sTitle, "geoFrenchAll", geoRefArea.GeoRefArea(False).AreasRef["geoFrenchAll"])
                else:
                    self.addFile2Catalog(False, dstFileName, self.sHeadFileDate[:-1], sTitle, "geoAll")
                sToken = str("@@file@@Openair-airspaces-all"+ poaffCst.cstWithTopo + "@@").replace("-all", aTypeFile[0])
                self.publishFile(dstFileName, sToken, sTitle)

                #Fichier warning non-régionalisé (ex: 20210131_airspaces-ff-withT-wrn.txt)
                srcFileNameb = str(srcFileName).replace(".txt", "-warning.txt")
                dstFileNameb = str(dstFileName).replace("-withT", "-wrn-withT")
                bWarningFile:bool = self.copyFile(self.sourcesPath, srcFileNameb, self.publishPathFiles, dstFileNameb)
                if bWarningFile:
                    sTitleb:str = cstDangersHeader + sTitle
                    self.addFile2Catalog(False, dstFileNameb, self.sHeadFileDate[:-1], sTitleb, "geoAll")
                    sTokenb = sToken[:-2] + "-warning@@"
                    self.publishFile(dstFileNameb, sTokenb, sTitleb)

            if aTypeFile[0]=="-ffvl-cfd":
                #Duplication du fichier "LastVersion"
                dstFileName2b = dstFileName.replace(self.sHeadFileDate, poaffCst.cstLastVersionFileName2)
                if self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName2b):
                    sTitle:str = aTypeFile[2] + sFormat
                    self.addFile2Catalog(True, dstFileName2b, self.sHeadFileDate[:-1], sTitle, "geoFrenchAll", geoRefArea.GeoRefArea(False).AreasRef["geoFrenchAll"])

            elif aTypeFile[0]=="-freeflight":
                #Déclinaison de toutes les régionalisations
                sNewTableRows:str = ""
                for sAreaKey, oAreaRef in geoRefArea.GeoRefArea(False).AreasRef.items():
                    if sAreaKey in ["geoFrenchNorth","geoFrenchSouth","geoFrenchNESW","geoFrenchVosgesJura","geoFrenchPyrenees","geoFrenchAlps"]:
                        continue
                    srcFileName2 = str(srcFileName).replace(".txt", "-" + sAreaKey + ".txt")
                    dstFileName2 = str(dstFileName).replace("_ff", "_ff-" + sAreaKey)
                    dstFileName2 = str(dstFileName2).replace("-geo", "-")
                    if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2):
                        sTitle:str = aTypeFile[2] + " / " + oAreaRef[enuAreasRef.desc.value] + sFormat
                        self.addFile2Catalog(False, dstFileName2, self.sHeadFileDate[:-1], sTitle, sAreaKey, oAreaRef)

                        #Fichier warning régionalisé (ex: 20210131_airspaces-ff-geoFrench-withT-wrn.txt)
                        srcFileName2b = str(srcFileName2).replace(".txt", "-warning.txt")
                        dstFileName2b = str(dstFileName2).replace("-withT", "-wrn-withT")
                        bWarningFile:bool = self.copyFile(self.sourcesPath, srcFileName2b, self.publishPathFiles, dstFileName2b)
                        if bWarningFile:
                            sTitleb:str = cstDangersHeader + sTitle
                            self.addFile2Catalog(False, dstFileName2b, self.sHeadFileDate[:-1], sTitleb, sAreaKey, oAreaRef)

                        sToken2 = str("@@file@@Openair-airspaces-all" + poaffCst.cstWithTopo).replace("-all", aTypeFile[0])
                        sToken2 += "-" + sAreaKey + "@@"
                        if sAreaKey=="geoFrenchAll":
                            self.publishFile(dstFileName2, sToken2, sTitle)
                            if bWarningFile:
                                sToken2b = sToken2[:-2] + "-warning@@"
                                self.publishFile(dstFileName2b, sToken2b, sTitleb)
                        else:
                            sNewTableRows += self.makeTableRow("Openair", sToken2, sAreaKey, oAreaRef, dstFileName2, sTitle)

                        #Duplication des fichiers "LastVersion" de la France
                        if sAreaKey in ["geoFrench","geoCorse","geoLaReunion","geoPolynesieFr"]:
                            dstFileName2b = dstFileName2.replace(self.sHeadFileDate, poaffCst.cstLastVersionFileName2)
                            if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2b):
                                self.addFile2Catalog(True, dstFileName2b, self.sHeadFileDate[:-1], sTitle, sAreaKey, oAreaRef)

                        #Traitement de tous les fichiers complémentaires épurés par jour d'activité
                        sLinks, sFind = self.publishFilesExeptDays(sToken2, srcFileName2, dstFileName2, aTypeFile[2], poaffCst.cstWithTopo[1:], sAreaKey, oAreaRef[enuAreasRef.desc.value], oAreaRef)
                        if sAreaKey=="geoFrenchAll":
                            self.sWebPageBuffer = self.sWebPageBuffer.replace(sFind, sLinks)
                        else:
                            sNewTableRows= sNewTableRows.replace(sFind, sLinks)

                if sNewTableRows:
                    self.sWebPageBuffer = self.sWebPageBuffer.replace("<tr><td></td><td>@@TR@@Openair-gpsWithTopo-DynamicTableRow@@</td></tr>", sNewTableRows)

            elif bCopyFile:
                sTitle:str = aTypeFile[2] + sFormat
                sComplementaryFiles += self.makeLink4File("files", dstFileName, sTitle) + " | "

        self.sWebPageBuffer = self.sWebPageBuffer.replace("@@file@@Openair-airspaces" + poaffCst.cstWithTopo + "-othersfileslist@@", sComplementaryFiles)


        #### 4b/ Openair files "-gpsWithTopo" for 'Flymaster SDs' or LimitedMemory
        sFormat:str = " [format Openair/" + poaffCst.cstWithTopo[1:] + "]"
        sComplementaryFiles:str = ""
        #Déclinaison de toutes les typologies de fichier racine  (-all, -ifr, -vfr, -ffvl-cfd, -ff)
        for aTypeFile in aTypeFiles:
            if aTypeFile[0]=="-freeflight":
                #Déclinaison de toutes les régionalisations
                sNewTableRows:str = ""
                for sAreaKey, oAreaRef in geoRefArea.GeoRefArea(False).AreasRef.items():
                    if not sAreaKey in ["geoFrenchNorth","geoFrenchSouth","geoFrenchNESW","geoFrenchVosgesJura","geoFrenchPyrenees","geoFrenchAlps"]:
                        continue
                    srcFileName2 = str(srcFileName).replace(".txt", "-" + sAreaKey + ".txt")
                    dstFileName2 = str(dstFileName).replace("_ff", "_ff-" + sAreaKey)
                    dstFileName2 = str(dstFileName2).replace("-geo", "-")
                    #dstFileName2 = str(dstFileName2).replace(poaffCst.cstWithTopo, "")
                    #dstFileName2 = str(dstFileName2).replace(".txt", "-withT.txt")
                    if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2):
                        sTitle:str = aTypeFile[2] + " / " + oAreaRef[enuAreasRef.desc.value] + sFormat
                        self.addFile2Catalog(False, dstFileName2, self.sHeadFileDate[:-1], sTitle, sAreaKey, oAreaRef)

                        #Fichier warning régionalisé (ex: 20210131_airspaces-ff-geoFrenchNorth-withT-wrn.txt)
                        srcFileName2b = str(srcFileName2).replace(".txt", "-warning.txt")
                        dstFileName2b = str(dstFileName2).replace("-withT", "-wrn-withT")
                        bWarningFile:bool = self.copyFile(self.sourcesPath, srcFileName2b, self.publishPathFiles, dstFileName2b)
                        if bWarningFile:
                            sTitleb:str = cstDangersHeader + sTitle
                            self.addFile2Catalog(False, dstFileName2b, self.sHeadFileDate[:-1], sTitleb, sAreaKey, oAreaRef)

                        sToken2 = str("@@file@@Openair-airspaces-all"+ poaffCst.cstWithTopo).replace("-all", aTypeFile[0])
                        sToken2 += "-" + sAreaKey + "@@"
                        sNewTableRows += self.makeTableRow("Openair", sToken2, sAreaKey, oAreaRef, dstFileName2, sTitle)

                        #Traitement de tous les fichiers complémentaires épurés par jour d'activité
                        sLinks, sFind = self.publishFilesExeptDays(sToken2, srcFileName2, dstFileName2, aTypeFile[2], poaffCst.cstWithTopo[1:], sAreaKey, oAreaRef[enuAreasRef.desc.value], oAreaRef)
                        sNewTableRows= sNewTableRows.replace(sFind, sLinks)

                if sNewTableRows:
                    self.sWebPageBuffer = self.sWebPageBuffer.replace("<tr><td></td><td>@@TR@@Openair-gpsWithTopo-LimitedMemory-DynamicTableRow@@</td></tr>", sNewTableRows)

            elif bCopyFile:
                sTitle:str = aTypeFile[2] + sFormat
                sComplementaryFiles += self.makeLink4File("files", dstFileName, sTitle) + " | "

        self.sWebPageBuffer = self.sWebPageBuffer.replace("@@file@@Openair-airspaces" + poaffCst.cstWithTopo + "-othersfileslist@@", sComplementaryFiles)


        #### 4c/ Openair files "-gpsWithoutTopo" for Flytec / Brauniger
        sFormat:str = " [format Openair/" + poaffCst.cstWithoutTopo[1:] + "]"
        sComplementaryFiles:str = ""
        #Déclinaison de toutes les typologies de fichier racine  (-all, -ifr, -vfr, -ffvl-cfd, -ff)
        for aTypeFile in aTypeFiles:
            srcFileName = poaffCst.cstGlobalHeader + poaffCst.cstSeparatorFileName + str(poaffCst.cstAsAllOpenairFileName).replace("-all", aTypeFile[0])
            dstFileName = str(self.sHeadFileDate + poaffCst.cstAsAllOpenairFileName).replace("-all", aTypeFile[1])
            dstFileName = dstFileName.replace("airspaces-", "")
            srcFileName = srcFileName.replace(poaffCst.cstWithTopo, poaffCst.cstWithoutTopo)
            dstFileName = dstFileName.replace(poaffCst.cstWithTopo, "")
            dstFileName = dstFileName.replace(".txt", "-outT.txt")
            bCopyFile:bool = self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName)
            if bCopyFile:
                sTitle:str = aTypeFile[2] + sFormat
                if aTypeFile[0]=="-ffvl-cfd":
                    self.addFile2Catalog(False, dstFileName, self.sHeadFileDate[:-1], sTitle, "geoFrenchAll", geoRefArea.GeoRefArea(False).AreasRef["geoFrenchAll"])
                else:
                    self.addFile2Catalog(False, dstFileName, self.sHeadFileDate[:-1], sTitle, "geoAll")
                sToken = str("@@file@@Openair-airspaces-all"+ poaffCst.cstWithoutTopo + "@@").replace("-all", aTypeFile[0])
                self.publishFile(dstFileName, sToken, sTitle)

                #Fichier warning non-régionalisé (ex: 20210131_airspaces-ff-outT-wrn.txt)
                srcFileNameb = str(srcFileName).replace(".txt", "-warning.txt")
                dstFileNameb = str(dstFileName).replace("-outT", "-wrn-outT")
                bWarningFile:bool = self.copyFile(self.sourcesPath, srcFileNameb, self.publishPathFiles, dstFileNameb)
                if bWarningFile:
                    sTitleb:str = cstDangersHeader + sTitle
                    self.addFile2Catalog(False, dstFileNameb, self.sHeadFileDate[:-1], sTitleb, "geoAll")
                    sTokenb = sToken[:-2] + "-warning@@"
                    self.publishFile(dstFileNameb, sTokenb, sTitleb)

            if aTypeFile[0]=="-freeflight":
                #Déclinaison de toutes les régionalisations
                sNewTableRows:str = ""
                for sAreaKey, oAreaRef in geoRefArea.GeoRefArea(False).AreasRef.items():
                    if sAreaKey in ["geoFrenchNorth","geoFrenchSouth","geoFrenchNESW","geoFrenchVosgesJura","geoFrenchPyrenees","geoFrenchAlps"]:
                        continue
                    srcFileName2 = str(srcFileName).replace(".txt", "-" + sAreaKey + ".txt")
                    dstFileName2 = str(dstFileName).replace("_ff", "_ff-" + sAreaKey)
                    dstFileName2 = str(dstFileName2).replace("-geo", "-")
                    if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2):
                        sTitle:str = aTypeFile[2] + " / " + oAreaRef[enuAreasRef.desc.value] + sFormat
                        self.addFile2Catalog(False, dstFileName2, self.sHeadFileDate[:-1], sTitle, sAreaKey, oAreaRef)

                        #Fichier warning régionalisé (ex: 20210131_airspaces-ff-geoFrench-outT-wrn.txt)
                        srcFileName2b = str(srcFileName2).replace(".txt", "-warning.txt")
                        dstFileName2b = str(dstFileName2).replace("-outT", "-wrn-outT")
                        bWarningFile:bool = self.copyFile(self.sourcesPath, srcFileName2b, self.publishPathFiles, dstFileName2b)
                        if bWarningFile:
                            sTitleb:str = cstDangersHeader + sTitle
                            self.addFile2Catalog(False, dstFileName2b, self.sHeadFileDate[:-1], sTitleb, sAreaKey, oAreaRef)

                        sToken2 = str("@@file@@Openair-airspaces-all"+ poaffCst.cstWithoutTopo).replace("-all", aTypeFile[0])
                        sToken2 += "-" + sAreaKey + "@@"
                        if sAreaKey=="geoFrenchAll":
                            self.publishFile(dstFileName2, sToken2, sTitle)
                            if bWarningFile:
                                sToken2b = sToken2[:-2] + "-warning@@"
                                self.publishFile(dstFileName2b, sToken2b, sTitleb)
                        else:
                            sNewTableRows += self.makeTableRow("Openair", sToken2, sAreaKey, oAreaRef, dstFileName2, sTitle, True)

                        #Duplication des fichiers "LastVersion" de la France
                        if sAreaKey in ["geoFrench"]:
                            dstFileName2b = dstFileName2.replace(self.sHeadFileDate, poaffCst.cstLastVersionFileName2)
                            if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2b):
                                self.addFile2Catalog(True, dstFileName2b, self.sHeadFileDate[:-1], sTitle, sAreaKey, oAreaRef)

                        #Traitement de tous les fichiers complémentaires épurés par jour d'activité
                        sLinks, sFind = self.publishFilesExeptDays(sToken2, srcFileName2, dstFileName2, aTypeFile[2], poaffCst.cstWithoutTopo[1:], sAreaKey, oAreaRef[enuAreasRef.desc.value], oAreaRef)
                        if sAreaKey=="geoFrenchAll":
                            self.sWebPageBuffer = self.sWebPageBuffer.replace(sFind, sLinks)
                        else:
                            sNewTableRows= sNewTableRows.replace(sFind, sLinks)

                if sNewTableRows:
                    self.sWebPageBuffer = self.sWebPageBuffer.replace("<tr><td></td><td>@@TR@@Openair-gpsWithoutTopo-DynamicTableRow@@</td></tr>", sNewTableRows)

            elif bCopyFile:
                sTitle:str = aTypeFile[2] + sFormat
                sComplementaryFiles += self.makeLink4File("files", dstFileName, sTitle) + " | "

        self.sWebPageBuffer = self.sWebPageBuffer.replace("@@file@@Openair-airspaces" + poaffCst.cstWithoutTopo + "-othersfileslist@@", sComplementaryFiles)


        #### 4d/ Openair files "-gpsWithoutTopo" for 'Flymaster' or LimitedMemory
        sFormat:str = " [format Openair/" + poaffCst.cstWithoutTopo[1:] + "]"
        sComplementaryFiles:str = ""
        #Déclinaison de toutes les typologies de fichier racine  (-all, -ifr, -vfr, -ffvl-cfd, -ff)
        for aTypeFile in aTypeFiles:
            if aTypeFile[0]=="-freeflight":
                #Déclinaison de toutes les régionalisations
                sNewTableRows:str = ""
                for sAreaKey, oAreaRef in geoRefArea.GeoRefArea(False).AreasRef.items():
                    if not sAreaKey in ["geoFrenchNorth","geoFrenchSouth","geoFrenchNESW","geoFrenchVosgesJura","geoFrenchPyrenees","geoFrenchAlps"]:
                        continue
                    srcFileName2 = str(srcFileName).replace(".txt", "-" + sAreaKey + ".txt")
                    dstFileName2 = str(dstFileName).replace("_ff", "_ff-" + sAreaKey)
                    dstFileName2 = str(dstFileName2).replace("-geo", "-")
                    if self.copyFile(self.sourcesPath, srcFileName2, self.publishPathFiles, dstFileName2):
                        sTitle:str = aTypeFile[2] + " / " + oAreaRef[enuAreasRef.desc.value] + sFormat
                        self.addFile2Catalog(False, dstFileName2, self.sHeadFileDate[:-1], sTitle, sAreaKey, oAreaRef)

                        #Fichier warning régionalisé (ex: 20210131_airspaces-ff-geoFrenchNorth-outT-wrn.txt)
                        srcFileName2b = str(srcFileName2).replace(".txt", "-warning.txt")
                        dstFileName2b = str(dstFileName2).replace("-outT", "-wrn-outT")
                        bWarningFile:bool = self.copyFile(self.sourcesPath, srcFileName2b, self.publishPathFiles, dstFileName2b)
                        if bWarningFile:
                            sTitleb:str = cstDangersHeader + sTitle
                            self.addFile2Catalog(False, dstFileName2b, self.sHeadFileDate[:-1], sTitleb, sAreaKey, oAreaRef)

                        sToken2 = str("@@file@@Openair-airspaces-all"+ poaffCst.cstWithoutTopo).replace("-all", aTypeFile[0])
                        sToken2 += "-" + sAreaKey + "@@"
                        sNewTableRows += self.makeTableRow("Openair", sToken2, sAreaKey, oAreaRef, dstFileName2, sTitle)

                        #Traitement de tous les fichiers complémentaires épurés par jour d'activité
                        sLinks, sFind = self.publishFilesExeptDays(sToken2, srcFileName2, dstFileName2, aTypeFile[2], poaffCst.cstWithoutTopo[1:], sAreaKey, oAreaRef[enuAreasRef.desc.value], oAreaRef)
                        sNewTableRows= sNewTableRows.replace(sFind, sLinks)

                if sNewTableRows:
                    self.sWebPageBuffer = self.sWebPageBuffer.replace("<tr><td></td><td>@@TR@@Openair-gpsWithoutTopo-LimitedMemory-DynamicTableRow@@</td></tr>", sNewTableRows)

            elif bCopyFile:
                sTitle:str = aTypeFile[2] + sFormat
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
            sFrDate:str = bpaTools.getDate(cstPOAFFdateTrait, frmt="dmy", sep="/")
            if not sFrDate in aPubDates:
                aPubDates.append(sFrDate)
                oJsonParam.update({sParamPubDates:aPubDates})
                bpaTools.writeJsonFile(self.publishPath + sFilePubDates, oJsonParam)
            sBuffStr:str = "; ".join(aPubDates[0:-1])
            sBuffStr += "; <b>" + aPubDates[-1] + "</b>"
            self.sWebPageBuffer = self.sWebPageBuffer.replace("@@DatesList@@webPublicationDates@@", sBuffStr)
            self.sWebPageBuffer = self.sWebPageBuffer.replace("@@DatesList@@webPublicationLastDate@@", str(aPubDates[-1]))
            sAIRACdates:str = cstAIRACdateStart.strftime("%d/%m/%Y") + " au " + cstAIRACdateEnd.strftime("%d/%m/%Y")
            self.sWebPageBuffer = self.sWebPageBuffer.replace("@@DatesList@@AIRACdates@@", sAIRACdates)

            sNewWebPage:str = "index.htm"
            sMsg = "Creating Web file - {}".format(sNewWebPage)
            self.oLog.info(sMsg, outConsole=True)
            fWebPageIndex = open(self.publishPath + sNewWebPage, "w", encoding="utf-8", errors="ignore")	#or encoding="cp1252"
            fWebPageIndex.write(self.sWebPageBuffer)
            fWebPageIndex.close()
            self.copyFile(self.publishPath, sNewWebPage, self.publishPath, self.sHeadFileDate + sNewWebPage)
        return

    #Traitement de tous les fichiers complémentaires épurés par jour d'activité
    def publishFilesExeptDays(self, sToken:str, sSrcFile:str, sDstFile:str, sTypeFile:str, sGpsType:str, sAreaKey:str="", sAreaDesc:str="", oAreaRef:list=None) -> str:
        aExeptDays:list =   [ ["-forSAT", "4SAT", "Fichier spécifiquement utilisable les 'SATerday/Samedis' (dépourvu des zones non-activables 'exceptSAT')"], \
                              ["-forSUN", "4SUN", "Fichier spécifiquement utilisable les 'SUNday/Dimanches' (dépourvu des zones non-activables 'exceptSUN')"], \
                              ["-forHOL", "4HOL", "Fichier spécifiquement utilisable les 'HOLiday/Jours-Fériés' (dépourvu des zones non-activables 'exceptHOL')"]]
        sDayFiles:str=""
        for sDayKey, sDayDst, sDayDesc in aExeptDays:
            srcFileName = str(sSrcFile).replace(".txt", sDayKey + ".txt")
            #dstFileName = str(sDstFile).replace(sAreaKey[4:], sAreaKey[4:] + sDayDst) #frmt 20210525_ff-FrenchAll4SAT-outT.txt
            dstFileName = str(sDstFile).replace("_ff", "_ff" + sDayDst)
            if self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName):
                sFormat:str = " [format Openair/"
                if sAreaDesc:
                    sTitle:str = sTypeFile + " / " + sAreaDesc + " / " + sDayDesc + sFormat + sGpsType + "/" + sDayKey[1:] + "]"
                else:
                    sTitle:str = sTypeFile + " / " + sDayDesc + sFormat + sGpsType + "/" + sDayKey[1:] + "]"
                self.addFile2Catalog(False, dstFileName, self.sHeadFileDate[:-1], sTitle, sAreaKey, oAreaRef)
                sDayFiles += "<li>" + self.makeLink4File("files", dstFileName, sTitle) + "</li>"

                #Duplication du fichier "LastVersion" de la France
                if sAreaKey in ["geoFrench"]:
                    dstFileName2 = dstFileName.replace(self.sHeadFileDate, poaffCst.cstLastVersionFileName2)
                    if self.copyFile(self.sourcesPath, srcFileName, self.publishPathFiles, dstFileName2):
                        self.addFile2Catalog(True, dstFileName2, self.sHeadFileDate[:-1], sTitle, sAreaKey, oAreaRef)

        if sAreaKey:
            sToken2 = sToken.replace(sAreaKey, sAreaKey + "-forDAYS")
        else:
            sToken2 = sToken.replace(sGpsType, sGpsType + "-forDAYS")

        #old - self.sWebPageBuffer = self.sWebPageBuffer.replace(sToken2, sDayFiles)
        return sDayFiles, sToken2

    def makeTableRow(self, sFileType:str, sToken:str, sAreaKey:str, oAreaRef:list, dstFileName:str, sTitle:str, bFAF:bool=False) -> str:
        aTableCols:list = []
        sQualityMsg:str     = "(i) Qualité des données non garantie..."
        bQualityLight:bool  = sAreaKey[:9]!="geoFrench" and not sAreaKey in ["geoPWCFrenchAlps","geoCorse","geoLaReunion","geoGuyaneFr","geoStPierreEtMiquelon","geoAntillesFr","geoMayotte","geoPolynesieFr","geoNouvelleCaledonie"]

        sWarnFile:str       = dstFileName.replace(sAreaKey[4:], sAreaKey[4:] + "-wrn")
        bWarnFile:bool      = os.path.exists(self.publishPathFiles + sWarnFile)

        sFileExt:str        = bpaTools.getFileExt(dstFileName)
        sKmlFile:str        = dstFileName.replace(sFileExt, ".kml")
        sKmlFile            = sKmlFile.replace("-withT", "")            #sKmlFile.replace("-gpsWithTopo", "")
        sKmlFile            = sKmlFile.replace("-outT", "")             #sKmlFile.replace("-gpsWithoutTopo", "")
        sKmlWarnFile:str    = sKmlFile.replace(".", "-wrn.")
        bKmlFile:bool       = os.path.exists(self.publishPathFiles + sKmlFile)
        bKmlWarnFile:bool   = os.path.exists(self.publishPathFiles + sKmlWarnFile)
        if bKmlFile or bKmlWarnFile:
            sEndOf:str      = bpaTools.getContentOf(sTitle, "[", "]")
            sTitleClean:str   = sTitle.replace("[" + sEndOf + "]", "")
            sTitle3D:str       = sTitleClean.replace("Cartographie", "Cartographie 3D")
            sTitleWarn3D:str   = sTitle3D.replace(" 3D ", " 3D des zones dangereuses ")

        #--Colonne 1--
        sCellContent:str = cstTextBold.format(oAreaRef[enuAreasRef.desc.value])
        if (sAreaKey[:9]=="geoFrench") or (sAreaKey in ["geoPWCFrenchAlps"]):
            sCellContent += '<br/>avec ZSM (Zone de Sensibilité Majeure)'
        aTableCols.append(cstCellStd.format(sCellContent))
        #--Colonne 2-- - bloc images-a-gauche
        sCellContent:str = ''
        sContent:str = ''
        sImgFile = 'img/' + sAreaKey + '_localization.jpg'
        if os.path.exists(self.publishPath + sImgFile):
            sContent:str = '<a title="Localisation..." target="map" href="' + sImgFile + '"><img height="50" src="' + sImgFile + '" /></a> '
        sImgFile = 'img/' + sAreaKey + '_border.jpg'
        if os.path.exists(self.publishPath + sImgFile):
            sContent += '<a title="Découpage..." target="map" href="' + sImgFile + '"><img height="50" src="' + sImgFile + '" /></a>'
        if True:  #sFileType=="GeoJSON":
            sPath:str = 'files/geoRef/'
            sFile:str =  sAreaKey + '_border.geojson'
            if os.path.exists(self.publishPath + sPath + sFile):
                sContent += '<br/>' + self.makeLink4File(sPath[:-1], sFile, "GeoJSON Border file...", "GeoJSON Border")
        if sContent:
            sCellContent:str = cstSpanLeft.format(sContent)
        #--Colonne 2-- - bloc images-a-droite
        sContent:str = ''
        sImgFile = 'img/' + sAreaKey + '_sample_GeoJSON.jpg'
        if os.path.exists(self.publishPath + sImgFile):
            if bWarnFile:
                sImgFileb = 'img/' + sAreaKey + '-warning_sample_GeoJSON.jpg'
                sContent += '<a title="Dangers dans la zone..." target="map" href="' + sImgFileb + '"><img height="50" src="' + sImgFileb + '" /></a> '
            sContent += '<a title="Exemple de représentation..." target="map" href="' + sImgFile + '"><img height="50" src="' + sImgFile + '" /></a>'
            sKmlLinks:str=""
            if bKmlWarnFile:
                sKmlLinks += self.makeLink4File("files", sKmlWarnFile, sTitleWarn3D + "[format KML]", "KML-Warning") + ' / '
            if bKmlFile:
                sKmlLinks += self.makeLink4File("files", sKmlFile, sTitle3D + "[format KML]", "KML-Map")
            if sKmlLinks:
                sContent += '<br/>' + sKmlLinks
            if bQualityLight:
                sContent += '<br/><a title="' + sQualityMsg + '"><img height="30" src="img/travaux.png" /></a>'
            sCellContent += cstSpanRight.format(sContent)
        #--Colonne 2-- - bloc contenu
        sCellContent += cstTextBold.format(oAreaRef[enuAreasRef.desc.value])
        if oAreaRef[enuAreasRef.descComp.value]:
            sCellContent += '<br/>' + str(oAreaRef[enuAreasRef.descComp.value]).replace("\n", "<br/>")
        sCellContent += '<br/>'
        if bQualityLight:
            sCellContent += '<br/>' + cstTextItalic.format(sQualityMsg)
        else:
            sCellContent += '<br/>'
        if sToken:
            sToken2:str = sToken.replace(sAreaKey, sAreaKey + "-forDAYS")
            #sCellContent += '<br/><br/>' + sToken2
            sCellContent += sToken2
        aTableCols.append(cstCellCenter.format(sCellContent))
        #--Colonne 3--
        sContent:str = sFileType
        if bFAF:
            sContent += ' et FAF'
        sContent += ' - ' + oAreaRef[enuAreasRef.desc.value] + ' - Vol-libre'
        sCellContent:str = cstTextBold.format(cstTextUnderlined.format(sContent))
        sCellContent += '<ul>'
        sCellContent += '<li>' + self.makeLink4File("files", dstFileName, sTitle) + '</li>'
        if bWarnFile:
            sCellContent += '<li>' + self.makeLink4File("files", sWarnFile, cstDangersHeader + sTitle) + '</li>'
        if bFAF:
            sCellContent += '<li><b>FAF</b> - <i>non disponible (en cours de réalisation)</i></li>'
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

    def makeLink4File(self, sPath:str, sFile:str, sTitle:str, sLinkName:str="") -> str:
        cstStdLync:str  = '<a title="@@title@@" target="newPage" href="download.php?file=@@path@@/@@file@@">@@linkName@@</a>'
        sNewLink:str    = cstStdLync.replace("@@title@@", sTitle)
        sNewLink        = sNewLink.replace("@@path@@", sPath)
        sNewLink        = sNewLink.replace("@@file@@", sFile)
        if not sLinkName:
            sLinkName = sFile
        sNewLink        = sNewLink.replace("@@linkName@@", sLinkName)
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
    oWeb.createPoaffWebPage()                                   #Preparation pour publication

    print()
    oLog.Report()
    oLog.closeFile()
