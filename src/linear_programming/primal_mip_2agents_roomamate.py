import mip
import numpy as np
import pickle

problem = mip.Model()

gs = problem.add_var_tensor((6,6,6,4,4),"gs",lb=0,ub=1)
ts = problem.add_var_tensor((6,6,6,4,4),"ts",lb=0)

problem.objective = mip.minimize(mip.xsum(ts.flatten()))

# succ[p][i] で選好 p で i より好きな人の一覧
# succ = [
#     [[],[0],[0,1]],# 0,1,2 -> 012の順で好き
#     [[],[0,2],[0]],# 0,2,1 -> 021の順で好き
#     [[1],[],[0,1]],# 1,0,2 -> 102の順で好き
#     [[2],[0,2],[]],# 1,2,0 -> 201の順で好き
#     [[1,2],[],[1]],# 2,0,1 -> 120の順で好き
#     [[1,2],[2],[]] # 2,1,0 -> 210の順で好き
# ]
succ = [
    [[],[0]],
    [[1],[]]
]

# succeq = [
#     [[0],[0,1],[0,1,2]],# 0,1,2
#     [[0],[0,1,2],[0,2]],# 0,2,1
#     [[0,1],[1],[0,1,2]],# 1,0,2
#     [[0,2],[0,1,2],[2]],# 1,2,0
#     [[0,1,2],[1],[1,2]],# 2,0,1
#     [[0,1,2],[1,2],[2]]# 2,1,0
# ]

succeq = [
    [[0],[0,1]],
    [[0,1],[1]]
]

# (0,1), (0,2), (1,2)
# change = [
#     [2,5,1], # 0,1,2
#     [4,3,0], # 0,2,1
#     [0,4,3], # 1,0,2
#     [5,1,2], # 1,2,0
#     [1,2,5], # 2,0,1
#     [3,0,4], # 2,1,0
# ]
change = [
    [1],
    [0]
]

for p1 in range(2):
    for p2 in range(2):
        for q1 in range(2):
            for q2 in range(2):
                ps = [p1,p2]
                qs = [q1,q2]

                # feasibility
                for w in range(2):
                    problem += mip.xsum(gs[p1,p2,q1,q2,w,:]) <= 1
                for f in range(2):
                    problem += mip.xsum(gs[p1,p2,q1,q2,:,f]) <= 1
                
                # stability
                for w in range(2):
                    for f in range(2):
                        constraint = ts[p1,p2,q1,q2,w,f] + gs[p1,p2,q1,q2,w,f]
                        for f_ in succ[ps[w]][f]:
                            constraint += gs[p1,p2,q1,q2,w,f_]
                        for w_ in succ[qs[f]][w]:
                            constraint += gs[p1,p2,q1,q2,w_,f]
                        problem += constraint >= 1
                
                # strategy proofness
                for w in range(2):
                    for p_ in range(2):
                        for f in range(2):
                            constraint = 0
                            flag = 0
                            for f_ in succeq[ps[w]][f]:
                                flag = 1
                                if w == 0:
                                    constraint += gs[p_,p2,q1,q2,w,f_] - gs[p1,p2,q1,q2,w,f_]
                                elif w == 1:
                                    constraint += gs[p1,p_,q1,q2,w,f_] - gs[p1,p2,q1,q2,w,f_]
                            if flag:
                                problem += constraint <= 0

                for f in range(2):
                    for q_ in range(2):
                        for w in range(2):
                            constraint = 0
                            flag = 0
                            for w_ in succeq[qs[f]][w]:
                                flag = 1
                                if f == 0:
                                    constraint += gs[p1,p2,q_,q2,w_,f] - gs[p1,p2,q1,q2,w_,f]
                                elif f == 1:
                                    constraint += gs[p1,p2,q1,q_,w_,f] - gs[p1,p2,q1,q2,w_,f]
                            if flag:
                                problem += constraint <= 0
                
                # anonymity
                for f in range(2):
                    problem += gs[p1,p2,q1,q2,0,f] == gs[p2,p1,change[q1][0],change[q2][0],1,f]
                    problem += gs[p1,p2,q1,q2,1,f] == gs[p2,p1,change[q1][0],change[q2][0],0,f]
                
                for w in range(2):
                    problem += gs[p1,p2,q1,q2,w,0] == gs[change[p1][0],change[p2][0],q2,q1,w,1]
                    problem += gs[p1,p2,q1,q2,w,1] == gs[change[p1][0],change[p2][0],q2,q1,w,0]

print("start optimizing")
print("##############################################################")                   
problem.optimize()

with open("log_2agents.txt", 'w') as f:
    print(problem.objective.x,file=f)

dic = {}
for p1 in range(2):
    for p2 in range(2):
        for q1 in range(2):
            for q2 in range(2):
                r = [[0,0],[0,0]]
                for w in range(2):
                    for f in range(2):
                        r[w][f] = gs[p1,p2,q1,q2,w,f].x
                dic[str(p1)+str(p2)+str(q1)+str(q2)] = r

with open("output_2agents.pkl","wb") as f:
    pickle.dump(dic,f)

# with open("output_raw.pkl","wb") as f:
#     pickle.dump(gs,f)
    
# with open("output_problem.pkl","wb") as f:
#     pickle.dump(problem,f)
print("done")