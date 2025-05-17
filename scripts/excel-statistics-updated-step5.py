import pandas as pd
import os
from collections import Counter
import argparse
from datetime import datetime

def analyze_excel_file(file_path, column_name='线长'):
    """
    分析Excel文件中所有工作表的指定列的值分布并生成统计表格。
    
    Args:
        file_path (str): Excel文件的路径
        column_name (str): 要分析的列名，默认为'线长'
    
    Returns:
        dict: 包含每个值出现次数的字典
    """
    print(f"正在分析Excel文件: {file_path}")
    
    # 使用ExcelFile对象读取Excel文件
    excel_file = pd.ExcelFile(file_path)
    sheet_names = excel_file.sheet_names
    print(f"发现 {len(sheet_names)} 个工作表: {', '.join(sheet_names)}")
    
    # 初始化计数器
    all_values = []
    sheet_counters = {}  # 每个工作表的统计结果
    
    # 处理每个工作表
    for sheet_name in sheet_names:
        try:
            print(f"处理工作表 '{sheet_name}'...")
            # 读取当前工作表
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            
            # 检查"线长"列是否存在
            if column_name in df.columns:
                # 收集"线长"列中的所有值，跳过NaN值
                values = df[column_name].dropna().tolist()
                all_values.extend(values)
                sheet_counters[sheet_name] = Counter(values)
                print(f"  在'{sheet_name}'中找到 {len(values)} 个'{column_name}'列的值")
            else:
                print(f"  警告: 在工作表'{sheet_name}'中没有找到'{column_name}'列")
        except Exception as e:
            print(f"  处理工作表'{sheet_name}'时出错: {str(e)}")
    
    # 计算所有值的出现次数
    value_counts = Counter(all_values)
    
    return value_counts, sheet_counters

def create_statistics_excel(file_path, value_counts, sheet_counters, column_name='线长'):
    """
    创建包含统计结果的新Excel文件
    
    Args:
        file_path (str): 原始Excel文件的路径
        value_counts (Counter): 所有工作表的值计数器
        sheet_counters (dict): 每个工作表的值计数器
        column_name (str): 分析的列名
    
    Returns:
        str: 新Excel文件的路径
    """
    # 创建输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_file = f"{base_name}_线长统计_{timestamp}.xlsx"
    
    # 创建Excel写入器
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # 创建汇总统计表
        if value_counts:
            # 按值排序
            sorted_counts = sorted(value_counts.items())
            total_count = sum(value_counts.values())
            
            # 创建DataFrame
            data = []
            for value, count in sorted_counts:
                percentage = (count / total_count) * 100
                data.append({
                    '线长值': value,
                    '出现次数': count,
                    '百分比': f"{percentage:.2f}%"
                })
            
            summary_df = pd.DataFrame(data)
            summary_df.loc[len(summary_df)] = ['总计', total_count, '100.00%']
            
            # 写入汇总工作表
            summary_df.to_excel(writer, sheet_name='总体统计', index=False)
            
            # 为每个工作表创建单独的统计表
            for sheet_name, counter in sheet_counters.items():
                if counter:
                    sheet_sorted_counts = sorted(counter.items())
                    sheet_total = sum(counter.values())
                    
                    sheet_data = []
                    for value, count in sheet_sorted_counts:
                        percentage = (count / sheet_total) * 100
                        sheet_data.append({
                            '线长值': value,
                            '出现次数': count,
                            '百分比': f"{percentage:.2f}%"
                        })
                    
                    sheet_df = pd.DataFrame(sheet_data)
                    sheet_df.loc[len(sheet_df)] = ['总计', sheet_total, '100.00%']
                    
                    # 写入工作表
                    sheet_stats_name = f"{sheet_name}统计"[:31]  # Excel工作表名最长31个字符
                    sheet_df.to_excel(writer, sheet_name=sheet_stats_name, index=False)
    
    print(f"\n统计结果已保存到: {output_file}")
    return output_file

def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='统计Excel文件中所有工作表的线长值分布')
    parser.add_argument('file_path', help='Excel文件的路径')
    parser.add_argument('--column', '-c', default='线长', help='要分析的列名 (默认: 线长)')
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.file_path):
        print(f"错误: 文件 '{args.file_path}' 不存在")
        return
    
    # 分析Excel文件
    value_counts, sheet_counters = analyze_excel_file(args.file_path, args.column)
    
    # 显示结果
    if value_counts:
        print("\n统计结果:")
        print(f"'{args.column}'列的值分布:")
        
        # 按值排序
        sorted_counts = sorted(value_counts.items())
        
        # 计算总数
        total_count = sum(value_counts.values())
        
        # 打印表头
        print(f"{'值':<10} {'出现次数':<10} {'百分比':<10}")
        print("-" * 30)
        
        # 打印每个值的统计信息
        for value, count in sorted_counts:
            percentage = (count / total_count) * 100
            print(f"{value:<10} {count:<10} {percentage:.2f}%")
        
        print("-" * 30)
        print(f"总计: {total_count} 个值")
        
        # 创建统计Excel文件
        create_statistics_excel(args.file_path, value_counts, sheet_counters, args.column)
    else:
        print("没有找到任何值进行统计")

if __name__ == "__main__":
    main()
