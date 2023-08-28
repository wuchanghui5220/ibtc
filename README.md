# ibtc
An Infiniband Fabric Topology Calculator Python descript.

# run ibtc.py 
![image](https://github.com/wuchanghui5220/ibtc/assets/33740652/20f23689-96ce-4b25-b61c-08edf3c55a37)

# run fwlink.py, will print a firmware link to download

# run ofde.py, will print a ofed link to downlad


# a demo
    admin@ip-172-31-13-238:~$ ./fwlink.py 
     1: bf3
     2: bf2
     3: cx7
     4: cx6de
     5: cx6lx
     6: cx6dx
     7: cx6en
     8: cx6ib
     9: cx5en
    10: cx5ib
    11: cx4lx
    12: cx4en
    13: cx4ib
    14: cx3proen
    15: cx3proib
    16: cx3en
    17: cx3ib
    18: quantum2
    19: quantum
    20: switchib2
    21: switchib
            
    Enter a number: 19
    当前固件版本：
    1. 27.2010.6102
    2. 27.2010.4302-LTS
    请选择固件版本:1
    
    支持的OPN：
    1. MQM8790
    请选择OPN:1
    
    PSID：
    1. MT_0000000063
    请选择PSID:1
    
    输出下载链接：
    https://www.mellanox.com/downloads/firmware/fw-Quantum-rel-27_2010_6102-MQM8790-HS2X_Ax.bin.zip
# requrement
    sudo apt update
    sudo apt install python3
