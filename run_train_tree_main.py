# code to train decision tree on the three features and predict returns and volatility

tgt_lst = [sr_targets.iloc[-3151:,:], vola_targets.iloc[1:,:]]
tgt_names = ['Returns', 'Volatility']

feat_lst = [entropy.iloc[-3152:-1,:], kl_div.iloc[-3152:-1,:], 
            kl_div_pr.iloc[-3152:-1,:]]
feat_names = ['Entropy', 'KL-div-max', 'KL-div-pr']

data_acc_2 = {}
data_f1_2 = {}
data_best_p_2 = {}
for i, tgt in enumerate(tgt_lst):
    for j, feat in enumerate(feat_lst):
     
        acc_results_2, f1_results_2, best_p_lst_2 = train_tree(feat, tgt)
        
        data_acc_2['{0} & {1}'.format(feat_names[j], tgt_names[i])] = acc_results_2
        data_f1_2['{0} & {1}'.format(feat_names[j], tgt_names[i])] = f1_results_2
        data_best_p_2['{0} & {1}'.format(feat_names[j], tgt_names[i])] = best_p_lst_2
