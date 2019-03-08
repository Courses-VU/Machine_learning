import glob
from itertools import cycle
import sys
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import sklearn
from mlxtend.plotting import plot_confusion_matrix, plot_decision_regions
from sklearn import datasets
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest
from sklearn.metrics import accuracy_score, auc, confusion_matrix, roc_curve
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler, label_binarize
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier


def roc_plot(X_train,y_train,X_test, y_test, linear, tree, knn):
    """
    This function should calculate the roc plot for every class of SVM classifier
    using every class ALl-against-all. Then make the average for the different classes
    and plot.   WORKING: for svm
    """
    #convert dataframe to list(numbers instead of labels)
    labels_test, uniques = pd.factorize(y_test.iloc[:, 0].tolist())
    labelst_train,uniques = pd.factorize(y_train.iloc[:,0].tolist())
    # Binarize the output
    y_test = label_binarize(labels_test, classes=[0, 1, 2, 3, 4])
    y_train=label_binarize(labelst_train,classes=[0, 1, 2, 3, 4])
    n_classes = 5
    #print(y_test, y_train)
    # Learn to predict each class against the other
    classifier = OneVsRestClassifier(SVC(kernel="linear",probability=True, C=1,random_state=0))
    #classifier = OneVsRestClassifier(knn)
    print(classifier)
    #print(y_train)
    y_score = classifier.fit(X_train, y_train).decision_function(X_test)
    #y_score = classifier.fit(X_train, y_train).predict_proba(X_test)
    # print(y_score[:,0])
    #compute ROC curve for each class
    fpr=dict()
    tpr=dict()
    roc_auc=dict()
    for i in range(n_classes):
        fpr[i],tpr[i], _ = roc_curve(y_test[:,i],y_score[:,i])
        #print(fpr[i], tpr[i])
        roc_auc[i]=auc(fpr[i],tpr[i])
    
    #compute micro-average ROC
    fpr["micro"],tpr["micro"],_=roc_curve(y_test.ravel(), y_score.ravel())
    roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])
    #plot class 2
    #print("hello 2")
    plt.figure()
    lw = 2
    plt.figure()
    plt.plot(fpr["micro"], tpr["micro"],
         label='micro-average ROC curve (area = {0:0.2f})'
               ''.format(roc_auc["micro"]),
         color='deeppink', linestyle=':', linewidth=4)
    
    colors = cycle(['aqua', 'darkorange', 'cornflowerblue','yellow','black'])
    for i, color in zip(range(n_classes), colors):
        plt.plot(fpr[i], tpr[i], color=color, lw=lw,
                label='ROC curve of class {0} (area = {1:0.2f})'
                ''.format(i, roc_auc[i]))
        
    
    
    # plt.plot(fpr[index], tpr[index], color='darkorange',
    #         lw=lw, label='ROC curve (area = %0.2f)' % roc_auc[index])
    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic example')
    plt.legend(loc="lower right")
    plt.show()


def decision_tree(X_train, X_test, y_train, y_test):
    tree=DecisionTreeClassifier()
    dtree_model = tree.fit(X_train, y_train) 
    dtree_predictions = dtree_model.predict(X_test) 
    # creating a confusion matrix 
    cm = confusion_matrix(y_test, dtree_predictions)
    accuracy=accuracy_score(dtree_predictions,y_test)
    return cm,accuracy, tree


def support_vector_machine(X_train, X_test, y_train, y_test):
     # training a linear SVM classifier 
    linear=SVC(kernel = 'linear', C = 1)
    svm_model_linear = linear.fit(X_train, y_train) 
    svm_predictions = svm_model_linear.predict(X_test) 
    
    # model accuracy for X_test   
    accuracy = svm_model_linear.score(X_test, y_test) 
    # creating a confusion matrix 
    cm = confusion_matrix(y_test, svm_predictions)

    #labels, uniques = pd.factorize(y_test.iloc[:, 0].tolist())
    # labels=labels.astype('U')
    # labels = np.array(labels, dtype=data.astype('U'))
    # print(labels.dtype)
    # print(X_test.as_matrix().dtype)
    #plot_decision_regions(X_test, y_test, clf=linear, res=0.1)
    #plt.show()

    return cm, accuracy, linear

def k_nearest_neighbors(X_train, X_test, y_train, y_test):
    # training a KNN classifier 
    knn=KNeighborsClassifier(n_neighbors = 15)
    knn.fit(X_train, y_train)
    
    # accuracy on X_test 
    accuracy = knn.score(X_test, y_test)     
    # creating a confusion matrix 
    knn_predictions = knn.predict(X_test)  
    cm = confusion_matrix(y_test, knn_predictions)
    return cm, accuracy, knn


def plot_boundaries(svm_model,tree, knn, X,y):
    # Plot Decision Region using mlxtend's  plotting function
    # Plotting decision regions
    plot_decision_regions(X=X, y=y, clf=svm_model, legend=2)
    plt.show()
    plot_decision_regions(X=X, y=y, clf=knn, legend=2)
    plt.show()
    plot_decision_regions(X=X, y=y, clf=tree, legend=2)
    plt.show()

def plot_accuracy(method, cm,accuracy):
    print("Classifier: "+method)
    print("Confusion matrix: \n")
    print(cm)
    print("Accuracy: "+str(accuracy)+"\n")
    fig, ax = plot_confusion_matrix(conf_mat=cm)
    plt.title("Confusion matrix "+method)
    plt.show()
    

def main():
    Data = np.loadtxt("data/PCA_transformed_data.csv", delimiter=",")
    Labels=pd.read_csv("data/labels.csv",index_col=0)
    print(Labels)
    #convert labels from string to numbers
    Labels, uniques = pd.factorize(Labels.iloc[:, 0].tolist())
    #selecting only 2 components
    Data=Data[:,1:3]
    print(Data)
    print(Labels)
    
    #TO VISUALIZE the FEATURE SPACE, remove comments below
    # labels, uniques = pd.factorize(Labels.iloc[:, 1].tolist())
    # plt.scatter(Data.as_matrix()[:,0], Data.as_matrix()[:,1], s=4, alpha=0.3, c=labels, cmap='RdYlBu_r')
    # plt.show()
    #split dataset in tr
    # aining and testing
    X_train, X_test, y_train, y_test = train_test_split(Data, Labels, random_state = 0,test_size=0.5) 
    
    #decision tree classifier
    cm_dt, acc_dt,tree=decision_tree(X_train, X_test, y_train, y_test)
    plot_accuracy("decision tree", cm_dt, acc_dt)   

    #SVM
    cm_svm, accuracy_svm, svm_model =support_vector_machine(X_train, X_test, y_train, y_test)
    plot_accuracy("SVM", cm_svm, accuracy_svm)

    #KNN
   
    cm_knn, accuracy_knn, knn=k_nearest_neighbors(X_train, X_test, y_train, y_test)
    plot_accuracy("K-NN", cm_knn, accuracy_knn)

    plot_boundaries(svm_model,tree,knn, X_test, y_test)

    #roc plot --> takes a lot for svm
    #roc_plot(X_train, y_train, X_test, y_test, svm_model, tree, knn)




if __name__ == '__main__':
    main()
