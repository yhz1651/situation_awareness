import json
file_id = 2 # 读取的文件的id,范围[1,250]
entity_id = 1 # 要转化数据的实体的id，范围[0,199]

def work():
    # 读取 JSON 文件
    # file_id = file_id 
    json_road = r"data/large_scale_enemy_advantage_"+str(file_id)+".json" # r"data/large_scale_enemy_advantage_1.json"
    with open(json_road, 'r') as f:  
        data = json.load(f)
        
    # 轨迹数据，例如一个包含经度和纬度的列表
    longitude = []
    latitude = []
    altitude = []
    for i in range(200): # 
        longitude.append([])
        latitude.append([])
        altitude.append([])
        
    num_use_enti = 200 # 10

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
                f.write(str(longitude[entity_id][i]))
                f.write(',')
                f.write(str(latitude[entity_id][i]))
                f.write('\n')
                
                
    txt_road = r"LSTM/input-data.txt" 
    write_data(txt_road)
    txt_road = r"LSTM/input-data-test.txt" 
    write_data(txt_road)

    print("Change to txt finished!")
    
