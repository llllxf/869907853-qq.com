import numpy as np

n = int(input())
arr_1 = []
arr_index1 = []
arr_2 = []
arr_index2 = []
for i in range(n):
    hang = input()
    num = int(hang.split(" ")[0])
    kind = int(hang.split(" ")[1])
    #print(num,kind)
    if kind == 1:
        arr_1.append(num)
        arr_index1.append(i+1)
    else:
        arr_2.append(num)
        arr_index2.append(i+1)
#print(arr_1,arr_2)

a_s_1 = np.argsort(arr_1)[::-1]

a_s_2 = np.argsort(arr_2)[::-1]

most_1 = 0
most_2 = 0
if len(arr_1)>=3:
    most_1 = arr_1[a_s_1[0]]+arr_1[a_s_1[1]]+arr_1[a_s_1[2]]
if len(arr_2)>=3:
    most_2 = arr_2[a_s_2[0]]+arr_2[a_s_2[1]]+arr_2[a_s_2[2]]

if most_1 > most_2:
        print(str(arr_index1[a_s_1[2]]) + " " + str(arr_index1[a_s_1[1]]) + " " + str(arr_index1[a_s_1[0]]))
        print("1")
        print(most_1)
elif most_1 == most_2:
        print(str(arr_index1[a_s_1[2]]) + " " + str(arr_index1[a_s_1[1]]) + " " + str(arr_index1[a_s_1[0]]))
        print("1")
        print(most_1)
        print(str(arr_index2[a_s_2[2]]) + " " + str(arr_index2[a_s_2[1]]) + " " + str(arr_index2[a_s_2[2]]))
        print("2")
        print(most_2)
else:
        print(str(arr_index2[a_s_2[2]]) + " " + str(arr_index2[a_s_2[1]]) + " " + str(arr_index2[a_s_2[0]]))
        print("2")
        print(most_2)
















