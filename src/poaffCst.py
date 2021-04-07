#!/usr/bin/env python3

###  Context applicatif  ####
callingContext:str          = "Paragliding-OpenAir-FrenchFiles"             #Your app calling context
linkContext:str             = "http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/"
aixmParserAppName:str       = "aixmParser"

###  Environnement applicatif  ###
cstPoaffOutPath:str         = "_POAFF/"
cstPoaffWebPath:str         = "_POAFF_www/"
cstPoaffWebPathFiles:str    = "files/"
cstCfdWebPath:str           = "_CFD_www/"
cstReferentialPath:str      = "referentials/"
cstSeparatorFileName:str    = "@"
cstGlobalHeader:str         = "global"
cstCatalogFileName:str      = "airspacesCatalog.json"
cstAsAllGeojsonFileName:str = "airspaces-all.geojson"
cstAsAllOpenairFileName:str = "airspaces-all-gpsWithTopo.txt"
cstWithTopo:str             = "-gpsWithTopo"
cstWithoutTopo:str          = "-gpsWithoutTopo"
cstLastVersionFileName:str  = "LastVersion_"

### Spécificité applicative ###
cstPoaffCloneObject:str     = "PoaffClone-"

### scriptProcessing constantes  ###
cstSpExecute:str            = "Execute"                         #Identification du Flag d'execution des traitements
cstSpSrcFile:str            = "srcFile"                         #Identification du fichier source
cstSpSrcOwner:str           = "srcOwner"                        #Identification du propriétaire du fichier source
cstSpOutPath:str            = "outPath"                         #Identification du dossier de sorties
cstSpProcessType:str        = "processType"                     #Typage du processus de consolidation des données
cstSpPtAdd:str              = "processType-AppendData"          #Consolidation des données par simple ajout (empilage des données sans contrôle de présence)
cstSpPtAddDelta:str         = "processType-AppendIfNotExist"    #Consolidation des données par ajout des données qui ne sont pas déjà présentes dans la consolidation

###  Standard GeoJSON structure  ###
cstGeoType:str              = "type"
cstGeoFeatureCol:str        = "FeatureCollection"
cstGeoFeatures:str          = "features"
cstGeoFeature:str           = "Feature"
cstGeoProperties:str        = "properties"
cstGeoGeometry:str          = "geometry"
cstGeoPoint:str             = "Point"
cstGeoMultiPoint:str        = "MultiPoint"
cstGeoLine:str              = "LineString"
cstGeoMultiLine:str         = "MultiLineString"
cstGeoPolygon:str           = "Polygon"
cstGeoMultiPolygon:str      = "MultiPolygon"
cstGeoCoordinates:str       = "coordinates"
cstGeoHeaderFile:str        = "headerFile"             #Extended GeoJSON structure

#### Paramétrage de l'optimisation des tracés ####
cstGeojsonCfdEpsilonReduce:float    = -1    #Simplification des tracés GeoJSON pour sortie officielle CFD
cstGeojsonEpsilonReduce:float       = -1    #Simplification des tracés GeoJSON standard
cstKmlCfdEpsilonReduce:float        = -1    #Simplification des tracés KML     pour sortie officielle CFD
cstKmlEpsilonReduce:float           = -1    #Simplification des tracés KML standard
cstOpenairCfdEpsilonReduce:float    = -1    #Simplification des tracés Openair pour sortie officielle CFD
cstOpenairEpsilonReduce:float       = -1    #Simplification des tracés Openair standard
cstOpenairEpsilonReduceMR:float     = -1    #Simplification des tracés Openair pour les zones régionnales "ISO_Perimeter=Partial" (gpsWithTopo or gpsWithoutTopo)
cstOpenairDigitOptimize:float       =  0    #openairDigitOptimize=-1 / 0 / 2

