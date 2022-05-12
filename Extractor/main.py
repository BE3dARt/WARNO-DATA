import descriptor
import helper
import copy

####################################################################
# RETRIEVE A VARIABLE FROM A FILE
# filename: Name of the file the variable is defined in
# varName: Variable name
####################################################################
def getVariableFromNDFFile(filename, varName):

    #Read file into one large string
    file = open(filename,"r").read()

    #Capture variable
    index = file.find(varName)
    var = file[index+len(varName):file.find("\n", index+len(varName))]

    var = var.translate({ord('='):None})
    var = var.translate({ord('('):None})
    var = var.translate({ord(')'):None})
    
    if var.find("//") != -1:
        var = var[:var.find("//")]

    if var.find("* Metre") != -1:
        var = var[:var.find("* Metre")]
    
    var = var.strip()

    #Special Examples
    if varName == "MultiplicateurMetreRTSVersDistanceFeedbackTactique" or varName == "MultiplicateurMetreRTSVersVitesseTactiquePourVehicule":
        var1 = float(var[:var.find("div")])
        var2 = float(var[var.find("div")+3:])
        var = var1 / var2

    return var


####################################################################
# CONSTANTS
####################################################################
constant_Distance = getVariableFromNDFFile("GDConstantes.ndf", "MultiplicateurMetreRTSVersDistanceFeedbackTactique")
constant_Speed = getVariableFromNDFFile("GDConstantes.ndf", "MultiplicateurMetreRTSVersVitesseTactiquePourVehicule")
constant_AltitudeMax = getVariableFromNDFFile("AirplaneConstantes.ndf", "MaxAltitude is") #Metre
constant_PitchSpeed = getVariableFromNDFFile("AirplaneConstantes.ndf", "MaxPitchSpeed is")
constant_AltitudeMinForRoll = getVariableFromNDFFile("AirplaneConstantes.ndf", "MinAltitudeForRoll is") #Metre
constant_MinRollSpeedForRoll = getVariableFromNDFFile("AirplaneConstantes.ndf", "MinRollSpeedForRoll is")

####################################################################
# SEARCH KEYWORD IN GIVEN TEXT AND RETRIEVE ITS VALUE
####################################################################
def analzye(text, keyword):
    index = text.find(keyword[1])
    
    #If the given keyword does not exist
    if index == -1:
        return None
    
    #If keyword itself is present in the value 
    if keyword[0] == "WeaponDescriptor" and keyword[1] == "WeaponDescriptor":
        keywordlength = len(keyword[1])
        captured = text[index:text.find("\n", index)]
        return captured

    #If value of keyword is NOT an array
    if keyword[0] != "RoleList" and keyword[0] != "SpecialtiesList" and keyword[0] != "Salves" and keyword[0] != "SalvoIsMainSalvo":
        keywordlength = len(keyword[1])
        captured = text[index+keywordlength:text.find("\n", index+keywordlength)]
        captured = captured.translate({ord('\''):None})
        captured = captured.translate({ord('='):None})
        captured = captured.translate({ord(','):None})
        captured = captured.translate({ord('('):None})
        captured = captured.translate({ord(')'):None})
        captured = captured.translate({ord('~'):None})
        captured = captured.translate({ord('/'):None})
        captured = captured.strip()
    else:
        keywordlength = len(keyword[1])
        captured = text[index+keywordlength:text.find("]", index+keywordlength)]
        captured = captured.translate({ord('='):None})
        captured = captured.translate({ord('['):None})
        captured = captured.translate({ord('\''):None})
        captured = captured.translate({ord(' '):None})
        captured = captured.translate({ord('\n'):None})

        #If array always has one element
        if keyword[0] != "SpecialtiesList" and keyword[0] != "Salves" and keyword[0] != "SalvoIsMainSalvo":
            return helper.stringToType(captured.translate({ord(','):None}))

        #Seperate the elements by looking at ","
        captureArrayString = ""
        captureArray = []
        for i in range(len(captured)):
            if captured[i] == ",": #We need a dedicated return type function which gives either integer, float, string or boolean back
                captureArray.append(helper.stringToType(captureArrayString))
                captureArrayString = ""
            else:
                captureArrayString += captured[i]
                
        return captureArray #Returns array. Maybe it needs quotation marks to be a JSON array.

    #If keyword is a constant and always the same
    if keyword[0] == "AltitudeMax":
        return constant_AltitudeMax * constant_Distance
    if keyword[0] == "PitchSpeed":
        return constant_PitchSpeed
    if keyword[0] == "AltitudeMinForRoll":
        return constant_AltitudeMinForRoll * constant_Distance
    if keyword[0] == "MinRollSpeedForRoll":
        return constant_MinRollSpeedForRoll

    #SPEED: For every value that has "* Metre" in it, chop it away and multiply it by the corresponding constant.
    if keyword[0] in ["MaxSpeed","MaxAcceleration","MaxDeceleration", "UpwardSpeed"]:
        return float(captured[:-8]) * constant_Speed

    #Distance: For every value that has "* Metre" in it, chop it away and multiply it by the corresponding constant.
    if keyword[0] in ["AltitudeMin","Altitude","AgilityRadius"]:
        return float(captured[:-8]) * constant_Distance

    #Special cases
    match keyword[0]:
        case "WeaponDescriptor":
            return captured[:-34]
        case "UniteDescriptor":
            return captured[:-21]
        case "Factory":
            return captured[17:]
        case "Nationalite":
            return captured[12:]

    #Return value in it's correct type
    return helper.stringToType(captured)

def gogoRecursion(subStr, level, index):

    counterChar = 0
    counterUnit = 0
    temporaryStr = ""

    while counterChar < len(subStr):
        match level:
            case 0: 
                if subStr[counterChar:counterChar+23] == "export WeaponDescriptor" or counterChar == len(subStr)-1:
                    if counterUnit > 0:

                        UnitDescriptor.append(copy.deepcopy(descriptor.weapon))
                        
                        UnitDescriptor[index[0]][0][2] = analzye(temporaryStr, UnitDescriptor[index[0]][0])
                        print(UnitDescriptor[index[0]-1][1][0] + ": " + str(analzye(temporaryStr, UnitDescriptor[index[0]-1][1])))
                        print(UnitDescriptor[index[0]-1][2][0] + ": " + str(analzye(temporaryStr, UnitDescriptor[index[0]-1][2])))
                        print(UnitDescriptor[index[0]-1][3][0] + ": " + str(analzye(temporaryStr, UnitDescriptor[index[0]-1][3])))
                        gogoRecursion(temporaryStr, level + 1, index)
                        index[1] = 1
                        index[0] += 1

                    temporaryStr = ""
                    counterUnit += 1
            case 1:
                if subStr[counterChar:counterChar+24] == "TTurretTwoAxisDescriptor" or subStr[counterChar:counterChar+21] == "TTurretUnitDescriptor" or subStr[counterChar:counterChar+27] == "TTurretInfanterieDescriptor" or counterChar == len(subStr)-1:
                    if counterUnit > 0:
                        addToIndex = 4 if index[1] == 1 else 17 + 7 *(index[1] -2)
                        print(UnitDescriptor[index[0]-1][0+addToIndex][0] + ": " + str(analzye(temporaryStr, UnitDescriptor[index[0]-1][0+addToIndex])))
                        print(UnitDescriptor[index[0]-1][1+addToIndex][0] + ": " + str(analzye(temporaryStr, UnitDescriptor[index[0]-1][1+addToIndex])))
                        print(UnitDescriptor[index[0]-1][2+addToIndex][0] + ": " + str(analzye(temporaryStr, UnitDescriptor[index[0]-1][2+addToIndex])))
                        print(UnitDescriptor[index[0]-1][3+addToIndex][0] + ": " + str(analzye(temporaryStr, UnitDescriptor[index[0]-1][3+addToIndex])))
                        index[1] = index[1] + 1
                        gogoRecursion(temporaryStr, level + 1, index)
                        index[2] = 1

                    temporaryStr = ""
                    counterUnit += 1
            case 2:
                if subStr[counterChar:counterChar+24] == "TMountedWeaponDescriptor" or counterChar == len(subStr)-1:
                    if counterUnit > 0:
                        addToIndex = 4 if index[1] == 2 else 17 + 7 *(index[1] -3)
                        addToIndex = addToIndex + 3 * (index[2])
                        print(UnitDescriptor[index[0]-1][1+addToIndex][0] + ": " + str(analzye(temporaryStr, UnitDescriptor[index[0]-1][1+addToIndex])))
                        print(UnitDescriptor[index[0]-1][2+addToIndex][0] + ": " + str(analzye(temporaryStr, UnitDescriptor[index[0]-1][2+addToIndex])))
                        print(UnitDescriptor[index[0]-1][3+addToIndex][0] + ": " + str(analzye(temporaryStr, UnitDescriptor[index[0]-1][3+addToIndex])))
                        index[2] = index[2] + 1

                    temporaryStr = ""
                    counterUnit += 1

        temporaryStr += subStr[counterChar]
        counterChar += 1

UnitDescriptor= []
gogoRecursion(open("WeaponDescriptor.ndf","r").read(), 0, [0, 1, 1])
print(UnitDescriptor)

def captureUnitDescriptor():
    file = open("UniteDescriptor.ndf","r").read()

    counter = 0
    unitCounter = 0
    stringVehicle = ""
    
    while True:

        #New Weapon Type
        if file[counter:counter+17] == "export Descriptor": #We need to include the last entry!!!! Change this
            if unitCounter > 0:

                for x in descriptor.unit:
                    print(x[0] + ": " + str(analzye(stringVehicle, x)))
                    
                print("")

                stringVehicle = ""
                
            unitCounter += 1 #Vehicle counter

        stringVehicle += file[counter]
            
        counter += 1 #Count up loop

        if counter == len(file):
            break

#captureWeaponDescriptor()
#captureUnitDescriptor()
input("Press enter to continue...")
