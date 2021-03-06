'''
实现对训练好的模型每个不同角度进行准确率比较。
'''
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.autograd import Variable
import numpy
import torch.utils.data as Data
import torch
import sys
import os
from ProcessProgram.NeurNetWorkProcess.ProceRawDataToTensor import *

Work_Path = "F:\\PlantarPressurePredictExperiment"
os.chdir(Work_Path)

#region ModelImport
#LSTM
# from ProcessProgram.Pytorch.LSTM import LSTM
# from ProcessProgram.Pytorch.LSTM import sequenceLen
# from ProcessProgram.Pytorch.LSTM import getmodel,BATCH_SIZE

# CNN
from ProcessProgram.Pytorch.CNN import CNN
from ProcessProgram.Pytorch.CNN import getmodel,BATCH_SIZE

#endregion

global x_test,y_test,test_loader

#region 文件导入
def importData():
    SaveTestDataFilePath = "Pytorch\\data\\angle\\TestData.csv"
    SaveTestLabelFilePath = "Pytorch\\data\\angle\\TestLabel.csv"
    global x_test,y_test
    with open(SaveTestDataFilePath, encoding='utf-8') as path_x_test_m, \
        open(SaveTestLabelFilePath, encoding='utf-8')as path_y_test_m:

        x_test = np.loadtxt(path_x_test_m, dtype=float,delimiter=",")
        y_test = np.loadtxt(path_y_test_m,dtype = int, delimiter=",")
#endregion

#region  数据转换
def TrainFormData():
    global x_test,y_test,test_loader
    #LSTM RESHAPE
    # x_test = x_test.reshape(len(x_test),sequenceLen,1260)
    #CNN RESHAPE
    x_test = x_test.reshape(len(x_test),1,60,21)

    x_test = torch.from_numpy(x_test)
    y_test = torch.from_numpy(y_test)

    x_test =  torch.tensor(x_test,dtype= torch.float32)
    y_test = torch.tensor(y_test,dtype=torch.long)

    test_dataset = Data.TensorDataset(x_test,y_test)
    test_loader = Data.dataloader.DataLoader(dataset= test_dataset,batch_size = BATCH_SIZE ,shuffle= True)
#endregion


def TestNetWork(model):
    correct = 0
    correctCount = [0,0,0,0,0]      #0，30，60，90  正确数量
    TotalCount = [0,0,0,0,0]        #总数
    ErrRect = np.zeros((5,5))
    for step, (data, target) in enumerate(test_loader):
        data, target = Variable(data),Variable(target)
        output = model(data)
        # sum up batch loss
        # get the index of the max log-probability
        pred = torch.max(output.data, 1)[1]
        correct += int(pred.eq(target.data.view_as(pred)).cpu().sum())

        for ansIndex in range(len(pred)):
            angleIndex = target[ansIndex]     #真值
            predictIndex = pred[ansIndex]     #预测值
            if(predictIndex == angleIndex):
                correctCount[angleIndex] += 1
                TotalCount[angleIndex] += 1
            else:
                TotalCount[angleIndex] += 1
                ErrRect[angleIndex][pred[ansIndex]] +=1


    correctRate = 100. * correct / len(test_loader.dataset)
    print('Accuracy: {}/{} ({:.0f}%)\n'.format(correct, len(test_loader.dataset),correctRate))
    print("Count：0°:{}/{} 30°:{}/{}  60°:{}/{}  90°:{}/{}".format(correctCount[0],TotalCount[0],
                                                                  correctCount[1],TotalCount[1],
                                                                  correctCount[2],TotalCount[2],
                                                                  correctCount[3],TotalCount[3],))
    print("angelAccuracy：0°:{:.2f}%  30°:{:.2f}%  60°:{:.2f}%  90°:{:.2f}%".format(100. * correctCount[0]/TotalCount[0],
                                                                                   100. * correctCount[1]/TotalCount[1],
                                                                                   100. * correctCount[2]/TotalCount[2],
                                                                                   100. * correctCount[3]/TotalCount[3]))
    print("错误矩阵:-------------\n",ErrRect)



    return ("{:.0f}%".format(100. * correct / len(test_loader.dataset)))


if __name__ == '__main__':
    importData()
    TrainFormData()
    lstm = getmodel("cnn3_31_0_correct88%.pkl")        #放入模型
    TestNetWork(lstm)

    pass