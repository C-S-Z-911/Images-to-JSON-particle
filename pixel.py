from PIL import Image
import json


class Pixel:
    def __init__(self):
        self.json = {'count': 1, 'size': {'width': 1, 'height': 1}, 'points': [(1, 1, '#000000ff')]}
        self.pil_image = Image.new('RGBA', (10, 10), (255, 255, 255, 255))

    @staticmethod
    def rgba_to_hex(rgba):
        if rgba[3] == 0:  # 完全透明
            return None
        # 转rgba
        return f"#{rgba[0]:02x}{rgba[1]:02x}{rgba[2]:02x}{rgba[3]:02x}"

    @staticmethod
    def hex_to_rgba(hex_color):
        # 移除可能存在的 '#' 前缀并确保长度正确
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 8:
            raise ValueError("Input must be in the format '#RRGGBBAA'")

        # 每两个字符作为一个十六进制值进行转换
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        a = int(hex_color[6:8], 16)

        return r, g, b, a

    def image_to_json(self, url=None, interval=1):
        if url is not None:
            # 打开图像并确保处理透明度
            img = Image.open(url)
            # 统一转换为RGBA格式以处理透明度
            self.pil_image = img.convert("RGBA")

        pixel_access = self.pil_image.load()
        width, height = self.pil_image.size
        points = []
        count = 0

        # 遍历采样像素
        for y in range(0, height, interval):
            for x in range(0, width, interval):
                rgba = pixel_access[x, y]
                hex_color = self.rgba_to_hex(rgba)
                # 只记录非完全透明的像素
                if hex_color is not None:
                    points.append((x, y, hex_color))
                    count += 1

        size = {"width": width, "height": height}
        self.json = {'count': count, 'size': size, 'points': points}

    def json_to_pil(self, url=None):
        if url is not None:
            with open(url, 'r', encoding='utf-8') as file:
                self.json = json.load(file)

        # 创建一个新的空白图像，模式为 RGBA（包含透明度）
        width = self.json["size"]["width"]
        height = self.json["size"]["height"]
        self.pil_image = Image.new('RGBA', (width, height), (0, 0, 0, 0))

        # 加载像素数据
        pixels = self.pil_image.load()

        # 在指定坐标处绘制目标颜色的像素
        for coord in self.json["points"]:
            x, y, rgba = coord
            hex_rgba = self.hex_to_rgba(rgba)
            pixels[x, y] = hex_rgba

    def get_pil_image(self):
        return self.pil_image

    def get_json(self):
        return self.json

# pixel = Pixel()
# pixel.image_to_json("Logo.png", 1)
# print(pixel.json)
# pixel.json_to_pil()
#
# image = pixel.pil_image
#
# output_path = 'output_image.png'
# image.save(output_path)
