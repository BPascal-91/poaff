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
        if not self.oGeo:
            sMsg:str = " file {0} - Empty source geometry".format(fileDst)
            self.oLog.warning("Unwritten" + sMsg, outConsole=False)
            bpaTools.deleteFile(fileDst)
            return

        self.oKml.write(fileDst, bExpand=bExpand)
        sMsg:str = "Write file - " + fileDst
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

    def createKmlStyle(self, oDoc, sStyle:str, sColorLine:str, sColorPoly:str) -> None:
        oTag0 = self.oKml.addTag(oDoc, "Style", sId=sStyle)
        oTag1 = self.oKml.addTag(oTag0, "LineStyle")
        self.oKml.addTag(oTag1, "color", sValue=sColorLine)
        self.oKml.addTag(oTag1, "width", sValue="1")
        oTag1 = self.oKml.addTag(oTag0, "PolyStyle")
        self.oKml.addTag(oTag1, "color", sValue=sColorPoly)
        return

    def createKmlFolder(self, oDoc, sNameFolder:str, sName:str, sVisibility:str, sDescription:str=""):
        oFolder = self.oKml.addTag(oDoc, sNameFolder)
        if sName:
            self.oKml.addTag(oFolder, "name", sValue=sName)
        if sVisibility:
            self.oKml.addTag(oFolder, "visibility", sValue=sVisibility)
        if sDescription:
            sDesc:str = self.oKml.letCDATA(sDescription)
            self.oKml.addTag(oFolder, "description", sValue=sDesc)
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
        #if self.oLog:
        #    self.oLog.info(sTitle, outConsole=False)

        #Interprétation du contenu source
        if poaffCst.cstGeoFeatures in self.oGeo:
            oFeatures:dict = self.oGeo[poaffCst.cstGeoFeatures]
            barre = bpaTools.ProgressBar(len(oFeatures), 20, title=sTitle)
            idx = 0
            for oAs in oFeatures:
                idx+=1
                oAsPro = oAs[poaffCst.cstGeoProperties]              #get properties
                oAsGeo = oAs[poaffCst.cstGeoGeometry]                #get geometry

                sClassZone:str = oAsPro.get("class","")
                sTypezZone:str = oAsPro.get("type","")
                if "name" in oAsPro:
                    sNameZone:str = "[" + sClassZone + "] " + oAsPro.get("name","")
                else:
                    sNameZone:str = "[" + sClassZone + "] " + oAsPro.get("nameV","")
                sDeclassifiable:str = oAsPro.get("declassifiable","")
                sOrdUpperM:str = oAsPro.get("ordinalUpperM", None)      #Ordinal AGL value
                sOrdLowerM:str = oAsPro.get("ordinalLowerM", None)      #Ordinal AGL value
                sUpperM:str = oAsPro.get("upperM", 9999)
                sLowerM:str = oAsPro.get("lowerM", 0)

                sDesc:str = self.makeAirspaceHtmlDesc(sName             = sNameZone,
                                                      sClass            = sClassZone,
                                                      sType             = sTypezZone,
                                                      sCodeActivity     = oAsPro.get("codeActivity",""),
                                                      bDeclassifiable   = sDeclassifiable,
                                                      sLower            = oAsPro.get("lower","SFC"),
                                                      sUpper            = oAsPro.get("upper","FL999"),
                                                      sLowerMin         = oAsPro.get("lowerMin",""),
                                                      sUpperMax         = oAsPro.get("upperMax",""),
                                                      sLowerM           = sLowerM,
                                                      sUpperM           = sUpperM,
                                                      sDescription      = oAsPro.get("desc",""),
                                                      sActivationDesc   = oAsPro.get("activationDesc",""),
                                                      sTimeScheduling   = oAsPro.get("timeScheduling",""),
                                                      sMhz              = oAsPro.get("Mhz","") )

                #Classification pour organisation des zones
                if "freeFlightZone" in oAsPro:
                    if   (oAsPro.get("freeFlightZoneExt",None)==True) and (oAsPro.get("freeFlightZone",None)==False):
                        sTypeZone:str = "vfrZoneExt"
                    elif (oAsPro.get("vfrZoneExt",None)==True) and (oAsPro.get("vfrZone",None)==False):
                        sTypeZone:str = "vfrZoneExt"
                    elif oAsPro.get("vfrZone",None)==True:
                        sTypeZone:str = "vfrZone"
                    elif oAsPro.get("vfrZone",None)==False:
                        sTypeZone:str = "ifrZone"
                elif "lowerM" in oAsPro:
                    if   float(sLowerM) < 3500:
                        sTypeZone:str = "vfrZone"
                    elif float(sLowerM) < 5940:
                        sTypeZone:str = "vfrZoneExt"
                    else:
                        sTypeZone:str = "ifrZone"
                else:
                    sTypeZone:str = "Airspace"

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
                #if (len(oCoords)>1) and (sNameZone.find("LTA FRANCE 1")<0):
                if len(oCoords)>1:
                    oZone:list = [sNameZone, sDesc, sTypezZone, sDeclassifiable, sUpperM, sLowerM, sOrdUpperM, sOrdLowerM, oCoords]
                    oClassZone.append(oZone)
                    oTypeZone.update({sClassZone:oClassZone})
                    self.oKmlTmp.update({sTypeZone:oTypeZone})

                barre.update(idx)
            barre.reset()

            #Construction de l'organisation des polygons dans le KML
            if len(self.oKmlTmp)>0:
                sTitle = "KML generator"
                #if self.oLog:
                #    self.oLog.info(sTitle, outConsole=False)

                #https://developers.google.com/kml/documentation/kmlreference#color
                #The first two hex characters define the alpha band, or opacity.
                #   ff = completely solid
                #   7f =  50% transparency
                #   4f = ~20% transparency
                #   1f = ~10% transparency
                #   00 = completely translucent
                ## Couleurs de bases
                #   Rouge - ff0000ff
                #   Jaune - ff00ffff
                #   Bleu - ffff0000
                #   Vert - ff00ff00
                #   Violet - FF800080
                #   Orange - FF0080FF
                #   Marron - FF336699
                #   Rose - ffff00ff
                self.createKmlStyle(self.oKmlDoc, "fillRedPoly",        "ff0000ff", "6f0000ff")
                self.createKmlStyle(self.oKmlDoc, "transRedPoly",       "ff0000ff", "3f0000ff")
                self.createKmlStyle(self.oKmlDoc, "noFillRedPoly",      "ff0000ff", "1f0000ff")
                self.createKmlStyle(self.oKmlDoc, "fillRedPurplePoly",  "ff0000ff", "6f800080")
                self.createKmlStyle(self.oKmlDoc, "transRedPurplePoly", "ff0000ff", "3f800080")
                self.createKmlStyle(self.oKmlDoc, "fillPurplePoly",     "ff800080", "6F800080")
                self.createKmlStyle(self.oKmlDoc, "transPurplePoly",    "ff800080", "3F800080")
                self.createKmlStyle(self.oKmlDoc, "noFillPurplePoly",   "ff800080", "1f800080")
                self.createKmlStyle(self.oKmlDoc, "fillOrangePoly",     "ff0080ff", "6f0080ff")
                self.createKmlStyle(self.oKmlDoc, "transOrangePoly",    "ff0080ff", "3f0080ff")
                self.createKmlStyle(self.oKmlDoc, "noFillOrangePoly",   "ff0080ff", "1f0080ff")
                self.createKmlStyle(self.oKmlDoc, "fillBrownPoly",      "ff004b9c", "6f004b9c")
                self.createKmlStyle(self.oKmlDoc, "transBrownPoly",     "ff004b9c", "3f004b9c")
                #self.createKmlStyle(self.oKmlDoc, "fillBluePoly",       "ffff0000", "6fff0000")
                self.createKmlStyle(self.oKmlDoc, "transBluePoly",      "ffff0000", "3fff0000")
                self.createKmlStyle(self.oKmlDoc, "noFillBluePoly",     "ffff0000", "1fff0000")
                self.createKmlStyle(self.oKmlDoc, "transGreenPoly",     "ff00ff00", "3f00ff00")
                self.createKmlStyle(self.oKmlDoc, "noFillGreenPoly",    "ff00ff00", "1f00ff00")
                self.createKmlStyle(self.oKmlDoc, "transYellowPoly",    "ff00ffff", "6f00ffff")
                #self.createKmlStyle(self.oKmlDoc, "noFillYellowPoly","ff00ffff", "1f00ffff")

                barre = bpaTools.ProgressBar(len(oFeatures), 20, title=sTitle)
                idx = 0
                for sKeyType, oTypeZone in self.oKmlTmp.items():

                    sVisiblility:str="0" #default value
                    if sKeyType == "vfrZone":
                        sVisiblility:str="1"
                        oFolderType = self.createKmlFolder(self.oKmlDoc, "Folder", "Couche VFR", sVisiblility, "Couche de l'espace aérien VFR ; dont le plancher s'étand depuis la surface de la terre (SFC/AGL) jusqu'à l'altitude limite de la surface 'S' (FL115)")
                    elif sKeyType == "vfrZoneExt":
                        oFolderType = self.createKmlFolder(self.oKmlDoc, "Folder", "Couche VFR-Ext", sVisiblility, "Couche de l'espace aérien VFR étandue ; zones dont le plafond s'élève jusqu'à la limite maximum de FL195")
                    elif sKeyType == "ifrZone":
                        oFolderType = self.createKmlFolder(self.oKmlDoc, "Folder", "Couche IFR", sVisiblility, "Couche de l'espace aérien IFR ; zones hautes (UTA=UpperControlArea, OCA=OceanicControlArea, OTA=OceanicTransitionArea, ...) et autres espaces-aériens nécessaires aux transmissions radards ou radios (FIR=FlightInformationRegion, UIR=UpperFlightInformationRegion, SECTOR=ControlSector, ...")

                    for sKeyClass, oClassZone in oTypeZone.items():
                        oFolderClass = self.createKmlFolder(oFolderType, "Folder", "Classe " + sKeyClass, sVisiblility)

                        for oZone in oClassZone:
                            idx+=1
                            sZoneName:str       = oZone[0]
                            sDesc:str           = oZone[1]
                            sTypezZone:str      = oZone[2]
                            sDeclassifiable:str = oZone[3]
                            sUpperM:str         = oZone[4]
                            sLowerM:str         = oZone[5]
                            sOrdUpperM:str      = oZone[6]          #Ordinal AGL value
                            sOrdLowerM:str      = oZone[7]          #Ordinal AGL value
                            oCoords:list        = oZone[8]

                            #Red and fill
                            if  sKeyClass in ["P","ZIT"]:
                                sStyle = "#fillRedPoly"
                            #Red and fill
                            elif  sKeyClass in ["A","B","C","CTR","CTR-P","TMA","TMA-P","TMZ","RMZ/TMZ","TMZ/RMZ"]:
                                if sLowerM==0:
                                    sStyle = "#fillRedPoly"
                                else:
                                    sStyle = "#transRedPoly"
                            #Red and No-Fill
                            elif sKeyClass in ["CTA","CTA-P","FIR","FIR-P","NO-FIR","PART","CLASS","SECTOR","SECTOR-C","OCA","OCA-P","OTA","OTA-P","UTA","UTA-P","UIR","UIR-P","TSA","CBA","RCA","RAS","TRA","AMA","ASR","ADIZ","POLITICAL","OTHER","AWY"]:
                                sStyle = "#noFillRedPoly"
                            #Purple and No-fill
                            elif sKeyClass=="D" and sTypezZone=="LTA":
                                sStyle = "#noFillPurplePoly"
                            #Red and fill
                            elif sKeyClass in ["D","D-AMC"] and not bool(sDeclassifiable):
                                if sLowerM==0:
                                    sStyle = "#fillRedPoly"
                                else:
                                    sStyle = "#transRedPoly"
                            #Purple and fill
                            elif sKeyClass in ["D","D-AMC"] and bool(sDeclassifiable):
                                if sLowerM==0:
                                    sStyle = "#fillRedPurplePoly"
                                else:
                                    sStyle = "#transRedPurplePoly"
                            #Purple and fill
                            elif sKeyClass in ["R","R-AMC"] and sTypezZone!="RTBA":
                                if sLowerM==0:
                                    sStyle = "#fillPurplePoly"
                                else:
                                    sStyle = "#transPurplePoly"
                            #Brown and fill
                            elif sKeyClass in ["R","R-AMC"] and sTypezZone=="RTBA":
                                if sLowerM==0:
                                    sStyle = "#fillBrownPoly"
                                else:
                                    sStyle = "#transBrownPoly"
                            #Orange
                            elif sKeyClass in ["GP","Q","VV","VL","BA","PA"]:       #Danger; Vol à voile; Vol libre; Ballon; Parachutisme
                                sStyle = "#noFillOrangePoly"
                            #Orange and No-Fill
                            elif sKeyClass in ["RMZ","W"]:
                                if sLowerM==0:
                                    sStyle = "#fillOrangePoly"
                                else:
                                    sStyle = "#transOrangePoly"
                            #Blue
                            elif sKeyClass in ["ZSM","BIRD","PROTECT","D-OTHER","SUR","AER","TRPLA","TRVL","VOL","REFUEL"]:
                                if sLowerM==0:
                                    sStyle = "#transBluePoly"
                                else:
                                    sStyle = "#noFillBluePoly"
                            #Green
                            elif sKeyClass in ["E","F","G","SIV","FIS","FFVL","FFVP"]:
                                if sLowerM==0:
                                    sStyle = "#transGreenPoly"
                                else:
                                    sStyle = "#noFillGreenPoly"
                            #Yellow
                            else:
                                sStyle = "#transYellowPoly"
                                if self.oLog:
                                    self.oLog.warning("KML Color not found for Class={0}".format(sKeyClass), outConsole=False)

                            oPlacemark = self.createKmlFolder(oFolderClass, "Placemark", sZoneName, sVisibility=sVisiblility, sDescription=sDesc)
                            self.oKml.addTag(oPlacemark, "styleUrl", sValue=sStyle)
                            oMultiGeo = self.oKml.addTag(oPlacemark, "MultiGeometry")

                            oPolygon:list = []
                            sAltitudeMode:str = "absolute"
                            if sLowerM==0:     #Le plancher est plaqué au sol
                                #Define the context
                                sFinalUpper:str = sUpperM           #Standard AMSL value
                                if sOrdUpperM:                      #Ordinal AGL value
                                    sFinalUpper = sOrdUpperM
                                    sAltitudeMode:str = "relativeToGround"
                                #Construct top panel
                                for oAs in oCoords:
                                    sPoint:str = str(oAs[0]) + "," + str(oAs[1]) + ","
                                    oPolygon.append(sPoint + str(sFinalUpper))
                                #add top panel
                                oKmlCoords = self.createKmlPolygon(oMultiGeo, sExtrude="1", sAltitudeMode=sAltitudeMode)
                                oKmlCoords.text = " ".join(oPolygon)
                            else:
                                #Construct top panel
                                for oAs in oCoords:
                                    sPoint:str = str(oAs[0]) + "," + str(oAs[1]) + ","
                                    oPolygon.append(sPoint + str(sUpperM))
                                #add top panel
                                oKmlCoords = self.createKmlPolygon(oMultiGeo, sExtrude="0", sAltitudeMode=sAltitudeMode)
                                oKmlCoords.text = " ".join(oPolygon)

                                #Construct bottom panel
                                oPolygon:list = []
                                for oAs in oCoords:
                                    sPoint:str = str(oAs[0]) + "," + str(oAs[1]) + ","
                                    oPolygon.append(sPoint + str(sLowerM))
                                #add bottom panel
                                oKmlCoords = self.createKmlPolygon(oMultiGeo, sExtrude="0", sAltitudeMode=sAltitudeMode)
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
                                    oKmlCoords = self.createKmlPolygon(oMultiGeo, sExtrude="0", sAltitudeMode=sAltitudeMode)
                                    oKmlCoords.text = " ".join(oPolygon)

                        barre.update(idx)
                barre.reset()
        return

    #Contruction dynamique du tableau de présentation
    def makeAirspaceHtmlDesc(self, sName:str, sClass:str, sType:str="", sCodeActivity:str="", bDeclassifiable:bool=False, sLower:str="", sUpper:str="", sLowerMin:str="", sUpperMax:str="", sLowerM:str="", sUpperM:str="", sDescription:str="", sActivationDesc:str="", sTimeScheduling:str="", sMhz:str="") -> None:
        cstTable:str                = '<table border="1" cellpadding="2" cellspacing="0" style="text-align:center;">{0}</table>'
        cstTableHead:str            = '<th>{0}</th>'
        cstTableRow:str             = '<tr>{0}</tr>'
        cstTableColRawspan:str      = '<td rowspan="{0}">{1}</td>'
        cstTableCol:str             = '<td>{0}</td>'
        cstTextBold:str             = '<b>{0}</b>'
        #cstTextItalic:str           = '<i>{0}</i>'
        #cstTextUnderlined:str       = '<u>{0}</u>'
        #cstSpanCentert:str          = '<span style="text-align:center; display:block;">{0}</span>'

        """ Ouput sample :
          <table border="1" cellpadding="2" cellspacing="0" style="text-align: center;">
    		<tr>
    		  <th>Class</th>
    		  <th>Type</th>
    		  <th>Lower / Upper</th>
    		</tr>
            <tr>
    		  <td rowspan="2"><font size=6><b>A</b></font></td>
              <td rowspan="2"><b>CTR</b></td>
    		  <td>2500F MSL</td>
    		</tr>
            <tr>
    		  <td>2000F MSL</td>
    		</tr>
          </table>
          <br/><b>Description</b>: Tyty et toto sont sur un bateau...
          <br/><b>Activity</b>: Autorisation de vol donnée par la tour de contrôle...
        """

        sHtmlDesc:str  = ""
        sContent:str    = ""

        sRow:str        = cstTableHead.format("Class")
        if sClass!=sType:
            sRow       += cstTableHead.format("Type")
        if sCodeActivity:
            sRow       += cstTableHead.format("Activity")
        sRow           += cstTableHead.format("Upp / Low")
        if sLowerMin or sUpperMax:
            sRow       += cstTableHead.format("Max / Min")
        if sLowerM!="" or sUpperM!="":
            sRow       += cstTableHead.format("<i>in meter</i>")
        sContent       += cstTableRow.format(sRow)

        if not bDeclassifiable:
            sStyle:str = 'style="background-color:black; color:white;"'
        else:
            sStyle:str = ""
        sRow:str        = cstTableColRawspan.format(2, '<font size=6 ' + sStyle + '>' + cstTextBold.format(sClass) + '</font>')
        if sClass!=sType:
            sRow       += cstTableColRawspan.format(2, cstTextBold.format(sType))
        if sCodeActivity:
            sRow       += cstTableColRawspan.format(2, cstTextBold.format(sCodeActivity))
        sRow           += cstTableCol.format(sUpper)
        if sLowerMin or sUpperMax:
            sRow       += cstTableCol.format(sUpperMax)
        sRow           += cstTableCol.format(str(sUpperM) + (" m" if sUpperM!="" else ""))
        sContent       += cstTableRow.format(sRow)

        sRow:str        = cstTableCol.format(sLower)
        if sLowerMin or sUpperMax:
            sRow       += cstTableCol.format(sLowerMin)
        sRow           += cstTableCol.format(str(sLowerM) + (" m" if sLowerM!="" else ""))
        sContent       += cstTableRow.format(sRow)

        sHtmlDesc = cstTable.format(sContent)
        if sDescription:
            sHtmlDesc += "<br/>" + cstTextBold.format("Description: ") + sDescription
        if sActivationDesc:
            sHtmlDesc += "<br/><br/>" + cstTextBold.format("Activation: ") + sActivationDesc
        if sTimeScheduling:
            sHtmlDesc += "<br/><br/>" + cstTextBold.format("TimeScheduling: ") + str(sTimeScheduling)
        if sMhz:
            sHtmlDesc += "<br/><br/>" + cstTextBold.format("Frequencies: ") + str(sMhz)

        return sHtmlDesc

if __name__ == '__main__':
    sPath:str    = "../output/Tests/map/"
    sSrcFile:str = "20210127_BPa_FR-ZSM_Protection-des-rapaces.geojson"   #20210201_airspaces-freeflight-geoFrenchAlps.geojson - 20210123_BPa_FR-ZSM_Protection-des-rapaces.geojson - 20210111_airspaces-freeflight-gpsWithTopo-geoFrenchAll.geojson
    oKml = Geojson2Kml()
    oKml.readGeojsonFile(sPath + sSrcFile)
    sTilte:str = "Paragliding Openair Frensh Files"
    sDesc:str  = "Created at: " + bpaTools.getNowISO() + "<br/>http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/"
    oKml.createKmlDocument(sTilte, sDesc)
    oKml.makeAirspacesKml()
    oKml.writeKmlFile(sPath + sSrcFile.replace(".geojson", ".kml"), bExpand=1)

    """
    oKml.readGeojsonFile(sPath + "__testAirspaces-freeflight.geojson")
    oKml.makeKml()
    oKml.writeKmlFile(sPath + "__testAirspaces-freeflight.kml", bExpand=0)

    oKml.readGeojsonFile(sPath + "___truncateFile3.geojson")
    oKml.makeKml()
    oKml.writeKmlFile(sPath + "__truncateAirspaces-freeflight.kml", bExpand=0)
    """
