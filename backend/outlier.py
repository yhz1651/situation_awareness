from math import sin, cos, sqrt, atan2, radians
from collections import defaultdict
from collections import Counter
import glob
import os
import gmplot
import googlemaps, gmplot, webbrowser, os, json


gmaps = googlemaps.Client(key='AIzaSyBvk0FzLa1I3firizOClEPkV9WDkVqhwZw')
geocode_result = gmaps.geocode('Beijing')
gmap = gmplot.GoogleMapPlotter(39.9042, 116.4074, 13 )
#gmap = gmplot.GoogleMapPlotter.from_geocode("Beijing")
gmaps = googlemaps.Client(key='AIzaSyBvk0FzLa1I3firizOClEPkV9WDkVqhwZw')
gmap.apikey = 'AIzaSyBvk0FzLa1I3firizOClEPkV9WDkVqhwZw'


#path = 'C:\\Users\\User\\Downloads\\T-drive Taxi Trajectories\\release\\taxi_log_2008_by_id\\*.txt'
#path = '/Users/fym/Desktop/space-project/release/taxi_log_2008_by_id/*.txt'
path = '/root/yhz/code/situation_awareness/backend/taxi_log_2008_by_id/*.txt'

#计算两个地理坐标点之间的距离
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

#返回一个字典 DBt，其中包含了在指定时间窗口内的出租车轨迹数据
def window(cur_day, cur_hour, cur_endtime):  #Function for windowing through the dataset

    files = glob.glob(path)
    DBt = defaultdict(list)
    i = 1
    temp = -1
    
    #读取数据集中的信息，如果时间点符合要求，记录经纬度
    for file in files:
        
        if i == 500:         # CHANGE NUMBER OF FILES HERE!!!! (An error with one of the files so skipping)
            break
        i = i+1
        
        f = open(file,'r')
        ID = os.path.basename(f.name).split('.')[0]       #Trajectory ID (File name)
        
        for line in f:
            x = line.split(' ')
            
            date = x[0].split(',')  #List whose 2nd element contains date (yyyy-mm-dd) - date [1]
            time = x[1].split(',')  #List whose 1st element contains time (HH:MM::SS) - time[0]
	    

            lat = time[1]
            lon = time[2]
            
            day = date[1].split('-')[2]      #Day
            hour = time[0].split(':')[0]     #HOUR
            min_ = time[0].split(':')[1]     #MINS
            secs = time[0].split(':')[2]     #SECS

            
            if (cur_day == day and cur_hour == hour and int(cur_endtime) - int('15') <= int(min_)  and min_ <= cur_endtime and min_!= temp):
                #print(ID, min_, "\n")
                    
                temp = min_
                DBt[ID].append(lat)              #Trajectories in window
                DBt[ID].append(lon)
                DBt[ID].append(min_)
                           
    return DBt

#通过插值方法填补数据中的间隙，确保时间连续性，返回填补完间隙后的字典DBt
def fill_gaps(DBt, cur_endtime):  #Preprocessing to remove gaps between inconsistent sampling

    missing = list(map(str,range( int(cur_endtime) - 14, int(cur_endtime) + 1 )))
    #print(missing)

    for key in DBt:

        #print(key)   
        lat = float(DBt[key][0])
        long = float(DBt[key][1])
        
        for i in range(0, len(missing)):

            #print("diff_lat", (float(DBt[key][len(DBt[key]) - 3]) - float(DBt[key][0]) ) / ((len(DBt[key]) - missing[i])))
            #print("diff_long", diff_long)
            #print("denom",)
            
            if (missing[i]) not in DBt[key]:

                diff_lat = (float(DBt[key][len(DBt[key]) - 3]) - float(DBt[key][0])) /( 15)
                diff_long = (float(DBt[key][len(DBt[key]) - 2]) - float(DBt[key][1])) / ( 15)

                lat = lat + diff_lat
                long = long + diff_long
                #print(missing[i],lat)

                
                DBt[key].append(str(lat))              
                DBt[key].append(str(long))
                DBt[key].append(missing[i])

    return DBt
    
    
# 目的: 为每个时间窗口生成一个图，包含所有邻居（即在这个时间窗口内接近的其他轨迹）
# 参数: 输入的字典 DBt 包含出租车的轨迹数据
# 返回值: 返回一个名为 TR_list 的字典，它包含了每个轨迹点的邻居信息
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
                        print ('next')
            
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
                            
                                if d <= 1000:
                                    #print (key,s_key)
                                    #print (lat1,lon1,lat2,lon2)
                                    TR_list[key][timebin].append(s_key)

                            k = k + 3        # The format is such that every 4th element is a new trajectory point
                    
            i = i + 3

#  DEBUGGING FOR PROFILING

  #  for key in TR_list:
  #      print (key, ':', TR_list[key])
  #      print ('\n')
    return (TR_list)


# 目的: 根据指定的阈值和邻居数量，检测并分类轨迹数据中的异常值和正常值。
# 参数: 邻居数量 k，阈值 threshold，以及包含邻居信息的字典 TR_list。
# 返回值: 返回两个列表，分别包含异常值 (outliers) 和正常值 (inliers) 的轨迹ID。
# 参数：
# k: 一个整数，表示每个轨迹在时间窗口内应有的最小邻居数量，用于区分异常值和正常值。
# threshold: 一个整数，表示在考虑轨迹是否为异常值之前，轨迹必须至少出现在多少个时间窗口中。
# TR_list: 一个字典，包含了轨迹ID作为键，每个键对应的值是另一个字典，该字典的键是时间戳，值是包含该时间戳下轨迹邻居的列表。
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
            
'''        
TR_list = defaultdict(lambda: defaultdict(list))

TR_list[10035][32].append('1495')
TR_list[10035][37].append('1495')

TR_list[10035][32].append('1520')
TR_list[10035][37].append('1520')


TR_list[10137][37].append('10188')
TR_list[10137][42].append('10188')
'''

#print(TR_list[1][])  
#print (TR_list)

if __name__ == '__main__':
    ans = window('02','15','47') #文件中符合要求的经纬度和秒数
    #print(ans)
    ans = fill_gaps(ans,'47')


    #print (ans)
    #print ((ans['1'][2]))

    check = neighbor_timebins(ans)
    print (check)

    out, inl = trajectory_outlier(2, 3, check)

    print("inlier", len(inl), "outlier",len(out))        #LENGTH



    #start
    latitude_list = []
    longitude_list = []
    j=0

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
                ans[ID][i].rstrip()
                longitude_list.append(float(ans[ID][i]))

        #print(ID,'\n')
        #print(ans[ID],'\n')
        #print(latitude_list, '\n')
        #print(longitude_list, '\n')
        longitude_list.sort()
        latitude_list.sort()
        #print(latitude_list)
        gmap.scatter(longitude_list, latitude_list, '#FF0000',
                                  size = 30, marker = False )
        gmap.plot(longitude_list, latitude_list,
               'red', edge_width = 6)

    latitude_list1 = []
    longitude_list1 = []
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

        #print(ID,'\n')
        #print(ans[ID],'\n')
        #print(latitude_list1, '\n')
        #print(longitude_list1, '\n')
        longitude_list1.sort()
        latitude_list1.sort()
        gmap.scatter(longitude_list1, latitude_list1, '#0000FF',
                                  size = 40, marker = False )
        gmap.plot(longitude_list1, latitude_list1,
               'cornflowerblue', edge_width = 5)




    #print (len(latitude_list))
    #print (len(longitude_list))

    #print (latitude_list)
    #print("Outlier", out, "Inlier", inl)

    # end


    '''
    gmap = gmplot.GoogleMapPlotter(39.9042, 116.4074, 13 ) 
    #gmap = gmplot.GoogleMapPlotter.from_geocode("Beijing")    # IF THIS LINE IS HERE, IT WORKS
    gmap.apikey = 'AIzaSyCul2f2Ao1xZ6_Lo3SdtxR-LuBeQjSysYw'
    
    gmap.scatter( latitude_list, longitude_list, '#0000FF', 
                                  size = 40, marker = False )
    gmap.plot(latitude_list, longitude_list,  
               'cornflowerblue', edge_width = 5) 
    '''

    #######

    #hidden_gem_lat, hidden_gem_lon = lat,lng
    #gmap.marker(hidden_gem_lat, hidden_gem_lon, 'cornflowerblue')

    # Draw
    gmap.draw("my_map.html")

    filename = 'file:///'+os.getcwd()+'/' + 'my_map.html'
    webbrowser.open_new_tab(filename)






