import subprocess
import os
import time
import pandas
import numpy
#import py4j

poi = ""
user = "dehnertjj27"
server = "washington.uww.edu"
password1 = "jardeh3070"
password2 = "jd4546"
database = "pokedextcg"
pathway = r"C:\Program Files\PuTTY\putty.exe"
command = "mysql -u dehnertjj27 -p pokedextcg"

cmd = f'plink -batch -ssh {user}@{server} -pw {password1}'
getIN = "use " + database
bruh = " INTO OUTFILE 'C:/Users/cdyl2/OneDrive/Documents/GitHub/PokedexTCG1999to2023/TextStuff.txt'"
func = "SELECT * FROM pokemon;"

#searchByAll = "WHERE id LIKE '" + s + "' or setId LIKE '" + s + "' or series "

#CSV TIMMMMMEEEEE

#Set_num, level, hp, convertedRetreatCost are ints
def fuckITWEBALL():
    np = subprocess.Popen(cmd, shell=True, stdin =subprocess.PIPE, pipesize=1000000000000, stdout= subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2)
    np.stdin.write('mysql -u dehnertjj27 -p pokedextcg\n'.encode())
    np.stdin.flush()
    time.sleep(0.5)
    np.stdin.write('jd4546\n'.encode())
    np.stdin.flush()
    time.sleep(0.5)
    np.stdin.write(f'{func}\n'.encode())
    np.stdin.flush()
    np.stdin.write('exit\n'.encode())
    np.stdin.write('exit\n'.encode())
    stdout, stderr = np.communicate(timeout = 60)
    bruh = stdout.decode("utf8")
    poi = stdout.decode("utf8")
    
    np.stdin.close()
    np.stderr.close()
    np.stdout.close()
    cutOut(poi)

def cutOut(poi):
    if(poi.find("+") != -1 or poi.find("rows in set") != -1):
        firstCut = poi.index("+")
        lastCut = poi.index("rows in set")
        theList = poi[firstCut + 1: lastCut - 6]
        betterList = theList.replace("  ", "")
        evenNo = betterList.replace("   ", "")
        evenevenNo = evenNo.replace("  ", "")
        
        #print(theList)

        dataLines = evenevenNo.strip().split('\n')
        allTheData = []

        for line in dataLines[3:]:
            if line:
                values = line.strip().split('|')
                allTheData.append(values)
                
        index = []
        index.append("Null")
        index.append("id")
        index.append("set")
        index.append("series")
        index.append("publisher")
        index.append("generation")
        index.append("release_date")
        index.append("artist")
        index.append("name")
        index.append("set_num")
        index.append("types")
        index.append("supertype")
        index.append("subtypes")
        index.append("level")
        index.append("hp")
        index.append("evolvesFrom")
        index.append("evolvesTo")
        index.append("abilities")
        index.append("attacks")
        index.append("weaknesses")
        index.append("retreatCost")
        index.append("convertedRetreatCost")
        index.append("rarity")
        index.append("flavorText")
        index.append("nationalPokedexNumbers")
        index.append("legalities")
        index.append("resistances")
        index.append("rules")
        index.append("regulationMark")
        index.append("ancientTrait")
        index.append("weird")
        if allTheData:
            df = pandas.DataFrame(columns= index, data =allTheData)
            excel_name = "pain.csv"
            df.to_csv(excel_name, index = False)
            print("Gone through")
        else:
            print("It didn't work")

    else:
        print("Invaild")

fuckITWEBALL()
