import json
import os
import shutil
import sys

pathTubs = sys.argv[1] + '/'

tubsList=os.listdir(pathTubs)

for tub in tubsList:
    print(f"Processing {tub}")
    atub=os.listdir(f"{pathTubs}{tub}")
    currentPath=f"{pathTubs}{tub}/"
    catalogs=[files for files in atub if files.endswith(".catalog")]
    if(len(catalogs)<1):
        continue

    

    for cat in catalogs:
        f = open(f'{currentPath}{cat}')
        f=f.readlines()
        new_catalog=[]


        leftTrehs=-0.5
        rightTrehs=0.5
        i=0
        frameCounterLeft=0
        frameCounterRight=0
        isTurning=True

        howManyFrames=2
        for line in f:
            try:
                data=json.loads(line)
            except:
                continue
            # if(data["user/angle"]>=rightTrehs):
            #     data["label"]= "Right"
            #     data["state"]= 2
            #     data["one_hot_state_array"]= [0.0, 0.0, 1.0]
            # elif(data["user/angle"]<=leftTrehs):
            #     data["label"]= "Left"
            #     data["state"]= 0
            #     data["one_hot_state_array"]= [1.0, 0.0, 0.0]
            # else:
            data["behavior/label"]= "Straight"
            data["behavior/state"]= 1
            data["behavior/one_hot_state_array"]= [0.0, 1.0, 0.0]
            if(data["user/angle"]==0):
                isTurning=False
                frameCounterLeft=0
                frameCounterRight=0
            if(data["user/angle"]>=rightTrehs):
                frameCounterRight+=1
            if(data["user/angle"]<=leftTrehs):
                frameCounterLeft+=1
            if(frameCounterRight>=howManyFrames and not isTurning):
                isTurning=True
                frame2=new_catalog[i-1]
                
                data["behavior/label"]= "Right"
                data["behavior/state"]= 2
                data["behavior/one_hot_state_array"]= [0.0, 0.0, 1.0]

                for j in range(1,howManyFrames):
                    frame=new_catalog[i-j]
                    frame["behavior/label"]= "Right"
                    frame["behavior/state"]= 2
                    frame["behavior/one_hot_state_array"]= [0.0, 0.0, 1.0]


                frameCounterRight=0
            elif(frameCounterLeft>=howManyFrames and not isTurning):
                isTurning=True

                data["behavior/label"]= "Left"
                data["behavior/state"]= 0
                data["behavior/one_hot_state_array"]= [1.0, 0.0, 0.0]

                for j in range(1,howManyFrames):
                    frame=new_catalog[i-j]

                    frame["behavior/label"]= "Left"
                    frame["behavior/state"]= 0
                    frame["behavior/one_hot_state_array"]= [1.0, 0.0, 0.0]
                frameCounterLeft=0

            new_catalog.append(data)

        with open(f"{currentPath}/{cat}","w") as newCatalog:
            for line in new_catalog:
                newCatalog.write(json.dumps(line)+"\n")
