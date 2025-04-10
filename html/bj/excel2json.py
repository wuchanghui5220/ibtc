#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import pandas as pd
import logging
import time
import argparse
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("excel_processor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ExcelProcessor")

def process_excel_to_json(excel_file, output_dir="output", output_filename=None):
    """
    处理Excel文件并转换为JSON格式
    
    参数:
        excel_file: Excel文件路径
        output_dir: 输出目录
        output_filename: 输出文件名（可选，默认使用时间戳）
    
    返回:
        输出的JSON文件路径
    """
    try:
        logger.info(f"开始处理Excel文件: {excel_file}")
        
        # 检查文件是否存在
        if not os.path.exists(excel_file):
            logger.error(f"文件不存在: {excel_file}")
            return None
        
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"创建输出目录: {output_dir}")
        
        # 读取Excel文件
        df = pd.read_excel(excel_file)
        
        # 检查所需列是否存在
        required_columns = ['Price Book Organizer', 'Product Name', 'Product Description', 'P3 - OEM Price']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.error(f"Excel文件缺少以下必要列: {', '.join(missing_columns)}")
            return None
        
        # 转换为JSON格式
        products = []
        for _, row in df.iterrows():
            # 只保留我们需要的列
            product = {
                'id': str(row.name),  # 使用DataFrame的索引作为ID
                'price_book_organizer': str(row.get('Price Book Organizer', '')),
                'product_name': str(row.get('Product Name', '')),
                'product_description': str(row.get('Product Description', '')),
                'price': float(row.get('P3 - OEM Price', 0) or 0)  # 处理None或空值
            }
            products.append(product)
        
        # 创建最终的JSON对象
        result = {
            'products': products,
            'metadata': {
                'total_products': len(products),
                'generated_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'source_file': os.path.basename(excel_file)
            }
        }
        
        # 生成输出文件名
        if not output_filename:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            output_filename = f"products-{timestamp}.json"
        
        output_path = os.path.join(output_dir, output_filename)
        
        # 写入JSON文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"成功生成JSON文件: {output_path}")
        
        # 创建一个固定名称的最新版本文件
        latest_path = os.path.join(output_dir, "products-latest.json")
        try:
            with open(latest_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"成功更新最新版本文件: {latest_path}")
        except Exception as e:
            logger.error(f"更新最新版本文件时出错: {e}")
        
        return output_path
        
    except Exception as e:
        logger.error(f"处理Excel文件时出错: {e}")
        return None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='将Excel产品清单转换为JSON格式')
    parser.add_argument('excel_file', help='输入的Excel文件路径')
    parser.add_argument('--output-dir', '-o', default='output', help='输出目录')
    parser.add_argument('--output-filename', '-f', help='输出文件名')
    
    args = parser.parse_args()
    
    logger.info("开始Excel到JSON转换程序")
    output_path = process_excel_to_json(
        args.excel_file, 
        args.output_dir, 
        args.output_filename
    )
    
    if output_path:
        logger.info(f"处理完成，输出文件: {output_path}")
    else:
        logger.error("处理失败")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
