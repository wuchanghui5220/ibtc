#!/usr/bin/python3
# -*- coding: utf-8 -*-

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.gridspec as gs
import time
import subprocess
import math

def print_dashes(num=90):
    for i in range(num):
        print("-", end="")
    print()
def transform(x,n):
  return n * math.ceil(x/n)

print_dashes()    
EDR = 36
HDR = 40
NDR200 = 128
NDR = 64

ports = 0
speed = ""

ratio_input = input("Enter ratio (default is 1:1): ")
ratio = int(ratio_input) if ratio_input.strip() else 1
RA = ratio + 1
print("Ratio is " + str(RA))
print_dashes()
input_ports_str = input("""1: EDR
2: HDR
3: NDR200
4: NDR
please select your Speed: """)

input_ports = int(input_ports_str) if input_ports_str.strip() else 4
ports = {
    1: EDR,
    2: HDR,
    3: NDR200,
    4: NDR
}.get(input_ports, None)
speed = {
    1: "EDR",
    2: "HDR",
    3: "NDR200",
    4: "NDR"
}.get(input_ports, None)

ratio_text = ""
# Update ports based on RA and current ports
if RA == 2 and ports == EDR:
    bisection = math.ceil(ports / RA)
    ratio_text = "1:1"
    switch_tpye = "SB7800"
elif RA == 2 and ports == HDR:
    bisection = math.ceil(ports / RA)
    ratio_text = "1:1"
    switch_tpye = "QM8700"
elif RA == 2 and ports == NDR200:
    bisection = math.ceil(ports / RA)
    ratio_text = "1:1"
    switch_tpye = "QM9700"
elif RA == 2 and ports == NDR:
    bisection = math.ceil(ports / RA)
    ratio_text = "1:1"
    switch_tpye = "QM9700"
elif RA == 3 and ports == EDR:
    bisection = math.ceil(ports / RA)
    ratio_text = "1:2"
    switch_tpye = "SB7800"
elif RA == 3 and ports == HDR:
    bisection = 16
    ratio_text = "3:5"
    switch_tpye = "QM8700"
elif RA == 3 and ports == NDR:
    bisection = 20
    ratio_text = "1:2"
    switch_tpye = "QM9700"
else:
    bisection = 18
    ratio_text = "1:1"
    switch_tpye = "SB7800"
    
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
if speed == "EDR":
    Switch_OT = (spines + leafs) * 36
    Hca_OT = nodes
elif speed == "HDR":
    Spine2Leaf_OT_number = leafs * 20 * 2
    Leaf2Server_OT_number = nodes
    Switch_OT = Spine2Leaf_OT_number + Leaf2Server_OT_number
    Hca_OT = nodes
elif speed == "NDR":
    Spine2Leaf_OT_number = leafs * 16 * 2
    Leaf2Server_OT_number = math.ceil(nodes/2)
    Switch_OT = Spine2Leaf_OT_number + Leaf2Server_OT_number
    Hca_OT = nodes
elif speed == "NDR200":
    Spine2Leaf_OT_number = leafs * 16 * 2
    Leaf2Server_OT_number = math.ceil(nodes/2)
    Switch_OT = Spine2Leaf_OT_number + Leaf2Server_OT_number
    Hca_OT = nodes
print()

# spine to leaf cables
if ports == NDR200:
    spine_to_leaf_cables = int(leafs * (bisection / 2))
    leaf_to_server_cables = int(math.ceil(nodes/2))
else:
    spine_to_leaf_cables = int(leafs * bisection)
    leaf_to_server_cables = int(nodes)


print_dashes()
# Create graph
G = nx.Graph()

# Add spine switches nodes
for i in range(spines):
    G.add_node("Spine " + str(i), pos=(i, 2))

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
        G.add_edge("Spine " + str(i), "Leaf " + str(j))

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
gs = gs.GridSpec(2, 1, height_ratios=[7, 3])
ax1 = plt.subplot(gs[0, :]) # create a subplot in the first row
ax2 = plt.subplot(gs[1, :]) # create a subplot in the second row
gs.update(wspace=10, hspace=0.1)
ax2.axis("off")
nx.draw_networkx(G, pos, with_labels=False, ax=ax1, node_color=node_color, edge_color=edge_color_map)

tx, ty, tx_ = 0.036, 0.8, 0.1

# if use dac cable, 
leaf2spine_each_line = int(bisection/spines)
print(f"Leaf to Spine each line: {leaf2spine_each_line}")

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
print(f"Switch optical transceiver: {Spine2Leaf_OT_number} + {Leaf2Server_OT_number} = {Switch_OT}")
print("HCA optical transceiver: " + str(Hca_OT))

# ax2.legend(handles=legend_labels, loc='upper right', bbox_to_anchor=(1, 1)) # add legend to ax2
font = {'fontsize': 14, 'fontweight': 'bold'}
# 使用ax1.set_title方法来设置标题
ax1.set_title('Infiniband Topology Calculator v0.9.3', fontdict=font) # set the title for ax1
# Add information about the fabric to the canvas
ax1.text(0.89, 0.9, "ZhengYang", fontsize=12, transform=ax1.transAxes)
ax1.text(0.89, 0.85, "Technology", fontsize=9, transform=ax1.transAxes)
ax2.text(tx, ty, "Spine & Leaf: " + " (" + switch_tpye + ")", fontsize=10, transform=ax2.transAxes)
ax2.text(tx, ty - 0.14, str(spines) + "+" + str(leafs) + "=" + str(spines + leafs), fontsize=10, transform=ax2.transAxes)
if ports == NDR:
    ax2.text(tx, ty - 0.28, "MPO-12/APC Cables: ", fontsize=10, transform=ax2.transAxes)
else:
    ax2.text(tx, ty - 0.28, "All cables: ", fontsize=10, transform=ax2.transAxes)
if ports == NDR200:
    plt.text(tx, ty - 0.42, str(spine_to_leaf_cables) + "+" + str(leaf_to_server_cables) + "(1 to 2)" + "=" + str(all_cables), fontsize=10, transform=ax2.transAxes)
else:
    plt.text(tx, ty - 0.42, str(spine_to_leaf_cables) + "+" + str(leaf_to_server_cables) + "=" + str(all_cables), fontsize=10, transform=ax2.transAxes)
ax2.text(tx + 0.25, ty, "Speed: " + speed, fontsize=10, transform=ax2.transAxes)
ax2.text(tx + 0.25, ty - 0.14, "Ratio: " + ratio_text, fontsize=10, transform=ax2.transAxes)

if su != 0:
    ax2.text(tx + 0.25, ty - 0.28, "GPU SU: " + str(real_su), fontsize=10, transform=ax2.transAxes)

if s_su != 0 and su != 0:
    ax2.text(tx + 0.25, ty - 0.42, "Storage SU: " + str(real_s_su), fontsize=10, transform=ax2.transAxes)
elif s_su != 0 and su == 0:
    ax2.text(tx + 0.25, ty - 0.28, "Storage SU: " + str(real_s_su), fontsize=10, transform=ax2.transAxes)

if gpu_servers != 0:
    ax2.text(tx + 0.45, ty, "GPU Servers: " + str(gpu_server_num) + " [" + str(card_num) + "]", fontsize=10, transform=ax2.transAxes)

if storage_server_num != 0 and gpu_servers ==0:
    ax2.text(tx + 0.45, ty, "Storage Servers: " + str(storage_server_num) + " [" + str(s_card_num) + "]", fontsize=10, transform=ax2.transAxes)
elif storage_server_num != 0 and gpu_servers != 0:
    ax2.text(tx + 0.45, ty - 0.14, "Storage Servers: " + str(storage_server_num) + " [" + str(s_card_num) + "]", fontsize=10, transform=ax2.transAxes)

if cpu_server_num != 0 and gpu_servers == 0 and storage_server_num == 0:
    ax2.text(tx + 0.45, ty, "CPU Servers: " + str(cpu_server_num) + " [" + str(c_card_num) + "]", fontsize=10, transform=ax2.transAxes)
elif cpu_server_num != 0 and (gpu_servers == 0 or storage_server_num == 0):
    ax2.text(tx + 0.45, ty - 0.14, "CPU Servers: " + str(cpu_server_num) + " [" + str(c_card_num) + "]", fontsize=10, transform=ax2.transAxes)
elif cpu_server_num != 0 and gpu_servers != 0 and storage_server_num != 0:
    ax2.text(tx + 0.45, ty - 0.28, "CPU Servers: " + str(cpu_server_num) + " [" + str(c_card_num) + "]", fontsize=10, transform=ax2.transAxes)

if other_server_num == 0:
    pass
elif other_server_num != 0 and gpu_servers == 0 and storage_server_num == 0 and cpu_server_num == 0:
    ax2.text(tx + 0.45, ty, "Other: " + str(other_server_num) + " [" + str(o_card_num) + "]", fontsize=10, transform=ax2.transAxes)
elif other_server_num != 0 and ((gpu_servers == 0 and storage_server_num == 0) or (gpu_servers == 0 and cpu_server_num == 0) or (storage_servers == 0 and cpu_server_num ==0)):
    ax2.text(tx + 0.45, ty - 0.14, "Other: " + str(other_server_num) + " [" + str(o_card_num) + "]", fontsize=10, transform=ax2.transAxes)
elif other_server_num != 0 and (gpu_servers == 0 or storage_server_num == 0 or cpu_server_num == 0):
    ax2.text(tx + 0.45, ty - 0.28, "Other: " + str(other_server_num) + " [" + str(o_card_num) + "]", fontsize=10, transform=ax2.transAxes)
elif other_server_num != 0 and gpu_servers != 0 and storage_server_num != 0 and cpu_server_num != 0:
    ax2.text(tx + 0.45, ty - 0.42, "Other: " + str(other_server_num) + " [" + str(o_card_num) + "]", fontsize=10, transform=ax2.transAxes)

if ports == NDR:
    ax2.text(tx + 0.7, ty, f"800G OT: {Spine2Leaf_OT_number} + {Leaf2Server_OT_number} = {Switch_OT}", fontsize=10, transform=ax2.transAxes)
    ax2.text(tx + 0.7, ty - 0.14, "400G OT: " + str(Hca_OT), fontsize=10, transform=ax2.transAxes)
    if dac_cable_number > 0:
        ax2.text(tx + 0.7, ty - 0.28, "DAC (1to2)cables: " + str(dac_cable_number), fontsize=10, transform=ax2.transAxes)
elif ports == NDR200:
    ax2.text(tx + 0.7, ty, f"800G OT: {Spine2Leaf_OT_number} + {Leaf2Server_OT_number} = {Switch_OT}", fontsize=10, transform=ax2.transAxes)
    ax2.text(tx + 0.7, ty - 0.14, "400G OT: " + str(Hca_OT), fontsize=10, transform=ax2.transAxes)
plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)

current_time = time.strftime("%Y%m%d-%H%M%S")
filename = f'figure-{current_time}.png'
plt.savefig(filename, dpi=200, bbox_inches='tight', transparent=True)
# 要在屏幕显示图像，把下一行代码取消注释
# plt.show()

# 以下命令运行在Linux，如果要在windows系统运行，把以下代码全部注释！
# 获取html目录
sub_dir = 'html/ib'
ret = subprocess.run(['mkdir','-p', sub_dir])
#if ret.returncode == 0:
#  print(f'{sub_dir} created successfully!')
ret = subprocess.run(['pwd'], capture_output=True)
html_dir = ret.stdout.decode().strip() + '/' + sub_dir
# html_dir = "/home/admin/html/ib"

# 构造mv命令
cmd = ['mv', filename, html_dir]

# 调用mv命令移动文件
subprocess.call(cmd)

# 生成HTML代码
html = f'<img src="{filename}" alt="ZhengYang Technology">'

# 将HTML代码写入文件
with open('html/ib/index.html', 'w') as f:
  f.write(html)
