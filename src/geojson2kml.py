#!/usr/bin/env python3

from rdp import rdp

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
            if self.oLog:
                self.oLog.info("Unwritten" + sMsg, outConsole=False)
            else:
                print(sMsg)
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

    #Use epsilonReduce for compress shape in KML file   (Nota. epsilonReduce=-1 for no compression, =0 supress-doublon; samples: 0.0001 or 0.0005)
    def makeAirspacesKml(self, epsilonReduce:float=-1) -> None:
        sTitle = "KML analyse"
        #if self.oLog:
        #    self.oLog.info("makeAirspacesKml() " + sTitle, outConsole=False)

        #Interprétation du contenu source
        if poaffCst.cstGeoFeatures in self.oGeo:
            oFeatures:dict = self.oGeo[poaffCst.cstGeoFeatures]
            barre = bpaTools.ProgressBar(len(oFeatures), 20, title=sTitle)
            idx = 0
            for oAs in oFeatures:
                idx+=1
                oAsPro = oAs[poaffCst.cstGeoProperties]              #get properties
                oAsGeo = oAs[poaffCst.cstGeoGeometry]                #get geometry

                sClassZone:str = oAsPro.get("class", oAsPro.get("category","?class"))
                sTypezZone:str = oAsPro.get("type","")
                sTmpName:str = oAsPro.get("name", oAsPro.get("nameV", "?name"))
                sNameZone:str = "[" + sClassZone + "] " + sTmpName
                sDeclassifiable:str = oAsPro.get("declassifiable","")
                sOrdUpperM:str = oAsPro.get("ordinalUpperM", None)      #Ordinal AGL value
                sOrdLowerM:str = oAsPro.get("ordinalLowerM", None)      #Ordinal AGL value
                sUpperM:str = oAsPro.get("upperM", oAsPro.get("top_m", 9999))
                sLowerM:str = oAsPro.get("lowerM", oAsPro.get("bottom_m", 0))
                sMinGroundHeight:str = 0
                sMaxGroundHeight:str = 0
                aGroundEH:list = oAsPro.get("groundEstimatedHeight", None)
                if aGroundEH:
                    sMinGroundHeight = aGroundEH[0]
                    sMaxGroundHeight = aGroundEH[3]

                sDesc:str = self.makeAirspaceHtmlDesc(sName             = sNameZone,
                                                      sClass            = sClassZone,
                                                      sType             = sTypezZone,
                                                      sCodeActivity     = oAsPro.get("codeActivity",""),
                                                      bDeclassifiable   = sDeclassifiable,
                                                      sLower            = oAsPro.get("lower",oAsPro.get("bottom","SFC")),
                                                      sUpper            = oAsPro.get("upper",oAsPro.get("top"   ,"FL999")),
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
                        sTypeZone:str = "LTA"       #LTA=Lower Traffic Area
                    elif (oAsPro.get("vfrZoneExt",None)==True) and (oAsPro.get("vfrZone",None)==False):
                        sTypeZone:str = "LTA"
                    elif oAsPro.get("vfrZone",None)==True:
                        sTypeZone:str = "LTA"       #LTA=Lower Traffic Area
                    elif oAsPro.get("vfrZone",None)==False:
                        sTypeZone:str = "UTA"       #UTA=Upper Traffic Area
                elif "lowerM" in oAsPro:
                    if   float(sLowerM) < 3500:
                        sTypeZone:str = "vfrZone"
                    elif float(sLowerM) < 5940:
                        sTypeZone:str = "LTA"       #LTA=Lower Traffic Area
                    else:
                        sTypeZone:str = "UTA"       #UTA=Upper Traffic Area
                else:
                    sTypeZone:str = "Airspace"

                #Répartition du VFR en deux blocs : "vfrZone" et "vfrZoneComp"
                if sTypeZone == "vfrZone" and sClassZone in ["E","G","G","Q"]:
                    sTypeZone = "vfrZoneComp"

                oTypeZone:dict = self.oKmlTmp.get(sTypeZone, {})
                oClassZone:list = oTypeZone.get(sClassZone, [])

                if oAsGeo[poaffCst.cstGeoType].lower()==(poaffCst.cstGeoPoint).lower():
                    oCoords:list = []                                       #Don't show this point feature
                elif oAsGeo[poaffCst.cstGeoType].lower()==(poaffCst.cstGeoLine).lower():
                    oCoords:list = oAsGeo[poaffCst.cstGeoCoordinates]        #get coordinates of geometry
                elif oAsGeo[poaffCst.cstGeoType].lower()==(poaffCst.cstGeoPolygon).lower():
                    oCoords:list = oAsGeo[poaffCst.cstGeoCoordinates][0]     #get coordinates of geometry

                if len(oCoords)>1:
                    #Optimisation du tracé
                    if epsilonReduce==0 or (epsilonReduce>0 and len(oCoords)>40):   #Ne pas optimiser le tracé des zones ayant moins de 40 segments (préservation des tracés de cercle minimaliste)
                        oCoordsDst:list = rdp(oCoords, epsilon=epsilonReduce)       #Optimisation du tracé des coordonnées
                        iOrgSize:int = len(oCoords)
                        iNewSize:int = len(oCoordsDst)
                        if iNewSize>0 and iNewSize!=iOrgSize:
                            percent:float = round((1-(iNewSize/iOrgSize))*100,1)
                            percent = int(percent) if percent>=1.0 else percent
                            sOpti:str = "Segments optimisés à {0}% ({1}->{2}) [rdp={3}] ***".format(percent, iOrgSize, iNewSize, epsilonReduce)
                            self.oLog.debug("Kml RDP Optimisation: {0} - {1}".format(sNameZone, sOpti), level=2, outConsole=False)
                    else:
                        oCoordsDst:list = oCoords

                    #Stockage organisationnel temporaire
                    oZone:list = [sNameZone, sDesc, sTypezZone, sDeclassifiable, sUpperM, sLowerM, sOrdUpperM, sOrdLowerM, sMinGroundHeight, sMaxGroundHeight, oCoordsDst]
                    oClassZone.append(oZone)
                    oTypeZone.update({sClassZone:oClassZone})
                    self.oKmlTmp.update({sTypeZone:oTypeZone})

                barre.update(idx)
            barre.reset()

            #Construction de l'organisation des polygons dans le KML
            if len(self.oKmlTmp)>0:

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

                #Construction du KML avec ordonancement des dossiers
                aTypeList = ["UTA","LTA","vfrZoneComp","vfrZone","Airspace"]
                for sKeyType in aTypeList:
                    oTypeZone = self.oKmlTmp.get(sKeyType, None)
                    self.makeFolder(sKeyType, oTypeZone)
        return

    #Contruction du dossier interne KML
    def makeFolder(self, sKeyType, oTypeZone) -> None:
        if oTypeZone == None:
            return

        sVisiblility:str="0" #default value
        if sKeyType == "Airspace":
            sVisiblility:str="1"
            oFolderType = self.createKmlFolder(self.oKmlDoc, "Folder", "Airspace", sVisiblility, "Espace aérien")
        elif sKeyType == "vfrZone":
            sVisiblility:str="1"
            oFolderType = self.createKmlFolder(self.oKmlDoc, "Folder", "Couche VFR", sVisiblility, "Couche de l'espace aérien VFR (Visual Flight Rule) ; dont le plancher s'étand depuis la surface de la terre (SFC/AGL) jusqu'à l'altitude limite de la surface 'S' (FL115)")
        elif sKeyType == "vfrZoneComp":
            oFolderType = self.createKmlFolder(self.oKmlDoc, "Folder", "Zones VFR complémentaires", sVisiblility, "Zones complémentaires de la couche de l'espace aérien VFR (Visual Flight Rule). Il s'agit des Classes de type E, F, G ou des zones Dangereues...")
        elif sKeyType == "LTA":             #LTA=Lower Traffic Area
            oFolderType = self.createKmlFolder(self.oKmlDoc, "Folder", "Couche LTA", sVisiblility, "Couche de l'espace aérien LTA (Lower Traffic Area) ; zones intermédiaires dont le plancher s'élève depuis le FL115 et jusqu'au plafond maximum de FL195")
        elif sKeyType == "UTA":
            oFolderType = self.createKmlFolder(self.oKmlDoc, "Folder", "Couche UTA", sVisiblility, "Couche de l'espace aérien UTA (Upper Traffic Area) ; zones hautes dont le plancher s'élève au delà du FL195")

        sTitle = "KML generator: " + sKeyType
        barre = bpaTools.ProgressBar(len(oTypeZone.items()), 20, title=sTitle)
        idxBarre = 0
        for sKeyClass, oClassZone in oTypeZone.items():
            idxBarre+=1
            if sKeyClass in ["A","B","C","D","E","F","G"]:
                sLib:str = "Classe " + sKeyClass
            else:
                sLib:str = "Zone " + sKeyClass
            oFolderClass = self.createKmlFolder(oFolderType, "Folder", sLib, sVisiblility)

            for oZone in oClassZone:

                sZoneName:str       = oZone[0]
                sDesc:str           = oZone[1]
                sTypezZone:str      = oZone[2]
                sDeclassifiable:str = oZone[3]
                sUpperM:str         = oZone[4]
                sLowerM:str         = oZone[5]
                sOrdUpperM:str      = oZone[6]          #Ordinal AGL value
                sOrdLowerM:str      = oZone[7]          #Ordinal AGL value
                sMinGroundHeight    = oZone[8]
                sMaxGroundHeight    = oZone[9]
                oCoords:list        = oZone[10]

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
                sFinalUpper:str = sUpperM           #Standard AMSL value
                if sOrdUpperM:                      #Ordinal AGL value
                    sFinalUpper = int(sMaxGroundHeight) + int(sOrdUpperM)    #New - Elevation au dessus du point géographique le plus élevé de la zone

                if sLowerM==0:     #Le plancher est plaqué au sol
                    #Construct top panel
                    for oAs in oCoords:
                        sPoint:str = str(oAs[0]) + "," + str(oAs[1]) + ","
                        oPolygon.append(sPoint + str(sFinalUpper))
                    #add top panel
                    oKmlCoords = self.createKmlPolygon(oMultiGeo, sExtrude="1", sAltitudeMode=sAltitudeMode)
                    oKmlCoords.text = " ".join(oPolygon)
                else:
                    sFinalLower:str = sLowerM           #Standard AMSL value
                    if sOrdLowerM:                      #Ordinal AGL value
                        sFinalLower = int(sMinGroundHeight) + int(sOrdLowerM)    #New - Elevation au dessus du point géographique le moins élevé de la zone

                    #Construct top panel
                    for oAs in oCoords:
                        sPoint:str = str(oAs[0]) + "," + str(oAs[1]) + ","
                        oPolygon.append(sPoint + str(sFinalUpper))
                    #add top panel
                    oKmlCoords = self.createKmlPolygon(oMultiGeo, sExtrude="0", sAltitudeMode=sAltitudeMode)
                    oKmlCoords.text = " ".join(oPolygon)

                    #Construct bottom panel
                    oPolygon:list = []
                    for oAs in oCoords:
                        sPoint:str = str(oAs[0]) + "," + str(oAs[1]) + ","
                        oPolygon.append(sPoint + str(sFinalLower))
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
                        oPolygon.append(sPoint0 + str(sFinalLower))
                        oPolygon.append(sPoint0 + str(sFinalUpper))
                        oPolygon.append(sPoint1 + str(sFinalUpper))
                        oPolygon.append(sPoint1 + str(sFinalLower))
                        oPolygon.append(sPoint0 + str(sFinalLower))

                        #Side panel
                        oKmlCoords = self.createKmlPolygon(oMultiGeo, sExtrude="0", sAltitudeMode=sAltitudeMode)
                        oKmlCoords.text = " ".join(oPolygon)

            barre.update(idxBarre)
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
    sPath:str    = "../output/_POAFF/"                          #../output/Tests/map/
    sSrcFile:str = "global@airspaces-ifr.geojson"               #global@airspaces-ifr.geojson
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
