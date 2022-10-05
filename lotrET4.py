# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 09:31:28 2021

@author: maxlm
"""

# -*- coding: utf-8 -*-


import csv
import random
import statistics
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score

## calcule le score d'un nom pour chaque race en fonction des differents criteres
def score(ListeRaces, string_to_iterate, allLetterPresent, allLetterDepend, allLetterSuccess, allSyllabDistrib, allPhonetic, parameters, name):
    bestRace=ListeRaces[0]
    bestScore = -float("inf")
     
    lettersPresent = getLettersForOne(string_to_iterate, name)
    letterDistrib = oftenTogetherForOne(string_to_iterate, name)
    letterSuccess = oftenAfterForOne(string_to_iterate, name)
    namePhonetic = phoneticForOne(name)
    

    syllabNumber = compareSyllab(ListeRaces, allSyllabDistrib, name)
    letterFreq = compareLetterFreq(ListeRaces, string_to_iterate, lettersPresent, allLetterPresent)
    letterDepend = compareLetterDistrib(ListeRaces, letterDistrib, allLetterDepend)
    letterAfter = compareLetterSuccess(ListeRaces, letterSuccess, allLetterSuccess)
    phonetics = comparePhonetics(ListeRaces, namePhonetic, allPhonetic)

    syllabNumber = rank(syllabNumber)
    letterFreq = rank(letterFreq)
    letterDepend = rank(letterDepend)
    letterAfter = rank(letterAfter)
    phonetics = rank(phonetics)

    for race in ListeRaces:
        score = syllabNumber[race] * parameters[race][1] + letterFreq[race] * parameters[race][0] + letterDepend[race]* parameters[race][2] + letterAfter[race] * parameters[race][3] + phonetics[race] * parameters[race][4]   
        if score > bestScore :
            bestScore = score
            bestRace = race
    return (bestRace, bestScore)

## trie les scores obtenus et attribue des valeurs en fonction du rang et de la valeur du score. Permet d'éviter dans un premier temps de pondérer certins critères plus que d'autres
def rank(data):
    data2 = {}
    data3 = sorted(data.items(), key=lambda kv: kv[1])
    cpt = 0
    for item in data3:
        key, value = item
        multi = 1
        if value <= 0:
            multi = 0
        data2[key] = cpt * multi
        cpt += 1
    
    return data2

## remplace les majuscules d'une chaine de caracteres en minuscule
def convToMin(s):
    convertToMin = dict([
    ("A","a"),
    ("B","b"),
    ("C","c"),
    ("D","d"),
    ("E","e"),
    ("F","f"),
    ("G","g"),
    ("H","h"),
    ("I","i"),
    ("J","j"),
    ("K","k"),
    ("L","l"),
    ("M","m"),
    ("N","n"),
    ("O","o"),
    ("P","p"),
    ("Q","q"),
    ("R","r"),
    ("S","s"),
    ("T","t"),
    ("U","u"),
    ("V","v"),
    ("W","w"),
    ("X","x"),
    ("Y","y"),
    ("Z","z"),
    ("Ë","ë"),
    ("Ä","ä"),
    ("Ö","ö"),
    ("Â","â"),
    ("Ê","ê"),
    ("Î","î"),
    ("Ô","ô"),
    ("Á","á"),
    ("É","é"),
    ("Í","í"),
    ("Ó","ó"),
    ("Ú","ú")
    ])
    s2 = ""
    for i in range(len(s)):
        if s[i] in convertToMin:
            s2 += convertToMin[s[i]]
        else:
            s2 += s[i]
    return s2

## donne la frequence d'apparition de chaque lettre pour chaque race (moyenne sur le nombre d'individus de chaque race)
def  getLettersData(ListeRaces, string_to_iterate, data):
    dicoRaces = {}
    for race in ListeRaces :
        alphabet ={}
        for char in string_to_iterate:
           alphabet[char]=0
        dicoRaces[race]=alphabet
    for row in data:
        for char in convToMin(row[1]):
            dicoRaces.get(row[2])[char]+=1
    raceCounter = countMembers(ListeRaces, data)
    for race in ListeRaces:
        for char in string_to_iterate:
            if raceCounter.get(race) != 0:
                dicoRaces.get(race)[char]/=float(raceCounter.get(race))
    return dicoRaces

## donne la frequence de chaque lettre du nom data
def getLettersForOne(string_to_iterate,data):
    alphabet ={}
    for char in string_to_iterate:
        alphabet[char]=0
    for char in convToMin(data):
        alphabet[char]+=1
    return alphabet

## compte le nombre de syllabes d'un mot
def countSyllabs(s):
    voyelles = ["a","e","i","o","u","y"]
    accents = ["ä","ë","ö","â","ê","î","û","ô","é","á","í","ó","ú"]
    syllabs = 0
    i=0
    voy = False
    while i < len(s):
        if s[i] in voyelles and not voy:
            syllabs += 1
            i += 1
            voy = True
        elif s[i] in voyelles:
            if s[i] == "y":
                voy = False
            i += 1
        elif s[i] in accents:
            syllabs += 1
            i += 1
            voy = False
        elif s[i] == "*":
            syllabs += 1
            i += 1
            voy = False
        else:
            i += 1
            voy = False
    return syllabs

## donne pour chaque race la distribution du nombre de syllabes
def getDistribSyllab(ListeRaces, data):
    DistribSyllab={}
    for race in ListeRaces :
        nbSyll ={}
        for i in range (0,10):
           nbSyll[i]=0
        DistribSyllab[race]=nbSyll
    for row in data:
        DistribSyllab.get(row[2])[countSyllabs(convToMin(row[1]))]+=1
            
    raceCounter = countMembers(ListeRaces, data)
    for race in ListeRaces:
        for i in range (0,10):
            if raceCounter.get(race) != 0:
                DistribSyllab.get(race)[i]/=float(raceCounter.get(race))
    return DistribSyllab

## Donne la probabilité pour chaque race de tomber au moins une fois sur une lettre spécifique en sachant qu'une autre y est (moyenne sur le nombre d'individus possédant cette deuxième lettre par race)
def oftenTogether(ListeRaces, string_to_iterate, data):
    togethers = dict([])
    for race in ListeRaces:
        firstLetter = dict([])
        for letter in string_to_iterate:
            lettersProbs = dict([])
            for letter2 in string_to_iterate:
                lettersProbs[letter2]= 0
            firstLetter[letter] = lettersProbs
        togethers[race]=firstLetter

    letterRaceCounter = dict([])
    for race in ListeRaces:
        letterCounter = dict([])
        for letter in string_to_iterate:
            letterCounter[letter]=0
        letterRaceCounter[race] = letterCounter

    for row in data:
        for letter in string_to_iterate:
            if letter in convToMin(row[1]):
                letterRaceCounter[row[2]][letter]+=1
        treated = ""
        for i in range(len(row[1])):
            if convToMin(row[1])[i] not in treated:
                post_treated = ""
                for j in range(i+1,len(row[1])):
                    if convToMin(row[1])[j] not in post_treated:
                        togethers[row[2]][convToMin(row[1])[j]][convToMin(row[1])[i]]+=1
                        if convToMin(row[1])[i] != convToMin(row[1])[j]:
                            togethers[row[2]][convToMin(row[1])[i]][convToMin(row[1])[j]]+=1
                    post_treated+=convToMin(row[1])[j]
            treated+=convToMin(row[1])[i]

    for race in ListeRaces:
        for letter in string_to_iterate:
            for letter2 in string_to_iterate:
                if letterRaceCounter[race][letter] != 0:
                    togethers[race][letter][letter2]/=float(letterRaceCounter[race][letter])
    
    return togethers

## donne la fréquence d'apparition de chaque lettre sachant la présence des autres lettres
def oftenTogetherForOne(string_to_iterate, data):
    firstLetter = dict([])
    for letter in string_to_iterate:
        lettersProbs = dict([])
        for letter2 in string_to_iterate:
            lettersProbs[letter2]= 0
        firstLetter[letter] = lettersProbs

    treated = ""
    for i in range(len(data)):
        if convToMin(data)[i] not in treated:
            post_treated = ""
            for j in range(i+1,len(data)):
                firstLetter[convToMin(data)[j]][convToMin(data)[i]]+=1
                if convToMin(data)[i] != convToMin(data)[j]:
                    firstLetter[convToMin(data)[i]][convToMin(data)[j]]+=1
                post_treated+=convToMin(data)[j]
        treated+=convToMin(data)[i]
    
    return firstLetter

## donne la fréquence d'apparition d'une lettre juste après une autre (moyenne sur le nombre d'individus avec cette seconde lettre dans leur nom par race)
def oftenAfter(ListeRaces, string_to_iterate, data):
    after = dict([])
    for race in ListeRaces:
        firstLetter = dict([])
        for letter in string_to_iterate:
            lettersProbs = dict([])
            for letter2 in string_to_iterate:
                lettersProbs[letter2]= 0
            firstLetter[letter] = lettersProbs
        after[race]=firstLetter

    letterRaceCounter = dict([])
    for race in ListeRaces:
        letterCounter = dict([])
        for letter in string_to_iterate:
            letterCounter[letter]=0
        letterRaceCounter[race] = letterCounter

    for row in data:
        for letter in string_to_iterate:
            if letter in convToMin(row[1]):
                letterRaceCounter[row[2]][letter]+=convToMin(row[1]).count(letter)
        for i in range(len(row[1])-1):
            after[row[2]][convToMin(row[1])[i]][convToMin(row[1])[i+1]]+=1

    for race in ListeRaces:
        for letter in string_to_iterate:
            for letter2 in string_to_iterate:
                if letterRaceCounter[race][letter] != 0:
                    after[race][letter][letter2]/=float(letterRaceCounter[race][letter])
    
    return after

## donne la fréquence d'apparition d'une lettre juste après une autre
def oftenAfterForOne(string_to_iterate, data):
    firstLetter = dict([])
    for letter in string_to_iterate:
        lettersProbs = dict([])
        for letter2 in string_to_iterate:
            lettersProbs[letter2]= 0
        firstLetter[letter] = lettersProbs

    for i in range(len(data)-1):
        firstLetter[convToMin(data)[i]][convToMin(data)[i+1]]+=1
    
    return firstLetter

## donne la fréquence d'utilisation d'ensembles phoniques par race
def phonetic(ListeRaces, data):
    phonetique = {}
    for race in ListeRaces:
        phonetique[race] = {"labiale":0,
                            "sifflante":0,
                            "dentale":0,
                            "palatale":0,
                            "velaire":0,
                            "labiale":0,
                            "gutturale":0,
                            "linguale":0
                            }

    for row in data:
        s = convToMin(row[1])
        for i in range(len(s)) :
            if s[i] in "csteaoq" :
                if s[i] == "c" and i != len(s)-1:
                    if s[i+1] in "hi":
                        phonetique[row[2]]["sifflante"]+=1
                        i+=1
                    else:
                        phonetique[row[2]]["gutturale"]+=1
                if s[i] == "s" and i != len(s)-1:
                    if s[i+1] in "h":
                        phonetique[row[2]]["sifflante"]+=1
                        i+=1
                    else:
                        phonetique[row[2]]["sifflante"]+=1
                if s[i] == "t" and i != len(s)-1:
                    if s[i+1] in "h":
                        phonetique[row[2]]["sifflante"]+=1
                        i+=1
                    else:
                        phonetique[row[2]]["dentale"]+=1
                if s[i] == "e" and i != len(s)-1:
                    if s[i+1] in "u":
                        phonetique[row[2]]["palatale"]+=1
                        i+=1
                    else:
                        phonetique[row[2]]["palatale"]+=1
                if s[i] == "a" and i != len(s)-1:
                    if s[i+1] in "i":
                        phonetique[row[2]]["palatale"]+=1
                        i+=1
                    elif s[i+1] in "u":
                        phonetique[row[2]]["velaire"]+=1
                        i+=1
                if s[i] == "o" and i != len(s)-1:
                    if s[i+1] in "o":
                        phonetique[row[2]]["velaire"]+=1
                        i+=1
                    else:
                        phonetique[row[2]]["velaire"]+=1
                if s[i] == "q" and i != len(s)-1:
                    if s[i+1] in "u":
                        phonetique[row[2]]["gutturale"]+=1
                        i+=1
                    else:
                        phonetique[row[2]]["gutturale"]+=1
            else:
                if s[i] in "bmp" :
                    phonetique[row[2]]["labiale"]+=1
                elif s[i] in "z" :
                    phonetique[row[2]]["sifflante"]+=1
                elif s[i] in "d" :
                    phonetique[row[2]]["dentale"]+=1
                elif s[i] in "ëéêiîïíy" :
                    phonetique[row[2]]["palatale"]+=1
                elif s[i] in "âäáóôöuûüú" :
                    phonetique[row[2]]["velaire"]+=1
                elif s[i] in "fwv" :
                    phonetique[row[2]]["labiale"]+=1
                elif s[i] in "gkr" :
                    phonetique[row[2]]["gutturale"]+=1
                elif s[i] in "ln" :
                    phonetique[row[2]]["linguale"]+=1

        
    raceCounter = countMembers(ListeRaces, data)
    for race in ListeRaces:
        for phone in phonetique[race]:
            if raceCounter.get(race) != 0:
                phonetique.get(race)[phone]/=float(raceCounter.get(race))

    return phonetique

## donne la fréquence d'utilisation d'ensembles phoniques du nom name
def phoneticForOne(name):
    phonetique = {"labiale":0,
                    "sifflante":0,
                    "dentale":0,
                    "palatale":0,
                    "velaire":0,
                    "labiale":0,
                    "gutturale":0,
                    "linguale":0
                        }


    s = convToMin(name)
    for i in range(len(s)) :
        if s[i] in "csteaoq" :
            if s[i] == "c" and i != len(s)-1:
                if s[i+1] in "hi":
                    phonetique["sifflante"]+=1
                    i+=1
                else:
                    phonetique["gutturale"]+=1
            if s[i] == "s" and i != len(s)-1:
                if s[i+1] in "h":
                    phonetique["sifflante"]+=1
                    i+=1
                else:
                    phonetique["sifflante"]+=1
            if s[i] == "t" and i != len(s)-1:
                if s[i+1] in "h":
                    phonetique["sifflante"]+=1
                    i+=1
                else:
                    phonetique["dentale"]+=1
            if s[i] == "e" and i != len(s)-1:
                if s[i+1] in "ua":
                    phonetique["palatale"]+=1
                    i+=1
                else:
                    phonetique["palatale"]+=1
            if s[i] == "a" and i != len(s)-1:
                if s[i+1] in "i":
                    phonetique["palatale"]+=1
                    i+=1
                elif s[i+1] in "u":
                    phonetique["velaire"]+=1
                    i+=1
            if s[i] == "o" and i != len(s)-1:
                if s[i+1] in "o":
                    phonetique["velaire"]+=1
                    i+=1
                else:
                    phonetique["velaire"]+=1
            if s[i] == "q" and i != len(s)-1:
                if s[i+1] in "u":
                    phonetique["gutturale"]+=1
                    i+=1
                else:
                    phonetique["gutturale"]+=1
        else:
            if s[i] in "bmp" :
                phonetique["labiale"]+=1
            elif s[i] in "z" :
                phonetique["sifflante"]+=1
            elif s[i] in "d" :
                phonetique["dentale"]+=1
            elif s[i] in "ëéêiîïíy" :
                phonetique["palatale"]+=1
            elif s[i] in "âäáóôöuûüú" :
                phonetique["velaire"]+=1
            elif s[i] in "fwv" :
                phonetique["labiale"]+=1
            elif s[i] in "gkr" :
                phonetique["gutturale"]+=1
            elif s[i] in "ln" :
                phonetique["linguale"]+=1

    return phonetique

## compare la frequence des lettres dans le nom et pour chaque race, retourne la liste des scores obtenus par race
def compareLetterFreq(ListeRaces, string_to_iterate, name, letterData):
    scores = {}
    
    for race in ListeRaces:
        score = 0
        letters = 0
        for char in string_to_iterate:
            if name[char] != 0:
                score += abs(letterData[race][char] - name[char])
                letters += 1
        scores[race] = 1 - float(score)/letters

    return scores

## compare la frequence des lettres suivant une autre dans le nom et pour chaque race, retourne la liste des scores obtenus par race
def compareLetterSuccess(ListeRaces, name, letterData):
    scores = {}

    for race in ListeRaces:
        score = 0
        letters = 0
        for char in string_to_iterate:
            subscore = 0
            letters2 = 0
            for char2 in string_to_iterate:
                if name[char][char2] != 0:
                    subscore += abs(letterData[race][char][char2] - name[char][char2])
                    letters2 += 1
            if letters2 != 0:
                score += float(subscore)/letters2
                letters += 1
        scores[race] = 1 - float(score)/letters

    return scores

## compare la probabilite des lettres dans le nom en sachant la presence d'une autre lettre et pour chaque race, retourne la liste des scores obtenus par race
def compareLetterDistrib(ListeRaces, name, letterData):
    scores = {}

    for race in ListeRaces:
        score = 0
        letters = 0
        for char in string_to_iterate:
            subscore = 0
            letters2 = 0
            for char2 in string_to_iterate:
                if name[char][char2] != 0:
                    subscore += abs(letterData[race][char][char2] - name[char][char2])
                    letters2 += 1
            if letters2 != 0:
                score += float(subscore)/letters2
                letters += 1
        scores[race] = 1 - float(score)/letters

    return scores

## compare la frequence des lettre dans le nom et pour chaque race, retourne la liste des scores obtenus par race
def compareSyllab(ListeRaces, data, nom):
    
    NbSyllabMyst= countSyllabs(convToMin(nom))
    RaceScore={}

    for race in ListeRaces:
        RaceScore[race]= data.get(race)[NbSyllabMyst]
        if NbSyllabMyst != 1:
            RaceScore[race]+= data.get(race)[NbSyllabMyst-1]
        if NbSyllabMyst != 9:
            RaceScore[race]+= data.get(race)[NbSyllabMyst+1]

    return RaceScore

## compare la frequence des ensembles phoniques dans le nom et pour chaque race, retourne la liste des scores obtenus par race
def comparePhonetics(ListeRaces, namePhonetic, allPhonetic):
    scores = {}
    
    for race in ListeRaces:
        score = 0
        phonemes = 0
        for phoneme in allPhonetic[race]:
            score += abs(allPhonetic[race][phoneme] - namePhonetic[phoneme])
            phonemes += 1
        scores[race] = 1 - float(score)/phonemes

    return scores

## retourne le nombre d'indicidus par race dans les donnees d'entrainement
def countMembers(ListeRaces, data):
    counter = {}
    for race in ListeRaces:
        counter[race]=0
    for row in data:
        counter[row[2]]+=1
    return counter

## elimine des donnes d'entrainement les noms trop eloignes de la moyenne pour chaque race
def filterData(ListeRaces, allLetterPresent, allSyllabDistrib, allLetterDepend, allLetterSuccess, allPhonetic, threshold_on_training, dataToTrain):
    meanScores = {}
    for race in ListeRaces:
        meanScores[race] = 0

    for row in dataToTrain:
        meanScores[row[2]]+=rank(compareLetterFreq(ListeRaces, string_to_iterate, getLettersForOne(string_to_iterate, row[1]), allLetterPresent))[row[2]] * parametersRanked[row[2]][0]
        +rank(compareSyllab(ListeRaces, allSyllabDistrib, row[1]))[row[2]] * parametersRanked[row[2]][1]
        +rank(compareLetterDistrib(ListeRaces, oftenTogetherForOne(string_to_iterate, row[1]), allLetterDepend))[row[2]] * parametersRanked[row[2]][2]
        +rank(compareLetterSuccess(ListeRaces, oftenAfterForOne(string_to_iterate, row[1]), allLetterSuccess))[row[2]] * parametersRanked[row[2]][3]
        +rank(comparePhonetics(ListeRaces, phoneticForOne(row[1]), allPhonetic))[row[2]] * parametersRanked[row[2]][4]

    members = countMembers(ListeRaces, dataToTrain)
    for race in ListeRaces:
        meanScores[race]/=float(members[race])

    listToEject = []
    for row in dataToTrain:
        score=rank(compareLetterFreq(ListeRaces, string_to_iterate, getLettersForOne(string_to_iterate, row[1]), allLetterPresent))[row[2]] * parametersRanked[row[2]][0]
        +rank(compareSyllab(ListeRaces, allSyllabDistrib, row[1]))[row[2]] * parametersRanked[row[2]][1]
        +rank(compareLetterDistrib(ListeRaces, oftenTogetherForOne(string_to_iterate, row[1]), allLetterDepend))[row[2]] * parametersRanked[row[2]][2]
        +rank(compareLetterSuccess(ListeRaces, oftenAfterForOne(string_to_iterate, row[1]), allLetterSuccess))[row[2]] * parametersRanked[row[2]][3]
        +rank(comparePhonetics(ListeRaces, phoneticForOne(row[1]), allPhonetic))[row[2]] * parametersRanked[row[2]][4]

        if not meanScores[row[2]] - (threshold_on_training * meanScores[row[2]]) < score < meanScores[row[2]] + (threshold_on_training * meanScores[row[2]]):
            listToEject.append(row)

    for row in listToEject:
        dataToTrain.remove(row)
    return dataToTrain
    
## Parametres inherents au .csv, c'est la liste des races qui y figurent et la liste des symboles composants les noms ("*" signifie un numéro quelconque dans la base d'origine)
ListeRaces=["Orcs","Men","Hobbits","Elves","Dwarves","Ainur"]
string_to_iterate ="abcdefghijklmnopqrstuvwxyzöëíúáâóäéêîûô -'.*"

## Hyperparametres
training = 0.7 # taille des donnees d'entrainement
testing = 1 - training

threshold_on_training = 0.5 # seuil a partir duquel on filtre les donnes si depasse, plus il est haut, moins il filtre

nb_iterations = 1 # nombre de fois que le programme est lance, pour faire des moyennes. En cas d'utilisation pour demonstration, mettre a 1

# extraction des donnees du .csv
data = []
with open('lotr.csv', newline='', encoding="utf8") as csvfile:
    content = csv.reader(csvfile, delimiter=';', quotechar='|')
    for row in content:
        data += [row]

## en commentaires, le code qui nous a permi d'estimer les hyperparametres de parametresRanked

##scores = {}
##for race in ListeRaces:
##    scores[race] = {"presence":0,
##                    "syllabe":0,
##                    "distribution":0,
##                    "succession":0,
##                    "phonetique":0}
##
##for row in dataToTrain:
##    scores[row[2]]["presence"]+=rank(compareLetterFreq(ListeRaces, string_to_iterate, getLettersForOne(string_to_iterate, row[1]), allLetterPresent))[row[2]]
##    scores[row[2]]["syllabe"]+=rank(compareSyllab(ListeRaces, allSyllabDistrib, row[1]))[row[2]]
##    scores[row[2]]["distribution"]+=rank(compareLetterDistrib(ListeRaces, oftenTogetherForOne(string_to_iterate, row[1]), allLetterDepend))[row[2]]
##    scores[row[2]]["succession"]+=rank(compareLetterSuccess(ListeRaces, oftenAfterForOne(string_to_iterate, row[1]), allLetterSuccess))[row[2]]
##    scores[row[2]]["phonetique"]+=rank(comparePhonetics(ListeRaces, phoneticForOne(row[1]), allPhonetic))[row[2]]
##
##members = countMembers(ListeRaces, dataToTrain)
##for race in ListeRaces:
##    scores[race]["presence"]/=float(members[race])
##    scores[race]["syllabe"]/=float(members[race])
##    scores[race]["distribution"]/=float(members[race])
##    scores[race]["succession"]/=float(members[race])
##    scores[race]["phonetique"]/=float(members[race])
##
##for race in ListeRaces:
##    print(race+" : ")
##    for key in scores[race]:
##        print(key + " = " + str(float(int(scores[race][key]*100))/100))
##    print("")

parametersRanked = {"Orcs":[2,4,4,5,5],
                "Men":[5,0,5,10,0],
                "Hobbits":[3,4,4,7,2],
                "Elves":[4,1,6,6,3],
                "Dwarves":[4,2,1,7,6],
                "Ainur":[2,5,4,5,4]
                }

## initialisation des listes reel / predit
realList = []
predictedList = []

accuracyScores = []

for iterate in range(nb_iterations):

    # listes utilisees pour effectuer des calculs sur les resultats
    realListForOneIteration = []
    predictedListForOneIteration = []
        
    # on melange les donnees car la table est triee par defaut, et permet de lancer plusieurs fois le code sans avoir les memes resultats
    random.shuffle(data)
    dataToTrain = data[0:int(training*len(data))]
    dataToTest = data[int(training*len(data)):len(data)]

    # on calcule les donnees par race utiles depuis les donnees d'entrainement
    allLetterPresent = getLettersData(ListeRaces, string_to_iterate, dataToTrain)
    allLetterDepend = oftenTogether(ListeRaces, string_to_iterate, dataToTrain)
    allLetterSuccess = oftenAfter(ListeRaces, string_to_iterate, dataToTrain)
    allSyllabDistrib = getDistribSyllab(ListeRaces, dataToTrain)
    allPhonetic = phonetic(ListeRaces, dataToTrain)


    # on filtre les donnees pour eliminer le bruit, attention a la pertinence du seuil (bon seuil = 0.5 ou plus)
    dataToTrain = filterData(ListeRaces, allLetterPresent, allSyllabDistrib, allLetterDepend, allLetterSuccess, allPhonetic, threshold_on_training, dataToTrain)

    # trouve la race qui correspond le mieux d'apres les donnees calculees
    for i in range(len(dataToTest)):
        race,scoring = score(ListeRaces, string_to_iterate, allLetterPresent, allLetterDepend, allLetterSuccess, allSyllabDistrib, allPhonetic, parametersRanked, dataToTest[i][1])
        predictedList.append(race)
        predictedListForOneIteration.append(race)
        realListForOneIteration.append(dataToTest[i][2])
        realList.append(dataToTest[i][2])

    print(str(int(float(iterate+1)/nb_iterations*100))+"%")

    accuracyScores.append(int(accuracy_score(realList, predictedList)*10000)/100)


    ## code en commentaires : pour savoir sur quels noms la machine s'est trompee ou a vu juste
    
    ##file = open("C:\\Users\\maxlm\\Desktop\\lotr.txt","w")
    ##
    ##for i in range(len(dataToTest)):
    ##    file.write(dataToTest[i][1]+" ; "+realList[i] + " : " + predictedList[i] + "\n")
    ##
    ##file.close()

## affichage des resultats
print("predicted ->")
print("for |")
print("    ^")
print("Confusion matrix : ")
print(confusion_matrix(realList, predictedList,labels=ListeRaces))

print("Accuracy score : " )
print(str(int(accuracy_score(realList, predictedList)*10000)/100) + "%\n")

print("")
print("Best Score : "+str(max(accuracyScores)))
print("Worst Score : "+str(min(accuracyScores)))
print("Variance : "+str(statistics.variance(accuracyScores)))
print("")
print("Accuracy by race : ")
for race in ListeRaces:
    qtt = 0
    trouve = 0
    for i in range(len(dataToTest)*nb_iterations):
        if realList[i] == race:
            qtt +=1
            if predictedList[i] == race:
                trouve +=1
    if qtt != 0:
        print(race +": " + str(int(float(trouve)/qtt*100))+"%")
