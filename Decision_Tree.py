def train_tree(X_data, y_data):
    """ Function that receives two data with similar number rows as observations
        and columns of tickers. The function splits the data and train 
        a decision tree for each stock ticker """

    X_train, X_test, y_train, y_test = train_test_split(X_data, 
                                                        y_data, 
                                                        test_size = 0.2, random_state=0)

    acc_results = []
    f1_results = []
    best_p_lst = []
    for ticker in list(X_train):
        parameters = {'max_depth':range(3,10)}
        clf = GridSearchCV(tree.DecisionTreeClassifier(), parameters, n_jobs=4, cv=10)
        clf.fit(X=X_train[ticker].reshape(-1, 1), y=np.array(y_train[ticker], dtype=int))
        tree_model = clf.best_estimator_
        
        y_pred = clf.predict(X_test[ticker].reshape(-1, 1))
        acc_results.append(accuracy_score(np.array(y_test[ticker], dtype=int), y_pred))
        f1_results.append(f1_score(np.array(y_test[ticker], dtype=int), y_pred, 
                                   average='weighted'))
        best_p_lst.append(list(clf.best_params_.values())[0])

    return acc_results, f1_results, best_p_lst
