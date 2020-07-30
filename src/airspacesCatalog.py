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

            if self.isCleanArea4FreeFlight(sKeyFile, oAs):                                             #Exclure certaines zones
                oAs.update({"freeFlightZone":False})
                oAs.update({"excludeAirspaceByFilter":True})

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
        #if "excludeAirspaceNotCoord" in oAs:
        #    if oAs["excludeAirspaceNotCoord"]:     return False     #Exclure les zones sans bordures identifiées

        if sKeyFile == "BPa-Test4Clean":
            #Test de suppression manuel d'une zone en mer - [Q] 18 B1 (id=LFD18B1)
            if oAs["id"] in ["LFD18B1"]:
                ret = False

        elif sKeyFile == "EuCtrl":
            #Supprimer les zones
            #    [D] ALBERT BRAY (CTR / id=LFAQ)   - car mauvais tracé et récupération via le fichier SIA
            if oAs["id"] in ["LFAQ"]:
                ret = False

        if not(ret):
            self.oLog.info("Unvalid area by manual filter - ({0}){1}".format(sKeyFile, oAs["UId"], oAs["id"], outConsole=False))
        return ret

    #Flager certaine zone 'inutile' pour la vision 'freeflight'
    def isCleanArea4FreeFlight(self, sKeyFile:str, oAs:dict) -> bool:
        ret:bool = False                                    #Default value
        if not oAs["freeFlightZone"]:   return ret          #Exclure les zones de non concernées

        if sKeyFile == "BPa-Test4AppDelta":
            #Test de suppression volontaire
            if oAs["id"] in ["LFRD02"]:
                ret = True

        elif sKeyFile in ["EuCtrl","SIA"]:
            #    [R] BRUSSELS FIR (RMZ / EQUIPMENT / id=EBBU RMZ)
            #    [P] BRUSSELS FIR (TMZ / EQUIPMENT / id=EBBU TMZ)
            #    [E] LA REUNION 1 (TMA / id=FMEE1)
            #    [Q] 18 B1 (id=LFD18B1)                     - en mer, face au finistere
            #    [Q] 18 A5 (id=LFD18A5)                     - en mer, face au finistere
            #    [Q] 214 (SeeNotam / id=LFD214)             - en mer, face au finistere
            #    [D] ILES ANGLO NORMANDES (CTR / id=EGJJ)   - en mer...
            #    [A] ILES ANGLO NORMANDES (TMA / id=EGJJ1)
            #    [C] CHANNEL ISLANDS TMA SOUTH (TMA / id=EGJJS)
            #    [D] CHANNEL ISLANDS CTR SOUTH (CTR / id=EGJA-2)
            #    [D] LORIENT 1 (TMA / id=LFRH1)
            #    [Q] 18 B3 (id=LFD18B3)
            #    [Q] 16 D (SeeNotam / id=LFD16D)
            #    [R] 13 C (SeeNotam / id=LFR13C)
            #    [Q] 18 B2 (id=LFD18B2)                     - en mer...
            #    [Q] 31 D (id=LFD31)                        - en mer...
            #    [Q] 32 (id=LFD32)                          - en mer...
            #    [Q] 18 A4 (id=LFD18A4)                     - en mer
            #    [E] TAHITI.20 (OCA / id=OCA4521.20)        * aucun interet...
            if oAs["id"] in ["EBBU RMZ","EBBU TMZ","FMEE1","LFD18B1","LFD18A5","LFD214","EGJJ","EGJJ1","EGJJS","EGJA-2","LFRH1","LFD18B3","LFD16D","LFR13C","LFD18B2","LFD31","LFD32","LFD18A4","OCA4521.20"]:
                ret = True

        if (ret):
            self.oLog.info("Ignored freeflight area by manual filter - ({0}){1}".format(sKeyFile, oAs["UId"], oAs["id"], outConsole=False))
        return ret

