#!/usr/bin/python3
# -*- coding: utf-8 -*-

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import pandas as pd
import time
import subprocess
import math
import re
import openpyxl
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox


def print_dashes(num=66):
    for i in range(num):
        print("-", end="")
    print()
def transform(x,n):
  return n * math.ceil(x/n)

def add_logo(ax, ports, leafs):
    zoom = 0.15
    x, y = 0.9, 0.9

    if ports == 64:
        if leafs <= 8:
            pass
        elif leafs <= 16:
            pass
        elif leafs <= 32:
            zoom = 0.2
        elif leafs <= 40:
            zoom = 0.24
            x = 0.93
        elif leafs <= 48:
            zoom = 0.24
            x = 0.93
        else:
            zoom = 0.3
            y = 0.86

    elif ports == 40:
        if leafs <= 12:
            zoom = 0.1
        elif leafs <= 20:
            x = 0.9
        elif leafs <= 24:
            x = 0.93
        elif leafs <= 28:
            zoom = 0.2
        elif leafs > 40:
            zoom = 0.25
            y = 0.86

    im = OffsetImage(logo, zoom=zoom)
    ab = AnnotationBbox(im, (x, y), xycoords=ax.transAxes, boxcoords="offset points", frameon=False)
    ax.add_artist(ab)

def replace_line(file, line_no, new_text):
    with open(file) as f:
        lines = f.readlines()
        del lines[line_no - 1]    
        lines.insert(line_no - 1, str(new_text) + '\n')
    
    with open(file, 'w') as f:
        f.writelines(lines)

# 生成leaf到spine的端口映射列表
def generate_port_mappings_combined(leaf_count, spine_count, leaf_ports_per_spine, leaf_start_port, spine_start_port, reverse=False):
    mappings = []
    for leaf_index in range(leaf_count):
        leaf_name = f'leaf{leaf_index + 1:02d}'
        for spine_index in range(spine_count):
            spine_name = f'spine{spine_index + 1:02d}'
            for port_index in range(leaf_ports_per_spine):
                if not reverse:
                    leaf_port = leaf_start_port + port_index + (leaf_ports_per_spine * spine_index)
                    spine_port = spine_start_port + port_index + (leaf_ports_per_spine * leaf_index)
                    local = f'{leaf_name}-{leaf_port}'
                    remote = f'{spine_name}-{spine_port}'
                else:
                    spine_port = spine_start_port + port_index + (leaf_ports_per_spine * leaf_index)
                    leaf_port = leaf_start_port + port_index + (leaf_ports_per_spine * spine_index)
                    local = f'{spine_name}-{spine_port}'
                    remote = f'{leaf_name}-{leaf_port}'
                mapping = {
                    "本端": local,
                    "对端": remote
                }
                mappings.append(mapping)
    return mappings

# 生成leaf到server的端口映射列表
def generate_leaf_to_server_mappings_combined(server_count, leaf_count, ports_per_server, switch_ports, reverse=False):
    group_size = int(switch_ports / 2)
    mappings = []
    ports_per_leaf = server_count // (leaf_count // ports_per_server) if server_count >= group_size else server_count

    for server_index in range(server_count):
        server_name = f'server{server_index + 1:02d}'
        group_offset = (server_index // group_size) * ports_per_server

        for port_index in range(ports_per_server):
            leaf_number = group_offset + port_index + 1
            leaf_name = f'leaf{leaf_number:02d}'
            leaf_port = server_index % group_size + 1

            if not reverse:
                local = f'{leaf_name}-{leaf_port}'
                remote = f'{server_name}-{port_index + 1}'
            else:
                local = f'{server_name}-{port_index + 1}'
                remote = f'{leaf_name}-{leaf_port}'

            mapping = {
                "本端": local,
                "对端": remote
            }
            mappings.append(mapping)

    return mappings

def process_data(df, prefix, count):
    # 创建一个空的DataFrame用于存放最终数据
    final_df = pd.DataFrame()

    # 循环处理prefix01到prefixN
    for i in range(1, count + 1):
        item_name = f'{prefix}{i:02}'  # 格式化item名称
        # 筛选包含当前item名称的行，使用正则表达式匹配整个单词
        regex_pattern = f'\\b{item_name}\\b'  # 构建正则表达式
        df_item = df[df['本端'].str.contains(regex_pattern, na=False, regex=True)]
        
        # 重置索引，为了转置后的DataFrame保持干净的索引
        df_item.reset_index(drop=True, inplace=True)
        
        # 转置DataFrame，将两列转换为两行
        df_item_transposed = df_item.T
        
        # 重置索引，这样列名会变成一行数据
        df_item_transposed.reset_index(inplace=True)
        
        # 转置后的DataFrame已经是两行了，直接追加到最终的DataFrame中
        final_df = pd.concat([final_df, df_item_transposed], ignore_index=True)

        # 追加一个空行
        empty_row = pd.DataFrame([['']*len(df_item_transposed.columns)], columns=df_item_transposed.columns)
        final_df = pd.concat([final_df, empty_row], ignore_index=True)

    return final_df


ndr_products = [
{'name':'400G IB交换机','model':'MQM9790-NS2F','desc':'NVIDIA Quantum-2 based NDR InfiniBand Switch, 64 NDR ports, 32 OSFP ports, 2 Power Supplies (AC), Standard depth, Unmanaged, P2C airflow, RailKit', 'qty':22},
{'name':'400G IB交换机','model':'MQM9700-NS2F','desc':'NVIDIA Quantum-2 based NDR InfiniBand Switch, 64 NDR ports, 32 OSFP ports, 2 Power Supplies (AC), Standard depth, Managed, P2C airflow, Rail Kit', 'qty':22 },
{'name':'800G 光模块','model':'MMA4Z00-NS','desc':'NVIDIA twin port transceiver, 800Gbps,2xNDR, OSFP, 2xMPO12 APC, 850nm MMF, up to 50m, finned', 'qty':22},
{'name':'400G 光模块','model':'MMA4Z00-NS400','desc':'NVIDIA single port transceiver, 400Gbps,NDR, OSFP, MPO12 APC, 850nm MMF,  up to 50m, flat top', 'qty':22 },
{'name':'MPO12-APC光纤','model':'MFP7E10-N030','desc':'NVIDIA passive fiber cable, MMF, MPO12 APC to MPO12 APC, 30m', 'qty':22},
{'name':'MPO12-APC 1分2光纤','model':'MFP7E20-N030','desc':'NVIDIA passive fiber cable, MMF, MPO12 APC to 2xMPO12 APC, 30m', 'qty':22},
]

hdr_products = [
{'name':'200G IB交换机','model':'MQM8790-HS2F', 'desc':'Mellanox Quantum HDR InfiniBand Switch, 40 QSFP56 ports, 2 Power Supplies (AC), unmanaged, standard depth, P2C airflow, Rail Kit', 'qty':22},
{'name':'200G IB交换机','model':'MQM8700-HS2F', 'desc':'Mellanox Quantum HDR InfiniBand Switch, 40 QSFP56 ports, 2 Power Supplies (AC), x86 dual core, standard depth, P2C airflow, Rail Kit', 'qty':22},
{'name':'200G IB AOC线缆', 'model':'MFS1S00-H030V', 'desc':'Mellanox active optical cable, up to 200Gb/s IB HDR, QSFP56, 30m', 'qty':22},
{'name':'200G IB AOC 1分2线缆', 'model':'MFS1S50-H030V','desc':'Mellanox active optical cable, 200Gb/s to 2x100Gb/s IB HDR, QSFP56 to 2x QSFP56, 30m', 'qty':22},
]

def generate_table_tr(products, model, qty):
    new_table_tr = ''

    for product in products:
        if product['model'] == model:
            new_table += '<tr>'
            new_table += '  <td>{}</td>'.format(product['name'])
            new_table += '  <td>{}</td>'.format(product['model'])
            new_table += '  <td>{}</td>'.format(product['desc'])
            new_table += '  <td>{}</td>'.format(qty)
            new_table += '</tr>'

    return new_table_tr

logo = mpimg.imread('elite.png')

print_dashes()    
EDR = 36
HDR = 40
NDR200 = 128
NDR = 64
ports = 0
speed = ""
products = []
switch_name = ""
switch_type = ""
cable_name = ""
cable2_name = ""
cable_type = ""
cable2_type = ""
ot_800 = ""
ot_400 = ""

ratio_input = input("Enter ratio (default is 1:1): ")
ratio = int(ratio_input) if ratio_input.strip() else 1
RA = ratio + 1
print("Ratio is " + str(RA))
print_dashes()
input_ports_str = input("""1: HDR
2: NDR
please select your Speed: """)

input_ports = int(input_ports_str) if input_ports_str.strip() else 2
ports = {
    1: HDR,
    2: NDR
}.get(input_ports, None)
speed = {
    1: "HDR",
    2: "NDR"
}.get(input_ports, None)

if speed == "NDR":
    products = ndr_products
    switch_name = "400G IB 交换机"
    cable_name = "MPO12-APC 光纤"
    cable2_name = "MPO12-APC 1分2光纤"
    cable_type = "MFP7E10-N030"
    cable2_type = "MFP7E20-N030"
    ot_800 = "MMA4Z00-NS"
    ot_400 = "MMA4Z00-NS400"

else:
    products = hdr_products
    switch_name = "200G IB 交换机"
    cable_name = "200G IB AOC 线缆"
    cable2_name = "200G IB AOC 1分2线缆"
    cable_type = "MFS1S00-H030V"
    cable2_type = "MFS1S50-H030V"

ratio_text = ""
# Update ports based on RA and current ports
if RA == 2 and ports == HDR:
    bisection = math.ceil(ports / RA)
    ratio_text = "1:1"
    switch_type = "MQM8790-HS2F"
elif RA == 2 and ports == NDR:
    bisection = math.ceil(ports / RA)
    ratio_text = "1:1"
    switch_type = "MQM9790-NS2F"
elif RA == 3 and ports == HDR:
    bisection = 16
    ratio_text = "3:5"
    switch_type = "MQM8790-HS2F"
elif RA == 3 and ports == NDR:
    bisection = 20
    ratio_text = "1:2"
    switch_type = "MQM9790-NS2F"
else:
    bisection = 32
    ratio_text = "1:1"
    switch_type = "MQM9790-NS2F"
    
print("Fabric speed is " + speed)

# bisection = math.ceil(ports / RA)
print("bisection is " + str(bisection) )

factors = []
# Find the factors of bisection and append them to the factors list
for i in range(1, bisection + 1):
    if bisection % i == 0:
        factors.append(i)
print(str(bisection) + " 's factors is " + str(factors))
print_dashes()


spines = 0
leafs = 0
gpu_leafs = 0
storage_leafs = 0
cpu_leafs = 0
other_leafs = 0
gpu_type = ""
gpu_servers = 0
storage_servers = 0
cpu_servers = 0
other_servers = 0
real_su = 0
real_s_su = 0
real_c_su = 0
real_o_su = 0
card_num = 0
su_nodes = 0
su = 0
# input GPU server number
gpu_server_num_input = input("Enter GPU Server Numbers: ")
gpu_server_num = int(gpu_server_num_input) if gpu_server_num_input.isdigit() else 0
if  gpu_server_num == 0:
    card_num = 0
else:
    gpu_type = input("Enter GPU model(Default H800): ")
    if gpu_type == "":
        gpu_type = "H800"
    card_num_input = input("Select GPU server's NIC Number(1 or 2 or 4 or 8): ")
    card_num = int(card_num_input) if card_num_input in ["1", "2", "4", "8"] else 8
    if ports == NDR200 and (card_num == 4 or card_num == 8):
        su_nodes = card_num * (bisection)
        print("GPU YES YOU ARE HERE")
    else:
        su_nodes = card_num * bisection
    su = math.ceil((gpu_server_num * card_num) / su_nodes)
    gpu_leafs = card_num * su
    gpu_servers = gpu_leafs
    real_su = round(gpu_server_num * card_num/su_nodes, 2)
gpu_nodes = gpu_server_num * card_num
rest_gpu_switch_ports = su*su_nodes - gpu_server_num*card_num
print("GPU nodes: " + str(gpu_nodes))
print("The SU is " + str(real_su))
print("So math.ceil(SU) is " + str(su))
print("gpu_leafs original value: " + str(gpu_leafs))
print("GPU rest_gpu_switch_ports  is " + str(rest_gpu_switch_ports))
print_dashes()
# input storage server number
storage_server_num_input = input("Enter Storage Server Numbers: ")
storage_server_num = int(storage_server_num_input) if storage_server_num_input.isdigit() else 0
s_su_nodes = 0
s_su = 0

if  storage_server_num == 0:
    s_card_num = 0
else:
    s_card_num_input = input("Select Storage server's NIC Number(1 or 2 or 4): ")
    s_card_num = int(s_card_num_input) if s_card_num_input in ["1", "2", "4"] else 1
    if ports == NDR200 and (s_card_num == 1 or s_card_num == 2):
        s_su_nodes = s_card_num * (bisection)
        print("Storage YES YOU ARE HERE")
    else:
        s_su_nodes = s_card_num * bisection
    s_su = math.ceil((storage_server_num * s_card_num) / s_su_nodes)
    real_s_su = round(storage_server_num * s_card_num/s_su_nodes, 2)
    storage_leafs = (storage_server_num * s_card_num - rest_gpu_switch_ports) / bisection
    if storage_leafs > 0:
        storage_leafs = transform(storage_leafs, s_card_num)
    else:
        storage_leafs = 0
    storage_servers = storage_leafs
storage_nodes = storage_server_num * s_card_num
rest_storage_switch_ports = (gpu_leafs + storage_leafs) * bisection - (gpu_nodes + storage_nodes)
print("Storage nodes: " + str(storage_nodes))
print("The S_SU is " + str(real_s_su))
print("So math.ceil(SU) is " + str(s_su))
print("storage_leafs transform value: " + str(storage_leafs))
print("Storage rest_storage_switch_ports  is " + str(rest_storage_switch_ports))
print_dashes()
# input cpu server number
cpu_server_num_input = input("Enter CPU Server Numbers: ")
cpu_server_num = int(cpu_server_num_input) if cpu_server_num_input.isdigit() else 0
c_su_nodes = 0
c_su = 0

if  cpu_server_num == 0:
    c_card_num = 0
else:
    c_card_num_input = input("Select CPU server's NIC Number(1 or 2): ")
    c_card_num = int(c_card_num_input) if c_card_num_input in ["1", "2"] else 1
    if ports == NDR200 and (c_card_num == 1 or c_card_num == 2):
        c_su_nodes = c_card_num * (bisection)
        print("CPU YES YOU ARE HERE")
    else:
        c_su_nodes = c_card_num * bisection
    c_su = math.ceil((cpu_server_num * c_card_num) / c_su_nodes)
    real_c_su = round(cpu_server_num * c_card_num/c_su_nodes, 2)
    cpu_leafs = (cpu_server_num * c_card_num - rest_storage_switch_ports) / bisection
    if cpu_leafs > 0:
        cpu_leafs = transform(cpu_leafs, c_card_num)
    else:
        cpu_leafs = 0
    cpu_servers = cpu_leafs
cpu_nodes = cpu_server_num * c_card_num
rest_cpu_switch_ports = (gpu_leafs + storage_leafs + cpu_leafs) * bisection - (gpu_nodes + storage_nodes + cpu_nodes)
print("CPU nodes: " + str(cpu_nodes))
print("The C_SU is " + str(real_c_su))
print("So math.ceil(SU) is " + str(c_su))
print("CPU_leafs transform value: " + str(cpu_leafs))
print("CPU rest_CPU_switch_ports  is " + str(rest_cpu_switch_ports))
print_dashes()
# input other server number
other_server_num_input = input("Enter Other Server Numbers: ")
other_server_num = int(other_server_num_input) if other_server_num_input.isdigit() else 0
o_su_nodes = 0
o_su = 0

if  other_server_num == 0:
    o_card_num = 0
else:
    o_card_num_input = input("Select Other server's NIC Number(1 or 2): ")
    o_card_num = int(o_card_num_input) if o_card_num_input in ["1", "2"] else 1
    if ports == NDR200 and (o_card_num == 1 or o_card_num == 2):
        o_su_nodes = o_card_num * (bisection)
        print("Other YES YOU ARE HERE")
    else:
        o_su_nodes = o_card_num * bisection
    o_su = math.ceil((other_server_num * o_card_num) / o_su_nodes)
    real_o_su = round(other_server_num * o_card_num/o_su_nodes, 2)
    other_leafs = (other_server_num * o_card_num - rest_cpu_switch_ports) / bisection
    if other_leafs > 0:
        other_leafs = transform(other_leafs, o_card_num)
    else:
        other_leafs = 0
    other_servers = other_leafs
other_nodes = other_server_num * o_card_num
rest_other_switch_ports = (gpu_leafs + storage_leafs + cpu_leafs + other_leafs) * bisection - (gpu_nodes + storage_nodes + cpu_nodes + other_nodes)
print("Other nodes: " + str(other_nodes))
print("The O_SU is " + str(real_o_su))
print("So math.ceil(SU) is " + str(o_su))
print("Other_leafs transform value: " + str(other_leafs))
print("Other rest_other_switch_ports  is " + str(rest_other_switch_ports))
print_dashes()

# dac cable choice
dac_cable_number_input = input("Enter DAC cables: ")
dac_cable_number = int(dac_cable_number_input) if dac_cable_number_input.isdigit() else 0
print(dac_cable_number)
print_dashes()

# servers and nodes
server_num = gpu_server_num + storage_server_num + cpu_server_num + other_server_num
print("Ther server Number is :" + str(server_num))
nodes = gpu_nodes + storage_nodes + cpu_nodes + other_nodes
print("All nodes is :" + str(nodes))

# leaf and spine switch
leaf_used_by_nodes = math.ceil(nodes / (ports - bisection))
print("The nodes/bisection = The leaf used by nodes is :" + str(leaf_used_by_nodes))

leafs = gpu_leafs + storage_leafs + cpu_leafs + other_leafs

spines = math.ceil(leafs * bisection / ports)
if spines not in factors:
    for factor in factors:
        if factor > spines:
            spines = factor
            break
print("\nspine switches: " + str(spines))
print("leaf switches: " + str(leafs))
print("Ratio is " + ratio_text)

# Optical Transcevier
Spine2Leaf_OT_number = 0
Leaf2Server_OT_number = 0
Switch_OT = 0
Hca_OT = 0
if speed == "NDR":
    Spine2Leaf_OT_number = leafs * 16 * 2
    Leaf2Server_OT_number = math.ceil(nodes/2)
    Switch_OT = Spine2Leaf_OT_number + Leaf2Server_OT_number
    Hca_OT = nodes
print()

# spine to leaf cables
spine_to_leaf_cables = int(leafs * bisection)
# leaf to server cables
leaf_to_server_cables = int(nodes)


print_dashes()
# Create graph
G = nx.Graph()

# Add spine switches nodes
spacing = (leafs - spines)/2
spacing = round(spacing, 2)
for i in range(spines):
    G.add_node("Spine " + str(i+spacing), pos=(i+spacing, 2))

# Add leaf switches nodes
for i in range(leafs):
    G.add_node("Leaf " + str(i), pos=(i, 1.2))

# Add servers
# for i in range(servers):
#     G.add_node("Server " + str(i+1), pos=(i+1, 0.7))
for i in range(gpu_servers):
    G.add_node("Gpu_Server " + str(i), pos=(i, 0.7))
for i in range(storage_servers):
    G.add_node("Storage_Server " + str(i+gpu_leafs), pos=(i+gpu_leafs, 0.7))
for i in range(cpu_servers):
    G.add_node("Cpu_Server " + str(i + gpu_leafs + storage_leafs), pos=(i + gpu_leafs + storage_leafs, 0.7))
for i in range(other_servers):
    G.add_node("Other_Server " + str(i+gpu_leafs+storage_leafs+cpu_leafs), pos=(i+gpu_leafs+storage_leafs+cpu_leafs, 0.7))
# Print node coordinates
pos = nx.get_node_attributes(G, 'pos')
# for node in G.nodes():
#     print(node + " coordinates: " + str(pos[node]))

# Add edges between spine and leaf switches
for i in range(spines):
    for j in range(leafs):
        G.add_edge("Spine " + str(i+spacing), "Leaf " + str(j))

# add leaf to all nodes edge
   
# add gpu edge
if gpu_server_num != 0 and card_num != 1:  
    gpu_leafs_list = list(range(gpu_leafs))
    gpu_leafs_spilt_list = [gpu_leafs_list[i:i+card_num] for i in range(0, len(gpu_leafs_list), card_num)]
    gpu_servers_list = list(range(gpu_servers))
    gpu_servers_spilt_list = [gpu_servers_list[i:i+card_num] for i in range(0, len(gpu_servers_list), card_num)]
# Add edges between leaf switches and servers
    for a in range(len(gpu_leafs_spilt_list)):
        for b in range(len(gpu_servers_spilt_list)):
            if b == a:
                for i in gpu_leafs_spilt_list[a]:
                    for j in gpu_servers_spilt_list[b]:
                        G.add_edge("Leaf " + str(i), "Gpu_Server " + str(j))
# Add edges for leaf to server, Like this, leaf1 to server1, leaf2 to server2, and so on
elif gpu_server_num != 0 and card_num == 1:
    for i in range(gpu_leafs):
        G.add_edge("Leaf " + str(i), "Gpu_Server " + str(i))

# add storage edge
if storage_server_num != 0 and s_card_num != 1:  
    storage_leafs_list = list(range(gpu_leafs, gpu_leafs + storage_leafs))
    storage_leafs_spilt_list = [storage_leafs_list[i:i+s_card_num] for i in range(0, len(storage_leafs_list), s_card_num)]
    storage_servers_list = list(range(gpu_servers, gpu_servers + storage_servers))
    storage_servers_spilt_list = [storage_servers_list[i:i+s_card_num] for i in range(0, len(storage_servers_list), s_card_num)]
# Add edges between leaf switches and servers
    for a in range(len(storage_leafs_spilt_list)):
        for b in range(len(storage_servers_spilt_list)):
            if b == a:
                for i in storage_leafs_spilt_list[a]:
                    for j in storage_servers_spilt_list[b]:
                        G.add_edge("Leaf " + str(i), "Storage_Server " + str(j))
elif storage_server_num != 0 and s_card_num == 1:
    for i in range(gpu_leafs, gpu_leafs + storage_leafs):
        G.add_edge("Leaf " + str(i), "Storage_Server " + str(i))
# add cpu edge
if cpu_server_num != 0 and c_card_num != 1:  
    cpu_leafs_list = list(range(gpu_leafs + storage_leafs, gpu_leafs + storage_leafs+ cpu_leafs))
    cpu_leafs_spilt_list = [cpu_leafs_list[i:i+c_card_num] for i in range(0, len(cpu_leafs_list), c_card_num)]
    cpu_servers_list = list(range(gpu_servers + storage_leafs, gpu_servers + storage_servers + cpu_leafs))
    cpu_servers_spilt_list = [cpu_servers_list[i:i+c_card_num] for i in range(0, len(cpu_servers_list), c_card_num)]
# Add edges between leaf switches and servers
    for a in range(len(cpu_leafs_spilt_list)):
        for b in range(len(cpu_servers_spilt_list)):
            if b == a:
                for i in cpu_leafs_spilt_list[a]:
                    for j in cpu_servers_spilt_list[b]:
                        G.add_edge("Leaf " + str(i), "Cpu_Server " + str(j))
elif cpu_server_num != 0 and c_card_num == 1:
    for i in range(gpu_leafs + storage_leafs, gpu_leafs + storage_leafs + cpu_leafs):
        G.add_edge("Leaf " + str(i), "Cpu_Server " + str(i))
# add other edge
if other_server_num != 0:
    for i in range(gpu_leafs + storage_leafs + cpu_leafs, leafs):
        G.add_edge("Leaf " + str(i), "Other_Server " + str(i))


# Add edge color map
edge_color_map = []
for edge in G.edges():
    if 'Spine' in edge[0]:
        edge_color_map.append('skyblue')
    elif 'Gpu_Server' in edge[1]:
        edge_color_map.append('green')
    elif 'Storage_Server' in edge[1]:
        edge_color_map.append('lightgreen')
    elif 'Cpu_Server' in edge[1]:
        edge_color_map.append('black')
    else:
        edge_color_map.append('black')

# Set node color map 
node_color = ['blue' if 'Spine' in node else 'blue' if 'Leaf' in node else 'green' if 'Gpu_Server' in node else 'lightgreen' if 'Storage_Server' in node else 'gray' for node in G.nodes()]

# Draw graph
pos = nx.get_node_attributes(G, 'pos')
# fig, ax = plt.subplots(figsize=(10, 5))
fig = plt.figure(figsize=(10, 5))
if spines > 20:
    fig.set_size_inches(25, 5)
elif spines > 15:
    fig.set_size_inches(15, 5)
elif spines > 10:
    fig.set_size_inches(10, 5)
# create a grid with 2 rows and 1 column, the first row is 70% and the second row is 30% of the height
gs = gs.GridSpec(2, 1, height_ratios=[10, 0])
ax1 = plt.subplot(gs[0, :]) # create a subplot in the first row
ax2 = plt.subplot(gs[1, :]) # create a subplot in the second row
gs.update(wspace=10, hspace=0.1)
ax2.axis("off")
nx.draw_networkx(G, pos, with_labels=False, ax=ax1, node_color=node_color, edge_color=edge_color_map)
ax1.set_xlabel(str(gpu_server_num) + " " + gpu_type + " " + str(card_num) + "*" + speed + " InfiniBand Network Topology", fontdict={'size': 15})

tx, ty, tx_ = 0.036, 0.8, 0.1

# leaf to spine line 
leaf2spine_each_line = int(bisection/spines)
print(f"Leaf to Spine each line: {leaf2spine_each_line}")
uplink_group = spines

if dac_cable_number > 0:
    leaf_to_server_cables = leaf_to_server_cables - (dac_cable_number * 2)
    Leaf2Server_OT_number = Leaf2Server_OT_number - dac_cable_number
    Switch_OT = Spine2Leaf_OT_number + Leaf2Server_OT_number
    Hca_OT = Hca_OT - (dac_cable_number * 2)

all_cables = spine_to_leaf_cables + leaf_to_server_cables
max_leaf_to_server_cables = leafs * (ports - bisection)

print()
print("spine to leaf cables: " + str(spine_to_leaf_cables))
print("leaf to server cables: " + str(leaf_to_server_cables) + " (Max:" + str(max_leaf_to_server_cables) + ")")

print("all cables: " + str(all_cables))
print()

# ax2.legend(handles=legend_labels, loc='upper right', bbox_to_anchor=(1, 1)) # add legend to ax2
font = {'fontsize': 14, 'fontweight': 'bold'}
# 使用ax1.set_title方法来设置标题
ax1.set_title('Infiniband Topology Calculator v0.12.0', fontdict=font) # set the title for ax1
# Add Logo information about the fabric to the canvas
add_logo(ax1, ports, leafs)

plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
current_time = time.strftime("%Y%m%d-%H%M%S")
png_filename = f'figure-{current_time}.png'
plt.savefig(png_filename, dpi=300, bbox_inches='tight', transparent=True)

print_dashes()
#print("cable_type" + cable_type)

data = []
data.append({'name': 'spine_switch', 'model': switch_type, 'num': spines, 'note': 'Spine 交换机'})
data.append({'name': 'leaf_switch', 'model': switch_type, 'num': leafs, 'note': 'Leaf 交换机'})
data.append({'name': 'spine_to_leaf_cables','model': cable_type, 'num': spine_to_leaf_cables, 'note': 'Spine 到 Leaf 之间互连的线缆'})
data.append({'name': 'leaf_to_server_cables', 'model': cable_type, 'num': leaf_to_server_cables, 'note': 'Leaf 到 Server 之间互连的线缆'})
#if cable2_type != '':
#    data.append({'name': 'leaf_to_server2_cables', 'model': cable2_type, 'num': leaf_to_server2_cables})

if speed == "NDR":
    data.append({'name': 'spine_to_leaf_ot', 'model': 'MMA4Z00-NS', 'num': Spine2Leaf_OT_number, 'note': 'Spine 到 Leaf 之间互连 800G 模块'})
    data.append({'name': 'leaf_to_server_ot', 'model':'MMA4Z00-NS', 'num': Leaf2Server_OT_number, 'note': 'Leaf 到 Server 交换机端 800G 模块'})
    data.append({'name': 'hca_ot', 'model': 'MMA4Z00-NS400', 'num': Hca_OT, 'note': '网卡端 400G 模块'})


print("spines: " + str(spines))
print("leafs: " + str(leafs))
print("spine to leaf cable: " + str(spine_to_leaf_cables))
print("leaf to server cables: " + str(leaf_to_server_cables) + " (Max:" + str(max_leaf_to_server_cables) + ")")
if speed == "NDR":
    print(f"Switch optical transceiver: {Spine2Leaf_OT_number} + {Leaf2Server_OT_number} = {Switch_OT}")
    print("HCA optical transceiver: " + str(Hca_OT))

with open("index.html", encoding='utf-8') as f:
    content = f.read()
pattern = r"<img.*?src=\"(.*?)\".*?>"
new_content = re.sub(pattern, f'<img src="{png_filename}">', content)
pattern = r'<img.*?id="myImg" src="(.*?)">'
new_content = re.sub(pattern, r'<img id="myImg" src="' + png_filename + r'">', content)
with open("index.html", 'w', encoding='utf-8') as f:
    f.write(new_content)


#print(data)
lines = {
    45: switch_name,
    48: switch_type,
    51: ports, 
    53: speed,
    
    60: cable_name,
    63: cable_type,
    66: leaf2spine_each_line,
    68: uplink_group,
    70: spines,
    
    78: gpu_type, 
    81: card_num,
    83: speed,
    
    91: cable_name,
    94: cable_type,
    97: card_num, 
    99: card_num
}

for line, val in lines.items():
    replace_line('index.html', line, val)

# Leaf到Spine的端口映射列表，相关参数和执行结果
leaf_count = leafs # leaf交换机的数量
spine_count = spines  # spine交换机的数量
leaf_ports_per_spine = leaf2spine_each_line  # 每个spine交换机映射的leaf端口数量
leaf_start_port = int(ports / 2) + 1 # leaf交换机的起始端口号
spine_start_port = 1  # spine交换机的起始端口号

# 生成映射列表
port_mappings_combined = generate_port_mappings_combined(leaf_count, spine_count, leaf_ports_per_spine, leaf_start_port, spine_start_port)
port_mappings_combined_reverse = generate_port_mappings_combined(leaf_count, spine_count, leaf_ports_per_spine, leaf_start_port, spine_start_port, reverse=True)

# Leaf到Server的端口映射列表，相关参数和执行结果
server_count = gpu_server_num  # 服务器的数量
leaf_count = leafs    # leaf交换机的数量
ports_per_server = card_num # 每台服务器的网卡端口数量
switch_ports = ports   # 交换机的端口数量

# 生成映射列表
leaf_to_server_mappings_combined = generate_leaf_to_server_mappings_combined(server_count, leaf_count, ports_per_server, switch_ports)
server_to_leaf_mappings_combined = generate_leaf_to_server_mappings_combined(server_count, leaf_count, ports_per_server, switch_ports, reverse=True)


current_time = time.strftime("%Y%m%d-%H%M%S")
excel_filename = f'{gpu_server_num}_{gpu_type}_{card_num}x{speed}_ib_port_mapping_{current_time}.xlsx'
excel_filename2 = f'{gpu_server_num}_{gpu_type}_{card_num}x{speed}_ib_device_port_mapping_{current_time}.xlsx'
# 创建一个Excel文件并添加所有工作表
with pd.ExcelWriter(excel_filename) as writer:
    # 保存leaf到spine的映射到sheet1
    pd.DataFrame(port_mappings_combined).to_excel(writer, index=False, sheet_name='Leaf_to_Spine')
    # 保存spine到leaf的映射到sheet2
    pd.DataFrame(port_mappings_combined_reverse).to_excel(writer, index=False, sheet_name='Spine_to_Leaf')
    # 保存leaf到server的映射到sheet3
    pd.DataFrame(leaf_to_server_mappings_combined).to_excel(writer, index=False, sheet_name='Leaf_to_Server')
    # 保存server到leaf的映射到sheet4
    pd.DataFrame(server_to_leaf_mappings_combined).to_excel(writer, index=False, sheet_name='Server_to_Leaf')


# 读取Excel文件中的所有sheet
xls = pd.ExcelFile(excel_filename)

# 定义每个sheet的搜索条件和数量
sheet_conditions = {
    'Leaf_to_Spine': ('leaf', leafs),  # 根据实际情况调整leaf的数量
    'Spine_to_Leaf': ('spine', spines),  # 根据实际情况调整spine的数量
    'Leaf_to_Server': ('leaf', leafs),  # 根据实际情况调整leaf的数量
    'Server_to_Leaf': ('server', gpu_server_num),  # 根据实际情况调整server的数量
}

# 创建一个Excel写入器
writer = pd.ExcelWriter(excel_filename2)

# 循环遍历所有sheet
for sheet_name, (prefix, count) in sheet_conditions.items():
    # 读取当前sheet的数据
    df = pd.read_excel(xls, sheet_name=sheet_name)

    # 处理数据，并获取新的DataFrame
    new_df = process_data(df, prefix, count)

    # 将处理后的数据写入新的Excel文件的对应sheet中
    new_df.to_excel(writer, sheet_name=sheet_name, index=False)

# 保存新的Excel文件
writer.close()

# 设置规则文件命名
#current_time = time.strftime("%Y%m%d-%H%M%S")
replace_rules_file = f'replace_rules-{current_time}.xlsx'

# 创建一个新的工作簿
workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.title = '替换规则'

# 添加列标题
sheet['A1'] = '模板名称'
sheet['B1'] = '项目名称'

# 自动生成leaf01到leaf20以及spine01到spine10
for i in range(1, leafs + 1):
    sheet[f'A{i+1}'] = f'leaf{i:02d}'

for i in range(1, spines + 1):
    sheet[f'A{i+ leafs + 1}'] = f'spine{i:02d}'

# 添加server01到serverN
for i in range(1, gpu_server_num + 1):
    sheet[f'A{i+ leafs + spines + 1}'] = f'server{i:02d}'

# 保存工作簿
workbook.save(replace_rules_file)

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.splitlines()
    del lines[122:]

    for item in data:
        model = item['model']
        qty = item['num']
        note = item['note']
        for product in products:
            if product['model'] == model:
                lines.append('<tr>')
                lines.append('<td>{}</td>'.format(product['name']))
                lines.append('<td>{}</td>'.format(product['model']))
                lines.append('<td>{}</td>'.format(product['desc']))
                lines.append('<td>{}</td>'.format(qty))
                lines.append('<td>{}</td>'.format(note))
                lines.append('</tr>')
    # 重新追加结尾标签
    lines.append('        </table>')
    lines.append('    </div>')
    lines.append('    <script src="script.js"></script>')
    html_line = f'<footer><p>Copyright © 2024 Vincent@nvlink.vip <a href="{excel_filename}">pm</a><a href="modified_{excel_filename}">Mpm</a> <a href="{excel_filename2}">dm</a><a href="modified_{excel_filename2}">Mdm</a></p></footer>'
    lines.append(html_line)
    lines.append('    </body>') 
    lines.append('</html>')

    content = "\n".join(lines)
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
