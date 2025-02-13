class Map:
    def __init__(self, longitude, latitude, altitude):
        self.longitude = longitude # 经度
        self.latitude = latitude # 纬度
        self.altitude = altitude # 高度

    def get_coordinates(self):
        return self.longitude, self.latitude

    def get_altitude(self):
        return self.altitude

    def set_coordinates(self, longitude, latitude):
        self.longitude = longitude
        self.latitude = latitude

    def set_altitude(self, altitude):
        self.altitude = altitude

# 示例用法
if __name__ == "__main__":
    # 创建一个地图对象
    my_location = Map(longitude=30.0, latitude=40.0, altitude=100.0)

    # 获取当前坐标和高度
    current_coordinates = my_location.get_coordinates()
    current_altitude = my_location.get_altitude()
    print(f"Current Coordinates: {current_coordinates}")
    print(f"Current Altitude: {current_altitude} meters")

    # 更新坐标和高度
    my_location.set_coordinates(35.0, 45.0)
    my_location.set_altitude(150.0)

    # 获取更新后的坐标和高度
    updated_coordinates = my_location.get_coordinates()
    updated_altitude = my_location.get_altitude()
    print(f"Updated Coordinates: {updated_coordinates}")
    print(f"Updated Altitude: {updated_altitude} meters")
