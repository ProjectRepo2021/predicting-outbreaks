
from math import sqrt
from numpy import split
from numpy import array
from pandas import read_csv
from sklearn.metrics import mean_squared_error
from matplotlib import pyplot
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Conv1D
from tensorflow.keras.layers import MaxPooling1D
from tensorflow.keras.layers import Dense, Dropout, Activation, Conv1D, MaxPooling1D, Embedding, GlobalAveragePooling1D,AveragePooling1D
import tensorflow.keras.optimizers
from numpy import concatenate
from matplotlib import pyplot
from pandas import DataFrame
from pandas import concat
from sklearn.preprocessing import MinMaxScaler
import random
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
import numpy as np


#Initilaize population
def init_poplulation(numberOfParents):
    
    #initialize array for parameters
    filter_size1 = np.empty([numberOfParents, 1])
    layer2 = np.empty([numberOfParents, 1])
    filter_size2 = np.empty([numberOfParents, 1])
    layer3 = np.empty([numberOfParents, 1])
    filter_size3 = np.empty([numberOfParents, 1])
    OptionalDense = np.empty([numberOfParents, 1])
    Dense_size = np.empty([numberOfParents, 1])
    epochs = np.empty([numberOfParents, 1])
    batchsize = np.empty([numberOfParents, 1])
    
    
    
    #range of values for parameters
    filterList = [6,12,16,18,24,28,32,64]
    OptionalLayerList=[0,1]
    OptionalDenseList=[1,0]
    Dense_sizeList=[10,16,32,50,64, 100,128]
    epochsList=[40,50,60,70,100,120,150]
    batchsizeList=[4,16,18,32,64]
    
    for i in range(numberOfParents):

        filter_size1[i] = random.choice(filterList)
        layer2[i] = random.choice(OptionalLayerList)
        filter_size2[i]= random.choice(filterList)
        layer3[i] = random.choice(OptionalLayerList) 
        filter_size3[i]= random.choice(filterList)
        OptionalDense[i] = random.choice(OptionalLayerList)
        Dense_size[i] = random.choice(Dense_sizeList)
        epochs[i] = random.choice(epochsList)
        batchsize[i] = random.choice(batchsizeList)
    
        
    population = np.concatenate((filter_size1,layer2,filter_size2,layer3,filter_size3,OptionalDense,Dense_size,epochs,batchsize), axis= 1)
    #print (population)
    population = population.astype(int)
    return population


def CalculateFitness(population, train_X, train_y,test_X, test_y, n_hours, n_features):
    
    
    #Scale Xinputes and outputs
    x_scaler = MinMaxScaler()
    train_X = x_scaler.fit_transform(train_X)
    test_X = x_scaler.transform(test_X)

    #reshape output
    test_y = test_y.reshape((len(test_y), 1))
    train_y = train_y.reshape((len(train_y), 1))
    n_outputs =train_y.shape[1]

    #Scale Yinputes and outputs
    y_scaler = MinMaxScaler()
    train_y = y_scaler.fit_transform(train_y)
    test_y = y_scaler.transform(test_y)

    # reshape input to be 3D [samples, timesteps, features]
    train_X = train_X.reshape((train_X.shape[0], n_hours, n_features))
    test_X = test_X.reshape((test_X.shape[0], n_hours, n_features))
    
    inputShape= (train_X.shape[1], train_X.shape[2])
    
    Score=[]
    
    params_dict={}
    
    for i in range(population.shape[0]):
        
    
        params_dict['filter_size1'] = population[i][0]
        params_dict['layer2'] = population[i][1]
        params_dict['filter_size2']= population[i][2]
        params_dict['layer3'] = population[i][3]
        params_dict['filter_size3']= population[i][4]
        params_dict['OptionalDense'] = population[i][5]
        params_dict['Dense_size'] = population[i][6]
        params_dict['epochs'] = population[i][7]
        params_dict['batchsize'] = population[i][8]
        
        #----------reproducibility------------------
        tf.compat.v1.get_default_graph()
        tf.random.set_seed(2)
        random.seed(2)
        np.random.seed(2)
        
        #Create the model
        model = Sequential()
        #----------First Conv Layer-------------------
        #kernelSize=params_dict['kernel_size1']
        #print(kernelSize)
        #model.add(Conv1D(filters=params_dict['filter_size1'], kernel_size=(kernelSize), activation='relu', input_shape=(inputShape)))
        model.add(Conv1D(filters=params_dict['filter_size1'], kernel_size=1, activation='relu', input_shape=(inputShape)))
        model.add(MaxPooling1D(pool_size=1)) #first pool
              
        #----------Second Conv Layer------------------- 
        layer2=params_dict['layer2']
        if layer2>0:
    
            model.add(Conv1D(filters=params_dict['filter_size2'], kernel_size=1, activation='relu'))
            model.add(MaxPooling1D(pool_size=1)) #2nd pool
              
       #----------Third Conv Layer----------------------
        layer3=params_dict['layer3']
        if layer3>0:
    
            model.add(Conv1D(filters=params_dict['filter_size3'], kernel_size=1, activation='relu'))
            model.add(MaxPooling1D(pool_size=1)) #3rd pool
       
        model.add(Flatten())

        #----------Optional Dense layer------------------
        OptionalDense=params_dict['OptionalDense']
        if OptionalDense>0:
              
            model.add(Dense(params_dict['Dense_size'], activation='relu'))
    
        model.add(Dense(1))
              
        model.compile(loss='mse', optimizer='adam')
    
        # fit network
        history = model.fit(train_X, train_y, epochs=params_dict['epochs'], batch_size=params_dict['batchsize'], validation_data=(test_X, test_y), verbose=0, shuffle=False)

        # make a prediction
        yhat = model.predict(test_X)

        #inverse the scales
        yhat = y_scaler.inverse_transform(yhat)
        inv_y = y_scaler.inverse_transform(test_y)

        # calculate RMSE
        rmse = sqrt(mean_squared_error(inv_y, yhat))
        #print('Test RMSE: %.3f' % rmse)
        Score.append(rmse)
              
    return Score

#select n number of parents for mating
def new_parents_selection(population, fitness, numParents):
    #fitness=fitnessvalue array
    #population=population array
    bestparentsIndex=np.argpartition(fitness,numParents)[:numParents]
    bestparents=population[bestparentsIndex]
    return bestparents


# Perform uniform crossover on parents to create n children
def crossover_uniform(parents, numberOfParameters, NumChild):
    
    random.seed()
    np.random.seed()
    
    childrenSize=(NumChild,numberOfParameters)
    crossoverPointIndex = np.arange(0, np.uint8(childrenSize[1]), 1, dtype= np.uint8) #get all the index
    crossoverPointIndex1 = np.random.randint(0, np.uint8(childrenSize[1]), np.uint8(childrenSize[1]/2)) # select half  of the indexes randomly
    crossoverPointIndex2 = np.array(list(set(crossoverPointIndex) - set(crossoverPointIndex1))) #select leftover indexes
    
    children = np.empty(childrenSize)
    
    '''
    Create child by choosing parameters from two paraents selected using new_parent_selection function. The parameter values
    will be picked from the indexes, which were randomly selected above. 
    '''
    for i in range(children.shape[0]):
        
        #find parent 1 index 
        parent1_index = i%parents.shape[0]
        #find parent 2 index
        parent2_index = (i+1)%parents.shape[0]
        #insert parameters based on random selected indexes in parent 1
        children[i, crossoverPointIndex1] = parents[parent1_index, crossoverPointIndex1]
        #insert parameters based on random selected indexes in parent 1
        children[i, crossoverPointIndex2] = parents[parent2_index, crossoverPointIndex2]
        
        children=children.astype(int)
        
    return children


def Single_mutation(crossover, numberOfParameters):
    
    random.seed()
    np.random.seed()
    #choose a parameter to be mutated
    parameterSelect = np.random.randint(0, numberOfParameters, 1)
    
    #define the possible values for each parameter
    filterList = [6,12,16,18,24,28,32,64]
    OptionalLayerList=[0,1]
    OptionalDenseList=[1,0]
    Dense_sizeList=[10,16,32,50,64,100,128]
    epochsList=[40,50,60,70,100,120,150]
    batchsizeList=[4,16,18,32,64]
    
    #randomly select a value for each parameter
    
    P1 = random.choice(filterList)
    P2 = random.choice(OptionalLayerList)
    P3 = random.choice(filterList)
    P4 = random.choice(OptionalLayerList) 
    P5 = random.choice(filterList)
    P6 = random.choice(OptionalLayerList)
    P7 = random.choice(Dense_sizeList)
    P8 = random.choice(epochsList)
    P9 = random.choice(batchsizeList)
    
    print("_________Here are the new PSSSSSS_____________", parameterSelect)
    print(P1,P2,P3,P4,P5,P6,P7,P8,P9)
    
    if parameterSelect == 0: #filter1size
        crossover[0][0] = P1 #Parameter1
        
    if parameterSelect == 1: # layer 2
        crossover[0][1] = P2 #Parameter2
        
    if parameterSelect == 2: #filter2size
        crossover[0][2] = P3 #Parameter3
        
    if parameterSelect == 3: #layer3
        crossover[0][3] = P4 #Parameter4
        
    if parameterSelect == 4: #filter3size
        crossover[0][4] = P5 #Parameter5
        
    if parameterSelect == 5: #Denselayer
        crossover[0][5] = P6 #Parameter6
     
    if parameterSelect == 6: #Densesize
        crossover[0][6] = P7 #Parameter7
        
    if parameterSelect == 7: #epochs
        crossover[0][7] = P8 #Parameter8
        
    if parameterSelect == 8: #batchsize
        crossover[0][8] = P9 #Parameter9
        

    crossover= crossover.astype(int)
    
    print("-------------------This is the new child to replace parent----------------")
    print(crossover)
    
    return crossover


def mutation(crossover):
    
    #np.random.seed()
    random.seed()
    np.random.seed()
    #print(crossover)
    #choose a parameter to be mutated
    #parameterSelect = np.random.randint(0, numberOfParameters, 1)
    
    #define the possible values for each parameter
    filterList = [6,12,16,18,24,28,32]
    OptionalLayerList=[0,1]
    OptionalDenseList=[1,0]
    Dense_sizeList=[10,16,32,64,128]
    epochsList=[40,50,60,70,100,120,150]
    batchsizeList=[4,16,18,32,64]
    
    #randomly select a value for each parameter
    
    P1 = random.choice(filterList)
    P2 = random.choice(OptionalLayerList)
    P3 = random.choice(filterList)
    P4 = random.choice(OptionalLayerList) 
    P5 = random.choice(filterList)
    P6 = random.choice(OptionalLayerList)
    P7 = random.choice(Dense_sizeList)
    P8 = random.choice(epochsList)
    P9 = random.choice(batchsizeList)
   # print("_________Here are the new PSSSSSS_____________")
   # print(P1,P2,P3,P4,P5,P6,P7,P8,P9)
    
    #if parameterSelect == 0: #filter1size
    crossover[0][0] = P1 #Parameter1
    
    #if parameterSelect == 1: # layer 2
    crossover[0][1] = P2 #Parameter2
        
    #if parameterSelect == 2: #filter2size
    crossover[0][2] = P3 #Parameter3
        
    #if parameterSelect == 3: #layer3
    crossover[0][3] = P4 #Parameter4
        
    #if parameterSelect == 4: #filter3size
    crossover[0][4] = P5 #Parameter5
        
    #if parameterSelect == 5: #Denselayer
    crossover[0][5] = P6 #Parameter6
     
    #if parameterSelect == 6: #Densesize
    crossover[0][6] = P7 #Parameter7
        
    #if parameterSelect == 7: #epochs
    crossover[0][7] = P8 #Parameter8
        
    #if parameterSelect == 8: #batchsize
    crossover[0][8] = P9 #Parameter9
        
    crossover= crossover.astype(int)
    
    print("This is the new child to replace parent")
    print(crossover)
    
    return crossover


#select parents for replacement #fxn is still in progress
def parents_replacement(population, fitness, numParents, Children):#creates new population
    WorstparentsIndex=np.argpartition(fitness,-numParents)[-numParents:] #returns an arry of index
    print("The worst parent index for this iteration is :")
    print(WorstparentsIndex)
    population[WorstparentsIndex]= Children
    #print(fitness[WorstparentsIndex])
    return population, WorstparentsIndex


def UpdateFitnessValues(population, childIndex, fitnessValue,train_X, train_y,test_X, test_y, n_hours, n_features):
    
    Newchild=population[childIndex]
    
    
    #Scale Xinputes and outputs
    x_scaler = MinMaxScaler()
    train_X = x_scaler.fit_transform(train_X)
    test_X = x_scaler.transform(test_X)

    #reshape output
    test_y = test_y.reshape((len(test_y), 1))
    train_y = train_y.reshape((len(train_y), 1))
    n_outputs =train_y.shape[1]

    #Scale Yinputes and outputs
    y_scaler = MinMaxScaler()
    train_y = y_scaler.fit_transform(train_y)
    test_y = y_scaler.transform(test_y)

    # reshape input to be 3D [samples, timesteps, features]
    train_X = train_X.reshape((train_X.shape[0], n_hours, n_features))
    test_X = test_X.reshape((test_X.shape[0], n_hours, n_features))
    
    inputShape= (train_X.shape[1], train_X.shape[2])
    
    Score=[]
    
    params_dict={}
    
    for i in range(Newchild.shape[0]):
        
    
        params_dict['filter_size1'] = Newchild[i][0]
        params_dict['layer2'] = Newchild[i][1]
        params_dict['filter_size2']= Newchild[i][2]
        params_dict['layer3'] = Newchild[i][3]
        params_dict['filter_size3']= Newchild[i][4]
        params_dict['OptionalDense'] = Newchild[i][5]
        params_dict['Dense_size'] = Newchild[i][6]
        params_dict['epochs'] = Newchild[i][7]
        params_dict['batchsize'] = Newchild[i][8]
        
        #----------reproducibility------------------
        tf.compat.v1.get_default_graph()
        tf.random.set_seed(2)
        random.seed(2)
        np.random.seed(2)
        
        #Create the model
        model = Sequential()
        #----------First Conv Layer-------------------
        #kernelSize=params_dict['kernel_size1']
        #print(kernelSize)
        #model.add(Conv1D(filters=params_dict['filter_size1'], kernel_size=(kernelSize), activation='relu', input_shape=(inputShape)))
        model.add(Conv1D(filters=params_dict['filter_size1'], kernel_size=1, activation='relu', input_shape=(inputShape)))
        model.add(MaxPooling1D(pool_size=1)) #first pool
              
        #----------Second Conv Layer------------------- 
        layer2=params_dict['layer2']
        if layer2>0:
    
            model.add(Conv1D(filters=params_dict['filter_size2'], kernel_size=1, activation='relu'))
            model.add(MaxPooling1D(pool_size=1)) #2nd pool
              
       #----------Third Conv Layer----------------------
        layer3=params_dict['layer3']
        if layer3>0:
    
            model.add(Conv1D(filters=params_dict['filter_size3'], kernel_size=1, activation='relu'))
            model.add(MaxPooling1D(pool_size=1)) #3rd pool
       
        model.add(Flatten())

        #----------Optional Dense layer------------------
        OptionalDense=params_dict['OptionalDense']
        if OptionalDense>0:
              
            model.add(Dense(params_dict['Dense_size'], activation='relu'))
    
        model.add(Dense(1))
              
        model.compile(loss='mse', optimizer='adam')
    
        # fit network
        history = model.fit(train_X, train_y, epochs=params_dict['epochs'], batch_size=params_dict['batchsize'], validation_data=(test_X, test_y), verbose=0, shuffle=False)

        # make a prediction
        yhat = model.predict(test_X)

        #inverse the scales
        yhat = y_scaler.inverse_transform(yhat)
        inv_y = y_scaler.inverse_transform(test_y)

        # calculate RMSE
        rmse = sqrt(mean_squared_error(inv_y, yhat))
        #print('Test RMSE: %.3f' % rmse)
        Score.append(rmse)
        
        print('this is the child rmse', rmse)
        
        fitnessValue[childIndex[0]]=Score[0]
        
    return fitnessValue


def plot_parameters(numberOfGenerations, numberOfParents, parameter, parameterName):
    #inspired from https://matplotlib.org/gallery/images_contours_and_fields/image_annotated_heatmap.html
    generationList = ["Gen {}".format(i) for i in range(numberOfGenerations+1)]
    populationList = ["Parent {}".format(i) for i in range(numberOfParents)]
    
    
    
    fig, ax = plt.subplots(figsize=(50,50)) #15,20 looks great formely 10,15
    im = ax.imshow(parameter, cmap=plt.get_cmap('Blues'))
    #im = ax.imshow(parameter, cmap='hot')
    
    # show ticks
    ax.set_xticks(np.arange(len(populationList)))
    ax.set_yticks(np.arange(len(generationList)))
    
    # show labels
    ax.set_xticklabels(populationList, size='25')
    ax.set_yticklabels(generationList, size='25')
    
    # set ticks at 45 degrees and rotate around anchor
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")
    
    
    # insert the value of the parameter in each cell
    #for i in range(len(generationList)):
     #   for j in range(len(populationList)):
      #      text = ax.text(j, i, parameter[i, j],
       #                    ha="center", va="center", color="k", size='25')
    
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="2%", pad=0.5)
   

    cbar=plt.colorbar(im, cax=cax)
    cbar.ax.tick_params(labelsize=30)
    cbar.set_label(parameterName, rotation=90, size='30')
    
  #  cbar=plt.colorbar(im,pad=0.04)
    
    
  #  cbar.set_label(parameterName, rotation=90)
    
    
    ax.set_title("Change in the value of " + parameterName, size='30')
    fig.tight_layout()
    plt.show()
   # plt.savefig("C:/Users/Amina Lawal/Documents/My Thesis/Original_DatasetFiles/image1.png",bbox_inches='tight',dpi=100)
    