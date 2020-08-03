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
cstKeyCatalogKeyExtOfFrench = "externalOfFrench"

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
        for sAsKey, oAs in oAsAreas.items():
            if self.isValidArea(sKeyFile, oAs):                                             #Exclure certaines zones
                oAs.update({cstKeyCatalogKeySrcFile:sKeyFile})                              #Ajout de la réfénce au fichier source
                sNewKey = str(oAs["id"]).strip()                                            #Nouvelle identifiant de référence pour le catalogue global
                if sNewKey=="": sNewKey = self.makeNewKey()                                 #Initialisation d'une clé non vide
                if   oFile[poaffCst.cstSpProcessType]==poaffCst.cstSpPtAdd:                 #Ajout systématique des zones (avec débloublonnage des 'id' automatisé)
                    if sNewKey in oGlobalAreas:
                        sNewKey2 = self.makeNewKey(sNewKey, oGlobalAreas)                   #Identification d'une nouvelle clé unique
                        self.oLog.info("Deduplication area for global catalog - orgId={0} --> newId={1}".format(sNewKey, sNewKey2, outConsole=False))
                        sNewKey = sNewKey2
                    oAs.update({cstKeyCatalogKeyGUId:sNewKey})
                    oGlobalAreas.update({sNewKey:oAs})                                      #Ajoute la zone au catalogue global
                    self.oLog.info("Add area in global catalog - ({0}){1}".format(sKeyFile, sNewKey, outConsole=False))
                elif oFile[poaffCst.cstSpProcessType]==poaffCst.cstSpPtAddDelta:                                          #Ajout des zones qui ne sont pas déjà existante
                    if sNewKey in oGlobalAreas:                                             #Controle prealable de presence
                        self.oLog.info("Ignored area (existing in global catalog) - ({0}){1}".format(sKeyFile, sNewKey, outConsole=False))
                    else:
                        oAs.update({cstKeyCatalogKeyGUId:sNewKey})
                        oGlobalAreas.update({sNewKey:oAs})                                  #Ajoute la zone au catalogue global
                        self.oLog.info("Add area in global catalog - ({0}){1}".format(sKeyFile, sNewKey, outConsole=False))
                else:
                    self.oLog.error("Process type error - {0}".format(oFile[poaffCst.cstSpProcessType], outConsole=True))

            self.isCleanArea4FreeFlight(sKeyFile, oAs)
            self.isSpecialArea4FreeFlight(sKeyFile, oAs)

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

    #Suppression physique de zones concidérées comme étant fausse dans le fichier source
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
        if not oAs["freeFlightZone"]:   return              #Zone déjà non-concernée

        ret:bool = False                                    #Default value
        if sKeyFile == "BPa-Test4AppDelta":
            if oAs["id"] in ["LFRD02"]:                     #Test de suppression volontaire
                ret = True

        elif sKeyFile in ["EuCtrl","SIA"]:
            #Exclusion de zones non-concernées ou en mer...
            #    [E] PIARCO A.20 (CTA / id=CTA4351A.2)            
            #    [A] PALMA TM (id=LECP_A)
            #    [C] PALMA TMA (RMZ) (TMA / id=LECP)
            #    [D] BARCELONA TMA (id=LEBL_D)
            #    [R] BRUSSELS FIR (RMZ / EQUIPMENT / id=EBBU RMZ)
            #    [P] BRUSSELS FIR (TMZ / EQUIPMENT / id=EBBU TMZ)
            #    [E] LA REUNION 1 (TMA / id=FMEE1)
            #    [R] 13 B1 (SeeNotam / id=LFR13B1)
            #    [Q] 18 B1 (id=LFD18B1)                     - en mer, face au finistere
            #    [Q] 18 A5 (id=LFD18A5)                     - en mer, face au finistere
            #    [Q] 214 (SeeNotam / id=LFD214)             - en mer, face au finistere
            #    [Q] 16 D (SeeNotam / id=LFD16D)
            #    [R] 13 C (SeeNotam / id=LFR13C)
            #    [Q] 18 B2 (id=LFD18B2)                     - en mer...
            #    [Q] 31 D (id=LFD31)                        - en mer...
            #    [Q] 32 (id=LFD32)                          - en mer...
            #    [Q] 18 A4 (id=LFD18A4)                     - en mer
            #    [E] TAHITI.20 (OCA / id=OCA4521.20)        * aucun interet...
            #    [A] SHANNON OCEANIC TRANSITION AREA (SOTA) (id=EISOA)
            #    [D] ZONA '2' (CTA / id=LICTARR2)
            #    [C] TUNIS CTA NORTH WEST (CTA / id=DTKA)
            #    [Q] LI D40/A - DECIMOMANNU (id=LID40A)
            #    [Q] LI D40/B - CAGLIARI (id=LID40B)
            #    [Q] LI D91 - MAR LIGURE (id=LID91)
            #    [Q] LI D91/BIS - LIGURIA (id=LID91BIS)
            #    [D] NICE 3 (TMA / id=LFMN3)
            #    [R] 225 (id=LFR225)
            #    [D] NICE 2 (CTR / id=LFMN2)
            #    [D] CANNES 2 (CTR / id=LFMD2)
            #    [Q] 54 C1 (id=LFD54C1)
            #    [Q] 54 C2 (id=LFD54C2)
            #    [Q] 54 B1 (id=LFD54B1)
            #    [Q] 54 B2 (id=LFD54B2)
            #    [Q] 54 WC (id=LFD54WC)
            #    [Q] 143 B (id=LFD143B)
            #    [D] PROVENCE 11 (TMA / id=LFML11)
            #    [Q] 54 WA (id=LFD54WA)
            #    [Q] 54 WB (id=LFD54WB)
            #    [D] PROVENCE 7 (TMA / id=LFML7)
            #    [Q] 121 (id=LFD121)
            #    [Q] 142 (id=LFD142)
            #    [D] MONTPELLIER 17.20 (TMA / id=LFMT17.20)
            #    [Q] 108 E (id=LFD108)
            #    [Q] 143 A (id=LFD143A)
            #    [R] 217 /2 (id=LFR217/2)
            #    [D] RHONE 2 (CTA / id=CTA47782)
            #    [R] 191 A (SeeNotam / id=LFR191A)
            #    [R] 108 C (id=LFR108C)
            #    [Q] 33 (id=LFD33)
            #    [Q] 16 A (SeeNotam / id=LFD16A)
            #    [Q] 16 B (SeeNotam / id=LFD16B)
            #    [Q] 16 C (SeeNotam / id=LFD16C)
            #    [Q] 16 E (SeeNotam / id=LFD16E)
            #    [Q] PLYMOUTH (id=EGD008A)
            #    [Q] PLYMOUTH (id=EGD008B)
            #    [Q] PLYMOUTH (id=EGD003)
            #    [Q] PLYMOUTH (id=EGD004)
            #    [C] CHANNEL ISLANDS CTA 1 SOUTH (CTA / id=EGJJ1S)
            #    [D] ILES ANGLO-NORMANDES 1 (CTA / id=CTA11561)
            #    [D] CHANNEL ISLANDS CTR NORTH (CTR / id=EGJA-1)
            #    [C] CHANNEL ISLANDS TMA NORTH (TMA / id=EGJJN)
            #    [C] CHANNEL ISLANDS CTA 1 NORTH (CTA / id=EGJJ1N)
            #    [C] CHANNEL ISLANDS CTA 2 (CTA / id=EGJJ2)
            #    [D] ILES ANGLO-NORMANDES 2 (CTA / id=CTA11562)
            #    [C] BERRY HEAD CTA 5 (CTA / id=EGTE5)
            #    [C] BERRY HEAD CTA 4 (CTA / id=EGTE4)
            #    [Q] LYME BAY (id=EGD013)
            #    [Q] PORTLAND (id=EGD017)
            #    [Q] PORTLAND (id=EGD023)
            #    [C] PORTSMOUTH CTA 5 (CTA / id=EGVF5)
            #    [C] PORTSMOUTH CTA 4 (CTA / id=EGVF4)
            #    [Q] PORTSMOUTH (id=EGD036)
            #    [Q] PORTSMOUTH (id=EGD038)
            #    [Q] PORTSMOUTH (id=EGD039)
            #    [Q] PORTSMOUTH (id=EGD040)
            #    [C] WORTHING CTA 6 (CTA / id=EGWO6)
            #    [C] WORTHING CTA 2 (CTA / id=EGWO2)
            #    [C] WORTHING CTA 1 (CTA / id=EGWO1)
            #    [C] WORTHING CTA 3 (CTA / id=EGWO3)
            #    [Q] LI D67 - SOLENZARA (FRANCIA - FRANCE) (SeeNotam / id=LID67)
            #    [Q] 67 (SeeNotam / id=LFD67)
            #    [Q] 50 (SeeNotam / id=FM50)
            if oAs["id"] in ["EBBU RMZ","EBBU TMZ","FMEE1","LFR13B1","LFD18B1","LFD18A5","LFD214","LFD16D","LFR13C","LFD18B2","LFD31","LFD32","LFD18A4","OCA4521.20","EISOA","LICTARR2","DTKA","LID40A","LID40B","LID91","LID91BIS","LFMN3","LFR225","LFMN2","LFMD2","LFD54C1","LFD54C2","LFD54B1","LFD54B2","LFD54WC","LFD143B","LFML11","LFD54WA","LFD54WB","LFML7","LFD121","LFD142","LFMT17.20","LFD108","LFD143A","LFR217/2","CTA47782","LFR191A",R"LFR108C","LECP_A","LECP","LEBL_D","LFD33","LFD16A","LFD16B","LFD16C","LFD16E","EGD008A","EGD008B","EGD003","EGD004","EGJJ1S","CTA11561","EGJA-1","EGJJN","EGJJ1N","EGJJ2","CTA11562","EGTE5","EGTE4","EGD013","EGD017","EGD023","EGVF5","EGVF4","EGD036","EGD038","EGD039","EGD040","EGWO6","EGWO2","EGWO1","EGWO3","LID67","LFD67","CTA4351A.2","FM50"]:
                ret = True

            elif oAs["id"] in ["EBS27"]:        #Exclusion pour cause de mauvais tracé
                #[W] LOW FLYING AREA GOLF ONE (R / GLIDER / SeeNotam / id=EBS27)
                #   2020-08-02 12:21:58,760 poaff v2.0.1 WARNING Missing geoBorder GbrUid='19004836' Name=BELGIUM_GERMANY of [W] LOW FLYING AREA GOLF ONE (R / GLIDER / SeeNotam / id=EBS27)
                #   2020-08-02 12:21:58,839 poaff v2.0.1 WARNING Missing geoBorder GbrUid='19076981' Name=BELGIUM_NETHERLANDS of [W] LOW FLYING AREA GOLF ONE (R / GLIDER / SeeNotam / id=EBS27)
                #   2020-08-02 12:21:59,036 poaff v2.0.1 WARNING Missing geoBorder GbrUid='19076981' Name=BELGIUM_NETHERLANDS of [W] LOW FLYING AREA GOLF ONE (R / GLIDER / SeeNotam / id=EBS27)
                ret = True

        if (ret):
            oAs.update({"freeFlightZone":False})
            oAs.update({"excludeAirspaceByFilter":True})
            self.oLog.info("Ignored freeflight area by manual filter - ({0}){1}".format(sKeyFile, oAs["UId"], oAs["id"], outConsole=False))
        return

    #Intégre sytematiquement certaine zone utile pour la vision 'freeflight'
    def isSpecialArea4FreeFlight(self, sKeyFile:str, oAs:dict) -> None:

        if sKeyFile in ["EuCtrl","SIA"] and oAs["type"]=="LTA":
            ret:bool = False                                    #Default value
            #Préserver systématiquement les LTA "FRANCE 3 ALPES" et "FRANCE 5 PYRENEES" pour l'extension de vol-libre au dessus de FL115 et en montagne jusqu'au FL175
            aTockens:list = ["FRANCE 3 ALPES", "FRANCE 5 PYRENEES"]
            for sToken in aTockens:
                if oAs["name"][:len(sToken)]==sToken:
                    ret = True

            if (ret):
                oAs.update({"vfrZone":True})
                oAs.update({"freeFlightZone":True})
                oAs.update({"excludeAirspaceByFilter":"Integrated"})
                self.oLog.info("Special integrated freeflight area by manual filter - ({0}){1}".format(sKeyFile, oAs["UId"], oAs["id"], outConsole=False))
            else:
                oAs.update({"vfrZone":False})
                oAs.update({"freeFlightZone":False})
                oAs.update({"excludeAirspaceByFilter":True})
                self.oLog.info("Special ignored freeflight area by manual filter - ({0}){1}".format(sKeyFile, oAs["UId"], oAs["id"], outConsole=False))

        elif sKeyFile in ["EuCtrl","SIA"] and oAs["type"]=="R":
            if oAs["id"] in ["LFR45A","LFR45B","LFR45C","LFR45D","LFR45N2","LFR45N3","LFR45N4","LFR45N5.1","LFR45N5.2","LFR45S1","LFR45S2","LFR45S3","LFR45S4","LFR45S5","LFR45S6.1","LFR45S6.2","LFR45S7","LFR45NS","LFR46A","LFR46B","LFR46C","LFR46D","LFR46E1","LFR46E2","LFR46F1","LFR46F2","LFR46F3","LFR46G","LFR46N1","LFR46N2","LFR69","LFR139","LFR142","LFR143","LFR144","LFR145","LFR147","LFR165","LFR152","LFR166A","LFR166B","LFR166C","LFR56","LFR57","LFR149A","LFR149B","LFR149D","LFR149E","LFR193A","LFR193B","LFR590A","LFR590B","LFR191A","LFR191B","LFR191C","LFR589A","LFR589B","LFR591","LFR592","LFR593A","LFR593B"]:
                oAs.update({"type":"RTBA"})
                oAs.update({"exceptSAT":True})
                oAs.update({"exceptSUN":True})
                oAs.update({"exceptHOL":True})
                oAs.update({"nameV":aixmReader.getVerboseName(oAs)})
                #self.oLog.info("Special French-RTBA areas - ({0}){1}".format(sKeyFile, oAs["UId"], oAs["id"], outConsole=False))
        
        if sKeyFile == "BPa-Test4Clean":
            if oAs["id"] in ["LFD16E"]:                     #Test d'exclusion volontaire de territoire
                oAs.update({cstKeyCatalogKeyExtOfFrench:True})
                
        elif sKeyFile in ["EuCtrl","SIA"]:                  #Exclusion volontaire de territoire Français
            if oAs["id"] in ["EBS63","EBS154","EBS86","EBS87","EBS61","EBS128","EBS65","LFST30","EUC25SL2","LSGG5","LSR28","LSR26","LED67","LED8","LER152","LER153","EGJJ","EGJJ1","EGJJS","EGJA-2","LICTAMM9","LIMJ2","LIMF4","LICTAMM4","LIR64BIS","LIMF5","LIMF3","LIR64","LEPP","LICTASA7","LICTASA6","LICTASA5","LICTASA4","LICTASA2","LIEA","LSAZ","LSR24","LSAG","LSR22","LSR23","LSR21","LSVLAVAUX","LSR22","LSR23","LSR21","LSR81","LSR80","EUC25SL1","LSR27","LSR29","LFSB16C","LFSB16D","LFSB20.20","LFSB20","LFSB30","LFSB30.20","LFSB17C","LFSB17D","LFSB01D1","LFSB01A","LFSB1D1","LFSB2","LFSB01S","LFSB3","LFSB1S","LFSB22C","LFSB80","LFSB85","LFSB24D","LFSB03S1","LFSB03S","LFSB04S","LFSB03S2","LSR75_1","LSR75_2","LFSB02S","LFSB60.20","LFSB60","LFSB20C","LFSB20D","LFSBNORD","LFSB15C","EDTG","EDTGPJA","EDTL","EDTLPJA","EDSBCLDG","EDSBCLDE","LFST1.1","EDSBCLDB","EDSBCLDC","EDSB1","EDSBCLDA","EDSBCLDD","EDSBCLDF","EDR205C","EDR205D","EDDR1","ELLX2F2","ELLX2F1","ELLXCLDB","ELLX1A","ELLX","ELLX5","EBSOUTH3","EBS29","EBS33-1","EBD29","EBD26","EBHTA06","EBLFA06","EBHTA04A","EBS177","EBLFA04","EBD32","EBFS","EBS182","EBS30","EBLFA11","EBR24B","EBHTA10C","EBR25","EBHTA10A","EBKT RMZ","EBKT TMZ","EBHTA10D","LFQQ2","EBS02"]:
                oAs.update({cstKeyCatalogKeyExtOfFrench:True})
            #    [Q] VILLERS-LA-LOUE (SPORT / id=EBS63)
            #    [Q] SAINT-VINCENT (SPORT / id=EBS154)
            #    [Q] MAZEE (SPORT / id=EBS86)
            #    [Q] MACON (SPORT / id=EBS87)
            #    [Q] GRANDRIEU (SPORT / id=EBS61)
            #    [Q] HAVAY (SPORT / id=EBS128)
            #    [Q] THUMAIDE (SPORT / id=EBS65)
            #    [D] STRASBOURG DELEG. STUTTGART (CTR / id=LFST30)
            #    [R] EUC25SL2 (CBA / id=EUC25SL2)
            #    [C] GENEVE TMA5 (TMA / id=LSGG5)
            #    [R] YVERDON (id=LSR28)
            #    [R] CHARBONNIERES (id=LSR26)
            #    [Q] SAN CLEMENTE SASEBAS (GERONA) (id=LED67)
            #    [Q] JAIZQUIBEL (GUIPUZCOA) (id=LED8)
            #    [R] PARQUE NACIONAL DE ORDESA Y MONTE PERDIDO NORTE (HUESCA) (id=LER152)
            #    [R] PARQUE NACIONAL DE ORDESA Y MONTE PERDIDO SUR (HUESCA) (id=LER153)
            #    [D] ILES ANGLO NORMANDES (CTR / id=EGJJ)
            #    [A] ILES ANGLO NORMANDES (TMA / id=EGJJ1)
            #    [C] CHANNEL ISLANDS TMA SOUTH (TMA / id=EGJJS)
            #    [D] CHANNEL ISLANDS CTR SOUTH (CTR / id=EGJA-2)
            #    [D] ZONA '9' (CTA / id=LICTAMM9)
            #    [D] ZONA/ZONE '2' (CTR / id=LIMJ2)
            #    [D] ZONA/ZONE '4' (CTR / id=LIMF4)
            #    [D] ZONA '4' (CTA / id=LICTAMM4)
            #    [R] LI R64/BIS - BARGE (id=LIR64BIS)
            #    [D] ZONA/ZONE '5' (CTR / id=LIMF5)
            #    [D] ZONA/ZONE '3' (CTR / id=LIMF3)
            #    [R] LI R64 - CUNEO (id=LIR64)
            #    [D] PAMPLONA (CTA / id=LEPP)
            #    [D] ZONA '7' (CTA / id=LICTASA7)
            #    [D] ZONA '6' (CTA / id=LICTASA6)
            #    [D] ZONA '5' (CTA / id=LICTASA5)
            #    [D] ZONA '4' (CTA / id=LICTASA4)
            #    [D] ZONA '2' (CTA / id=LICTASA2)
            #    [D] ALGHERO (CTR / id=LIEA)
            #    [C] ZURICH (CTA / id=LSAZ)
            #    [R] WALLIS S (id=LSR24)
            #    [C] GENEVA (CTA / id=LSAG)
            #    [R] BERNER OBERLAND (id=LSR22)
            #    [R] UNTERWALLIS S (id=LSR23)
            #    [R] UNTERWALLIS N (id=LSR21)
            #    [Q] LAVAUX (ANTIHAIL / id=LSVLAVAUX)
            #    [R] BERNER OBERLAND (id=LSR22)
            #    [R] UNTERWALLIS S (id=LSR23)
            #    [R] UNTERWALLIS N (id=LSR21)
            #    [W] T LE BRASSUS (R / GLIDER / id=LSR81)					
            #    [W] T VALLORBE (R / GLIDER / id=LSR80)
            #    [R] EUC25SL1 (CBA / id=EUC25SL1)
            #    [R] NEUCHATEL (id=LSR27)
            #    [R] TAVANNES (id=LSR29)
            #    [C] BALE PARTIE DELEG.LANGEN S-E C (TMA / id=LFSB16C)
            #    [D] BALE PARTIE DELEG.LANGEN S-E D (TMA / id=LFSB16D)
            #    [D] BALE DELEG.LANGEN S-E.20 (TMA / id=LFSB20.20)
            #    [C] BALE DELEG.LANGEN S-E (TMA / id=LFSB20)
            #    [C] BALE DELEG.LANGEN SW1 (TMA / id=LFSB30)
            #    [D] BALE DELEG.LANGEN SW1.20 (TMA / id=LFSB30.20)
            #    [C] BALE PARTIE DELEG.LANGEN SW1 C (TMA / id=LFSB17C)
            #    [D] BALE PARTIE DELEG.LANGEN SW1 D (TMA / id=LFSB17D)
            #    [D] BALE 01 ALLEMANDE (TMA / id=LFSB01D1)
            #    [D] BALE 01 ALLEMANDE (TMA / id=LFSB01A)
            #    [D] BALE ALLEMANDE (CTR / id=LFSB1D1)
            #    [D] BALE ALLEMANDE (CTR / id=LFSB2)
            #    [D] BALE 01 SUISSE (TMA / id=LFSB01S)
            #    [D] BALE SUISSE (CTR / id=LFSB3)
            #    [D] BALE SUISSE (CTR / id=LFSB1S)
            #    [C] BALE PARTIE DELEG.ZURICH-AZ4 C (TMA / id=LFSB22C)
            #    [C] BALE DELEG.ZURICH-AZ4 (TMA / id=LFSB80)
            #    [D] BALE DELEG.ZURICH-AZ4 T2 (TMA / id=LFSB85)
            #    [D] BALE PARTIE DELEG.ZURICH-AZ4 T2 D (TMA / id=LFSB24D)
            #    [D] BALE PARTIE 03 SUISSE 1 (TMA / id=LFSB03S1)
            #    [D] BALE 03 SUISSE (TMA / id=LFSB03S)
            #    [D] BALE 04 SUISSE (TMA / id=LFSB04S)
            #    [D] BALE PARTIE 03 SUISSE 2 (TMA / id=LFSB03S2)
            #    [W] T DITTINGEN WEST (R / GLIDER / id=LSR75_1)
            #    [W] T DITTINGEN WEST (R / GLIDER / id=LSR75_2)
            #    [D] BALE 02 SUISSE (TMA / id=LFSB02S)
            #    [D] BALE DELEG.ZURICH-AZ2.20 (TMA / id=LFSB60.20)
            #    [C] BALE DELEG.ZURICH-AZ2 (TMA / id=LFSB60)
            #    [C] BALE PARTIE DELEG.ZURICH-AZ2 C (TMA / id=LFSB20C)
            #    [D] BALE PARTIE DELEG.ZURICH-AZ2 D (TMA / id=LFSB20D)
            #    [C] BALE DELEG.LANGEN NORD (TMA / id=LFSBNORD)
            #    [C] BALE PARTIE DELEG.LANGEN NORD C (TMA / id=LFSB15C)
            #    [P] BREMGARTEN (PROTECT / id=EDTG)
            #    [Q] BREMGARTEN/BADEN-WUERTTEMBERG (PARACHUTE / id=EDTGPJA)
            #    [D] LAHR (CTR / id=EDTL)
            #    [Q] LAHR/BADEN-WUERTTEMBERG (PARACHUTE / id=EDTLPJA)
            #    [D] KARLSRUHE/BADEN-BADEN G (id=EDSBCLDG)
            #    [D] KARLSRUHE/BADEN-BADEN E (id=EDSBCLDE)
            #    [D] STRASBOURG 1.1 (TMA / id=LFST1.1)
            #    [D] KARLSRUHE/BADEN-BADEN B (id=EDSBCLDB)
            #    [D] KARLSRUHE/BADEN-BADEN C (id=EDSBCLDC)
            #    [D] KARLSRUHE/BADEN-BADEN (CTR / id=EDSB1)
            #    [D] KARLSRUHE/BADEN-BADEN A (id=EDSBCLDA)
            #    [D] KARLSRUHE/BADEN-BADEN D (id=EDSBCLDD)
            #    [D] KARLSRUHE/BADEN-BADEN F (id=EDSBCLDF)
            #    [R] TRA LAUTER 1 C (id=EDR205C)
            #    [R] TRA LAUTER 1 D (id=EDR205D)
            #    [D] SAARBRUECKEN (CTR / id=EDDR1)
            #    [E] LUXEMBOURG TMA TWO F2 (TMA / ATS / id=ELLX2F2)
            #    [E] LUXEMBOURG TMA TWO F1 (TMA / ATS / id=ELLX2F1)
            #    [D] LUXEMBOURG B (id=ELLXCLDB)
            #    [D] LUXEMBOURG TMA ONE A (TMA / ATS / id=ELLX1A)
            #    [D] LUXEMBOURG (CTR / ATS / id=ELLX)
            #    [D] LUXEMBOURG TMA FIVE (TMA / ATS / id=ELLX5)
            #    [C] BRUSSELS CTA SOUTH THREE (CTA / ATS / id=EBSOUTH3)
            #    [W] LOW FLYING AREA GOLF TWO SOUTH (R / GLIDER / SeeNotam / id=EBS29)
            #    [W] LOW FLYING AREA GOLF FIVE WEST (R / GLIDER / SeeNotam / id=EBS33-1)
            #    [Q] ARDENNES 07 (MILOPS / SeeNotam / id=EBD29)
            #    [Q] ARDENNES 05 (MILOPS / SeeNotam / id=EBD26)
            #    [Q] HELICOPTER TRAINING AREA ARDENNES 06 (MILOPS / SeeNotam / id=EBHTA06)
            #    [Q] LOW FLYING ARDENNES AREA 06 (MILOPS / id=EBLFA06)
            #    [Q] HELICOPTER TRAINING AREA ARDENNES 04A (MILOPS / SeeNotam / id=EBHTA04A)
            #    [W] MILFAG14 - LIBIN GLIDING AREA (R / GLIDER / id=EBS177)
            #    [Q] LOW FLYING ARDENNES AREA 04 (MILOPS / id=EBLFA04)
            #    [Q] BERTRIX AREA (MILOPS / SeeNotam / id=EBD32)
            #    [C] FLORENNES (CTA / ATS / SeeNotam / id=EBFS)
            #    [W] TOURNAI/MAUBRAY (R / GLIDER / id=EBS182)
            #    [W] LOW FLYING AREA GOLF TWO WEST (R / GLIDER / SeeNotam / id=EBS30)
            #    [Q] KOKSIJDE TRAINING AREA (MILOPS / id=EBLFA11)
            #    [R] KOKSIJDE LET-DOWN (MILOPS / id=EBR24B)
            #    [Q] IEPER HELICOPTER TRAINING AREA (MILOPS / SeeNotam / id=EBHTA10C)
            #    [R] KOKSIJDE CLIMB-OUT (JETCLIMB / id=EBR25)
            #    [Q] COASTAL HELICOPTER TRAINING AREA (MILOPS / SeeNotam / id=EBHTA10A)
            #    [RMZ] RADIO MANDATORY ZONE KORTRIJK (EQUIPMENT / id=EBKT RMZ)
            #    [TMZ] TRANSPONDER MANDATORY ZONE KORTRIJK (EQUIPMENT / id=EBKT TMZ)
            #    [Q] TOURNAI HELICOPTER TRAINING AREA (MILOPS / SeeNotam / id=EBHTA10D)
            #    [D] LILLE 2 (TMA / id=LFQQ2)
            #    [Q] BELOEIL (BALLOON / id=EBS02)

        return
