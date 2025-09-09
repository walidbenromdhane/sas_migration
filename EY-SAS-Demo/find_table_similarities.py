from public_functions import Public_functions
import pandas as pd
from sas_table_compare import Sas_tables_compare
import math
import os
class Find_table_similarities:

    ####################################################################################
    ####################################################################################
    ####################################################################################
    def __init__(self, ORG, main_directory_sasfiles, report_counter, max_table_similarity_matrix_size,output_directory):

        self.file_suffix = os.path.split(main_directory_sasfiles)[-1]
        self.output_directory = output_directory
        all_tables = sorted(ORG.tables_df, key=lambda a: a['path'])
        m = max_table_similarity_matrix_size
        indexes = [i * m for i in range(math.ceil(len(all_tables) / m))]

        if len(indexes) > 0:
            if indexes[-1] < len(all_tables):
                indexes.append(len(all_tables))

            for idx in range(1, len(indexes)):
                df_t = [{b: a[b] for b in ['id', 'column_names', 'column_unq']} for a in all_tables[indexes[idx - 1]:indexes[idx]]]
                table_sim = []
                for ii in range(len(df_t)):
                    for jj in range(ii+1,len(df_t)):

                        sim_res = Sas_tables_compare(df_t[ii],df_t[jj])

                        table_sim.append({'table_1_id'           : df_t[ii]['id'],
                                          'table_2_id'           : df_t[jj]['id'],
                                          'table_1_2_name_sim'   : sim_res.match_tbl1_tbl2['name_sim'],
                                          'table_1_2_content_sim': sim_res.match_tbl1_tbl2['content_sim'],
                                          'table_2_1_name_sim'   : sim_res.match_tbl2_tbl1['name_sim'],
                                          'table_2_1_content_sim': sim_res.match_tbl2_tbl1['content_sim']})

                print('{0} table similarities were checked!'.format(str(idx - 1 + len(df_t))))
                self.save_results(table_sim, idx)

    ####################################################################################
    ####################################################################################
    ####################################################################################
    def save_results(self, table_sim, counter):
        Public_functions.save_dict_to_csv(table_sim, '{0}/sas_tables_sim_{1}_{2}.csv'.format(self.output_directory, str(counter), self.file_suffix), ['table_1_id',
                                                                                                            'table_2_id',
                                                                                                            'table_1_2_name_sim',
                                                                                                            'table_1_2_content_sim',
                                                                                                            'table_2_1_name_sim',
                                                                                                            'table_2_1_content_sim'])







