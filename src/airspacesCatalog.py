#!/usr/bin/env python3
from copy import deepcopy

import bpaTools
import aixmReader
import poaffCst
from geoRefArea import enuAreasRef
import geoRefArea

####  Constantes de paramétrage des catalogues  ####
cstDeduplicateSeparator = "@@-"
cstKeyCatalogCatalog = "catalog"
cstKeyCatalogSoftware = "software"
cstKeyCatalogCreated = "created"
cstKeyCatalogContent = "content"

cstKeyCatalogNbAreas = "numberOfAreas"
cstKeyCatalogSrcFiles = "srcFiles"
cstKeyCatalogSrcFile = "srcFile"
cstKeyCatalogSrcOwner = "srcOwner"
cstKeyCatalogSrcOrigin = "srcOrigin"
cstKeyCatalogSrcVersion = "srcVersion"
cstKeyCatalogSrcCreated = "srcCreated"

cstKeyCatalogKeySrcFile = "keySrcFile"              #Clé d'identification de fichier source
cstKeyCatalogKeyId   = "id"                         #Identifiant local  des zones ; avant consolidation de toutes les sources
cstKeyCatalogKeyGUId = "GUId"                       #Identifiant global des zones ; après consolidation de toutes les sources
cstKeyCatalogKeyAreaDesc = "areaDescription"

cstAirspacesCatalog:str   = "AirspacesCatalog"

class AsCatalog:

    def __init__(self, oLog)-> None:
        bpaTools.initEvent(__file__, oLog)
        self.oLog                       = oLog
        self.oGlobalCatalogHeader:dict  = {}                        #Entête du catalogue gloabal
        self.oGlobalCatalog:dict        = {}
        self.oClonesCatalog:dict        = None
        self.sFileCatalog:str           = ""
        return

    def getContent(self) -> dict:
        if cstKeyCatalogCatalog in self.oGlobalCatalog:
            return self.oGlobalCatalog[cstKeyCatalogCatalog]    #Liste des zones consolidés
        else:
            return {}                                           #Liste vide

    def saveCatalogFiles(self, sFile:str=None) -> bool:
        if sFile:   self.sFileCatalog = sFile
        bpaTools.writeJsonFile(self.sFileCatalog, self.oGlobalCatalog)
        sFile = self.sFileCatalog.replace(".json", ".csv")
        csv = aixmReader.convertJsonCalalogToCSV(self.oGlobalCatalog)
        bpaTools.writeTextFile(sFile, csv)
        return

    def addSrcFile(self, sKeyFile:str, sFile:str, sOwner:str, sOrigin:str, sVersion:str, sCreated:str) -> None:
        oCatalogFile:dict = {}                                   #Description du fichier analysé
        oCatalogFile.update({cstKeyCatalogSrcFile:sFile})        #Nom du fichier analysé
        oCatalogFile.update({cstKeyCatalogSrcOwner:sOwner})      #Référence au propriétaire
        oCatalogFile.update({cstKeyCatalogSrcOrigin:sOrigin})    #Origine du fichier analysé
        oCatalogFile.update({cstKeyCatalogSrcVersion:sVersion})  #Version du fichier analysé
        oCatalogFile.update({cstKeyCatalogSrcCreated:sCreated})  #Horodatage de la création du fichier analysé
        if cstKeyCatalogSrcFiles in self.oGlobalCatalogHeader:
            self.oGlobalCatalogFiles = self.oGlobalCatalogHeader[cstKeyCatalogSrcFiles]     #Récupération de la liste des fichiers sources
        else:
            self.oGlobalCatalogFiles:dict = {}                                              #Création de la liste des fichiers sources
        self.oGlobalCatalogFiles.update({sKeyFile:oCatalogFile})                            #Enregistrement de la description du fichier analysé
        self.oGlobalCatalogHeader.update({cstKeyCatalogSrcFiles:self.oGlobalCatalogFiles})  #Enregistrement de la nouvelle liste des fichiers sources
        return

    def mergeJsonCatalogFile(self, sKeyFile:str, oFile:dict) -> None:
        if not oFile[poaffCst.cstSpExecute]:       #Flag pour prise en compte du traitement de fichier
            return

        fileCatalog = oFile[poaffCst.cstSpOutPath] + poaffCst.cstReferentialPath + sKeyFile + poaffCst.cstSeparatorFileName + poaffCst.cstCatalogFileName           #Fichier comportant le catalogue des zones
        self.oLog.info("..oooOOOO  poaffMergeFiles() --> Catalog consolidation file {0}: {1} --> {2}".format(sKeyFile, fileCatalog, oFile[poaffCst.cstSpProcessType]), outConsole=False)
        ofileCatalog = bpaTools.readJsonFile(fileCatalog)                                                #Chargement du catalogue du fichier analysé
        #self.oLog.info("ofileCatalog:\n{0}".format(ofileCatalog, outConsole=False))

        oHeadFile = ofileCatalog[poaffCst.cstGeoHeaderFile]                                                #Entête concernant le fichier analysé

        if cstKeyCatalogSrcFiles in self.oGlobalCatalogHeader:
            self.oGlobalCatalogFiles = self.oGlobalCatalogHeader[cstKeyCatalogSrcFiles]     #Récupération de la liste des fichiers sources
        else:
            self.oGlobalCatalogFiles:dict = {}                                              #Création de la liste des fichiers sources
        if self.oGlobalCatalog=={}:                                                                      #Catalogue vde, donc initialisation du catalogue gloabal
            self.oGlobalCatalog.update({poaffCst.cstGeoType:ofileCatalog[poaffCst.cstGeoType]})              #Typage du catalogue
            self.oGlobalCatalogHeader.update({cstKeyCatalogSoftware:oHeadFile[cstKeyCatalogSoftware]})   #Référence au soft de construction
            self.oGlobalCatalogHeader.update({cstKeyCatalogCreated:oHeadFile[cstKeyCatalogCreated]})     #Heurodatage de la construction
            self.oGlobalCatalogHeader.update({cstKeyCatalogContent:oHeadFile[cstKeyCatalogContent]})     #Déclaration du contenu
            self.oGlobalCatalog.update({poaffCst.cstGeoHeaderFile:self.oGlobalCatalogHeader})              #Ajout de l'entête de catalogue
        else:
            self.oGlobalCatalogHeader = self.oGlobalCatalog[poaffCst.cstGeoHeaderFile]                     #Entête du catalogue gloabal

        self.addSrcFile(sKeyFile, \
                        oHeadFile[cstKeyCatalogSrcFiles]["1"]["srcAixmFile"], \
                        oFile[poaffCst.cstSpSrcOwner], \
                        oHeadFile[cstKeyCatalogSrcFiles]["1"]["srcAixmOrigin"], \
                        oHeadFile[cstKeyCatalogSrcFiles]["1"]["srcAixmVersion"], \
                        oHeadFile[cstKeyCatalogSrcFiles]["1"]["srcAixmCreated"])

        if sKeyFile in ["BPa-FrenchSS","BPa-ZonesComp","BPa-TestXmlSIA","BPa-TestRefAlt","BPa-Test4Clean","BPa-Test4AppDelta1","BPa-Test4AppDelta2","BPa-Test4AppDelta3"]:
            sSrcFile:str = "POAFF"
        elif sKeyFile in ["BPa-Parcs","LPO-Parcs"]:
            sSrcFile:str = "POAFF-Parcs"
        elif sKeyFile in ["BPa-Birds","LPO-Birds","FFVP-Birds"]:
            sSrcFile:str = "POAFF-Birds"
        elif sKeyFile in ["FFVL-Protocoles"]:
            sSrcFile:str = "POAFF-Prot"
        elif sKeyFile in ["SIA-SUPAIP"]:
            sSrcFile:str = "POAFF-SUPAIP"
        elif sKeyFile in ["SIA-XML","SIA-AIXM"]:
            sSrcFile:str = "SIA"
        elif sKeyFile=="EuCtrl":
            sSrcFile:str = "EuCtrl"
        else:
            sSrcFile:str = "?"

        self.oClonesCatalog:dict = {}
        oGlobalAreas = self.getContent()
        oAsAreas = ofileCatalog[cstKeyCatalogCatalog]                                       #Catalogue des Espace-aériens contenus dans le fichier analysé
        sTitle = cstAirspacesCatalog + " Merge Catalog File + " + sKeyFile
        barre = bpaTools.ProgressBar(len(oAsAreas), 20, title=sTitle)
        idx = 0
        for sAsKey, oAs in oAsAreas.items():
            idx+=1
            oAs.update({cstKeyCatalogKeySrcFile:sKeyFile})                                  #Clé de référence au fichier source
            oAs.update({"srcFile":sSrcFile})                                                #Seconde référence au fichier source

            #if oAs["id"] in ["LFLL10"]:
            #    print("zzz.zzz")

            self.isCleanArea4FreeFlight(sKeyFile, oAs)                                      #Eventuelles épurations
            self.isSpecialArea4FreeFlight(sKeyFile, oAs)                                    #TRaitements particuliers de transformation de zones (Modif de type 'RTBA' + Clônes de type 'LTA', etc)
            oAs.update({"nameV":aixmReader.getVerboseName(oAs)})                            #Mise a jour systématique du libellé (si chgt via fct)

            if self.isValidArea(sKeyFile, oAs):                                             #Exclure certaines zones
                sNewKey = str(oAs["id"]).strip()                                            #Nouvel identifiant de référence pour le catalogue global
                if sNewKey=="": sNewKey = self.makeNewKey()                                 #Initialisation d'une clé non vide
                if   oFile[poaffCst.cstSpProcessType]==poaffCst.cstSpPtAdd:                 #Ajout systématique des zones (avec débloublonnage des 'id' automatisé)
                    if sNewKey in oGlobalAreas:
                        sNewKey2 = self.makeNewKey(sNewKey, oGlobalAreas)                   #Identification d'une nouvelle clé unique
                        #self.oLog.info("Deduplication area for global catalog - orgId={0} --> newId={1}".format(sNewKey, sNewKey2, outConsole=False))
                        sNewKey = sNewKey2
                    oAs.update({cstKeyCatalogKeyGUId:sNewKey})
                    oGlobalAreas.update({sNewKey:oAs})                                      #Ajoute la zone au catalogue global
                    #self.oLog.info("Add area in global catalog - ({0}){1}".format(sKeyFile, sNewKey, outConsole=False))
                elif oFile[poaffCst.cstSpProcessType]==poaffCst.cstSpPtAddDelta:                                          #Ajout des zones qui ne sont pas déjà existante
                    lExist:int = self.ctrlExistArea(oGlobalAreas, oAs, sNewKey)
                    #   1 if area exist with the sames caracteristics
                    #   0 if area not exist
                    #  -1 if area exist with the different caracteristics                        oAs.update({cstKeyCatalogKeyGUId:sNewKey})
                    if lExist == -1:
                        sNewKey2 = self.makeNewKey(sNewKey, oGlobalAreas)                   #Identification d'une nouvelle clé unique
                        #self.oLog.info("Deduplication area for global catalog - orgId={0} --> newId={1}".format(sNewKey, sNewKey2, outConsole=False))
                        sNewKey = sNewKey2
                    if lExist <= 0:
                        oAs.update({"deltaExt":True})                                       #DeltaExtended - Marquage d'une extension de périmètre par analyse différentielle
                        oAs.update({cstKeyCatalogKeyGUId:sNewKey})
                        oGlobalAreas.update({sNewKey:oAs})                                  #Ajoute la zone au catalogue global
                        #self.oLog.debug("Delta add area in global catalog - ({0}){1}".format(sKeyFile, sNewKey, outConsole=False))
                    else:
                        #self.oLog.info("Ignored area (existing in global catalog) - ({0}){1}".format(sKeyFile, sNewKey, outConsole=False))
                        None
                else:
                    self.oLog.error("Process type error - {0}".format(oFile[poaffCst.cstSpProcessType], outConsole=True))

            self.isSpecialExcludeArea(sKeyFile, oAs)                                        #Gestion des inclusions/Exclusions de zones des périmètres

            barre.update(idx)
        barre.reset()

        #Ajouter dans le catalogue globale les éventuelles zones clônés (durant le traitement...)
        for sKey, oClone in self.oClonesCatalog.items():
            oGlobalAreas.update({sKey:oClone})                                              #Ajoute la zone au catalogue global

        oSrcFiles = self.oGlobalCatalogHeader.pop(cstKeyCatalogSrcFiles)
        self.oGlobalCatalogHeader.update({cstKeyCatalogNbAreas:len(oGlobalAreas)})          #Nombre de zones
        self.oGlobalCatalogHeader.update({cstKeyCatalogSrcFiles:oSrcFiles})
        self.oGlobalCatalog.update({cstKeyCatalogCatalog:oGlobalAreas})                     #Nouvelle liste de zones
        return

    def addRefAreasInCatalogFile(self, partialConstruct:bool) -> None:
        self.oLog.info("..oooOOOO  addRefAreasInCatalogFile() --> Add all areas in global Catalog", outConsole=False)
        oGlobalAreas = self.getContent()
        oAreasRef:dict = geoRefArea.GeoRefArea(partialConstruct).AreasRef
        sTitle = cstAirspacesCatalog + " Add RefAreas in global Catalog"
        barre = bpaTools.ProgressBar(len(oAreasRef), 20, title=sTitle)
        idx = 0
        for sAreaKey, oAreaRef in oAreasRef.items():
            idx+=1
            sNewKey:str = "#poaff-" + sAreaKey
            oArea:dict = oAreaRef[enuAreasRef.geoJSON.value]
            oArea = oArea["features"]
            for oArea2 in oArea:
                #Sample of area catalog content {'zoneType': 'Airspace Zone', 'groupZone': False, 'UId': '400002237139872', 'id': 'EYSPP', 'srcClass': 'G', 'srcType': 'RAS', 'name': 'PAJUOSTIS TIZ', 'class': 'RMZ', 'type': 'RAS', 'srcLocalType': 'EYPP TRAFFIC INFORMATION ZONE', 'srcCodeActivity': 'MILOPS', 'codeActivity': 'MILOPS', 'srcCodeMil': 'MIL', 'vfrZone': True, 'freeFlightZone': True, 'freeFlightZoneExt': False, 'srcName': 'PAJUOSTIS TIZ', 'upperType': 'ALT', 'upperValue': '4500', 'upperUnit': 'FT', 'lowerType': 'HEI', 'lowerValue': '0', 'lowerUnit': 'FT', 'lower': 'SFC', 'upper': '4500FT AMSL', 'lowerM': 0, 'upperM': 1371, 'vfrZoneExt': False, 'potentialFilter4FreeFlightZone': True, 'srcCodeLocInd': 'EYPP', 'activationCode': 'H24', 'desc': '1. LTU MILTel.: +370 5 2748194,e-mail: pajuostis.ops@mil.lt2. Call sign - PAJUOSTIS RADIO. Frequency 122.550 MHz3.TIZ is radio mandatory zone (RMZ). In RMZ pilots shall maintain continuous air-ground voice communication watch and establish two-way communication, as necessary, on the appropriate communication channel. Before entering RMZ, a pilot shall establish radio comunication, and transmit call sign, type of aircraft, position, level, and intentions of the flight - MON-FRI: 0500-2100 SAT: 0600-1800: - 1HR HOL: voir/see NOTAM', 'nameV': 'RAS PAJUOSTIS TIZ (MILOPS)', 'keySrcFile': 'BPa-TestRefAlt', 'GUId': 'EYSPP'}
                sNewKey2:str = "{0}({1})".format(sNewKey, oArea2["properties"]["name"])
                oAreaCat:dict = {}
                oAreaCat.update({"zoneType"             :"Geographical area"})
                oAreaCat.update({"groupZone"            :False})
                oAreaCat.update({"vfrZone"              :True})
                oAreaCat.update({"vfrZoneExt"           :True})
                oAreaCat.update({"freeFlightZone"       :True})
                oAreaCat.update({"freeFlightZoneExt"    :True})
                oAreaCat.update({"keySrcFile"           :"AreasRef"})
                oAreaCat.update({"srcFile"              :"POAFF-Area"})
                oAreaCat.update({"orgName"              :"POAFF"})
                oAreaCat.update({"headId"               :"POAFF"})
                oAreaCat.update({"orgName2"             :"POAFF"})
                oAreaCat.update({cstKeyCatalogKeyGUId   :sNewKey2})
                oAreaCat.update({"UId"                  :sNewKey2})
                oAreaCat.update({cstKeyCatalogKeyId     :sNewKey2})
                oAreaCat.update({"class"                :"AREA"})
                oAreaCat.update({"type"                 :"GEO"})
                oAreaCat.update({"name"                 :"{0} (ISO={1})".format(oArea2["properties"]["name"], oArea2["properties"]["countryIsoCode"])})
                if oAreaRef[enuAreasRef.descComp.value] == "":
                    oAreaCat.update({"desc"             :"{0}".format(str(oAreaRef[enuAreasRef.desc.value]).replace("\n",""))})
                else:
                    oAreaCat.update({"desc"             :"{0} - {1}".format(str(oAreaRef[enuAreasRef.desc.value]).replace("\n",""), str(oAreaRef[enuAreasRef.descComp.value]).replace("\n",""))})

                oAreaCat.update({"lower"                :"SFC"})
                oAreaCat.update({"lowerM"               :0})
                oAreaCat.update({"lowerType"            :"HEI"})
                oAreaCat.update({"lowerValue"           :"0"})
                oAreaCat.update({"lowerUnit"            :"FT"})
                #For map
                #oAreaCat.update({"lower"               :"1000 AMSL"})
                #oAreaCat.update({"lowerM"              :300})
                #oAreaCat.update({"lowerType"           :"ALT"})
                #oAreaCat.update({"lowerValue"          :"1000"})
                #oAreaCat.update({"lowerUnit"           :"FT"})

                oAreaCat.update({"upper"                :"FL999"})
                oAreaCat.update({"upperM"               :30449})
                oAreaCat.update({"upperType"            :"STD"})
                oAreaCat.update({"upperValue"           :"999"})
                oAreaCat.update({"upperUnit"            :"FL"})
                oAreaCat.update({"nameV"                :aixmReader.getVerboseName(oAreaCat)})

                oGlobalAreas.update({sNewKey2:oAreaCat})                                      #Ajoute la zone au catalogue global
            barre.update(idx)
        barre.reset()
        return

    #return values
    #   1 if area exist with the sames caracteristics
    #   0 if area not exist
    #  -1 if area exist with the different caracteristics
    def ctrlExistArea(self, oGlobalAreas:dict, oAs:dict, sKey:str) -> int:
        lRet:int = 0
        if not sKey in oGlobalAreas:
            return lRet
        #Contrôle de cohérence sur une clé-fonctionnelle constituée sur 2 ou 4 caractéristiques
        sFKeyActivObj2:str = oAs.get("class", "") + oAs.get("type" , "")
        sFKeyActivObj4:str = sFKeyActivObj2 + oAs.get("lower", "") + oAs.get("upper", "")
        lIdx:int
        for lIdx in range(10):       #Contrôle sur occurence de 10 doublons envisagés
            sNewKey:str = sKey
            if lIdx > 0:
                sNewKey += cstDeduplicateSeparator + str(lIdx)
            if sNewKey in oGlobalAreas:
                oExistObj = oGlobalAreas[sNewKey]
                sFKeyExistObj:str = oExistObj.get("class", "") + oExistObj.get("type" , "")
                sFKeyActivObj:str = sFKeyActivObj2
                if oExistObj.get("keySrcFile", "")!="SIA-SUPAIP":
                    sFKeyExistObj += oExistObj.get("lower", "") + oExistObj.get("upper", "")
                    sFKeyActivObj:str = sFKeyActivObj4
                if sFKeyActivObj == sFKeyExistObj:
                    lRet = 1
                else:
                    lRet = -1
            if lRet==1:
                break
        return lRet

    def makeNewKey(self, sKey:str="", oCat:dict={}) -> str:
        lIdx:int = 1
        aKey = sKey.split(cstDeduplicateSeparator)
        if len(aKey)>1: sKey = aKey[0]
        while True:
            sNewKey = sKey + cstDeduplicateSeparator + str(lIdx)
            if not(sNewKey in oCat):
                break
            lIdx+=1
        return sNewKey

    #Suppression physique de zones concidérées comme fausse à la source / Les zones exclus ne sont pas reprises dans le catalogue final
    def isValidArea(self, sKeyFile:str, oAs:dict) -> bool:
        ret:bool = True                                                 #Default value

        #Exclure les zones de regroupement
        if oAs["groupZone"]:
            return False

        #Exclure les zones sans précision de coordonnées
        if oAs.get("excludeAirspaceNotCoord",False):
            return False

        #Depuis le 06/10/2020 ; Préserver les zones particulières de type Point
        if oAs.get("excludeAirspaceNotFfArea", False)==True and oAs.get("geometryType", "")!="Point":
           return False

        if sKeyFile == "BPa-Test4Clean":                    #Suppression manuelle de zones
            if oAs[cstKeyCatalogKeyId] in ["LFD18B1"]:    #Test de suppression manuelle d'une zone en mer - [Q] 18 B1 (id=LFD18B1)
                ret = False

        if sKeyFile in ["SIA-AIXM","BPa-Test4Clean"]:       #Suppression manuelle de zones
            #D CTR KOKSIJDE (EBFN) - Tracé Français incomplet dans le fichier SIA !
            #Suppression de nombreux tracé SIA (border with France) et en doublon avec ceux d'Eurocontrol ! donc je ne prend pas en compte l'instance SIA
            if oAs[cstKeyCatalogKeyId] in ["TMA16213","TMA16214","UIR4831","EBFN","EB1","LFCB1A","LFCB1B","LFSTNORD","LFSTSUD","LFST1.1","LFST30","LFSB10.20","LFSBNORD","LFSB20.30","LFSB20.20","LFSB20","LFSB30.30","LFSB30",
                  "LFSB30.20","LFSB40.20","LFSB40.30","LFSB40","LFSB70.20","LFSB70","LFSB88","LFSB88.20","LFSB80.20","LFSB80","LFBALE1.2","LFSB85","LFSB85.20","LFSB82","LFSB82.20",
                  "LFSB02S","LFSB60","LFSB60.20","LFSB50","LFSB50.20","LFSB02F","LFSB3","LFSB01S","LFSB2","LFSB01A","LFSB02A",'LFSB03S',"LFSB04S","TTZP"]:
                ret = False

        if sKeyFile == "EuCtrl":                            #Suppression manuelle de zones
            #Nota. [D] CTR ALBERT BRAY (id=LFAQ) - a un mauvais tracé et récupération via le fichier SIA
            #Nota. [D] CTR CHAMBERY 2 (id=LFLB2) - suite aux modifications coté SIA-France - le fichier Eurocontrol n'est pas encore synchronisé
            #Suppression de quelques tracé Eurocontrol (recouvrement France-autre pays) dont la définition Eurocontrol n'est pas bonne par rapport a l'instance SIA
            if oAs[cstKeyCatalogKeyId] in ["LFLB2","EDSB2","LFSB1F","LSGG","LSGG1","LSGG2","LSGG3","LSGG4","LSGG4.1","LSGG6","LSGG7","LSGG8","LSGG9","LSGG10"]:
                ret = False

        if not(ret):
            self.oLog.info("Unvalid area by manual filter - ({0}) GUId={1} UId={2} name={3}".format(sKeyFile, oAs[cstKeyCatalogKeyGUId], oAs["UId"], oAs["nameV"]), outConsole=False)
        return ret

    #Flager certaine zone 'inutile' pour la vision 'freeflight'
    def isCleanArea4FreeFlight(self, sKeyFile:str, oAs:dict) -> None:
        bClean:bool = False                                 #Default value

        #Test de suppression volontaire
        if sKeyFile == "BPa-Test4AppDelta1":
            if oAs[cstKeyCatalogKeyId] in ["LFRD02"]:
                bClean = True

        #Fonctionnalité d'Exclusion de certaines zones
        elif sKeyFile in ["EuCtrl","SIA-AIXM"]:

            #Suppression de zones non-utile
            if oAs[cstKeyCatalogKeyId] in ["LER152","LER153"]:
                bClean = True
                #### LER152+LER153 - Parc en Espagne, deja intégré dans les parcs naturels via integration FFVP

            #Suppression de zones non-utile, exemple en mer ou autres cas...
            #elif oAs[cstKeyCatalogKeyId] in ["EGWO2","LFD18B1","LFD18A5","LFD18B2","LFD214","LFD16B","LFD16D","LFD31","LFD54B1","LFD54B2","LFD143B",
            #        "LFML11","LFD54WB","LFR217/2","CTA47782","LFR191A","LFR108C",LFR225","LFMD2","LFD54B3","LFR157","LFPG7.3","LFPG7.4","LFD54WA"]:
            #    bClean = True

        if bClean:
            oAs.update({"freeFlightZone":False})
            oAs.update({"freeFlightZoneExt":False})
            oAs.update({"excludeAirspaceByFilter":True})
            #self.oLog.info("Ignored freeflight area by manual filter - ({0}){1}".format(sKeyFile, oAs["UId"], oAs[cstKeyCatalogKeyGUId], outConsole=False))
        return

    #Intégre sytematiquement certaine zone utile pour la vision 'freeflight'
    def isSpecialArea4FreeFlight(self, sKeyFile:str, oAs:dict) -> None:

        #Traitements particuliers
        if sKeyFile in ["EuCtrl","SIA-AIXM","SIA-SUPAIP","FFVL-Protocoles","BPa-Test4AppDelta1"]:

            ### deb -Protocoles FFVL ou FFVP - Gestion spécifique des protocoles particuliers négociés par la FFVL ou la FFVP
            cstFfvlProtType:str = "FFVL-Prot"
            cstFfvpProtType:str = "FFVP-Prot"
            cstProtBase:str = "(Pascal Bazile: Voir protocole {0}) - "
            ### FFVL ###
            #Zones règlementés ou de classe D
            if oAs[cstKeyCatalogKeyId] in ["LFR30A","LFR30B"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Massifdumontblancchamonix.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LFSRMZOH"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Protocole_La_Heve_Lejard_10_03_2017.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LFR331","LFR332A","LFR332B"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/13EME-BCA-LFR331.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LFR138","LFR138TA"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/ALVL_UCPA_E3P_Canjuers_2017.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LFLN1.4"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Protocole-TMA-2016-03-31_0.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LFR211","LFR212","LFR45D","LFR45S7"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/BA116%20protocole%20d%27accord%2013032008.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["SOCA"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/CAYENNEROCHAMBEAU.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LFAT"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/CTR_LE_TOUQUET.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LFSO","LFR92"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/BA133.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LFRD01"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/DINARD.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LFOE","LFOE1"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/BA105-VL-2018.pdf + https://federation.ffvl.fr/sites/ffvl.fr/files/Accord%20%20sites%20de%20treuils%20Quatremare%20et%20Quittebeuf.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LFRG"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Trouville_grand_bec.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LFR77A"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/convention%20base%20salon.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LFCR"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Protocole%20SNA%20-%20Comit%C3%A9%20Dept%20Vol%20libre%20Rodez%202009.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LFR55D"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/BA115-VL-2018.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            #Zones classifiés Dangereuses
            if oAs[cstKeyCatalogKeyId] in ["LF963"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Poitiers.pdf")
                oAs.update({"name":oAs.get("name","") + " - " + cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LF889"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/TreuilEnSemaine.pdf")
                oAs.update({"name":oAs.get("name","") + " - " + cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LF8917"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/arreteMasserac.pdf")
                oAs.update({"name":oAs.get("name","") + " - " + cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LFV934TOW"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/ArretedefLaNoe%20avril%202017_0.pdf")
                oAs.update({"name":oAs.get("name","") + " - " + cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LF915", "LF916"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Accord%20%20sites%20de%20treuils%20Quatremare%20et%20Quittebeuf.pdf")
                oAs.update({"name":oAs.get("name","") + " - " + cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LFV1007TOW"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/BA105-VL-2018.pdf")
                oAs.update({"name":oAs.get("name","") + " - " + cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LF995"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Savineslelac.pdf")
                oAs.update({"name":oAs.get("name","") + " - " + cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LF9605"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Protocole.pdf")
                oAs.update({"name":oAs.get("name","") + " - " + cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})

            ### Cas particulier FFVL + FFVP ###
            if oAs[cstKeyCatalogKeyId] in ["LFST1","LFST2"]:
                #Cas particulier de 2 protocoles: FFVL + FFVP !
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Strasbourg_Entzheim.pdf + https://federation.ffvl.fr/sites/ffvl.fr/files/TMA_Strasbourg.pdf")
                oAs.update({"codeActivity":cstFfvlProtType + " / " + cstFfvpProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LFRG2"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/TMA-DEAUVILLE.pdf")
                oAs.update({"codeActivity":cstFfvlProtType + " / " + cstFfvpProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LFR19610", "LFR19620", "LFR19630", "LFR196A2", "LFR196B", "LFR19660", "LFR19670", "LFR19680"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/GAPVALENSOLE.pdf")
                oAs.update({"codeActivity":cstFfvlProtType + " / " + cstFfvpProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})

            ### FFVP ###
            if oAs[cstKeyCatalogKeyId] in ["EDSB-F","LFST-BADC","LFR199","LFST2.1","LFST1.2","LFST7","LFR197","LFR198"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/TMA_Strasbourg.pdf")
                oAs.update({"codeActivity":cstFfvpProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LFBI1","LFBI2"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Protocole_Poitiers_CTR1_et_CTR2.pdf")
                oAs.update({"codeActivity":cstFfvpProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LFOJ5.2", "LFOJ1.2", "LFOJ6.2", "LFOJ8", "LFOJ5.1"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Protocole_Orleans_2015-BA123.pdf")
                oAs.update({"codeActivity":cstFfvpProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs[cstKeyCatalogKeyId] in ["LFBG", "CTA4721", "LFR49A1", "LFR49A2"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Cognac_0.pdf")
                oAs.update({"codeActivity":cstFfvpProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            ### fin - Protocoles FFVL ou FFVP

        #Fonctionnalité spécifique pour exclusion standard et intégratrion spécifique pour la CFD
        #Les zones suivantes sont utilisées pour un affichage quasi-exaustif ou garantie des caulculs-automatisés
        if sKeyFile in ["EuCtrl","SIA-AIXM"]:
            if oAs[cstKeyCatalogKeyId] in ["FMEE1","CTA4351A.2","OCA4521.20"]:
                oAs.update({"freeFlightZone":False})
                oAs.update({"freeFlightZoneExt":False})
                oAs.update({"use4cfd":True})
                oAs.update({"excludeAirspaceByFilter":True})
                #[E] TMA LA REUNION 1 (id=FMEE1)
                #[E] CTA PIARCO A.20 (id=CTA4351A.2)
                #[E] OCA TAHITI.20 (id=OCA4521.20)

        #Test pour test de flag sur une RTBA (SIA France, ne sont jamais activées les samedis/dimanches et jours fériés)
        if sKeyFile in ["BPa-Test4Clean","BPa-Test4AppDelta1","BPa-TestRefAlt"] and oAs["type"]=="R":
            if oAs[cstKeyCatalogKeyId] in ["LFR145","Test4"]:
                oAs.update({"type":"RTBA"})
                if oAs.get("codeActivity", "")=="":
                    oAs.update({"codeActivity":"MILOPS"})
                else:
                    oAs.update({"codeActivity":"MILOPS" + ";" + oAs.get("codeActivity", "")})
                oAs.update({"exceptSAT":True})
                oAs.update({"exceptSUN":True})
                oAs.update({"exceptHOL":True})

        #Toutes les RTBA du SIA France, ne sont jamais activées les samedis/dimanches et jours fériés
        if sKeyFile in ["EuCtrl","SIA-AIXM"] and oAs["type"]=="R":
            if oAs[cstKeyCatalogKeyId] in ["LFR45A","LFR45B","LFR45C","LFR45D","LFR45N2","LFR45N3","LFR45N4","LFR45N5.1","LFR45N5.2","LFR45S1","LFR45S2","LFR45S3","LFR45S4","LFR45S5","LFR45S6.1","LFR45S6.2","LFR45S7","LFR45NS","LFR46A","LFR46B","LFR46C","LFR46D","LFR46E1","LFR46E2","LFR46F1","LFR46F2","LFR46F3","LFR46G","LFR46N1","LFR46N2","LFR69","LFR139","LFR142","LFR143","LFR144","LFR145","LFR147","LFR165","LFR152","LFR166A","LFR166B","LFR166C","LFR56","LFR57","LFR149A","LFR149B","LFR149D","LFR149E","LFR193A","LFR193B","LFR590A","LFR590B","LFR191A","LFR191B","LFR191C","LFR589A","LFR589B","LFR591","LFR592","LFR593A","LFR593B"]:
                oAs.update({"type":"RTBA"})
                if oAs.get("codeActivity", "")=="":
                    oAs.update({"codeActivity":"MILOPS"})
                else:
                    oAs.update({"codeActivity":"MILOPS" + ";" + oAs.get("codeActivity", "")})
                oAs.update({"exceptSAT":True})
                oAs.update({"exceptSUN":True})
                oAs.update({"exceptHOL":True})
                #self.oLog.info("Special French-RTBA areas - ({0}){1}".format(sKeyFile, oAs["UId"], oAs[cstKeyCatalogKeyGUId], outConsole=False))

        #LTA - Traitements spécifiques pour construction des zones d'extention de vol libre
        if sKeyFile in ["SIA-SUPAIP","BPa-FrenchSS","SIA-AIXM","EuCtrl","BPa-Test4AppDelta1"] and oAs["type"]=="LTA":

            #Construction volontaire 'freeFlightZone' des clônes de certaines zones pour constituer la surface S en France
            if oAs[cstKeyCatalogKeyId] in ["LTA130731","LTA130751","LTA130752","LTA130753"]:
                #Id=LTA130731 - AC E - AN LTA FRANCE 3 ALPES 1 / *AAlt ["3000FT AGL-FL115/FL195", "3505m/5943m", "ffExt=Yes"]
                #Id=LTA130751 - AC E - AN LTA FRANCE 5 PYRENEES 1 Lower(3000FT AGL-FL115) / *AAlt ["3000FT AGL-FL115/FL195", "3505m/5943m", "ffExt=Yes"]
                #Id=LTA130752 - AC E - AN LTA FRANCE 5 PYRENEES 2 Lower(3000FT AGL-FL115) / *AAlt ["3000FT AGL-FL115/FL195", "3505m/5943m", "ffExt=Yes"]
                #Id=LTA130753 - AC E - AN LTA FRANCE 5 PYRENEES 3 Lower(3000FT AGL-FL115) / *AAlt ["3000FT AGL-FL115/FL195", "3505m/5943m", "ffExt=Yes"]

                if sKeyFile in ["SIA-SUPAIP","BPa-FrenchSS","SIA-AIXM","BPa-Test4AppDelta1"]:  #Ne pas clôner les zones sur les sources: "EuCtrl","BPa-Test4AppDelta1"
                    #Phase 1.0 - Contruction du clone d'objet
                    oClone = deepcopy(oAs)
                    sNewKey:str = poaffCst.cstPoaffCloneObject + oAs["UId"]
                    oClone.update({"GUId":sNewKey})
                    oClone.update({"class":"D"})
                    oClone.update({"desc":"(Pascal Bazile) Zone spécifique pour limitation de la 'Surface S en France'"})
                    #---Lower---
                    del oClone["lowerMin"]
                    oClone.update({"lower":oAs["upper"]})               #FL195
                    oClone.update({"lowerM":oAs["upperM"]})             #5943
                    del oClone["ordinalLowerMinM"]                      #delete item
                    oClone.update({"lowerType":oAs["upperType"]})       #STD
                    oClone.update({"lowerValue":oAs["upperValue"]})     #195
                    oClone.update({"lowerUnit":oAs["upperUnit"]})       #FL
                    del oClone["lowerTypeMnm"]                          #delete item
                    del oClone["lowerValueMnm"]                         #delete item
                    del oClone["lowerUnitMnm"]                          #delete item
                    #---Upper---
                    oClone.update({"upper":"FL220"})
                    oClone.update({"upperM":"6706"})
                    oClone.update({"upperType":"STD"})
                    oClone.update({"upperValue":"220"})
                    oClone.update({"upperUnit":"FL"})
                    oClone.update({"nameV":aixmReader.getVerboseName(oClone)})
                    #Phase 1.1 - Exclusion volontaire 'vfrZone' des clônes de la zone d'origine
                    #oClone.update({"vfrZone":False})
                    #oClone.update({"vfrZoneExt":False})
                    #oClone.update({"excludeAirspaceByFilter":True})
                    oClone.update({"ExtOfItaly":True})                  #Exclusion volontaire du pays
                    oClone.update({"ExtOfSwitzerland":True})            #Exclusion volontaire du pays
                    self.oClonesCatalog.update({sNewKey:oClone})        #Ajoute ce clône zone au catalogue des objets clonés


            #Filtrage volontaire 'vfrZone' et 'freeFlightZone' de la base officielle de la surface S en France (car la nouvelle 'surface S' est spécifiquement retracée par BPascal)
            if oAs[cstKeyCatalogKeyId] in ["LTA13071"]:
                #Id=LTA13071 - AN LTA FRANCE 1 Lower(3000FT AGL-FL115)
                oAs.update({"groupZone":True})          #Utile pour suppression au niveau des toutes sorties (y compris 'ifr')
                oAs.update({"vfrZone":False})
                oAs.update({"vfrZoneExt":False})
                oAs.update({"freeFlightZone":False})
                oAs.update({"freeFlightZoneExt":False})
                oAs.update({"excludeAirspaceByFilter":True})


            #Filtrage volontaire des bases officielles classée 'E' au dessus de la surface S en France
            if oAs[cstKeyCatalogKeyId] in ["LTA130731","LTA130732.","LTA130733.","LTA130734.","LTA130735.","LTA130736.","LTA130737.","LTA130741.","LTA130751","LTA130752","LTA130753"]:
                #Id=LTA130731 - AC E - AN LTA FRANCE 3 ALPES 1 / *AAlt ["3000FT AGL-FL115/FL195", "3505m/5943m", "ffExt=Yes"]
                #Id=LTA130732. - AC E - AN LTA FRANCE 3 ALPES 2.20 Lower(3000FT AGL-FL115) / *AAlt ["3000FT AGL-FL115/FL125", "3505m/3810m", "ffExt=Yes"]
                #Id=LTA130733. - AC E - AN LTA FRANCE 3 ALPES 3.20 Lower(3000FT AGL-FL115) / *AAlt ["3000FT AGL-FL115/FL145", "3505m/4419m", "ffExt=Yes"]
                #Id=LTA130734. - AC E - AN LTA FRANCE 3 ALPES 4.20 Lower(3000FT AGL-FL115) / *AAlt ["3000FT AGL-FL115/FL125", "3505m/3810m", "ffExt=Yes"]
                #Id=LTA130735. - AC E - AN LTA FRANCE 3 ALPES 5.20 Lower(3000FT AGL-FL115) / *AAlt ["3000FT AGL-FL115/FL175", "3505m/5334m", "ffExt=Yes"]
                #Id=LTA130736. - AC E - AN LTA FRANCE 3 ALPES 6.20 Lower(3000FT AGL-FL115) / *AAlt ["3000FT AGL-FL115/FL175", "3505m/5334m", "ffExt=Yes"]
                #Id=LTA130737. - AC E - AN LTA FRANCE 3 ALPES 7.20 Lower(3000FT AGL-FL115) / *AAlt ["3000FT AGL-FL115/FL135", "3505m/4114m", "ffExt=Yes"]
                #Id=LTA130741. - AC E - AN LTA FRANCE 4.20 Lower(3000FT AGL-FL115) / *AAlt ["3000FT AGL-FL115/FL135", "3505m/4114m", "ffExt=Yes"]
                #Id=LTA130751 - AC E - AN LTA FRANCE 5 PYRENEES 1 Lower(3000FT AGL-FL115) / *AAlt ["3000FT AGL-FL115/FL195", "3505m/5943m", "ffExt=Yes"]
                #Id=LTA130752 - AC E - AN LTA FRANCE 5 PYRENEES 2 Lower(3000FT AGL-FL115) / *AAlt ["3000FT AGL-FL115/FL195", "3505m/5943m", "ffExt=Yes"]
                #Id=LTA130753 - AC E - AN LTA FRANCE 5 PYRENEES 3 Lower(3000FT AGL-FL115) / *AAlt ["3000FT AGL-FL115/FL195", "3505m/5943m", "ffExt=Yes"]
                oAs.update({"vfrZone":False})
                oAs.update({"vfrZoneExt":True})
                oAs.update({"freeFlightZone":False})
                oAs.update({"freeFlightZoneExt":False})
                oAs.update({"excludeAirspaceByFilter":True})

        return

    #Gestion des Intégrations/Exclusions des zones associées aux périmètres
    def isSpecialExcludeArea(self, sKeyFile:str, oAs:dict) -> None:

        #Test de fonctionnalité d'Exclusion volontaire de certaines zones du territoire Français
        if sKeyFile in ["BPa-Test4Clean","BPa-Test4AppDelta1"]:
            if oAs[cstKeyCatalogKeyId] in ["LFD16E","EBS02","LECBFIR_E"]:
                oAs.update({"ExtOfFrench":True})       #Exclusion volontaire

        #Traitements particuliers
        if sKeyFile in ["EuCtrl","SIA-AIXM","SIA-SUPAIP","FFVL-Protocoles","BPa-ZonesComp","BPa-Parcs","LPO-Parcs","LPO-Birds","BPa-Birds","FFVP-Birds","BPa-Test4AppDelta1"]:

            #Fonctionnalité d'Exclusion volontaire de certaines zones de tous les territoires: Français (geoFrench + geoFrenchNorth + geoFrenchSouth etc...)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","EBBU-RMZ","EBBU-TMZ","EBKT-TMZ","EBKT-RMZ","EBUR","EBBU","EBCBA1C","EBLFA11","EBLCTA","EBHTA10A-P","EBTRAW","EBTSA15","EBTRA15","EBR25","EBS27","EBHTA10C-P","EBS30","EBHTA10D","EBS02","EBS182","EBTRA-SA","EBD29","EBS29","EBS33-1","EBS177","EBD26","EBS161","EBTSA27A","EBTSA27D","EBHTA04A-P","EBFS","EBFS@@-1","EBTSA27E","EBHTA06","EBSOUTH3","EBUR@@-1",
                  "EDUUSLN13","EDUUSLN23","EDUUSLN33","ETOANG4","EDGGBAD1","EDUUNTM141","EDUUNTM142","EDUUNTM24","EDUUNTM34","EDUUNTM44","EDR305Z","EDR305C","EDR305D","EDYYB5KH","ELLX2F2","ELLX5","ELLX1A","ELLXCLDB","ELLX2F1","EDCLCN","EDCLG","EDUU","EDCLEN","EDYYB5NL","EDYYB5LH","EDYYB5NIH","EDYYB5LL","EDGG","EDFIS08","EDDFCLE","EDR205DZ","EDGGPFA1","EDR205D","EDRJPJA","EDR205C","EDRZPJA","EDFIS09","EDGGPFA4","EDSBCLDF","EDGGSTG6","EDSBCLE","EDGGREU2","EDTL","LFSBDLN","EDTGPJA","EDTG","EDYYB5KL","LFSBDLSE","LFSBCLD01N","LFSBCLD01N@@-1","LFSB01AN.2",
                  "LFSB36Z.20","LFSBDZZ4","LFSB38Z.20","LFSBDZZ4T2","LFSTSUD","LFSTNORD","LFSB20L.20","LFSB21L.30","LFSBCLDSE","LFSB21L.20","LFSB22L.30","EDCLSBAE","LFSBCLE","LFSBCLDSW1","LFSB22L.20","LFSBDLSW1",
                  "LS-T21Z_1","LS-T201Z","LS-T21Z_2","LS-T23Z_3","LSAS","LSAS@@-1","LSAZ","LSR75_1","LSR75_2","LSR29","EUC25SMZ","EUC25SHZ","EUC25SM","EUC25SH","EUC25SMPZ","EUC25SLZ","EUC25SL1","EUC25SL2","EUC25SLPZ","LSR27","LSAG","LSR28","LSR26","LSR80","LSR81","LSR21","LSR23","LSR24","LSGG5",
                  "LECBFIR_G","LECB","LECB@@-1","LEBL_G","LEBL_C","LEBL_D","LEBL","LER152","LECM","LECM@@-1","LECMFIR_G","LESO-PART1","LESO","LECM-C","LECBFIR_C","LECBUIR_C","LED47B","LECBFIR_E","LECMUIR_C","LECMFIR_E","LED47A","LETLPRPTC1",
                  "LICTAMM18","LIMM","LIMM@@-1","LISFRAM01A","LIR4","LITSA72","LIR64","LICTAMM4","LICTAMM7","EGUP","EGTT","EGTT@@-1","EGSO","EGWO2","EGJA-2","EGJJ","EGJJS","EGJJ1","EGJJ2","CTA11562","LIGRANPARADISO","LEOrdessa","LIMM@@-2","LSASFRA1","LSASFRA2","LEFRA1","LED47Z2","LED47Z1","LETS91","LS-R18"]:
                oAs.update({"ExtOfFrench":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoFrenchNESW (supprimer les LTA Pyrénées, trop lourdes pour la mémoire des Flymaster)
            if oAs[cstKeyCatalogKeyGUId] in ["LTA130751","LTA130752","LTA130753"]:
                oAs.update({"ExtOfFrenchNESW":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones dans le territoire: geoCorse
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","LISFRAM01A","LIMM","LIMM@@-1","LIRR","LIRR@@-1","LICTARR2","LICTAMM10","LITSA73B","LIR82","LIRQ4","LITMARR3","LFMMB1","LFMMB2","LFMMB3","LFMMB4"]:
                oAs.update({"ExtOfCorse":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones dans le territoire: geoAntillesFr
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR"]:
                oAs.update({"ExtOfAntillesFr":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones dans le territoire: geoGuyaneFr
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR"]:
                oAs.update({"ExtOfGuyaneFr":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones dans le territoire: LaReunion
            if oAs[cstKeyCatalogKeyGUId] in ["FMR3"]:
                oAs.update({"ExtOfLaReunion":True})       #Exclusion volontaire sur base de l'Id

            #geoNouvelleCaledonie
            #geoMayotte
            #geoPolynesieFr

            #Fonctionnalité d'Exclusion volontaire de certaines zones dans le territoire: geoStPierreEtMiquelon
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR"]:
                oAs.update({"ExtOfStPierreEtMiquelon":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones dans le territoire: PWC France-Alpes, périmètre de performances (geoPWCFrenchAlps)
            #Nota. "LSR23" est en limite Suisse (je la garde ou pas?)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","UTA1641","UIR1640.20","LFMM","LIMM","LIMM@@-1","ECAC1","LSAS","LSAS@@-1","LSAG","LICTAMM18","LS-T21Z_2",
                  "LFLB1","LFLB2","LFLB3","LFLB3@@-1","LTA130731","LTA130733.","LTA130734.","LTA130735.","LTA130736.","LTA130737.","LFRoseland-Neige","LIMM@@-2"]:
                oAs.update({"ExtOfPWCFrenchAlps":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Inclusion volontaire de certaines zones dans le territoire: PWC France-Alpes, périmètre de performances (geoPWCFrenchAlps)
            if oAs[cstKeyCatalogKeyGUId] in ["LFLS1","TMA16161","LTA130732","LFVercors","LFEcrins"]:
                oAs.update({"IncOfPWCFrenchAlps":True})       #Inclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: Massif des Alpes (geoAlps)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","LHCC","EDCLCN"]:
                oAs.update({"ExtOfAlps":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoAlbania
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","SEAFRA1","LYBA","LYBA@@-1","LYBA@@-2", "LYBA@@-3","LGGG","LGGG@@-1","LGGG@@-2","LWSS","LWSS@@-1","LWSFRA","LGMD","LGKR","LGKR@@-1","LGKA","LWSH","LWSU","LWST","LYPG"]:
                oAs.update({"ExtOfAlbania":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones d'Andore (geoAndorra)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","LEBL","LEBL_C","LEBL_D","LEBL_G","LECB","LECB@@-1","LECBFIR_C","LECBFIR_G","LECBUIR_C"]:
                oAs.update({"ExtOfAndorra":True})           #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoires: Austria / Autriche (geoAustria)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","EDNYTMZB","EDNYTMZA","LSAZ","LSR43","LSR3","LSR54","LSR56","LS-VSE19","LS-VSE18","LJDO1_D","LJDO","LJDT","LKAAM","LKAATB","LKAASL","LKAASM","LKAASH","LKAAST","LKAAE","LKAAW","LKAAKV","LKAAWL","LKAAWM",
                  "LJDT2_D","LJLT","LJMU_D","LJMU","LJMB2_D","LJMT","LJMT@@-1","LHCC","LHCC@@-1","LHB16","LHB22","LHD52","LHSLESMO","LHB18","LHB20","LZBB","LZBB@@-1","EDUUDON13","EDUUDON23","EDUUDON33","EDUUCHI23","EDUUCHI33",
                  "LZBB-WEST","LZIB4","LZIB","LZIB2","LZR01","LKTB","LKTB@@-1","LKTB4","LKR4","LKKV","LKR1","LOWSCLDA","LOWS2","LOWS2@@-1","LOWSCLDB","LOWSCLDD",
                  "EDR142","LZTRA03","EDCLCN","LISFRAM01A","LJLA085P","LJLA095P","LJLA115P","LJLA125P","LJLA135P","LJLA145P","LJLA165P","LJLA195P","LJLA2024P","LJLA2529P","LJLA3032P","LJLA33P","LJLA34P","LJLA35P",
                  "LJLA36P","LJLA37P","LJLA38P","LJLA3966P","LI_IS01_3","LI_IS01_4","LI_IS01_5","LI_IS01_6","LI_IS01_7","LI_IS01_8","LI_IS01_9","LI_IS01_10","LI_IS01_11","LI_IS01_12","LI_IS01_13","LI_IS01_14",
                  "LJMBFRA","LJMURA1","LJMURA2","LJMURA3","LJMURA4","LJMURA5","LHLOWG01","LHWESTLP","LHLESMOL2","LHLESMOP","LHLESMOU","LKFRAB","LKPR-2","LKTRA12Z2","LKTRA13Z2","LKTRA11Z2",
                  "LKBUDEX0","LKBUDEX1","LKBUDEX2","LKBUDEX3","LKBUDEX4","LKBUDEX5","LKLOWL01","EDMMEGG1","EDLOWL03","EDLOWL04","EDLOWL01","EDLOWS04","EDUUCHI132","EDLOWS03KS","EDMMTRU2","EDMMTRU1","EDLOWS01KS","EDLOWI01","EDLOWI03","EDLOWI04","EDLOWI05","EDLOWI06","EDLOWI07","EDLOWI08","EDLOWI09",
                  "EDMMTEG1","LS-T53_1","LOVVW1IA01","LJLOWK01","LHLESMOL1","LKLOWW17","LKLOWW15","LKLOWW13","LKLOWW14","LKLOWW12","LKLOWW11","LKLOWW10","LKLOWW09","LKLOWW08","LKLOWW07","LKLOWW04","LKLOWW03","LKLOWW02","LKLOWL02","EDUU","LSAS","LSAS@@-1","LIMM","LIMM@@-1","LKAA","EDMM","LJLA","LKAMA1550","LKAMA1450",
                  "LJS001","LJS001A","LJS002A","LJS003","LJS005","LJS008","LHLESMO","LKTRA18Z","LKTRA19Z","LKTRA79Z","LKTRA75Z","LKTSA1Z","LS-R3Z","LS-T40","LS-T400","LS-T51","LS-T501","LZBB-FIS","EDCLG","EDFIS07","EDFIS06","LJDO1_E","LJMB2_E","LJMU_E","EDCLEN","EDCLSSAE","EDCLES","EDNYCLEC","EDNYCLEA","EDNYCLEB",
                  "LICTAPP17","LICTAPP5","LICTAPP1","LICTAPP19","LJDO1_C","LJUP","LJDT2_C","LJMU_C","LZSFRA","EDCLCS","LIMM@@-2","LSASFRA1","LZSLZIB004","LZSLZIB005","LZSLZIB001","LZSLZIB002","LSTMZNE"]:
                oAs.update({"ExtOfAustria":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire : geoBelarus
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","EPWWADIZ2","EPWWADIZ3","EPWWOATJR","EPWWZL","EPWWZH","EPWWEL","EPWWOATNE","EPWWEH","EPWWNL","EPWWNH","ECAC1","EPSFRA_P","EYVCL2","EYVCU2","EYVCL3","EYVCU3","EYVCL4","EYVCU4","EYVCL5","EYVCU5","UKBU","EYVL@@-1","UKBV","UKLV","EPWW","EYVL","EVRR@@-1","ULLL","UUWV","UKT503Z","UKT502Z",
                  "EPTR110","EPTR111","EPTR112A","EPTR112B","EPTR113","EPTR114","EPTR115A","EPTR115B","EPTR116","EPTR117","EPTR118","EPTR119","EPTR120A","EVR17","EPR9","EYD21","UUWV@@-1","ULLL@@-1","EVRRRIA3","EYVIFIS","EYKAFIS","EPSFIS1","EPSFIS2","UKLVED","UKBVLD","UKBVMD","UKBVMC","UKBVC","UKBB1","UKBVLC","UKBVW","UKLVC","UKLVU","UKLVEC",
                  "EYVC","EYVLL","EYVLM","EYSFRA","EYVC@@-1","EYVLU","EYVLE","EYVI-A","EYVI-B","EVRREAST","EVRR","EVRRCTA"]:
                oAs.update({"ExtOfBelarus":True})           #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: Belgium / Belgique (geoBelgium)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","EBUL607","EBSASKI A","EHL179","EBR24A","LFQQ","LFQQ1","LFQQ2","LFQQ3","LFQQ4","LFQQ4.1","LFQQ5","EBR18B",
                  "LFCBA16B","LFP38","EBR18A","ELLX1A","ELLX4","TMA16214","ELLX1B","ELS06","ELS05","EDR165A","EDR117","EBEHBKTMA","EHBK1-1",
                  "EHBK2","EHSRMZBK","EHBK1","EHBK1","EHMCD-1","EHMCD-1_B","EBL179","EHSRMZBDA","EBBL2","EHSRMZBL","EHEH4","EHEH3","EHEH1","EHEH2",
                  "EHGR","EHSRMZGR","EHV-REGTEH","EHAMS2","EHV-SCHIJF","EHAMS1","EHSTMZ-G1","EHWO","EHSRMZWO","EHB-51","EBLG1-2","EBEAST4A-2",
                  "EBEIJSDEN","EHMCD-2","EHMCD-2_B","EHSRMZGR1","EHSRMZWO1","EHSAFIZBDA","EHATZBDA","EHSRMZBL1","EHSAFIZBDB","EHATZBDB","EHSRMZBDB",
                  "EBLG2-2","EHTRA12","EBTSA29C","ELTSA03","EHTMZ-MAA1","EHTSA23","EHTMZ-MAA2","EHTMZ-D2","EHTMZ-D1","EDCLCN","LFFFTM","LFFFAP",
                  "LFEEXR","LFEEKR","LFEEYR","LFEEHR","LFEEUR","LFFFTE","LFFFTB","LFEEHN","LFEEUB","LFEEYB","EDGGNOR7","EDGGBOT5","EDGGNOR1","EDGGDKA3",
                  "EDGGDKA2","EDGGNOR6","EDGGEIF1","EDGGRUD5","EDVV","EDUU","EHAA","EDGG","15901","15902","ETADAOR01","EHSFRA","EHTRA12Z","LFCB1BZ","LFCB1AZ",
                  "LFFF","LFQQ7","EDCLG","EDFIS08","EDCLEN","EDDLCLE","EHMCD-1_E","EHMCD-2_E","EHSRMZBL2","EHSRMZGR2","EHMCG1","EHSRMZWO2","EBZEELAND","EHMCG2",
                  "UTA1641","UIR1640.20","EHAA@@-1","EBMAASTRIC","EHAADLG48","EHAADLG3","EHAADLG14","EHAADLG13A","EHAADLG13","EBSASKI-A","EDR117Z","EHAADLG42","EHBK2@@-1","EHAADLG29","EHAADLG18","EHAADLG35C","EHAADLG35D","EHAADLG11","LFFFCLC","LFFF@@-2","EHAADLG13C"]:
                oAs.update({"ExtOfBelgium":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoBosniaHerzegovina
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","LDDU1","LDSP4","LDSP2@@-1","LDZA2","LYBA@@-3","LYBA","LDZO","LDTR199","LDTS199","LDTR180","LDTS180","LDTR179","LDTS179","LDTR178","LDTS178","LDTR194","LDTS194","LDTR170","LDTS170","LDTR169","LDTS169","LDTR167","LDTS167","LDTR165","LDTS165","LDTR164","LDTS164","LDTR163","LDTS163","LDTR162","LDTS162","LDTR193","LDTS193",
                  "LDD199","LDD180","LDD179","LDD178","LDD194","LDD170","LDD169","LDD167","LDD165","LDD164","LDD163","LDD162","LDD193","LYBA@@-2","LDZO_D","LDSP1_D","LDZD6","LDPL6","LDOS","LDZO_C","LDDU2","LDSP1_C","LDSP1@@-1","LDZA1","LYBA@@-1","LYBE2","LYKV","LYBE1","LYPG"]:
                oAs.update({"ExtOfBosniaHerzegovina":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoBulgaria
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","LT_ACC01U","LRKOMAN1","LRKOMAN2","LRLOMOS","SEAFRA1","LT_ACC01L1","LRDINSI1","LRDINSI2","LRARGES1","LRARGES2","LYBA@@-3","LGGG","LGGG@@-1","LTBB","LWSS","LYBA","LRBB","LWSFRA","LRR167","LRR50","LGMD","LWSS@@-1","LYBA@@-2","LRBU2","LTFM11","LTFM24","LTFM26","LTFM13",
                  "LWSH","LWSU","LWST","LYBA@@-1","LYNI","LYBE1","LRBU1","LRCK"]:
                oAs.update({"ExtOfBulgaria":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoCroatia
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","LISFRAM01A","LJLA145P","LJLA165P","LJLA195P","LJLA2024P","LJLA2529P","LJLA3032P","LJLA33P","LJLA34P","LJLA35P","LJLA36P","LJLA37P","LJLA38P","LJLA3966P","LJLA085P","LJLA095P","LJLA115P","LJLA125P","LJLA135P","LJPZFRA","LJMBFRA","LJMURA1","LJMURA2","LJMURA3","LJMURA4","LJMURA5","LHWESTLP",
                  "LYBA@@-3","LYBA","LQSB","LJLA","LHCC","LJS009","LJS005","LJS008","LJPZ@@-1","LQSL","LQSU","LYBA@@-2","LJMT@@-1","LJMU","LJDO","LQMO@@-1","LQBK@@-1","LJMB2_E","LJMU_E","LJMT","LJDO1_E","LJDO1_D","LJCE","LJCE1","LJPZ@@-2","LJMO","LJMB2_D","LJMU_D","LQVK","LJDO1_C","LJUP","LJMU_C","LHCCWESTM","LHCCWESTU","LHCCWESTH","LHCC@@-1","LHCCWESTT",
                  "LYBA@@-1","LYPG","LYBE1","LYBE2","LYBT","LQBK"]:
                oAs.update({"ExtOfCroatia":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: Czechia / Tchéquie (geoCzechia)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","EPCTA05","EPX181","EPR26","EPR13","EPDLG01","LOWW8","LOWW6","LZBB-WEST","LZIB4","LZBB","LZBB@@-1","LZ_GLIDER5","LZR02",
                  "LZR01","LZBB-EAST","LZZI1","LZZI2","LZ_GLIDER7","EPKK5","EPCTA04","EPTR03A","LZTRA03","LZHL","EPTS46","EPTS45","EPTS43",
                  "EPTS42","EPTS41","EPTS40","EDCLCN","EPWWOATJR","EPWWKL","EPWWKH","EPWWJL","EPWWJH","EPWWTH","EPWWTL","EPWWOATDT","EDMMSASL","EDUUSPE12","EDUUSPE22","EDUUSAL12","EDUUSAL22","EDMMHOF","EDUUERL12","EDUUERL22","EDUUDON13","EDUUDON23","EDUUDON33","LOVVE2","LOVVE3","LOVVE4","LOVVE5","LOVVE1","LOWW_TUN","EPSFRA_P","LKAANL3","LKAANM3","LKAAMT2","LKAANL2","LKAANM2"
                  "EDMMMEI1","EDMMFRKL1","EDMMFRKL2","EDMMRDG2","EDMMRDG1","EDMMEGG1","LOWL04A","LOVVFISN03","LONO","EDLOWL04","LOVVFIST03","LOWW04","LOVVFIST04","LOWW05","LOWW_TLN1","LOVV@@-1","EDUU","LOVV","EDMM","EPWW","EPTR03AZ","LZAGLIDER5","LZAGLIDER7","EDCLG","EDFIS07","EDFIS02","EPSFIS7","EPSFIS8","LZBB-FIS","EDCLEN","EDQDCLE","LZSFRA","EPDLG71","EPDLG72","EPDLG02","EPDLG82","LZSLZIB004","LZSLZIB003","LZNPZ3"]:
                oAs.update({"ExtOfCzechia":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Denmark / Danemark (geoDenmark)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","EDR201E","EDCLCN","EDYYD5JL","EDYYD5JH","EDWWEIDE","EKDKY","ESAA2A","ESAA1","EKDK00013","EDVV","EDWW","ESAA","EDVVDLGALS","EDD101BZ","EDCLG","EDFIS04","EDCLEN","EDALSIE"]:
                oAs.update({"ExtOfDenmark":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoEstonia
            if oAs[cstKeyCatalogKeyGUId] in ["ECAC-PLUS2","ULLL","EVRR@@-1","EVTSA13Q","ULLL@@-1","EVR7","EVRRRIA3","EVRRRIA2-1","EVRREAST","EVRR","EVRA1","EVR27","EVR28","EVTSA16","EVRRCTA","EVRRRIA2P","EVRRRIA2"]:
                oAs.update({"ExtOfEstonia":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoFaroeIslands
            #if oAs[cstKeyCatalogKeyGUId] in [""]:
            #    oAs.update({"ExtOfFaroeIslands":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoFinland
            if oAs[cstKeyCatalogKeyGUId] in ["DSFAB","ESOS-K-1","ENBDE","ESAA2A","ESAA1","ECAC-PLUS2","ESTRA80P","ULLL","ENOR","ESOS1","ESAA","ENSFRAENOR","ENT111Z","ENT105Z","ENT104Z","ENT102Z","ESUPTIA","ENR402","ULR38","ESTRA80","ESR01","ENT111","ENT105","ENT104","ENT102","ULP5","ULLL@@-1","ENKR@@-1","ENBDE01","ENBDE01_C","DSFRA"]:
                oAs.update({"ExtOfFinland":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: ? (geoGermany)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","DSFAB","EHSTMZ-EEL","EHAME1","EHB-01","EHSTMZ-C1","EHMCC-1_B","EHMCC-1","EHB-26","EHATZTW","EHSRMZTW","EHSTMZ-E",
                  "EHMCE_D","EHAME2","EHMCE","EHB-27","EHB-33","EHMCD-1","EHMCD-1_B","EDLV2","EHSRMZLV","EBS27",
                  "EHBK1-1","EHBK2","EBEHBKTMA","EHSRMZBK","EHBK1","EBLG5","EBS31","EBD29","EBS29","EBS33-2","EBEAST5","EBS189","EBR04",
                  "EBLFA03","EBS178","EBHTA03B","ELLX1B","ELS05","ELS08","ELLX1A","ELLX3","TMA16213","LFR45N3","LFR45N3@@-1","LFJL4","LFR163B","LFST10",
                  "LFJL5","LFJL5.1","LFSTMZ001","LFR122","LFR150D2","LFST9","LFR150D1","LFR228B","LFR228A","LFST8",
                  "LFST-BADF","LFST-BADD","LFST-BADA","EDSB2","LFST-BADC","EDSB-F","LFST1","LFST-BADB","LFST-BADE","LFST1","LFR199","LFR322",
                  "LFR323","LFST7","LFSB09","LFSB10","LFSB08","LFSB03F","LFP36","LFSB01F","LFSB1","LFSB1S","LSZH13","LSR70","LSVTGN","EDNY2",
                  "LOCE","LOHPGBREGE","LOSTMZWIW","LOSTMZWIE","LOWI5","LOHPGKOESS","LOWS1","LOWS","LOHPGUNTER","LOTRALOWSN","LKKV","LKR1",
                  "LKMT","EPCTA05","EPDLG01","LKR2","EPSC4","EPSC3","EPSCRC","EPX003","EPSCRE","EPSC5","EDAH2","EHSRMZTW1","EHSTMZXMAL",
                  "EHSRMZLV1","ZRTBGTQ","EHTRA15","EHTRA14","EHTRA14C","EHTRA12","ZRTBGTQ","LFSB02S","LFSB3","LFSB01S","EHTMZ-D1","EHTMZ-MAA1",
                  "EHATZSV","EBTSA28A","EBTSA28B","EBTSA29B","EBTSA29C","ZRTBGTQ","EPTS40","ZRTBGTQ","FFVLLFR111","LFSB09F","LFSB10F","LFSB08F",
                  "LFSB03","LFSB01","LFSB1FS","LFSB31Z.20","LFSB02","LFSBDZZ1FS","LFSB33Z.20","LFSBDZZ2S","LFSBDZZ3S","LKAAW","LKAAWL","LKAAKV","LKAAWM","LKAAE","EPWWTH","EPWWTL","EPWWOATDT","EPWWDH","EPWWDL","EPWWBL","EPWWOATB","EPWWBH","EKDKA","EKDKUA","EKDKC","EKDKUC",
                  "LFEEE2","LFEEE3","LFEEUE","LFEEXE","LFEEKE","LFEEHE","LFEEE1","LFEESE1","LFEESE2","LFEEUH","LFEEXH","LFEEKH","LFEEHH","EPSFRA_P","LOVVFISS01","LOWI03","EDMMSTA2","LOVVFISS05","LOVVFISS07","LOWI06","LOVVW1","EDLOWS02KS","LOWS08","LOWS06","LOWS02","LOWS01",
                  "LOVVFISN07","LOVVFISN05","LOVVFISN04","LOWL04A","LONO","LOVVN1","LOVVFISN03","LKLOWL01","LKBUDEX0","LKBUDEX1","LKBUDEX2","LKBUDEX3","LKBUDEX4","LKPR-2","LKBUDEX5","LKFRAB","LKAANL1","LKAANM1","LKAANH1","LKAANT1","LKAAMT1","LKAAMT2","LKAANL2","LKAANM2",
                  "EKDK00020","EKDK00005","EKDK00009","EBLCTA","EDGGPFA5","LOVV@@-1","LSAS@@-1","EPWW","EHAA","LKAA","LOVV","LSAS","53352.2.20","53352.2","53352.1.20","53352.1","53351.1","LFBALE1.3","53351.2","LFBALE1.1","LKTRA75Z","EPTS13BZ","EKR38Z","EKD373Z",
                  "EHSFRA","EHTRA10AZ","EHTRA12Z","EHTRA12AZ","LFTR22AZ","LFFFVLLFR111","EBBU-RMZ","EBBU-TMZ","EHTRA12A","LFZRTBGTQ","LFTR22A","LFTR22B","EHTRA15A","LFEE","EBBU","LSAZ","EPSFIS7","EPSFIS4","EPSFIS5","EKDK","EKCHCTAB","EHGG","EHMCC-1_E","EHSRMZTW2","EHMCE_E","EHMCD-1_E","EHSRMZLV2",
                  "LFQU","LFST9.20","LFST8.20","LFSB35Z.20","EKCHCTAA","DSFRA","EHAA@@-1","EBUR@@-1","EBUR","UTA1641","UIR1640.20","EBMAASTRIC","EPDLG71","EHAADLG15","EHAADLG15E","EHAADLG45X","EHAADLG7","EHAADLG6A","EHAADLG20E","EHAADLG20","EDGGBOT3","EHAADLG20B","EHAADLG33","EHAADLG19D","EHAADLG19",
                  "EDGGBOT4","EHBK2@@-1","EHAADLG19B","EHAADLG41","EHAADLG42","EHAADLG23D","EHAADLG23","EHAADLG23B","EHAADLG22D","EHAADLG22B","EHAADLG22","EBTSA28CZ","EBTSA28C","LSTMZNE","LSZR@@-1","EPTR42Z","LFFFCLC","LFFF@@-2","LSASFRA1","EDYYD3WL1","EDYYD3WM","EDYYD6WH","EHAADLG48","EHAADLG35A","EHAADLG35B"]:
                oAs.update({"ExtOfGermany":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoGreece
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","LT_ACC01U","LT_ACC02U","LT_ACC02L1","LT_ACC01L1","LBSRCTA02","LBSRSD01","LBSRSD02","LBSRSD12","LBSRSD23","LBSRSD34","LBSRSD45","LBSRSD56","LBSRSD67","LBSRSD78","LBSRSD89","LBSRCTA03","LBSRSDU9","LBSRSC01","LBSRSC02","LBSRSC03","LBSRSC12","LBSRSC23","LBSRSC34","LBSRSC45","LBSRSC56","LBSRSC67",
                  "LBSRSC78","LBSRSC89","LBSRCTA01","LBSRSCU9","LTBB","LAAA","LWSS","LBSR","LWSFRA","LBD20D","LTFM12","LTFM25","LTFM26","LTFM13","LTFM11","LTFM24","LWSS@@-1","LBSFRA","LWSH","LWSU","LWST","LAAA@@-1","LASFRA","LBD20D1"]:
                oAs.update({"ExtOfGreece":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: Hungary / Hongrie (geoHungary)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","LDZO_D","LDZA1","LJMB2_D","LJMT","LJMT@@-1","LJMU_D","LJMU","LDD103","LDD104","LDD109","LDD114","LDD119","LDD129","LDD128","LDOS","LYBT","LRBU2","LRAR1","LRAR1@@-1","LRAR","LROD","LRSM","UKLVWD","UKLVWC","UKLU","LZBB-EAST","LZR55","LZBB","LZBB@@-1","LZKZ1","LZKZ","LZKZ3","LZBB-WEST","LZIB4","LZIB1","LZIB","LOWW3","LOWW2",
                  "LOSTMZWW","LOTRASPIS","LOTRASPISH","LOR16","LOWW5","LOWW7","LOTRAPINKA","LZR10","LZRUTOL","LZKZ4","LZKZ1C","LZKZ1B","LDTR103","LDTR104","LDTR109","LDTR114","LDTR119","LDTR129","LDTR128","LDTS103","LDTS104","LDTS109","LDTS114","LDTS119","LDTS129","LDTS128","LRMOPUG","LRBUDOP","LOVVE1","LOVVE2","LOVVE3","LOVVE4","LOVVE5","SEAFRA1",
                  "LDZA2","LJLA085P","LJLA095P","LJLA115P","LJLA125P","LOVVFISS16","LJMBFRA","LJMURA1","LJMURA2","LJMURA3","LJMURA4","LJMURA5","LOWG04","LOSO","LOVVS1","LOVVS2","LOVVS3","LOVVS4","LOVVS5","LOVVFIST05","LOWW_TLS","LOWW06","LOWW08","LOWW_TUS","LOVVSBOX","LOVVFIST01","LOWW03","LOVVFIST02","LOWW_TLN2","LHLESMOL1","LYBA@@-3","LOVV@@-1",
                  "UKBU","UKLV","LRBB","LYBA","LDZO","LJLA","LOVV","LZBB-FIS","LYBA@@-2","LJMU_E","LJMB2_E","LZSFRA","UKLVC","UKLVU","LRBU1","LYBA@@-1","LDZO_C","LJMU_C","LJUP","LJS008","LJNPZ2","UKLU1","LZNPZ1","LZSLZIB001","LKAMA1749","LZSLZIB003","LZSLZKZ010","LZSLZKZ002","LZSLZKZ003","LZSLZKZ005","LRR175"]:
                oAs.update({"ExtOfHungary":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones dans le territoire: geoIceland
            #if oAs[cstKeyCatalogKeyGUId] in [""]:
            #    oAs.update({"ExtOfIceland":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: Ireland / Irlande (geoIreland)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","EGPX","EGPX@@-1","EGUP","EGIS1","EGTG9"]:
                oAs.update({"ExtOfIreland":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: Italy / Italie (geoItaly)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","UTA1641","UIR1640.20","LTA130736","LTA130736.","LTA130735","LTA130735.","LTA130731","LFR221A","LFR19630","LFR19610","LFR196A2","LFMN14","LFMN13","LFR30B","LFR30C","LSAG","LSR24","LSR32","LSAZ","LSZL6","LSR62","LSR54","LSR55","LS-R11A","LSR56","LOCE","LJDT","LJDT2_D","LJDO1_D","LJDO","LJPZ","LJPZ@@-1","LJPZ@@-2","LMMMWST","LFMMMN1",
                  "LFMMMN2","LFMME1","LFMME2","LFMME3","LFMMB1","LFMMB2","LFMMB3","LFMMB4","LFMMLE11","LFMMLE12","EDUUALP13","EDUUALP23","EDUUALP33","LOVVW2","LOVVW3","LOVVW4","LOVVW5","LS-T23Z_3","LS-T23Z_1","LS-T23Z_2","LS-T23_1","LS-T23_2","LS-T53Z_1","LS-T53Z_2","LS-T53_1","LS-T53_2","LOVVFISS02","LOWI05","EDMMZUG3","EDMMSTA2","LOVVFISS01",
                  "LOWI03","EDMMTEG2","LOVVFISS06","LOVVFISS13","LOWI07","LOVVW1","LOWI04","LOVVFISS07","LOWK06","LOWK04","LJLA135P","LJLA085P","LJLA095P","LJLA115P","LJLA125P","LJLA145P","LJLA165P","LJLA195P","LJLA2024P","LJLA2529P","LJLA3032P","LJLA33P","LJLA34P","LJLA35P","LJLA36P","LJLA37P","LJLA38P","LJLA3966P","LOWK05","LJPZFRA","LOVV@@-1",
                  "LSAS@@-1","LJLA","LOVV","LSAS","LFNICE1.1","34383","34382","LS-T203Z","LS-T31Z","LS-T24Z","LS-T204Z","LS-T32Z","LS-T302Z","LS-T62+Z","LS-T602+Z","LS-T62Z","LS-T602Z","LS-T52Z","LS-T61Z","LS-T601Z","LS-T502Z","LS-T51Z","LS-T501Z","LS-R11AZ","LS-R11Z","LJS001","LJS001A","LJS003","LJS005","LJS009",
                  "LS-T203","LS-T24","LS-T204","LS-T32","LS-T302","LS-T62","LS-T602","LS-T52","LS-T502","LS-T61","LS-T601","LFMM","LOAR","LOGL","LJDO1_E","LSA9-2","LJDO1_C","LJUP","LJDT2_C","PoaffClone-1566263","LFZSM@@-6","LFVanoise","LFGdeSassiere","LFMercantour","LFContamines","LFFFCLC","LFFF@@-2","LSASFRA1","LSTMAMM1","LSTMAMM3","LSTMAMM2","LS-R16","LS-R12","LFZSM@@-6",
                  "LFCoeurduParcnationalduMercantour-1.0","LFReservenaturellenationaledesContamines-Montjoie-4.0","EDUUALP14","EDUUALP24","EDUUALP34","EDUUALP44"]:
                oAs.update({"ExtOfItaly":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoLatvia
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","ECAC-PLUS2","ULP3-2","EYVCL7","EYVCU7","EYVCL8","EYVCU8","EYVCL10","EYVCU10","EYVCL3","EYVCU3","EYVL@@-1","EYVL","UMMV","ULLL","EETT","EYSZA","EYTSA4","EER1","EETSA4Z","EETSA4A","EEVLFAS","EYP2","EYP1","ULLL@@-1","UMMS","EYVIFIS","EYPAFIS","EYSAFIS","EETTFIS","EETTFISE","EETT_G_GND","EYSA","EYVC","EYVLE","EYVLL","EYVLM","EYSFRA","EYVC@@-1","EYVLU",
                  "EYPA3","EYPA2","EYPA1","EYPA","EETTE1","EETT@@-1","EETT_FIR_C","EETTE2","EYZA","EYSA@@-1"]:
                oAs.update({"ExtOfLatvia":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: Liechtenstein (geoLiechtenstein)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","LOVVFISS02","LOVV@@-1","LOVV","LS-T51","LS-T501","LS-T40","LS-T400","LOAR","LSAZ","LSR54","LSR3"]:
                oAs.update({"ExtOfLiechtenstein":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoLithuania
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","ECAC-PLUS2","ECAC-PLUS1","EPSFRA_P","EPWWADIZ1","EPWWADIZ2","EPWWOATNE","EPWWNL","EPWWNH","EPWW","UMMV","EVRR@@-1","UMKK2","EVTIAEVLA","ULR109","EPTR108","EPTR109A","EPTR109B","EPTR110","EVR25","EVR26","EVTSA15","EVTSA17","EVTSA13G","EVTSA13Y","EVR4","EVTRA19","EPSFIS1","UMMS","UMMG2","UMMG1","UMKK","UMKK2@@-1","EVRRRIA3","EVR13","EVR12","EVRRRIA2-1","EVRRLEPL",
                  "EPTR81","EPTR80","EPTR87","EVRREAST","EVRR","EVRA1","EVRRSOUTH","EVRRCTA","EVRRRIA2P","EVRRRIA2","EVRRRIA5","EVRRLEP1","EVRRLEP3"]:
                oAs.update({"ExtOfLithuania":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: Luxembourg (geoLuxembourg)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","EDUUNTM142","EDGGPFA6","EDGGKIR5","EDUU","EDGG","53352.2.20","53352.2","53353.20","53353","LFTS200AZ1","LFTS200EZ","ETADAOR01","EBTRASBZ2","EDR305D","EDR305A","EDR205D","EDR205A","ELLXCLDB","ELS02-1","ELLX2C2","ELLXCLDA","EBS31","EBS29","EBS27","EBLFA03","EBS178","EBD29","EBHTA03B","EBLFA02","EBHTA03A","EBS33-1","EBHTA07","EBSOUTH3","TMA16214",
                  "LFR45N3","LFR45N3@@-1","ELLX3","TMA16213","EBTRA S6","EBTRA-SA","EBTSA29A","EBTSA S6","EBTSA-S6","EBTRA-S6","EBTSA29B","EDCLCN","LFEE","LFFF","EDCLG","EDFIS08","EDCLEN","EDDFCLE","ELLX2F1","ELLX2D","ELLX2B","ELLX2A","UTA1641","UIR1640.20","LFEEXR","LFEEKR","LFEEYR","LFEEHR","LFFFTM","LFFFAP","LFEEE2","LFEEE3","LFEEUE","LFEEXE","LFEEKE","LFEEHE","LFEEE1","EDUUNTM24","EDUUNTM34","EDUUNTM44",
                  "LFFFCLC","LFFF@@-2","LFTR200AZ1","LFTR200EZ"]:
                oAs.update({"ExtOfLuxembourg":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoMalta
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR"]:
                oAs.update({"ExtOfMalta":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoMoldova
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","LRDINSI1","LRDINSI2","LRBACAU","UKBU","UKOV","UKBV","UKLV","LRBB","LRBU2","UKOVCD","UKOVND","UKBVOD","UKLVWD","LRBU1","UKOVCC","UKOVNC","UKOO3","UKBVOC","UKLVC","UKLVU","UKLVWC","LRIA"]:
                oAs.update({"ExtOfMoldova":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoMontenegro
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","LDDU1","LAAA","LDZO","LQSB","LQSL","LQSU","LDZO_D","LDZO_C","LAAA@@-1","LASFRA","LATI"]:
                oAs.update({"ExtOfMontenegro":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: Netherlands / Pays-Bas (geoNetherlands)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","EBLCTA","EBHTA10B-P","EBHTA10A-P","EDGGNOR1","EDGGBOT5","EDGGNOR7","EDGGBOT1","EDGGBOT2","EDGGHMM4","EDWWEMS1","EDWWEMS6","EDWWFRI1","EDVV","EDGG","EDWW","EDGGDLGVAA","EDGGDLGVAB","ETNGSOR02","ETNGMVA04","ETNGMVA04C","ETNGMVA03","ETNGMVA03C","ETNGMVA02","ETNGMVA02C","EDGGDLGMKA","EDGGDLGMKB","ETNGMVA01","ETNGMVA01C","EDGGDLGTEB","EDGGDLGKLL",
                  "EDGGDLGKLM","EDGGDLGKLH","EDGGDLGSON","EDR202DZ","EDR302Z","EDR302BCZ","EDR302BZ","EBBU-RMZ","EBBU-TMZ","EBTRA-NA","EBTRA-N3","EBTSA-N3","EBTRA-NB","EBR07B","EDR312","EDR302C","EDR302","EDR302B","ETXJOJ","EBBU","EDCLG","EDFIS08","EDFIS05","EDFIS11","EDCLEN","EDDLCLE","EBUR@@-1","EBUR","EHSRMZNSAA","EHSTMZNSAA","EBOS2","EBOS1","EBHTA10A","EBS27","EBHTA10B","EBBR3A","EBBR2","EBBR3B",
                  "EBS168","EBS28","EBS168","EBHTA14A","EBBR7","EBBL1","EBBL1","EBBL","EBR05B","EBBL2","EBR05C","EBBL3","EBS165","EBLG3","EBEAST3","EBLG1-1","EBLG2-1","EBEAST4A-1","EHBK1-3","EBEAST4B","EHBK1-2","EHBK2","EBLG5","ETNG","EHBK2","EDDLCLCX","EDLVTMZC","EDLV1","EDLVTMZD","EDLVTMZB","EDLVCLD","EDLSPJA","EDR202D","EDR202A","EDR202E","EBR54","EBR55","EBTRA NA","EBTRA17","EDCLCN","EDYYH5RL","EDYYH5RH",
                  "EHBK3","EHVFRSSVA","EDWWDLGTWL","EDWWDLGTWM","EDWWDLGTWH"]:
                oAs.update({"ExtOfNetherlands":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoNorth-Macedonia
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","SEAFRA1","LBSRCTA01","LBSRSC03","LBSRSC01","LBSRSC02","LBSRSC12","LBSRSC23","LBSRSC34","LBSRSC45","LBSRSC56","LBSRSC67","LBSRSC78","LBSRSC89","LBSRSCU9","LYBA@@-3","LGGG","LGGG@@-1","LAAA","LBSR","LYBA","LGMD","LYBA@@-2","LBSFRA","LYNI","LYBA@@-1","LAAA","LAAA@@-1","LASFRA","LGMD"]:
                oAs.update({"ExtOfNorthMacedonia":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoNorway
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","DSFAB","EFINZ","ECAC-PLUS2","ESAA2A","ESAA1","ESAA2B","ULLL","EFIN","ESOS1","ESAA","ESMM1","EFSETFU","ESR57","ESR01","EFTSAJ30","EFTSAJ29","EFTSAJ11","EFTSAJ24","EFTSAJ25","EFTSAJ32","EFTSAJ33","EFTSAJ31","EFTSAJ34","EFTSAJ35","EFD200","ULLL@@-1","EFDLG1","EFDLG3","DSFRA","ESDLG15","ESDLG16","ESDLG17","ENKRC","ENKRW","ESOS-K-1","ESMM-4-2","ESMM-4-8","ESMM-4-9",
                  "ESDLG8","ESDLG9","ESDLG10","ESDLG11","ESDLG12","ESMM-4-7","ESDLG13","ESOS-3-1","ESOS-3-6","ESDLG14","ESOS-N-1","ESOS-N-3","ESOS-K-3","ESOS-K-2","EFTSAJ29Z","EFTSAJ11Z","EFTSAJ24Z","EFTSAJ25Z","EFTSAJ35Z","EFTSAJ33Z","EFTSAJ31Z","EFTSAJ34Z","EFTSAJ32Z","ULR42","EFTSAJ30Z","EFD300"]:
                oAs.update({"ExtOfNorway":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoSvalbard
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR"]:
                oAs.update({"ExtOfSvalbard":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: Poland / Pologne (geoPoland)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","ECAC-PLUS2","LKFRAB","LKPR-2","LKAAMT1","LKAANM1","LKAANH1","LKAANL1","LKAANT1","EDMMMEI1","EDWWDBAS1","EDWWFLG2","EDMMMEI2","EDWWDBAS2","EDWWFLG1","EDWWDBAN1","EDWWMAR2","EDWWMAR1","EDWWMRZ1","ECAC-PLUS1","EYVCL5","EYVCU5","LKAANL4","EYVL@@-1","UKBU","EDUU","UKLV","UMMV","EYVL","UMKK2","EDWW","EDMM","LKAA","LZAGLIDER7",
                  "LZBB-FIS","EDCLG","EDFIS02","EDFIS01","EYKAFIS","UMKK2@@-1","LKAMTZA3","LKAMTZA1","LKAMTZA2","LKAMTFR2","EDCLEN","EDAHCLE","LZBB@@-1","LZSFRA","UKLVC","UKLVU","EYVLM","EYVC@@-1","EYVLU","EDAH1","EDR76A","LKMT","LKR3","EPR13","LKTSA42","LKTSA43","LKTSA44","LKTSA46","LKTSA49","LKMT3","LKMT1","LKMT2","LZBB-EAST","LZBB","LZ_GLIDER7","LZTT4","LZR55","UKLU","UKLVWD",
                  "UKLVWC","UKLVED","UKLVEC","UMBB1","UMMS","UMMG1","UMMG2","EYVC","EYSFRA","EYVLL","EYVLE","UMKK","LZTT3","EDCLCN","EDUUOSE12","EDUUOSE22","EDUUHVL12","EDUUHVL22","EDWWDBDN","EDWWDBDS","EDUUSPE12","EDUUSPE22","EDMMSASL","LKAAE","LKTRA37Z","LKAASL","LKAASM","LKAASH","LKAAST","LKAAM","EPDLG03","LZNPZ1","UKLU1","LZSLZTT001","LZSLZTT008","LZSLZTT009","EDMMSAS"]:
                oAs.update({"ExtOfPoland":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: Portugal (geoPortugal)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","LECMDLG12A","LECMDLG12B","LECMDLG11","LECMDLG6","LECM@@-1","LECM","LER86C","LETRA01","LER71A-(1)","LED124","LECMFIR_G","LEBZ","LEBZ_D","LECGU","LECMUIR_C","LEBZ_C","LECM-C","LED123","LER86B","LER86A","LER71C","LER71A (1)","LECGL","LECG","LER86Z","LETRA1Z","LEFRA1","LETR1Z","LETR1"]:
                oAs.update({"ExtOfPortugal":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoRomania
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","LHEASTLP","SEAFRA1","LBSRSA01","LBSRSA02","LBSRSA12","LBSRSA23","LBSRSA34","LBSRSA45","LBSRSA56","LBSRSA67","LBSRSA78","LBSRSA89","LBSRSAU9","LBSRCTA01","LBSRCTA02","LBSRCTA07","LBSRSB01","LBSRSB02","LBSRVA02","LBSRVA04","LYBA@@-3","UKBU","LBSR","UKOV","LUUU","UKLV","LHCC","LYBA","LBD15A","LBD15B","LBD16A","LBD16B","LBD18A","LBD18B1",
                  "LUD14","LUD15","LUD1","LUD12","LUUU@@-1","LHBC","LYBA@@-2","UKOVCD","UKLVWD","UKLN","LBSFRA","UKOVCC","LUSFRA","LUKK2","UKLVC","UKLVU","UKLVWC","UKLN1","LHCCNORTHL","LHCCNORTHM","LHCCNORTHU","LHCCNORTHH","LHCC@@-1","LHCCNORTHT","LHCCEASTM","LHCCEASTU","LHCCEASTH","LHCCEASTT","LYBT","LYBA@@-1","LYBE2","LYBE1","LYVR@@-1","LUR6"]:
                oAs.update({"ExtOfRomania":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoSerbia
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","LBSRSC01","LBSRSC02","LBSRSC03","LBSRSC12","LBSRSC23","LBSRSC34","LBSRSC45","LBSRSC56","LBSRSC67","LBSRSC78","LBSRSC89","LBSRCTA01","LBSRSA02","LBSRSCU9","LBSRSA01","LBSRSA12","LBSRSA23","LBSRSA34","LBSRSA45","LBSRSA56","LBSRSA67","LBSRSA78","LBSRSA89","LBSRSAU9","LHEASTLP","LHWESTLP","LBSFTA","LRLOMOS","LRMOPUG","LWSS","LBSR","LRBB",
                  "LHCC","LDZO","LQSB","LAAA","LWSFRA","LHB35B","LRR182","LRR186","LRR170","LBD15C","LBD15A","LWSS@@-1","LBSF6_G","LBSF6","LRBU2","LQSL","LQSU","LDOS","LDZO_D","LDOS@@-1","LDOB","LAAA@@-1","LASFRA","LWSH","LWSU","LWST","LBSFRA","LBSF1","LBSF6_C","LRBU1","LRAR1","LRAR1@@-1","LHCCEASTM","LHCCEASTU","LHCCEASTH","LHCC@@-1","LHCCEASTT","LHCCWESTM","LHCCWESTU","LHCCWESTH","LHCCWESTT","LDZO_C","LHB35A"]:
                oAs.update({"ExtOfSerbia":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: Slovakia / Slovaquie (geoSlovakia)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","LOTRASPIC","LOTRASPICH","LOGLDSPITZ","LOWW2","LOTRASPIS","LOTRASPISH","LHSLESMO","LHCC","LOTRASPIN","LOTRASPINH","LHBPTMAW","LHBP2A","LHSG113/V","LHSG113/S","LHSG111","LHB19A","LHBPTMAE","LHB26","LHSG110","LHSG112","LHSG114","LHBP7","LHB31","LHCCNORTHL","LZKZ2","LHB03","UKLVWD","UKLVWC","UKLU","UKLU","EPWWADIZ3","EPR10","EPX178","EPR27","EPKK5","EPR15",
                  "EPR19","EPR8","LKMT","LKTB","LKTB3","LOWW6","LOWW4","LOWW3","EPTR174","EPTR94","LHPR","EPTR03A","EPTR03B","EPTR01A","EPTR14C","EPTR14D","EPTR15B","EPTR130A","EPTR15A","EPTR130B","LHWESTLP","LHEASTLP","EPSFRA_P","LKAAMT1","LKFRAB","LKPR-2","LOWW_TLN1","LOVVFIST03","LOWW04","LOVVFIST01","LOWW03","LOWW08","LOVVFIST02","LOWW_TLN2","LOWW_TUS","LHLESMOL2","LHLESMOP","LHLESMOU","EPWWRL","EPWWOATJR",
                  "EPWWRH","EPWWKL","EPWWKH","LKAAM","LKAASL","LKAASM","LKAASH","LKAAST","LKAATB","LOWW_TUN","LOVVE1","LOVVE2","LOVVE3","LOVVE4","LOVVE5","LOVV@@-1","UKBU","UKLV","EPWW","LKAA","LOVV","EPTR15BZ","EPTR15AZ","EPTR14DZ","EPTR14CZ","EPTR01AZ","EPTR03BZ","EPTR03AZ","LHLESMO","EPSFIS3","EPSFIS8","LKTB@@-1","UKLU@@-1","LHCCWESTM","LHCCWESTU","LHCCWESTH","LHCC@@-1","LHCCWESTT","LHCCEASTM","LHCCEASTU",
                  "LHCCEASTH","LHCCEASTT","LHCCNORTHM","LHCCNORTHU","LHCCNORTHH","LHCCNORTHT","UKLVC","UKLVU","EPTR80","UKLU1@@-1","UKLU1","LZSLZKZ014","LZSLZKZ013","LZSLZKZ015","LZSLZKZ012"]:
                oAs.update({"ExtOfSlovakia":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: Slovenia / Slovénie (geoSlovenia)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","LICTAPP7","LDZO_D","LDX81","LDPL6","LDZA3","LDD173","LDZA1","LDD160","LDD159","LDD191","LDD192","LDD190","LDD187","LDD186","LDD185","LDD184","LDX51","LDD108","LDD107","LDD101","LDD103","LHCC","LHB16","LOWG2","LOHPGPETZ1","LDTR173","LDTR160","LDTR159","LDTR191","LDTR192","LDTR190","LDTR187","LDTR186","LDTR185","LDTR184","LDTR108","LDTR107","LDTR101","LDTR103","LHTRA21A",
                  "LDTS173","LDTS160","LDTS159","LDTS191","LDTS192","LDTS190","LDTS187","LDTS186","LDTS185","LDTS184","LDTS108","LDTS107","LDTS101","LDTS103","LDPL1","SEAFRA1","LHWESTLP","LHLOWG01","LOVVS1","LOVVFISS16","LOWG04","LOSO","LOVVS2","LOVVS3","LOVVS4","LOVVS5","LOVVFISS17","LOWG03","LOWK03","LI_IS01_3","LI_IS01_4","LI_IS01_5","LI_IS01_6","LI_IS01_7","LI_IS01_8","LI_IS01_9","LI_IS01_10","LI_IS01_11","LI_IS01_12",
                  "LI_IS01_13","LI_IS01_14","LOWK07","LISFRAM01A","LOVV@@-1","LIMM@@-1","LDZO","LOVV","LIMM","LOTRAOBD","LDA81","LDA51","LICTAPP5","LDZO_C","LHCCWESTM","LHCCWESTU","LHCCWESTH","LHCC@@-1","LHCCWESTT","LIMM@@-2"]:
                oAs.update({"ExtOfSlovenia":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: Spain / Espagne (geoSpain)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","ECAC-PLUS2","GMMM1","LPSFRA1","LPDEMOSL1","LPNOL1","LPNOL2","LPCEL1","LPCEL2","LPSOL1","LPSOL2","LPR51BS1","LPR51BN1","LPPR4","LPSFRA2","LPSFRA3","LPSFRA4","LPSFRA5","LFMT14","LFMT18","LFMT18.20","LTA130753","LTA130752","LTA130751","LFBZ9.2","LFBZ9.1","LFBZ1","LFR266","LPR24C","LPABG01","LPAMU01","LPFR_B","LPTRA54","LPTRA55","LPTRA57","LP-SOU","LP-CET","LFMMML1","LFBBH1",
                  "LFBBH2","LFBBH3","LFBBH4","LFBBH5","LFBBTG","LFBBTZ","LFBBN1","LFBBN2","LFBBN3","LFBBN4","LFBBN5","LFBBZ1","LFBBZ2","LFBBZ3","LFBBZ4","LFBBZ5","GMMM@@-1","LPPC","GMMM","15936","15937","16023","16021","1598","1584","LFR108HSZ","LFR108HWZ","LFTS40Z","LFTS34CZ","LFTS34AZ","LFTS34AZ","LFTS34DZ","LFTS34BZ","LFTS34BZ","LFR108RMZ","LFR108HS","LFR108RM","LFR108HW",
                  "LFR108HW","LFTS40","LFTS34C","LFTS34B","LFTS34A","LFMM","LFBB","LFMT18.30","LFBZ9.2.20","UTA1641","UIR1640.20","LFSFRAM02","LPPRU","LP-NOM","LP-NOT","LPPC2","LPPC3","LP-CEM","LPPC4","LPPC5","LPFR_A","PoaffClone-1565957","PoaffClone-1565959","PoaffClone-1565961","LFPyreneesCoeur","LFPyreneesVAspe","LFPyreneesVOssau","LFPyreneesZ2VAzunPdeC","LFPyreneesZ3VAzunVOAM","LFPyreneesZ4VOPdLA","LFPyreneesZ6VA","LFPyreneesZ3VAzVOAM",
                  "LFPyreneesZ2VAzPdeC","LFFFCLC","LFFF@@-2","LFMMML2","LFMMM1","LFMMM2","LFMMM3","LFMMM4","LFTR40Z","LFTR40","PoaffClone-1565961","PoaffClone-1565959","PoaffClone-1565957","LFTR34CZ","LFTR34A","LFTR34AZ","LFTR34DZ","LFTR34B","LFTR34BZ","LFTR34C","LFBOAW2","LFBOAE2","LFMTFA3","LFBOAE5"]:
                oAs.update({"ExtOfSpain":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoSweden
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","ENBDC1","ENOS3","ENOS2","ENOS1","ENBDS19","ENBDCU","ENBDN","EFIN","ENOR","ENSFRAENOR","ENT138Z","ENT137Z","ENT136Z","ENS362","ENT134Z","ENT133Z","ENT132Z","ENS360","ENT131Z","ENT129Z","ENT128Z","ENT127Z","ENT125Z","ENT124Z","EFTSAJ30Z","EFTSAJ29Z","EFTSAJ11Z","EFTSAJ10Z","EFTRAJ23Z","EFTSAJ19Z","EFTRAJ19Z","EFTSAJ18Z","EFTRAJ18Z","EFTSAH31Z","EFTRAH31Z",
                  "EFTSAH39Z","EFTRAH15Z","ENR103","EFTSAJ30","EFTSAJ29","EFTSAJ11","EFTSAJ10","EFTSAJ19","EFTSAJ18","EFTSAH31","EFTRAH39","EFTSAH39","EFTRAH15","ENS625","ENS622","ENS621","ENS614","ENT138","ENT137","ENT136","ENT134","ENT132","ENT131","ENT129","ENT128","ENT125","ENT124","EFDLG1","ENBO4","ENBO3","EFKE@@-1","ENOR6_C","ENOS29","ENOR21_C","ENOR21","ENOS30","ENAREAOB","ENOR6","ENOR20_C","ENOR20","ENGM7","ENGM6","ENOR5_C",
                  "ENOR5","ENBDS11_C","ENRO1","ENBDS11","ENOR17_C","ENOR17","ENBDS19_C","ENBDS19@@-1","ENBDS18_C","ENBDS18","ENVA3","ENOR3_C","ENOR3","ENAREANO","ENAREABO","ENOR16_C","ENOR16","ENOR1","ENOR1_C","ENBDN04_C","ENBDN04","ENBDE01","ENBDE01_C","ENBDN03_C","ENBDN03","EFTRAJ23","EFTRAJ19","EFTRAJ18","EFTRAH31","ENS158","EKDK00004","EDUUALP14","EDUUALP24","EDUUALP34","EDUUALP44"]:
                oAs.update({"ExtOfSweden":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: Switzerland / Suisse (geoSwitzerland)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","LOVVFISS02","LOWI05","EDMMZUG3","LOVVFISS01","LISFRAM01A","LFSBCLD01S","17.20","LFSBCLD01S","LFSB4D","LFSB4","LFSBDZZ1D","LFSB30Z.20","LFSBCLDAZ1","LFSBCLD02","LFSBCLD02","LFSBDZZ2D","LFSB32Z.20","LFSBCLDAZ2","LFSBDZZ3DS","TMA16167","LFSBDLSW2D","LFSB23L.20","LFSBCLDSW2","LFSB01AN.2","LFSBCLD01N","LFSBCLD01N","LFSB2D","TMA161645","LFR158A","EUC25FE","LFSB07","LFSB04F","LFSB03F",
                  "LFSB02F","LFSB1","LFSB01F","LFSB18D","LFSB18C","LFSB40","LFSB40.20","LFSB02D","LFSB02A","LFSB01D2","LFSB1D2","LFSB01A","LFSB2","LFSB01D1","LFSB1D1","LSZH9","EDNYTMZA","EDNY1","LOCE","LOR18","LICTAMM1","LITMAMM5","LTA130736.","LFR30B","LTA130737","LTA130737.","LTA130736","LICTAMM18","EDCLCN","LFSB07F","LFSB1FS","LFSB01","LFMMLE2","LFEESE1","LFEESE2","LFEEUH","LFEEXH","LFEEKH","LFEEHH","EDUUALP13","EDUUALP23","EDUUALP33",
                  "LOVV@@-1","LIMM@@-1","EDUU","LIMM","LOVV","EDMM","EDGG","LFBALE2.1","LFBALE2.3","34381","34382","LIR108A","LIR108B","LFMM","LOAR","EDCLG","EDFIS09","LFEE","EDNYCLEC","EDCLEN","EDCLSBAE","LFSBCLE","LFSB23L.30","LFSB05F","LFSB12F","LICTAMM2","LICTAMM12","LICTAMM14","LICTAPP17","LICTAPP16","LFSBCLD01N@@-1","LFSBCLD02@@-1","LFSBCLD01S@@-1","UTA1641","UIR1640.20","LFSixtPassy","LFPJuraNord","LISTELVIOLOMBARDIA",
                  "LFFFCLC","LFFF@@-2","LIMM@@-2","LFBALE2.4","34390","LSZHCLCB","LSZHCLCK","LSZHCLCF","LSZHCLCG2","LSZHCLCI","LSZHCLCG1","LSZHCLCE","LSZHCLCD","LSZHCLCH","LSZHCLCJ"]:
                oAs.update({"ExtOfSwitzerland":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoUkraine
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","ECAC-PLUS2","LRDINSI1","LRDINSI2","EPSFRA_P","EPWWADIZ3","EPWWADIZ2","LRBACAU","LRNAPOC","LRBUDOP","EPWWOATJR","EPWWRL","EPWWRH","EPWWZL","EPWWZH","URRV4","URRV3","UUWV","UMMV","EPWW","LZBB","LHCC","LRBB","LUUU","EPTS03DZ","EPTS03EZ","EPTS03FZ","EPTR38BZ","EPTR120A","EPTR120B","EPTR121","EPTR122","EPTR123","EPTR124","EPTR125","EPTR126","EPTR127","EPTR128","EPTR129A","EPTR129B","EPR10",
                  "EPTR15B","LZR55","LUD12","LUD17","LUD6","LUD16","LUD14","LRBU2","LUUU@@-1","URKA","URRV1","URRV","UUWV@@-1","UMGG1","UMMS","UMBB1","EPSFIS2","EPSFIS3","LZBB-FIS","LRBU1","LRSV","LUSFRA","LUKK2","LRSM","LRTC","EPTR78","EPTR81","EPRZ4","EPTR94","LZBB-EAST","LZBB@@-1","LZSFRA","LHCCNORTHL","LHCCNORTHM","LHCCNORTHU","LHCCNORTHH","LHCC@@-1","LHCCNORTHT","LZNPZ1","LUR6"]:
                oAs.update({"ExtOfUkraine":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Jersey Guernsey (geoUkJerseyGuernsey)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR"]:
                oAs.update({"ExtOfUkJerseyGuernsey":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: United-Kingdom / Royaume-Uni (geoUnitedKingdom)
            if oAs[cstKeyCatalogKeyGUId] in ["K-FIR","EISN","EISN_C"]:
                oAs.update({"ExtOfUnitedKingdom":True})       #Exclusion volontaire sur base de l'Id

        return
