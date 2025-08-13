from check_encodings import ConvertSasCodeUtf

source_folder = "//sasdata/a66/EY/statel/1209/DAS_EQUIFAX/"
# source_folder = "C:\\Users\\hl63ejg\\Desktop\\Work\\test\\server\\output\\statel\\0729\\"
output_folder = "//sasdata/a66/EY/DAS Equifax/"
report_name = "encoding_convert_report.csv"

trans_utf1 = ConvertSasCodeUtf(path=source_folder, output=output_folder)

report = trans_utf1.run()
report.to_csv(output_folder+f"\\{report_name}")
