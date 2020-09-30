#!/usr/bin/env python3
import bpaTools
import aixmReader
import poaffCst

####  Constantes de paramétrage des catalogues  ####
cstDeduplicateSeparator = "@@-"
cstKeyCatalogType = "type"
cstKeyCatalogHeaderFile = "headerFile"
cstKeyCatalogCatalog = "catalog"
cstKeyCatalogSoftware = "software"
cstKeyCatalogCreated = "created"
cstKeyCatalogContent = "content"

cstKeyCatalogNbAreas = "numberOfAreas"
cstKeyCatalogSrcFiles = "srcFiles"
cstKeyCatalogSrcFile = "srcFile"
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

    def addSrcFile(self, sKeyFile:str, sFile:str, sOrigin:str, sVersion:str, sCreated:str) -> None:
        oCatalogFile:dict = {}                                      #Description du fichier analysé
        oCatalogFile.update({cstKeyCatalogSrcFile:sFile})        #Nom du fichier analysé
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

        oHeadFile = ofileCatalog[cstKeyCatalogHeaderFile]                                                #Entête concernant le fichier analysé

        self.oGlobalCatalogHeader:dict = {}                                                              #Entête du catalogue gloabal
        if self.oGlobalCatalog=={}:                                                                      #Catalogue vde, donc initialisation du catalogue gloabal
            self.oGlobalCatalog.update({cstKeyCatalogType:ofileCatalog[cstKeyCatalogType]})              #Typage du catalogue
            self.oGlobalCatalogHeader.update({cstKeyCatalogSoftware:oHeadFile[cstKeyCatalogSoftware]})   #Référence au soft de construction
            self.oGlobalCatalogHeader.update({cstKeyCatalogCreated:oHeadFile[cstKeyCatalogCreated]})     #Heurodatage de la construction
            self.oGlobalCatalogHeader.update({cstKeyCatalogContent:oHeadFile[cstKeyCatalogContent]})     #Déclaration du contenu
            self.oGlobalCatalog.update({cstKeyCatalogHeaderFile:self.oGlobalCatalogHeader})              #Ajout de l'entête de catalogue
        else:
            self.oGlobalCatalogHeader = self.oGlobalCatalog[cstKeyCatalogHeaderFile]                     #Entête du catalogue gloabal

        self.addSrcFile(sKeyFile, \
                        oHeadFile[cstKeyCatalogSrcFiles]["1"]["srcAixmFile"], \
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
        ret:bool = True                                                  #Default value
        if oAs["groupZone"]:                           return False     #Exclure les zones de regroupement
        if oAs.get("excludeAirspaceNotCoord",False):   return False     #Exclure les zones sans précision de coordonnées
        if oAs.get("excludeAirspaceNotFfArea",False):  return False      #Exclure les zones sans précision de coordonnées

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

            #Exclusion volontaire pour différentes causes
            if sKeyFile=="EuCtrl" and (oAs["id"] in ["EBS27","LSGG1","LSGG2","LSGG3","LSGG4","LSGG4.1","LSGG6","LSGG7","LSGG8","LSGG9","LSGG10","LSGG","LFSB1F","LFSB19C","LFSB19D"]):
                bClean = True
                #### Très mauvais tracé (il manque les bordure de frontières Blegique-PaysBas)
                #[W] LOW FLYING AREA GOLF ONE (R / GLIDER / SeeNotam / id=EBS27)
                #### Suppression de doublons entre fichier SIA-FR et fourniture Suisse via Eurocontrol
                #[D] GENEVA (CTR / id=LSGG)
                #[C] GENEVE TMA1 (TMA / id=LSGG1)
                #[C] GENEVE TMA2 (TMA / id=LSGG2)
                #[C] GENEVE TMA3 (TMA / id=LSGG3)
                #[C] GENEVE TMA4 (TMA / id=LSGG4)
                #[C] GENEVE TMA4.1 (TMA / id=LSGG4.1)
                #[C] GENEVE TMA6 (TMA / id=LSGG6)
                #[C] GENEVE TMA7 (TMA / id=LSGG7)
                #[C] GENEVE TMA8 (TMA / id=LSGG8)
                #[C] GENEVE TMA9 (TMA / id=LSGG9)
                #[C] GENEVE TMA10 (TMA / id=LSGG10)
                #(Eurocontrol)[D] CTR BALE FRANCAISE (id=LFSB1F) est en doublon avec (SIA)id=LFSB1 (id sans le 'F')
                #(Eurocontrol)[C] TMA BALE PARTIE DELEG.ZURICH-AZ1 C (id=LFSB19C) en doublon avec (SIA)id=LFSB50
                #(Eurocontrol)[D] TMA BALE PARTIE DELEG.ZURICH-AZ1 D (id=LFSB19D) en doublon avec (SIA)id=LFSB50.20

            #Suppression de zones non-utile
            elif oAs["id"] in ["LECM C","LECMFIR_E","LECBFIR_E","LSAZ","LER152","LER153"]:
                bClean = True
                #[C] ZURICH (CTA / id=LSAZ)
                #### Parc en Espagne, deja intégré dans les parcs naturels via integration FFVP
                #[R] PARQUE NACIONAL DE ORDESA Y MONTE PERDIDO NORTE (HUESCA) (id=LER152)
                #[R] PARQUE NACIONAL DE ORDESA Y MONTE PERDIDO SUR (HUESCA) (id=LER153)
                #LECBFIR_E - E BARCELONA FIR
                #LECMFIR_E - E MADRID FIR
                #LECM C - PART MADRID FIR CLASS C

                
            #Suppression de zones non-utile, exemple en mer ou autres cas...
            elif oAs["id"] in ["LEVASC11","EBBU RMZ","EBBU TMZ","LFR13B1","LFD18B1","LFD18A5","LFD214","LFD16D","LFD18B2","LFD31","LFD32","OCA4521.20","EISOA","LICTARR2","DTKA","LID40A","LID40B","LID91","LID91BIS","LFMN3","LFD54C1","LFD54C2","LFD54B1","LFD54B2","LFD54WC","LFD143B","LFML11","LFD54WB","LFD121","LFD142","LFD108","LFD143A","LFR217/2","CTA47782","LSAG","LFR191A",R"LFR108C","LECP_A","LECP","LFD33","LFD16A","LFD16B","LFD16C","LFD16E","EGD008A","EGD008B","EGD003","EGD004","EGJJ1S","CTA11561","EGJA-1","EGJJN","EGJJ1N","EGJJ2","CTA11562","EGTE5","EGTE4","EGD013","EGD017","EGD023","EGVF5","EGVF4","EGVF3","EGD036","EGD038","EGD039","EGD040","EGWO6","EGWO2","EGWO1","EGWO3","LID67","LFD67","CTA4351A.2","FM50"]:
                bClean = True
                #### Zone en mer ou autres...
                #[Q] SORT (LLEIDA) (ASCENT / id=LEVASC11)
                #[A] PALMA TM (id=LECP_A)
                #[C] PALMA TMA (RMZ) (TMA / id=LECP)
                #[R] BRUSSELS FIR (RMZ / EQUIPMENT / id=EBBU RMZ)
                #[P] BRUSSELS FIR (TMZ / EQUIPMENT / id=EBBU TMZ)
                #[Q] 18 B1 (id=LFD18B1)
                #[Q] 18 A5 (id=LFD18A5)
                #[Q] 214 (SeeNotam / id=LFD214)
                #[Q] 16 D (SeeNotam / id=LFD16D)
                #[Q] 18 B2 (id=LFD18B2)
                #[Q] 31 D (id=LFD31)
                #[Q] 32 (id=LFD32)
                #[Q] 33 (id=LFD33)
                #[A] SHANNON OCEANIC TRANSITION AREA (SOTA) (id=EISOA)
                #[D] ZONA '2' (CTA / id=LICTARR2)
                #[C] TUNIS CTA NORTH WEST (CTA / id=DTKA)
                #[Q] LI D40/A - DECIMOMANNU (id=LID40A)
                #[Q] LI D40/B - CAGLIARI (id=LID40B)
                #[Q] LI D91 - MAR LIGURE (id=LID91)
                #[Q] LI D91/BIS - LIGURIA (id=LID91BIS)
                #[D] NICE 3 (TMA / id=LFMN3)
                #[Q] 54 C1 (id=LFD54C1)
                #[Q] 54 C2 (id=LFD54C2)
                #[Q] 54 B1 (id=LFD54B1)
                #[Q] 54 B2 (id=LFD54B2)
                #[Q] 54 WC (id=LFD54WC)
                #[Q] 143 B (id=LFD143B)
                #[D] PROVENCE 11 (TMA / id=LFML11)
                #[Q] 54 WB (id=LFD54WB)
                #[Q] 121 (id=LFD121)
                #[Q] 142 (id=LFD142)
                #[Q] 108 E (id=LFD108)
                #[Q] 143 A (id=LFD143A)
                #[R] 217 /2 (id=LFR217/2)
                #[D] RHONE 2 (CTA / id=CTA47782)
                #[C] GENEVA (CTA / id=LSAG)
                #[R] 191 A (SeeNotam / id=LFR191A)
                #[R] 108 C (id=LFR108C)
                #[Q] 16 A (SeeNotam / id=LFD16A)
                #[Q] 16 B (SeeNotam / id=LFD16B)
                #[Q] 16 C (SeeNotam / id=LFD16C)
                #[Q] 16 E (SeeNotam / id=LFD16E)
                #[Q] PLYMOUTH (id=EGD008A)
                #[Q] PLYMOUTH (id=EGD008B)
                #[Q] PLYMOUTH (id=EGD003)
                #[Q] PLYMOUTH (id=EGD004)
                #[C] CHANNEL ISLANDS CTA 1 SOUTH (CTA / id=EGJJ1S)
                #[D] ILES ANGLO-NORMANDES 1 (CTA / id=CTA11561)
                #[D] CHANNEL ISLANDS CTR NORTH (CTR / id=EGJA-1)
                #[C] CHANNEL ISLANDS TMA NORTH (TMA / id=EGJJN)
                #[C] CHANNEL ISLANDS CTA 1 NORTH (CTA / id=EGJJ1N)
                #[C] CHANNEL ISLANDS CTA 2 (CTA / id=EGJJ2)
                #[D] ILES ANGLO-NORMANDES 2 (CTA / id=CTA11562)
                #[C] BERRY HEAD CTA 5 (CTA / id=EGTE5)
                #[C] BERRY HEAD CTA 4 (CTA / id=EGTE4)
                #[Q] LYME BAY (id=EGD013)
                #[Q] PORTLAND (id=EGD017)
                #[Q] PORTLAND (id=EGD023)
                #[C] PORTSMOUTH CTA 5 (CTA / id=EGVF5)
                #[C] PORTSMOUTH CTA 4 (CTA / id=EGVF4)
                #[C] PORTSMOUTH CTA 3 (CTA / id=EGVF3)
                #[Q] PORTSMOUTH (id=EGD036)
                #[Q] PORTSMOUTH (id=EGD038)
                #[Q] PORTSMOUTH (id=EGD039)
                #[Q] PORTSMOUTH (id=EGD040)
                #[C] WORTHING CTA 6 (CTA / id=EGWO6)
                #[C] WORTHING CTA 2 (CTA / id=EGWO2)
                #[C] WORTHING CTA 1 (CTA / id=EGWO1)
                #[C] WORTHING CTA 3 (CTA / id=EGWO3)
                #[Q] LI D67 - SOLENZARA (FRANCIA - FRANCE) (SeeNotam / id=LID67)
                #[Q] 67 (SeeNotam / id=LFD67)
                #[Q] 50 (SeeNotam / id=FM50)

        if bClean:
            oAs.update({"freeFlightZone":False})
            oAs.update({"freeFlightZoneExt":False})
            oAs.update({"excludeAirspaceByFilter":True})
            #self.oLog.info("Ignored freeflight area by manual filter - ({0}){1}".format(sKeyFile, oAs["UId"], oAs["id"], outConsole=False))
        return

    #Intégre sytematiquement certaine zone utile pour la vision 'freeflight'
    def isSpecialArea4FreeFlight(self, sKeyFile:str, oAs:dict) -> None:

        #Test de fonctionnalité d'Inclusion volontaire de certaines zones du territoire Français
        if sKeyFile == "BPa-Test4Clean":
            if oAs["id"] in ["LFD16E"]:
                oAs.update({"ExtOfFrensh":True})       #Exclusion volontaire

        #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire Français
        elif sKeyFile in ["EuCtrl","SIA"]:
            if oAs["id"] in ["LIEA","LICTASA2","LICTASA4","LICTASA5","LICTASA7","LICTASA6","LIP218","LIP170","LIMJ2","LICTAMM9","LIR64BIS","LIMF3","LIMF4","LIMF5","LSR22","LSVLAVAUX","LSVBEGNINS","EBOS1","LS-R4A","EUC25SLP","LFSB04S","LFSB03S1","LFSB03S","LFSB03S2","LSR75_1","LSR75_2","LFSB88","LFSB25D","LFSB82","LFSB23D","LSR33","LSXGOESGEN","LSR76","LFSB02D","LFSB02A","LFSB40.20","LFSB40","LFSB18C","LFSB18D","LFSB70","LFSB21C","LSZH8","EDTFPJA","EDTF","EDSBCLDH","ED0004","ELS02-2","EBS80","EBR41","EBS136","EBLFA01","EBR06B","EBS153","EBS92","EBCI","EBR22","EBCI1","EBSOUTH1","EBCV","EBBR2", "EBBR3A","EBS103","EBR70","EBS120","EBS109","EBS14","EBS73","EBS105","EBS113","EB1","EBCBA1C","EBS180","EBR08","EBR24A","EUC25SL2","LED67","LED8","LEBL_C","LEBL_D","LEPP","LICTAMM4","LICTAMM7","LIR64","LSR24","LSR23","LSR21","LSR81","LSR80","LSR26","LSGG5","LSR28","LSAG","EUC25SL1","LSR27","LSR29","LFSB85","LFSB24D","LFSB80","LFSB22C","LFSB02S","LFSB60.20","LFSB60","LFSB20C","LFSB20D","LFSB3","LFSB01S","LFSB1S","LFSB2","LFSB1D1","LFSB01A","LFSB01D1","LFSB30","LFSB30.20","LFSB17C","LFSB17D","LFSB20.20","LFSB20","LFSB16C","LFSB16D","EDTG","EDTGPJA","LFSBNORD","LFSB15C","EDTLPJA","EDTL","LFST30","EDSBCLDG","EDSBCLDE","EDSBCLDB","LFST1.1","EDSBCLDC","EDSB1","EDSBCLDA","EDSBCLDD","EDSBCLDF","EDRZPJA","EDRZRMZ","EDR205C","EDDR1","EDRJPJA","ETXUTE","EDR205D","ELLX2F2","ELLX2F1","ELLXCLDB","ELLX","ELLX1A","ELLX5","EBS63","EBS154","EBSOUTH3","EBLFA06","EBHTA06","EBS161","EBS177","EBD26","EBLFA04","EBHTA04A","EBS86","EBS29","EBS33-1","EBD29","EBFS","EBS128","EBS61","EBS87","EBS65","EBS02","EBS182","LFQQ2","EBHTA10A","EBLFA11","EBHTA10C","EBKT TMZ","EBKT RMZ","EBS30","EBR25","EBR24B","EBHTA10D"]:
                oAs.update({"ExtOfFrensh":True})       #Exclusion volontaire sur bas de l'Id
                #LIEA - CTR ALGHERO
                #LICTASA2 - CTA ZONA '2'D
                #LICTASA4 - CTA ZONA '4'
                #LICTASA5 - CTA ZONA '5'
                #LICTASA7 - CTA ZONA '7'
                #LICTASA6 - CTA ZONA '6'
                #LIP218 - P LI P218 - SANREMO
                #LIP170 - P LI P170 - IMPERIA
                #LIMJ2 - CTR ZONA/ZONE '2'
                #LICTAMM9 - CTA ZONA '9'
                #LIR64BIS - R LI R64/BIS - BARGE
                #LIMF3 - CTR ZONA/ZONE '3'
                #LIMF4 - CTR ZONA/ZONE '4'
                #LIMF5 - CTR ZONA/ZONE '5'
                #LSR22 - R BERNER OBERLAND
                #LSVLAVAUX - Q LAVAUX (ANTIHAIL)
                #LSVBEGNINS - Q BEGNINS (ANTIHAIL)
                #LS-R4A - R LAC DE NEUCHATEL
                #EUC25SLP - CBA EUC25SLP
                #LFSB04S - TMA BALE 04 SUISSE
                #LFSB03S1 - TMA BALE PARTIE 03 SUISSE 1
                #LFSB03S - TMA BALE 03 SUISSE
                #LFSB03S2 - TMA BALE PARTIE 03 SUISSE 2
                #LSR75_2 - R T DITTINGEN WEST (GLIDER)
                #LSR75_1 - R T DITTINGEN WEST (GLIDER)
                #LFSB88 - TMA BALE DELEG.ZURICH-AZ4 T3
                #LFSB25D - TMA BALE PARTIE DELEG.ZURICH-AZ4 T3 D
                #LFSB82 - TMA BALE DELEG.ZURICH-AZ4 T1
                #LFSB23D - TMA BALE PARTIE DELEG.ZURICH-AZ4 T1 D
                #LSR33 - R BALSTHAL
                #LSXGOESGEN - PROTECT GOESGEN (IND-NUCLEAR)
                #LSR76 - R T DITTINGEN EAST (GLIDER)
                #LFSB02D - TMA BALE 02 ALLEMANDE
                #LFSB02A - TMA BALE 02 ALLEMANDE
                #LFSB40.20 - TMA BALE DELEG.LANGEN SW2.20
                #LFSB40 - TMA BALE DELEG.LANGEN SW2
                #LFSB18C - TMA BALE PARTIE DELEG.LANGEN SW2 C
                #LFSB18D - TMA BALE PARTIE DELEG.LANGEN SW2 D
                #LFSB70 - TMA BALE DELEG.ZURICH-AZ3
                #LFSB21C - TMA BALE PARTIE DELEG.ZURICH-AZ3 C
                #LSZH8 - TMA ZURICH TMA SECTOR 8
                #EDTFPJA - Q FREIBURG/BADEN-WUERTTEMBERG (PARACHUTE)
                #EDTF - PROTECT FREIBURG I.BR.
                #EDSBCLDH - D KARLSRUHE/BADEN-BADEN H
                #ED0004 - PROTECT RHEINSTETTEN
                #ELS02-2 - R KONZ / KONEN GLIDER SECTOR SOUTH (GLIDER)
                #EBS80 - Q WOLKRANGE (SPORT)
                #EBR41 - R LAGLAND-ARLON (MILOPS / SeeNotam)
                #EBS136 - Q LOUETTE-SAINT-DENIS (SPORT)
                #EBLFA01 - Q LOW FLYING ARDENNES AREA 01 (MILOPS)
                #EBR06B - PART FLORENNES
                #EBS153 - Q MERBES-LE-CHATEAU (SPORT)
                #EBS92 - Q HAULCHIN (SPORT)
                #EBCI - CTR CHARLEROI (ATS)
                #EBR22 - R CASTEAU (OTHER)
                #EBCI1 - TMA CHARLEROI TMA ONE (ATS)
                #EBSOUTH1 - CTA BRUSSELS CTA SOUTH ONE (ATS)
                #EBCV - CTR CHIEVRES (ATS)
                #EBBR2 - TMA BRUSSELS TMA TWO (ATS)
                #EBBR3A - TMA BRUSSELS TMA THREE A (ATS)
                #EBS103 - Q POTTES (SPORT)
                #EBR70 - R POTTES (TRG / SeeNotam)
                #EBS120 - Q DOTTIGNIES (SPORT)
                #EBS109 - Q MOORSELE (SPORT)
                #EBS14 - Q MOORSELE (PARACHUTE)
                #EBS73 - Q HOUTHEM (SPORT)
                #EBS105 - Q VLAMERTINGE (SPORT)
                #EBS113 - Q HOOGSTADE (SPORT)
                #EB1 - CBA 1
                #EBCBA1C - CBA CROSS BORDER AREA ONE CHARLIE (MILOPS)
                #EBS180 - Q KOKSIJDE (SPORT)
                #EBR24A - R KOKSIJDE (MILOPS)
                #EBR08 - R KOKSIJDE (MILOPS)
                #EUC25SL2 - CBA EUC25SL2
                #EBHTA10A - Q COASTAL HELICOPTER TRAINING AREA (MILOPS / SeeNotam)
                #EBLFA11 - Q KOKSIJDE TRAINING AREA (MILOPS)
                #EBOS1 - TMA OOSTENDE TMA ONE (ATS)
                #EBHTA10C - Q IEPER HELICOPTER TRAINING AREA (MILOPS / SeeNotam)
                #EBKT TMZ - TMZ TRANSPONDER MANDATORY ZONE KORTRIJK (EQUIPMENT)
                #EBKT RMZ - RMZ RADIO MANDATORY ZONE KORTRIJK (EQUIPMENT)
                #EBS30 - R LOW FLYING AREA GOLF TWO WEST (GLIDER / SeeNotam)
                #EBR25 - R KOKSIJDE CLIMB-OUT (JETCLIMB)
                #EBR24B - R KOKSIJDE LET-DOWN (MILOPS)
                #EBHTA10D - Q TOURNAI HELICOPTER TRAINING AREA (MILOPS / SeeNotam)
                #LFQQ2 - TMA LILLE 2 App(120.275)
                #EBS182 - R TOURNAI/MAUBRAY (GLIDER)
                #EBS02 - Q BELOEIL (BALLOON)
                #EBS65 - Q THUMAIDE (SPORT)
                #EBS128 - Q HAVAY (SPORT)
                #EBS61 - Q GRANDRIEU (SPORT)
                #EBS87 - Q MACON (SPORT)
                #EBFS - TMA FLORENNES (ATS / SeeNotam)
                #EBFS - CTA FLORENNES (ATS / SeeNotam)
                #EBD29 - Q ARDENNES 07 (MILOPS / SeeNotam)
                #EBS33-1 - R LOW FLYING AREA GOLF FIVE WEST (GLIDER / SeeNotam)
                #EBS29 - R LOW FLYING AREA GOLF TWO SOUTH (GLIDER / SeeNotam)
                #EBS86 - Q MAZEE (SPORT)
                #EBHTA04A - Q HELICOPTER TRAINING AREA ARDENNES 04A (MILOPS / SeeNotam)
                #EBLFA04 - Q LOW FLYING ARDENNES AREA 04 (MILOPS)
                #EBD26 - Q ARDENNES 05 (MILOPS / SeeNotam)
                #EBS177 - R MILFAG14 - LIBIN GLIDING AREA (GLIDER)
                #EBS161 - R BERTRIX (GLIDER / SeeNotam)
                #EBHTA06 - Q HELICOPTER TRAINING AREA ARDENNES 06 (MILOPS / SeeNotam)
                #EBLFA06 - Q LOW FLYING ARDENNES AREA 06 (MILOPS)
                #EBSOUTH3 - CTA BRUSSELS CTA SOUTH THREE (ATS)
                #EBS154 - Q SAINT-VINCENT (SPORT)
                #EBS63 - Q VILLERS-LA-LOUE (SPORT)
                #ELLX5 - TMA LUXEMBOURG TMA FIVE (ATS)
                #ELLX1A - TMA LUXEMBOURG TMA ONE A (ATS)
                #ELLX - CTR LUXEMBOURG (ATS)
                #ELLXCLDB -D LUXEMBOURG B
                #ELLX2F1 - TMA LUXEMBOURG TMA TWO F1 (ATS)
                #ELLX2F2 - TMA LUXEMBOURG TMA TWO F2 (ATS)
                #EDR205D - R TRA LAUTER 1 D
                #ETXUTE - PROTECT ARA UTE (REFUEL)
                #EDRJPJA - Q SAARLOUIS-DUEREN/SAARLAND (PARACHUTE)
                #EDDR1 - CTR SAARBRUECKEN
                #EDR205C - R TRA LAUTER 1 C
                #EDRZRMZ - RMZ ZWEIBRUECKEN
                #EDRZPJA - Q ZWEIBRUECKEN/RHEINLAND-PFALZ (PARACHUTE)
                #EDSBCLDF - D KARLSRUHE/BADEN-BADEN F
                #EDSBCLDD - D KARLSRUHE/BADEN-BADEN D
                #EDSBCLDA - D KARLSRUHE/BADEN-BADEN A
                #EDSB1 - CTR KARLSRUHE/BADEN-BADEN
                #EDSBCLDC - D KARLSRUHE/BADEN-BADEN C
                #LFST1.1 - TMA STRASBOURG 1.1 App(120.700)
                #EDSBCLDB - D KARLSRUHE/BADEN-BADEN B
                #EDSBCLDE - D KARLSRUHE/BADEN-BADEN E
                #EDSBCLDG - D KARLSRUHE/BADEN-BADEN G
                #LFST30 - CTR STRASBOURG DELEG. STUTTGART
                #EDTL - CTR LAHR
                #EDTLPJA - Q LAHR/BADEN-WUERTTEMBERG (PARACHUTE)
                #LFSB15C - TMA BALE PARTIE DELEG.LANGEN NORD C
                #LFSBNORD - TMA BALE DELEG.LANGEN NORD
                #EDTGPJA - Q BREMGARTEN/BADEN-WUERTTEMBERG (PARACHUTE)
                #EDTG - PROTECT BREMGARTEN
                #LFSB16D - TMA BALE PARTIE DELEG.LANGEN S-E D
                #LFSB16C - TMA BALE PARTIE DELEG.LANGEN S-E C
                #LFSB20 - TMA BALE DELEG.LANGEN S-E
                #LFSB20.20 - TMA BALE DELEG.LANGEN S-E.20
                #LFSB17D - TMA BALE PARTIE DELEG.LANGEN SW1 D
                #LFSB17C - TMA BALE PARTIE DELEG.LANGEN SW1 C
                #LFSB30.20 - TMA BALE DELEG.LANGEN SW1.20
                #LFSB30 - TMA BALE DELEG.LANGEN SW1
                #LFSB01D1 - TMA BALE 01 ALLEMANDE
                #LFSB01A - TMA BALE 01 ALLEMANDE
                #LFSB1D1 - CTR BALE ALLEMANDE
                #LFSB2 - CTR BALE ALLEMANDE Twr(118.300)
                #LFSB1S - CTR BALE SUISSE
                #LFSB01S - TMA BALE 01 SUISSE
                #LFSB3 - CTR BALE SUISSE Twr(118.300)
                #LFSB20D - TMA BALE PARTIE DELEG.ZURICH-AZ2 D
                #LFSB20C - TMA BALE PARTIE DELEG.ZURICH-AZ2 C
                #LFSB60 - TMA BALE DELEG.ZURICH-AZ2.20
                #LFSB60.20 - TMA BALE DELEG.ZURICH-AZ2.20
                #LFSB02S - TMA BALE 02 SUISSE
                #LFSB22C - TMA BALE PARTIE DELEG.ZURICH-AZ4 C
                #LFSB80 - TMA BALE DELEG.ZURICH-AZ4
                #LFSB24D - TMA BALE PARTIE DELEG.ZURICH-AZ4 T2 D
                #LFSB85 - TMA BALE DELEG.ZURICH-AZ4 T2
                #LSR29 - R TAVANNES
                #LSR27 - R NEUCHATEL
                #EUC25SL1 - CBA EUC25SL1
                #LSAG - CTA GENEVA
                #LSR28 - R YVERDON
                #LSGG5 - TMA GENEVE TMA5
                #LSR81 - R T LE BRASSUS (GLIDER)
                #LSR80 - R T VALLORBE (GLIDER)
                #LSR26 - R CHARBONNIERES
                #LSR21 - R UNTERWALLIS N
                #LSR23 - R UNTERWALLIS S
                #LSR24 - R WALLIS S
                #LIR64 - R LI R64 - CUNEO
                #LICTAMM7 - CTA ZONA '7'
                #LICTAMM4 - CTA ZONA '4'
                #LEPP - CTA PAMPLONA
                #LEBL_C - C BARCELONA TMA
                #LEBL_D - D BARCELONA TMA
                #LED8 - Q JAIZQUIBEL (GUIPUZCOA)
                #LED67 - Q SAN CLEMENTE SASEBAS (GERONA)

        #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire Français
        elif sKeyFile=="FFVP-Parcs":
            if oAs["UId"] in ["GrandParadis","Ordessa"]:
                oAs.update({"ExtOfFrensh":True})       #Exclusion volontaire sur base de l'UId
                #UId='GrandParadis' - ZSM Grand Paradis
				#UId='Ordessa' - ZSM Ordessa

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

        #Toutes les RTBA du SIA France, ne sont jamais activées les samedis/dimanches et jours fériés
        if sKeyFile in ["EuCtrl","SIA"] and oAs["type"]=="R":
            if oAs["id"] in ["LFR45A","LFR45B","LFR45C","LFR45D","LFR45N2","LFR45N3","LFR45N4","LFR45N5.1","LFR45N5.2","LFR45S1","LFR45S2","LFR45S3","LFR45S4","LFR45S5","LFR45S6.1","LFR45S6.2","LFR45S7","LFR45NS","LFR46A","LFR46B","LFR46C","LFR46D","LFR46E1","LFR46E2","LFR46F1","LFR46F2","LFR46F3","LFR46G","LFR46N1","LFR46N2","LFR69","LFR139","LFR142","LFR143","LFR144","LFR145","LFR147","LFR165","LFR152","LFR166A","LFR166B","LFR166C","LFR56","LFR57","LFR149A","LFR149B","LFR149D","LFR149E","LFR193A","LFR193B","LFR590A","LFR590B","LFR191A","LFR191B","LFR191C","LFR589A","LFR589B","LFR591","LFR592","LFR593A","LFR593B"]:
                oAs.update({"type":"RTBA"})
                oAs.update({"exceptSAT":True})
                oAs.update({"exceptSUN":True})
                oAs.update({"exceptHOL":True})
                #self.oLog.info("Special French-RTBA areas - ({0}){1}".format(sKeyFile, oAs["UId"], oAs["id"], outConsole=False))

        return
