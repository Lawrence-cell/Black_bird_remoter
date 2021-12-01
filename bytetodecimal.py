# 二进制转十进制
i = "11111111111111111111111111111"
s = str(int(i, 2))
# print(s)


valid_list = []
decimal_num = 0
for i in range(29):
    valid_list.append('1')
str1=''.join(valid_list) 
print(str(int(str1, 2)))

i = 20.3555
s = str(i)
print(s)
