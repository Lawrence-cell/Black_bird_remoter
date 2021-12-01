import math
import copy
import pickle
import os
import time

def read_energy_history_file(path):
    pass


def Vpp_to_dBm(vpp):
    return 10 * math.log10(vpp * 0.5) - 10 * math.log10(50) + 30


# 添加FM信号的判决规则,提取关键信息保存到信号列表,并在rest_index_lists列表中去掉此信号的索引
def extract_valid_FM_index_and_signal(lists_after_usd_filter,rest_index_lists):
    FM_signal_lists = []
    tmp_lists = copy.copy(rest_index_lists)
    for i in tmp_lists:
        one_item = lists_after_usd_filter[i]
        # 中心频率处在FM频带范围内，且带宽不低于50kHz，不高于300kHz，则认为是FM信号
        flag1 = one_item[0] > 87e6 and one_item[0] < 108e6
        flag2 = one_item[1] > 50e3 and one_item[1] < 350e3
        if(flag1 and flag2):
            rest_index_lists.remove(i)
            FM_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'FM调频广播 87~108 MHz'])
    return FM_signal_lists,rest_index_lists
        

#添加P-GSM 900信号群，保存列表中的下标，提取关键信息保存到信号列表
# 934~948M 中国移动
# 1825~1830M 中国移动
# 949~954M 中国联通
# 1830~1880M 可能存在联通GSM，通过带宽判断
def extract_valid_GSM_index_and_signal(lists_after_usd_filter,rest_index_lists):

    GSM_signal_lists = []
    tmp_lists = copy.copy(rest_index_lists)

    bw_limitation = [150e3,350e3]
    cf_limitation = 0.25

    for i in tmp_lists:
        one_item = lists_after_usd_filter[i]

        if( one_item[0] > 935e6 and one_item[1] < 948e6 ):
            decimals_part,int_part = math.modf((one_item[0]-935e6)/200e3)
            flag2 =  decimals_part < cf_limitation  #中心频率对200k取余后与门限比较
            flag3 = one_item[1]>bw_limitation[0] and one_item[1]<bw_limitation[1]    # 带宽的范围限制
            if(flag2 and flag3):
                rest_index_lists.remove(i)
                GSM_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'GSM-900: {:.1f}M, ARFCN: {:.0f}，中国移动GSM'.format(int_part*200e3+935e6,int_part)])
        
        elif( one_item[0] > 1825e6 and one_item[1] < 1830e6 ):
            decimals_part,int_part = math.modf((one_item[0]-1805.2e6)/200e3)
            flag2 =  decimals_part < cf_limitation  #中心频率对200k取余后与门限比较
            flag3 = one_item[1]>bw_limitation[0] and one_item[1]<bw_limitation[1]    # 带宽的范围限制
            if(flag2 and flag3):
                rest_index_lists.remove(i)
                GSM_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'GSM-1800: {:.1f}M, ARFCN: {:.0f}，中国移动GSM'.format(int_part*200e3+935e6,int_part+512)])

        elif( one_item[0] > 949e6 and one_item[1] < 954e6 ):
            decimals_part,int_part = math.modf((one_item[0]-935e6)/200e3)
            flag2 =  decimals_part < cf_limitation  #中心频率对200k取余后与门限比较
            flag3 = one_item[1]>bw_limitation[0] and one_item[1]<bw_limitation[1]    # 带宽的范围限制
            if(flag2 and flag3):
                rest_index_lists.remove(i)
                GSM_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'GSM-900: {:.1f}M, ARFCN: {:.0f}，中国联通GSM'.format(int_part*200e3+935e6,int_part)])
        
        elif( one_item[0] > 1803e6 and one_item[1] < 1810e6 ):
            decimals_part,int_part = math.modf((one_item[0]-1805.2e6)/200e3)
            flag2 =  decimals_part < cf_limitation  #中心频率对200k取余后与门限比较
            flag3 = one_item[1]>bw_limitation[0] and one_item[1]<bw_limitation[1]    # 带宽的范围限制
            if(flag2 and flag3):
                rest_index_lists.remove(i)
                GSM_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'GSM-1800: {:.1f}M, ARFCN: {:.0f}，中国移动GSM'.format(int_part*200e3+935e6,int_part)])

        elif( one_item[0] > 1830e6 and one_item[1] < 1880e6 ):
            decimals_part,int_part = math.modf((one_item[0]-1805.2e6)/200e3)
            flag2 =  decimals_part < cf_limitation  #中心频率对200k取余后与门限比较
            flag3 = one_item[1]>bw_limitation[0] and one_item[1]<bw_limitation[1]    # 带宽的范围限制
            if(flag2 and flag3):
                rest_index_lists.remove(i)
                GSM_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'GSM-1800: {:.1f}M, ARFCN: {:.0f}，中国联通GSM'.format(int_part*200e3+935e6,int_part+512)])
        
    return GSM_signal_lists,rest_index_lists
                           

def extract_valid_LTE_index_and_signal(lists_after_usd_filter,rest_index_lists):
    LTE_signal_lists = []
    tmp_lists = copy.copy(rest_index_lists)

    bw_limitation = [5e6,10e6]
    cf_limitation = 300e3

    for i in tmp_lists:
        one_item = lists_after_usd_filter[i]

        if(  abs(one_item[0] - 939e6) <  cf_limitation ):
            if(one_item[1]>4e6 and one_item[1]<11e6):
                rest_index_lists.remove(i)
                LTE_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'band8, 中国移动FDD-LTE'])

        elif(  abs(one_item[0] - 1815e6) <  cf_limitation ):
            if(one_item[1]>4e6 and one_item[1]<21e6):
                rest_index_lists.remove(i)
                LTE_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'band3, 中国移动FDD-LTE'])

        elif(  abs(one_item[0] - 2017.5e6) <  cf_limitation ):
            if(one_item[1]>4e6 and one_item[1]<15e6):
                rest_index_lists.remove(i)
                LTE_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'band34, 中国移动TD-LTE'])

        elif(  one_item[0] >1880e6 and one_item[0]<1920e6):
            if(one_item[1]>4e6 and one_item[1]<21e6):
                rest_index_lists.remove(i)
                LTE_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'band39, 中国移动TD-LTE'])

        elif(  one_item[0] >2320e6 and one_item[0]<2370e6):
            if(one_item[1]>15e6 and one_item[1]<21e6):
                rest_index_lists.remove(i)
                LTE_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'band40, 中国移动TD-LTE室内频点'])

        elif(  one_item[0] >1830e6 and one_item[0]<1880e6):
            if(one_item[1]>4e6 and one_item[1]<21e6):
                rest_index_lists.remove(i)
                LTE_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'band3, 联通/电信共享,FDD-LTE'])

        elif(  one_item[0] >2110e6 and one_item[0]<2155e6):
            if(one_item[1]>4e6 and one_item[1]<21e6):
                rest_index_lists.remove(i)
                LTE_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'band1, 联通/电信共享,FDD-LTE'])

        elif(  one_item[0] >2300e6 and one_item[0]<2320e6):
            if(one_item[1]>4e6 and one_item[1]<21e6):
                rest_index_lists.remove(i)
                LTE_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'band40, 联通TD-LTE'])

        elif(  one_item[0] >869e6 and one_item[0]<880e6):
            if(one_item[1]>4e6 and one_item[1]<21e6):
                rest_index_lists.remove(i)
                LTE_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'band5, 电信FDD-LTE'])

    return LTE_signal_lists,rest_index_lists


def extract_valid_NR_index_and_signal(lists_after_usd_filter,rest_index_lists):
    NR_signal_lists = []
    tmp_lists = copy.copy(rest_index_lists)

    for i in tmp_lists:
        one_item = lists_after_usd_filter[i]

        if( one_item[0] >2515e6 and one_item[0]<2615e6 ):
            if(one_item[1]>40e6 and one_item[1]<100e6):
                rest_index_lists.remove(i)
                NR_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'n41, 中国移动-5G'])
        elif( one_item[0] >4800e6 and one_item[0]<4900e6 ):
            if(one_item[1]>40e6 and one_item[1]<100e6):
                rest_index_lists.remove(i)
                NR_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'n79, 中国移动-5G'])
        elif( one_item[0] >758e6 and one_item[0]<788e6 ):
            if(one_item[1]>20e6 and one_item[1]<30e6):
                rest_index_lists.remove(i)
                NR_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'n28, 中国移动/广电共享-5G'])
        elif( one_item[0] >3300e6 and one_item[0]<3400e6 ):
            if(one_item[1]>40e6 and one_item[1]<100e6):
                rest_index_lists.remove(i)
                NR_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'n78, 联通/电信/广电共享-5G，仅室内'])
        elif( one_item[0] >3400e6 and one_item[0]<3600e6 ):
            if(one_item[1]>40e6 and one_item[1]<100e6):
                rest_index_lists.remove(i)
                NR_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'n78, 联通/电信共享-5G'])
        elif( one_item[0] >4900e6 and one_item[0]<4960e6 ):
            if(one_item[1]>30e6 and one_item[1]<60e6):
                rest_index_lists.remove(i)
                NR_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'n79, 广电-5G'])

    return NR_signal_lists,rest_index_lists


def extract_valid_IMT_3G_index_and_signal(lists_after_usd_filter,rest_index_lists):
    IMT_3G_signal_lists = []
    tmp_lists = copy.copy(rest_index_lists)

    for i in tmp_lists:
        one_item = lists_after_usd_filter[i]
        if( one_item[0] >869e6 and one_item[0]<880e6 ):
            if(one_item[1]>2e6 and one_item[1]<5e6):
                rest_index_lists.remove(i)
                IMT_3G_signal_lists.append( [one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'中国电信, CDMA2000']  )
    
    return IMT_3G_signal_lists,rest_index_lists


def extract_unknown_index_and_signal(lists_after_usd_filter,rest_index_lists):
    unknown_signal_lists = []
    for i in rest_index_lists:
        one_item = lists_after_usd_filter[i]
        unknown_signal_lists.append([one_item[0],one_item[1],Vpp_to_dBm(one_item[9]),'无备案信息'])
    
    return unknown_signal_lists


###################################
###################################


def whether_in_wide_range(cf,wide_band_freq_range):
    for i in wide_band_freq_range:
        if( cf>i[0] and cf<i[1] ):
            return True
    return False

def readHisFile():
    
    # 加载仅能量判决的Energy_history
    this_projectPath = os.getcwd()
    path = this_projectPath + '\\stateFile\\raw_Energy_history.his'
    with open(path, 'r') as f:
        cont = f.readlines()
        raw_energy_signals = cont[9:]  # 每一行即是一条信号记录
    
    processed_signals = []
    path = this_projectPath + '\\stateFile\\signalDatabase.his'
    with open(path, 'r') as f:
        cont = f.readlines()
        raw_signals = cont[1:]  # 每一行即是一条信号记录
           

    # print(raw_signals)
    # print('***********************************************************************')


    raw_energy_signals_list = []
    for i in raw_energy_signals:
        tmp = [float(v.strip()) for v in i.split(',')]
        raw_energy_signals_list.append(tmp)

    raw_signalsDB_list = []
    for i in raw_signals:
        tmp = [v.strip() for v in i.split(',')]
        raw_signalsDB_list.append(tmp)
    i = 0
    while i < len(raw_signalsDB_list) - 1 :
        raw_signalsDB_list[i].extend(raw_signalsDB_list[i+1])
        processed_signals.append(raw_signalsDB_list[i])
        i = i + 2
    
    
    


    all_energy = []
    # 过滤，把滤除噪声后的剩余信号添加到unknown_signal_list列表中
    for sig in raw_energy_signals_list:
    #     pos_index = int((sig[0]-start_freq)/interval_freq)
    #     noise_baseline_power =  threshold_power_dBm_lists[pos_index]
    #     if(  Vpp_to_dBm(sig[10]) - Vpp_to_dBm(noise_baseline_power) > 10 ):
    #频率 带宽 功率 intercepts occupancy
        all_energy.append([sig[0],sig[1],Vpp_to_dBm(sig[9]),sig[4],sig[15]])
    
    
    usd_showContent = []
    modrec_showContent = []
    for sig in processed_signals:
        if sig[5] == 'Universal':
            timeArray = time.localtime(float(sig[3]))  # 秒数
            timeCurrent = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            usd_showContent.append([timeCurrent, sig[2], sig[15], sig[17]])
    #(['时间','中心频率', '带宽', '调制方式'])        
        else:
            timeArray = time.localtime(float(sig[3]))  # 秒数
            timeCurrent = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            if sig[26] == '-1':
                modrec_showContent.append([timeCurrent, sig[2], sig[15], sig[17], sig[4], '--', '--' ])
            else:
                # s = ' {name1} {name2}/{name3}'.format(name1 = sig[26], name2= sig[27], name3= sig[28] )
                s = ' {name1} %'.format(name1 = sig[26])
                modrec_showContent.append([timeCurrent, sig[2], sig[15], sig[17], sig[4], sig[21], s])            
    # u, u, 频率, 时间, u, duration, type, u, u, u, u, u, u, u, u, invalid, bandwidth, u, description
    # u, u,  SNR, 
    #(['时间','中心频率', '带宽', '调制方式','Duration','SNR', 'Confidence'])
    # print(all_energy)
    # print('***********************************************************************')
    # print(usd_showContent)
    # print('***********************************************************************')
    # print(modrec_showContent)
    # global_sig_var[0] = all_energy
    # global_sig_var[1] = global_sig_var[1].extend(usd_showContent)
    # global_sig_var[2] = global_sig_var[2].extend(modrec_showContent)
    return [all_energy, usd_showContent, modrec_showContent]
    
    

#从his文件中读取信号值
def generate_signal_list():

    energy_lists_with_level_mode = []
    energy_lists_with_auto_mode = []

    # 加载仅能量判决的Energy_history
    this_projectPath = os.getcwd()
    path = this_projectPath + '\\stateFile\\raw_Energy_history.his'
    with open(path, 'r') as f:
        cont = f.readlines()
        raw_energy_signals = cont[9:]  # 每一行即是一条信号记录

    raw_energy_signals_list = []
    for i in raw_energy_signals:
        tmp = [float(v.strip()) for v in i.split(',')]
        raw_energy_signals_list.append(tmp)


    # 加使用了USD的Energy_history
    path = this_projectPath + '\\stateFile\\auto_USD_Energy_history.his'
    with open(path, 'r') as f:
        cont = f.readlines()
        usd_signals = cont[9:]  # 每一行即是一条信号记录

    usd_signals_list = []
    for i in usd_signals:
        tmp = [float(v.strip()) for v in i.split(',')]
        usd_signals_list.append(tmp)


    items_meet_USD_requirements = []

    items_not_meet_USD_requirements = []


    cf_error_degree_limitation = 50000  # 中心频率相差50kHz以内，认为频率接近
    bw_error_degree_limitation = 0.1    # 带宽相差10%以内，认为带宽接近

    #Step1:先加载Auto模式下的纯能量检测结果，并去除其中位于宽带信号频段范围内的数据

    # 规定宽带信号的频率区间
    wide_band_freq_range = [(758e6,788e6),(869e6,880e6),(934e6,941.5e6),(1880e6,2370e6),(2400e6,2670e6),(3.3e9,3.6e9),(4800e6,4960e6)]

    # 这一块可优化的空间比较大，甚至可以使用多线程
    used_flag = 0
    for raw_item in raw_energy_signals_list:
        raw_item_cf = raw_item[0]  # 取频率和带宽
        if(whether_in_wide_range(raw_item_cf,wide_band_freq_range)):
            continue
        raw_item_bw = raw_item[1]
        for usd_item in usd_signals_list:
            usd_item_cf = usd_item[0]
            usd_item_bw = usd_item[1]
            cf_error_range = abs(raw_item_cf - usd_item_cf)
            bw_error_degree = abs(raw_item_bw - usd_item_bw)/usd_item_bw
            if(cf_error_range < cf_error_degree_limitation and bw_error_degree<bw_error_degree_limitation):
                items_meet_USD_requirements.append(raw_item)
                used_flag = 1
                break

        if(used_flag!=1):
            items_not_meet_USD_requirements.append(raw_item)
        else:
            used_flag = 0
        

    rest_index_lists = list(range(len(items_meet_USD_requirements)))

    FM_signal,rest_index_lists = extract_valid_FM_index_and_signal(items_meet_USD_requirements,rest_index_lists)
    GSM_signal,rest_index_lists = extract_valid_GSM_index_and_signal(items_meet_USD_requirements,rest_index_lists)
    unknown_signal_list = extract_unknown_index_and_signal(items_meet_USD_requirements,rest_index_lists)

    known_signal_dict = {}
    known_signal_dict['FM'] = FM_signal
    known_signal_dict['GSM'] = GSM_signal


    ######### 把那些不符合USD的信号集合中，类噪声信号去除，剩余部分添加进unknown_signal_list中
    
    
    path = this_projectPath + '\\stateFile\\raw_Threshold.his'
    with open(path,'r') as f:
        threshold_text = f.readlines()

    start_freq =  float( threshold_text[1].split(',')[1] )
    interval_freq =  float( threshold_text[1].split(',')[2] )
    total_num = int( threshold_text[1].split(',')[3] )
    # print(start_freq,interval_freq,total_num)

    threshold_power_dBm_lists = []
    for i in threshold_text[2:]:
        one_row_lists = i.strip().split(',')
        for j in one_row_lists:
            if(j!=''):
                threshold_power_dBm_lists.append(float(j))


    # 过滤，把滤除噪声后的剩余信号添加到unknown_signal_list列表中
    for sig in items_not_meet_USD_requirements:
        pos_index = int((sig[0]-start_freq)/interval_freq)
        noise_baseline_power =  threshold_power_dBm_lists[pos_index]
        if(  Vpp_to_dBm(sig[10]) - Vpp_to_dBm(noise_baseline_power) > 10 ):
            unknown_signal_list.append([sig[0],sig[1],Vpp_to_dBm(sig[9]),'无备案信息'])

        
    ## 此时把auto模式改成level模式，再导出一次USD的结果，对宽带信号进行检测
    # 加使用了USD的Energy_history
    path = this_projectPath + '\\stateFile\\level_USD_Energy_history.his'
    with open(path, 'r') as f:
        cont = f.readlines()
        level_usd_signals = cont[9:]  # 每一行即是一条信号记录

    wideband_signals_list = []
    for i in level_usd_signals:
        tmp = [float(v.strip()) for v in i.split(',')]
        if(whether_in_wide_range(tmp[0],wide_band_freq_range)):
            wideband_signals_list.append(tmp)

    rest_index_lists = list(range(len(wideband_signals_list)))
    LTE_signal,rest_index_lists = extract_valid_LTE_index_and_signal(wideband_signals_list,rest_index_lists)
    NR_signal,rest_index_lists = extract_valid_NR_index_and_signal(wideband_signals_list,rest_index_lists)
    IMT_3G_signal,rest_index_lists = extract_valid_IMT_3G_index_and_signal(wideband_signals_list,rest_index_lists)
    rest_unknown_signal_list = extract_unknown_index_and_signal(wideband_signals_list,rest_index_lists)


    known_signal_dict['LTE'] = LTE_signal
    known_signal_dict['NR'] = NR_signal
    known_signal_dict['IMT_3G'] = IMT_3G_signal
    unknown_signal_list.extend(rest_unknown_signal_list)

    konwn_sig = []
    konwn_sig.extend(LTE_signal)
    konwn_sig.extend(NR_signal)
    konwn_sig.extend(IMT_3G_signal)
    konwn_sig.extend(FM_signal)
    konwn_sig.extend(GSM_signal)
    
    all_sig = []
    all_sig.extend(konwn_sig)
    all_sig.extend(unknown_signal_list)
    all_sig.sort(key=lambda x:x[0])

    return [all_sig,konwn_sig,unknown_signal_list]