from math import sin, cos, sqrt, atan2, radians
from collections import defaultdict
from collections import Counter
import glob
import os
import gmplot
import googlemaps, gmplot, webbrowser, os, json
from datetime import datetime

def days_difference(month1, day1, month2, day2, year=2023):
    """计算两个日期之间的天数差异。
    
    参数:
    month1, day1: 第一个日期的月份和日子。
    month2, day2: 第二个日期的月份和日子。
    year: 年份，默认为2023，因为年份对计算相对天数差异没有影响，除非涉及到闰年。
    """
    date1 = datetime(year, month1, day1)
    date2 = datetime(year, month2, day2)
    
    # 计算两个日期之间的差异，并返回天数
    difference = (date2 - date1).days
    return difference


gmap = gmplot.GoogleMapPlotter(-3.343366, 7.806870, 5)
gmap.apikey = 'AIzaSyBvk0FzLa1I3firizOClEPkV9WDkVqhwZw'
gmaps = googlemaps.Client(key=gmap.apikey)
geocode_result = gmaps.geocode('Beijing')

path = 'output_folder/*.csv'

def distance(lat1, lon1, lat2, lon2):  #Function to calculate distance between two pairs of Geo-coordinates using Haversine Approximation

    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    #print("Result:", distance*1000)
    return distance*1000


def window(cur_year, cur_month, cur_day):  #Function for windowing through the dataset

    files = glob.glob(path)
    DBt = defaultdict(list)
    i = 1
    temp = -1
    
    #读取数据集中的信息，如果时间点符合要求，记录经纬度
    for file in files:

        i = i+1
        
        f = open(file,'r')
        ID = os.path.basename(f.name).split('.')[0]       #Trajectory ID (File name)
        
        line_number = 0  # 初始化行号计数器

        for line in f:
            # 根据我的代码，相同的行代表相同的时间
            line_number += 1  # 每读取一行，行号加一

            x = line.split(' ')
            
            date = x[0].split(',')  #List whose 2nd element contains date (yyyy-mm-dd) - date [1]
            time = x[1].split(',')  #List whose 1st element contains time (HH:MM::SS) - time[0]
	    
            lat = time[1]
            lon = time[2]
            
            year = date[1].split('-')[0]    #Year
            month = date[1].split('-')[1]    #Month
            day = date[1].split('-')[2]      #Day
            hour = time[0].split(':')[0]     #HOUR
            min_ = time[0].split(':')[1]     #MINS
            secs = time[0].split(':')[2]     #SECS

            diff = days_difference(int(month), int(day), int(cur_month), int(cur_day), int(year))
           
            if (diff <= 32):
                DBt[ID].append(lat)              #Trajectories in window
                DBt[ID].append(lon)
                DBt[ID].append(line_number)
                           
    return DBt

    
def neighbor_timebins(DBt):   # This generates the graph and contains all the neighbors

    TR_list = defaultdict(lambda: defaultdict(list))
    i=2

    for key in DBt:
        i=2
        for l in range(0,len(DBt[key])):
            if (i <= len(DBt[key])):

                for s_key in DBt:

                    if (s_key == key):
                        continue
            
                    k = 2

                    #print (key,s_key)

                    for j in range(0,len(DBt[s_key])):
                        if k <= len(DBt[s_key]):

                            lat1 = float(DBt[key][i-2])         # Latitude 1
                            lon1 = float(DBt[key][i-1])         # Longitude 1
                            lat2 = float(DBt[s_key][k-2])       # Latitude 2
                            lon2 = float(DBt[s_key][k-1])       # Longitude 2

                            timebin = DBt[s_key][k]

                            if DBt[key][i] == DBt[s_key][k]:

                                d = distance(lat1,lon1,lat2,lon2)
                                # print(d)

                                # inlier 46 outlier 4
                                if d <= 150000:
                                    # print (key,s_key)
                                    # print (lat1,lon1,lat2,lon2)
                                    TR_list[key][timebin].append(s_key)

                            k = k + 3        # The format is such that every 4th element is a new trajectory point
                    
            i = i + 3

#  DEBUGGING FOR PROFILING

    for key in TR_list:
        print (key, ':', TR_list[key])
        print ('\n')
    return (TR_list)



def trajectory_outlier(k, threshold, TR_list):
    outliers = []
    inliers = []

    for key in TR_list:

        if len(TR_list[key]) >= threshold:
            # print("check")
            for t_bins in TR_list[key]:

                for i in TR_list[key][t_bins]:
                    a=list(TR_list[key].values()) 
                    total=[]
                    for j in a:
                        total = total + j
                    final = Counter(total)        # Contains the count of the number of occurences of each point of an ID for each Trajectory

                    # print(key,final)  DEBUGGINH FOR PROFILING
          
                if len(final) >= k:
                    num = 0
                    #print (key, final)             # DEBUG
                    for items in final:
                        
                        if final[items] >= threshold:
                            num = num +1             # Check whether number of neighbor trajectories >= k
                    if num >= k:
                        #print (key, "In_line")      # DEBUG
                        if key not in inliers:
                            inliers.append(key)
                        #print (num)                  # DEBUG
                        dummy=0
                    else:
                        #print("outlier")             # DEBUG
                        if key not in outliers:
                            outliers.append(key)
                            
                    #print (len(final))              # DEBUG
                else:
                    if key not in outliers:
                        outliers.append(key)
                    
        else:
            if key not in outliers:
                outliers.append(key)
            #print ("outliers")                     # DEBUG

#   print (num)
    return outliers, inliers
            

def convert_to_geojson(longitude_list, latitude_list, savePath):

    # Create a list of coordinates from the given longitude and latitude lists
    # coordinates = [[longitude_list[i], latitude_list[i]] for i in range(len(longitude_list))]
    coordinates = [[latitude_list[i], longitude_list[i]] for i in range(len(longitude_list))]

    # Define the structure of the GeoJSON
    geojson = {
        'type': 'Feature',
        'geometry': {
            'type': 'LineString',
            'coordinates': coordinates
        }
    }

    save_path = savePath

    # 检查文件是否存在
    if os.path.exists(save_path):
        # 如果文件已存在，则删除文件
        os.remove(save_path)

    # 保存为 GeoJSON 文件
    with open(save_path, 'w') as outfile:
        print('ok')
        json.dump(geojson, outfile)


if __name__ == '__main__':
    # 提取 2 号 15 点 32 分到 47 分之间的数据点，并存储在 ans 变量中。
    ans = window('2023','7','17') # cur_year, cur_month, cur_day
    # print(ans)

    check = neighbor_timebins(ans)
    print (check)

    # threshold表示去重后有多少邻居，k表示32个时间片里有多少个时间片的实体和当前实体是相邻的
    out, inl = trajectory_outlier(2, 1, check) # k, threshold

    print("inlier", len(inl), "outlier",len(out))        #LENGTH


    #start
    latitude_list = []
    longitude_list = []
    j=0

    # outlier
    for ID in sorted(out):
        latitude_list = []
        longitude_list = []
        for i in range(0,len(ans[ID])):
            j = j + 1
            if j == 3:
                j = 0
                continue
            if j == 1:
                ans[ID][i] = ans[ID][i].rstrip()
                latitude_list.append(float(ans[ID][i]))
            if j == 2:
                ans[ID][i] = ans[ID][i].rstrip()
                longitude_list.append(float(ans[ID][i]))

        # print(ID,'\n')
        # print(ans[ID],'\n')
        # print(latitude_list, '\n')
        # print(longitude_list, '\n')
        # longitude_list.sort()
        # latitude_list.sort()
        # print(latitude_list)
        gmap.scatter(longitude_list, latitude_list, '#FF0000',
                                  size = 30, marker = False )
        gmap.plot(longitude_list, latitude_list,
               'red', edge_width = 6)
        convert_to_geojson(longitude_list, latitude_list, 'path.geojson')

    latitude_list1 = []
    longitude_list1 = []
    #inlier
    for ID in sorted(inl):
        latitude_list1 = []
        longitude_list1 = []
        for i in range(0,len(ans[ID])):
            j = j + 1
            if j == 3:
                j = 0
                continue
            if j == 1:
                ans[ID][i] = ans[ID][i].rstrip()
                latitude_list1.append(float(ans[ID][i]))
            if j == 2:
                ans[ID][i].rstrip()
                longitude_list1.append(float(ans[ID][i]))

        # print(ID,'\n')
        # print(ans[ID],'\n')
        # print(latitude_list1, '\n')
        # print(longitude_list1, '\n')
        # longitude_list1.sort()
        # latitude_list1.sort()
        gmap.scatter(longitude_list1, latitude_list1, '#0000FF',
                                  size = 40, marker = False )
        gmap.plot(longitude_list1, latitude_list1,
               'cornflowerblue', edge_width = 5)
        convert_to_geojson(longitude_list1, latitude_list1, 'path1.geojson')
        

    # Draw
    gmap.draw("my_map.html")

    filename = 'file:///'+os.getcwd()+'/' + 'my_map.html'
    webbrowser.open_new_tab(filename)






