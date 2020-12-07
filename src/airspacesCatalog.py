#!/usr/bin/env python3
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
        self.oLog.info("Catalog consolidation file {0}: {1} --> {2}".format(sKeyFile, fileCatalog, oFile[poaffCst.cstSpProcessType]), outConsole=False)
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

        oGlobalAreas = self.getContent()
        oAsAreas = ofileCatalog[cstKeyCatalogCatalog]                                       #Catalogue des Espace-aériens contenus dans le fichier analysé
        barre = bpaTools.ProgressBar(len(oAsAreas), 20, title="Merge Catalog File + " + sKeyFile)
        idx = 0
        for sAsKey, oAs in oAsAreas.items():
            idx+=1
            self.isCleanArea4FreeFlight(sKeyFile, oAs)
            self.isSpecialArea4FreeFlight(sKeyFile, oAs)
            oAs.update({"nameV":aixmReader.getVerboseName(oAs)})

            #if oAs["id"] in ["FMEE1"]:
            #    print("zzz.zzz")

            if self.isValidArea(sKeyFile, oAs):                                             #Exclure certaines zones
                oAs.update({cstKeyCatalogKeySrcFile:sKeyFile})                              #Ajout de la réfénce au fichier source
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
                        self.oLog.debug("Delta add area in global catalog - ({0}){1}".format(sKeyFile, sNewKey, outConsole=False))
                    else:
                        #self.oLog.info("Ignored area (existing in global catalog) - ({0}){1}".format(sKeyFile, sNewKey, outConsole=False))
                        None
                else:
                    self.oLog.error("Process type error - {0}".format(oFile[poaffCst.cstSpProcessType], outConsole=True))

            barre.update(idx)
        barre.reset()
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
        #Contrôle de cohérence sur une clé-fonctionnelle constituée de 4 caractéristiques
        sFKeyActivObj = oAs.get("class", "") + oAs.get("type" , "") + oAs.get("lower", "") + oAs.get("upper", "")
        lIdx:int
        for lIdx in range(10):       #Contrôle sur occurence de 10 doublons envisagés
            sNewKey:str = sKey
            if lIdx > 0:
                sNewKey += cstDeduplicateSeparator + str(lIdx)
            if sNewKey in oGlobalAreas:
                oExistObj = oGlobalAreas[sNewKey]
                sFKeyExistObj = oExistObj.get("class", "") + oExistObj.get("type" , "") + oExistObj.get("lower", "") + oExistObj.get("upper", "")
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

        #Depuis le 06/10 ; Préserver les zones particulières de type Point
        if oAs.get("excludeAirspaceNotFfArea", False)==True and oAs.get("geometryType", "")!="Point":
           return False

        if sKeyFile == "BPa-Test4Clean":                #Suppression manuelle de zones
            if oAs["id"] in ["LFD18B1"]:                #Test de suppression manuelle d'une zone en mer - [Q] 18 B1 (id=LFD18B1)
                ret = False

        #elif sKeyFile == "EuCtrl":                      #Suppression manuelle de zones
            #Nota.    [D] CTR ALBERT BRAY (id=LFAQ) - a un mauvais tracé et récupération via le fichier SIA
            #if oAs["id"] in ["LFAQ"]:
            #    ret = False

        if not(ret):
            self.oLog.info("Unvalid area by manual filter - ({0}){1}".format(sKeyFile, oAs["UId"], oAs["id"], outConsole=False))
        return ret

    #Flager certaine zone 'inutile' pour la vision 'freeflight'
    def isCleanArea4FreeFlight(self, sKeyFile:str, oAs:dict) -> None:
        bClean:bool = False                                    #Default value

        #Test de suppression volontaire
        if sKeyFile == "BPa-Test4AppDelta1":
            if oAs["id"] in ["LFRD02"]:
                bClean = True

        #Fonctionnalité d'Exclusion de zones pour épurer le périmètre (non-concernées ou en mer...)
        elif sKeyFile in ["EuCtrl","SIA"]:

            #### Suppression de doublons entre fichier SIA-FR et fourniture Suisse via Eurocontrol
            if sKeyFile=="EuCtrl" and (oAs["id"] in ["LSGG","LSGG1","LSGG2","LSGG3","LSGG4","LSGG4.1","LSGG6","LSGG7","LSGG8","LSGG9","LSGG10","LFSB1F","LFSB19C","LFSB19D"]):
                bClean = True

            #Suppression de zones non-utile
            elif oAs["id"] in ["LER152","LER153"]:
                bClean = True
                #### Parc en Espagne, deja intégré dans les parcs naturels via integration FFVP
                #[R] PARQUE NACIONAL DE ORDESA Y MONTE PERDIDO NORTE (HUESCA) (id=LER152)
                #[R] PARQUE NACIONAL DE ORDESA Y MONTE PERDIDO SUR (HUESCA) (id=LER153)

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

        #Test de fonctionnalité d'Inclusion volontaire de certaines zones du territoire Français
        if sKeyFile in ["BPa-Test4Clean","BPa-Test4AppDelta1"]:
            if oAs["id"] in ["LFD16E","EBS02","LECBFIR_E"]:
                oAs.update({"ExtOfFrench":True})       #Exclusion volontaire

        #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Français (geoFrench*)
        if sKeyFile in ["EuCtrl"]:
            if oAs["id"] in ["LFST3"]:
                oAs.update({"ExtOfFrench":True})       #Exclusion volontaire sur bas de l'Id

        #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Français (geoFrench*)
        if sKeyFile in ["EuCtrl","SIA"]:
            if oAs["id"] in ["LECM C","LEBL_D","LEBL_C","LECBFIR_E","LECMFIR_E","LICTAMM4","LICTAMM7","LIR64","LSR24","LSAG","LSR23",
                  "LSR21","LSGG5","LSAZ","LSR81","LSR80","LSR26","LSR28","LSR27","EUC25SL1","EUC25SL2","LSR29","LFSB22C","LFSB80","LFSB24D",
                  "LFSB85","LFSB02S","LSR75_2","LSR75_1","LFSB1S","LFSB3","LFSB2","LFSB17D","LFSB17C","LFSB30.20","LFSB30","LFSB16D","LFSB16C",
                  "LFSB20","LFSB01A","LFSB01S","LFSB01D1","LFSB1D1","LFSB03S2","LFSB03S","LFSB03S1","LFSB04S","LFSB20.20","LFSB15C","LFSBNORD",
                  "EDTG","EDTGPJA","EDTL","EDSBCLDE","LFST1.1","EDSB1","EDSBCLDC","EDSBCLDA","EDSBCLDD","EDSBCLDF","EDR205C","EDRZRMZ",
                  "EDRZPJA","EDR205D","EDDR1","EDRJPJA","ELLXCLDB","EBBU TMZ","EBBU RMZ","ELLX1A","EBS27","EBS29","EBD29","EBS33-1","EBS177",
                  "EBD26","EBS161","ELLX5","EBSOUTH3","EBHTA06","EBHTA04A","EBFS","EBS02","EBS30","EBHTA10D","EBS182","LFQQ2","EBHTA10C",
                  "EBKT TMZ","EBKT RMZ","EBR25","EBHTA10A","EBOS1","EBLFA11","EBR24B","ETXUTE","LFST30","ELLX2F1","ELLX2F2",
                  "EGJA-2","EGJJS","EGJJ", "EGJJ1","EBS87"]:
                oAs.update({"ExtOfFrench":True})       #Exclusion volontaire sur bas de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: PWC France-Alpes, périmètre de performances (geoPWCFrenchAlps)
            if oAs["id"] in ["LSR23","LSAG","LFLL04","LFLL03","LFLL04.20","LFLL02","LFLL12"]:
                oAs.update({"ExtOfPWCFrenchAlps":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire: Massif des Alpes (geoAlps)
            if oAs["id"] in ["LHCC"]:
                oAs.update({"ExtOfAlps":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Austria / Autriche (geoAustria)
            if oAs["id"] in ["EDNYTMZB","EDNYTMZA","LSAZ","LSR43","LSR3","LSR54","LSR56","LS-VSE19","LS-VSE18","LJDO1_D","LJDO","LJDT",
                  "LJDT2_D","LJLT","LJMU_D","LJMU","LJMB2_D","LJMT","LHCC","LHB16","LHB22","LHD52","LHSLESMO","LHB18","LHB20","LZBB",
                  "LZBB-WEST","LZIB4","LZIB","LZIB2","LZR01","LKTB","LKTB4","LKR4","LKKV","LKR1","LOWSCLDA","LOWS2","LOWSCLDB","LOWSCLDD",
                  "EDR142"]:
                oAs.update({"ExtOfAustria":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Belgium / Belgique (geoBelgium)
            if oAs["id"] in ["EBUL607","EBFN","EBSASKI A","EHL179","EBR24A","LFQQ","LFQQ1","LFQQ2","LFQQ3","LFQQ4","LFQQ4.1","LFQQ5","EBR18B",
                  "LFCBA16B","LFP38","EBR18A","ELLX1A","ELLX4","TMA16214","ELLX1B","ELS06","ELS05","EDR165A","EDR117","EBEHBKTMA","EHBK1-1",
                  "EHBK2","EHSRMZBK","EHBK1","EHBK1","EHMCD-1","EHMCD-1_B","EBL179","EHSRMZBDA","EBBL2","EHSRMZBL","EHEH4","EHEH3","EHEH1","EHEH2",
                  "EHGR","EHSRMZGR","EHV-REGTEH","EHAMS2","EHV-SCHIJF","EHAMS1","EHSTMZ-G1","EHWO","EHSRMZWO","EHB-51","EBLG1-2","EBEAST4A-2",
                  "EBEIJSDEN","EHMCD-2","EHMCD-2_B"]:
                oAs.update({"ExtOfBelgium":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Czechia / Tchéquie (geoCzechia)
            if oAs["id"] in ["EPCTA05","EPX181","EPR26","EPR13","EPDLG01","LOWW8","LOWW6","LZBB-WEST","LZIB4","LZBB","LZ_GLIDER5","LZR02",
                  "LZR01","LZBB-EAST","LZZI1","LZZI2","LZ_GLIDER7","EPKK5","EPCTA04"]:
                oAs.update({"ExtOfCzechia":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Denmark / Danemark (geoDenmark)
            if oAs["id"] in ["EDR201E"]:
                oAs.update({"ExtOfDenmark":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: ? (geoGermany)
            if oAs["id"] in ["EHSTMZ-EEL","EHAME1","EHB-01","EHSTMZ-C1","EHMCC-1_B","EHMCC-1","EHB-26","EHATZTW","EHSRMZTW","EHSTMZ-E",
                  "EHMCE_D","EHAME2","EHMCE","EHB-27","EHB-33","EHMCD-1","EHMCD-1_B","EDLV2","EHSRMZLV","EBBU TMZ","EBBU RMZ","EBS27",
                  "EHBK1-1","EHBK2","EBEHBKTMA","EHSRMZBK","EHBK1","EBLG5","EBS31","EBD29","EBS29","EBS33-2","EBEAST5","EBS189","EBR04",
                  "EBLFA03","EBS178","EBHTA03B","ELLX1B","ELS05","ELS08","ELLX1A","ELLX3","TMA16213","LFR45N3","LFJL4","LFR163B","LFST10",
                  "LFJL5","LFJL5.1","EDDR-F","LFSTMZ001","LFR122","LFR150D2","LFST9","LFR150D1","LFR228B","LFR228A","EDRZ2","LFST8",
                  "LFST-BADF","LFST-BADD","LFST-BADA","EDSB2","LFST-BADC","EDSB-F","LFST1","LFST-BADB","LFST-BADE","LFST1","LFR199","LFR322",
                  "LFR323","LFST7","LFSB09","LFSB10","LFSB08","LFSB03F","LFP36","LFSB01F","LFSB1","LFSB1S","LSZH13","LSR70","LSVTGN","EDNY2",
                  "LOCE","LOHPGBREGE","LOSTMZWIW","LOSTMZWIE","LOWI5","LOHPGKOESS","LOWS1","LOWS","LOHPGUNTER","LOTRALOWSN","LKKV","LKR1",
                  "LKMT","EPCTA05","EPDLG01","LKR2","EPSC4","EPSC3","EPSCRC","EPX003","EPSCRE","EPSC5","EDAH2"]:
                oAs.update({"ExtOfGermany":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Hungary / Hongrie (geoHungary)
            if oAs["id"] in ["LDZO_D","LDZA1","LJMB2_D","LJMT","LJMU_D","LJMU","LDD103","LDD104","LDD109","LDD114","LDD119","LDD129","LDD128",
                  "LDOS","LYBT","LRBU2","LRAR1","LRAR1","LRAR","LROD","LRSM","UKLVWD","UKLVWC","UKLU","LZBB-EAST","LZR55","LZBB","LZKZ1","LZKZ",
                  "LZKZ3","LZBB-WEST","LZIB4","LZIB1","LZIB","LOWW3","LOWW2","LOSTMZWW","LOTRASPIS","LOTRASPISH","LOR16","LOWW5","LOWW7",
                  "LOTRAPINKA","LZR10","LZRUTOL"]:
                oAs.update({"ExtOfHungary":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Ireland / Irlande (geoIreland)
            #if oAs["id"] in ["aucune zone a exclure de l'Irlande"]:
            #    oAs.update({"ExtOfIreland":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Italy / Italie (geoItaly)
            if oAs["id"] in ["LTA130736.","LTA130735.","LTA130731","LFR221A","LFR19630","LFR19610","LFR196A2","LFMN14","LFMN13","LFR30B",
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
                  "EBHTA03B","EBLFA02","EBHTA03A","EBS33-1","EBHTA07","EBSOUTH3","ELLX5","ELLX4","TMA16214","LFR45N3","ELLX3","TMA16213"]:
                oAs.update({"ExtOfLuxembourg":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Netherlands / Pays-Bas (geoNetherlands)
            if oAs["id"] in ["EHSRMZNSAA","EHSTMZNSAA","EBBU TMZ","EBBU RMZ","EBOS2","EBOS1","EBHTA10A","EBS27","EBHTA10B","EBBR3A","EBBR2",
                  "EBBR3B","EBS168","EBS28","EBS168","EBHTA14A","EBBR7","EBBL1","EBBL1","EBBL","EBR05B","EBBL2","EBR05C","EBBL3","EBS165",
                  "EBLG3","EBEAST3","EBLG1-1","EBLG2-1","EBEAST4A-1","EHBK1-3","EBEAST4B","EHBK1-2","EHBK2","EBLG5","ETNG","EHBK2","EDDLCLCX",
                  "EDLVTMZC","EDLV1","EDLVTMZD","EDLVTMZB","EDLVCLD","EDLSPJA","EDR202D","EDR202A","EDR202E"]:
                oAs.update({"ExtOfNetherlands":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Poland / Pologne (geoPoland)
            if oAs["id"] in ["EDAH1","EDR76A","LKMT","LKR3","EPR13","LKTSA42","LKTSA43","LKTSA44","LKTSA46","LKTSA49","LKMT3","LKMT1","LKMT2",
                  "LZBB-EAST","LZBB","LZ_GLIDER7","LZTT4","LZR55","UKLU","UKLVWD","UKLVWC","UKLVED","UKLVEC","UMBB1","UMMS","UMMG1","UMMG2",
                  "EYVC","EYSFRA","EYVLL","EYVLE","UMKK"]:
                oAs.update({"ExtOfPoland":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Portugal (geoPortugal)
            if oAs["id"] in ["LECM C","LED123","LER86B","LER86A","LER71C","LER71A (1)","LECGL","LECG"]:
                oAs.update({"ExtOfPortugal":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Slovakia / Slovaquie (geoSlovakia)
            if oAs["id"] in ["LOTRASPIC","LOTRASPICH","LOGLDSPITZ","LOWW2","LOTRASPIS","LOTRASPISH","LHSLESMO","LHCC","LOTRASPIN","LOTRASPINH",
                  "LHBPTMAW","LHBP2A","LHSG113/V","LHSG113/S","LHSG111","LHB19A","LHBPTMAE","LHB26","LHSG110","LHSG112","LHSG114","LHBP7","LHB31",
                  "LHCCNORTHL","LZKZ2","LHB03","UKLVWD","UKLVWC","UKLU","UKLU","EPWWADIZ3","EPR10","EPX178","EPR27","EPKK5","EPR15","EPR19","EPR8",
                  "LKMT","LKTB","LKTB3","LOWW6","LOWW4","LOWW3"]:
                oAs.update({"ExtOfSlovakia":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Slovenia / Slovénie (geoSlovenia)
            if oAs["id"] in ["LICTAPP7","LDZO_D","LDX81","LDPL6","LDZA3","LDD173","LDZA1","LDD160","LDD159","LDD191","LDD192","LDD190","LDD187",
                  "LDD186","LDD185","LDD184","LDX51","LDD108","LDD107","LDD101","LDD103","LHCC","LHB16","LOWG2","LOHPGPETZ1"]:
                oAs.update({"ExtOfSlovenia":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Spain / Espagne (geoSpain)
            if oAs["id"] in ["LFMT14","LFMT18","LFMT18.20","LTA130753","LTA130752","LTA130751","LFBZ9.2","LFBZ9.1","LFBZ1","LFR266","LPR24C",
                  "LPABG01","LPAMU01","LPFR_B"]:
                oAs.update({"ExtOfSpain":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: Switzerland / Suisse (geoSwitzerland)
            if oAs["id"] in ["TMA161645","LFR158A","EUC25FE","LFSB07","LFSB04F","LFSB03F","LFSB02F","LFSB1","LFSB01F","LFSB18D","LFSB18C","LFSB40",
                  "LFSB40.20","LFSB02D","LFSB02A","LFSB01D2","LFSB1D2","LFSB01A","LFSB2","LFSB01D1","LFSB1D1","LSZH9","EDNYTMZA","EDNY1","LOCE",
                  "LOR18","LICTAMM1","LITMAMM5","LTA130736.","LFR30B","LTA130737","LTA130737.","",""]:
                oAs.update({"ExtOfSwitzerland":True})       #Exclusion volontaire sur base de l'Id

            #Fonctionnalité d'Exclusion volontaire de certaines zones des territoires: United-Kingdom / Royaume-Uni (geoUnitedKingdom)
            #if oAs["id"] in ["aucune zone a exclure de l'United-Kingdom"]:
            #    oAs.update({"ExtOfUnitedKingdom":True})       #Exclusion volontaire sur base de l'Id

        #Fonctionnalité d'Exclusion volontaire de certains Parcs naturels
        if sKeyFile=="FFVP-Parcs":
            if oAs["UId"] in ["GrandParadis","Ordessa"]:
                oAs.update({"ExtOfFrench":True})       #Exclusion volontaire sur base de l'UId

            if oAs["UId"] in ["Vanoise","GdeSassiere","Mercantour","Contamines"]:
                oAs.update({"ExtOfItaly":True})       #Exclusion volontaire sur base de l'UId

            if oAs["UId"] in ["Pyrennees"]:
                oAs.update({"ExtOfSpain":True})       #Exclusion volontaire sur base de l'UId

            if oAs["UId"] in ["Sixt"]:
                oAs.update({"ExtOfSwitzerland":True})       #Exclusion volontaire sur base de l'UId

        #Fonctionnalité d'Exclusion volontaire de certaines zones de protection d'oiseaux
        if sKeyFile=="FFVP-Birds":
            if oAs["nameV"] in ["ZSM Mercantour-Ubaye Bird Protection Tampon"]:
                oAs.update({"ExtOfItaly":True})       #Exclusion volontaire sur base du nommage verbeux

        #Fonctionnalité d'Exclusion volontaire de certaines zones de protection d'oiseaux
        if sKeyFile=="BPa-ZonesComp":
            if oAs["id"] in ["CdR-Neige"]:
                oAs.update({"ExtOfPWCFrenchAlps":True})       #Exclusion volontaire sur base de l'Id


        #Fonctionnalité spécifique pour exclusion standard et intégratrion spécifique pour la CFD
        #Les zones suivantes sont utilisées pour un affichage quasi-exaustif ou garantie des caulculs-automatisés
        if sKeyFile in ["EuCtrl","SIA"]:
            if oAs["id"] in ["FMEE1","CTA4351A.2","OCA4521.20"]:
                oAs.update({"freeFlightZone":False})
                oAs.update({"freeFlightZoneExt":False})
                oAs.update({"use4cfd":True})
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
        if sKeyFile in ["EuCtrl","SIA"] and oAs["type"]=="R":
            if oAs["id"] in ["LFR45A","LFR45B","LFR45C","LFR45D","LFR45N2","LFR45N3","LFR45N4","LFR45N5.1","LFR45N5.2","LFR45S1","LFR45S2","LFR45S3","LFR45S4","LFR45S5","LFR45S6.1","LFR45S6.2","LFR45S7","LFR45NS","LFR46A","LFR46B","LFR46C","LFR46D","LFR46E1","LFR46E2","LFR46F1","LFR46F2","LFR46F3","LFR46G","LFR46N1","LFR46N2","LFR69","LFR139","LFR142","LFR143","LFR144","LFR145","LFR147","LFR165","LFR152","LFR166A","LFR166B","LFR166C","LFR56","LFR57","LFR149A","LFR149B","LFR149D","LFR149E","LFR193A","LFR193B","LFR590A","LFR590B","LFR191A","LFR191B","LFR191C","LFR589A","LFR589B","LFR591","LFR592","LFR593A","LFR593B"]:
                oAs.update({"type":"RTBA"})
                oAs.update({"exceptSAT":True})
                oAs.update({"exceptSUN":True})
                oAs.update({"exceptHOL":True})
                #self.oLog.info("Special French-RTBA areas - ({0}){1}".format(sKeyFile, oAs["UId"], oAs["id"], outConsole=False))

        return
