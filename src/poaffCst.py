#!/usr/bin/env python3

###  Context applicatif  ####
callingContext          = "Paragliding-OpenAir-FrenchFiles"             #Your app calling context
linkContext             = "http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/"
aixmParserAppName       = "aixmParser"

###  Environnement applicatif  ###
cstPoaffOutPath             = "_POAFF/"
cstPoaffWebPath             = "_POAFF_www/"
cstPoaffWebPathFiles        = "files/"
cstCfdWebPath               = "_CFD_www/"
cstReferentialPath          = "referentials/"
cstSeparatorFileName        = "@"
cstGlobalHeader             = "global"
cstCatalogFileName          = "airspacesCatalog.json"
cstAsAllGeojsonFileName     = "airspaces-all.geojson"
cstAsAllOpenairFileName     = "airspaces-all-gpsWithTopo.txt"
cstWithTopo                 = "-gpsWithTopo"
cstWithoutTopo              = "-gpsWithoutTopo"
cstLastVersionFileName      = "LastVersion_"

### scriptProcessing constantes  ###
cstSpExecute      = "Execute"                         #Identification du Flag d'execution des traitements
cstSpSrcFile      = "srcFile"                         #Identification du fichier source
cstSpOutPath      = "outPath"                         #Identification du dossier de sorties
cstSpProcessType  = "processType"                     #Typage du processus de consolidation des données
cstSpPtAdd        = "processType-AppendData"          #Consolidation des données par simple ajout (empilage des données sans contrôle de présence)
cstSpPtAddDelta   = "processType-AppendIfNotExist"    #Consolidation des données par ajout des données qui ne sont pas déjà présentes dans la consolidation

###  Standard GeoJSON structure  ###
cstGeoType          = "type"
cstGeoFeatureCol    = "FeatureCollection"
cstGeoFeatures      = "features"
cstGeoFeature       = "Feature"
cstGeoProperties    = "properties"
cstGeoGeometry      = "geometry"
cstGeoPoint         = "Point"
cstGeoMultiPoint    = "MultiPoint"
cstGeoLine          = "LineString"
cstGeoMultiLine     = "MultiLineString"
cstGeoPolygon       = "Polygon"
cstGeoMultiPolygon  = "MultiPolygon"
cstGeoCoordinates   = "coordinates"

###  Specific GeoJSON structure  ###
cstGeoHeaderFile    = "headerFile"



###  Convertion constantes ###
ft = 0.3048      #foot in meter

