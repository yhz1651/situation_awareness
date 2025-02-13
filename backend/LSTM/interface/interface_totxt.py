import json

# 传入JSON数据和entity_id
def work(data, entity_id): # 
    
    # num_use_enti为实体数量。large: 200个实体。small: 50个实体
    num_use_enti = len(data[0]['entities']) # 自动判断实体数量
    print("num_use_enti =", num_use_enti)
    print("time stamps =", len(data)) # 32，代表32个时间戳
    
    # print("entity_id =", entity_id)
    # print("data[0] =", data[0])
    # print("len(data[0]) =", len(data[0])) # 2
    # print("len data 0 entities =", len(data[0]['entities'])) # 50或200
    
    # entities_count = len(data["entities"])  
    # print("entities_count =", entities_count)
    
    # 轨迹数据，例如一个包含经度和纬度的列表
    longitude = []
    latitude = []
    altitude = []
    
    for i in range(200): # 
        longitude.append([])
        latitude.append([])
        altitude.append([])
    
    # 打印读取的 JSON 数据
    # 获取 'name' 字段的值
    for i in range(len(data)):
        data_now = data[i]
        time0 = data_now['time']
        entities = data_now['entities']
        
        for j in range(0, num_use_enti): # 
            policy = entities[j]['policy']
            ent0 = entities[j]
            ent0_loca = ent0['location']
            # print("ent0_loca:", ent0_loca) # 输出经度，纬度，高度
            
            longitude[j].append(ent0_loca['longitude']) # 经度
            latitude[j].append(ent0_loca['latitude']) # 纬度
            altitude[j].append(ent0_loca['altitude']) # 高度
            

    # 写入文件
    def write_data(txt_road):
        # 打开文件以写入内容，如果文件不存在则创建它  
        # 如果文件已存在并且使用'w'模式，则内容会被覆盖 
        with open(txt_road, 'w', encoding='utf-8') as f:  
            f.write('Our trajectory\n')  
            f.write('This is our trajectory.\n')  
            f.write('longitude,latitude\n')  
            
            # entity_id = entity_id # 要转化数据的实体的id
            for i in range(0, 32): # 32个时间戳
                try:
                    f.write(str(longitude[entity_id][i]))
                    f.write(',')
                    f.write(str(latitude[entity_id][i]))
                    f.write('\n')
                except:
                    print("Error: ")
                    print("i =", i) # 31
                    print("entity_id =", entity_id) # 0
                    
                
    txt_road = r"LSTM/interface/input-data.txt" 
    write_data(txt_road)
    txt_road = r"LSTM/interface/input-data-test.txt" 
    write_data(txt_road)

    # print("Change to txt finished!")
    
