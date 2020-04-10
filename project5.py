import Nio
import os
from calendar import monthrange
import numpy as np
import math
import time

def add_days(date, days):
    dsamnt = monthrange(date[0], date[1])
    date[2] += days
    if date[2] > dsamnt[1]:
        date[2] -= dsamnt[1]
        date[1] += 1
    if date[1] == 13:
        date[1] = 1
        date[0] += 1

def wind_speed(x, y):
    return (x*x + y*y)**(0.5)


def b_search(val, lst):
    l = 0
    r = len(lst)
    while r-l != 1:
        m = (l + r)//2
        if lst[m] > val:
            r = m
        else:
            l = m
    return l

def crt_names(cdate, wind_fldr, sea_fldr):
    wind_name = str(cdate[0])
    if len(str(cdate[1])) == 1:
        wind_name += '0'
    wind_name += str(cdate[1])

    sea_name = str(cdate[0])
    if len(str(cdate[1])) == 1:
        sea_name += '0'
    sea_name += str(cdate[1])
    if len(str(cdate[2])) == 1:
        sea_name += '0'
    sea_name += str(cdate[2])
    wind_ret = wind_fldr + wind_name
    if cdate[0] > 2011 or (cdate[0] == 2011 and cdate[1] >= 4):
        wind_ret += ".grib2"
    else:
        wind_ret += ".grb2"

    return wind_ret, sea_fldr + sea_name + "12.nc"

def get_str_date(cdate):
    ans = str(cdate[0]) + '/'
    if len(str(cdate[1])) == 1:
        ans += '0'
    ans += str(cdate[1]) + '/'
    if len(str(cdate[2])) == 1:
        ans += '0'
    ans += str(cdate[2])
    return ans


def get_sea_files(cdate, cur_sea_file, storms, lat, lon, u_comp_b, v_comp_b, p):
    sea = Nio.open_file(cur_sea_file,"r")
    sl = sea.variables['SLA']
    sla = sl[0, :, :]
    sea_lat = sea.variables['Latitude']
    sea_lon = sea.variables['Longitude']

    for k in range(len(storms)):
        i = storms[k][0]
        j = storms[k][1]
        s = b_search(lat[i], sea_lat)
        q = b_search(lon[j], sea_lon)
        val = sla[q, s]
        if not math.isnan(val):
            t = wind_speed(u_comp_b[cdate[2]-1, i, j], v_comp_b[cdate[2]-1, i, j])
            if t > p:
                storms[k][2] += val
                storms[k][3] += 1
            else:
                storms[k][4] += val
                storms[k][5] += 1
    sea.close()




def main():
    sea_fldr = "/mnt/e/ArtFiles2/project/Storm and sea level/data/sea/ssh_grids_v1812_"
    wind_fldr = "/mnt/e/ArtFiles2/project/Storm and sea level/data/wind/wnd10m.l.gdas."
    f = open("input.txt", "r")
    start = list(f.readline().rstrip().split('\t'))
    end = list(f.readline().rstrip().split('\t'))
    p = int(f.readline().rstrip())
    f.close()
    for i in range(3):
        start[i] = int(start[i])
        end[i] = int(end[i])
    uw = 'UGRD_P0_L103_GGA0'
    vw = 'VGRD_P0_L103_GGA0'


    cdate = list()
    cdate.append(start[0])
    cdate.append(start[1])
    cdate.append(start[2])
    cycles_cnt = 0

    series = 11
    u_comp_b = list()
    v_comp_b = list()
    lat = list()
    lon = list()

    prev_time = time.time()
    prev_month = 0
    wind = 0
    storms = list()
    cnt_days = 0
    while not (cdate[0] == end[0] and cdate[1] == end[1]):
        cur_wind_file, cur_sea_file = crt_names(cdate, wind_fldr, sea_fldr)
        if cdate[1] != prev_month:
            #get_wind_files(cur_wind_file, u_comp_b, v_comp_b, lat, lon)
            wind = Nio.open_file(cur_wind_file,"r")
            u_comp = wind.variables[uw]
            u_comp_b = u_comp[2::4, 0, :, :]
            v_comp = wind.variables[vw]
            v_comp_b = v_comp[2::4, 0, :, :]
            lat = wind.variables['lat_0']
            lon = wind.variables['lon_0']
            prev_month = cdate[1]

        if not os.path.exists(cur_sea_file):
            add_days(cdate, 1)
            continue

        if cnt_days == series:
            dot_amnt = 0
            f = open("output_every.txt", "a")
            for k in range(len(storms)):
                if storms[k][3] >= 4 and storms[k][5] >= 4:
                    dot_amnt += 1
                    avg_storm = storms[k][2] / storms[k][3]
                    avg_calm = storms[k][4] / storms[k][5]
                    avg_storm -= avg_calm
                    f.write("{}\t{}\t{}\n".format(get_str_date(cdate), p, avg_storm))
            cnt_days = 0
            f.close()
            cur_time = time.time()
            print(p, dot_amnt, cdate, cur_time - prev_time)
            cycles_cnt += 1
            if cycles_cnt == 1 or cur_time - prev_time > 50:
                print("Switch time!")
                break
            prev_time = cur_time

        if cnt_days == 0:
            #if zero, we create new storm points
            a = len(lat)
            b = len(lon)
            storms = list()
            for i in range(a):
                if -80 < lat[i] < 80:
                    for j in range(b):
                        t = wind_speed(u_comp_b[cdate[2]-1, i, j], v_comp_b[cdate[2]-1, i, j])
                        if t > p:
                            storms.append([i, j, 0, 0, 0, 0])

        get_sea_files(cdate, cur_sea_file, storms, lat, lon, u_comp_b, v_comp_b, p)
        print(cdate)
        #sea.close()
        add_days(cdate, 5)
        if cdate[1] != prev_month:
            wind.close()
        cnt_days += 1

    wind.close()
    f = open("input.txt", "w")
    f.write("{}\t{}\t{}\n".format(cdate[0], cdate[1], cdate[2]))
    f.write("{}\t{}\t{}\n".format(end[0], end[1], end[2]))
    f.write("{}".format(p))
    f.close()


if __name__ == '__main__':
    main()
