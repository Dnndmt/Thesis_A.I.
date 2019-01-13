# Benchmark decision tree only on targets. Previous day targets predict next day targets

tgt_lst = [sr_targets.iloc[-3151:,:], vola_targets.iloc[1:,:]]
tgt_names = ['Returns', 'Volatility']

feat_lst = [sr_targets.iloc[-3152:-1,:], vola_targets.iloc[:-1,:]]
feat_names = ['Returns_pr', 'Volatility_pr']

data_acc1 = {}
data_f11 = {}
data_best_p1 = {}
for i, tgt in enumerate(tgt_lst):
    for j, feat in enumerate(feat_lst):
     
        acc_results1, f1_results1, best_p_lst1 = train_tree(feat, tgt)
        
        data_acc1['{0} & {1}'.format(feat_names[j], tgt_names[i])] = acc_results1
        data_f11['{0} & {1}'.format(feat_names[j], tgt_names[i])] = f1_results1
        data_best_p1['{0} & {1}'.format(feat_names[j], tgt_names[i])] = best_p_lst1
