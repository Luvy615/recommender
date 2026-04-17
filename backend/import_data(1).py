import csv
import os
import re
import sys
from pathlib import Path
from sqlalchemy import text
import pymysql

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.database import init_db, engine
from backend.config import config


CATEGORY_MAPPING = {
    "上衣类": "上衣",
    "下装": "下装",
    "连衣裙类": "连衣裙",
    "鞋子": "鞋子",
    "配件": "配件"
}

SUB_CATEGORY_MAPPING = {
    "衬衫": "衬衫",
    "T恤": "T恤",
    "卫衣": "卫衣",
    "毛衣": "毛衣",
    "外套": "外套",
    "大衣": "大衣",
    "背心": "背心",
    "polo": "Polo",
    "下装_裤子": "裤子",
    "下装_短裤": "短裤",
    "下装_牛仔裤": "牛仔裤",
    "下装_裙子": "裙子",
    "下装_休闲裤": "休闲裤",
    "连衣裙": "连衣裙",
    "半身裙": "半身裙",
    "背带裤": "背带裤",
    "休闲鞋": "休闲鞋",
    "运动鞋": "运动鞋",
    "帆布鞋": "帆布鞋",
    "高跟鞋": "高跟鞋",
    "凉鞋": "凉鞋",
    "靴子": "靴子",
    "配饰_包包": "包包",
    "配饰_帽子": "帽子",
    "配饰_围巾": "围巾",
    "配饰_腰带": "腰带",
    "配饰_袜子": "袜子"
}


def extract_price(price_str: str) -> float:
    if not price_str:
        return 0.0
    price_str = str(price_str)
    match = re.search(r'[\d.]+', price_str.replace(',', ''))
    if match:
        return float(match.group())
    return 0.0


def extract_color_from_name(name: str) -> str:
    colors = ['白色', '黑色', '蓝色', '红色', '绿色', '黄色', '粉色', '紫色', '灰色', '棕色', '卡其色', '米色', '奶白色', '藏青色']
    for color in colors:
        if color in name:
            return color
    return '其他'


def extract_style_from_name(name: str) -> str:
    name_lower = name.lower()
    if any(word in name_lower for word in ['jk', '学院', '制服', '校供']):
        return '学院'
    elif any(word in name_lower for word in ['lolita', '洛丽塔', '洋装', '哥特']):
        return '洛丽塔'
    elif any(word in name_lower for word in ['商务', '正装', '通勤']):
        return '商务'
    elif any(word in name_lower for word in ['休闲', '日常', '百搭']):
        return '休闲'
    elif any(word in name_lower for word in ['运动', '跑步', '健身']):
        return '运动'
    elif any(word in name_lower for word in ['复古', 'vintage']):
        return '复古'
    elif any(word in name_lower for word in ['韩系', '韩版', '韩风']):
        return '韩系'
    return '休闲'


def import_csv_data(csv_path: str, category: str, sub_category: str = None) -> int:
    count = 0
    conn = pymysql.connect(
        host=config.MYSQL_HOST,
        port=config.MYSQL_PORT,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DATABASE,
        charset='utf8mb4'
    )
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    product_name = row.get('产品名称', '')
                    if not product_name:
                        continue
                    
                    image_url = row.get('图片地址', '')
                    product_url = row.get('商品链接', '')
                    
                    if not image_url or not product_url:
                        continue
                    
                    price = extract_price(row.get('产品价格', '0'))
                    color = extract_color_from_name(product_name)
                    style = extract_style_from_name(product_name)
                    
                    with conn.cursor() as cursor:
                        sql = """
                        INSERT INTO products 
                        (id, source, source_id, name, category, sub_category, color, style, season, price, image_url, product_url)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        import uuid
                        cursor.execute(sql, (
                            str(uuid.uuid4()),
                            'taobao',
                            row.get('商品id', ''),
                            product_name,
                            category,
                            sub_category,
                            color,
                            style,
                            '四季',
                            price,
                            image_url[:1000] if image_url else None,
                            product_url
                        ))
                        count += 1
                        
                except Exception as e:
                    continue
            
            conn.commit()
    finally:
        conn.close()
    
    return count


def main():
    print("Initializing database...")
    init_db()
    print("Database initialized.")
    
    base_path = Path(__file__).parent.parent
    total_count = 0
    
    print("\n开始导入数据...")
    
    for category_folder, category in CATEGORY_MAPPING.items():
        category_path = base_path / category_folder
        if not category_path.exists():
            print(f"跳过不存在的目录: {category_folder}")
            continue
        
        print(f"\n处理分类: {category}")
        
        for csv_file in category_path.glob("*.csv"):
            sub_category = SUB_CATEGORY_MAPPING.get(csv_file.stem, csv_file.stem)
            print(f"  导入文件: {csv_file.name} (子分类: {sub_category})")
            count = import_csv_data(str(csv_file), category, sub_category)
            print(f"    成功导入 {count} 条记录")
            total_count += count
    
    print(f"\n导入完成! 总共导入 {total_count} 条商品记录。")


if __name__ == "__main__":
    main()
