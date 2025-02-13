from map import Map
from entity import Tank, Soldier, Helicopter
from math import sqrt, pow, log
import json
import random
from data_generate import read_and_extract_entities, save_json_to_file

# 局部战力优势
def local_strength_advantage(current_entity, all_entities):
    entities = current_entity.entities_in_attack_range(all_entities)  # 当前实体射程范围内所有实体
    # print(f"Entities in range of current_entity: {[entity.get_name() for entity in entities]}")
    
    advantage_ours = 0
    advantage_enemys = 0
    for entity in entities:
        if entity.enemy:
            advantage_enemys += entity.get_strength()
        else:
            advantage_ours += entity.get_strength()
    # print(f"strength_advantage_enemys: {advantage_enemys}")
    # print(f"strength_advantage_ours: {advantage_ours}")
    
    if advantage_ours + advantage_enemys == 0:
        advantages = 0
    else:
        advantages = (advantage_ours - advantage_enemys) / (advantage_ours + advantage_enemys)
    # print(f"strength_advantages: {advantages}")
    
    return advantages


# 局部地势优势
def local_terrain_advantage(current_entity, all_entities):
    entities = current_entity.entities_in_attack_range(all_entities)  # 当前实体射程范围内所有实体
    # print(f"Entities in range of current_entity: {[entity.get_name() for entity in entities]}")
    
    advantage_ours = 0
    advantage_enemys = 0
    for entity in entities:
        if entity.enemy:
            advantage_enemys += entity.get_altitude()
        else:
            advantage_ours += entity.get_altitude()
    # print(f"terrain_advantage_enemys: {advantage_enemys}")
    # print(f"terrain_advantage_ours: {advantage_ours}")

    if advantage_ours + advantage_enemys == 0:
        advantages = 0
    else:
        advantages = (advantage_ours - advantage_enemys) / (advantage_ours + advantage_enemys)
    # print(f"terrain_advantages: {advantages}")
    
    return advantages


# 单方战力优势
def unilateral_strength_advantage(current_entities, all_entities):
    advantages = 0
    for entity in current_entities:
        advantages += local_strength_advantage(entity, all_entities)
    if(len(current_entities) > 0):
        advantages = advantages / len(current_entities)
    # print(f"unilateral_strength_advantages: {advantages}")
    
    return advantages


# 单方地势优势
def unilateral_terrain_advantage(current_entities, all_entities):
    advantages = 0
    for entity in current_entities:
        advantages += local_terrain_advantage(entity, all_entities)
    if(len(current_entities) > 0):
        advantages = advantages / len(current_entities)
    # print(f"unilateral_terrain_advantages: {advantages}")
    
    return advantages


# 战场混乱程度
def battlefield_chaos_degree(our_entities, enemy_entities, all_entities):
    for entity in all_entities:
        entity.chaos_g = (local_strength_advantage(entity, all_entities) + 1) /2
        entity.chaos_h = (local_terrain_advantage(entity, all_entities) +1) /2
    
    e_our_g = 0
    for entity in our_entities:
        if entity.chaos_g > 0:
            e_our_g += entity.chaos_g * log(entity.chaos_g, len(our_entities))
    e_our_h = 0
    for entity in our_entities:
        if entity.chaos_h > 0:    
            e_our_h += entity.chaos_h * log(entity.chaos_h, len(our_entities))
    e_enemy_g = 0
    for entity in enemy_entities:   
        if entity.chaos_g > 0: 
            e_enemy_g += entity.chaos_g * log(entity.chaos_g, len(enemy_entities))
    e_enemy_h = 0
    for entity in enemy_entities:  
        if entity.chaos_h > 0:  
            e_enemy_h += entity.chaos_h * log(entity.chaos_h, len(enemy_entities))
        
    p_our_g = 0
    for entity in our_entities:
        p_our_g += entity.chaos_g
    if len(our_entities):  
        p_our_g = p_our_g / len(our_entities)
    p_our_h = 0
    for entity in our_entities:
        p_our_h += entity.chaos_h  
    if len(our_entities): 
        p_our_h = p_our_h / len(our_entities)
    p_enemy_g = 0
    for entity in enemy_entities:
        p_enemy_g += entity.chaos_g
    if len(enemy_entities):   
        p_enemy_g = p_enemy_g / len(enemy_entities)
    p_enemy_h = 0
    for entity in enemy_entities:
        p_enemy_h += entity.chaos_h
    if len(enemy_entities):  
        p_enemy_h = p_enemy_h / len(enemy_entities)
        
    e_g = 0
    e_h = 0
    # 计算 e_g
    if p_our_g != 0 and e_our_g != 0:
        e_g = e_our_g * p_our_g * log(p_our_g, 2)
    if p_enemy_g != 0 and e_enemy_g != 0:
        e_g += e_enemy_g * p_enemy_g * log(p_enemy_g, 2)

    # 计算 e_h
    if p_our_h != 0 and e_our_h != 0:
        e_h = e_our_h * p_our_h * log(p_our_h, 2)
    if p_enemy_h != 0 and e_enemy_h != 0:
        e_h += e_enemy_h * p_enemy_h * log(p_enemy_h, 2)
    
    E = e_g + e_h
    # print(f"battlefield_chaos_degree: {E}")
    return E



if __name__ == "__main__":
    #
    # print("main") #
    
    # # 我方
    # soldier1 = Soldier(name="Soldier1", enemy=False, location=Map(500, 300, 20))
    # tank1 = Tank(name="Tank1", enemy=False, location=Map(1000, 1200, 50))
    # tank2 = Tank(name="Tank2", enemy=False, location=Map(600, 500, 40))  
    # helicopter1 = Helicopter(name="Helicopter1", enemy=False, location=Map(1000, 1000, 200))

    # # 敌方
    # soldier2 = Soldier(name="Soldier2", enemy=True, location=Map(500, 400, 20))
    # tank3 = Tank(name="Tank3", enemy=True, location=Map(2000, 500, 60))
    # helicopter2 = Helicopter(name="Helicopter2", enemy=True, location=Map(300, 700, 150))

    # our_entities = [soldier1, tank1, tank2, helicopter1] # 我方实体
    # enemy_entities = [soldier2, tank3, helicopter2] # 敌方实体
    # all_entities = [soldier1, soldier2, tank1, tank2, tank3, helicopter1, helicopter2] # 全部实体
    
    json_data = generate_json_data_multiple_times(num_times=10, num_entities_per_time=10) # [ERROR]
    # TypeError: generate_json_data_multiple_times() got an unexpected keyword argument 'num_entities_per_time'
    
    save_json_to_file(json_data, "backend/generated_data.json")
    all_entities_info = read_and_extract_entities("backend/generated_data.json")

    for time_data in all_entities_info:
        time = time_data["time"]
        entities = time_data["entities"]

        # 我方、敌方实体
        our_entities = [entity for entity in entities if not entity.enemy]
        enemy_entities = [entity for entity in entities if entity.enemy]
        
        # 随机选择一个实体作为当前实体
        entity = random.choice(entities)
        
        print(f"Time: {time}")
        # print(f"Local Strength Advantages: {local_strength_advantage(entity, entities)}")
        # print(f"Local Terrain Advantages: {local_terrain_advantage(entity, entities)}")
        print(f"Our Strength Advantages: {unilateral_strength_advantage(our_entities, entities)}")
        print(f"Enemy Strength Advantages: {unilateral_strength_advantage(enemy_entities, entities)}")
        print(f"Our Terrain Advantages: {unilateral_terrain_advantage(our_entities, entities)}")
        print(f"Enemy Terrain Advantages: {unilateral_terrain_advantage(enemy_entities, entities)}")
        print(f"Battlefield Chaos Degree: {battlefield_chaos_degree(our_entities, enemy_entities, entities)}")
        print("\n" + "=" * 100 + "\n")
