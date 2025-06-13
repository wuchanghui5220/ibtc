import pandas as pd
import os
from collections import Counter, defaultdict
import argparse
from datetime import datetime

def analyze_excel_file(file_path, length_column='线长优化', type_column='线缆类型'):
    """
    分析Excel文件中所有工作表的指定列的值分布并生成统计表格，
    同时按线缆类型进行分组统计。
    
    Args:
        file_path (str): Excel文件的路径
        length_column (str): 要分析的长度列名，默认为'标准线缆长度(米)'
        type_column (str): 要分析的类型列名，默认为'线缆类型'
    
    Returns:
        tuple: (总体计数, 每个工作表的计数, 按类型分组的计数)
    """
    print(f"正在分析Excel文件: {file_path}")
    
    # 使用ExcelFile对象读取Excel文件
    excel_file = pd.ExcelFile(file_path)
    sheet_names = excel_file.sheet_names
    print(f"发现 {len(sheet_names)} 个工作表: {', '.join(sheet_names)}")
    
    # 初始化计数器
    all_values = []  # 所有长度值
    all_types = []   # 所有类型值
    sheet_counters = {}  # 每个工作表的统计结果
    type_counters = defaultdict(Counter)  # 按类型分组的统计结果
    combined_data = []  # 存储类型和长度的组合数据
    
    # 处理每个工作表
    for sheet_name in sheet_names:
        try:
            print(f"处理工作表 '{sheet_name}'...")
            # 读取当前工作表
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            
            # 检查必要的列是否存在
            has_length_column = length_column in df.columns
            has_type_column = type_column in df.columns
            
            if has_length_column:
                # 收集长度列中的所有值，跳过NaN值
                length_values = df[length_column].dropna().tolist()
                all_values.extend(length_values)
                sheet_counters[sheet_name] = Counter(length_values)
                print(f"  在'{sheet_name}'中找到 {len(length_values)} 个'{length_column}'列的值")
                
                # 如果同时有类型列和长度列
                if has_type_column:
                    print(f"  在'{sheet_name}'中找到'{type_column}'列，进行类型分组统计")
                    
                    # 创建类型和长度的组合数据
                    # 过滤掉任一列为NaN的行
                    valid_rows = df.dropna(subset=[length_column, type_column])
                    
                    # 收集所有类型值
                    types = valid_rows[type_column].tolist()
                    all_types.extend(types)
                    
                    # 按类型统计长度
                    for idx, row in valid_rows.iterrows():
                        cable_type = row[type_column]
                        cable_length = row[length_column]
                        type_counters[cable_type][cable_length] += 1
                        combined_data.append((cable_type, cable_length))
                else:
                    print(f"  警告: 在工作表'{sheet_name}'中没有找到'{type_column}'列")
            else:
                print(f"  警告: 在工作表'{sheet_name}'中没有找到'{length_column}'列")
        except Exception as e:
            print(f"  处理工作表'{sheet_name}'时出错: {str(e)}")
    
    # 计算所有值的出现次数
    value_counts = Counter(all_values)
    
    return value_counts, sheet_counters, type_counters, combined_data

def create_statistics_excel(file_path, value_counts, sheet_counters, type_counters, combined_data, 
                           length_column='线长优化', type_column='线缆类型'):
    """
    创建包含统计结果的新Excel文件
    
    Args:
        file_path (str): 原始Excel文件的路径
        value_counts (Counter): 所有工作表的值计数器
        sheet_counters (dict): 每个工作表的值计数器
        type_counters (defaultdict): 按类型分组的计数器
        combined_data (list): 类型和长度的组合数据
        length_column (str): 分析的长度列名
        type_column (str): 分析的类型列名
    
    Returns:
        str: 新Excel文件的路径
    """
    # 创建输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_file = f"{base_name}_线缆统计_{timestamp}.xlsx"
    
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
                    length_column: value,
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
                            length_column: value,
                            '出现次数': count,
                            '百分比': f"{percentage:.2f}%"
                        })
                    
                    sheet_df = pd.DataFrame(sheet_data)
                    sheet_df.loc[len(sheet_df)] = ['总计', sheet_total, '100.00%']
                    
                    # 写入工作表
                    sheet_stats_name = f"{sheet_name}统计"[:31]  # Excel工作表名最长31个字符
                    sheet_df.to_excel(writer, sheet_name=sheet_stats_name, index=False)
            
            # 添加按线缆类型统计的工作表
            if type_counters:
                # 创建按类型分组的统计工作表
                type_stats_sheet = f"按{type_column}统计"
                
                # 按类型统计总数
                type_summary_data = []
                for cable_type, counter in type_counters.items():
                    type_total = sum(counter.values())
                    percentage = (type_total / len(combined_data)) * 100
                    type_summary_data.append({
                        type_column: cable_type,
                        '出现次数': type_total,
                        '百分比': f"{percentage:.2f}%"
                    })
                
                # 按出现次数排序
                type_summary_df = pd.DataFrame(type_summary_data)
                type_summary_df = type_summary_df.sort_values('出现次数', ascending=False)
                
                # 添加总计行
                type_summary_df.loc[len(type_summary_df)] = [
                    '总计', 
                    len(combined_data), 
                    '100.00%'
                ]
                
                # 写入按类型统计的工作表
                type_summary_df.to_excel(writer, sheet_name=type_stats_sheet, index=False)
                
                # 为每种类型创建详细统计表
                for cable_type, counter in type_counters.items():
                    if counter:
                        # 限制工作表名长度，避免超出31字符限制
                        type_sheet_name = f"{cable_type}统计"
                        if len(type_sheet_name) > 31:
                            type_sheet_name = type_sheet_name[:28] + "..."
                        
                        type_sorted_counts = sorted(counter.items())
                        type_total = sum(counter.values())
                        
                        type_data = []
                        for value, count in type_sorted_counts:
                            percentage = (count / type_total) * 100
                            type_data.append({
                                length_column: value,
                                '出现次数': count,
                                '百分比': f"{percentage:.2f}%"
                            })
                        
                        type_detail_df = pd.DataFrame(type_data)
                        type_detail_df.loc[len(type_detail_df)] = ['总计', type_total, '100.00%']
                        
                        # 写入类型详细统计工作表
                        type_detail_df.to_excel(writer, sheet_name=type_sheet_name, index=False)
                
                # 创建交叉表分析
                if combined_data:
                    # 将组合数据转换为DataFrame
                    cross_df = pd.DataFrame(combined_data, columns=[type_column, length_column])
                    
                    # 创建交叉表
                    cross_tab = pd.crosstab(
                        cross_df[type_column], 
                        cross_df[length_column],
                        margins=True, 
                        margins_name='总计'
                    )
                    
                    # 写入交叉表工作表
                    cross_tab.to_excel(writer, sheet_name='交叉分析表')
    
    print(f"\n统计结果已保存到: {output_file}")
    return output_file

def main():
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='统计Excel文件中线缆长度和类型的分布')
    parser.add_argument('file_path', help='Excel文件的路径')
    parser.add_argument('--length', '-l', default='线长优化', help='要分析的长度列名 (默认: 线长优化)')
    parser.add_argument('--type', '-t', default='线缆类型', help='要分析的类型列名 (默认: 线缆类型)')
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.file_path):
        print(f"错误: 文件 '{args.file_path}' 不存在")
        return
    
    # 分析Excel文件
    value_counts, sheet_counters, type_counters, combined_data = analyze_excel_file(
        args.file_path, args.length, args.type
    )
    
    # 显示结果
    if value_counts:
        print("\n总体统计结果:")
        print(f"'{args.length}'列的值分布:")
        
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
        
        # 显示线缆类型统计
        if type_counters:
            print(f"\n按'{args.type}'分组的统计:")
            
            # 计算每种类型的总数
            type_totals = {cable_type: sum(counter.values()) for cable_type, counter in type_counters.items()}
            
            # 按数量排序
            sorted_types = sorted(type_totals.items(), key=lambda x: x[1], reverse=True)
            
            # 打印表头
            print(f"{args.type:<20} {'数量':<10} {'百分比':<10}")
            print("-" * 40)
            
            # 打印每种类型的统计信息
            combined_total = sum(type_totals.values())
            for cable_type, count in sorted_types:
                percentage = (count / combined_total) * 100
                print(f"{str(cable_type):<20} {count:<10} {percentage:.2f}%")
            
            print("-" * 40)
            print(f"总计: {combined_total} 个组合")
        
        # 创建统计Excel文件
        create_statistics_excel(
            args.file_path, value_counts, sheet_counters, type_counters, combined_data,
            args.length, args.type
        )
    else:
        print("没有找到任何值进行统计")

if __name__ == "__main__":
    main()
