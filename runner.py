import sys
import os

start = [1992, 10, 2]
end = [2019, 1, 1]

#start = [1992, 10, 2]
#end = [2011, 4, 1]
#vals = [10, 15, 20]
vals = [10, 15]

for p in vals:
    f = open("input.txt", "w")
    f.write("{}\t{}\t{}\n".format(start[0], start[1], start[2]))
    f.write("{}\t{}\t{}\n".format(end[0], end[1], end[2]))
    f.write("{}".format(p))
    f.close()
    while True:
        f = open("input.txt", "r")
        start_cur = list(f.readline().rstrip().split('\t'))
        end_cur = list(f.readline().rstrip().split('\t'))
        f.close()
        for i in range(3):
            start_cur[i] = int(start_cur[i])
            end_cur[i] = int(end_cur[i])
        if not (start_cur[0] == end_cur[0] and start_cur[1] == end_cur[1]):
            os.system('python project6.py')
        else:
            break
    print("P =", p, "is Done")
