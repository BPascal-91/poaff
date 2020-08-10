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
cstKeyCatalogSrcAixmFile = "srcAixmFile"
cstKeyCatalogSrcAixmOrigin = "srcAixmOrigin"
cstKeyCatalogSrcAixmVersion = "srcAixmVersion"
cstKeyCatalogSrcAixmCreated = "srcAixmCreated"

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

    def saveCatalogFiles(self, sFile:str=None) -> bool:
        if sFile:   self.sFileCatalog = sFile
        bpaTools.writeJsonFile(self.sFileCatalog, self.oGlobalCatalog)
        sFile = self.sFileCatalog.replace(".json", ".csv")
        csv = aixmReader.convertJsonCalalogToCSV(self.oGlobalCatalog)
        bpaTools.writeTextFile(sFile, csv)
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

        oCatalogFile:dict = {}                                                                      #Description du fichier analysé
        oCatalogFile.update({cstKeyCatalogSrcAixmFile:oHeadFile[cstKeyCatalogSrcFiles]["1"][cstKeyCatalogSrcAixmFile]})         #Nom du fichier analysé
        oCatalogFile.update({cstKeyCatalogSrcAixmOrigin:oHeadFile[cstKeyCatalogSrcFiles]["1"][cstKeyCatalogSrcAixmOrigin]})     #Origine du fichier analysé
        oCatalogFile.update({cstKeyCatalogSrcAixmVersion:oHeadFile[cstKeyCatalogSrcFiles]["1"][cstKeyCatalogSrcAixmVersion]})   #Version du fichier analysé
        oCatalogFile.update({cstKeyCatalogSrcAixmCreated:oHeadFile[cstKeyCatalogSrcFiles]["1"][cstKeyCatalogSrcAixmCreated]})   #Horodatage de la création du fichier analysé

        if cstKeyCatalogSrcFiles in self.oGlobalCatalogHeader:
            self.oGlobalCatalogFiles = self.oGlobalCatalogHeader[cstKeyCatalogSrcFiles]     #Récupération de la liste des fichiers sources
        else:
            self.oGlobalCatalogFiles:dict = {}                                              #Création de la liste des fichiers sources
        self.oGlobalCatalogFiles.update({sKeyFile:oCatalogFile})                            #Enregistrement de la description du fichier analysé
        self.oGlobalCatalogHeader.update({cstKeyCatalogSrcFiles:self.oGlobalCatalogFiles})  #Enregistrement de la nouvelle liste des fichiers sources

        if cstKeyCatalogCatalog in self.oGlobalCatalog:
            oGlobalAreas = self.oGlobalCatalog[cstKeyCatalogCatalog]                        #Récupération de la liste des zones consolidés
        else:
            oGlobalAreas:dict = {}                                                          #Création d'une liste des zones a consolider

        oAsAreas = ofileCatalog[cstKeyCatalogCatalog]                                       #Catalogue des Espace-aériens contenus dans le fichier analysé
        barre = bpaTools.ProgressBar(len(oAsAreas), 20, title="Merge Catalog File + " + sKeyFile)
        idx = 0
        for sAsKey, oAs in oAsAreas.items():
            idx+=1
            if self.isValidArea(sKeyFile, oAs):                                             #Exclure certaines zones
                oAs.update({cstKeyCatalogKeySrcFile:sKeyFile})                              #Ajout de la réfénce au fichier source
                sNewKey = str(oAs["id"]).strip()                                            #Nouvelle identifiant de référence pour le catalogue global
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
                    if sNewKey in oGlobalAreas:                                             #Controle prealable de presence
                        #self.oLog.info("Ignored area (existing in global catalog) - ({0}){1}".format(sKeyFile, sNewKey, outConsole=False))
                        None
                    else:
                        oAs.update({cstKeyCatalogKeyGUId:sNewKey})
                        oAs.update({"deltaExt":True})                                       #DeltaExtended - Marquage d'une extension de périmètre par analyse différentielle
                        oGlobalAreas.update({sNewKey:oAs})                                  #Ajoute la zone au catalogue global
                        self.oLog.info("Delta add area in global catalog - ({0}){1}".format(sKeyFile, sNewKey, outConsole=False))
                else:
                    self.oLog.error("Process type error - {0}".format(oFile[poaffCst.cstSpProcessType], outConsole=True))

            self.isCleanArea4FreeFlight(sKeyFile, oAs)
            self.isSpecialArea4FreeFlight(sKeyFile, oAs)
            barre.update(idx)
        barre.reset()
        oSrcFiles = self.oGlobalCatalogHeader.pop(cstKeyCatalogSrcFiles)
        self.oGlobalCatalogHeader.update({cstKeyCatalogNbAreas:len(oGlobalAreas)})          #Nombre de zones
        self.oGlobalCatalogHeader.update({cstKeyCatalogSrcFiles:oSrcFiles})
        self.oGlobalCatalog.update({cstKeyCatalogCatalog:oGlobalAreas})                     #Nouvelle liste de zones
        return

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
        ret:bool = True                                             #Default value
        if oAs["groupZone"]:                       return False     #Exclure les zones de regroupement

        if sKeyFile == "BPa-Test4Clean":                #Suppression manuelle de zones
            if oAs["id"] in ["LFD18B1"]:                #Test de suppression manuelle d'une zone en mer - [Q] 18 B1 (id=LFD18B1)
                ret = False

        elif sKeyFile == "EuCtrl":                      #Suppression manuelle de zones
            #    [D] ALBERT BRAY (CTR / id=LFAQ) - car mauvais tracé et récupération via le fichier SIA
            if oAs["id"] in ["LFAQ"]:
                ret = False

        if not(ret):
            self.oLog.info("Unvalid area by manual filter - ({0}){1}".format(sKeyFile, oAs["UId"], oAs["id"], outConsole=False))
        return ret

    #Flager certaine zone 'inutile' pour la vision 'freeflight'
    def isCleanArea4FreeFlight(self, sKeyFile:str, oAs:dict) -> None:
        bClean:bool = False                                    #Default value

        #Test de suppression volontaire
        if sKeyFile == "BPa-Test4AppDelta1":
            if oAs["id"] in ["LFRD02","LTA13071"]:
                bClean = True
                #[D] FRANCE 1 (LTA / id=LTA13071)

        #Fonctionnalité d'Exclusion de zones pour épurer le périmètre (non-concernées ou en mer...)
        elif sKeyFile in ["EuCtrl","SIA"]:

            #Exclusion volontaire pour différentes causes
            if sKeyFile=="EuCtrl" and (oAs["id"] in ["EBS27","LSGG1","LSGG2","LSGG3","LSGG4","LSGG4.1","LSGG6","LSGG7","LSGG8","LSGG9","LSGG10","LSGG","LFSB1F"]):
                #### Très mauvais tracé (il manque les bordure de frontières Blegique-PaysBas)
                #[W] LOW FLYING AREA GOLF ONE (R / GLIDER / SeeNotam / id=EBS27)
                #### Suppression de doublons entre fichier SIA-FR et fourniture Suisse via Eurocontrol
                #[D] GENEVA (CTR / id=LSGG)
                #[C] GENEVE TMA1 (TMA / id=LSGG1)
                #[C] GENEVE TMA2 (TMA / id=LSGG2)
                #[C] GENEVE TMA3 (TMA / id=LSGG3)
                #[C] GENEVE TMA4 (TMA / id=LSGG4)
                #[C] GENEVE TMA4.1 (TMA / id=LSGG4.1)
                #[C] GENEVE TMA5 (TMA / id=LSGG5) ne pas l'exclure car sur territoire Francais et non présente ds le fichier SIA-FR !!!
                #[C] GENEVE TMA6 (TMA / id=LSGG6)
                #[C] GENEVE TMA7 (TMA / id=LSGG7)
                #[C] GENEVE TMA8 (TMA / id=LSGG8)
                #[C] GENEVE TMA9 (TMA / id=LSGG9)
                #[C] GENEVE TMA10 (TMA / id=LSGG10)
                #[D] BALE FRANCAISE (CTR / id=LFSB1F)
                bClean = True

            #Suppression de zones non-utile pour le parapente, exemple en mer ou autres cas...
            elif oAs["id"] in ["LSAZ","LER152","LER153","LEVASC11","EBBU RMZ","EBBU TMZ","LFR13B1","LFD18B1","LFD18A5","LFD214","LFD16D","LFD18B2","LFD31","LFD32","OCA4521.20","EISOA","LICTARR2","DTKA","LID40A","LID40B","LID91","LID91BIS","LFMN3","LFD54C1","LFD54C2","LFD54B1","LFD54B2","LFD54WC","LFD143B","LFML11","LFD54WB","LFD121","LFD142","LFD108","LFD143A","LFR217/2","CTA47782","LSAG","LFR191A",R"LFR108C","LECP_A","LECP","LFD33","LFD16A","LFD16B","LFD16C","LFD16E","EGD008A","EGD008B","EGD003","EGD004","EGJJ1S","CTA11561","EGJA-1","EGJJN","EGJJ1N","EGJJ2","CTA11562","EGTE5","EGTE4","EGD013","EGD017","EGD023","EGVF5","EGVF4","EGVF3","EGD036","EGD038","EGD039","EGD040","EGWO6","EGWO2","EGWO1","EGWO3","LID67","LFD67","CTA4351A.2","FM50"]:
                bClean = True
                #[C] ZURICH (CTA / id=LSAZ)
                #### Parc en Espagne, deja intégré dans les parcs naturels via integration FFVP
                #[R] PARQUE NACIONAL DE ORDESA Y MONTE PERDIDO NORTE (HUESCA) (id=LER152)
                #[R] PARQUE NACIONAL DE ORDESA Y MONTE PERDIDO SUR (HUESCA) (id=LER153)
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
                oAs.update({"deltaExt":False})       #Inclusion volontaire

        #Fonctionnalité d'Exclusion volontaire de certaines zones du territoire Français
        elif sKeyFile=="SIA":
            if oAs["id"] in ["LFQQ2","LFST1.1","LFST30","LFSBNORD","LFSB20.20","LFSB20","LFSB30","LFSB30.20","LFSB40.20","LFSB40","LFSB01A","LFSB2","LFSB01S","LFSB3","LFSB02S","LFSB60.20","LFSB60","LFSB70","LFSB02A","LFSB82","LFSB80","LFSB88","LFSB85"]:
                oAs.update({"deltaExt":True})       #Exclusion volontaire
                #[D] LILLE 2 (TMA / id=LFQQ2)
                #[D] STRASBOURG 1.1 (TMA / id=LFST1.1)
                #[D] STRASBOURG DELEG. STUTTGART (CTR / id=LFST30)
                #[C] BALE DELEG.LANGEN NORD (TMA / id=LFSBNORD)
                #[D] BALE DELEG.LANGEN S-E.20 (TMA / id=LFSB20.20)
                #[C] BALE DELEG.LANGEN S-E (TMA / id=LFSB20)
                #[C] BALE DELEG.LANGEN SW1 (TMA / id=LFSB30)
                #[D] BALE DELEG.LANGEN SW1.20 (TMA / id=LFSB30.20)
                #[D] BALE DELEG.LANGEN SW2.20 (TMA / id=LFSB40.20)
                #[C] BALE DELEG.LANGEN SW2 (TMA / id=LFSB40)
                #[D] BALE 01 ALLEMANDE (TMA / id=LFSB01A)
                #[D] BALE ALLEMANDE (CTR / id=LFSB2)
                #[D] BALE 01 SUISSE (TMA / id=LFSB01S)
                #[D] BALE SUISSE (CTR / id=LFSB3)
                #[D] BALE 02 SUISSE (TMA / id=LFSB02S)
                #[D] BALE DELEG.ZURICH-AZ2.20 (TMA / id=LFSB60.20)
                #[C] BALE DELEG.ZURICH-AZ2 (TMA / id=LFSB60)
                #[C] BALE DELEG.ZURICH-AZ3 (TMA / id=LFSB70)
                #[D] BALE 02 ALLEMANDE (TMA / id=LFSB02A)
                #[D] BALE DELEG.ZURICH-AZ4 T1 (TMA / id=LFSB82)
                #[C] BALE DELEG.ZURICH-AZ4 (TMA / id=LFSB80)
                #[D] BALE DELEG.ZURICH-AZ4 T3 (TMA / id=LFSB88)
                #[D] BALE DELEG.ZURICH-AZ4 T2 (TMA / id=LFSB85)

        #Fonctionnalité d'Inclusion volontaire de certaines zones du territoire Français
        elif sKeyFile=="EuCtrl":
            if oAs["id"] in ["EGR095","EGJJS","EGJA-2","LFBD7.10","EUC25FW","EUC25FC","EUC25FE","EBR24A","LFCBA1A","LFCBA16B","EBCBA1C","EBR18A","EBR18B","EBUL607","EBOS2","EBOS1","EDSB2"]:
                oAs.update({"deltaExt":False})      #Inclusion volontaire
                #[R] SARK (id=EGR095)
                #[C] CHANNEL ISLANDS TMA SOUTH (TMA / id=EGJJS)
                #[D] CHANNEL ISLANDS CTR SOUTH (CTR / id=EGJA-2)
                #[D] LF TMA AQUITAINE 7.10 (TMA / id=LFBD7.10)      #Zone manquante dans le fichier SIA
                #[R] C 25 FW (CBA / id=EUC25FW)                     #idem
                #[R] C 25 FC (CBA / id=EUC25FC)                     #idem
                #[R] C 25 FE (CBA / id=EUC25FE)                     #idem
                #[R] KOKSIJDE (MILOPS / id=EBR24A)
                #[R] CROSS BORDER AREA 1 ALPHA (CBA / MILOPS / id=LFCBA1A)
                #[R] CROSS BORDER AREA 16 BRAVO (CBA / JETCLIMB / id=LFCBA16B)
                #[R] CROSS BORDER AREA ONE CHARLIE (CBA / MILOPS / id=EBCBA1C)
                #[R] FLORENNES (JETCLIMB / id=EBR18A)
                #[R] FLORENNES (JETCLIMB / id=EBR18B)
                #[C] (U)L607 AREA (CTA / ATS / id=EBUL607)
                #[C] OOSTENDE TMA TWO (TMA / ATS / id=EBOS2)
                #[C] OOSTENDE TMA ONE (TMA / ATS / id=EBOS1)
                #[D] KARLSRUHE BADEN (CTR / id=EDSB2)

        #Fonctionnalité spécifique pour une présentation étendue de type CFD
        #Les zones suivantes sont utilisées pour un affichage quasi-exaustif ou garantie des caulculs-automatisés
        if sKeyFile in ["EuCtrl","SIA"]:
            if oAs["id"] in ["LTA13071","CTA4351A.2","FMEE1","OCA4521.20"]:
                oAs.update({"use4cfd":True})
                #[D] FRANCE 1 (LTA / id=LTA13071)
                #[E] PIARCO A.20 (CTA / id=CTA4351A.2)
                #[E] LA REUNION 1 (TMA / id=FMEE1)
                #[E] TAHITI.20 (OCA / id=OCA4521.20)

        #Toutes les RTBA du SIA France, ne sont jamais activées les samedis/dimanches et jours fériés
        if sKeyFile in ["EuCtrl","SIA"] and oAs["type"]=="R":
            if oAs["id"] in ["LFR45A","LFR45B","LFR45C","LFR45D","LFR45N2","LFR45N3","LFR45N4","LFR45N5.1","LFR45N5.2","LFR45S1","LFR45S2","LFR45S3","LFR45S4","LFR45S5","LFR45S6.1","LFR45S6.2","LFR45S7","LFR45NS","LFR46A","LFR46B","LFR46C","LFR46D","LFR46E1","LFR46E2","LFR46F1","LFR46F2","LFR46F3","LFR46G","LFR46N1","LFR46N2","LFR69","LFR139","LFR142","LFR143","LFR144","LFR145","LFR147","LFR165","LFR152","LFR166A","LFR166B","LFR166C","LFR56","LFR57","LFR149A","LFR149B","LFR149D","LFR149E","LFR193A","LFR193B","LFR590A","LFR590B","LFR191A","LFR191B","LFR191C","LFR589A","LFR589B","LFR591","LFR592","LFR593A","LFR593B"]:
                oAs.update({"type":"RTBA"})
                oAs.update({"exceptSAT":True})
                oAs.update({"exceptSUN":True})
                oAs.update({"exceptHOL":True})
                oAs.update({"nameV":aixmReader.getVerboseName(oAs)})
                #self.oLog.info("Special French-RTBA areas - ({0}){1}".format(sKeyFile, oAs["UId"], oAs["id"], outConsole=False))


        return
