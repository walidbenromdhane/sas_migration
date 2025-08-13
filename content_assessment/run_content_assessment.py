from content_assessment import ContentAssessementExecution
import platform, os, traceback


if platform.system() == "Windows":
    main_directory_sasfiles_list = [r'C:\Users\h163ejg\Desktop\Work\test\server\input\001_darc']
    main_output_directory = r'C:\Users\h163ejg\Desktop\Work\test\server\output\001_darc'

            
if platform.system() == "Linux":
    main_directory_sasfiles_list = ['/sasdata/a66/EY/state0/0806/']
    main_output_directory = '/sasdata/a66/EY/ey_ca_output/darp/recouvrement/'

cae = ContentAssessementExecution(main_directory_sasfiles_list, main_output_directory)
cae.run()