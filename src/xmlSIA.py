#!/usr/bin/env python3

from bs4 import BeautifulSoup
import bpaTools
import aixmReader

cstFreqTypePriority:list = ["APP","TWR","FIS","AFIS","ATIS"]  #Priorisation des typologies de fréquence radio

def getMasterFrequecy(oFreqs:dict, sTypeZone:str="") -> str:
    sFreqType:str = "xxx"
    sFreq:str = None
    sPhone:str = None
    if sTypeZone == "TMA":              #Cas d'une TMA
        sFreqType = "APP"               #Prendre la Fréqunce d'APProche
        if not sFreqType in oFreqs:
            sFreqType = "TWR"           #A défaut, prendre la Fréqunce de la Tour-de-Control
    elif sTypeZone == "CTR":            #Cas d'une CTR
        sFreqType = "TWR"               #Prendre la Fréqunce de la Tour-de-Control
        if not sFreqType in oFreqs:
            sFreqType = "APP"           #A défaut, prendre la Fréqunce d'APProche
    if sFreqType in oFreqs:
        sFreq = oFreqs[sFreqType][0]
        if len(oFreqs[sFreqType]) == 3:
            sPhone = oFreqs[sFreqType][2]
    else:
        for sFreqType in cstFreqTypePriority:
            if sFreqType in oFreqs:
                sFreq = oFreqs[sFreqType][0]
                if len(oFreqs[sFreqType]) == 3:
                    sPhone = oFreqs[sFreqType][2]                
                break
    if sFreq!=None:
        if sFreq[-1]=="*":
            sFreq = sFreq[:-1]
        sFreq = sFreqType[0].upper() + sFreqType[1:].lower() + "(" + sFreq 
        if sPhone!=None:
            sFreq += " / " + sPhone
        sFreq += ")"
    return sFreq

class XmlSIA:
    
    def __init__(self, oLog):
        bpaTools.initEvent(__file__, oLog)
        self.oLog = oLog
        self.sKeyFile:str = None
        self.doc:BeautifulSoup = None
        self.oFrequecies:dict = {}
        return

    def openFile(self, sSrcFile:str, sKeyFile:str) -> None:
        #self.sSrcFile = sSrcFile
        self.sKeyFile = sKeyFile
        sTitle = "Xml parsing file - {0}".format(self.sKeyFile)
        self.oLog.info(sTitle, outConsole=True)
        self.doc = BeautifulSoup(open(sSrcFile, "r", encoding="utf-8"), "xml", from_encoding="utf-8")
        #self.doc = BeautifulSoup(open(sSrcFile, 'r', encoding="ISO-8859-1"), "xml", from_encoding="ISO-8859-1") 	   #or encoding="cp1252"
        #with open(sSrcFile, 'r', encoding='iso-8859-1') as f_in:
        #    f_in.readline()  # skipping header and letting soup create its own header
        #self.doc = BeautifulSoup(f_in.read(), 'xml', from_encoding='ISO-8859-1')
        
        root = self.doc.find("SiaExport")
        self.srcVersion = root['Version']
        self.srcOrigin = root['Origine']
        self.srcCreated = root['Date']
        return
    
    def syncFrequecies(self, oCat:dict) -> None:
        sTitle = "Airspaces frequencies"
        sMsg = "Synchronyse {0}".format(sTitle)
        self.oLog.info(sMsg)
        barre = bpaTools.ProgressBar(len(self.oFrequecies), 20, title=sMsg)
        idx = 0
        for sAsKey, oFreqs in self.oFrequecies.items():
            idx+=1
            
            #OLD - Organiser les frequences radio par un tri alphabétique des typologies
            #oNewFrequencies:dict = {}
            #aFreqKeySort = sorted(oFreqs.keys())
            #for sFreqKey in aFreqKeySort:
            #    oNewFrequencies.update({sFreqKey:oFreqs[sFreqKey]})
            
            #NEW - Organiser les frequences radio par la priorisation des typologies
            oNewFrequencies:dict = {}
            aFreqKeySort = sorted(oFreqs.keys())
            for sFreqType in cstFreqTypePriority:
                for sFreqKey in aFreqKeySort:
                    if sFreqKey[0:len(sFreqType)] == sFreqType:
                        oNewFrequencies.update({sFreqKey:oFreqs[sFreqKey]})
            for sFreqKey in aFreqKeySort:
                if not (sFreqKey in oNewFrequencies):
                    oNewFrequencies.update({sFreqKey:oFreqs[sFreqKey]})                    
   
            #Localisation principale
            sGUID:str = sAsKey
            self.affecFrequecies(oCat, sGUID, oNewFrequencies)
            self.syncGUIDdoublons(oCat, sGUID, oNewFrequencies)
                    
            #Complement de recherche pour extension de zone
            #Exp: LFBD + LFBD1-1 + LFBD1-2 + LFBD2-1 + LFBD2-2 ../.. + LFBD7 + LFBD7.10 + LFBD7.20 + ../.. + LFBD10
            #Exp: LFLC + LFLC1 + LFLC1.20 + LFLC2.1 + LFLC2.1.20
            #Warning! des '-', des '.' ou des '0' finaux commes LFBD7.10 et LFBD7.20
            for lIdx1 in range(1, 20):
                #Ajout indice sur clé locale pour localiser les extentions des zone
                sGUID1:str = sGUID + str(lIdx1)
                self.affecFrequecies(oCat, sGUID1, oNewFrequencies)
                self.syncGUIDdoublons(oCat, sGUID1, oNewFrequencies)
                self.syncGUID0(oCat, sGUID1, oNewFrequencies, "-")
                self.syncGUID0(oCat, sGUID1, oNewFrequencies, ".")
                
            #else:
            #    self.oLog.error("syncFrequecies() - Airspace not found {0} - {1}".format(sAsKey, oFreqs), outConsole=False)
            barre.update(idx)
        barre.reset()
        return

    #Complement de recherche pour déboublonnage de zone
    def syncGUIDdoublons(self, oCat:dict, sGUID:str, oNewFrequencies) -> None:
        for lIdx in range(1, 10):
            sGUID0:str = sGUID + "@@-" + str(lIdx)     #Ajout indice de déblonnage de clé locale
            self.affecFrequecies(oCat, sGUID0, oNewFrequencies)        
        return

    #Ajout indice sur clé locale pour localiser les extentions des zone
    def syncGUID0(self, oCat:dict, sGUID:str, oNewFrequencies, sSep:str) -> None:
        for lIdx in range(1, 20):
            sGUID0:str = sGUID + sSep + str(lIdx)
            self.affecFrequecies(oCat, sGUID0, oNewFrequencies)
            self.syncGUID1(oCat, sGUID0, oNewFrequencies, "-")
            self.syncGUID1(oCat, sGUID0, oNewFrequencies, ".")
            sGUID0 += "0"
            self.affecFrequecies(oCat, sGUID0, oNewFrequencies)
        return

    #Ajout indice sur clé locale pour localiser les extentions des zone
    def syncGUID1(self, oCat:dict, sGUID:str, oNewFrequencies, sSep:str) -> None:
        for lIdx in range(1, 20):
            sGUID0:str = sGUID + sSep + str(lIdx)
            self.affecFrequecies(oCat, sGUID0, oNewFrequencies)
            sGUID0 += "0"
            self.affecFrequecies(oCat, sGUID0, oNewFrequencies)                    
        return

    def affecFrequecies(self, oCat:dict, sGUID:str, oNewFrequencies) -> None:
        if sGUID in oCat:       #test de présence
            oAs = oCat[sGUID]
            oAs.update({"Mhz":oNewFrequencies})
            oAs.update({"nameV":aixmReader.getVerboseName(oAs)})
            #Data Quality Control
            #if "desc" in oAs:
            #    sDesc = oAs["desc"]
            #    sFreq = getMasterFrequecy(oNewFrequencies)
            #    sFreq = sFreq.replace("*","")
            #    if not sFreq:
            #        self.oLog.warning("syncFrequecies() - MasterFrequency not found {0} - {1}".format(oFreqs), outConsole=False)
            #    if sDesc.find(sFreq) < 0:
            #        self.oLog.warning("syncFrequecies() - Data Quality - MasterFrequency not found in Description GUIf={0} - MasterFrequency={1} - [{2}] - Description={3}".format(sAsKey, sFreq, oFreqs, sDesc), outConsole=False)
        return
    
	#<Frequence pk="14660" lk="[LF][RK][TWR CAEN Tour][134.525]">
	#	<Service pk="1760" lk="[LF][RK][TWR CAEN Tour]"/>
    #	<Frequence>134.525</Frequence>
	#	<HorCode>HO</HorCode>
	#</Frequence>   
    def loadFrequecies(self) -> None:
        sTitle = "Airspaces frequencies"
        sXmlTag = "Frequence"
        if not self.doc.find(sXmlTag):
            sMsg = "Missing tags {0} - {1}".format(sXmlTag, sTitle)
            self.oLog.warning(sMsg, outConsole=True)
            return

        sMsg = "Indexing {0} - {1}".format(sXmlTag, sTitle)
        self.oLog.info(sMsg)
        oList = self.doc.find_all(sXmlTag)
        barre = bpaTools.ProgressBar(len(oList), 20, title=sMsg)
        idx = 0
        #oFreqKey:dict = {}
        #oHorCode:dict = {}
        #oRemarque:dict = {}
        for o in oList:
            idx+=1
            if len(o)>1:                                            #Exclure les tags interne de type '<Frequence>360.125</Frequence>'
                sFreq = o.Frequence.string
                if (float(sFreq)>=118) and (float(sFreq)<=136):
                    sLocKey:str = o["lk"]                           #lk="[LF][RK][TWR CAEN Tour][134.525]
                    sLocKey = sLocKey.replace("[", "")
                    aLocKey:list = sLocKey.split("]")
                    if len(aLocKey)>=3:                             #Exclure les Frequences sans référence exp - <Frequence lk="null[122.100]" pk="300054">
                        sAsKey:str = aLocKey[0] + aLocKey[1]        #AirspaceKey  = 'LFRK'
                        aFreqKey:list = aLocKey[2].split(" ")            
                        sFreqKey:str = aFreqKey[0]                  #FrequenceKey = 'TWR','APP' etc...
                        bExclude:bool = bool(sFreqKey in ["VDF","UAC","UTA","SRE","CEV","PAR"])   #Exclure certains typage de fréquences
                        if not bExclude and o.Remarque:     #Exclure certaines fréquences non utiles
                            sRem:str = o.Remarque.string
                            bExclude = bExclude or ("ur instruction" in sRem.lower())   #'Sur instruction ../..' ou 'FREQ sur instruction' etc...
                            bExclude = bExclude or ("radar" in sRem.lower())            #'Sur instruction ../..' ou 'FREQ sur instruction' etc...
                            bExclude = bExclude or (sRem[0:24] == "Diffusion des paramètres")
                            bExclude = bExclude or (sRem[0:10] == "Exploitant")
                            bExclude = bExclude or (sRem[0:15] == "CTL ACFT au sol")
                            bExclude = bExclude or (sRem[0:20] == "Contrôle ACFT au sol")
                            bExclude = bExclude or (sRem[0:18] == "Circulation au sol")
                            bExclude = bExclude or (sRem[0:13] == "Fréquence SOL")
                            bExclude = bExclude or (sRem[0: 7] == "Roulage")
                            bExclude = bExclude or (sRem[0:11] == "FREQ Départ")
                            bExclude = bExclude or (sRem[0:15] == "FREQ de secours")
                            bExclude = bExclude or (sRem[0:37] == "Au profit des postes de stationnement")
                            bExclude = bExclude or (sRem[0: 8] == "Détresse")
                            bExclude = bExclude or (sRem[0:27] == "Coordinations des activités")
                        if not bExclude:
                            bExclude = bExclude or (aLocKey[2][0:3]=="TWR" and aLocKey[2][-3:]=="Sol")        #[TWR SAINT YAN Sol] a filtrer / [TWR SAINT YAN Tour] a garder
                            bExclude = bExclude or (aLocKey[2][0:3]=="TWR" and aLocKey[2][-6:]=="Prévol")
                            bExclude = bExclude or (aLocKey[2][0:3]=="TWR" and aLocKey[2][-1:]==".")          #[LF][MD][TWR LERINS .] a filtrer / [TWR CANNES Tour] a garder
                            bExclude = bExclude or (aLocKey[2][0:3]=="APP" and aLocKey[2][-8:]=="Contrôle")   #[APP BALE Contrôle] a filtrer / [APP ... Approche] a garder
                        if not bExclude:        #Memorisation de fréquence
                            if not sAsKey in self.oFrequecies:
                                self.oFrequecies.update({sAsKey:{}})
                            oFreqList:dict = self.oFrequecies[sAsKey]
                            if o.HorCode.string != "H24":
                                sFreq += "*"                            #(*) = Horaire non permanent
                            aDetFreq:list = [sFreq]
                            if o.Remarque:
                                sRem:str = aixmReader.AixmTools(None).getField(o, "Remarque", "ret")["ret"]
                                aDetFreq.append(sRem)
                                sPhone:str = self.getPhoneNumber(sRem)
                                if sPhone:
                                    aDetFreq.append(sPhone)
                            if o.Suppletive:
                                bSupp:bool = True if str(o.Suppletive.string).lower=="oui" else False
                                sFreqKey = self.makeNewKey(sFreqKey, oFreqList, bSupp)
                            else:
                                sFreqKey = self.makeNewKey(sFreqKey, oFreqList)
                            oFreqList.update({sFreqKey:aDetFreq})
                    #Analyses
                    #oFreqKey.update({sFreqKey:sFreqKey})
                    #sObj:str = o.HorCode.string
                    #oHorCode.update({sObj:sObj})
                    #if o.Remarque:
                    #    sObj:str = o.Remarque.string
                    #    oRemarque.update({sObj:sObj})
            barre.update(idx)
        barre.reset()
        #self.oLog.info("oFreqKey={}".format(oFreqKey)) --> 2020-08-21 14:49:33,261 poaff v2.0.3 INFO oFreqKey={'VDF': 'VDF', 'UAC': 'UAC', 'APP': 'APP', 'AFIS': 'AFIS', 'TWR': 'TWR', 'ATIS': 'ATIS', 'FIS': 'FIS', 'null': 'null', 'A/A': 'A/A', 'SRE': 'SRE', 'CEV': 'CEV', 'PAR': 'PAR', '': '', 'CCM': 'CCM'}
        #self.oLog.info("oHorCode={}".format(oHorCode)) --> 2020-08-21 14:49:33,261 poaff v2.0.3 INFO oHorCode={'HO': 'HO', 'HX': 'HX', 'H24': 'H24'}
        #self.oLog.info("oRemarque={}".format(oRemarque)) --> 2020-08-24 15:59:55,798 poaff v2.0.3 INFO oRemarque={'Canal 8.33': 'Canal 8.33', 'Particulière transit/Particular to transit': 'Particulière transit/Particular to transit', 'Exploitant/Operator : DAC Polynésie Française': 'Exploitant/Operator : DAC Polynésie Française', 'Plus toutes fréquences de LORIENT / Over all frequencies from LORIENT.': 'Plus toutes fréquences de LORIENT / Over all frequencies from LORIENT.', 'Exploitant/Operator : Aéroport de Tahiti': 'Exploitant/Operator : Aéroport de Tahiti', 'TEL : 01 39 56 54 70': 'TEL : 01 39 56 54 70', 'Exploitant/Operator : DAC POLYNESIE FRANCAISE': 'Exploitant/Operator : DAC POLYNESIE FRANCAISE', 'Air/sol - Air /ground': 'Air/sol - Air /ground', 'Auto-information en Français uniquement.': 'Auto-information en Français uniquement.', 'Exploitant/Operator : Territoire': 'Exploitant/Operator : Territoire', 'Traversée maritime VFR et transit CTR.': 'Traversée maritime VFR et transit CTR.', 'Diffusion des paramètres de DEP et ARR.#\nDEP and ARR parameters broadcasting.': 'Diffusion des paramètres de DEP et ARR.#\nDEP and ARR parameters broadcasting.', "Transit CAG - RAI - Jusqu'au/until FL 200": "Transit CAG - RAI - Jusqu'au/until FL 200", 'Exploitant/Operator : AVA': 'Exploitant/Operator : AVA', 'Exploitant/Operator : AVA#Assure APP/APP operations': 'Exploitant/Operator : AVA#Assure APP/APP operations', 'Sur instruction TWR pour circulation au sol.': 'Sur instruction TWR pour circulation au sol.', 'TEL : 05 62 47 53 27': 'TEL : 05 62 47 53 27', 'FR seulement / only': 'FR seulement / only', 'Canal 8.33#\nTEL : 02 98 32 02 02': 'Canal 8.33#\nTEL : 02 98 32 02 02', 'SKED : See NOTAM': 'SKED : See NOTAM', 'FR#\nEnglish language possible for commercial flights only with PPR 96 HR via E-mail : aeroport@caba.fr': 'FR#\nEnglish language possible for commercial flights only with PPR 96 HR via E-mail : aeroport@caba.fr', 'COS 25 NM/FL 030.': 'COS 25 NM/FL 030.', 'Information/Radar SIV 3 et 5': 'Information/Radar SIV 3 et 5', 'Diffusion des parametres DEP et ARR.TEL 0320161954.': 'Diffusion des parametres DEP et ARR.TEL 0320161954.', 'Exploitant/Operator : Collectivité de Saint-Barthélemy#HOR ATS : 1100 - SS+15': 'Exploitant/Operator : Collectivité de Saint-Barthélemy#HOR ATS : 1100 - SS+15', 'Secteur Ouest-Contrôle en TMA': 'Secteur Ouest-Contrôle en TMA', 'FR seulement/only': 'FR seulement/only', 'Exploitant/Operator : Conseil général#Renseignements sur ouverture / Information during opening : TWR ST PIERRE (0508 41 18 22).': 'Exploitant/Operator : Conseil général#Renseignements sur ouverture / Information during opening : TWR ST PIERRE (0508 41 18 22).', 'FR uniquement.': 'FR uniquement.', 'Absence ATS : A/A FR seulement/only': 'Absence ATS : A/A FR seulement/only', 'NIL': 'NIL', 'Réservée au trafic civil avec ACFT CIV HNO : RAI / reserved for CIV traffic with CIV ACFT during HNO: automatic info transmitter': 'Réservée au trafic civil avec ACFT CIV HNO : RAI / reserved for CIV traffic with CIV ACFT during HNO: automatic info transmitter', 'RAI / Automatic info transmitter': 'RAI / Automatic info transmitter', 'Fréquence TOUR / Tower frequency': 'Fréquence TOUR / Tower frequency', 'Secteur Est-Contrôle en TMA': 'Secteur Est-Contrôle en TMA', 'HOR ATS : 1100 - SS + 15': 'HOR ATS : 1100 - SS + 15', 'Secteur Ouest': 'Secteur Ouest', 'Canal 8.33 : diffusion paramètres ARR/DEP et activité zones LF-R 125 et LF-R 127.': 'Canal 8.33 : diffusion paramètres ARR/DEP et activité zones LF-R 125 et LF-R 127.', 'Canal 8.33 : contrôle ACFT au sol sauf RWY': 'Canal 8.33 : contrôle ACFT au sol sauf RWY', 'Exploitant/Operator :  DAC Polynésie Française': 'Exploitant/Operator :  DAC Polynésie Française', "Canal 8.33 : sur instruction ATC jusqu'au FL 100": "Canal 8.33 : sur instruction ATC jusqu'au FL 100", 'Exploitant/Operator : Territoire - FR seulement / only': 'Exploitant/Operator : Territoire - FR seulement / only', 'Canal 25': 'Canal 25', 'Canal 25 : pour décollage et approche finale.': 'Canal 25 : pour décollage et approche finale.', 'Transit VFR dans CTR et TMA de LORIENT. / Transit VFR within LORIENT CTR and TMA.': 'Transit VFR dans CTR et TMA de LORIENT. / Transit VFR within LORIENT CTR and TMA.', "jusqu'au FL200/up to FL200": "jusqu'au FL200/up to FL200", 'Canal 8.33#\nFREQ sur instruction ATC pour JH': 'Canal 8.33#\nFREQ sur instruction ATC pour JH', 'RAIZ en cas de fermeture du FIS/when FIS closed': 'RAIZ en cas de fermeture du FIS/when FIS closed', 'SIV 7': 'SIV 7', 'Air-Sol VHF - Veillée / VHF Air-Ground - Monitored': 'Air-Sol VHF - Veillée / VHF Air-Ground - Monitored', "Jusqu'au FL200/Up to FL200": "Jusqu'au FL200/Up to FL200", 'ATIS disponible au 03 88 59 94 16': 'ATIS disponible au 03 88 59 94 16', 'Particulère Transit VFR / Particular VFR transit.': 'Particulère Transit VFR / Particular VFR transit.', 'FREQ sur instruction': 'FREQ sur instruction', 'Canal 8.33.# TEL : 03 44 84 69 41': 'Canal 8.33.# TEL : 03 44 84 69 41', 'APP : secteur Ouest portée réduite, inutilisable en-dessous de 10 000 ft.#\nFréquence RAI quand AD fermé./\nAPP : West sector range reduced, unavailable below 10 000 ft.#\nRAI frequency when AD closed.': 'APP : secteur Ouest portée réduite, inutilisable en-dessous de 10 000 ft.#\nFréquence RAI quand AD fermé./\nAPP : West sector range reduced, unavailable below 10 000 ft.#\nRAI frequency when AD closed.', 'FR seulement/only. TEL 01 60 04 88 75': 'FR seulement/only. TEL 01 60 04 88 75', 'TEL +33(0)4 67 90 88 88': 'TEL +33(0)4 67 90 88 88', 'Fréquence supplétive / Auxilary frequency': 'Fréquence supplétive / Auxilary frequency', 'Secteur OUEST': 'Secteur OUEST', 'ALT antenne/antenna : 1440 m': 'ALT antenne/antenna : 1440 m', 'Tél. 05 59 22 43 72': 'Tél. 05 59 22 43 72', 'TEL : (689) 40 86 13 00': 'TEL : (689) 40 86 13 00', 'TEL : +33 5 62 32 62 68': 'TEL : +33 5 62 32 62 68', 'APP TOULOUSE (SFC/FL075 Secteur Albi-Castres-Carcassonne).': 'APP TOULOUSE (SFC/FL075 Secteur Albi-Castres-Carcassonne).', 'Information/Radar SIV 1': 'Information/Radar SIV 1', 'Secteur OUEST - Contrôle en TMA.#\nAppareils non-équipés 8,33 KHz : voir AD 2 LFBO.23.#\nWest sector - Control within TMA.#\nAircraft non 8.33 KHz-equipped : see AD 2 LFBO.23.': 'Secteur OUEST - Contrôle en TMA.#\nAppareils non-équipés 8,33 KHz : voir AD 2 LFBO.23.#\nWest sector - Control within TMA.#\nAircraft non 8.33 KHz-equipped : see AD 2 LFBO.23.', 'Secteur EST - Contrôle en TMA.#\nAppareils non-équipés 8,33 KHz : voir AD 2 LFBO.23.#\nEast Sector - Control within TMA.#\nAircraft non 8.33 KHz-equipped : see AD 2 LFBO.23.': 'Secteur EST - Contrôle en TMA.#\nAppareils non-équipés 8,33 KHz : voir AD 2 LFBO.23.#\nEast Sector - Control within TMA.#\nAircraft non 8.33 KHz-equipped : see AD 2 LFBO.23.', 'Canal 8.33 : RAI : activation/désactivation des secteurs T1/T2/T3 (espaces délégués Zürich).': 'Canal 8.33 : RAI : activation/désactivation des secteurs T1/T2/T3 (espaces délégués Zürich).', 'Exploitant / operator : Syndicat Mixte de Pierrefonds': 'Exploitant / operator : Syndicat Mixte de Pierrefonds', 'canal 8.33': 'canal 8.33', 'Assistance au VFR dans le SIV TOULOUSE.': 'Assistance au VFR dans le SIV TOULOUSE.', 'FR seulement HO': 'FR seulement HO', 'VFR en espace D sur instruction CTL-POS 40/FL150.#\nAppareils non-équipés 8,33 KHz : voir AD 2 LFBO.23.#\nVFR in class D airspace, with instruction CTL-POS 40/FL150.#\nAircraft non 8.33 KHz-equipped : see AD 2 LFBO.23.': 'VFR en espace D sur instruction CTL-POS 40/FL150.#\nAppareils non-équipés 8,33 KHz : voir AD 2 LFBO.23.#\nVFR in class D airspace, with instruction CTL-POS 40/FL150.#\nAircraft non 8.33 KHz-equipped : see AD 2 LFBO.23.', 'FREQ Zone Industrielle Nord. FR seulement/only.': 'FREQ Zone Industrielle Nord. FR seulement/only.', 'Information/Radar SIV 2 et 4': 'Information/Radar SIV 2 et 4', '#\nAu profit des postes de stationnement A, B, C, D, E, F, J, K et L.#\nIn respect of parking stands A, B, C, D, E, F, J, K and L.#\nCanal 8.33': '#\nAu profit des postes de stationnement A, B, C, D, E, F, J, K et L.#\nIn respect of parking stands A, B, C, D, E, F, J, K and L.#\nCanal 8.33', 'Au profit des postes de stationnement B et D. / In respect of parking stands B and D.#Canal 8.33': 'Au profit des postes de stationnement B et D. / In respect of parking stands B and D.#Canal 8.33', 'Exploitant/Operator : AVA. HOR TWR/TWR SKED': 'Exploitant/Operator : AVA. HOR TWR/TWR SKED', 'Détresse/Distress VHF': 'Détresse/Distress VHF', 'TEL : 05 34 46 08 36': 'TEL : 05 34 46 08 36', 'FR seulement/only.': 'FR seulement/only.', 'Utilisée sur instruction / Used upon instruction': 'Utilisée sur instruction / Used upon instruction', 'Sur instruction CTL': 'Sur instruction CTL', 'Commune APP / Common to APP': 'Commune APP / Common to APP', '- TMA Montpellier parties 7, 8, 9 et de 14 à 23 / TMA Montpellier parts 7, 8, 9 and from 14 to 23.#\n- Volumes des TMA 3, 4 et 5 inclus dans le SIV Montpellier partie 5 / Volumes of TMA 3, 4 and 5 included in FIS Montpellier part 5.': '- TMA Montpellier parties 7, 8, 9 et de 14 à 23 / TMA Montpellier parts 7, 8, 9 and from 14 to 23.#\n- Volumes des TMA 3, 4 et 5 inclus dans le SIV Montpellier partie 5 / Volumes of TMA 3, 4 and 5 included in FIS Montpellier part 5.', 'FREQ veillée': 'FREQ veillée', 'TEL ATIS : 04 67 13 11 70': 'TEL ATIS : 04 67 13 11 70', 'Particulière transit - veillée - RAI / Particular to transit - monitored': 'Particulière transit - veillée - RAI / Particular to transit - monitored', 'ATIS/V-25NM/FL40': 'ATIS/V-25NM/FL40', 'Urgence/Emergency': 'Urgence/Emergency', 'ATIS/V-FR-Tel : 01 60 80 96 86': 'ATIS/V-FR-Tel : 01 60 80 96 86', 'RADAR': 'RADAR', 'AUTO-INFO Jour-Nuit/AUTO-INFO Day-Night': 'AUTO-INFO Jour-Nuit/AUTO-INFO Day-Night', 'ATIS/V-Fr. uniquement/only#TEL :01 30 85 09 86': 'ATIS/V-Fr. uniquement/only#TEL :01 30 85 09 86', 'ATIS/V-TEL 01 60 17 97 94': 'ATIS/V-TEL 01 60 17 97 94', 'Au profit du poste de stationnement F. / In respect of parking stand F.#Canal 8.33': 'Au profit du poste de stationnement F. / In respect of parking stand F.#Canal 8.33', "ACFT à l'ARR ou au DEP de METZ NANCY LORRAINE#\nACFT inbound or outbound METZ NANCY LORRAINE": "ACFT à l'ARR ou au DEP de METZ NANCY LORRAINE#\nACFT inbound or outbound METZ NANCY LORRAINE", 'GCA - APP Control': 'GCA - APP Control', "En l'absence AFIS, A/A en FR seulement.": "En l'absence AFIS, A/A en FR seulement.", 'Roulage / Taxiing': 'Roulage / Taxiing', 'SIV secteur NORD/NORTH sector.': 'SIV secteur NORD/NORTH sector.', 'SIV secteur SUD/SOUTH sector.#': 'SIV secteur SUD/SOUTH sector.#', "Dans l'espace du SIV situé sous CTR NOUMEA LA TONTOUTA partie 1.#In SIV airspace located under CTR NOUMEA LA TONTOUTA part 1.": "Dans l'espace du SIV situé sous CTR NOUMEA LA TONTOUTA partie 1.#In SIV airspace located under CTR NOUMEA LA TONTOUTA part 1.", "Dans l'espace du SIV situé sous TMA NOUMEA partie 1.4 ILES LOYAUTE.#In SIV airspace located under TMA NOUMEA part 1.4 ILES LOYAUTE.": "Dans l'espace du SIV situé sous TMA NOUMEA partie 1.4 ILES LOYAUTE.#In SIV airspace located under TMA NOUMEA part 1.4 ILES LOYAUTE.", 'FREQ veillée/monitored': 'FREQ veillée/monitored', 'FREQ utilisable sur instruction ATC.': 'FREQ utilisable sur instruction ATC.', "Radar mobile susceptible d'être déplacé sans préavis/Mobile radar likely to be displaced without prior notice": "Radar mobile susceptible d'être déplacé sans préavis/Mobile radar likely to be displaced without prior notice", 'Freq veillée/Monitored frequency': 'Freq veillée/Monitored frequency', 'RAI': 'RAI', 'Coordinations des activités ops. de la marine.': 'Coordinations des activités ops. de la marine.', 'Canal 8.33.#FREQ utilisable sur instruction ATC.': 'Canal 8.33.#FREQ utilisable sur instruction ATC.', 'SRE CENTAURE': 'SRE CENTAURE', 'O/R APP': 'O/R APP', 'Roulage VHF - Veillée / VHF taxiing - Monitored': 'Roulage VHF - Veillée / VHF taxiing - Monitored', 'Détresse - Veillée / Distress - Monitored': 'Détresse - Veillée / Distress - Monitored', 'O/T RAIZ - FREQ veillée/monitored': 'O/T RAIZ - FREQ veillée/monitored', 'Fréquence SOL / Ground frequency': 'Fréquence SOL / Ground frequency', 'Détresse/Distress': 'Détresse/Distress', 'Particular Air-sol/Particular Air-Ground': 'Particular Air-sol/Particular Air-Ground', "FREQ information de vol planeurs selon protocole. Sur instruction ATC#\nGlider's flight information FREQ. With ATC instruction.": "FREQ information de vol planeurs selon protocole. Sur instruction ATC#\nGlider's flight information FREQ. With ATC instruction.", 'SIV 1, SIV 5 et/and SIV 6': 'SIV 1, SIV 5 et/and SIV 6', 'Diffusion des paramètres de DEP et ARR.': 'Diffusion des paramètres de DEP et ARR.', "ETE : 0700 - maximum de SS+30 et 1900, limité à 2100.#HIV : 0800 - maximum de SS+30 et 1900, limité à 2100.#En-dessous de 4500ft AMSL, contact radio non garanti à l'Ouest de PARIS INFO OUEST (région L'Aigle, Falaise et Mortagne au Perche).": "ETE : 0700 - maximum de SS+30 et 1900, limité à 2100.#HIV : 0800 - maximum de SS+30 et 1900, limité à 2100.#En-dessous de 4500ft AMSL, contact radio non garanti à l'Ouest de PARIS INFO OUEST (région L'Aigle, Falaise et Mortagne au Perche).", 'Canal 25 : supplétive sur instruction ATC': 'Canal 25 : supplétive sur instruction ATC', "Protection 50 NM jusqu'au FL250.": "Protection 50 NM jusqu'au FL250.", "Fréquence auxilliaire d'opération SAR. Exploitant AVA": "Fréquence auxilliaire d'opération SAR. Exploitant AVA", 'Exploitant AVA. Au sud du RDL 264° SDG': 'Exploitant AVA. Au sud du RDL 264° SDG', 'Exploitant AVA': 'Exploitant AVA', 'Fr. uniquement': 'Fr. uniquement', "Exploitant : Ville d'Ouessant. - O/R pour transport et EVASAN.": "Exploitant : Ville d'Ouessant. - O/R pour transport et EVASAN.", 'Particulière radar / Particular to radar': 'Particulière radar / Particular to radar', "Particulière Radar - Peut utiliser toutes les fréquences de l'APP / Particular to radar - Can use all the APP frequencies": "Particulière Radar - Peut utiliser toutes les fréquences de l'APP / Particular to radar - Can use all the APP frequencies", 'Détresse civile - veillée/Civilian distress - monitored': 'Détresse civile - veillée/Civilian distress - monitored', 'Détresse civile - veillée / Civilian distress - monitored': 'Détresse civile - veillée / Civilian distress - monitored', 'Utilisation suspendue.': 'Utilisation suspendue.', 'ETE : 0700 - maximum de SS+30 et 1900, limité à 2100.#HIV : 0800 - maximum de SS+30 et 1900, limité à 2100.#Contact radio non garanti sous 2000ft AMSL dans PARIS INFO NORD.#Contact radio et/ou radar non garanti sous 3500ft AMSL au Nord-Est de PARIS INFO NORD (région Sedan Charleville Mézières).': 'ETE : 0700 - maximum de SS+30 et 1900, limité à 2100.#HIV : 0800 - maximum de SS+30 et 1900, limité à 2100.#Contact radio non garanti sous 2000ft AMSL dans PARIS INFO NORD.#Contact radio et/ou radar non garanti sous 3500ft AMSL au Nord-Est de PARIS INFO NORD (région Sedan Charleville Mézières).', 'ETE : 0700 - maximum de SS+30 et 1900, limité à 2100.#HIV : 0800 -  maximum de SS+30 et 1900, limité à 2100.#Contact radio non garanti sous 1500ft AMSL dans PARIS SUD INFO.': 'ETE : 0700 - maximum de SS+30 et 1900, limité à 2100.#HIV : 0800 -  maximum de SS+30 et 1900, limité à 2100.#Contact radio non garanti sous 1500ft AMSL dans PARIS SUD INFO.', 'Commune GCA - non veillée / Common to GCA - not monitored': 'Commune GCA - non veillée / Common to GCA - not monitored', 'Particulière GCA - non veillée / Particular to GCA - not monitored': 'Particulière GCA - non veillée / Particular to GCA - not monitored', 'HOR : voir/see AD 2 NWWM.3#CTR NOUMEA MAGENTA parties 1 et 2 / parts 1 and 2#Absence ATS : A/A FR seulement/only#Exploitant/Operator : AVA': 'HOR : voir/see AD 2 NWWM.3#CTR NOUMEA MAGENTA parties 1 et 2 / parts 1 and 2#Absence ATS : A/A FR seulement/only#Exploitant/Operator : AVA', 'TWR / APP': 'TWR / APP', "Jusqu'au FL200 / Up to FL200": "Jusqu'au FL200 / Up to FL200", "Jusqu'au FL145 / Up to FL145": "Jusqu'au FL145 / Up to FL145", 'Exploitant/Operator : AVA.#HOR NOTAM / NOTAM SKED (voir/see AD 2 NWWE.3)': 'Exploitant/Operator : AVA.#HOR NOTAM / NOTAM SKED (voir/see AD 2 NWWE.3)', 'Fréquence pour régulation radar / Frequency for radar sequencing': 'Fréquence pour régulation radar / Frequency for radar sequencing', 'Secteur BE.': 'Secteur BE.', 'Secteur BW.': 'Secteur BW.', 'Freq veillée.RAI/Monitored frequency.Automatical information transmitter': 'Freq veillée.RAI/Monitored frequency.Automatical information transmitter', 'SIV IROISE 3 hors/out LANDIVISIAU SKED': 'SIV IROISE 3 hors/out LANDIVISIAU SKED', "Fréquence d'information.": "Fréquence d'information.", "Jusqu'au FL200": "Jusqu'au FL200", 'Au profit des postes de stationnement I.#\nIn favour of parking stands I.\n#Canal 8.33': 'Au profit des postes de stationnement I.#\nIn favour of parking stands I.\n#Canal 8.33', 'Principale': 'Principale', 'Diffusion des paramètres de DEP et ARR (EN)/ARR-DEP parameters broadcasting(EN).#Canal 8.33': 'Diffusion des paramètres de DEP et ARR (EN)/ARR-DEP parameters broadcasting(EN).#Canal 8.33', 'Au profit des postes de stationnement A, C et E. / In respect of parking stands A, C and E.#Canal 8.33': 'Au profit des postes de stationnement A, C et E. / In respect of parking stands A, C and E.#Canal 8.33', 'FREQ sur instruction UAC UN / UB /KN /YB /HN /UR /XR /KR /HR /KF /KD': 'FREQ sur instruction UAC UN / UB /KN /YB /HN /UR /XR /KR /HR /KF /KD', 'Fréquence supplétive CTR NOUMEA LA TONTOUTA parties 1 et 2.#\nAuxiliary frequency CTR NOUMEA LA TONTOUTA parts 1 and 2.': 'Fréquence supplétive CTR NOUMEA LA TONTOUTA parties 1 et 2.#\nAuxiliary frequency CTR NOUMEA LA TONTOUTA parts 1 and 2.', 'TEL : 02 31 08 42 80': 'TEL : 02 31 08 42 80', 'Secteur COTENTIN/COTENTIN sector': 'Secteur COTENTIN/COTENTIN sector', 'TMA NOUMEA partie 1.1 TONTOUTA.# \nTMA NOUMEA part 1.1 TONTOUTA.': 'TMA NOUMEA partie 1.1 TONTOUTA.# \nTMA NOUMEA part 1.1 TONTOUTA.', 'Secteur Sud/South sector.': 'Secteur Sud/South sector.', 'Appareils non-équipés 8,33 KHz : voir AD 2 LFBO.23.#\nAircraft non 8.33 KHz-equipped : see AD 2 LFBO.23.': 'Appareils non-équipés 8,33 KHz : voir AD 2 LFBO.23.#\nAircraft non 8.33 KHz-equipped : see AD 2 LFBO.23.', 'CTR NOUMEA LA TONTOUTA parties 1 et 2/parts 1 and 2.': 'CTR NOUMEA LA TONTOUTA parties 1 et 2/parts 1 and 2.', 'Exploitant / operator : SNA/OI#\nService VDF (Gonio)': 'Exploitant / operator : SNA/OI#\nService VDF (Gonio)', "Jusqu'au FL100.#\nAppareils non-équipés 8,33 KHz : voir AD 2 LFBO.23.#\nUp to FL100.#\nAircraft non 8.33 KHz-equipped : see AD 2 LFBO.23.": "Jusqu'au FL100.#\nAppareils non-équipés 8,33 KHz : voir AD 2 LFBO.23.#\nUp to FL100.#\nAircraft non 8.33 KHz-equipped : see AD 2 LFBO.23.", 'Diffusion des paramètres de DEP et ARR. (FR)': 'Diffusion des paramètres de DEP et ARR. (FR)', 'AFIS SKED#Exploitant/operator : AVA#243°/486 m THR 26': 'AFIS SKED#Exploitant/operator : AVA#243°/486 m THR 26', 'HOR : Voir/see AD 2 NLWW.3#Exploitant/Operator : AVA': 'HOR : Voir/see AD 2 NLWW.3#Exploitant/Operator : AVA', 'Secteur SUD/South sector': 'Secteur SUD/South sector', 'Exploitant/Operator : AVA. HOR/SKED : voir/see AD 2 NWWL.3': 'Exploitant/Operator : AVA. HOR/SKED : voir/see AD 2 NWWL.3', 'Exploitant/Operator : AVA. HOR NOTAM': 'Exploitant/Operator : AVA. HOR NOTAM', "Protection jusqu'au FL 150. Approche Ouest.#Protection up to FL 150. West Approach.": "Protection jusqu'au FL 150. Approche Ouest.#Protection up to FL 150. West Approach.", '- TMA Montpellier parties 1, 2, 3.1, 4, 4.1, 6, 6.1 et de 10 à 13 / TMA Montpellier parts 1, 2, 3.1, 4, 4.1, 6, 6.1 and from 10 to 13#- Volumes des TMA Montpellier parties 3, 4, 5 inclus dans le SIV Montpellier partie 1 / Volumes of TMA Montpellier parts 3, 4, 5 included in FIS Montpellier part 1': '- TMA Montpellier parties 1, 2, 3.1, 4, 4.1, 6, 6.1 et de 10 à 13 / TMA Montpellier parts 1, 2, 3.1, 4, 4.1, 6, 6.1 and from 10 to 13#- Volumes des TMA Montpellier parties 3, 4, 5 inclus dans le SIV Montpellier partie 1 / Volumes of TMA Montpellier parts 3, 4, 5 included in FIS Montpellier part 1', 'TEL : 02 40 05 12 74': 'TEL : 02 40 05 12 74', 'TEL: 04 95 65 82 49': 'TEL: 04 95 65 82 49', 'HOR : voir/see AD 2 NWWM.3#TMA NOUMEA partie/part 1.2 MAGENTA#Exploitant/Operator : AVA': 'HOR : voir/see AD 2 NWWM.3#TMA NOUMEA partie/part 1.2 MAGENTA#Exploitant/Operator : AVA', 'Diffusion des paramètres de DEP et ARR/DEP and ARR parameters broadcasting TEL: (0)4.68.10.23.56': 'Diffusion des paramètres de DEP et ARR/DEP and ARR parameters broadcasting TEL: (0)4.68.10.23.56', 'HOR : HOR TWR#Exploitant/Operator : AVA': 'HOR : HOR TWR#Exploitant/Operator : AVA', 'TMA NOUMEA partie 1.3 ILE DES PINS et TMA NOUMEA parties 2 et 3 secteur SUD.#\nFréquence supplétive TMA NOUMEA partie 1.1 TONTOUTA et TMA NOUMEA partie 1.4 ILES LOYAUTE.#\nTMA NOUMEA part 1.3 ILE DES PINS and TMA NOUMEA parts 2 and 3 SOUTH sector.#\nAuxiliary frequency TMA NOUMEA part 1.1 TONTOUTA and TMA NOUMEA part 1.4 ILES LOYAUTE.': 'TMA NOUMEA partie 1.3 ILE DES PINS et TMA NOUMEA parties 2 et 3 secteur SUD.#\nFréquence supplétive TMA NOUMEA partie 1.1 TONTOUTA et TMA NOUMEA partie 1.4 ILES LOYAUTE.#\nTMA NOUMEA part 1.3 ILE DES PINS and TMA NOUMEA parts 2 and 3 SOUTH sector.#\nAuxiliary frequency TMA NOUMEA part 1.1 TONTOUTA and TMA NOUMEA part 1.4 ILES LOYAUTE.', 'FREQ arrivée Est.': 'FREQ arrivée Est.', 'TMA NOUMEA parties 2 et 3 Secteur NORD#\nTMA NOUMEA parts 2 and 3 NORTH sector.': 'TMA NOUMEA parties 2 et 3 Secteur NORD#\nTMA NOUMEA parts 2 and 3 NORTH sector.', 'FREQ arrivée Ouest.': 'FREQ arrivée Ouest.', 'TMA NOUMEA partie 1.4/part 1.4 ILES LOYAUTE.': 'TMA NOUMEA partie 1.4/part 1.4 ILES LOYAUTE.', 'CTL ACFT au sol.': 'CTL ACFT au sol.', 'FREQ sur instruction UAC UE /UH /UF /KF /XH /XE /KE /KH /HH /HE /KD /UR /XR /KR /HR': 'FREQ sur instruction UAC UE /UH /UF /KF /XH /XE /KE /KH /HH /HE /KD /UR /XR /KR /HR', "FREQ IFR et VFR en circuit d'aérodrome.": "FREQ IFR et VFR en circuit d'aérodrome.", 'FREQ réservée aux VFR en transit SA-EA et hélicoptères.': 'FREQ réservée aux VFR en transit SA-EA et hélicoptères.', 'TEL : 05 53 63 53 55': 'TEL : 05 53 63 53 55', 'Diffusion des paramètres de DEP et ARR (EN).': 'Diffusion des paramètres de DEP et ARR (EN).', 'SIV 2.1/2.2/2.3': 'SIV 2.1/2.2/2.3', 'FREQ pour TKOF et APCH finale toute condition MTO.': 'FREQ pour TKOF et APCH finale toute condition MTO.', 'Diffusion des paramètres de DEP et ARR (FR).': 'Diffusion des paramètres de DEP et ARR (FR).', '(1) En dehors de ces HOR, PPR PN 2HR TEL permanence gestionnaire.#(1) Outside these SKED, PPR 2HR TEL AD operator permanence': '(1) En dehors de ces HOR, PPR PN 2HR TEL permanence gestionnaire.#(1) Outside these SKED, PPR 2HR TEL AD operator permanence', 'FREQ " FIRE ".': 'FREQ " FIRE ".', 'FR seulement': 'FR seulement', 'FREQ réservée aux DEP.': 'FREQ réservée aux DEP.', 'Eléments de PLN et paramètres de DEP.': 'Eléments de PLN et paramètres de DEP.', "Protection jusqu'au FL 150. Approche Est.#Protection up to FL 150. East Approach.": "Protection jusqu'au FL 150. Approche Est.#Protection up to FL 150. East Approach.", 'SIV 1.1/1.2': 'SIV 1.1/1.2', 'ATIS/V-Tél : 01 30 56 38 02': 'ATIS/V-Tél : 01 30 56 38 02', 'TEL : 04 85 44 09 66': 'TEL : 04 85 44 09 66', '#Portée réduite / Reduced range.': '#Portée réduite / Reduced range.', "HOR : voir/see AD 2 NWWM.3#Dans l'espace du SIV situé sous TMA NOUMEA partie 1.2 MAGENTA#In FIS airspace located under TMA NOUMEA part 1.2 MAGENTA#Exploitant/Operator : AVA": "HOR : voir/see AD 2 NWWM.3#Dans l'espace du SIV situé sous TMA NOUMEA partie 1.2 MAGENTA#In FIS airspace located under TMA NOUMEA part 1.2 MAGENTA#Exploitant/Operator : AVA", 'HOR TWR/TWR SKED#Exploitant/Operator : AVA': 'HOR TWR/TWR SKED#Exploitant/Operator : AVA', 'Fréquence supplétive/Auxiliary frequency': 'Fréquence supplétive/Auxiliary frequency', 'Diffusion des paramètres de DEP et ARR (FR)/ARR-DEP parameters broadcasting.\n#Canal 8.33': 'Diffusion des paramètres de DEP et ARR (FR)/ARR-DEP parameters broadcasting.\n#Canal 8.33', "En l'absence AFIS A/A en FR seulement.": "En l'absence AFIS A/A en FR seulement.", 'FREQ arrivée.': 'FREQ arrivée.', 'Transit VFR/IFR - RAIZ': 'Transit VFR/IFR - RAIZ', 'Air/Sol VHF / Air/Ground VHF': 'Air/Sol VHF / Air/Ground VHF', 'Roulage VHF / Taxiing VHF': 'Roulage VHF / Taxiing VHF', 'Secteur Ouest/West sector.': 'Secteur Ouest/West sector.', 'Secteur EST': 'Secteur EST', 'Exploitant: Agglomération du Choletais.': 'Exploitant: Agglomération du Choletais.', 'Circulation au sol sauf RWY / Taxiing except on RWY': 'Circulation au sol sauf RWY / Taxiing except on RWY', 'SIV 1b': 'SIV 1b', 'O/R TWR 15 min avant utilisation.': 'O/R TWR 15 min avant utilisation.', 'AD non contrôlé SAM matin.': 'AD non contrôlé SAM matin.', 'APP CHERBOURG, APP LE HAVRE, APP CAEN': 'APP CHERBOURG, APP LE HAVRE, APP CAEN', 'FR seulement/only#\nExploitant/Operator : Délégation Guadeloupe': 'FR seulement/only#\nExploitant/Operator : Délégation Guadeloupe', 'FREQ Départ.': 'FREQ Départ.', 'SIV 1 et/and 2.': 'SIV 1 et/and 2.', 'Secteur NORD/NORTH sector': 'Secteur NORD/NORTH sector', 'Absence HOR ATS A/A FR seulement/only': 'Absence HOR ATS A/A FR seulement/only', 'Secteur Est': 'Secteur Est', "ACFT à l'ARR ou au DEP d'EPINAL MIRECOURT et NANCY ESSEY#\nACFT inbound or outbound EPINAL MIRECOURT and NANCY ESSEY": "ACFT à l'ARR ou au DEP d'EPINAL MIRECOURT et NANCY ESSEY#\nACFT inbound or outbound EPINAL MIRECOURT and NANCY ESSEY", 'Sur instruction UAC / on instruction UAC': 'Sur instruction UAC / on instruction UAC', 'Absence ATS : A/A FR uniquement/only.': 'Absence ATS : A/A FR uniquement/only.', 'cf AD2 LFRD.17': 'cf AD2 LFRD.17', 'Utilise toutes les fréq SRE - Utilisable QFU 29 ou 11/#\nUse all the SRE frequencies - Available for QFU 29 or 11': 'Utilise toutes les fréq SRE - Utilisable QFU 29 ou 11/#\nUse all the SRE frequencies - Available for QFU 29 or 11', 'SPAR MAINTENANCE LUN/MON 0800-1200 loc.': 'SPAR MAINTENANCE LUN/MON 0800-1200 loc.', 'FREQ supplétive (RWY 05)': 'FREQ supplétive (RWY 05)', 'RAI (H24)': 'RAI (H24)', 'FREQ Principale (RWY 05)': 'FREQ Principale (RWY 05)', 'Auto INFO - Fréq club': 'Auto INFO - Fréq club', 'FREQ de secours Prévol.': 'FREQ de secours Prévol.', 'RDH 06 : 49ft - RDH 24 : 52ft': 'RDH 06 : 49ft - RDH 24 : 52ft', 'Hors HOR MIL Nancy Ochey./Outside Nancy Ochey MIL SKED.': 'Hors HOR MIL Nancy Ochey./Outside Nancy Ochey MIL SKED.', 'Contrôle ACFT au sol.': 'Contrôle ACFT au sol.', '#MO/ML/MN/ST/AJ/BT#Sur instruction ATC/On ATC instruction.': '#MO/ML/MN/ST/AJ/BT#Sur instruction ATC/On ATC instruction.', 'Secteur Nord/North sector.': 'Secteur Nord/North sector.', 'FREQ sur instruction UAC UN /UB /KN /YB /HN /UR /XR /KR /HR /UF /KF /KD': 'FREQ sur instruction UAC UN /UB /KN /YB /HN /UR /XR /KR /HR /UF /KF /KD', 'TEL: 05 46 00 13 92': 'TEL: 05 46 00 13 92', 'TEL : 04 95 71 10 99': 'TEL : 04 95 71 10 99', 'FREQ sur instruction ACC E,SE.': 'FREQ sur instruction ACC E,SE.', 'ETE : 0700-SS+30 limité à 1800.#HIV : 0800-SS+30 limité à 1730.': 'ETE : 0700-SS+30 limité à 1800.#HIV : 0800-SS+30 limité à 1730.', 'Exploitant: Syndicat intercommunal.': 'Exploitant: Syndicat intercommunal.', 'FIS, APP, TWR. Sur instruction CTL/On ATC instruction.': 'FIS, APP, TWR. Sur instruction CTL/On ATC instruction.', 'Radiocommunications Air/Air': 'Radiocommunications Air/Air', 'Au profit des postes de stationnement K, L. / In respect of parking stands K, L.#Canal 8.33': 'Au profit des postes de stationnement K, L. / In respect of parking stands K, L.#Canal 8.33', '#A1/A2/A3/A4/B1/B2/B3/B4/D1/D3/E1/E2/E3/F1/F2/F3/F4/K1/K2/M1/M2/M3/M4/MO/ML/MN/ST/AJ/BT#Sur instruction ATC/On ATC instruction': '#A1/A2/A3/A4/B1/B2/B3/B4/D1/D3/E1/E2/E3/F1/F2/F3/F4/K1/K2/M1/M2/M3/M4/MO/ML/MN/ST/AJ/BT#Sur instruction ATC/On ATC instruction', 'ATIS/S': 'ATIS/S', 'Au profit des postes de stationnement J. / In respect of parking stands J.#Canal 8.33': 'Au profit des postes de stationnement J. / In respect of parking stands J.#Canal 8.33', 'Service saisonnier .Fr.uniquement.': 'Service saisonnier .Fr.uniquement.', "Canal 25 : sur instruction ATC  jusqu'au FL100": "Canal 25 : sur instruction ATC  jusqu'au FL100", 'Couverture: 25 NM/FL 100.': 'Couverture: 25 NM/FL 100.', 'Couverture: 25NM/FL40.': 'Couverture: 25NM/FL40.', 'O/R FREQ. de HYERES / O/R HYERES FREQ.': 'O/R FREQ. de HYERES / O/R HYERES FREQ.', 'Emplacement/Location : 036°/2000 m DTHR 04': 'Emplacement/Location : 036°/2000 m DTHR 04', '25NM/FL40.': '25NM/FL40.', 'Canal 25 : service : Information/Radar.': 'Canal 25 : service : Information/Radar.', '25NM/FL100.': '25NM/FL100.', 'APP TOULOUSE (SFC/FL075 Secteur Agen-Pamiers).#\nAppareils non-équipés 8,33 KHz : voir AD 2 LFBO.23.#\nTOULOUSE APP (SFC/FL075 Agen-Pamiers sector).#\nAircraft non 8.33 KHz-equipped : see AD 2 LFBO.23.': 'APP TOULOUSE (SFC/FL075 Secteur Agen-Pamiers).#\nAppareils non-équipés 8,33 KHz : voir AD 2 LFBO.23.#\nTOULOUSE APP (SFC/FL075 Agen-Pamiers sector).#\nAircraft non 8.33 KHz-equipped : see AD 2 LFBO.23.', 'Particulière Transit VFR ou RAI/Particular VFR transit or automatic information transmitter': 'Particulière Transit VFR ou RAI/Particular VFR transit or automatic information transmitter', 'Particulière Air-Sol VHF/Particular Air-Groung VHF': 'Particulière Air-Sol VHF/Particular Air-Groung VHF', "Angle de descente / Slope gradient 3°#Indicatif d'appel /  Call sign: LORIENT Précision.": "Angle de descente / Slope gradient 3°#Indicatif d'appel /  Call sign: LORIENT Précision.", "Dans l'espace du SIV situé sous / in SIV airspace located under TMA NOUMEA partie 1.1 TONTOUTA sauf sous / except under CTR NOUMEA LA TONTOUTA partie 1.": "Dans l'espace du SIV situé sous / in SIV airspace located under TMA NOUMEA partie 1.1 TONTOUTA sauf sous / except under CTR NOUMEA LA TONTOUTA partie 1.", 'Pente/Gradient 2.7°': 'Pente/Gradient 2.7°', 'Exploitant/Operator : SNA/OI#\nService VDF (Gonio).': 'Exploitant/Operator : SNA/OI#\nService VDF (Gonio).', 'Exploitant SNA/OI. Au sud du RDL 264° SDG.#\nOperator SNA/OI. South of RDL 264° SDG.#\nService VDF (Gonio).': 'Exploitant SNA/OI. Au sud du RDL 264° SDG.#\nOperator SNA/OI. South of RDL 264° SDG.#\nService VDF (Gonio).', "Paramètres de DEP et ARR jusqu'au FL 100. TEL: 03 85 26 60 78": "Paramètres de DEP et ARR jusqu'au FL 100. TEL: 03 85 26 60 78", 'Radar CENTAURE': 'Radar CENTAURE', 'Roulage/Taxiing': 'Roulage/Taxiing', 'TEL : 04 82 89 48 18': 'TEL : 04 82 89 48 18', 'SIV 1a': 'SIV 1a', 'SIV 3.1/3.2': 'SIV 3.1/3.2', 'TEL 03 21 06 62 84': 'TEL 03 21 06 62 84', 'Fréquence de transit/Transit frequency': 'Fréquence de transit/Transit frequency', 'TEL : 35 24 24': 'TEL : 35 24 24', 'exploitant : ville de ROYAN': 'exploitant : ville de ROYAN', 'Hors HOR ATC.': 'Hors HOR ATC.', 'CTL et/and transit': 'CTL et/and transit', '#G1/G2/G3/G4/Y1/Y2/Y3/Y4/W1/W2/W3/LO/LE/LS#Sur instruction ATC/On ATC instruction': '#G1/G2/G3/G4/Y1/Y2/Y3/Y4/W1/W2/W3/LO/LE/LS#Sur instruction ATC/On ATC instruction', 'SIV 3, 4  et/and 4.1.': 'SIV 3, 4  et/and 4.1.', 'TEL : 02 35 80 80 34': 'TEL : 02 35 80 80 34', 'Fr. uniquement.': 'Fr. uniquement.'}
        return

    def makeNewKey(self, sKey:str, oFreq:dict, bSuppletive=False) -> str:
        if not(bSuppletive) and not(sKey in oFreq):
            return sKey
        lIdx:int = 1
        while True:
            sNewKey = sKey + str(lIdx)
            if not(sNewKey in oFreq):
                break
            lIdx+=1
        return sNewKey
    
    def getPhoneNumber(self, sStr:str) -> str:
        sRet:str = ""
        lPos:int = sStr.lower().find("tel")
        if lPos == -1:
            lPos:int = sStr.lower().find("tél")
        if lPos != -1:
            for sChar in sStr[lPos+3:]:
                if sChar in ["+","0","1","2","3","4","5","6","7","8","9"]:
                    sRet += sChar
                elif sRet and (not sChar in [" ","."]):
                    break
        return sRet
    
    