# Benchmark decision tree only on targets. Previous day targets predict next day targets

tgt_lst = [sr_targets.iloc[-3151:,:], vola_targets.iloc[1:,:]]
tgt_names = ['Returns', 'Volatility']

feat_lst = [sr_targets.iloc[-3152:-1,:], vola_targets.iloc[:-1,:]]
feat_names = ['Returns_pr', 'Volatility_pr']

data_acc_pr = {}
data_f1_pr = {}
data_best_p_pr = {}
for i, tgt in enumerate(tgt_lst):
    for j, feat in enumerate(feat_lst):
     
        acc_results_pr, f1_results_pr, best_p_lst_pr = train_tree(feat, tgt)
        
        data_acc_pr['{0} & {1}'.format(feat_names[j], tgt_names[i])] = acc_results_pr
        data_f1_pr['{0} & {1}'.format(feat_names[j], tgt_names[i])] = f1_results_pr
        data_best_p_pr['{0} & {1}'.format(feat_names[j], tgt_names[i])] = best_p_lst_pr
