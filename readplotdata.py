import xlrd

workbook = xlrd.open_workbook('Excel_Result.xls')
sheet1 = workbook.sheet_by_index(0)
col_data = sheet1.col_values(0)
print(col_data)

cf = []