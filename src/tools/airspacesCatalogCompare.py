#!/usr/bin/env python3

try:
    import bpaTools
except ImportError:
    ### Include local modules/librairies  ##
    import os, sys
    aixmParserLocalSrc  = "../../../aixmParser/src/"
    module_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(module_dir, aixmParserLocalSrc))
    import bpaTools

try:
    import poaffCst
except ImportError:
    sLocalSrc:str = "../"                                       #Include local modules/librairies
    module_dir = os.path.dirname(__file__)
    sys.path.append(os.path.join(module_dir, sLocalSrc))
    import poaffCst


def splitDescription(sVal:str, sToken:str, oPop:list) -> str:
    #if oVal[0:len(sToken)+1]==sToken+" ":
    #    oPop.update({"type":sToken})
    #    oVal = oVal[len(sToken)+1:]
    if sToken in sVal:
        oPop.update({"type":sToken})
        sVal = sVal.replace(sToken,"")
        sVal = sVal.replace("  "," ")
    return sVal

def loadAirspacesCatalog (sFile:str, context="") -> dict:
    oLog.info("loadAirspacesCatalog - file source: {0}".format(sFile))
    oJson = bpaTools.readJsonFile(sFile)
    oContents = oJson[poaffCst.cstGeoFeatures]

    oCatZones:dict = dict()
    for oZone in oContents:
        oNewPropZone:dict = dict()
        oPropsZone =oZone[poaffCst.cstGeoProperties]
        #for key,val in oPropsZone.items():
        #    oLog.info("{0} --> {1}".format(key, val))

        if context == "aixmParserCatalog":
            aKey:list = ["class","type","nameV","lower","upper","GUId","UId","id"]
            for oKey in aKey:
                oVal = oPropsZone.get(oKey, None)
                oNewPropZone.update({oKey:oVal})

        if context == "aixmParser4CFDv2":
            aKey:list = ["category","type","name","bottom","top","Ids","UId","id"]
            oTranslation:dict = {"category":"class","type":"type","codeActivity":"codeActivity","name":"nameV","bottom":"lower","top":"upper","Ids":"Ids","UId":"UId","id":"id"}
            for oKey in aKey:
                oVal = oPropsZone.get(oKey, None)
                oNewPropZone.update({oTranslation[oKey]:oVal})

        if context == "aixmParser4CFDv1":
            aKey:list = ["category","type","codeActivity","name","alt","bottom","top","bottom_m","top_m","Ids"]
            for oKey in aKey:
                oVal = oPropsZone.get(oKey, None)
                oNewPropZone.update({oKey:oVal})

        elif context == "FlyXC":
            aKey:list = ["category", "name", "bottom", "top"]
            sKey:str = "[" + oPropsZone["category"] + "] " + oPropsZone["name"]
            oNewPropZone.update({"FlyXC-Key":sKey})
            oNewPropZone.update({"orgCategory":oPropsZone["category"]})
            oNewPropZone.update({"orgName":oPropsZone["name"]})
            for oKey in aKey:
                oVal = oPropsZone[oKey]
                oVal = oVal.replace("  ", " ")      #Cleanning

                #Normalisation des Class ou Category des zones
                if oKey=="category":
                    #Transcodage pour Normalisation & Complétude de données
                    if oPropsZone["category"]=="CTR":
                        oVal = "D"
                        oPropsZone.update({"category":oVal})
                        oNewPropZone.update({"type":"CTR"})
                    if oPropsZone["category"]=="RMZ":
                        oNewPropZone.update({"type":"RMZ"})
                    elif oPropsZone["category"]=="DANGER":
                        oVal = "Q"
                        oPropsZone.update({"category":oVal})
                        oNewPropZone.update({"type":oVal})
                    elif oPropsZone["category"]=="PROHIBITED":
                        oVal = "P"
                        oPropsZone.update({"category":oVal})
                        oNewPropZone.update({"type":"P"})
                    elif oPropsZone["category"]=="RESTRICTED":
                        oVal = "R"
                        oPropsZone.update({"category":oVal})
                        oNewPropZone.update({"type":oVal})
                    elif oPropsZone["category"]=="GLIDING":
                        oVal = "W"
                        oPropsZone.update({"category":oVal})
                        oNewPropZone.update({"type":"R"})
                        oNewPropZone.update({"codeActivity":"GLIDER"})

                #Cleanning; Transcodage & Complétude de données au niveau du nommage
                elif oKey=="name":
                    #Cleaning du nommage de zones
                    oVal=oVal.replace("CTA-", "CTA ")
                    oVal=oVal.replace("LF R ", "LFR")
                    oVal=oVal.replace("LFR ", "LFR")
                    #oVal = splitDescription(oVal, "TMA", oNewPropZone)
                    #oVal = splitDescription(oVal, "CTR", oNewPropZone)
                    #oVal = splitDescription(oVal, "CTA", oNewPropZone)

                    if oVal[0:4]=="Axe ":
                        oPropsZone.update({"category":"W"})
                        oNewPropZone.update({"category":"W"})
                        oNewPropZone.update({"type":"Assist"})
                        oNewPropZone.update({"codeActivity":"GLIDER"})

                    #Transcodage & Complétude de données
                    #if oVal[0:2]=="D " and oPropsZone["category"]=="Q":
                    #    oVal = oVal[2:]
                    #if oVal[0:2]=="R ":
                    #    oVal = "LFR" + oVal[2:]
                    #else:
                    #    oVal = oVal[11:]

                    """
                    #Cleaning des nommage de zones; exemples :
                    # "Agen2 119.15" --> a tranformer en "Agen 2 119.15"
                    oNewVal:str = ""
                    oPrevCharValue:str = ""
                    oPrevCharDigit:bool = False
                    iIdx:int = 0
                    for oChar in oVal:
                        oCharDigit = oChar.isdigit()
                        if oCharDigit and (not oPrevCharDigit) and (not oPrevCharValue in [" ", "-", "."]) and iIdx>0:
                            oNewVal += " "
                        oNewVal += oChar
                        oPrevCharValue = oChar
                        oPrevCharDigit = oCharDigit
                        iIdx+=1
                    oVal = oNewVal
                    """

                #Cleanning de valeur
                if oKey=="bottom" or oKey=="top":
                    oVal=oVal.replace("FL ", "FL")
                    oVal=oVal.replace("F ", "FT ")
                    oVal=oVal.replace("MSL", "AMSL")
                    oVal=oVal.replace("GND", "SFC")
                    pos = oVal.find("SFC")
                    if pos>1: oVal=oVal.replace("SFC", "AGL")

                #Stockage du nouveau couple: clé/valeur
                oNewPropZone.update({oKey:oVal})


        sIdx = len(oCatZones) + 1
        oCatZones.update({sIdx:oNewPropZone})
    #oLog.info("Catalog: {0}".format(oCatZones))
    return oCatZones


def writeTextFile(sFile="", oText=None):
    if sFile!="":
        oLog.info("Write file {0}".format(sFile), outConsole=True)
        with open(sFile, "w", encoding="cp1252", errors="replace") as output:
            output.write(oText)
    return


def saveCalalogCSV(sFileName:str, oCatalog) -> None:
    csv = ""
    #Order keys; for header in CSV file
    #aKey:list = ["category","type","codeActivity","name","alt","bottom","top","bottom_m","top_m","Ids"]
    oCols = {"category":0, "type":0, "codeActivity":0, "name":0, "bottom":0, "top":0, "bottom_m":0,"top_m":0, "alt":0, "Ids":0}
    for key0,val0 in oCatalog.items():
        for key1,val1 in val0.items():
            oCols.update({key1:0})

    #List all columns in order of the global index on columns
    for colKey,colVal in oCols.items():
        csv += '"{0}";'.format(colKey)

    #Content CSV file
    for key,val in oCatalog.items():
        csv += "\n"
        #Extract columns in order of the global index on columns
        for colKey,colVal in oCols.items():
            if colKey in val:
                csv += '"{0}";'.format(val[colKey])
            else:
                csv += ';'

    writeTextFile(sFileName, csv)
    return


def saveCalalogCSV2(sFileName:str, oCatalog) -> None:
    csv = ""
    #Order keys; for header in CSV file
    #aKey:list = ["class","type","codeActivity","nameV","lower","upper","GUId","UId","id"]
    oCols = {"class":0, "type":0, "nameV":0, "lower":0, "upper":0, "GUId":0, "UId":0, "id":0}
    for key0,val0 in oCatalog.items():
        for key1,val1 in val0.items():
            oCols.update({key1:0})

    #List all columns in order of the global index on columns
    for colKey,colVal in oCols.items():
        csv += '"{0}";'.format(colKey)

    #Content CSV file
    for key,item in oCatalog.items():
        csv += "\n"
        for colKey,colVal in item.items():
            csv += '"{0}";'.format(colVal)

    writeTextFile(sFileName, csv)
    return


def comparePoaffCfdWithFlyXC() -> None:
    sFileSrc1 = cfdPath + "20200920_airspaces-ffvl-cfd.geojson"
    sFileSrc2 = flyXCPath + "20200420_FlyXC-app_airspaces.geojson"
    #oLog.info("Compare files: \n\t{0} \n\t{1}".format(sFilseSrc1, sFilseSrc2))
    oCat1 = loadAirspacesCatalog(sFileSrc1, "aixmParser4CFDv1")
    oCat2 = loadAirspacesCatalog(sFileSrc2, "FlyXC")
    saveCalalogCSV(deltaPath + "aixmpCatalog.csv", oCat1)
    saveCalalogCSV(deltaPath + "flyxcCatalog.csv", oCat2)
    return


def extractGeoJSON() -> None:
    #sFileSrc = "20210109_airspaces-freeflight-geoFrench.geojson"
    sFileSrc = "20210109_airspaces-freeflight-geoBelgium.geojson"

    oLog.info("extractGeoJSON() - file source: {0}".format(sFileSrc))
    oJson = bpaTools.readJsonFile(cfdPath + sFileSrc)
    oContents = oJson[poaffCst.cstGeoFeatures]

    oCleanSource:list = list()
    oExcludeZones:list = list()

    for oZone in oContents:
        oPropsZone =oZone[poaffCst.cstGeoProperties]
        bExclude:bool        = bool(oPropsZone.get("class","")=="Q" and oPropsZone.get("type","")=="SIV")
        bExclude = bExclude or bool(oPropsZone.get("id","") in ["EBBU TMZ","EBBU RMZ","EDCLG"])
        #bExclude = bExclude or bool(oPropsZone.get("srcClass","")=="G" and oPropsZone.get("srcType","")=="RAS")
        if bExclude:
            oExcludeZones.append(oZone)
        else:
            oCleanSource.append(oZone)

    oNewJson:dict = {"type": "FeatureCollection","features":oCleanSource}
    sFileDst = sFileSrc.replace(".geojson","") + "-clean.geojson"
    bpaTools.writeJsonFile(cfdPath + sFileDst,oNewJson)

    oNewJson:dict = {"type": "FeatureCollection","features":oExcludeZones}
    sFileDst = sFileSrc.replace(".geojson","") + "-exclude.geojson"
    bpaTools.writeJsonFile(cfdPath + sFileDst,oNewJson)
    return


def comparePoaffWithPoaff() -> None:
    sStdAreaCode:str = "-geoFrenchAll"        #geoFrenchAll / geoBelgium / geoSwitzerland

    sFileSrc1 = "20210216_airspaces-freeflight" + sStdAreaCode + ".geojson"
    sFileSrc2 = "20210301_airspaces-freeflight" + sStdAreaCode + ".geojson"

    sFileDst1 = sFileSrc1.replace(".geojson","") + "-catalog.csv"
    sFileDst2 = sFileSrc2.replace(".geojson","") + "-catalog.csv"

    #oLog.info("Compare files: \n\t{0} \n\t{1}".format(sFilseSrc1, sFilseSrc2))
    oCat1 = loadAirspacesCatalog(cfdPath + sFileSrc1, "aixmParserCatalog")
    oCat2 = loadAirspacesCatalog(cfdPath + sFileSrc2, "aixmParserCatalog")
    saveCalalogCSV2(deltaPath + "/" + sFileDst1, oCat1)
    saveCalalogCSV2(deltaPath + "/" + sFileDst2, oCat2)
    return



if __name__ == '__main__':
    ### Context applicatif
    callingContext      = "Paragliding-OpenAir-FrenchFiles"         #Your app calling context
    appName             = bpaTools.getFileName(__file__)
    appPath             = bpaTools.getFilePath(__file__)            #or your app path
    appVersion          = "1.1.0"                                   #or your app version
    appId               = appName + " v" + appVersion
    outPath             = appPath + "../../output/"
    cfdPath             = outPath + "_CFD_www/"
    flyXCPath           = cfdPath + "FlyXC/"
    deltaPath           = cfdPath + "delta/"
    logFile             = deltaPath + "_" + appName + ".log"
    bpaTools.createFolder(outPath)                                  #Init dossier
    bpaTools.createFolder(deltaPath)                                  #Init dossier

    oLog = bpaTools.Logger(appId,logFile)
    oLog.resetFile()

    #comparePoaffCfdWithFlyXC()
    comparePoaffWithPoaff()
    #extractGeoJSON()

    print()
    oLog.Report()
    oLog.closeFile



