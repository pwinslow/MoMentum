api_key = "INSERT-YOUR-CHANGE.ORG-API-KEY-HERE"


#########################################################################################################

clf_feature_list = ['overview_linkcount',
                     'title_adjective_count',
                     u'title_subjectivity',
                     'title_verb_count',
                     'title_word_per_sentence',
                     'letter_body_adjective_count',
                     u'letter_body_polarity',
                     'letter_body_sentence_count',
                     u'letter_body_subjectivity',
                     'letter_body_verb_count',
                     'letter_body_word_per_sentence',
                     'overview_adjective_count',
                     u'overview_polarity',
                     'overview_sentence_count',
                     u'overview_subjectivity',
                     'overview_verb_count',
                     'overview_word_per_sentence']

goal_mean = 3822.6022144427257
goal_std = 13046.654706163794

norms_dict = {'goal_mean': 6283.668608477345,
 'goal_std': 23098.38184827937,
 'letter_body_adjective_count_mean': 3.895580958880737,
 'letter_body_adjective_count_std': 12.576480472849202,
 'letter_body_linkcount_mean': 0.06020425573402881,
 'letter_body_linkcount_std': 0.5760392122873208,
 'letter_body_sentence_count_mean': 3.2544665707948424,
 'letter_body_sentence_count_std': 8.080113913015628,
 'letter_body_verb_count_mean': 6.602749408925829,
 'letter_body_verb_count_std': 18.778688616301846,
 'letter_body_word_per_sentence_mean': 6.869003718017658,
 'letter_body_word_per_sentence_std': 3.707671890298295,
 'overview_adjective_count_mean': 18.268603602505667,
 'overview_adjective_count_std': 23.481619143142037,
 'overview_linkcount_mean': 0.6763107222073269,
 'overview_linkcount_std': 2.4610721816131123,
 'overview_sentence_count_mean': 13.119360421186048,
 'overview_sentence_count_std': 15.160062244345118,
 'overview_verb_count_mean': 30.8148048845882,
 'overview_verb_count_std': 35.82794528742458,
 'overview_word_per_sentence_mean': 9.994724282362359,
 'overview_word_per_sentence_std': 6.480282333017182,
 'target_count_mean': 2.8307943549369927,
 'target_count_std': 5.676411636048672,
 'title_adjective_count_mean': 0.4208691837082897,
 'title_adjective_count_std': 0.7024178390208461,
 'title_sentence_count_mean': 1.0913300996904478,
 'title_sentence_count_std': 0.33531429700590154,
 'title_verb_count_mean': 1.0229848636263923,
 'title_verb_count_std': 1.0043939597994052,
 'title_word_per_sentence_mean': 7.833104622159389,
 'title_word_per_sentence_std': 3.082275871771227}
