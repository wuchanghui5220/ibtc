// 产品数据
const ndrProducts = [
    {name: '400G IB交换机', model: 'MQM9790-NS2R', desc: 'NVIDIA Quantum-2 based NDR InfiniBand Switch, 64 NDR ports, 32 OSFP ports, 2 Power Supplies (AC), Standard depth, Unmanaged, C2P airflow, RailKit', qty: 0},
    {name: '400G IB交换机', model: 'MQM9700-NS2R', desc: 'NVIDIA Quantum-2 based NDR InfiniBand Switch, 64 NDR ports, 32 OSFP ports, 2 Power Supplies (AC), Standard depth, Managed, C2P airflow, Rail Kit', qty: 0},
    {name: '400G IB交换机', model: 'SN5600', desc: 'NVIDIA Spectrum-4 based 800GbE 2U Open Ethernet switch with Cumulus Linux authentication, 64 OSFP ports and 1 SFP28 port, 2 power supplies (AC), x86 CPU, Secure Boot, standard depth, C2P airflow, tool-less rail kit', qty: 0},
    {name: '800G IB交换机', model: 'Q3400', desc: '920-9B36F-00RX-8S0 NVIDIA AIR COOLED SYSTEM 72 PORTS OSFP XDR MNG SWITCH W/ 8 PS STANDARD DEPTH C2P AIRFLOW', qty: 0},
    {name: '800G 光模块', model: 'MMA4Z00-NS', desc: 'NVIDIA twin port transceiver, 800Gbps,2xNDR, OSFP, 2xMPO12 APC, 1310nm SMF, up to 500m, finned', qty: 0},
    {name: '400G 光模块', model: 'MMA4Z00-NS400', desc: 'NVIDIA single port transceiver, 400Gbps,NDR, OSFP, MPO12 APC, 850nm MMF,  up to 50m, flat top', qty: 0},
    {name: '1.6T 光模块', model: 'NVIDIA 1.6T transceiver', desc: 'NVIDIA twin port transceiver, 1.6Tbps, Q3, OSFP, MPO12 APC, 1310nm MMF, up to 500m', qty: 0},
    {name: '800G 光模块', model: 'MMS8X00-NS800', desc: 'NVIDIA single port transceiver, 800Gbps,XDR, OSFP, MPO12 APC, 1310nm SMF, up to 500m, flat top', qty: 0},
    {name: 'MPO12-APC光纤', model: 'MFP7E10-N030', desc: 'NVIDIA passive fiber cable, MMF, MPO12 APC to MPO12 APC, 30m', qty: 0},
    {name: 'MPO12-APC光纤(SMF)', model: 'MFP7E30-N030', desc: 'NVIDIA passive fiber cable, SMF, MPO12 APC to MPO12 APC, 30m', qty: 0},
    {name: 'MPO12-APC 1分2光纤', model: 'MFP7E20-N030', desc: 'NVIDIA passive fiber cable, MMF, MPO12 APC to 2xMPO12 APC, 30m', qty: 0}
];

const hdrProducts = [
    {name: '200G IB交换机', model: 'MQM8790-HS2F', desc: 'Mellanox Quantum HDR InfiniBand Switch, 40 QSFP56 ports, 2 Power Supplies (AC), unmanaged, standard depth, C2P airflow, Rail Kit', qty: 0},
    {name: '200G IB交换机', model: 'MQM8700-HS2F', desc: 'Mellanox Quantum HDR InfiniBand Switch, 40 QSFP56 ports, 2 Power Supplies (AC), x86 dual core, standard depth, C2P airflow, Rail Kit', qty: 0},
    {name: '200G IB AOC线缆', model: 'MFS1S00-H030V', desc: 'Mellanox active optical cable, up to 200Gb/s IB HDR, QSFP56, 30m', qty: 0},
    {name: '200G IB AOC 1分2线缆', model: 'MFS1S50-H030V', desc: 'Mellanox active optical cable, 200Gb/s to 2x100Gb/s IB HDR, QSFP56 to 2x QSFP56, 30m', qty: 0}
];

// 交换机端口数量
const PORTS = {
    EDR: 36,
    HDR: 40,
    NDR200: 128,
    NDR: 64,
    Q3: 144,
    SN5600_NDR: 128,
    SN5600_NDR800: 64
};

// 用于保存所有计算结果
let calculationResults = {};

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM loaded");
    
    // 初始化选项卡切换
    document.getElementById('inputTabBtn').addEventListener('click', function() {
        openTab('inputTab');
    });
    
    document.getElementById('resultsTabBtn').addEventListener('click', function() {
        openTab('resultsTab');
    });
    
    document.getElementById('productTabBtn').addEventListener('click', function() {
        openTab('productTab');
    });
    
    // 添加计算按钮事件监听
    document.getElementById('calculateButton').addEventListener('click', function() {
        console.log("Calculate button clicked");
        calculateTopology();
    });
    
    // 默认显示输入选项卡
    openTab('inputTab');
});

// 选项卡切换函数
function openTab(tabName) {
    console.log("Opening tab:", tabName);
    
    // 隐藏所有选项卡内容
    const tabContents = document.getElementsByClassName('tabcontent');
    for (let i = 0; i < tabContents.length; i++) {
        tabContents[i].style.display = 'none';
    }
    
    // 移除所有选项卡按钮的活动状态
    const tabLinks = document.getElementsByClassName('tablinks');
    for (let i = 0; i < tabLinks.length; i++) {
        tabLinks[i].classList.remove('active');
    }
    
    // 显示选定的选项卡并设置按钮为活动状态
    document.getElementById(tabName).style.display = 'block';
    document.getElementById(tabName + 'Btn').classList.add('active');
}

// 辅助函数
function transform(x, n) {
    return n * Math.ceil(x/n);
}

// 主计算函数
function calculateTopology() {
    console.log("Running topology calculation");
    
    // 获取基本参数
    const ratio = parseInt(document.getElementById('ratio').value) || 1;
    const RA = ratio + 1;
    
    const inputSpeed = parseInt(document.getElementById('speed').value);
    
    // 获取服务器参数
    const gpuServerNum = parseInt(document.getElementById('gpuServerNum').value) || 0;
    const gpuType = document.getElementById('gpuType').value || 'H800';
    const gpuCardNum = parseInt(document.getElementById('gpuCardNum').value);
    
    const storageServerNum = parseInt(document.getElementById('storageServerNum').value) || 0;
    const storageCardNum = parseInt(document.getElementById('storageCardNum').value);
    
    const cpuServerNum = parseInt(document.getElementById('cpuServerNum').value) || 0;
    const cpuCardNum = parseInt(document.getElementById('cpuCardNum').value);
    
    const otherServerNum = parseInt(document.getElementById('otherServerNum').value) || 0;
    const otherCardNum = parseInt(document.getElementById('otherCardNum').value);
    
    const dacCableNumber = parseInt(document.getElementById('dacCableNumber').value) || 0;
    
    // 端口数量和速度映射
    let ports, speed, products, switchName, cableName, cable2Name, cableType, cable2Type, ot800, ot400, ot1600, switchType;
    
    switch(inputSpeed) {
        case 1: // HDR
            ports = PORTS.HDR;
            speed = "HDR";
            products = hdrProducts;
            switchName = "200G IB交换机";
            cableName = "200G IB AOC线缆";
            cable2Name = "200G IB AOC 1分2线缆";
            cableType = "MFS1S00-H030V";
            cable2Type = "MFS1S50-H030V";
            switchType = "MQM8790-HS2F";
            break;
        case 2: // NDR
            ports = PORTS.NDR;
            speed = "NDR";
            products = ndrProducts;
            switchName = "400G IB交换机";
            cableName = "MPO12-APC光纤";
            cable2Name = "MPO12-APC 1分2光纤";
            cableType = "MFP7E10-N030";
            cable2Type = "MFP7E20-N030";
            ot800 = "MMA4Z00-NS";
            ot400 = "MMA4Z00-NS400";
            switchType = "MQM9790-NS2R";
            break;
        case 3: // SN5600 (NDR 400G)
            ports = PORTS.SN5600_NDR;
            speed = "SN5600-NDR";
            products = ndrProducts;
            switchName = "400G IB交换机";
            cableName = "MPO12-APC光纤";
            cable2Name = "MPO12-APC 1分2光纤";
            cableType = "MFP7E10-N030";
            cable2Type = "MFP7E20-N030";
            ot800 = "MMA4Z00-NS";
            ot400 = "MMA4Z00-NS400";
            switchType = "SN5600";
            break;
        case 4: // Q3400 (XDR)
            ports = PORTS.Q3;
            speed = "XDR";
            products = ndrProducts;
            switchName = "800G IB交换机";
            cableName = "MPO12-APC光纤(SMF)";
            cable2Name = "MPO12-APC 1分2光纤";
            cableType = "MFP7E30-N030";
            cable2Type = "MFP7E20-N030";
            ot1600 = "NVIDIA 1.6T transceiver";
            ot800 = "MMS8X00-NS800";
            switchType = "Q3400";
            break;
    }
    
    // 更新Fabric速度显示
    document.getElementById('resultFabricSpeed').textContent = speed;
    
    // 计算bisection
    let bisection, ratioText;
    
    if (RA === 2 && ports === PORTS.HDR) {
        bisection = Math.ceil(ports / RA);
        ratioText = "1:1";
    } else if (RA === 2 && ports === PORTS.NDR) {
        bisection = Math.ceil(ports / RA);
        ratioText = "1:1";
    } else if (RA === 3 && ports === PORTS.HDR) {
        bisection = 16;
        ratioText = "3:5";
    } else if (RA === 3 && ports === PORTS.NDR) {
        bisection = 20;
        ratioText = "1:2";
    } else if (ports === PORTS.SN5600_NDR) {
        bisection = Math.ceil(ports / RA);
        ratioText = "1:1";
    } else if (ports === PORTS.SN5600_NDR800) {
        bisection = Math.ceil(ports / RA);
        ratioText = "1:1";
    } else if (ports === PORTS.Q3) {
        bisection = Math.ceil(ports / RA);
        ratioText = "1:1";
    } else {
        bisection = 32;
        ratioText = "1:1";
    }
    
    document.getElementById('resultRatio').textContent = ratioText;
    
    // 寻找bisection的因子
    const factors = [];
    for (let i = 1; i <= bisection; i++) {
        if (bisection % i === 0) {
            factors.push(i);
        }
    }
    
    // GPU处理
    let gpuLeafs = 0;
    let realSu = 0;
    let su = 0;
    let suNodes = 0;
    let gpuNodes = 0;
    let restGpuSwitchPorts = 0;
    
    if (gpuServerNum > 0) {
        if (ports === PORTS.NDR200 && (gpuCardNum === 4 || gpuCardNum === 8)) {
            suNodes = gpuCardNum * bisection;
        } else {
            suNodes = gpuCardNum * bisection;
        }
        
        su = Math.ceil((gpuServerNum * gpuCardNum) / suNodes);
        gpuLeafs = gpuCardNum * su;
        realSu = Math.round((gpuServerNum * gpuCardNum) / suNodes * 100) / 100;
        gpuNodes = gpuServerNum * gpuCardNum;
        restGpuSwitchPorts = su * suNodes - gpuServerNum * gpuCardNum;
    }
    
    // 存储服务器处理
    let storageLeafs = 0;
    let realSSu = 0;
    let sSu = 0;
    let sSuNodes = 0;
    let storageNodes = 0;
    let restStorageSwitchPorts = 0;
    
    if (storageServerNum > 0) {
        if (ports === PORTS.NDR200 && (storageCardNum === 1 || storageCardNum === 2)) {
            sSuNodes = storageCardNum * bisection;
        } else {
            sSuNodes = storageCardNum * bisection;
        }
        
        sSu = Math.ceil((storageServerNum * storageCardNum) / sSuNodes);
        realSSu = Math.round((storageServerNum * storageCardNum) / sSuNodes * 100) / 100;
        storageLeafs = (storageServerNum * storageCardNum - restGpuSwitchPorts) / bisection;
        
        if (storageLeafs > 0) {
            storageLeafs = transform(storageLeafs, storageCardNum);
        } else {
            storageLeafs = 0;
        }
        
        storageNodes = storageServerNum * storageCardNum;
        restStorageSwitchPorts = (gpuLeafs + storageLeafs) * bisection - (gpuNodes + storageNodes);
    } else {
        storageNodes = 0;
        restStorageSwitchPorts = (gpuLeafs) * bisection - (gpuNodes);
    }
    
    // CPU服务器处理
    let cpuLeafs = 0;
    let realCSu = 0;
    let cSu = 0;
    let cSuNodes = 0;
    let cpuNodes = 0;
    let restCpuSwitchPorts = 0;
    
    if (cpuServerNum > 0) {
        if (ports === PORTS.NDR200 && (cpuCardNum === 1 || cpuCardNum === 2)) {
            cSuNodes = cpuCardNum * bisection;
        } else {
            cSuNodes = cpuCardNum * bisection;
        }
        
        cSu = Math.ceil((cpuServerNum * cpuCardNum) / cSuNodes);
        realCSu = Math.round((cpuServerNum * cpuCardNum) / cSuNodes * 100) / 100;
        cpuLeafs = (cpuServerNum * cpuCardNum - restStorageSwitchPorts) / bisection;
        
        if (cpuLeafs > 0) {
            cpuLeafs = transform(cpuLeafs, cpuCardNum);
        } else {
            cpuLeafs = 0;
        }
        
        cpuNodes = cpuServerNum * cpuCardNum;
        restCpuSwitchPorts = (gpuLeafs + storageLeafs + cpuLeafs) * bisection - (gpuNodes + storageNodes + cpuNodes);
    } else {
        cpuNodes = 0;
        restCpuSwitchPorts = (gpuLeafs + storageLeafs) * bisection - (gpuNodes + storageNodes);
    }
    
    // 其他服务器处理
    let otherLeafs = 0;
    let realOSu = 0;
    let oSu = 0;
    let oSuNodes = 0;
    let otherNodes = 0;
    let restOtherSwitchPorts = 0;
    
    if (otherServerNum > 0) {
        if (ports === PORTS.NDR200 && (otherCardNum === 1 || otherCardNum === 2)) {
            oSuNodes = otherCardNum * bisection;
        } else {
            oSuNodes = otherCardNum * bisection;
        }
        
        oSu = Math.ceil((otherServerNum * otherCardNum) / oSuNodes);
        realOSu = Math.round((otherServerNum * otherCardNum) / oSuNodes * 100) / 100;
        otherLeafs = (otherServerNum * otherCardNum - restCpuSwitchPorts) / bisection;
        
        if (otherLeafs > 0) {
            otherLeafs = transform(otherLeafs, otherCardNum);
        } else {
            otherLeafs = 0;
        }
        
        otherNodes = otherServerNum * otherCardNum;
        restOtherSwitchPorts = (gpuLeafs + storageLeafs + cpuLeafs + otherLeafs) * bisection - (gpuNodes + storageNodes + cpuNodes + otherNodes);
    } else {
        otherNodes = 0;
        restOtherSwitchPorts = (gpuLeafs + storageLeafs + cpuLeafs) * bisection - (gpuNodes + storageNodes + cpuNodes);
    }
    
    // 计算服务器和节点总数
    const serverNum = gpuServerNum + storageServerNum + cpuServerNum + otherServerNum;
    const nodes = gpuNodes + storageNodes + cpuNodes + otherNodes;
    
    // 计算叶子交换机和脊柱交换机
    const leafs = gpuLeafs + storageLeafs + cpuLeafs + otherLeafs;
    
    let spines = Math.ceil(leafs * bisection / ports);
    if (!factors.includes(spines)) {
        for (const factor of factors) {
            if (factor > spines) {
                spines = factor;
                break;
            }
        }
    }
    
    // 计算线缆数量
    const spineToLeafCables = Math.floor(leafs * bisection);
    let leafToServerCables = Math.floor(nodes);
    const maxLeafToServerCables = leafs * (ports - bisection);
    
    // 光模块数量
    let spine2LeafOTNumber = 0;
    let leaf2ServerOTNumber = 0;
    let switchOT = 0;
    let hcaOT = 0;
    let q3SpineToLeafOT = 0;
    let q3LeafToServerOT = 0;
    let q3OT = 0;
    
    if (speed === "NDR" || speed === "SN5600-NDR") {
        spine2LeafOTNumber = Math.ceil(leafs * bisection * 2 / 2);
        leaf2ServerOTNumber = Math.ceil(nodes / 2);
        switchOT = spine2LeafOTNumber + leaf2ServerOTNumber;
        hcaOT = nodes;
    } else if (speed === "XDR") {
        q3SpineToLeafOT = Math.ceil((leafs * bisection * 2) / 2);
        q3LeafToServerOT = Math.ceil(nodes / 2);
        q3OT = q3SpineToLeafOT + q3LeafToServerOT;
        hcaOT = nodes;
    }
    
    // DAC线缆处理
    if (dacCableNumber > 0) {
        leafToServerCables = leafToServerCables - (dacCableNumber * 2);
        if (speed === "NDR" || speed === "SN5600-NDR") {
            leaf2ServerOTNumber = leaf2ServerOTNumber - dacCableNumber;
            switchOT = spine2LeafOTNumber + leaf2ServerOTNumber;
            hcaOT = hcaOT - (dacCableNumber * 2);
        } else if (speed === "XDR") {
            q3LeafToServerOT = q3LeafToServerOT - dacCableNumber;
            q3OT = q3SpineToLeafOT + q3LeafToServerOT;
            hcaOT = hcaOT - (dacCableNumber * 2);
        }
    }
    
    const allCables = spineToLeafCables + leafToServerCables;
    
    console.log("Calculation completed, updating UI");
    
    // 保存计算结果
    calculationResults = {
        fabricSpeed: speed,
        ratio: ratioText,
        
        gpuServerNum,
        gpuNodes,
        gpuLeafs,
        
        storageServerNum,
        storageNodes,
        storageLeafs,
        
        cpuServerNum,
        cpuNodes,
        cpuLeafs,
        
        otherServerNum,
        otherNodes,
        otherLeafs,
        
        serverNum,
        nodes,
        
        spines,
        leafs,
        
        spineToLeafCables,
        leafToServerCables,
        maxLeafToServerCables,
        allCables,
        
        spine2LeafOTNumber,
        leaf2ServerOTNumber,
        switchOT,
        hcaOT,
        
        q3SpineToLeafOT,
        q3LeafToServerOT,
        q3OT,
        
        // 产品数据
        speed,
        switchType,
        cableType,
        cable2Type,
        ot800,
        ot400,
        ot1600
    };
    
    // 更新UI
    updateResults();
    updateProductTable();
    
    // 切换到结果选项卡
    openTab('resultsTab');
}

// 更新结果页面
function updateResults() {
    console.log("Updating results UI");
    
    // 更新基本信息
    document.getElementById('resultFabricSpeed').textContent = calculationResults.fabricSpeed;
    document.getElementById('resultRatio').textContent = calculationResults.ratio;
    
    // 更新服务器信息
    document.getElementById('gpuServerNumResult').textContent = calculationResults.gpuServerNum;
    document.getElementById('gpuNodesResult').textContent = calculationResults.gpuNodes;
    document.getElementById('gpuLeafsResult').textContent = calculationResults.gpuLeafs;
    
    document.getElementById('storageServerNumResult').textContent = calculationResults.storageServerNum;
    document.getElementById('storageNodesResult').textContent = calculationResults.storageNodes;
    document.getElementById('storageLeafsResult').textContent = calculationResults.storageLeafs;
    
    document.getElementById('cpuServerNumResult').textContent = calculationResults.cpuServerNum;
    document.getElementById('cpuNodesResult').textContent = calculationResults.cpuNodes;
    document.getElementById('cpuLeafsResult').textContent = calculationResults.cpuLeafs;
    
    document.getElementById('otherServerNumResult').textContent = calculationResults.otherServerNum;
    document.getElementById('otherNodesResult').textContent = calculationResults.otherNodes;
    document.getElementById('otherLeafsResult').textContent = calculationResults.otherLeafs;
    
    document.getElementById('totalServerNumResult').textContent = calculationResults.serverNum;
    document.getElementById('totalNodesResult').textContent = calculationResults.nodes;
    document.getElementById('totalLeafsResult').textContent = calculationResults.leafs;
    
    // 更新交换机拓扑
    document.getElementById('spinesResult').textContent = calculationResults.spines;
    document.getElementById('leafsResult').textContent = calculationResults.leafs;
    document.getElementById('spineToLeafCablesResult').textContent = calculationResults.spineToLeafCables;
    document.getElementById('leafToServerCablesResult').textContent = calculationResults.leafToServerCables;
    document.getElementById('maxLeafToServerCablesResult').textContent = calculationResults.maxLeafToServerCables;
    document.getElementById('totalCablesResult').textContent = calculationResults.allCables;
    
    // 更新光模块信息
    const otTable = document.getElementById('otTable');
    otTable.innerHTML = ''; // 清空表格
    
    // 创建表头
    const thead = document.createElement('tr');
    thead.innerHTML = '<th>光模块类型</th><th>数量</th>';
    otTable.appendChild(thead);
    
    if (calculationResults.fabricSpeed === "NDR" || calculationResults.fabricSpeed === "SN5600-NDR") {
        const row1 = document.createElement('tr');
        row1.innerHTML = '<td>Spine-to-Leaf 800G 双端口光模块</td><td>' + calculationResults.spine2LeafOTNumber + '</td>';
        otTable.appendChild(row1);
        
        const row2 = document.createElement('tr');
        row2.innerHTML = '<td>Leaf-to-Server 800G 双端口光模块</td><td>' + calculationResults.leaf2ServerOTNumber + '</td>';
        otTable.appendChild(row2);
        
        const row3 = document.createElement('tr');
        row3.innerHTML = '<td>交换机端光模块总数</td><td>' + calculationResults.switchOT + '</td>';
        otTable.appendChild(row3);
        
        const row4 = document.createElement('tr');
        row4.innerHTML = '<td>HCA 400G 光模块</td><td>' + calculationResults.hcaOT + '</td>';
        otTable.appendChild(row4);
    } else if (calculationResults.fabricSpeed === "XDR") {
        const row1 = document.createElement('tr');
        row1.innerHTML = '<td>Spine-to-Leaf 1.6T 双端口光模块</td><td>' + calculationResults.q3SpineToLeafOT + '</td>';
        otTable.appendChild(row1);
        
        const row2 = document.createElement('tr');
        row2.innerHTML = '<td>Leaf-to-Server 1.6T 双端口光模块</td><td>' + calculationResults.q3LeafToServerOT + '</td>';
        otTable.appendChild(row2);
        
        const row3 = document.createElement('tr');
        row3.innerHTML = '<td>交换机端光模块总数</td><td>' + calculationResults.q3OT + '</td>';
        otTable.appendChild(row3);
        
        const row4 = document.createElement('tr');
        row4.innerHTML = '<td>HCA 800G 光模块</td><td>' + calculationResults.hcaOT + '</td>';
        otTable.appendChild(row4);
    }
}

// 更新产品表格
function updateProductTable() {
    console.log("Updating product table");
    
    const productTable = document.getElementById('productTable');
    const productSummary = document.getElementById('productSummary');
    
    // 生成产品清单总结描述
    let summaryText = '';
    
    // 添加服务器信息
    let serverDetails = [];
    if (calculationResults.gpuServerNum > 0) {
        const gpuType = document.getElementById('gpuType').value || 'H800';
        serverDetails.push(`${calculationResults.gpuServerNum}台 ${gpuType} GPU服务器`);
    }
    if (calculationResults.storageServerNum > 0) {
        serverDetails.push(`${calculationResults.storageServerNum}台存储服务器`);
    }
    if (calculationResults.cpuServerNum > 0) {
        serverDetails.push(`${calculationResults.cpuServerNum}台CPU服务器`);
    }
    if (calculationResults.otherServerNum > 0) {
        serverDetails.push(`${calculationResults.otherServerNum}台其他服务器`);
    }
    
    // 如果没有任何服务器，显示总服务器数
    if (serverDetails.length === 0 && calculationResults.serverNum > 0) {
        serverDetails.push(`${calculationResults.serverNum}台服务器`);
    }
    
    // 组合服务器信息
    const serverInfo = serverDetails.join('、');
    
    // 添加网络类型
    const networkInfo = `${calculationResults.fabricSpeed}网络`;
    
    // 组合总结描述
    if (serverInfo) {
        summaryText = `<p><strong>${serverInfo} ${networkInfo}配置清单表</strong></p>`;
    } else {
        summaryText = `<p><strong>${networkInfo}配置清单表</strong></p>`;
    }
    
    // 显示总结描述
    productSummary.innerHTML = summaryText;
    
    // 清空产品表格内容，保留表头
    while (productTable.rows.length > 1) {
        productTable.deleteRow(1);
    }
    
    // 准备数据
    let data = [];
    data.push({
        name: 'spine_switch', 
        model: calculationResults.switchType, 
        num: calculationResults.spines, 
        note: 'Spine 交换机'
    });
    
    data.push({
        name: 'leaf_switch', 
        model: calculationResults.switchType, 
        num: calculationResults.leafs, 
        note: 'Leaf 交换机'
    });
    
    data.push({
        name: 'spine_to_leaf_cables', 
        model: calculationResults.cableType, 
        num: calculationResults.spineToLeafCables, 
        note: 'Spine 到 Leaf 之间互连的线缆'
    });
    
    data.push({
        name: 'leaf_to_server_cables', 
        model: calculationResults.cableType, 
        num: calculationResults.leafToServerCables, 
        note: 'Leaf 到 Server 之间互连的线缆'
    });
    
    if (calculationResults.fabricSpeed === "NDR" || calculationResults.fabricSpeed === "SN5600-NDR") {
        data.push({
            name: 'spine_to_leaf_ot', 
            model: calculationResults.ot800, 
            num: calculationResults.spine2LeafOTNumber, 
            note: 'Spine 到 Leaf 之间互连 800G 模块'
        });
        
        data.push({
            name: 'leaf_to_server_ot', 
            model: calculationResults.ot800, 
            num: calculationResults.leaf2ServerOTNumber, 
            note: 'Leaf 到 Server 交换机端 800G 模块'
        });
        
        data.push({
            name: 'hca_ot', 
            model: calculationResults.ot400, 
            num: calculationResults.hcaOT, 
            note: '网卡端 400G 模块'
        });
    } else if (calculationResults.fabricSpeed === "XDR") {
        data.push({
            name: 'spine_to_leaf_1.6t_ot', 
            model: calculationResults.ot1600, 
            num: calculationResults.q3SpineToLeafOT, 
            note: 'Spine 到 Leaf 之间互连 1.6T 模块 (双端口 800G)'
        });
        
        data.push({
            name: 'leaf_to_server_1.6t_ot', 
            model: calculationResults.ot1600, 
            num: calculationResults.q3LeafToServerOT, 
            note: 'Leaf 到 Server 交换机端 1.6T 模块 (双端口 800G)'
        });
        
        data.push({
            name: 'hca_ot', 
            model: calculationResults.ot800, 
            num: calculationResults.hcaOT, 
            note: '网卡端 800G 模块'
        });
    }
    
    // 将数据映射到产品表格
    let products = calculationResults.fabricSpeed === "HDR" ? hdrProducts : ndrProducts;
    
    for (const item of data) {
        for (const product of products) {
            if (product.model === item.model) {
                const row = productTable.insertRow();
                
                row.insertCell(0).textContent = product.name;
                row.insertCell(1).textContent = product.model;
                row.insertCell(2).textContent = product.desc;
                row.insertCell(3).textContent = item.num;
                row.insertCell(4).textContent = item.note;
                
                break;
            }
        }
    }
}
