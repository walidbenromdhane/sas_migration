import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import numpy as np

class Sas_tables_compare:

    def __init__(self, table_1, table_2):

        self.match_tbl1_tbl2 = self.compute_match_percentage(table_1,table_2)
        self.match_tbl2_tbl1 = self.compute_match_percentage(table_2,table_1)


    #######################################################################
    #######################################################################
    #######################################################################
    def compute_match_percentage(self, table_1, table_2):
        # match_table = [{'sim': [col1_tbl1,col1_tbl2,name_sim, content_sim]}]

        match_table = []

        for item in table_1['column_names']:

            try:
                #Compute match by column name
                #######################################################################
                corpus = table_2['column_names'].copy()
                corpus.insert(0,item)
                count_vectorizer = CountVectorizer(analyzer='char', ngram_range=(2, 3), decode_error='ignore')
                sparse_matrix = count_vectorizer.fit_transform(corpus)
                # doc_term_matrix = sparse_matrix.todense()
                cos_sim = cosine_similarity(sparse_matrix, sparse_matrix)
                matched_col = corpus[1:][np.argmax(cos_sim[0][1:])]
                matched_val = max(cos_sim[0][1:])

                #Compute match by column content
                #######################################################################
                tabl_1_col_idx = -1000
                tabl_2_col_idx = -1000
                content_sim = 'NA'
                try:
                    tabl_1_col_idx = table_1['column_names'].index(item)
                    tabl_2_col_idx = table_2['column_names'].index(matched_col)
                except:
                    print('column names not found!')

                if tabl_1_col_idx >= 0 and tabl_2_col_idx >= 0:
                    table_1_unq = table_1['column_unq'][tabl_1_col_idx]
                    table_2_unq = table_2['column_unq'][tabl_2_col_idx]
                    if table_1_unq != []:
                        unq_lst     = [a for a in table_1_unq if a in table_2_unq]
                        content_sim = len(unq_lst)/len(table_1_unq)

                match_table.append({'name_sim'   :[item, matched_col, matched_val],
                                    'content_sim':[item, matched_col, content_sim]})
            except Exception as e:
                print('####################################')
                print('Warning in compute_match_percentage!')
                print(e)
                print('####################################')

        if len(match_table) > 0:
            return {'name_sim'   : np.mean([a['name_sim'][2] for a in match_table]),
                    'content_sim': np.mean([a['content_sim'][2] for a in match_table if a['content_sim'][2] != 'NA'])}
        else:
            return {'name_sim': '',
                    'content_sim': ''}










