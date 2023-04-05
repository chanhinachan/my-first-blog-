S = input()

if len(S)<3:
    S = int(S)
    L = [8,16,61,24,42,32,23,48,84,56,65,64,46,72,27,88,96,69]
    if S in L:
        print("Yes")
    else:
        print("No")


else:
    S = list(S)
    import collections
    cnt = collections.Counter(S)
    
    multi_8 = list(range(112,1000,8))
    
    flag = True
    
    for m in multi_8:
        C = collections.Counter(list(str(m)))
        for c in C:
            if C[c]>cnt[c]:
                flag = False
                break
        if flag == True:
            print("Yes")
            exit()
            
    print("No")