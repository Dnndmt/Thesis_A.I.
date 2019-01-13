from sklearn.naive_bayes import GaussianNB

from sklearn.preprocessing import MinMaxScaler, StandardScaler

def train_bayes(X_data, y_data):
    """ Function that trains a naive bayes classifier algorithm to predict 
        one day ahead stock price direction. Standardization of the features is
        performed but cross validation is left to the default 3 folds"""
    
    names = X_data.columns
    
    #scaler = MinMaxScaler(feature_range=(0, 1))
    #X_data = scaler.fit_transform(X_data)
    
    scaler = StandardScaler()
    scaled_df = scaler.fit_transform(X_data)
    X_data = pd.DataFrame(scaled_df, columns=names)
    
    X_train, X_test, y_train, y_test = train_test_split(X_data, 
                                                        y_data, 
                                                        test_size = 0.2, random_state=0)
    acc_results = []
    f1_results = []
    for ticker in list(X_train):
        
        clf = GaussianNB()
        clf.fit(X=X_train[ticker].reshape(-1, 1), y=np.array(y_train[ticker], dtype=int))
        
        y_pred = clf.predict(X_test[ticker].reshape(-1, 1))
        acc_results.append(accuracy_score(np.array(y_test[ticker], dtype=int), y_pred))
        f1_results.append(f1_score(np.array(y_test[ticker], dtype=int), y_pred, 
                                   average='weighted'))

    return acc_results, f1_results
