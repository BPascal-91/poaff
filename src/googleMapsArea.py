#!/usr/bin/env python3
from copy import deepcopy
from rdp import rdp
import json

import bpaTools
import poaffCst
import aixmReader
import aixm2json
import airspacesCatalog
from airspacesCatalog import AsCatalog
import geoRefArea


cstGoogleMaps:str    = "GoogleMaps"


class GoogleMapsArea:

    def __init__(self, oLog:bpaTools.Logger, oAsCat:AsCatalog, oGlobalGeoJSON:dict, partialConstruct:bool)-> None:
        bpaTools.initEvent(__file__, oLog)
        self.oLog:bpaTools.Logger       = oLog                      #Log file
        self.oAsCat:AsCatalog           = oAsCat                    #Catalogue des zones
        self.aAsIndex                   = []                        #Index spécifique pour l'API GoogleMaps
        self.oGlobalGeoJSON:dict        = oGlobalGeoJSON            #Liste globale des zones
        self.oOutGeoJSON:dict           = {}                        #Sortie finale GeoJSON
        self.oGeoRefArea                = geoRefArea.GeoRefArea(partialConstruct)
        return

    def saveGoogleMapsFile4Area(self, sFile:str, sContext=cstGoogleMaps, epsilonReduce:float=None) -> None:
        self.makeGooglaMapIndex()
        for sAreaKey in self.oGeoRefArea.AreasRef.keys():
            self.saveGoogleMapsFile(sFile, sContext, sAreaKey, epsilonReduce)
        return

    def saveGoogleMapsFile(self, sFile:str, sContext:str="all", sAreaKey:str=None, epsilonReduce:float=None) -> None:
        oGoogleMaps:list = []
        sContent:str = ""

        oGlobalHeader = self.oAsCat.oGlobalCatalog[poaffCst.cstGeoHeaderFile]                   #Récupération de l'entete du catalogue global
        oNewHeader:dict = deepcopy(self.oAsCat.oGlobalCatalogHeader)

        #bpaTools.writeJsonFile(sFile + "-tmp.json", self.oGlobalGeoJSON)                       #Sérialisation pour mise au point
        oGlobalCats = self.oAsCat.oGlobalCatalog[airspacesCatalog.cstKeyCatalogCatalog]         #Récupération de la liste des zones consolidés
        sTitle = cstGoogleMaps + " save airspaces file - {0} / {1}".format(sContext, sAreaKey)
        barre = bpaTools.ProgressBar(len(oGlobalCats), 20, title=sTitle)
        idx = 0
        #for sGlobalKey, oGlobalCat in oGlobalCats.items():                                     #Traitement du catalogue global complet
        for sGlobalKey, sIdxKey in self.aAsIndex:                                               #Scrutation de l'index des zones triés de des plus hautes vers les plus basses
            oGlobalCat = oGlobalCats[sGlobalKey]                                                #Identification de la zone dans le catalogue
            idx+=1

            #if oGlobalCat["id"] in ["TMA16169","TMA16170"]:
            #    print(oGlobalCat["id"])

            #Filtrage des zones par typologie de sorties
            if sContext == cstGoogleMaps:
                bIsIncludeLoc:bool = True
                if sAreaKey!=None:
                    sKey4Find:str = sAreaKey.replace("geo","ExtOf")
                    if sAreaKey[:9]=="geoFrench":                                               #Spec for all french territories
                        sKey4Find = "ExtOfFrench"
                    if sKey4Find in oGlobalCat:
                        bIsIncludeLoc = not oGlobalCat[sKey4Find]                               #Exclusion de zone
                bIsInclude = bIsIncludeLoc and not oGlobalCat["groupZone"]
                sContent = "allZone"
                #sFile = sFile.replace("-all", "-" + cstGoogleMaps.lower())
            else:
                sContext = "all"
                sContent = "allZone"
                bIsInclude = True

            #Exclude area if unkwown coordonnees
            if bIsInclude and sContext!="all" and "excludeAirspaceNotCoord" in oGlobalCat:
                if oGlobalCat["excludeAirspaceNotCoord"]: bIsInclude = False

            #Filtrage des zones par régionalisation
            bIsArea:bool = True

            #Maintenir ou Supprimer la LTA-France1 (originale ou spécifique) des cartes non-concernées par le territoire Français --> [D] LTA FRANCE 1 (Id=LTA13071) [FL115-FL195]
            if oGlobalCat["id"] in ["LTA13071","LFBpaFrenchSS"]:
                if not sAreaKey in [None, "geoFrench","geoFrenchAll"]:
                    bIsArea = False

            elif bIsInclude and sAreaKey:
                if sAreaKey in oGlobalCat:
                    bIsArea = oGlobalCat[sAreaKey]
                else:
                    bIsArea = False

            if not bIsArea:
                sKey4Find:str = sAreaKey.replace("geo","IncOf")         #test d'inclusion volontaire de la zone ?
                bIsArea = oGlobalCat.get(sKey4Find, False)

            if bIsArea and bIsInclude and (sGlobalKey in self.oGlobalGeoJSON):

                #Extraction des coordonnées
                oAsGeo = self.oGlobalGeoJSON[sGlobalKey]
                if oAsGeo[poaffCst.cstGeoType].lower()==(poaffCst.cstGeoPoint).lower():
                    oCoords:list = oAsGeo[poaffCst.cstGeoCoordinates]                        #get coordinates of geometry
                elif oAsGeo[poaffCst.cstGeoType].lower()==(poaffCst.cstGeoLine).lower():
                    oCoords:list = oAsGeo[poaffCst.cstGeoCoordinates]                        #get coordinates of geometry
                elif oAsGeo[poaffCst.cstGeoType].lower()==(poaffCst.cstGeoPolygon).lower():
                    oCoords:list = oAsGeo[poaffCst.cstGeoCoordinates][0]                     #get coordinates of geometry

                #Optimisation du tracé GeoJSON
                oCoordsDst:list = []
                #if epsilonReduce<0: --> do not change !
                if epsilonReduce==0 or (epsilonReduce>0 and len(oCoords)>40):   #Ne pas optimiser le tracé des zones ayant moins de 40 segments (préservation des tracés de cercle minimaliste)
                    oCoordsDst = rdp(oCoords, epsilon=epsilonReduce)            #Optimisation du tracé des coordonnées

                #Remplacement du tracé s'il a été optimisé
                iOrgSize:int = len(oCoords)
                iNewSize:int = len(oCoordsDst)
                if iNewSize>0 and iNewSize!=iOrgSize:
                    percent:float = round((1-(iNewSize/iOrgSize))*100,1)
                    percent = int(percent) if percent>=1.0 else percent
                    sOpti:str = "Segments optimisés à {0}% ({1}->{2}) [rdp={3}] ***".format(percent, iOrgSize, iNewSize, epsilonReduce)
                    self.oLog.debug(cstGoogleMaps + " RDP Optimisation: {0} - {1}".format(oGlobalCat["nameV"], sOpti), level=2, outConsole=False)
                    #self.oCtrl.oLog.debug("RDP Src: {0}".format(oCoords), level=8)
                    #self.oCtrl.oLog.debug("RDP Dst: {0}".format(oCoordsDst), level=8)
                    if oAsGeo[poaffCst.cstGeoType].lower()==(poaffCst.cstGeoPoint).lower():
                        oNewGeo:dict = {poaffCst.cstGeoType:oAsGeo[poaffCst.cstGeoType], poaffCst.cstGeoCoordinates:oCoordsDst}
                    elif oAsGeo[poaffCst.cstGeoType].lower()==(poaffCst.cstGeoLine).lower():
                       oNewGeo:dict = {poaffCst.cstGeoType:oAsGeo[poaffCst.cstGeoType], poaffCst.cstGeoCoordinates:oCoordsDst}
                    elif oAsGeo[poaffCst.cstGeoType].lower()==(poaffCst.cstGeoPolygon).lower():
                        oNewGeo:dict = {poaffCst.cstGeoType:oAsGeo[poaffCst.cstGeoType], poaffCst.cstGeoCoordinates:[oCoordsDst]}
                    oArea:dict = oNewGeo
                else:
                    oArea:dict = oAsGeo

                #oGoogleMaps.append(oGlobalCat["nameV"])
                oGoogleMaps.append(oArea)
            barre.update(idx)
        barre.reset()

        if sAreaKey:
            sContent += " / " + sAreaKey
            sFile = sFile.replace(".geojson", "-" + sAreaKey + ".gmaps")
        else:
            sFile = sFile.replace(".geojson", ".gmaps")

        sMsg:str = " file {0} - {1} areas in map".format(sFile, len(oGoogleMaps))
        if len(oGoogleMaps) == 0:
            self.oLog.info(cstGoogleMaps + " unwritten" + sMsg, outConsole=False)
            bpaTools.deleteFile(sFile)
        else:
            self.oLog.info(cstGoogleMaps + " write" + sMsg, outConsole=False)

            #Entête des fichiers
            oSrcFiles = oNewHeader.pop(airspacesCatalog.cstKeyCatalogSrcFiles)
            oNewHeader.update({airspacesCatalog.cstKeyCatalogContent:sContent})
            sAreaDesc:str = ""
            if sAreaKey in self.oGeoRefArea.AreasRef:
                sAreaDesc:str = self.oGeoRefArea.AreasRef[sAreaKey][2]
                oNewHeader.update({airspacesCatalog.cstKeyCatalogKeyAreaDesc:sAreaDesc})

            del oNewHeader[airspacesCatalog.cstKeyCatalogNbAreas]
            oNewHeader.update({airspacesCatalog.cstKeyCatalogNbAreas:len(oGoogleMaps)})
            oNewHeader.update({airspacesCatalog.cstKeyCatalogSrcFiles:oSrcFiles})

            oTools = aixmReader.AixmTools(None)
            sGoogleMaps:str = oTools.makeHeaderOpenairFile(oHeader=oNewHeader, oOpenair=oGoogleMaps, context=sContext, sAreaKey=sAreaKey, sAreaDesc=sAreaDesc, epsilonReduce=epsilonReduce)

            #Sérialisation de toutes les zones
            for oGmap in oGoogleMaps:
                sGoogleMaps += json.dumps(oGmap) + "\n"

            bpaTools.writeTextFile(sFile, sGoogleMaps)  #Sérialisation du fichier
        return


        """
        Sample of content
        function geoTest1_defaultLocation() {
        	return {Lat:48,Lng:1.7,Zoom:7.4};		// Frensh north view
        }

        function geoTest1_addPolygons() {

        // CLASS D - LTA FRANCE 3 ALPES 1 FL220 - FL195
        var polygon = new google.maps.Polygon({
        map:map, path: google.maps.geometry.encoding.decodePath('m`otGyy`f@xt@q|bA}`H{hP`wb@mwt@rNdDzm@kq@xZu@pUeK`s@aR~_@oc@jq@cl@|_@rN`Yf^rNaRpUuGpU|ErNaYhWeDva@rh@`RrNrNhWkIzm@?|f@|_@zShWjIzSro@`RbRzL~X|LzLt@xZlIzLhWcKrNtGbKrNbRlBzL`s@?bRw{@v{@wa@bs@~E`s@jj@ldAbKn\\aRzLpUxZkPhrAcKdKn\\rh@v@rNn\\tG}Enc@xSnwAv@ro@f^hWzLkPn\\aRp\\`tAvZdDlc@cKlIf^xSde@f^cRu@|hB|EfWzLjPeDhx@hPpUcKbl@oBv{@zSlI`Rv@xZth@~y@}f@zLoBrUuh@f^p\\bK|aBoBn\\`Ybl@`YbnBo\\zLsU}Eu@dfAoc@ro@cKn\\uGzLv@rNqUth@cRznAmIhWeD`s@wZ`s@uGpv@dfAf`Bf^jP|f@|`AmIjq@oBzm@ua@xuAta@l_CmB~`Af_Alc@f^dKbKzm@bKrNmB~XvZn\\tGbRw@|aB~_@|LjPhPn\\|Lf^g^rNoB`Ycl@pUmIpUua@xt@|EhWcs@?iq@f`BgDhW`YvZso@~_@yS`Rf^de@?`YiW|E{Lth@uGlIkPkP_z@tGee@oBsqBv@w{@eDg^zf@gzBjPeKrN?jq@wZ|f@}ErNxuAxSoB~_@{gAzm@gDbKua@n\\so@ndA}E`tAxt@dDrNxSzLva@ro@lBsNcKkq@|E_Y~_@sNw@rh@f^lIhWpU`YaRriAjItGaRrNmdAoBkq@nc@}f@pUuGlByS`Y{LcKa{Arh@v@de@wZrNaYzt@{iCfWaYrUsh@rNkrArh@qv@v@{m@oBsh@zSyt@}EmkA|Eua@jPkP_F}f@aRySySwa@wa@_Y{LoBcRwZbs@itCf^ix@`Rcl@?g_AxZgyAt@_`@lIqUpwAyZbKubAlIkP|EpU`s@|En\\f^n}@nc@bs@pv@~_@qv@rGiWpv@so@bRmIzLsNxS|LxZcRta@dDlI|L`YoBde@qUhWzLbl@uh@xSu@vbAcmApUatAtGix@lc@?va@kPzLcK|`AyZbs@}E|Eth@gDzgA{Lnc@}Eta@}f@rpAeDde@dDjj@|ErU|E|`AfDhW{SvZtGvbAva@pv@th@hq@oBro@va@n\\~y@eD~_@`s@n\\zLro@g^hq@}EvbAw{@|EwZta@dD?vZcK~_@rNpv@ro@mIf^~_@`Rro@xZ?rN`YtbAw@rNlIxt@_FlIzSjPdfAdDlc@de@cRxS?bRndAzLxSuGhW|Eta@dKrNw@dl@cKxS~XrNhWoBv@zS~y@vZbRdfAta@hWdl@aYde@fDta@}LjPv@lj@aYrh@}_@f^qv@|f@lBva@iq@hWcs@rNo}@hPySjq@kPlc@sNbRsNtbAaoCn\\{LxZ{t@rN|LsNbmAf^dDjIxt@_Yth@de@nwAoBp\\lIta@ldA{LpUsNn\\bRth@eKde@|E~`AmBpUoBvZrNjPde@~_@?xSirA?_`@xZuh@|Esh@bKkPn\\|ErUeDbKeKro@qU~Xgx@rU}L|E_Y`RiWlIoc@hWcKhWwa@hW~E`RrGpUv@pUtGrNiWv@qU}EaYbKySdl@dKbK{SkPso@|f@_{AxZw@pUkIvZtGpUoBth@mIde@fD~_@qUjP}EzLsNf^iWhWy{@eK}_@dKmIt]hdDxa@xbDte@`aDti@b_Drm@~|Clq@tzCdu@fxCzx@puCr|@vrCb`AvoCtcAplC`gAfiCljAveCtmAbbCzpAf~B|sAjzBleB_Yks`@fncBekd@n`nAqac@f|D_uIe{JpwAeiDmtfA_pR_zl@_kTkeIo}xAsbOxvB}xMzfG')});
        //polygon.bounds  = new google.maps.LatLngBounds(new google.maps.LatLng(44.064722, 5.702500), new google.maps.LatLng(45.503611, 7.137222));
        polygon.altLow  = 19500;
        polygon.altHigh = 22000;
        attachPolygonInfoBox(polygon, infoBox, 'LTA FRANCE 3 ALPES 1<br />Class D<br />Upper:&nbsp; FL220<br />Lower:&nbsp; FL195');
        polygon.GUId="GUId-LTA-FRANCE3ALPES1";
        polygon.airspaceClass="D";
        polygon.VName="LTA FRANCE 3 ALPES 1";
        polygons.push(polygon);
        ../..
        """




    def makeGooglaMapIndex(self) -> None:
        """
        Tri des zones des plus hautes vers les plus basses. Tri inversé sur un index basé sur l'altitude 'plafond-plancher'.
        Explication: Google Maps nécessite un tri descendant depuis les zones de couche les plus hautes pour finir la liste sur les plus basse
        Ainsi, l'affichage des zones les plus basse sont dessinées en dernier sur la carte 2D ; ce qui permet de les visualiser par dessus celles qui sont pourtant physiquements plus hautes.
        Cette astuce permet : 1/ de bien visualiser les zones sur une carte aérienne 2/ d'utiliser l'evennement MouseMove pour mettre en surbrillance les couches basses en priorité
        Sample self.aAsIndex = [
                #(<UId> , <Key for index>),
                ('LFOT1', '04419-01066'),  # TMA TOURS 2 App(121.000)
                ('LFOT1', '03810-01066'),  # TMA TOURS 1 App(121.000)
                ('LFOT' , '01066-00000'),  # CTR TOURS VAL DE LOIRE Twr(124.400)
            ]
        """
        oGlobalCats = self.oAsCat.oGlobalCatalog[airspacesCatalog.cstKeyCatalogCatalog]         #Récupération de la liste des zones consolidés
        sTitle = cstGoogleMaps + " airspaces make index"
        barre = bpaTools.ProgressBar(len(oGlobalCats), 20, title=sTitle)
        idx = 0
        aTmp = []
        for sGlobalKey, oAs in oGlobalCats.items():                                      #Traitement du catalogue global complet
            idx+=1
            sIdxKey = "{0:05d}-{1:05d}".format(int(oAs["upperM"]), int(oAs["lowerM"]))
            aTmp.append((oAs["GUId"], sIdxKey))
            barre.update(idx)
        barre.reset()
        self.aAsIndex = sorted(aTmp, reverse=True, key=lambda oAS: oAS[1])              #Tri inversé sur l'altitude Plafond-Plancher
        return
