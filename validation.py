#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pickle
import os
import numpy as np
from sklearn.model_selection import RepeatedKFold
from pracmln import MLN
from pracmln import Database
from pracmln import MLNQuery
from pracmln import MLNLearn
from sklearn.model_selection import KFold
from sklearn import svm
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
from scikitplot.metrics import plot_confusion_matrix

###########################################################
## MLN learning and querieing
###########################################################
mln = MLN(grammar = 'PRACGrammar', logic = 'FirstOrderLogic')
##predicates
mln << 'shape(cluster, shape)'
mln << 'color(cluster, color)'
mln << 'size(cluster, size)'
mln << 'goggles_Text(cluster, text)'
mln << 'goggles_Logo(cluster, company)'
mln << 'goggles_Product(cluster, product)'
mln << 'scene(scene)'
mln << 'instance(cluster, instance)'
mln << 'object(cluster, object!)'
##formulas
mln << '0 shape(?c, +?sha) ^ color(?c, +?col) ^ size(?c, +?size) ^ instance(?c, +?inst) ^ object(?c, +?obj)'
mln << '0 goggles_Logo(?c, +?comp) ^ object(?c, +?obj)'
mln << '0 goggles_Text(?c, +?text) ^ object(?c, +?obj)'
mln << '0 goggles_Product(?c, +?prod) ^ object(?c, +?obj)'
mln << '0 scene(+?s) ^ object(?c, +?obj)'
##unique clusters
mln << '0 scene(+?s) ^ object(?c1, +?t1) ^ object(?c2, +?t2) ^ ?c1 =/= ?c2'

dbFileName = '/home/dominik/python_ws/testDB.txt'

#allDB = Database.load(mln, '/home/dominik/python_ws/testDB.txt')

allDB = Database.load(mln, dbFileName)

predictionList = []
predIdx = 0
groundTruthList = []
gtIdx = 0
i = 0
splits = 10
testArray = np.array(allDB, dtype=Database)
kf = KFold(n_splits=splits, shuffle=True)
for train, test in kf.split(testArray):
    print("%s %s" % (train, test))        
     

    predList = []
    pIdx = 0
    gtList = []  
    gtIdx = 0    

    ## create Directory
    dirName = 'run' + str(i)
    os.mkdir(dirName)

    ## read the input db
    delimiter = '---'    
    trainFileName = dirName + '/trainDB.txt'
    testFileName = dirName + '/testDB.txt'
    fs = open(dbFileName, 'r')
    dbs = fs.read().split(delimiter)    
    
    ## create train und test DB files based on the kfold splits
    ft = open(trainFileName, 'w')
    for x in train:
      ft.write(dbs[x])  
      ft.write(delimiter)
    ft.close()

    ft = open(testFileName, 'w')
    for x in test:   
      entry = []
      lines = dbs[x].split('\n')
      for l in lines:
        if l.find('object') != -1:          
          entry.append(l.strip())          

          ## if object line should occur in testfile
          #ft.write(l)
          #ft.write('\n')
        else:
          ft.write(l)
          ft.write('\n')
      ft.write(delimiter)
      gtList.append(entry)         
      gtIdx += 1
    ft.close()

    fs.close()
    
    ###################################
    ## learning of mln
    #################################
    trainDB = Database.load(mln, trainFileName)
    learndFileName = dirName + '/learnedMLN.mln'
    learndMLN = MLNLearn(mln=mln, db=trainDB, multicore=True, verbose=True, use_prior=True, prior_mean=0, prior_stdev=10, save=True, optimizer='').run()

    fs = open(learndFileName, 'w')
    learndMLN.write(stream=fs)
    fs.close()    

    ######################################
    ## testing of mln
    ######################################
    testDB = Database.load(learndMLN, testFileName)
     
    dbpredList = []
    dbgtList = []
    for db in testDB:
        result = MLNQuery(mln=learndMLN, db=db, method='WCSPInference', multicore=True, queries='object', verbose=True).run()

        ## find best result
        thisDBObjList = gtList[pIdx] 
        for entry in thisDBObjList:
          predObj = entry
          objVal = result.results[entry]
          for k, v in result.results.iteritems():          
            if k.find(entry.split(',')[0])  != -1:          
              if v > objVal:
                predObj = k
          predictionList.append(predObj)
          dbpredList.append(predObj)
          groundTruthList.append(entry)
          dbgtList.append(entry)
        pIdx += 1
        ## -----------------
    predFileName = dirName + '/result.p' 
    pickle.dump(dbpredList, open(predFileName, 'w'))
    gtFileName = dirName + '/result.p' 
    pickle.dump(dbgtList, open(gtFileName, 'w'))
    i += 1

#############################################################
## change list to only contain the objectnames
#############################################################
## create results Directory
dirName = 'results'
os.mkdir(dirName)

print groundTruthList
gtListFile = dirName + '/groundTruthListRaw.p'
pickle.dump(groundTruthList, open(gtListFile, 'w'))
print predictionList
predListFile = dirName + '/predictionListRaw.p'
pickle.dump(predictionList, open(predListFile, 'w'))

for x, entry in enumerate(groundTruthList):
  groundTruthList[x] = entry.split(',')[1].split(')')[0]

for x, entry in enumerate(predictionList):
  predictionList[x] = entry.split(',')[1].split(')')[0]

print groundTruthList
gtListFile = dirName + '/groundTruthList.p'
pickle.dump(groundTruthList, open(gtListFile, 'w'))
print predictionList
predListFile = dirName + '/predictionList.p'
pickle.dump(predictionList, open(predListFile, 'w'))

##########################################################
## metrics
##########################################################
fileName = dirName + '/metrics.txt'

fs = open(fileName, 'w')

print 'accuracy: ' + str(accuracy_score(groundTruthList, predictionList))
fs.write('accuracy: ' + str(accuracy_score(groundTruthList, predictionList)) + '\n')

print 'precision(macro): ' + str(precision_score(groundTruthList, predictionList, average='macro'))
print 'precision(micro): ' + str(precision_score(groundTruthList, predictionList, average='micro'))
fs.write('precision(macro): ' + str(precision_score(groundTruthList, predictionList, average='macro')) + '\n')
fs.write('precision(micro): ' + str(precision_score(groundTruthList, predictionList, average='micro')) + '\n')

print 'recall(macro): ' + str(recall_score(groundTruthList, predictionList, average='macro'))
print 'recall(micro): ' + str(recall_score(groundTruthList, predictionList, average='micro'))
fs.write('recall(macro): ' + str(recall_score(groundTruthList, predictionList, average='macro')) + '\n')
fs.write('recall(micro): ' + str(recall_score(groundTruthList, predictionList, average='micro')) + '\n')

print 'f1(macro): ' + str(f1_score(groundTruthList, predictionList, average='macro'))
print 'f1(micro): ' + str(f1_score(groundTruthList, predictionList, average='micro'))
fs.write('f1(macro): ' + str(f1_score(groundTruthList, predictionList, average='macro')) + '\n')
fs.write('f1(micro): ' + str(f1_score(groundTruthList, predictionList, average='micro')) + '\n')


print confusion_matrix(groundTruthList, predictionList)

plot_confusion_matrix(groundTruthList, predictionList)
matrixFileName = dirName + '/confusionMatrix.png'
plt.savefig(matrixFileName)
#plt.show()
fs.close()
