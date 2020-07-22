#!/usr/bin/env python3

import shutil
import bpaTools
import poaffCst

cstTemplateMoveTo:str       = "/__template__Index-MoveP2P.htm"
cstTemplateWebPage:str      = "__template__Index-Main.htm"
cstNewWebPage:str           = "index.htm"


class PoaffWebPage:
    
    def __init__(self, oLog, outPath:str)-> None:
        bpaTools.initEvent(__file__, oLog)
        self.oLog                   = oLog
        self.outPath                = outPath
        return

    def createPoaffWebPage(self, sHeadFileDate:str=None) -> None:
        if sHeadFileDate==None:
            sHeadFileDate:str = "{0}_".format(bpaTools.getDateNow())
    
        #### 1/ repository for POAFF
        fTemplate = open(poaffCst.cstPoaffWebPath + cstTemplateWebPage, "r", encoding="utf-8", errors="ignore")
        sPoaffWebPageBuffer = fTemplate.read()
        fTemplate.close()
    
        fVerionCatalog = open(poaffCst.cstPoaffWebPath + "files/LastVersionsCatalog_BPa.txt", "w", encoding="utf-8", errors="ignore")
        fVerionCatalog.write("Fichier;Date de transformation;Date d'origine de la source;Description\n")
    
        # Openair gpsWithTopo files
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/", "EuCtrl@airspaces-all-gpsWithTopo.txt", sHeadFileDate + "airspaces-all-gpsWithTopo.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-all-gpsWithTopo@@")
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/", "EuCtrl@airspaces-ifr-gpsWithTopo.txt", sHeadFileDate + "airspaces-ifr-gpsWithTopo.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-ifr-gpsWithTopo@@")
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/", "EuCtrl@airspaces-vfr-gpsWithTopo.txt", sHeadFileDate + "airspaces-vfr-gpsWithTopo.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-vfr-gpsWithTopo@@")
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithTopo.txt", sHeadFileDate + "airspaces-freeflight-gpsWithTopo.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-freeflight-gpsWithTopo@@")
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithTopo-forSAT.txt", sHeadFileDate + "airspaces-freeflight-gpsWithTopo-forSAT.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-freeflight-gpsWithTopo-forSAT@@")
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithTopo-forSUN.txt", sHeadFileDate + "airspaces-freeflight-gpsWithTopo-forSUN.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-freeflight-gpsWithTopo-forSUN@@")
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithTopo-forHOL.txt", sHeadFileDate + "airspaces-freeflight-gpsWithTopo-forHOL.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-freeflight-gpsWithTopo-forHOL@@")
    
        # LastVersion - (similar files of Openair gpsWithTopo files)
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithTopo.txt", "LastVersion_FR-BPa4XCsoar.txt", sPoaffWebPageBuffer, "@@file@@Openair-LastVersion-gpsWithTopo@@")
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithTopo-forSAT.txt", "LastVersion_FR-BPa4XCsoar-forSAT.txt", sPoaffWebPageBuffer, "@@file@@Openair-LastVersion-gpsWithTopo-forSAT@@")
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithTopo-forSUN.txt", "LastVersion_FR-BPa4XCsoar-forSUN.txt", sPoaffWebPageBuffer, "@@file@@Openair-LastVersion-gpsWithTopo-forSUN@@")
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithTopo-forHOL.txt", "LastVersion_FR-BPa4XCsoar-forHOL.txt", sPoaffWebPageBuffer, "@@file@@Openair-LastVersion-gpsWithTopo-forHOL@@")
        fVerionCatalog.write("LastVersion_FR-BPa4XCsoar.txt;" + sHeadFileDate[:-1] + ";" + sHeadFileDate[:-1] + ";OpenAir France spécifique pour XCsoar, LK8000, XCTrack, FlyMe, Compass ou Syride\n")
        fVerionCatalog.write("LastVersion_FR-BPa4XCsoar-forSAT.txt;" + sHeadFileDate[:-1] + ";" + sHeadFileDate[:-1] + ";OpenAir France spécifiquement utilisable les SAMEDIs ; pour XCsoar, LK8000, XCTrack, FlyMe, Compass ou Syride\n")
        fVerionCatalog.write("LastVersion_FR-BPa4XCsoar-forSUN.txt;" + sHeadFileDate[:-1] + ";" + sHeadFileDate[:-1] + ";OpenAir France spécifiquement utilisable les DIMANCHEs ; pour XCsoar, LK8000, XCTrack, FlyMe, Compass ou Syride\n")
        fVerionCatalog.write("LastVersion_FR-BPa4XCsoar-forHOL.txt;" + sHeadFileDate[:-1] + ";" + sHeadFileDate[:-1] + ";OpenAir France spécifiquement utilisable les Jours-Fériés ; pour XCsoar, LK8000, XCTrack, FlyMe, Compass ou Syride\n")
    
        # Openair gpsWithoutTopo files
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithoutTopo.txt", sHeadFileDate + "airspaces-freeflight-gpsWithoutTopo.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-freeflight-gpsWithoutTopo@@")
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithoutTopo-forSAT.txt", sHeadFileDate + "airspaces-freeflight-gpsWithoutTopo-forSAT.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-freeflight-gpsWithoutTopo-forSAT@@")
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithoutTopo-forSUN.txt", sHeadFileDate + "airspaces-freeflight-gpsWithoutTopo-forSUN.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-freeflight-gpsWithoutTopo-forSUN@@")
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight-gpsWithoutTopo-forHOL.txt", sHeadFileDate + "airspaces-freeflight-gpsWithoutTopo-forHOL.txt", sPoaffWebPageBuffer, "@@file@@Openair-airspaces-freeflight-gpsWithoutTopo-forHOL@@")
    
        # GeoJSON files
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/", "EuCtrl@airspaces-all.geojson", sHeadFileDate + "airspaces-all.geojson", sPoaffWebPageBuffer, "@@file@@GeoJSON-airspaces-all@@")
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/", "EuCtrl@airspaces-ifr.geojson", sHeadFileDate + "airspaces-ifr.geojson", sPoaffWebPageBuffer, "@@file@@GeoJSON-airspaces-ifr@@")
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/", "EuCtrl@airspaces-vfr.geojson", sHeadFileDate + "airspaces-vfr.geojson", sPoaffWebPageBuffer, "@@file@@GeoJSON-airspaces-vfr@@")
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight.geojson", sHeadFileDate + "airspaces-freeflight.geojson", sPoaffWebPageBuffer, "@@file@@GeoJSON-airspaces-freeflight@@")
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/", "EuCtrl@airspaces-freeflight.geojson", "LastVersion_airspaces-freeflight.geojson", sPoaffWebPageBuffer, "@@file@@GeoJSON-LastVersion-freeflight@@")
        fVerionCatalog.write("LastVersion_airspaces-freeflight.geojson;" + sHeadFileDate[:-1] + ";" + sHeadFileDate[:-1] + ";GeoJSON spécifiquement utilisable pour la CFD\n")
    
        # Calalog files
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/" + poaffCst.cstReferentialPath, "EuCtrl@airspacesCatalog.csv", sHeadFileDate + "airspacesCatalog.csv", sPoaffWebPageBuffer, "@@file@@CSV-airspacesCatalog@@")
        sPoaffWebPageBuffer = self.moveFile(self.outPath + "EuCtrl/" + poaffCst.cstReferentialPath, "EuCtrl" + poaffCst.cstSeparatorFileName + poaffCst.cstCatalogFileName, sHeadFileDate + "airspacesCatalog.json", sPoaffWebPageBuffer, "@@file@@JSON-airspacesCatalog@@")
        fVerionCatalog.write(sHeadFileDate + "airspacesCatalog.csv;" + sHeadFileDate[:-1] + ";" + sHeadFileDate[:-1] + ";Catalogue des espaces-aériens au format CSV\n")
        fVerionCatalog.write(sHeadFileDate + "airspacesCatalog.json;" + sHeadFileDate[:-1] + ";" + sHeadFileDate[:-1] + ";Catalogue des espaces-aériens au format JSON\n")
        fVerionCatalog.close()
    
        #### 2/ repository for CFD
        # GeoJSON and Catalog files
        shutil.copyfile(self.outPath + "EuCtrl/EuCtrl@airspaces-all.geojson", poaffCst.cstCfdWebPath + "/airspaces-all.geojson")
        shutil.copyfile(self.outPath + "EuCtrl/EuCtrl@airspaces-ifr.geojson", poaffCst.cstCfdWebPath + "/airspaces-ifr.geojson")
        shutil.copyfile(self.outPath + "EuCtrl/EuCtrl@airspaces-vfr.geojson", poaffCst.cstCfdWebPath + "/airspaces-vfr.geojson")
        shutil.copyfile(self.outPath + "EuCtrl/EuCtrl@airspaces-freeflight.geojson", poaffCst.cstCfdWebPath + "/airspaces-freeflight.geojson")
        shutil.copyfile(self.outPath + "EuCtrl/" + poaffCst.cstReferentialPath + "EuCtrl@airspacesCatalog.csv", poaffCst.cstCfdWebPath + "/airspacesCatalog.csv")
        shutil.copyfile(self.outPath + "EuCtrl/" + poaffCst.cstReferentialPath + "EuCtrl" + poaffCst.cstSeparatorFileName + poaffCst.cstCatalogFileName, poaffCst.cstCfdWebPath + "/airspacesCatalog.json")
    
        #### 3/ creating html main page
        sMsg = "Creating Web file - {}".format(cstNewWebPage)
        self.oLog.info(sMsg, outConsole=True)
        fWebPageIndex = open(poaffCst.cstPoaffWebPath + cstNewWebPage, "w", encoding="utf-8", errors="ignore")
        fWebPageIndex.write(sPoaffWebPageBuffer)
        fWebPageIndex.close()
        shutil.copyfile(poaffCst.cstPoaffWebPath + cstNewWebPage, poaffCst.cstPoaffWebPath + sHeadFileDate + cstNewWebPage)
    
        #### 4/ securisation and move to html main page
        sFileMoveTo = poaffCst.cstPoaffWebPath + cstTemplateMoveTo
        shutil.copyfile(sFileMoveTo, poaffCst.cstPoaffWebPath + "files/index.htm")
        shutil.copyfile(sFileMoveTo, poaffCst.cstPoaffWebPath + "files/res/index.htm")
        shutil.copyfile(sFileMoveTo, poaffCst.cstPoaffWebPath + "img/index.htm")
        shutil.copyfile(sFileMoveTo, poaffCst.cstPoaffWebPath + "palette01/index.htm")
        shutil.copyfile(sFileMoveTo, poaffCst.cstPoaffWebPath + "palette01/img/index.htm")
        return

    def moveFile(self, sSrcPath:str, sSrcFile:str, sCpyFileName:str, sPoaffWebPageBuffer, sToken:str) -> None:
        sCpyFile = "{0}{1}{2}".format(poaffCst.cstPoaffWebPath, "files/", sCpyFileName)
        shutil.copyfile(sSrcPath + sSrcFile, sCpyFile)
        self.oLog.info("Move file : {0} --> {1}".format(sSrcFile, sCpyFileName), outConsole=False)
        return sPoaffWebPageBuffer.replace(sToken, sCpyFileName)
    
