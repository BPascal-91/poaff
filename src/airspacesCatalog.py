#!/usr/bin/env python3
from copy import deepcopy

import bpaTools
import aixmReader
import poaffCst

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
cstKeyCatalogKeyGUId = "GUId"                       #Identifiant global de zones ; après consolidation) de toutes les sources
cstKeyCatalogKeyAreaDesc = "areaDescription"

class AsCatalog:

    def __init__(self, oLog)-> None:
        bpaTools.initEvent(__file__, oLog)
        self.oLog                       = oLog
        self.oGlobalCatalogHeader:dict  = {}                                                              #Entête du catalogue gloabal
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

        self.oClonesCatalog:dict = {}
        oGlobalAreas = self.getContent()
        oAsAreas = ofileCatalog[cstKeyCatalogCatalog]                                       #Catalogue des Espace-aériens contenus dans le fichier analysé
        barre = bpaTools.ProgressBar(len(oAsAreas), 20, title="Merge Catalog File + " + sKeyFile)
        idx = 0
        for sAsKey, oAs in oAsAreas.items():
            idx+=1
            oAs.update({cstKeyCatalogKeySrcFile:sKeyFile})                                  #Ajout de la réfénce au fichier source

            self.isCleanArea4FreeFlight(sKeyFile, oAs)
            self.isSpecialArea4FreeFlight(sKeyFile, oAs)
            oAs.update({"nameV":aixmReader.getVerboseName(oAs)})                            #Mise a jour systématique du libellé (si chgt via fct)

            #if oAs["id"] in ["LFLL10"]:
            #    print("zzz.zzz")

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
            if oAs["id"] in ["LFD18B1"]:                    #Test de suppression manuelle d'une zone en mer - [Q] 18 B1 (id=LFD18B1)
                ret = False

        if sKeyFile in ["SIA-AIXM","BPa-Test4Clean"]:     #Suppression manuelle de zones
            #D CTR KOKSIJDE (EBFN) - Tracé Français incomplet dans le fichier SIA !
            #Suppression de nombreux tracé SIA (border with France) et en doublon avec ceux d'Eurocontrol ! donc je ne prend pas en compte l'instance SIA
            if oAs["id"] in ["TMA16213","TMA16214","UIR4831","EBFN","EB1","LFCB1A","LFCB1B","LFSTNORD","LFSTSUD","LFST1.1","LFST30","LFSB10.20","LFSBNORD","LFSB20.30","LFSB20.20","LFSB20","LFSB30.30","LFSB30",
                  "LFSB30.20","LFSB40.20","LFSB40.30","LFSB40","LFSB70.20","LFSB70","LFSB88","LFSB88.20","LFSB80.20","LFSB80","LFBALE1.2","LFSB85","LFSB85.20","LFSB82","LFSB82.20",
                  "LFSB02S","LFSB60","LFSB60.20","LFSB50","LFSB50.20","LFSB02F","LFSB3","LFSB01S","LFSB2","LFSB01A","LFSB02A",'LFSB03S',"LFSB04S"]:
                ret = False

        if sKeyFile == "EuCtrl":                         #Suppression manuelle de zones
            #Nota. [D] CTR ALBERT BRAY (id=LFAQ) - a un mauvais tracé et récupération via le fichier SIA
            #Suppression de quelques tracé Eurocontrol (recouvrement France-autre pays) dont la définition Eurocontrol n'est pas bonne par rapport a l'instance SIA
            if oAs["id"] in ["EDSB2","LFSB1F","LSGG","LSGG1","LSGG2","LSGG3","LSGG4","LSGG4.1","LSGG6","LSGG7","LSGG8","LSGG9","LSGG10"]:
                ret = False

        if not(ret):
            self.oLog.info("Unvalid area by manual filter - ({0}) id={1} UId={2} name={3}".format(sKeyFile, oAs["id"], oAs["UId"], oAs["nameV"]), outConsole=False)
        return ret

    #Flager certaine zone 'inutile' pour la vision 'freeflight'
    def isCleanArea4FreeFlight(self, sKeyFile:str, oAs:dict) -> None:
        bClean:bool = False                                    #Default value

        #Test de suppression volontaire
        if sKeyFile == "BPa-Test4AppDelta1":
            if oAs["id"] in ["LFRD02"]:
                bClean = True

        #Fonctionnalité d'Exclusion de zones pour épurer le périmètre (non-concernées ou en mer...)
        elif sKeyFile in ["EuCtrl","SIA-AIXM"]:

            #Suppression de zones non-utile
            if oAs["id"] in ["LER152","LER153","EDCLG","EPSFIS3","EPSFIS4","EPSFIS5","LSAZ","EBBU RMZ","EBBU TMZ"]:
                bClean = True
                #### Parc en Espagne, deja intégré dans les parcs naturels via integration FFVP
                #[R] PARQUE NACIONAL DE ORDESA Y MONTE PERDIDO NORTE (HUESCA) (id=LER152)
                #[R] PARQUE NACIONAL DE ORDESA Y MONTE PERDIDO SUR (HUESCA) (id=LER153)
                #### Bordure - AN G BRD - *AUID GUId=EDCLG UId=400003699424412 Id=EDCLG
                #### + les Bordures FIS - EPSFIS3,EPSFIS4,EPSFIS5 etc
                ###"EBBU RMZ" + "EBBU TMZ" - RMZ et TMZ BRUSSELS FIR (EQUIPMENT)- Supprimés car elles couvrent toute la belgique !?

            #Suppression de zones non-utile, exemple en mer ou autres cas...
            elif oAs["id"] in ["EGWO2","LFD18B1","LFD18A5","LFD18B2","LFD214","LFD16B","LFD16D","LFD31","LFD54B1","LFD54B2","LFD143B",
                    "LFML11","LFD54WB","LFR217/2","CTA47782","LFR191A","LFR108C","EGJJ2","CTA11562","LFR225","LFMD2","LFD54B3",
                    "LFR157","LFPG7.3","LFPG7.4","LFD54WA"]:
                bClean = True

        if bClean:
            oAs.update({"freeFlightZone":False})
            oAs.update({"freeFlightZoneExt":False})
            oAs.update({"excludeAirspaceByFilter":True})
            #self.oLog.info("Ignored freeflight area by manual filter - ({0}){1}".format(sKeyFile, oAs["UId"], oAs["id"], outConsole=False))
        return

    #Intégre sytematiquement certaine zone utile pour la vision 'freeflight'
    def isSpecialArea4FreeFlight(self, sKeyFile:str, oAs:dict) -> None:

        #Test de fonctionnalité d'Exclusion volontaire de certaines zones du territoire Français
        if sKeyFile in ["BPa-Test4Clean","BPa-Test4AppDelta1"]:
            if oAs["id"] in ["LFD16E","EBS02","LECBFIR_E"]:
                oAs.update({"ExtOfFrench":True})       #Exclusion volontaire

        #Traitements particuliers
        if sKeyFile in ["EuCtrl","SIA-AIXM","SIA-SUPAIP","FFVL-Protocoles","BPa-Test4AppDelta1"]:

            ### deb -Protocoles FFVL ou FFVP - Gestion spécifique des protocoles particuliers négociés par la FFVL ou la FFVP
            cstFfvlProtType:str = "FFVL-Prot"
            cstFfvpProtType:str = "FFVP-Prot"
            cstProtBase:str = "(Pascal Bazile: Voir protocole {0}) - "
            ### FFVL ###
            #Zones règlementés ou de classe D
            if oAs["id"] in ["LFR30A","LFR30B"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Massifdumontblancchamonix.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LFSRMZOH"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Protocole_La_Heve_Lejard_10_03_2017.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LFR331","LFR332A","LFR332B"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/13EME-BCA-LFR331.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LFR138","LFR138TA"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/ALVL_UCPA_E3P_Canjuers_2017.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LFLN1.4"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Protocole-TMA-2016-03-31_0.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LFR211","LFR212","LFR45D","LFR45S7"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/BA116%20protocole%20d%27accord%2013032008.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["SOCA"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/CAYENNEROCHAMBEAU.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LFAT"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/CTR_LE_TOUQUET.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LFSO","LFR92"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/BA133.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LFRD01"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/DINARD.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LFOE","LFOE1"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/BA105-VL-2018.pdf + https://federation.ffvl.fr/sites/ffvl.fr/files/Accord%20%20sites%20de%20treuils%20Quatremare%20et%20Quittebeuf.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LFRG"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Trouville_grand_bec.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LFR77A"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/convention%20base%20salon.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LFCR"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Protocole%20SNA%20-%20Comit%C3%A9%20Dept%20Vol%20libre%20Rodez%202009.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LFR55D"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/BA115-VL-2018.pdf")
                oAs.update({"codeActivity":cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            #Zones classifiés Dangereuses
            if oAs["id"] in ["LF963"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Poitiers.pdf")
                oAs.update({"name":oAs.get("name","") + " - " + cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LF889"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/TreuilEnSemaine.pdf")
                oAs.update({"name":oAs.get("name","") + " - " + cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LF8917"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/arreteMasserac.pdf")
                oAs.update({"name":oAs.get("name","") + " - " + cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LFV934TOW"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/ArretedefLaNoe%20avril%202017_0.pdf")
                oAs.update({"name":oAs.get("name","") + " - " + cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LF915", "LF916"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Accord%20%20sites%20de%20treuils%20Quatremare%20et%20Quittebeuf.pdf")
                oAs.update({"name":oAs.get("name","") + " - " + cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LFV1007TOW"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/BA105-VL-2018.pdf")
                oAs.update({"name":oAs.get("name","") + " - " + cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LF995"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Savineslelac.pdf")
                oAs.update({"name":oAs.get("name","") + " - " + cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LF9605"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Protocole.pdf")
                oAs.update({"name":oAs.get("name","") + " - " + cstFfvlProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})

            ### Cas particulier FFVL + FFVP ###
            if oAs["id"] in ["LFST1","LFST2"]:
                #Cas particulier de 2 protocoles: FFVL + FFVP !
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Strasbourg_Entzheim.pdf + https://federation.ffvl.fr/sites/ffvl.fr/files/TMA_Strasbourg.pdf")
                oAs.update({"codeActivity":cstFfvlProtType + " / " + cstFfvpProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LFRG2"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/TMA-DEAUVILLE.pdf")
                oAs.update({"codeActivity":cstFfvlProtType + " / " + cstFfvpProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LFR19610", "LFR19620", "LFR19630", "LFR196A2", "LFR196B", "LFR19660", "LFR19670", "LFR19680"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/GAPVALENSOLE.pdf")
                oAs.update({"codeActivity":cstFfvlProtType + " / " + cstFfvpProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})

            ### FFVP ###
            if oAs["id"] in ["EDSB-F","LFST-BADC","LFR199","LFST2.1","LFST1.2","LFST7","LFR197","LFR198"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/TMA_Strasbourg.pdf")
                oAs.update({"codeActivity":cstFfvpProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LFBI1","LFBI2"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Protocole_Poitiers_CTR1_et_CTR2.pdf")
                oAs.update({"codeActivity":cstFfvpProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LFOJ5.2", "LFOJ1.2", "LFOJ6.2", "LFOJ8", "LFOJ5.1"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Protocole_Orleans_2015-BA123.pdf")
                oAs.update({"codeActivity":cstFfvpProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            if oAs["id"] in ["LFBG", "CTA4721", "LFR49A1", "LFR49A2"]:
                sMsg:str = cstProtBase.format("https://federation.ffvl.fr/sites/ffvl.fr/files/Cognac_0.pdf")
                oAs.update({"codeActivity":cstFfvpProtType})
                oAs.update({"activationDesc":sMsg + oAs.get("activationDesc","")})
            ### fin - Protocoles FFVL ou FFVP

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Français (geoFrench*)
            if oAs["id"] in ["LESO", "LFST3","LECM C","LEBL","LEBL_C","LEBL_D","LEBL_G","LECBFIR_E","LECMFIR_E","LICTAMM4","LICTAMM7","LIR64","LSR24","LSAG","LSR23",
                  "LSR21","LSGG5","LSAZ","LSR81","LSR80","LSR26","LSR28","LSR27","EUC25SL1","EUC25SL2","LSR29","LFSB22C","LFSB80","LFSB24D",
                  "LFSB85","LFSB02S","LSR75_2","LSR75_1","LFSB1S","LFSB3","LFSB2","LFSB17D","LFSB17C","LFSB30.20","LFSB30","LFSB16D","LFSB16C",
                  "LFSB20","LFSB01A","LFSB01S","LFSB01D1","LFSB1D1","LFSB03S2","LFSB03S","LFSB03S1","LFSB04S","LFSB20.20","LFSB15C","LFSBNORD",
                  "EDTG","EDTGPJA","EDTL","EDSBCLDE","LFST1.1","EDSB1","EDSBCLDC","EDSBCLDA","EDSBCLDD","EDSBCLDF","EDR205C","EDRZRMZ","LFSBDZZ4","LFSBDZZ4T2",
                  "EDRZPJA","EDR205D","EDDR1","EDRJPJA","ELLXCLDB","ELLX1A","EBS27","EBS29","EBD29","EBS33-1","EBS177","EBCBA1C","LFSBCLD01N","LFSB2D",
                  "EBD26","EBS161","ELLX5","EBSOUTH3","EBHTA06","EBHTA04A","EBFS","EBS02","EBS30","EBHTA10D","EBS182","LFQQ2","EBHTA10C",
                  "EBKT TMZ","EBKT RMZ","EBR25","EBHTA10A","EBOS1","EBLFA11","EBR24B","ETXUTE","LFST30","ELLX2F1","ELLX2F2",
                  "EDCLCN","LFSBDLN","LFSBCLDSE","LFSB21L.20","LFSBDLSE","LFSBCLDSW1","LFSB22L.20","LFSBDLSW1","LFSB01AN.2",
                  "EGJA-2","EGJJS","EGJJ", "EGJJ1","EBS87","LICTAMM18","EBTRA SA","EBTRAW", "EBTRA15","EBTSA15","EBTRA WC","EBTRA WA","EBTSA27A","EBTSA27D","EBTSA27E"]:
                oAs.update({"ExtOfFrench":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: geoFrenchNESW (supprimer les LTA Pyrénées, trop lourdes pour la mémoire des Flymaster)
            if oAs["id"] in ["LTA130751","LTA130752","LTA130753"]:
                oAs.update({"ExtOfFrenchNESW":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones dans le territoire: PWC France-Alpes, périmètre de performances (geoPWCFrenchAlps)
            if oAs["id"] in ["LSR23","LSAG","LFLL04","LFLL04.20","LFLL03","LFLL02","LFLL12","LICTAMM18"]:
                oAs.update({"ExtOfPWCFrenchAlps":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Inclusion volontaire de certaines zones dans le territoire: PWC France-Alpes, périmètre de performances (geoPWCFrenchAlps)
            if oAs["id"] in ["LFLS1","TMA16161","LFV11","LTA130732"]:
                oAs.update({"IncOfPWCFrenchAlps":True})       #Inclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: Massif des Alpes (geoAlps)
            if oAs["id"] in ["LHCC","EDCLCN"]:
                oAs.update({"ExtOfAlps":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones d'Andore (geoAndorra)
            if oAs["id"] in ["LEBL_G","LEBL_D","LEBL_C"]:
                oAs.update({"ExtOfAndorra":True})           #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Austria / Autriche (geoAustria)
            if oAs["id"] in ["EDNYTMZB","EDNYTMZA","LSAZ","LSR43","LSR3","LSR54","LSR56","LS-VSE19","LS-VSE18","LJDO1_D","LJDO","LJDT",
                  "LJDT2_D","LJLT","LJMU_D","LJMU","LJMB2_D","LJMT","LHCC","LHB16","LHB22","LHD52","LHSLESMO","LHB18","LHB20","LZBB",
                  "LZBB-WEST","LZIB4","LZIB","LZIB2","LZR01","LKTB","LKTB4","LKR4","LKKV","LKR1","LOWSCLDA","LOWS2","LOWSCLDB","LOWSCLDD",
                  "EDR142","LZTRA03","EDCLCN"]:
                oAs.update({"ExtOfAustria":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Belgium / Belgique (geoBelgium)
            if oAs["id"] in ["EBUL607","EBSASKI A","EHL179","EBR24A","LFQQ","LFQQ1","LFQQ2","LFQQ3","LFQQ4","LFQQ4.1","LFQQ5","EBR18B",
                  "LFCBA16B","LFP38","EBR18A","ELLX1A","ELLX4","TMA16214","ELLX1B","ELS06","ELS05","EDR165A","EDR117","EBEHBKTMA","EHBK1-1",
                  "EHBK2","EHSRMZBK","EHBK1","EHBK1","EHMCD-1","EHMCD-1_B","EBL179","EHSRMZBDA","EBBL2","EHSRMZBL","EHEH4","EHEH3","EHEH1","EHEH2",
                  "EHGR","EHSRMZGR","EHV-REGTEH","EHAMS2","EHV-SCHIJF","EHAMS1","EHSTMZ-G1","EHWO","EHSRMZWO","EHB-51","EBLG1-2","EBEAST4A-2",
                  "EBEIJSDEN","EHMCD-2","EHMCD-2_B","EHSRMZGR1","EHSRMZWO1","EHSAFIZBDA","EHATZBDA","EHSRMZBL1","EHSAFIZBDB","EHATZBDB","EHSRMZBDB",
                  "EBLG2-2","EHTRA12","EBTSA29C","ELTSA03","EHTMZ-MAA1","EHTSA23","EHTMZ-MAA2","EHTMZ-D2","EHTMZ-D1","EDCLCN"]:
                oAs.update({"ExtOfBelgium":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Czechia / Tchéquie (geoCzechia)
            if oAs["id"] in ["EPCTA05","EPX181","EPR26","EPR13","EPDLG01","LOWW8","LOWW6","LZBB-WEST","LZIB4","LZBB","LZ_GLIDER5","LZR02",
                  "LZR01","LZBB-EAST","LZZI1","LZZI2","LZ_GLIDER7","EPKK5","EPCTA04","EPTR03A","LZTRA03","LZHL","EPTS46","EPTS45","EPTS43",
                  "EPTS42","EPTS41","EPTS40","EDCLCN"]:
                oAs.update({"ExtOfCzechia":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Denmark / Danemark (geoDenmark)
            if oAs["id"] in ["EDR201E","EDCLCN"]:
                oAs.update({"ExtOfDenmark":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: ? (geoGermany)
            if oAs["id"] in ["EHSTMZ-EEL","EHAME1","EHB-01","EHSTMZ-C1","EHMCC-1_B","EHMCC-1","EHB-26","EHATZTW","EHSRMZTW","EHSTMZ-E",
                  "EHMCE_D","EHAME2","EHMCE","EHB-27","EHB-33","EHMCD-1","EHMCD-1_B","EDLV2","EHSRMZLV","EBS27",
                  "EHBK1-1","EHBK2","EBEHBKTMA","EHSRMZBK","EHBK1","EBLG5","EBS31","EBD29","EBS29","EBS33-2","EBEAST5","EBS189","EBR04",
                  "EBLFA03","EBS178","EBHTA03B","ELLX1B","ELS05","ELS08","ELLX1A","ELLX3","TMA16213","LFR45N3","LFJL4","LFR163B","LFST10",
                  "LFJL5","LFJL5.1","EDDR-F","LFSTMZ001","LFR122","LFR150D2","LFST9","LFR150D1","LFR228B","LFR228A","EDRZ2","LFST8",
                  "LFST-BADF","LFST-BADD","LFST-BADA","EDSB2","LFST-BADC","EDSB-F","LFST1","LFST-BADB","LFST-BADE","LFST1","LFR199","LFR322",
                  "LFR323","LFST7","LFSB09","LFSB10","LFSB08","LFSB03F","LFP36","LFSB01F","LFSB1","LFSB1S","LSZH13","LSR70","LSVTGN","EDNY2",
                  "LOCE","LOHPGBREGE","LOSTMZWIW","LOSTMZWIE","LOWI5","LOHPGKOESS","LOWS1","LOWS","LOHPGUNTER","LOTRALOWSN","LKKV","LKR1",
                  "LKMT","EPCTA05","EPDLG01","LKR2","EPSC4","EPSC3","EPSCRC","EPX003","EPSCRE","EPSC5","EDAH2","EHSRMZTW1","EHSTMZXMAL",
                  "EHSRMZLV1","ZRTBGTQ","EHTRA15","EHTRA14","EHTRA14C","EHTRA12","ZRTBGTQ","LFSB02S","LFSB3","LFSB01S","EHTMZ-D1","EHTMZ-MAA1",
                  "EHATZSV","EBTSA28A","EBTSA28B","EBTSA29B","EBTSA29C","ZRTBGTQ","EPTS40","ZRTBGTQ","FFVLLFR111","LFSB09F","LFSB10F","LFSB08F",
                  "LFSB03","LFSB01","LFSB1FS","LFSB31Z.20","LFSB02","LFSBDZZ1FS","LFSB33Z.20","LFSBDZZ2S","LFSBDZZ3S"]:
                oAs.update({"ExtOfGermany":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Hungary / Hongrie (geoHungary)
            if oAs["id"] in ["LDZO_D","LDZA1","LJMB2_D","LJMT","LJMU_D","LJMU","LDD103","LDD104","LDD109","LDD114","LDD119","LDD129","LDD128",
                  "LDOS","LYBT","LRBU2","LRAR1","LRAR1","LRAR","LROD","LRSM","UKLVWD","UKLVWC","UKLU","LZBB-EAST","LZR55","LZBB","LZKZ1","LZKZ",
                  "LZKZ3","LZBB-WEST","LZIB4","LZIB1","LZIB","LOWW3","LOWW2","LOSTMZWW","LOTRASPIS","LOTRASPISH","LOR16","LOWW5","LOWW7",
                  "LOTRAPINKA","LZR10","LZRUTOL","LZKZ4","LZKZ1C","LZKZ1B","LDTR103","LDTR104","LDTR109","LDTR114","LDTR119","LDTR129","LDTR128",
                  "LDTS103","LDTS104","LDTS109","LDTS114","LDTS119","LDTS129","LDTS128"]:
                oAs.update({"ExtOfHungary":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Ireland / Irlande (geoIreland)
            #if oAs["id"] in ["aucune zone a exclure de l'Irlande"]:
            #    oAs.update({"ExtOfIreland":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Italy / Italie (geoItaly)
            if oAs["id"] in ["LTA130736","LTA130736.","LTA130735","LTA130735.","LTA130731","LFR221A","LFR19630","LFR19610","LFR196A2","LFMN14","LFMN13","LFR30B","LFR30C",
                  "LSAG","LSR24","LSR32","LSAZ","LSZL6","LSR62","LSR54","LSR55","LS-R11A","LSR56","LOCE","LJDT","LJDT2_D","LJDO1_D","LJDO",
                  "LJPZ","LJPZ"]:
                oAs.update({"ExtOfItaly":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Jersey Guernsey (geoJerseyGuernsey)
            #if oAs["id"] in ["aucune zone a exclure de l'Jersey/Guernsey"]:
            #    oAs.update({"ExtOfJerseyGuernsey":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Liechtenstein (geoLiechtenstein)
            if oAs["id"] in ["LSAZ","LSR54","LSR3"]:
                oAs.update({"ExtOfLiechtenstein":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Luxembourg (geoLuxembourg)
            if oAs["id"] in ["EDR205D","EDR205A","ELLXCLDB","ELS02-1","ELLX2C2","ELLXCLDA","EBS31","EBS29","EBS27","EBLFA03","EBS178","EBD29",
                  "EBHTA03B","EBLFA02","EBHTA03A","EBS33-1","EBHTA07","EBSOUTH3","ELLX5","ELLX4","TMA16214","LFR45N3","ELLX3","TMA16213","EBTRA S6","EBTRA SA",
                  "EBTSA29A","EBTSA S6","EBTSA29B","EDCLCN"]:
                oAs.update({"ExtOfLuxembourg":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Netherlands / Pays-Bas (geoNetherlands)
            if oAs["id"] in ["EHSRMZNSAA","EHSTMZNSAA","EBOS2","EBOS1","EBHTA10A","EBS27","EBHTA10B","EBBR3A","EBBR2",
                  "EBBR3B","EBS168","EBS28","EBS168","EBHTA14A","EBBR7","EBBL1","EBBL1","EBBL","EBR05B","EBBL2","EBR05C","EBBL3","EBS165",
                  "EBLG3","EBEAST3","EBLG1-1","EBLG2-1","EBEAST4A-1","EHBK1-3","EBEAST4B","EHBK1-2","EHBK2","EBLG5","ETNG","EHBK2","EDDLCLCX",
                  "EDLVTMZC","EDLV1","EDLVTMZD","EDLVTMZB","EDLVCLD","EDLSPJA","EDR202D","EDR202A","EDR202E","EBR54","EBR55","EBTRA NA","EBTRA17","EDCLCN"]:
                oAs.update({"ExtOfNetherlands":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Poland / Pologne (geoPoland)
            if oAs["id"] in ["EDAH1","EDR76A","LKMT","LKR3","EPR13","LKTSA42","LKTSA43","LKTSA44","LKTSA46","LKTSA49","LKMT3","LKMT1","LKMT2",
                  "LZBB-EAST","LZBB","LZ_GLIDER7","LZTT4","LZR55","UKLU","UKLVWD","UKLVWC","UKLVED","UKLVEC","UMBB1","UMMS","UMMG1","UMMG2",
                  "EYVC","EYSFRA","EYVLL","EYVLE","UMKK","LZTT3","EDCLCN"]:
                oAs.update({"ExtOfPoland":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Portugal (geoPortugal)
            if oAs["id"] in ["LECM C","LED123","LER86B","LER86A","LER71C","LER71A (1)","LECGL","LECG"]:
                oAs.update({"ExtOfPortugal":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Slovakia / Slovaquie (geoSlovakia)
            if oAs["id"] in ["LOTRASPIC","LOTRASPICH","LOGLDSPITZ","LOWW2","LOTRASPIS","LOTRASPISH","LHSLESMO","LHCC","LOTRASPIN","LOTRASPINH",
                  "LHBPTMAW","LHBP2A","LHSG113/V","LHSG113/S","LHSG111","LHB19A","LHBPTMAE","LHB26","LHSG110","LHSG112","LHSG114","LHBP7","LHB31",
                  "LHCCNORTHL","LZKZ2","LHB03","UKLVWD","UKLVWC","UKLU","UKLU","EPWWADIZ3","EPR10","EPX178","EPR27","EPKK5","EPR15","EPR19","EPR8",
                  "LKMT","LKTB","LKTB3","LOWW6","LOWW4","LOWW3","EPTR174","EPTR94","LHPR","EPTR03A","EPTR03B","EPTR01A","EPTR14C","EPTR14D","EPTR15B",
                  "EPTR130A","EPTR15A","EPTR130B"]:
                oAs.update({"ExtOfSlovakia":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Slovenia / Slovénie (geoSlovenia)
            if oAs["id"] in ["LICTAPP7","LDZO_D","LDX81","LDPL6","LDZA3","LDD173","LDZA1","LDD160","LDD159","LDD191","LDD192","LDD190","LDD187",
                  "LDD186","LDD185","LDD184","LDX51","LDD108","LDD107","LDD101","LDD103","LHCC","LHB16","LOWG2","LOHPGPETZ1","LDTR173","LDTR160",
                  "LDTR159","LDTR191","LDTR192","LDTR190","LDTR187","LDTR186","LDTR185","LDTR184","LDTR108","LDTR107","LDTR101","LDTR103","LHTRA21A",
                  "LDTS173","LDTS160","LDTS159","LDTS191","LDTS192","LDTS190","LDTS187","LDTS186","LDTS185","LDTS184","LDTS108","LDTS107","LDTS101",
                  "LDTS103"]:
                oAs.update({"ExtOfSlovenia":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Spain / Espagne (geoSpain)
            if oAs["id"] in ["LFMT14","LFMT18","LFMT18.20","LTA130753","LTA130752","LTA130751","LFBZ9.2","LFBZ9.1","LFBZ1","LFR266","LPR24C",
                  "LPABG01","LPAMU01","LPFR_B","LPTRA54","LPTRA55","LPTRA57"]:
                oAs.update({"ExtOfSpain":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Switzerland / Suisse (geoSwitzerland)
            if oAs["id"] in ["LFSBCLD01S","17.20","LFSBCLD01S","LFSB4D","LFSB4","LFSBDZZ1D","LFSB30Z.20","LFSBCLDAZ1","LFSBCLD02","LFSBCLD02","LFSBDZZ2D",
                  "LFSB32Z.20","LFSBCLDAZ2","LFSBDZZ3DS","TMA16167","LFSBDLSW2D","LFSB23L.20","LFSBCLDSW2","LFSB01AN.2","LFSBCLD01N","LFSBCLD01N","LFSB2D",
                  "TMA161645","LFR158A","EUC25FE","LFSB07","LFSB04F","LFSB03F","LFSB02F","LFSB1","LFSB01F","LFSB18D","LFSB18C","LFSB40","LFSB40.20","LFSB02D",
                  "LFSB02A","LFSB01D2","LFSB1D2","LFSB01A","LFSB2","LFSB01D1","LFSB1D1","LSZH9","EDNYTMZA","EDNY1","LOCE","LOR18","LICTAMM1","LITMAMM5",
                  "LTA130736.","LFR30B","LTA130737","LTA130737.","LTA130736","LICTAMM18","EDCLCN","LFSB07F","LFSB1FS","LFSB01"]:
                oAs.update({"ExtOfSwitzerland":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: United-Kingdom / Royaume-Uni (geoUnitedKingdom)
            #if oAs["id"] in ["aucune zone a exclure de l'United-Kingdom"]:
            #    oAs.update({"ExtOfUnitedKingdom":True})       #Exclusion volontaire sur base de l'Id

        #Fonctionnalité d'Exclusion volontaire de certains Parcs naturels
        if sKeyFile=="BPa-Parcs":
            #Fonctionnalité d'Inclusion volontaire de certaines zones dans le territoire: PWC France-Alpes, périmètre de performances (geoPWCFrenchAlps)
            if oAs["id"] in ["Vercors","Ecrins"]:
                oAs.update({"IncOfPWCFrenchAlps":True})     #Inclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusions volontaires...
            if oAs["id"] in ["GRANPARADISO","Ordessa"]:
                oAs.update({"ExtOfFrench":True})            #Exclusion volontaire sur base de l'UId

            if oAs["id"] in ["Vanoise","GdeSassiere","Mercantour","Contamines"]:
                oAs.update({"ExtOfItaly":True})             #Exclusion volontaire sur base de l'UId

            if oAs["id"] in ["PyreneesCoeur","PyreneesVAspe","PyreneesVOssau","PyreneesZ2VAzunPdeC","PyreneesZ3VAzunVOAM","PyreneesZ4VOPdLA","PyreneesZ6VA"]:
                oAs.update({"ExtOfSpain":True})             #Exclusion volontaire sur base de l'UId

            if oAs["id"] in ["SixtPassy","PJuraNord","STELVIOLOMBARDIA"]:
                oAs.update({"ExtOfSwitzerland":True})       #Exclusion volontaire sur base de l'UId

        #Fonctionnalité d'Exclusion volontaire de certaines zones de protection d'oiseaux
        if sKeyFile=="FFVP-Birds":
            if oAs["nameV"] in ["ZSM Mercantour-Ubaye Bird Protection Tampon"]:
                oAs.update({"ExtOfItaly":True})       #Exclusion volontaire sur base du nommage verbeux

        #Fonctionnalité d'Exclusion volontaire de certaines zones de protection d'oiseaux
        if sKeyFile=="BPa-ZonesComp":
            if oAs["id"] in ["LFRoseland-Neige"]:
                oAs.update({"ExtOfPWCFrenchAlps":True})       #Exclusion volontaire sur base de l'Id

        #Fonctionnalité spécifique pour exclusion standard et intégratrion spécifique pour la CFD
        #Les zones suivantes sont utilisées pour un affichage quasi-exaustif ou garantie des caulculs-automatisés
        if sKeyFile in ["EuCtrl","SIA-AIXM"]:
            if oAs["id"] in ["FMEE1","CTA4351A.2","OCA4521.20"]:
                oAs.update({"freeFlightZone":False})
                oAs.update({"freeFlightZoneExt":False})
                oAs.update({"use4cfd":True})
                oAs.update({"excludeAirspaceByFilter":True})
                #[E] TMA LA REUNION 1 (id=FMEE1)
                #[E] CTA PIARCO A.20 (id=CTA4351A.2)
                #[E] OCA TAHITI.20 (id=OCA4521.20)

        #Test pour test de flag sur une RTBA (SIA France, ne sont jamais activées les samedis/dimanches et jours fériés)
        if sKeyFile in ["BPa-TestRefAlt"] and oAs["type"]=="R":
            if oAs["id"] in ["Test4"]:
                oAs.update({"type":"RTBA"})
                oAs.update({"exceptSAT":True})
                oAs.update({"exceptSUN":True})
                oAs.update({"exceptHOL":True})

        #Toutes les RTBA du SIA France, ne sont jamais activées les samedis/dimanches et jours fériés
        if sKeyFile in ["EuCtrl","SIA-AIXM"] and oAs["type"]=="R":
            if oAs["id"] in ["LFR45A","LFR45B","LFR45C","LFR45D","LFR45N2","LFR45N3","LFR45N4","LFR45N5.1","LFR45N5.2","LFR45S1","LFR45S2","LFR45S3","LFR45S4","LFR45S5","LFR45S6.1","LFR45S6.2","LFR45S7","LFR45NS","LFR46A","LFR46B","LFR46C","LFR46D","LFR46E1","LFR46E2","LFR46F1","LFR46F2","LFR46F3","LFR46G","LFR46N1","LFR46N2","LFR69","LFR139","LFR142","LFR143","LFR144","LFR145","LFR147","LFR165","LFR152","LFR166A","LFR166B","LFR166C","LFR56","LFR57","LFR149A","LFR149B","LFR149D","LFR149E","LFR193A","LFR193B","LFR590A","LFR590B","LFR191A","LFR191B","LFR191C","LFR589A","LFR589B","LFR591","LFR592","LFR593A","LFR593B"]:
                oAs.update({"type":"RTBA"})
                oAs.update({"exceptSAT":True})
                oAs.update({"exceptSUN":True})
                oAs.update({"exceptHOL":True})
                #self.oLog.info("Special French-RTBA areas - ({0}){1}".format(sKeyFile, oAs["UId"], oAs["id"], outConsole=False))

        #LTA - Traitements spécifiques pour construction des zones d'extention de vol libre
        if sKeyFile in ["SIA-SUPAIP","BPa-FrenchSS","SIA-AIXM","EuCtrl","BPa-Test4AppDelta1"] and oAs["type"]=="LTA":

            #Filtrage volontaire 'vfrZone' et 'freeFlightZone' de la base officielle de la surface S en France (car la nouvelle 'surface S' est spécifiquement retracée par BPascal)
            if oAs["id"] in ["LTA13071"]:
                #Id=LTA13071 - AN LTA FRANCE 1 Lower(3000FT AGL-FL115)
                oAs.update({"groupZone":True})          #Utile pour suppression au niveau des toutes sorties (y compris 'ifr')
                oAs.update({"vfrZone":False})
                oAs.update({"vfrZoneExt":False})
                oAs.update({"freeFlightZone":False})
                oAs.update({"freeFlightZoneExt":False})
                oAs.update({"excludeAirspaceByFilter":True})

            ##Maintien volontaire des bases officielles classée 'E' de la surface S en France
            #if oAs["id"] in ["LTA130732.","LTA130733.","LTA130734.","LTA130735.","LTA130736.","LTA130737.","LTA130741."]:
            #    #Id=LTA130732. - AC E - AN LTA FRANCE 3 ALPES 2.20 Lower(3000FT AGL-FL115) / *AAlt ["3000FT AGL-FL115/FL125", "3505m/3810m", "ffExt=Yes"]
            #    #Id=LTA130733. - AC E - AN LTA FRANCE 3 ALPES 3.20 Lower(3000FT AGL-FL115) / *AAlt ["3000FT AGL-FL115/FL145", "3505m/4419m", "ffExt=Yes"]
            #    #Id=LTA130734. - AC E - AN LTA FRANCE 3 ALPES 4.20 Lower(3000FT AGL-FL115) / *AAlt ["3000FT AGL-FL115/FL125", "3505m/3810m", "ffExt=Yes"]
            #    #Id=LTA130735. - AC E - AN LTA FRANCE 3 ALPES 5.20 Lower(3000FT AGL-FL115) / *AAlt ["3000FT AGL-FL115/FL175", "3505m/5334m", "ffExt=Yes"]
            #    #Id=LTA130736. - AC E - AN LTA FRANCE 3 ALPES 6.20 Lower(3000FT AGL-FL115) / *AAlt ["3000FT AGL-FL115/FL175", "3505m/5334m", "ffExt=Yes"]
            #    #Id=LTA130737. - AC E - AN LTA FRANCE 3 ALPES 7.20 Lower(3000FT AGL-FL115) / *AAlt ["3000FT AGL-FL115/FL135", "3505m/4114m", "ffExt=Yes"]
            #    #Id=LTA130741. - AC E - AN LTA FRANCE 4.20 Lower(3000FT AGL-FL115) / *AAlt ["3000FT AGL-FL115/FL135", "3505m/4114m", "ffExt=Yes"]

            #Construction volontaire 'freeFlightZone' des clônes de certaines zones pour constituer la surface S en France
            if oAs["id"] in ["LTA130731","LTA130751","LTA130752","LTA130753"]:
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
                    self.oClonesCatalog.update({sNewKey:oClone})         #Ajoute ce clône zone au catalogue des objets clonés

                """
                #Phase 2 - Exclusion volontaire 'freeFlightZone' de la zone d'origine
                oAs.update({"freeFlightZone":False})
                oAs.update({"freeFlightZoneExt":False})
                oAs.update({"excludeAirspaceByFilter":True})
                """

        return
