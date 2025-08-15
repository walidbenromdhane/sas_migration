import csv
import operator
import itertools
import collections, functools, operator
import os.path
import re
import pandas as pd
import numpy as np
import platform

##
import data_model_extractor as extractor
import os
import datetime
import json


class Public_functions:

    #############################################################################################

    @staticmethod
    def save_dict_to_csv(lst, fname, first_cols=None):
        keys = list(set([i for j in lst for i in j.keys()]))
        keys.sort()
        if (first_cols !=None) & (keys != []) & (len(keys) >= len(first_cols)):
            for item in first_cols: keys.remove(item)
            for item in first_cols[::-1]: keys.insert(0,item)
        with open(fname, 'w', newline='', errors='ignore') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(lst)

    #############################################################################################

    @staticmethod
    def group_dict_lst(lst,grp_key):
        if len(lst) == 0:
            return
        lst = sorted(lst, key=operator.itemgetter(*grp_key))
        all_keys = list(set([i for item in lst for i in list(item.keys())]))
        other_keys = [i for i in all_keys if i not in grp_key]
        outputList = []
        for i, g in itertools.groupby(lst, key=operator.itemgetter(*grp_key)):
            outputList.append(list(g))

        final_output=[]
        for item in outputList:
            # sum the values with same keys
            temp = {i:item[0][i] for i in grp_key}
            for i in other_keys: temp[i] = sum([j[i] for j in item if i in list(j.keys())])
            final_output.append(temp)

        return final_output

    #############################################################################################

    @staticmethod
    def find_inclusive_intervals(txt_idx):
        txt_idx = sorted(txt_idx, key=lambda a: a[0])
        b = []
        for begin, end in txt_idx:
            if b and b[-1][1] >= begin:
                b[-1][1] = max(b[-1][1], end)
            else:
                b.append([begin, end])
        return b

    #############################################################################################

    @staticmethod
    def find_exclusive_intervals(txt_idx):
        txt_idx = [a for a in txt_idx
                   if np.prod([1 - (a[0] - b[0] <= 0) * (a[1] - b[1] >= 0)
                               for b in txt_idx if b != a]) == 1]
        return txt_idx

    #############################################################################################

    @staticmethod
    def replace_txt(txt, src_txt, dst_txt):
        if src_txt.startswith('&'):
            txt = txt.replace(src_txt,dst_txt)
        else:
            txt1_idx = sorted([(a.start(0),a.end(0)) for a in re.finditer(r'["](.*?)["]'  , txt)], key=lambda a: a[0])
            txt2_idx = sorted([(a.start(0),a.end(0)) for a in re.finditer(r'[\'](.*?)[\']', txt)], key=lambda a: a[0])
            txt_idx  = [a for b in [txt1_idx,txt2_idx] for a in b]
            txt_idx  = [a for a in txt_idx if np.prod([1 - (a[0]-b[0]>=0)*(a[1]-b[1]<=0) for b in txt_idx if b!= a]) == 1]
            txt_idx.insert(0,(0,0))
            txt_idx.insert(len(txt_idx),(len(txt),len(txt)))
            txt_idx = sorted(txt_idx, key=lambda a: a[0])
            txt      = ''.join([txt[txt_idx[i-1][1]:txt_idx[i][0]].replace(src_txt,dst_txt) + txt[txt_idx[i][0]:txt_idx[i][1]] for i in range(1,len(txt_idx))])

        return txt

    #############################################################################################

    @staticmethod
    def clean_sas_code(sas_code_lst, sas_code):
        try:

            # #Clean the code
            sas_code = sas_code.replace(r"\t" ,"").\
                replace(r"\tab" ,"").\
                replace("=" ," = "). \
                replace("(" ," (").\
                replace(")" ,") ").\
                replace("  " ," ").\
                replace(" ;" ,";").\
                replace(";" ,"; ")
                        
            #find single comments
            sas_code_single_comments = re.findall(r"\n\*.*\n", sas_code)
            #replace single comments
            for item in sas_code_single_comments:
                sas_code = sas_code.replace(item, '\\n')
            #find multi comments
            sas_code_multi_comments  = re.findall(r"/\*(.*?)\*/", sas_code, re.DOTALL)
            #replace multi comments
            for item in sas_code_multi_comments:
                sas_code = sas_code.replace(item, '')

            #Create the output
            sas_code_lst = sas_code.split('\\n')
            sas_code_lst = [a for a in sas_code_lst if a not in (r'\n',r'\\n', '', ' ', r'\r')]
            sas_code = '\\n' + '\\n'.join(sas_code_lst)

        except Exception as e:

            print('Warning in cleaning SAS code')
            print('################################################################')
            print(e)
            print('################################################################')
            print(r'\n')

        return sas_code_lst, sas_code

    #############################################################################################

    @staticmethod
    def find_table_relationships(id_counter,input_file):
        try:
            dependencies_content = []

            with open(input_file, 'r') as f:
                file_content = f.read()

            file_content = extractor.normalize_text(file_content)

            blocks = extractor.get_blocks(file_content)

            for block in blocks:

                # Extract dependencies for the current block
                dependencies_content_current = extractor.extract_dependencies(id_counter,block)

                # Append the dependencies for the current Block to the global dependencies 
                #dependencies_content.append(list(dependencies_content_current.values()))
                dependencies_content.append(dependencies_content_current)
        except Exception as e:

            print('Warning in finding tabel relationships')
            print('################################################################')
            print(e)
            print('################################################################')
            print(r'\n')

        return dependencies_content

    #############################################################################################

    @staticmethod
    def find_include(sas_code):
        inc_lst = []
        sas_code = sas_code.lower()
        inc     = re.findall(r'%inc .*?;|%include .*?;', sas_code)
        inc_idx = [a.start(0) for a in re.finditer(r'%inc .*?;|%include .*?;', sas_code)]

        for idx in range(len(inc)):

            try:
                f_txt = inc[idx].strip().replace('"','').replace("'",'').replace(';','').split(' ')

                if len(f_txt) > 1:
                    inc_lst.append({'type'     : 'include',
                                     'original': inc[idx],
                                     'key'     : '',
                                     'value_0' : [f_txt[1]],
                                     'value_1' : [f_txt[1]],
                                     'index'   : inc_idx[idx]})

            except Exception as e:
                print('Warning in finding include!')
                print('################################################################')
                print(e)
                print('################################################################')
                print(r'\n')

        return inc_lst

    #############################################################################################

    @staticmethod
    def find_macro(sas_code):
        macro_lst = []
        sas_code = sas_code.lower()
        mac = re.findall(r'%macro .*?;', sas_code)
        mac_idx = [a.start(0) for a in re.finditer(r'%macro .*?;', sas_code)]
        if len(mac) > 0:
            try:
                mac = [{'type'     : 'macro',
                       'original'  : mac[i].strip(),
                        'key'     : 'macro',
                        'value_0'  : [mac[i].split(' ')[0].split('(')[0]],
                        'value_1'  : [''],
                        'index'    : mac_idx[i]} for i in range(len(mac_idx))]
            except Exception as e:
                print('Warning in detecting %let')
                print('################################################################')
                print(e)
                print('################################################################')
                print(r'\n')
        return mac

    #############################################################################################

    @staticmethod
    def find_let(sas_code):
        sas_code = sas_code.lower()
        let      = re.findall(r'%let .*?;', sas_code)
        let_idx = [a.start(0) for a in re.finditer(r'%let .*?;', sas_code)]
        if len(let) > 0:
            try:
                let = [{'type'     : 'let',
                        'original' : let[i].strip(),
                        'key'      : let[i].strip().split('=')[0],
                        'value_0'  : [''.join(let[i].strip().split('=')[1:])],
                        'value_1'  : [''],
                        'index'    : let_idx[i]} for i in range(len(let))]

            except Exception as e:
                print('Warning in detecting %let')
                print('################################################################')
                print(e)
                print('################################################################')
                print(r'\n')
        return let

    #############################################################################################

    @staticmethod
    def find_libname(sas_code):
        libname_lst = []
        sas_code = sas_code.lower()
        pattern = r'\\nlibname .*?;| libname .*?;'
        libname = re.findall(pattern, sas_code)
        
        libname_idx = [a.start(0) for a in re.finditer(pattern, sas_code)]
        engines = ['ACCESS','CEDA','CRSP','CSV','DB2','EXCEL','HBASE','HBASE','HBASE','JDBC','JDBC','MDDB',
                'POSTGRES','REDIS','SYBASE','XML','cvp','v9','BASE','SAS7BDAT','ORACLE','ODBC','PCFILES',
                'SPDE','SQLSVR','TERADATA','HADOOP','CAS',
                'OLEDB','JSON','SNOW','XLSX','XMLV2']

        for idx in range(len(libname)):

            try:
                #replace('"','').replace("'",'').
                f_txt = libname[idx].strip().replace(';','').split(' ')

                if len(f_txt) > 1 and f_txt[1] in ['clear', 'list', '_all_list', '_all_clear']:
                    continue
                if len(f_txt) > 2 and f_txt[2] in ['clear', 'list', '_all_list', '_all_clear']:
                    continue

                #detect engines based on a predefined list
                elif len(f_txt) > 2 and f_txt[2] in [a.lower() for a in engines]:
                    libname_lst.append({'type': 'libname',
                                        'original': libname[idx].replace('\\n',''),
                                        'key': f_txt[2],
                                        'value_0': [f_txt[3] if len(f_txt) > 3 else f_txt[2]],
                                        'value_1': [f_txt[3] if len(f_txt) > 3 else f_txt[2]],
                                        'index': libname_idx[idx]})
                
                #detect engines that are placed in macro variables
                elif len(f_txt) > 2 and re.match(r"^&.*", f_txt[2]):
                    libname_lst.append({'type': 'libname',
                                        'original': libname[idx].replace('\\n',''),
                                        'key': 'unknown',
                                        'value_0': [f_txt[3] if len(f_txt) > 3 else f_txt[2]],
                                        'value_1': [f_txt[3] if len(f_txt) > 3 else f_txt[2]],
                                        'index': libname_idx[idx]})

                #detect implicit use of BASE engine
                elif len(f_txt) > 2 and f_txt[2] not in [a.lower() for a in engines]:
                    libname_lst.append({'type': 'libname',
                                        'original': libname[idx].replace('\\n',''),
                                        'key': 'base',
                                        'value_0': [f_txt[2]],
                                        'value_1': f_txt[2].replace('(','').replace(')','').split(','),
                                        'index': libname_idx[idx]})
            except Exception as e:
                print('Warning in finding libname!')
                print('################################################################')
                print(e)
                print('################################################################')
                print(r'\n')

        return libname_lst

    #############################################################################################

    @staticmethod
    def find_filename(sas_code):
        filename_lst = []
        sas_code = sas_code.lower()
        filename = [a.strip() for a in re.findall(r'\\nfilename .*?;| filename .*?;', sas_code)]
        filename_idx = [a.start(0) for a in re.finditer(r'\\nfilename .*?;| filename .*?;', sas_code)]
        device_types = ['ACTIVEMQ','AZURE','CATALOG','DATAURL','DISK','DUMMY','DUMMY','FTP','GTERM','HADOOP','HADOOP',
                        'HADOOP','PLOTTER','PRINTER','S3','SFTP','SOCKET','TAPE','TEMP','TERMINAL','UPRINTER','URL','WEBDAV','WEBDAV']

        for idx in range(len(filename)):

            try:
                f_txt = filename[idx].strip().replace('\\n','').replace('"','').replace("'",'').replace(';','').split(' ')

                if len(f_txt) > 1 and f_txt[1] in ['clear', 'list', '_all_list', '_all_clear']:
                    continue
                if len(f_txt) > 2 and f_txt[2] in ['clear', 'list', '_all_list', '_all_clear']:
                    continue
                elif len(f_txt) > 2 and f_txt[2] in [a.lower() for a in device_types]:
                    filename_lst.append({'type': 'filename',
                                         'original': filename[idx].strip().replace('\\n',''),
                                         'key': f_txt[1],
                                         'value_0': [f_txt[2]],
                                         'value_1': [f_txt[3] if len(f_txt) > 3 else f_txt[2]],
                                         'index': filename_idx[idx]})

                elif len(f_txt) > 2 and f_txt[2] not in [a.lower() for a in device_types]:
                    filename_lst.append({'type': 'filename',
                                         'original': filename[idx].strip().replace('\\n',''),
                                         'key': f_txt[1],
                                         'value_0': [f_txt[2]],
                                         'value_1': [f_txt[2]],
                                         'index': filename_idx[idx]})

            except Exception as e:
                print('Warning in finding filename!')
                print('################################################################')
                print(e)
                print('################################################################')
                print(r'\n')

        return filename_lst

    #############################################################################################

    @staticmethod
    def find_proc(sas_code):
        proc = re.findall(r'proc .*?;', sas_code.lower(), re.DOTALL)
        proc = [a.split(' ')[1].replace(';','') for a in proc]
        return proc

    #############################################################################################

    @staticmethod
    def find_create_table(sas_code):
        create_tbl_lst = []
        sas_code = sas_code.lower()
        sql     = re.findall(r'create table .*? |data = .*? |out = .*? |data .*? | out = .*? ',sas_code,re.DOTALL)
        sql_idx = [a.start(0) for a in re.finditer(r'create table .*? |data = .*? |out = .*? |data .*? | out = .*? ',sas_code,re.DOTALL)]

        for idx in range(len(sql)):
            try:
                create_tbl_lst.append({'type': 'create_table',
                                       'original': sql[idx],
                                       'key': '',
                                       'value_0': [sql[idx].strip().split(' ')[-1]],
                                       'value_1': [sql[idx].strip().split(' ')[-1]],
                                       'index': sql_idx[idx]})
            except Exception as e:
                print('Warning in detecting create table!')
                print('################################################################')
                print(e)
                print('################################################################')
                print(r'\n')

        return create_tbl_lst

    #############################################################################################

    @staticmethod
    def find_select_from_table(sas_code):
        select_tbl_lst = []
        sas_code = sas_code.lower()
        sql = re.findall(r'from .*? |join .*? |set = .*? |set .*? |infile .*? |datafile .*? ', sas_code, re.DOTALL)
        sql_idx = [a.start(0) for a in re.finditer(r'from .*? |join .*? |set = .*? |set .*? |infile .*? |datafile .*? ', sas_code, re.DOTALL)]

        for idx in range(len(sql)):
            try:
                select_tbl_lst.append({'type': 'select_from_table',
                                       'original': sql[idx],
                                       'key': '',
                                       'value_0': [sql[idx].strip().split(' ')[-1]],
                                       'value_1': [sql[idx].strip().split(' ')[-1]],
                                       'index': sql_idx[idx]})
            except Exception as e:
                print('Warning in detecting select from table!')
                print('################################################################')
                print(e)
                print('################################################################')
                print(r'\n')

        return select_tbl_lst

    #############################################################################################

    @staticmethod
    def find_x_commands(sas_code):
        sas_code = sas_code.lower()
        # x_command_pattern = r'(^|\s)x\s+["\'].*?["\'];'
        x_command_pattern = r'\bx\b\s+["\'].*?["\'];'
        # Using the regex pattern variable
        x_commands = re.findall(x_command_pattern, sas_code)
        x_idx = [a.start(0) for a in re.finditer(x_command_pattern, sas_code)]
        
        if len(x_commands) > 0:
            try:
                x_commands = [{ 'type'     : 'x_command',
                                'original' : x_commands[i].strip(),
                                'key'      : x_commands[i].strip()[2:-1].strip().replace('"','').split(' ')[0],
                                'value_0'  : [''],
                                'value_1'  : [''],
                                'index'    : x_idx[i]} 
                             for i in range(len(x_commands))]
            except Exception as e:
                print('Warning in detecting x-commands')
                print('################################################################')
                print(e)
                print('################################################################')
                print(r'\n')
        return x_commands

    #############################################################################################

    @staticmethod
    def get_operating_system():
        os_name = platform.system()
        return os_name

    #############################################################################################

    @staticmethod
    def is_valid_linux(s):
        #general
        if '/\\' in s or '\\/' in s:
            return False
        
        if s.startswith('\\n'):
            return False
        
        forbidden_characters = ['&','@', ';', ':', '*', '?', '!', '<', '>', '%', '|', '(', ')','"',',',"'",'+','=']

        #forward slash
        pattern1 = r'^(/[^/]+)+$'
        match = re.match(pattern1, s)
        if match is not None:
            pattern = '[' + re.escape(''.join(forbidden_characters)) + ']'
            if re.search(pattern, s):
                return False
            else:
                return True

    #############################################################################################

    @staticmethod
    def is_valid_windows(s):
        #general
        if '/\\' in s or '\\/' in s:
            return False
        
        if s.startswith('\\n'):
            return False
        
        forbidden_characters = ['&','@', ';', '*', '?', '!', '<', '>', '%', '|', '(', ')','"',',',"'",'+','=']
        
        #local pattern
        pattern1 = r"^([A-Za-z]:\\\\|[A-Za-z]:\\|\\\\)([^\\]+\\)*[^\\]*$"
        match = re.match(pattern1, s)
        if match is not None:
            pattern = '[' + re.escape(''.join(forbidden_characters)) + ']'
            if re.search(pattern, s):
                return False
            else:
                return True

    #############################################################################################

    @staticmethod
    def is_valid(s,operating_system=None):
		if operating_system:
			if operating_system == 'Windows':
				return Public_functions.is_valid_windows(s)
			if operating_system == 'Linux':
				return Public_functions.is_valid_linux(s)
		else:
			a = Public_functions.is_valid_windows(s)
			b = Public_functions.is_valid_linux(s)
			return a or b


    #############################################################################################

    @staticmethod
    def find_hard_code(sas_code):
        #operating_system = Public_functions.get_operating_system()
        pattern = r'(["\'])(.*?)\1'
        hrd = []
        try:
            all_hrd = re.findall(pattern, sas_code)
            hrd = [a for b in all_hrd for a in b if a != "'" and a != '"' and Public_functions.is_valid(a) ]
        except Exception as e:
            print('Warning in find_hard_code!')
            print('################################################################')
            print(e)
            print('################################################################')
            print(r'\n')
        return hrd

    #############################################################################################

    @staticmethod
    def replace_vars(sas_code, let_lst, filename_lst, libname_lst, inc_lst, create_tbl_lst, select_from_tbl_lst):

        try:
            full_list = [let_lst, filename_lst, libname_lst, inc_lst, create_tbl_lst, select_from_tbl_lst]
            lst_all     = [b for a in full_list for b in a]
            lst_all     = sorted(lst_all, key=lambda a: a['index'])
            lst_final   = []

            for item in lst_all:
                lst_replace = [b for a in [let_lst, filename_lst, libname_lst] for b in a if b['index'] < item['index']]
                lst_replace = sorted(lst_replace, key=lambda a: a['index'], reverse=True)
                for rep_item in lst_replace:
                    for ii in range(len(item['value_0'])):
                        if   rep_item['type'] == 'let':
                            item['value_0'][ii] = Public_functions.replace_txt(item['value_0'][ii],'&{0}.'.format(rep_item['key']), rep_item['value_0'][0])
                            item['value_0'][ii] = Public_functions.replace_txt(item['value_0'][ii],'&{0}'.format(rep_item['key']) , rep_item['value_0'][0])
                            # item['value_0'][ii] = item['value_0'][ii].replace('&{0}.'.format(rep_item['key']), rep_item['value_0'][0]).replace('&{0}'.format(rep_item['key']), rep_item['value_0'][0])
                        elif rep_item['type'] in ('filename','libname'):
                            item['value_0'][ii] = Public_functions.replace_txt(item['value_0'][ii], rep_item['key'], rep_item['value_1'][0])
                            # item['value_0'][ii] = item['value_0'][ii].replace(rep_item['key'], rep_item['value_1'][0])

                    for ii in range(len(item['value_1'])):
                        if   rep_item['type'] == 'let':
                            item['value_1'][ii] = Public_functions.replace_txt(item['value_1'][ii], '&{0}.'.format(rep_item['key']), rep_item['value_0'][0])
                            item['value_1'][ii] = Public_functions.replace_txt(item['value_1'][ii], '&{0}'.format(rep_item['key']), rep_item['value_0'][0])
                            # item['value_1'][ii] = item['value_1'][ii].replace('&{0}.'.format(rep_item['key']), rep_item['value_0'][0]).replace('&{0}'.format(rep_item['key']), rep_item['value_0'][0])
                        elif rep_item['type'] in ('filename', 'libname'):
                            item['value_1'][ii] = Public_functions.replace_txt(item['value_1'][ii], rep_item['key'], rep_item['value_1'][0])
                            # item['value_1'][ii] = item['value_1'][ii].replace(rep_item['key'], rep_item['value_1'][0])

                lst_final.append(item)

            let_lst, filename_lst, libname_lst, inc_lst, create_tbl_lst, select_from_tbl_lst = [],[],[],[],[],[]
            for item in lst_final:
                if item['type'] == 'let':
                    let_lst.append(item)
                elif item['type'] == 'filename':
                    filename_lst.append(item)
                elif item['type'] == 'libname':
                    libname_lst.append(item)
                elif item['type'] == 'include':
                    inc_lst.append(item)
                elif item['type'] == 'create_table':
                    create_tbl_lst.append(item)
                elif item['type'] == 'select_from_table':
                    select_from_tbl_lst.append(item)

        except:
            print('Minor error in replacing variables!')

        return let_lst, filename_lst, libname_lst, inc_lst

    #############################################################################################

    @staticmethod
    def find_code_blocks(sas_code):
        try:
            sas_code = sas_code.lower()
            txt1_idx = [(a.start(0), a.end(0)) for a in re.finditer(r'\\n%macro .*?%mend', sas_code.lower(), re.DOTALL)]
            txt2_idx = [(a.start(0), a.end(0)) for a in re.finditer(r'\\ndata .*?run;|\\ndata .*?quit;'    , sas_code.lower(), re.DOTALL)]
            txt3_idx = [(a.start(0), a.end(0)) for a in re.finditer(r'\\nproc .*?run;|\\nproc .*?quit;', sas_code.lower(), re.DOTALL)]
            txt4_idx = [(a.start(0), a.end(0)) for a in re.finditer(r'\\n%include .*?;'  , sas_code.lower(), re.DOTALL)]
            txt_idx  = [a for b in [txt1_idx,txt2_idx,txt3_idx,txt4_idx] for a in b]
            txt_idx  = Public_functions.find_inclusive_intervals(txt_idx)
            if txt_idx == []:
                txt_idx = [[0,len(sas_code)]]
            txt_idx = [a for b in txt_idx for a in b]
            if min(txt_idx) > 0:
                txt_idx.insert(0,0)
            if max(txt_idx) < len(sas_code):
                txt_idx.extend([len(sas_code)])
            blck_lst = []
            for i in range(1,len(txt_idx)):
                blc_start = ' '.join(sas_code[txt_idx[i-1]:txt_idx[i]].replace(r"\\n" ,"").replace(r"\n" ,"").replace(r"\t" ,"").replace(r"\tab" ,"").strip().split(' ')[0:2])
                blc_start = blc_start[0:min(50,len(blc_start))]
                blc_end = sas_code[txt_idx[i-1]:txt_idx[i]].replace(r"\\n" ,"").replace(r"\n" ,"").replace(r"\t" ,"").replace(r"\tab" ,"").strip().split(' ')[-1]
                blc_end = blc_end[0:min(50,len(blc_end))]
                blck_lst.append({'block': [blc_start, blc_end], 'block_idx': [txt_idx[i-1],txt_idx[i]]})

            blck_lst = [a for a in blck_lst if a['block'] != ['', '']]
        except Exception as e:
            blck_lst = []
            print('Warning in detecting blocks!')
            print('################################################################')
            print(e)
            print('################################################################')
            print(r'\n')

        return blck_lst

    #############################################################################################

    @staticmethod
    def find_called_programs(sas_code):
        called_prg_lst = []
        called_prg_lst = list(set(called_prg_lst))
        called_prg = ";".join(i.strip() for i in called_prg_lst)
        return called_prg_lst, called_prg
