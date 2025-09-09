from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import euclidean_distances
import pandas as pd
import numpy as np
import math

from find_sas_files import Find_SAS_Files
from public_functions import Public_functions
import os

class Find_Similarities:

    #############################################################################################
    #############################################################################################
    #############################################################################################
    def __init__(self, ORG, main_directory_sasfiles, report_counter, max_similarity_matrix_size,output_directory):

        self.file_suffix = os.path.split(main_directory_sasfiles)[-1]
        self.output_directory = output_directory
        all_files = sorted(ORG.files_df, key=lambda a: a['path'])
        m = max_similarity_matrix_size
        indexes = [i*m for i in range(math.ceil(len(all_files) / m))]

        if len(indexes) > 0:
            if indexes[-1] < len(all_files):
                indexes.append(len(all_files))

            for idx in range(1, len(indexes)):
                df_f = [{b: a[b] for b in ['id','path','fname']} for a in all_files[indexes[idx - 1]:indexes[idx]]]
                sas_file_sim = []

                for row in df_f:
                    with open(os.path.join(row['path'], row['fname']), 'r', encoding="latin_1", errors='ignore') as sasfile:
                        row['txt'] = sasfile.read().strip()

                corpus = [a['txt'] for a in df_f]
                if len(corpus) > 1:
                    try:
                        count_vectorizer = CountVectorizer(analyzer='word', ngram_range=(2, 3), decode_error='ignore')
                        sparse_matrix = count_vectorizer.fit_transform(corpus)
                        sparse_matrix = sparse_matrix > 0
                        # doc_term_matrix = sparse_matrix.todense()
                        cos_sim = cosine_similarity(sparse_matrix, sparse_matrix)
                        sas_file_sim.extend([{'id1':df_f[j]['id'],
                                            'id2': df_f[i]['id'],
                                            'similarity': cos_sim[i,j].round(2)}
                                           for i in range(cos_sim.shape[0])
                                           for j in range(cos_sim.shape[1])])

                        Public_functions.save_dict_to_csv(sas_file_sim,
                                                          '{0}/sas_programs_sim_{1}_{2}.csv'.format(self.output_directory, str(idx),self.file_suffix),
                                                          ['id1','id2','similarity'])
                        print('{0} files checked for similarities!'.format(str(idx - 1 + len(df_f))))

                    except Exception as e:
                        print('####################################')
                        print('Warning in finding similarities!')
                        print(e)
                        print('####################################')


