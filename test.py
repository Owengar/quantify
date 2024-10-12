lis = [1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6]


where_lis = [False for j in lis]
if lis.count(2) > 1:
    first_index = lis.index(1)
    second_index = lis.index(1, first_index+1)
    index_diff = second_index-first_index
    print(index_diff)
    print((len(lis)//index_diff))
    for i in range(len(lis)//index_diff):
        where_lis[first_index + (index_diff * i)] = 1


print(where_lis)