#!/usr/bin/env python3


### Include local modules/librairies
import os
import sys
aixmParserLocalSrc  = "../../aixmParser/src/"
module_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(module_dir, aixmParserLocalSrc))
import bpaTools



def splitDescription(oVal:str, sToken:str, oPop:list):
    #if oVal[0:len(sToken)+1]==sToken+" ":
    #    oPop.update({"type":sToken})
    #    oVal = oVal[len(sToken)+1:]
    if sToken in oVal:
        oPop.update({"type":sToken})
        oVal = oVal.replace(sToken,"")
        oVal = oVal.replace("  "," ")
    return oVal


def loadAirspacesCatalog (sFile:str, context="") -> dict:
    oLog.info("loadAirspacesCatalog - file source: {0}".format(sFile))
    oJson = bpaTools.readJsonFile(sFile)
    oContents = oJson["features"]

    oCatZones = dict()
    for oZone in oContents:
        oNewPropZone = dict()
        oPropsZone = oZone["properties"]

        #for key,val in oPropsZone.items():
        #    oLog.info("{0} --> {1}".format(key, val))

        if context == "FlyXC":
            aKey:list = ["name", "category", "bottom", "top"]
            sKey:str = "[" + oPropsZone["category"] + "] " + oPropsZone["name"]
            oNewPropZone.update({"FlyXC-Key":sKey})
            for oKey in aKey:
                oVal = oPropsZone[oKey]
                
                #Cleanning; Transcodage & Complétude de données au niveau du nommage
                if oKey=="name":
                    #Cleaning du nommage de zones
                    oVal=oVal.replace("CTA-", "CTA ")
                    oVal=oVal.replace("LF R ", "LFR")
                    oVal=oVal.replace("LFR ", "LFR")
                    oVal = splitDescription(oVal, "TMA", oNewPropZone)
                    oVal = splitDescription(oVal, "CTR", oNewPropZone)
                    oVal = splitDescription(oVal, "CTA", oNewPropZone)   
                    
                    #Transcodage & Complétude de données
                    if oVal[0:2]=="D " and oPropsZone["category"]=="DANGER":
                        oPropsZone.update({"category":"Q"})
                        oNewPropZone.update({"type":"Q"})
                        oNewPropZone.update({"codeActivity":"DANGER"})
                        oVal = oVal[2:]
                    if oPropsZone["category"]=="GLIDING":
                        oPropsZone.update({"category":"W"})
                        oNewPropZone.update({"type":"R"})
                        oNewPropZone.update({"codeActivity":"GLIDER"})
                        if oVal[0:2]=="R ":
                            oVal = "LFR" + oVal[2:]
                        else:
                            oVal = oVal[11:]
                    if oVal[0:3]=="VV " and (oPropsZone["category"] in ["GLIDING", "RESTRICTED"]):
                        oPropsZone.update({"category":"W"})
                        oNewPropZone.update({"type":"R"})
                        oNewPropZone.update({"codeActivity":"GLIDER"})
                        if oVal[0:5]=="VV R ":
                            oVal = "LFR" + oVal[5:]
                        else:
                            oVal = oVal[3:]
                            
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
                
                #Transcodage du nommage de clé
                if oKey=="category":
                    oKey="class"
                    #oVal=oVal.replace("RESTRICTED", "R")
                    #oVal=oVal.replace("RESTRICTED", "R")
                    #oVal=oVal.replace("RESTRICTED", "R")
                
                #Cleanning de valeur
                if oKey=="bottom" or oKey=="top":
                    oVal=oVal.replace("FL ", "FL")
                    oVal=oVal.replace("F ", "FT ")
                    oVal=oVal.replace("MSL", "AMSL")
                    oVal=oVal.replace("GND", "SFC")
                    pos = oVal.find("SFC")
                    if pos>1: oVal=oVal.replace("SFC", "ASFC")
                
                #Stockage du nouveau couple: clé/valeur
                oNewPropZone.update({oKey:oVal})

        else:        # context == "aixmParser":
            aKey:list = ["UId", "id", "class", "type", "codeActivity", "name", "nameV", "alt"]
            for oKey in aKey:
                if oKey in oPropsZone:
                    oVal = oPropsZone[oKey]
                    if oKey=="alt":
                        aAlt = oVal[1:-1].split("/")
                        oNewPropZone.update({"bottom":aAlt[0]})
                        oNewPropZone.update({"top":aAlt[1]})
                    else:
                        oNewPropZone.update({oKey:oVal})

        sIdx = len(oCatZones) + 1
        oCatZones.update({sIdx:oNewPropZone})
    #oLog.info("Catalog: {0}".format(oCatZones))
    return oCatZones


def writeTextFile(sFile="", oText=None):
    if sFile!="":
        oLog.info("Write file {0}".format(sFile), outConsole=True)
        with open(sFile, "w", encoding="utf-8") as output:
            output.write(oText)
    return


def saveCalalogCSV(sFileName:str, oCatalog) -> None:
    csv = ""
    
    #Order keys; for header in CSV file
    oCols = {"UId":0, "id":0, "class":0, "type":0, "codeActivity":0, "name":0, "nameV":0, "bottom":0, "top":0}
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



if __name__ == '__main__':
    ### Context applicatif
    callingContext      = "Paragliding-OpenAir-FrenchFiles"         #Your app calling context
    appName             = bpaTools.getFileName(__file__)
    appPath             = bpaTools.getFilePath(__file__)            #or your app path
    appVersion          = "1.0.0"                                   #or your app version
    appId               = appName + " v" + appVersion
    outPath             = appPath + "../output/"
    cfdPath             = outPath + "_CFD_www/"
    flyXCPath           = cfdPath + "FlyXC/"
    deltaPath           = cfdPath + "delta/"
    logFile             = deltaPath + "_" + appName + ".log"
    bpaTools.createFolder(outPath)                                  #Init dossier
    bpaTools.createFolder(deltaPath)                                  #Init dossier

    oLog = bpaTools.Logger(appId,logFile)
    oLog.resetFile()

    #sFilseSrc1 = cfdPath + "airspaces-freeflight.geojson"
    sFilseSrc1 = cfdPath + "airspaces-vfr.geojson"
    sFilseSrc2 = flyXCPath + "20200420_FlyXC-app_airspaces.geojson"
    #oLog.info("Compare files: \n\t{0} \n\t{1}".format(sFilseSrc1, sFilseSrc2))

    oCat1 = loadAirspacesCatalog(sFilseSrc1, "aixmParser")
    oCat2 = loadAirspacesCatalog(sFilseSrc2, "FlyXC")

    saveCalalogCSV(deltaPath + "aixmpCatalog.csv", oCat1)
    saveCalalogCSV(deltaPath + "flyxcCatalog.csv", oCat2)
    

    print()
    oLog.Report()
    oLog.closeFile

