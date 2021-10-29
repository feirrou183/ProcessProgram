import os
import json
import csv
import numpy as np
import random


Work_Path = "F:\\PlantarPressurePredictExperiment"
os.chdir(Work_Path)



def getDic():
    with open("subjectConfig.json", "r",encoding= "utf-8") as f:
        subjectConfigDict = json.load(f)
    return subjectConfigDict





def GetKeyPoint(dic,subject,item,step):
    HC = dic[subject]["ResultData"][item][step].split(",")[0]
    SC = dic[subject]["ResultData"][item]["{0}SCValue".format(step)].split("_")[0]
    HL = dic[subject]["ResultData"][item]["{0}HLValue".format(step)].split("_")[0]
    TO = dic[subject]["ResultData"][item][step].split(",")[1]
    return int(HC),int(SC),int(HL),int(TO)


def GetArr(subject,detailItemName,eachStep,HC,SC,HL,TO):
    file = "1"
    if(eachStep == "BTS" or eachStep == "TS"):
        file = open("ProcessedData\\subject{0}\\{1}-L.csv".format(subject,detailItemName),encoding="utf-8")
    elif(eachStep == "BAP" or eachStep == "AP" or eachStep == "DS"):
        file = open("ProcessedData\\subject{0}\\{1}-R.csv".format(subject,detailItemName),encoding="utf-8")
    else:
        print("Error",subject,detailItemName)

    Arr = np.loadtxt(file,delimiter = ",")
    HCArr = Arr[HC-1:SC-1,:]
    MSArr = Arr[SC:HL-1,:]
    TOArr = Arr[HL:TO-1,:]
    file.close()
    return HCArr,MSArr,TOArr


def GetLabel(dic,subjectName,detailItemName):
    angle = dic[subjectName]["ResultData"][detailItemName]["angle"]
    strategy = dic[subjectName]["ResultData"][detailItemName]["strategy"]
    return angle,strategy

def DoBatchNormFun(Arr):
    '''
    对数据进行归一化
    :param Arr:
    :return:
    '''
    mean = Arr.mean()
    std = Arr.std()
    arr = (Arr - mean) / std  # 标准化数据
    return arr


def GetFileIterator(dic):
    randomList = [1,2,3,4,5]
    isTest = False
    DoBatchNorm = True #是否进行归一化
    for subject in subjects:
        for item in items:
            for sub_item in sub_items:
                isTest = True if(random.choice(randomList) == 1) else False           #独立样本
                detailItemName = "{0}-{1}".format(item, sub_item)
                subjectName = "subject{}".format(subject)
                if (dic[subjectName]["ResultData"].__contains__(detailItemName)):
                    for eachStep in Step:#每一个特征步
                        HC, SC, HL, TO = GetKeyPoint(dic, subjectName, detailItemName, eachStep)
                        HCArr, MSArr, TOArr = GetArr(subject, detailItemName, eachStep, HC, SC, HL, TO)
                        angle,strategy =  GetLabel(dic,subjectName,detailItemName)
                        if(angle == "120°") : continue      #不要30°和120°变化

                        #region 归一化
                        #是否进行归一化
                        if(DoBatchNorm):
                            #HCArr
                            #MSArr
                            #ToeArr
                            for ArrIndex in range(len(TOArr)):
                                TOArr[ArrIndex] = DoBatchNormFun(TOArr[ArrIndex])

                        #endregion
                        for k in range(len(TOArr)-(SeleSequence-1)):   #每帧取一个图像,取SeleSequence帧
                            #yield subjectName,detailItemName,angle,strategy,eachStep,HCArr,MSArr,TOArr
                            # isTest = True if (random.choice(randomList) == 1) else False   #常规样本
                            returnList = np.append(np.append(TOArr[k],TOArr[k+1]),np.append(TOArr[k+2],TOArr[k+3]))
                            returnList = np.append(returnList,np.append(TOArr[k+4],TOArr[k+5]))
                            #returnList = np.append(returnList,np.append(TOArr[k+6],TOArr[k+7]))
                            #returnList = np.append(returnList, np.append(TOArr[k + 8], TOArr[k + 9]))
                            yield subjectName, detailItemName, angle, strategy, eachStep,returnList,isTest
                        print(subjectName,"---",detailItemName)




def switchLabelClass(label):
    if label == 0:
        return 0
    if label ==30:
        return 1
    if label ==60:
        return 2
    if label == 90:
        return 3
    if label == 120:
        return 4



if __name__ == '__main__':
    subjects = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    items = ["1", "2", "3", "4", "5"]
    sub_items = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]
    #Step = ["BAP", "BTS", "AP", "TS", "DS"]
    Step = ["AP"]

    SaveTrainDataFilePath = "Pytorch\\data\\angle\\TrainData.csv"
    SaveTrainLabelFilePath = "Pytorch\\data\\angle\\TrainLabel.csv"
    SaveTestDataFilePath = "Pytorch\\data\\angle\\TestData.csv"
    SaveTestLabelFilePath = "Pytorch\\data\\angle\\TestLabel.csv"

    SeleSequence = 6  #每两帧取一个图像

    dic = getDic()
    TrainArr = []
    TrainAngle = []
    TestArr = []
    TestAngle = []

    for eachItem in GetFileIterator(dic):
        Arr = eachItem[5]
        label = int(eachItem[2].split("°")[0])
        label = switchLabelClass(label)

        if(eachItem[6]):
            TestArr.append(Arr)
            TestAngle.append(label)
        else:
            TrainArr.append(Arr)
            TrainAngle.append(label)

    TrainArr = np.array(TrainArr)
    TrainAngle = np.array(TrainAngle)
    TestArr = np.array(TestArr)
    TestAngle = np.array(TestAngle)

    np.savetxt(SaveTrainDataFilePath,TrainArr,delimiter=",")
    np.savetxt(SaveTrainLabelFilePath, TrainAngle,fmt="%d", delimiter=",")

    np.savetxt(SaveTestDataFilePath, TestArr, delimiter=",")
    np.savetxt(SaveTestLabelFilePath, TestAngle,fmt="%d", delimiter=",")















