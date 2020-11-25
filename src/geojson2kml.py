#!/usr/bin/env python3
try:
    import bpaTools
except ImportError:
    ### Include local modules/librairies  ##
    import os
    import sys
    aixmParserLocalSrc  = "../../aixmParser/src/"
    module_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(module_dir, aixmParserLocalSrc))
    import bpaTools

import poaffCst

class Geojson2Kml:

    def __init__(self, oLog=None, oGeo:dict=None)-> None:
        self.oLog = None
        if oLog:
            bpaTools.initEvent(__file__, oLog)
            self.oLog:bpaTools.Logger = oLog        #Log file
        self.oKmlTmp:dict = {}
        self.oKml:bpaTools.Xml = None
        self.oKmlDoc = None
        self.oGeo:dict = None
        if oGeo:
            self.oGeo:dict = oGeo
        return

    def readGeojsonFile(self, fileSrc:str) -> None:
        sMsg = "Read file - " + fileSrc
        if self.oLog:
            self.oLog.info(sMsg, outConsole=False)
        else:
            print(sMsg)
        self.oGeo = bpaTools.readJsonFile(fileSrc)
        return

    def writeKmlFile(self, fileDst:str, bExpand=0) -> None:
        self.oKml.write(fileDst, bExpand=bExpand)
        sMsg = "Write file - " + fileDst
        if self.oLog:
            self.oLog.info(sMsg, outConsole=False)
        else:
            print(sMsg)
        return

    def __createKmlRoot(self):
        self.oKml = bpaTools.Xml()
        sXmlns = "http://www.opengis.net/kml/2.2"
        oRoot = self.oKml.createRoot("kml", sXmlns=sXmlns)
        self.oKml.addAttrib(oRoot, "xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        self.oKml.addAttrib(oRoot, "xsi:schemaLocation", sXmlns + " http://schemas.opengis.net/kml/2.2.0/ogckml22.xsd")
        return oRoot

    def createKmlDocument(self, sName:str, sDesc:str=None):
        oRoot = self.__createKmlRoot()  #New Xml document
        oDoc = self.oKml.addTag(oRoot, "Document")
        self.oKml.addTag(oDoc, "name", sValue=sName)
        self.oKml.addTag(oDoc, "open", sValue="1")
        if sDesc:
            self.oKml.addTag(oDoc, "description", sValue=sDesc)
        self.oKmlDoc = oDoc
        return oDoc

    def createKmlStyle(self, oDoc, sStyle:str, sColorLine:str, sColorPloy:str) -> None:
        oTag0 = self.oKml.addTag(oDoc, "Style", sId=sStyle)
        oTag1 = self.oKml.addTag(oTag0, "LineStyle")
        self.oKml.addTag(oTag1, "color", sValue=sColorLine)
        self.oKml.addTag(oTag1, "width", sValue="1")
        oTag1 = self.oKml.addTag(oTag0, "PolyStyle")
        self.oKml.addTag(oTag1, "color", sValue=sColorPloy)
        return

    def createKmlFolder(self, oDoc, sNameFolder:str, sName:str, sVisibility:str, sDescription:str=""):
        oFolder = self.oKml.addTag(oDoc, sNameFolder)
        if sName:
            self.oKml.addTag(oFolder, "name", sValue=sName)
        if sVisibility:
            self.oKml.addTag(oFolder, "visibility", sValue=sVisibility)
        if sDescription:
            self.oKml.addTag(oFolder, "description", sValue=sDescription)
        return oFolder

    #sAltitudeMode:str="absolute" [altitudeModeEnum: clampToGround, relativeToGround, absolute, substitute gx:altitudeMode: clampToSeaFloor, relativeToSeaFloor}
    #sExtrude : Boolean value (0,1) specifies whether to connect the LinearRing to the ground
    def createKmlPolygon(self, oDoc, sExtrude:str="0", sAltitudeMode:str="relativeToGround"):
        oFolder0 = self.oKml.addTag(oDoc, "Polygon")
        self.oKml.addTag(oFolder0, "extrude", sValue=sExtrude)
        self.oKml.addTag(oFolder0, "altitudeMode", sValue=sAltitudeMode)
        oFolder1 = self.oKml.addTag(oFolder0, "outerBoundaryIs")
        oFolder2 = self.oKml.addTag(oFolder1, "LinearRing")
        oCoords = self.oKml.addTag(oFolder2, "coordinates")
        return oCoords

    def makeAirspacesKml(self) -> None:
        sTitle = "Analyse airspaces"
        if self.oLog:
            self.oLog.info(sTitle, outConsole=False)

        #Interprétation du contenu source
        if poaffCst.cstGeoFeatures in self.oGeo:
            oFeatures:dict = self.oGeo[poaffCst.cstGeoFeatures]
            barre = bpaTools.ProgressBar(len(oFeatures), 20, title=sTitle)
            idx = 0
            for oAs in oFeatures:
                idx+=1
                oAsPro = oAs[poaffCst.cstGeoProperties]              #get properties
                oAsGeo = oAs[poaffCst.cstGeoGeometry]                #get geometry

                #Classification pour organisation des zones
                if (oAsPro.get("vfrZoneExt",None)==True) and (oAsPro.get("vfrZone",None) ==False):
                    sTypeZone:str = "vfrZoneExt"
                elif oAsPro.get("vfrZone",None)==True:
                    sTypeZone:str = "vfrZone"
                elif oAsPro.get("vfrZone",None)==False:
                    sTypeZone:str = "ifrZone"
                else:
                    sTypeZone:str = "Airspace"

                sClassZone:str = oAsPro.get("class","")
                sNameZone:str = "[" + sClassZone + "] " + oAsPro.get("nameV","")
                sUpperM:str = oAsPro.get("upperM", 9999)
                sLowerM:str = oAsPro.get("lowerM", 0)
                sDesc:str = ""

                if "lowerMin" in oAsPro:
                    sDesc += oAsPro["lowerMin"] + "|"
                sDesc += oAsPro.get("lower","SFC") + " / " + oAsPro.get("upper","FL999")
                if "upperMax" in oAsPro:
                    sDesc += "|" + oAsPro["upperMax"]
                sDesc += " ({0}m / {1}m)".format(sLowerM , sUpperM)

                if "desc" in oAsPro:
                    sDesc += "<br/><br/>" + oAsPro["desc"]
                oTypeZone:dict = self.oKmlTmp.get(sTypeZone, {})
                oClassZone:list = oTypeZone.get(sClassZone, [])

                if oAsGeo[poaffCst.cstGeoType].lower()==(poaffCst.cstGeoPoint).lower():
                    oCoords:list = []                                       #Don't show this point feature
                elif oAsGeo[poaffCst.cstGeoType].lower()==(poaffCst.cstGeoLine).lower():
                    oCoords:list = oAsGeo[poaffCst.cstGeoCoordinates]        #get coordinates of geometry
                elif oAsGeo[poaffCst.cstGeoType].lower()==(poaffCst.cstGeoPolygon).lower():
                    oCoords:list = oAsGeo[poaffCst.cstGeoCoordinates][0]     #get coordinates of geometry

                #Stockage organisationnel temporaire
                #Nota. Exclure la LTA France dont le tracé 3D n'est pas très-bon
                if (len(oCoords)>1) and (sNameZone.find("LTA FRANCE 1")<0):
                    oZone:list = [sNameZone, sDesc, sUpperM, sLowerM, oCoords]
                    oClassZone.append(oZone)
                    oTypeZone.update({sClassZone:oClassZone})
                    self.oKmlTmp.update({sTypeZone:oTypeZone})

                barre.update(idx)
            barre.reset()

            #Construction de l'organisation des polygons dans le KML
            if len(self.oKmlTmp)>0:
                sTitle = "KML generator"
                if self.oLog:
                    self.oLog.info(sTitle, outConsole=False)

                self.createKmlStyle(self.oKmlDoc, "transRedPoly",    "ff1400FF", "7f0000ff")
                self.createKmlStyle(self.oKmlDoc, "transPurplePoly", "ff1400FF", "7fff00ff")
                self.createKmlStyle(self.oKmlDoc, "transBluePoly",   "ff1400FF", "7fff0000")
                self.createKmlStyle(self.oKmlDoc, "transGreenPoly",  "ffff0000", "4f00ff00")
                self.createKmlStyle(self.oKmlDoc, "transYellowPoly", "ff000000", "4f00ffff")

                barre = bpaTools.ProgressBar(len(oFeatures), 20, title=sTitle)
                idx = 0
                for sKeyType, oTypeZone in self.oKmlTmp.items():

                    sVisiblility:str="0" #defailt value
                    if sKeyType == "vfrZone":
                        sVisiblility:str="1"
                        oFolderType = self.createKmlFolder(self.oKmlDoc, "Folder", "Couche VFR", sVisiblility, "Couche de l'espace aérien VFR ; dont le plancher s'étand depuis la surface de la terre (SFC/AGL) jusqu'à l'altitude limite de la surface 'S' (FL115)")
                    elif sKeyType == "vfrZoneExt":
                        oFolderType = self.createKmlFolder(self.oKmlDoc, "Folder", "Couche VFR-Ext", sVisiblility, "Couche de l'espace aérien VFR étandue ; zones dont le plafond s'élève jusqu'à la limite maximum de FL175")
                    elif sKeyType == "ifrZone":
                        oFolderType = self.createKmlFolder(self.oKmlDoc, "Folder", "Couche IFR", sVisiblility, "Couche de l'espace aérien IFR ; zones hautes (UTA=UpperControlArea, OCA=OceanicControlArea, OTA=OceanicTransitionArea, ...) et autres espaces-aériens nécessaires aux transmissions radards ou radios (FIR=FlightInformationRegion, UIR=UpperFlightInformationRegion, SECTOR=ControlSector, ...")

                    for sKeyClass, oClassZone in oTypeZone.items():
                        oFolderClass = self.createKmlFolder(oFolderType, "Folder", "Classe " + sKeyClass, sVisiblility)

                        if  sKeyClass in ["A","B","C","P","TMZ"]:
                            sStyle = "#transRedPoly"
                        elif sKeyClass in ["D"]:
                            sStyle = "#transPurplePoly"
                        elif sKeyClass in ["R","RTBA","RMZ"]:
                            sStyle = "#transBluePoly"
                        elif sKeyClass in ["E"]:
                            sStyle = "#transGreenPoly"
                        else:
                            #print(sKeyClass)
                            sStyle = "#transYellowPoly"

                        for oZone in oClassZone:
                            idx+=1
                            sZoneName:str = oZone[0]
                            sDesc:str = oZone[1]
                            sUpperM:str = oZone[2]
                            sLowerM:str = oZone[3]
                            oCoords:list = oZone[4]

                            oPlacemark = self.createKmlFolder(oFolderClass, "Placemark", sZoneName, sVisibility=sVisiblility, sDescription=sDesc)
                            self.oKml.addTag(oPlacemark, "styleUrl", sValue=sStyle)
                            oMultiGeo = self.oKml.addTag(oPlacemark, "MultiGeometry")

                            #Construct top panel
                            oPolygon:list = []
                            for oAs in oCoords:
                                sPoint:str = str(oAs[0]) + "," + str(oAs[1]) + ","
                                oPolygon.append(sPoint + str(sUpperM))

                            if sLowerM==0:     #Le plancher est plaqué au sol
                                #add top panel
                                oKmlCoords = self.createKmlPolygon(oMultiGeo, sExtrude="1")
                                oKmlCoords.text = " ".join(oPolygon)
                            else:
                                #add top panel
                                oKmlCoords = self.createKmlPolygon(oMultiGeo, sExtrude="0")
                                oKmlCoords.text = " ".join(oPolygon)

                                #Construct bottom panel
                                oPolygon:list = []
                                for oAs in oCoords:
                                    sPoint:str = str(oAs[0]) + "," + str(oAs[1]) + ","
                                    oPolygon.append(sPoint + str(sLowerM))
                                #add bottom panel
                                oKmlCoords = self.createKmlPolygon(oMultiGeo, sExtrude="0")
                                oKmlCoords.text = " ".join(oPolygon)

                                #Construct sides panels
                                for idx, oAs in enumerate(oCoords):
                                    sPoint0:str = str(oCoords[idx][0]) + "," + str(oCoords[idx][1]) + ","
                                    if idx+1 == len(oCoords):
                                        sPoint1:str = str(oCoords[0][0]) + "," + str(oCoords[0][1]) + ","
                                    else:
                                        sPoint1:str = str(oCoords[idx+1][0]) + "," + str(oCoords[idx+1][1]) + ","

                                    oPolygon:list = []
                                    oPolygon.append(sPoint0 + str(sLowerM))
                                    oPolygon.append(sPoint0 + str(sUpperM))
                                    oPolygon.append(sPoint1 + str(sUpperM))
                                    oPolygon.append(sPoint1 + str(sLowerM))
                                    oPolygon.append(sPoint0 + str(sLowerM))

                                    #Side panel
                                    oKmlCoords = self.createKmlPolygon(oMultiGeo, sExtrude="0")
                                    oKmlCoords.text = " ".join(oPolygon)

                        barre.update(idx)
                barre.reset()
        return


if __name__ == '__main__':
    sPath = "../output/Tests/"
    oKml = Geojson2Kml()
    oKml.readGeojsonFile(sPath + "__testAirspaces.geojson")
    oKml.createKmlDocument("Paragliding Openair Frensh Files", "Cartographies aériennes France - http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/")
    oKml.makeAirspacesKml()
    oKml.writeKmlFile(sPath + "__testAirspaces.kml", bExpand=1)

    """
    oKml.readGeojsonFile(sPath + "__testAirspaces-freeflight.geojson")
    oKml.makeKml()
    oKml.writeKmlFile(sPath + "__testAirspaces-freeflight.kml", bExpand=0)

    oKml.readGeojsonFile(sPath + "___truncateFile3.geojson")
    oKml.makeKml()
    oKml.writeKmlFile(sPath + "__truncateAirspaces-freeflight.kml", bExpand=0)
    """
