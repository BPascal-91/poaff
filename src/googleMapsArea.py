#!/usr/bin/env python3
import os
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
import googleAPI  #from googleAPI import geocoding


cstGoogleMaps:str   = "GoogleMaps"
cstCRLF:str         = ""          # "\n" for map and "" for minimise Javascript module


class GoogleMapsArea:

    def __init__(self, oLog:bpaTools.Logger, oAsCat:AsCatalog, oGlobalGeoJSON:dict, partialConstruct:bool)-> None:
        bpaTools.initEvent(__file__, oLog)
        self.oLog:bpaTools.Logger       = oLog                      #Log file
        self.oAsCat:AsCatalog           = oAsCat                    #Catalogue des zones
        self.aAsIndex                   = []                        #Index spécifique pour l'API GoogleMaps
        self.oGlobalGeoJSON:dict        = oGlobalGeoJSON            #Liste globale des zones
        self.oOutGeoJSON:dict           = {}                        #Sortie finale GeoJSON
        self.oGeoRefArea                = geoRefArea.GeoRefArea(partialConstruct)
        self.geoCod:geocoding           = googleAPI.geocoding()
        return

    def saveGoogleMapsFile4Area(self, sFile:str, sContext=cstGoogleMaps, epsilonReduce:float=None) -> None:
        self.makeGooglaMapIndex()
        for sAreaKey in self.oGeoRefArea.AreasRef.keys():
            self.saveGoogleMapsFile(sFile, sContext, sAreaKey, epsilonReduce)
        self.makePoaffDataFile(sFile)
        return

    def makePoaffDataFile(self, sFile:str) -> None:
        sContent:str = "// " + bpaTools.getCopyright() + "\n"
        sContent += cstCRLF + 'const defaultCheckFile="geoFrench";' + cstCRLF
        sContent += 'var poaffFiles={' + cstCRLF
        for sAreaKey in self.oGeoRefArea.AreasRef.keys():
            sFileCible = sFile.replace("global@airspaces-all", "poaff")
            sFileCible = sFileCible.replace(".geojson", "-" + sAreaKey + ".gmaps")
            if os.path.exists(sFileCible):
                sContent += sAreaKey + ':["'
                sContent += sAreaKey[3:] + '","'
                sContent += self.oGeoRefArea.AreasRef[sAreaKey][geoRefArea.enuAreasRef.desc.value] + '","'
                descComp:str = self.oGeoRefArea.AreasRef[sAreaKey][geoRefArea.enuAreasRef.descComp.value]
                descComp = descComp.replace("\n"," ").replace("  "," ")
                sContent += descComp + '","'
                sContent += bpaTools.getFileNameExt(sFileCible) + '"],' + cstCRLF
        if cstCRLF=="":
            sContent = sContent[:-1] + cstCRLF
        else:
            sContent = sContent[:-2] + cstCRLF
        sContent += '};' + cstCRLF
        sContent += 'const enuPoaffFiles={name:0,desc:1,descComp:2,file:3};' + cstCRLF
        sFileCatalog:str = bpaTools.getFilePath(sFile) + "poaff-data.gmaps"
        bpaTools.writeTextFile(sFileCatalog, sContent)  #Sérialisation du fichier
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

            if sAreaKey.find("geoFrench")>=0:
                bIsArea = sAreaKey in ["geoFrench","geoFrenchAll"]

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

                sGooglaMapPolygon:str = self.makeGooglaMapPolygon(oGlobalCat, oArea)     #Sérialisation de la zone au format Google MAp API
                if sGooglaMapPolygon:
                    oGoogleMaps.append(sGooglaMapPolygon)
            barre.update(idx)
        barre.reset()

        sFile = sFile.replace("global@airspaces-all", "poaff")
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
                sAreaDesc:str = self.oGeoRefArea.AreasRef[sAreaKey][geoRefArea.enuAreasRef.desc.value]
                oNewHeader.update({airspacesCatalog.cstKeyCatalogKeyAreaDesc:sAreaDesc})

            del oNewHeader[airspacesCatalog.cstKeyCatalogNbAreas]
            oNewHeader.update({airspacesCatalog.cstKeyCatalogNbAreas:len(oGoogleMaps)})
            oNewHeader.update({airspacesCatalog.cstKeyCatalogSrcFiles:oSrcFiles})

            #1/ Add header file
            oTools = aixmReader.AixmTools(None)
            sGoogleMaps:str = oTools.makeHeaderOpenairFile(oHeader=oNewHeader, oOpenair=oGoogleMaps, context=sContext, sAreaKey=sAreaKey, sAreaDesc=sAreaDesc, epsilonReduce=epsilonReduce)

            #2/ Add defaultLocation() function - Sample of content: function geoTest1_defaultLocation() {return {Lat:48,Lng:1.7,Zoom:7.4};}
            sDefLocation:str = self.oGeoRefArea.AreasRef[sAreaKey][geoRefArea.enuAreasRef.defLocation.value]
            sGoogleMaps += "function "+ sAreaKey + "_defaultLocation() {return" + sDefLocation + ";}" + cstCRLF

            #3/ Add addPolygons() function - Header sample - function geoTest1_addPolygons()
            sGoogleMaps += "function "+ sAreaKey + "_addPolygons() {" + cstCRLF
            #Sérialisation de toutes les zones
            for oGmap in oGoogleMaps:
                sGoogleMaps += oGmap
            sGoogleMaps += "}" + cstCRLF

            bpaTools.writeTextFile(sFile, sGoogleMaps)  #Sérialisation du fichier
        return


    def makeGooglaMapPolygon(self, oGlobalCat:dict, oArea:dict) -> str:
        """
        Sample of return
            var pol = new google.maps.Polygon({map:map,
            path:google.maps.geometry.encoding.decodePath("m`otGyy`f@xt@q|bA}`H{hP`wb@mwt@rNdDzm@kq@xZu@pUeK`s@aR~_@oc@jq@cl@|_@rN`Yf^rNaRpUuGpU|ErNaYhWeDva@rh@`RrNrNhWkIzm@?|f@|_@zShWjIzSro@`RbRzL~X|LzLt@xZlIzLhWcKrNtGbKrNbRlBzL`s@?bRw{@v{@wa@bs@~E`s@jj@ldAbKn\\aRzLpUxZkPhrAcKdKn\\rh@v@rNn\\tG}Enc@xSnwAv@ro@f^hWzLkPn\\aRp\\`tAvZdDlc@cKlIf^xSde@f^cRu@|hB|EfWzLjPeDhx@hPpUcKbl@oBv{@zSlI`Rv@xZth@~y@}f@zLoBrUuh@f^p\\bK|aBoBn\\`Ybl@`YbnBo\\zLsU}Eu@dfAoc@ro@cKn\\uGzLv@rNqUth@cRznAmIhWeD`s@wZ`s@uGpv@dfAf`Bf^jP|f@|`AmIjq@oBzm@ua@xuAta@l_CmB~`Af_Alc@f^dKbKzm@bKrNmB~XvZn\\tGbRw@|aB~_@|LjPhPn\\|Lf^g^rNoB`Ycl@pUmIpUua@xt@|EhWcs@?iq@f`BgDhW`YvZso@~_@yS`Rf^de@?`YiW|E{Lth@uGlIkPkP_z@tGee@oBsqBv@w{@eDg^zf@gzBjPeKrN?jq@wZ|f@}ErNxuAxSoB~_@{gAzm@gDbKua@n\\so@ndA}E`tAxt@dDrNxSzLva@ro@lBsNcKkq@|E_Y~_@sNw@rh@f^lIhWpU`YaRriAjItGaRrNmdAoBkq@nc@}f@pUuGlByS`Y{LcKa{Arh@v@de@wZrNaYzt@{iCfWaYrUsh@rNkrArh@qv@v@{m@oBsh@zSyt@}EmkA|Eua@jPkP_F}f@aRySySwa@wa@_Y{LoBcRwZbs@itCf^ix@`Rcl@?g_AxZgyAt@_`@lIqUpwAyZbKubAlIkP|EpU`s@|En\\f^n}@nc@bs@pv@~_@qv@rGiWpv@so@bRmIzLsNxS|LxZcRta@dDlI|L`YoBde@qUhWzLbl@uh@xSu@vbAcmApUatAtGix@lc@?va@kPzLcK|`AyZbs@}E|Eth@gDzgA{Lnc@}Eta@}f@rpAeDde@dDjj@|ErU|E|`AfDhW{SvZtGvbAva@pv@th@hq@oBro@va@n\\~y@eD~_@`s@n\\zLro@g^hq@}EvbAw{@|EwZta@dD?vZcK~_@rNpv@ro@mIf^~_@`Rro@xZ?rN`YtbAw@rNlIxt@_FlIzSjPdfAdDlc@de@cRxS?bRndAzLxSuGhW|Eta@dKrNw@dl@cKxS~XrNhWoBv@zS~y@vZbRdfAta@hWdl@aYde@fDta@}LjPv@lj@aYrh@}_@f^qv@|f@lBva@iq@hWcs@rNo}@hPySjq@kPlc@sNbRsNtbAaoCn\\{LxZ{t@rN|LsNbmAf^dDjIxt@_Yth@de@nwAoBp\\lIta@ldA{LpUsNn\\bRth@eKde@|E~`AmBpUoBvZrNjPde@~_@?xSirA?_`@xZuh@|Esh@bKkPn\\|ErUeDbKeKro@qU~Xgx@rU}L|E_Y`RiWlIoc@hWcKhWwa@hW~E`RrGpUv@pUtGrNiWv@qU}EaYbKySdl@dKbK{SkPso@|f@_{AxZw@pUkIvZtGpUoBth@mIde@fD~_@qUjP}EzLsNf^iWhWy{@eK}_@dKmIt]hdDxa@xbDte@`aDti@b_Drm@~|Clq@tzCdu@fxCzx@puCr|@vrCb`AvoCtcAplC`gAfiCljAveCtmAbbCzpAf~B|sAjzBleB_Yks`@fncBekd@n`nAqac@f|D_uIe{JpwAeiDmtfA_pR_zl@_kTkeIo}xAsbOxvB}xMzfG")});
            //pol.bounds  = new google.maps.LatLngBounds(new google.maps.LatLng(44.064722, 5.702500), new google.maps.LatLng(45.503611, 7.137222));
            pol.GUId="GUId-LTA-FRANCE3ALPES1";
            pol.altLow  = 19500;
            pol.altHigh = 22000;
            pol.airspaceClass="D";
            pol.VName="LTA FRANCE 3 ALPES 1";
            attachPolygonInfoBox(pol, infoBox, 'LTA FRANCE 3 ALPES 1<br />Class D<br />Upper:&nbsp; FL220<br />Lower:&nbsp; FL195');
            polygons.push(pol);
            ../..
        """

        if oArea[poaffCst.cstGeoType].lower()==(poaffCst.cstGeoPoint).lower():
            return
        if oArea[poaffCst.cstGeoType].lower()==(poaffCst.cstGeoLine).lower():
           return
        #if oArea[poaffCst.cstGeoType].lower()==(poaffCst.cstGeoPolygon).lower():

        sPolygon:str = cstCRLF

        #print(json.dumps(oArea))
        #oCoords sample - [[3.758285, 47.636124], [3.756871, 47.654449], [3.75247, 47.672558], [3.745134, 47.690231], [3.734949, 47.707253], [3.722035, 47.723416], [3.706549, 47.738523], [3.688676, 47.75239], [3.668633, 47.764847], [3.646664, 47.775743], [3.623037, 47.784944], [3.598039, 47.792336], [3.571977, 47.797831], [3.545169, 47.80136], [3.517944, 47.80288], [3.490634, 47.802373], [3.463576, 47.799844], [3.4371, 47.795326], [3.411531, 47.788872], [3.387182, 47.780563], [3.364349, 47.770499], [3.343311, 47.758805], [3.324324, 47.745623], [3.307619, 47.731113], [3.293398, 47.715454], [3.281831, 47.698837], [3.273057, 47.681463], ../..]
        oCoords:list = oArea[poaffCst.cstGeoCoordinates][0]                     #get coordinates of geometry
        if cstCRLF!="":
            sPolygon += "/*geoJSON coords: " + json.dumps(oCoords) + " */"

        sPolygon += cstCRLF + "var pol=new google.maps.Polygon({map:map,"

        #0/ Std paths - sample - myCoordinates = [{lat:25.774,lng:-80.19},{lat:18.466,lng:-66.118}, ../..];
        #myCoordinates:str = ""
        #for aPt in oCoords:
        #    myCoordinates += "{" + "lat:{0},lng:{1}".format(aPt[1], aPt[0]) + "},"
        #sPolygon    += "path:[" + myCoordinates[:-1] + "]"

        #1/ API google.maps.LatLng() - problèmes: Source verbeux, Pile d'appels importante, API payante - sample - myCoordinates = [new google.maps.LatLng(0.457301,-0.597382),new google.maps.LatLng(0.475153,-0.569916),new google.maps.LatLng(0.494379,-0.563049)];
        #myCoordinates:str = ""
        #for aPt in oCoords:
        #    myCoordinates += "new google.maps.LatLng({0},{1}),".format(aPt[1], aPt[0])
        #sPolygon    += "path:[" + myCoordinates[:-1] + "]"

        #2/ API google.maps.geometry.encoding.decodePath() - problèmes: Bug sur l'encoding de certaines zones - sample - map:map, path: google.maps.geometry.encoding.decodePath("m`otGyy`f@xt@q|bA}`H{hP`wb@mwt@rNdDzm@kq@xZu@pUeK`s@aR~_@oc@jq@cl@|_@rN`Yf^rNaRpUuGpU|ErNaYhWeDva@rh@`RrNrNhWkIzm@?|f@|_@zShWjIzSro@`RbRzL~X|LzLt@xZlIzLhWcKrNtGbKrNbRlBzL`s@?bRw{@v{@wa@bs@~E`s@jj@ldAbKn\\aRzLpUxZkPhrAcKdKn\\rh@v@rNn\\tG}Enc@xSnwAv@ro@f^hWzLkPn\\aRp\\`tAvZdDlc@cKlIf^xSde@f^cRu@|hB|EfWzLjPeDhx@hPpUcKbl@oBv{@zSlI`Rv@xZth@~y@}f@zLoBrUuh@f^p\\bK|aBoBn\\`Ybl@`YbnBo\\zLsU}Eu@dfAoc@ro@cKn\\uGzLv@rNqUth@cRznAmIhWeD`s@wZ`s@uGpv@dfAf`Bf^jP|f@|`AmIjq@oBzm@ua@xuAta@l_CmB~`Af_Alc@f^dKbKzm@bKrNmB~XvZn\\tGbRw@|aB~_@|LjPhPn\\|Lf^g^rNoB`Ycl@pUmIpUua@xt@|EhWcs@?iq@f`BgDhW`YvZso@~_@yS`Rf^de@?`YiW|E{Lth@uGlIkPkP_z@tGee@oBsqBv@w{@eDg^zf@gzBjPeKrN?jq@wZ|f@}ErNxuAxSoB~_@{gAzm@gDbKua@n\\so@ndA}E`tAxt@dDrNxSzLva@ro@lBsNcKkq@|E_Y~_@sNw@rh@f^lIhWpU`YaRriAjItGaRrNmdAoBkq@nc@}f@pUuGlByS`Y{LcKa{Arh@v@de@wZrNaYzt@{iCfWaYrUsh@rNkrArh@qv@v@{m@oBsh@zSyt@}EmkA|Eua@jPkP_F}f@aRySySwa@wa@_Y{LoBcRwZbs@itCf^ix@`Rcl@?g_AxZgyAt@_`@lIqUpwAyZbKubAlIkP|EpU`s@|En\\f^n}@nc@bs@pv@~_@qv@rGiWpv@so@bRmIzLsNxS|LxZcRta@dDlI|L`YoBde@qUhWzLbl@uh@xSu@vbAcmApUatAtGix@lc@?va@kPzLcK|`AyZbs@}E|Eth@gDzgA{Lnc@}Eta@}f@rpAeDde@dDjj@|ErU|E|`AfDhW{SvZtGvbAva@pv@th@hq@oBro@va@n\\~y@eD~_@`s@n\\zLro@g^hq@}EvbAw{@|EwZta@dD?vZcK~_@rNpv@ro@mIf^~_@`Rro@xZ?rN`YtbAw@rNlIxt@_FlIzSjPdfAdDlc@de@cRxS?bRndAzLxSuGhW|Eta@dKrNw@dl@cKxS~XrNhWoBv@zS~y@vZbRdfAta@hWdl@aYde@fDta@}LjPv@lj@aYrh@}_@f^qv@|f@lBva@iq@hWcs@rNo}@hPySjq@kPlc@sNbRsNtbAaoCn\\{LxZ{t@rN|LsNbmAf^dDjIxt@_Yth@de@nwAoBp\\lIta@ldA{LpUsNn\\bRth@eKde@|E~`AmBpUoBvZrNjPde@~_@?xSirA?_`@xZuh@|Esh@bKkPn\\|ErUeDbKeKro@qU~Xgx@rU}L|E_Y`RiWlIoc@hWcKhWwa@hW~E`RrGpUv@pUtGrNiWv@qU}EaYbKySdl@dKbK{SkPso@|f@_{AxZw@pUkIvZtGpUoBth@mIde@fD~_@qUjP}EzLsNf^iWhWy{@eK}_@dKmIt]hdDxa@xbDte@`aDti@b_Drm@~|Clq@tzCdu@fxCzx@puCr|@vrCb`AvoCtcAplC`gAfiCljAveCtmAbbCzpAf~B|sAjzBleB_Yks`@fncBekd@n`nAqac@f|D_uIe{JpwAeiDmtfA_pR_zl@_kTkeIo}xAsbOxvB}xMzfG")});
        sPolygon    += 'path:google.maps.geometry.encoding.decodePath("'
        sPolygon    += self.geoCod.encode(oCoords) + '")'

        sPolygon    += '});' + cstCRLF

        sGUId:str = oGlobalCat.get("srcGUId", None)
        if sGUId==None:     sGUId = oGlobalCat.get("GUId", "!")
        sUId:str = oGlobalCat.get("srcUId", None)
        if sUId==None:      sUId:str = oGlobalCat.get("UId", "!")
        sId:str = oGlobalCat.get("id", "!")
        #sPolygon    += "pol.AUID=GUId={0} UId={1} Id={2}".format(sGUId, sUId, sId) + ";" + cstCRLF
        sPolygon    += 'pol.GUId="{0}"'.format(sGUId) + ";" + cstCRLF

        sPolygon    += 'pol.aClass="' + oGlobalCat["class"] + '";' + cstCRLF
        if oGlobalCat["type"]!=oGlobalCat["class"]:
            sPolygon    += 'pol.type="' + oGlobalCat["type"] + '";' + cstCRLF
        sPolygon    += 'pol.name="' + self.cleanStr(oGlobalCat["name"]) + '";' + cstCRLF
        sPolygon    += 'pol.nameV="' + self.cleanStr(oGlobalCat["nameV"]) + '";' + cstCRLF

        aAlt:list = []
        aAlt.append("{0}".format(aixmReader.getSerializeAlt (oGlobalCat)[1:-1]))
        aAlt.append("{0}".format(aixmReader.getSerializeAltM(oGlobalCat)[1:-1]))
        if "freeFlightZoneExt" in oGlobalCat:
            if oGlobalCat["freeFlightZoneExt"] and (not oGlobalCat["freeFlightZone"]):
                aAlt.append("ffExt=Yes")
        #if "lowerM" in oZone:
        #    if float(oGlobalCat.get("lowerM", 0)) > 3504:  #FL115 = 3505m
        #        aAlt.append("ffExt=Yes")
        if len(aAlt)==3:
            sPolygon += 'pol.AAlt=\'["{0}", "{1}", "{2}"]'.format(aAlt[0], aAlt[1], aAlt[2]) + "';" + cstCRLF
        else:
            sPolygon += 'pol.AAlt=\'["{0}", "{1}"]'.format(aAlt[0], aAlt[1]) + "';" + cstCRLF

        sPolygon    += 'pol.AH="'      + self.parseAlt("AH", "-gpsWithTopo"      , False, oGlobalCat) + '";' + cstCRLF
        if oGlobalCat.get("ordinalUpperMaxM", False):
            sPolygon += 'pol.AH2="{0}'.format(oGlobalCat["upperMax"]) + '";' + cstCRLF
        sPolygon    += 'pol.AL="'      + self.parseAlt("AL", "-gpsWithTopo"      , False, oGlobalCat) + '";' + cstCRLF
        if oGlobalCat.get("ordinalLowerMinM", False):
            sPolygon += 'pol.AL2="{0}'.format(oGlobalCat["lowerMin"]) + '";' + cstCRLF
        sPolygon    += 'pol.altHigh=' + self.parseAlt("AH", "-gpsWithoutTopo"   , True , oGlobalCat) + ';' + cstCRLF
        sPolygon    += 'pol.altLow='  + self.parseAlt("AL", "-gpsWithoutTopo"   , True , oGlobalCat) + ';' + cstCRLF

        if "desc" in oGlobalCat:    sPolygon += 'pol.descr="' + self.cleanStr(oGlobalCat["desc"]) + '";' + cstCRLF

        if ("activationCode" in oGlobalCat) and ("activationDesc" in oGlobalCat):
            sPolygon += 'pol.activ="[{0}] {1}'.format(oGlobalCat["activationCode"], self.cleanStr(oGlobalCat["activationDesc"])) + '";' + cstCRLF
        if ("activationCode" in oGlobalCat) and not ("activationDesc" in oGlobalCat):
            sPolygon += 'pol.activ="[{0}]'.format(oGlobalCat["activationCode"]) + '";' + cstCRLF
        if not("activationCode" in oGlobalCat) and ("activationDesc" in oGlobalCat):
            sPolygon += 'pol.activ="[{0}]'.format(self.cleanStr(oGlobalCat["activationDesc"])) + '";' + cstCRLF

        if "timeScheduling" in oGlobalCat:
            sPolygon += 'pol.times=\'{0}'.format(json.dumps(oGlobalCat["timeScheduling"], ensure_ascii=False)) + "';" + cstCRLF

        if "Mhz" in oGlobalCat:
            if isinstance(oGlobalCat["Mhz"], str):
                sDict:str = bpaTools.getContentOf(oGlobalCat["Mhz"], "{", "}", bRetSep=True)
                #sDict = sDict.replace("'", "\\'")
                oAMhz:dict = json.loads(sDict)
            elif isinstance(oGlobalCat["Mhz"], dict):
                oAMhz:dict = oGlobalCat["Mhz"]
            else:
                oAMhz:dict = None
            sPolygon += 'pol.mhz=\'{0}'.format(json.dumps(oAMhz, ensure_ascii=False).replace("'", "\\'")) + "';" + cstCRLF

        if bool(oGlobalCat.get("declassifiable",  False)):  sPolygon += "pol.decla=true;" + cstCRLF
        if bool(oGlobalCat.get("exceptSAT", False)):        sPolygon += "pol.exSAT=true;" + cstCRLF
        if bool(oGlobalCat.get("exceptSUN", False)):        sPolygon += "pol.exSUN=true;" + cstCRLF
        if bool(oGlobalCat.get("exceptHOL", False)):        sPolygon += "pol.exHOL=true;" + cstCRLF
        if bool(oGlobalCat.get("seeNOTAM",  False)):        sPolygon += "pol.seeNOTAM=true;" + cstCRLF

        sPolygon += "attachPolygonInfoBox(pol,infoBox,pol.nameV);" + cstCRLF

        sPolygon += "polygons.push(pol);" + cstCRLF
        return sPolygon

    def cleanStr(self, src:str) -> str:
        #iPos = src.find("'") + src.find('"')
        #if iPos > 0:
        #    print(src)
        ret = src.replace("'", "\\'")
        ret = ret.replace('"', '\\"')
        return ret

    def parseAlt(self, altRef:str, gpsType:str, bFeet:bool, oZone:dict) -> str:
        if altRef=="AH":
            if gpsType=="-gpsWithoutTopo" and (("ordinalUpperMaxM" in oZone) or ("ordinalUpperM" in oZone)):
                altM = oZone["upperM"]
                altFT = int(float(altM+100) / aixmReader.CONST.ft)      #Surélévation du plafond de 100 mètres pour marge d'altitude
                if bFeet:
                    ret = "{0}".format(altFT)
                else:
                    ret = "{0}FT AMSL".format(altFT)
                return ret
            #elif "ordinalUpperMaxM" in oZone:
            #    return oZone["upperMax"]
            else:
                if ("upper" in oZone):
                    if bFeet:
                        if oZone["upperType"]=="ALT":
                            return oZone["upperValue"]
                        elif oZone["upperType"]=="STD":
                            return oZone["upperValue"] + "00"
                        elif oZone["upperType"]=="HEI":
                            altM = oZone["upperM"]
                            altFT = int(float(altM+100) / aixmReader.CONST.ft)      #Surélévation du plafond de 100 mètres pour marge d'altitude
                            return "{0}".format(altFT)
                    else:
                        return oZone["upper"]
                else:
                    if bFeet:
                        return "99999"
                    else:
                        return "FL999"
        elif altRef=="AL":
            if gpsType=="-gpsWithoutTopo" and (("ordinalLowerMinM" in oZone) or ("ordinalLowerM" in oZone)):
                altM = oZone["lowerM"]
                altFT = int(float(altM-100) / aixmReader.CONST.ft)      #Abaissement du plancher de 100 mètres pour marge d'altitude
                if altFT <= 0:
                    if bFeet:
                        ret = "0"
                    else:
                        ret = "SFC"
                else:
                    if bFeet:
                        ret = "{0}".format(altFT)
                    else:
                        ret = "{0}FT AMSL".format(altFT)
                return ret
            #elif "ordinalLowerMinM" in oZone:
            #    return oZone["lowerMin"]
            else:
                if ("lower" in oZone):
                    if bFeet:
                        if oZone["lowerType"]=="ALT":
                            return oZone["lowerValue"]
                        elif oZone["lowerType"]=="STD":
                            return oZone["lowerValue"] + "00"
                        elif oZone["lowerType"]=="HEI":
                            if oZone["lowerValue"]=="0":
                                return "0"
                            else:
                                altM = oZone["lowerM"]
                                altFT = int(float(altM-100) / aixmReader.CONST.ft)      #Abaissement du plancher de 100 mètres pour marge d'altitude
                                return "{0}".format(altFT)
                    else:
                        return oZone["lower"]
                else:
                    if bFeet:
                        ret = "0"
                    else:
                        ret = "SFC"
                    return ret
        else:
            print("parseAlt() calling error !")
        return

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
