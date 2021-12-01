# -*- coding: utf-8-*-

import xlrd
import openpyxl
import xlwt
import os
from xlutils.copy import copy
from math import log10 as log


def takeSecond(elem):
    return elem[1]


# 读取excel表
wk_result = xlrd.open_workbook('Excel_Result.xls', formatting_info=True)
wk_official = xlrd.open_workbook('Excel_Official.xls')
wk_threshold =xlrd.open_workbook('Excel_Threshold.xlsx')


wt_all = wk_result.sheet_by_index(0)
wt_th = wk_threshold.sheet_by_index(0)


wb = copy(wk_result)
sheet = wb.get_sheet(0)   # wt_all


rows_all = wt_all.nrows
rows_th = wt_th.nrows


cf_limit = 0.05
bw_limit = 0.1
am_limit = 10

index_true = []
index_all = []

def usd_official (usd_index, official_index, row_number):

    wt_usd = wk_result.sheet_by_index(usd_index)
    wt_off = wk_official.sheet_by_index(official_index)

    rows_usd = wt_usd.nrows
    rows_off = wt_off.nrows

    for i in range(1, rows_usd):

        # Frequency
        cf_usd = float(wt_usd.cell_value(i, 0))

        # Bandwidth
        bw_usd = float(wt_usd.cell_value(i, 1))

        cf_error = abs(cf_all - cf_usd) / cf_usd
        bw_error = abs(bw_all - bw_usd) / bw_usd

        if cf_error < cf_limit and bw_error < bw_limit:

            error_list = []

            for j in range(1, rows_off):
                pair = []
                cf_select = float(wt_off.cell_value(j, 1))
                cf_select_error = abs(cf_all - cf_select) / cf_select

                pair.append(j)
                pair.append(cf_select_error)

                error_list.append(pair)
                error_list= sorted(error_list, key=(lambda x: x[1]))

            if error_list[0][1] < cf_limit:

                sheet.write(row_number, 4, "True")
                index_true.append(row_number)
                index_all.append(row_number)

                for k in range(5, 10):
                    sheet.write(row_number, k, wt_off.cell(error_list[0][0], k-5).value)

            else:
                sheet.write(row_number, 4, "False")

                index_all.append(row_number)

            break


for i in range(1, rows_all):

    row = wt_all.row_values(i)

    cf_all = float(wt_all.cell_value(i, 0))
    bw_all = float(wt_all.cell_value(i, 1))
    am_all = float(wt_all.cell_value(i, 2))

    count = 1

    # FM
    if cf_all >= 87  and cf_all <= 108:

        wt_usd = wk_result.sheet_by_index(1)
        rows_usd = wt_usd.nrows

        for j in range(1, rows_usd):
            # Frequency
            cf_usd = float(wt_usd.cell_value(j, 0))

            # Bandwidth
            bw_usd = float(wt_usd.cell_value(j, 1))

            cf_error = abs(cf_all - cf_usd) / cf_usd
            bw_error = abs(bw_all - bw_usd) / bw_usd

            if cf_error < cf_limit and bw_error < bw_limit:
                sheet.write(i, 4, "True")
                index_true.append(i)
                index_all.append(i)
                sheet.write(i, 5, "FM")
                sheet.write(i, 6, "87-108")
                sheet.write(i, 7, "256KHz")
                break


    # GSM
    elif cf_all >= 930  and cf_all <= 960:
        usd_official(1, 0, i)


    # WIDE  3G/4G/5G
    elif (cf_all >= 690 and cf_all <= 1000 and bw_all > 5000)\
         or (cf_all >= 1820 and cf_all <= 2700 and bw_all > 5000) \
        or (cf_all >= 3350 and cf_all <= 3650 and bw_all > 5000) \
         or (cf_all >= 4350 and cf_all <= 5100 and bw_all > 5000):
        usd_official(2, 4, i)


    else:
        number = int((cf_all*1E6 - 20000000)/6835.94)
        am_th = float(wt_th.cell_value(number,1))
        am_diff = abs(am_all - am_th)
        if am_diff > am_limit:
            sheet.write(i, 4, "False")

            index_all.append(i)

print(index_true)
print(index_all)

wb.save('Excel_Result.xls')

