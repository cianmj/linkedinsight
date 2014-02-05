'''
Created on Jul 8, 2013

@author: work
'''
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics

#from sklearn.decomposition import PCA
#from sklearn import svm

def forest_solver(train_data,test_data):
    best = 0.0
    val = 0
    best_Output = []
    for i in [x**2 for x in range(1,8)]:

        X = train_data[0::,1::]
        y = train_data[0::,0]
        
        Xt = test_data[0::,1::]
        yt = test_data[0::,0]

        Forest = RandomForestClassifier(n_estimators = i)#, compute_importances=True)#,random_state=1838) # = 93758
        Forest = Forest.fit(X,y)
        Output = Forest.predict(Xt)    
        result = Forest.score(Xt,yt)

        #clf = svm.SVC()
        #clf.fit(X,y)

        if result>best:
            best = result
            val = i
            best_Output = Output

    # pca analysis :
    #pca = PCA(n_components=len(X[0,:]))
    #pca.fit(X)
    #PCA(copy=True, n_components=len(X[0,:]), whiten=False)
    #print pca.explained_variance_ratio_
    #raw_input()

    #print best, val
    #print Forest.score(Xt,[0]*len(yt)),Forest.score(Xt,[1]*len(yt))
    #print Forest.score(X,y), Forest.score(X,[0]*len(y)), Forest.score(X,[1]*len(y))
    #print "Classification report for %s" % Forest
    #print metrics.classification_report(yt, [0]*len(yt))

    #print "Classification report for %s" % Forest
    #print metrics.classification_report(yt, Output)

    return Forest.feature_importances_

