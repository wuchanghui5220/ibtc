    document.addEventListener('DOMContentLoaded', function() {
        // 初始化变量
        let diagram, svg, connectionsGroup, nodesGroup;
        let tooltip = document.getElementById('tooltip');
        let isDragging = false;
        let lastX, lastY;

        // DOM元素
        const infoToggle = document.getElementById('infoToggle');
        const infoPanel = document.getElementById('infoPanel');
        const calculateButton = document.getElementById('calculateButton');
        const resetButton = document.getElementById('resetButton');
        //const zoomFitBtn = document.getElementById('zoomFitBtn');
        const toggleGridBtn = document.getElementById('toggleGridBtn');
        const exportSvgBtn = document.getElementById('exportSvgBtn');

        // 范围滑块值显示
        const spineLeafSlider = document.getElementById('spineLeafDistance');
        const leafNodeSlider = document.getElementById('leafNodeDistance');
        const nodeRowSlider = document.getElementById('nodeRowSpacing');
        const spineLeafValue = document.getElementById('spineLeafValue');
        const leafNodeValue = document.getElementById('leafNodeValue');
        const nodeRowValue = document.getElementById('nodeRowValue');

        // 初始化图表容器
        diagram = d3.select("#diagram");

        // 初始绘制拓扑图
        calculateAndDraw();

        // 绑定信息面板切换
        infoToggle.addEventListener('click', function() {
            this.classList.toggle('active');
            infoPanel.classList.toggle('show');
        });

        // 绑定工具栏按钮事件
        //zoomFitBtn.addEventListener('click', zoomToFit);
        toggleGridBtn.addEventListener('click', toggleGrid);
        exportSvgBtn.addEventListener('click', exportSVG);

        // 绑定计算按钮事件
        calculateButton.addEventListener('click', calculateAndDraw);

        // 绑定重置按钮事件
        resetButton.addEventListener('click', resetParameters);

        // 绑定交换机类型变更事件
        document.getElementById('switchType').addEventListener('change', updateNetworkCardOptions);

        // 绑定范围滑块值更新
        spineLeafSlider.addEventListener('input', function() {
            spineLeafValue.textContent = this.value + 'px';
        });

        leafNodeSlider.addEventListener('input', function() {
            leafNodeValue.textContent = this.value + 'px';
        });

        nodeRowSlider.addEventListener('input', function() {
            nodeRowValue.textContent = this.value + 'px';
        });

        function updateNetworkCardOptions() {
            const switchType = document.getElementById('switchType').value;
            const networkCardSelect = document.getElementById('networkCardType');

            switch(switchType) {
                case 'QM8700':
                    networkCardSelect.value = '200G';
                    break;
                case 'QM9700':
                case 'SN5600':
                    networkCardSelect.value = '400G';
                    break;
                case 'Q3400':
                    networkCardSelect.value = '800G';
                    break;
            }
        }

        function calculateAndDraw() {
            showLoading();
            updateStatusText("计算中...");

            // 为了模拟处理效果，添加延迟
            setTimeout(() => {
                const switchType = document.getElementById('switchType').value;
                const networkCardType = document.getElementById('networkCardType').value;
                const numServers = parseInt(document.getElementById('numServers').value);
                const numNetworkCardsPerServer = parseInt(document.getElementById('numNetworkCardsPerServer').value);
                const spineLeafDistance = parseInt(document.getElementById('spineLeafDistance').value);
                const leafNodeDistance = parseInt(document.getElementById('leafNodeDistance').value);
                const serversPerRow = parseInt(document.getElementById('serversPerRow').value);
                const diagramHeight = parseInt(document.getElementById('diagramHeight').value);
                const nodeRowSpacing = parseInt(document.getElementById('nodeRowSpacing').value);

                let switchPorts, leafUplinks, serversPerSU, possibleSpineCounts;

                switch(switchType) {
                    case 'QM8700':
                        switchPorts = 40;
                        leafUplinks = 20;
                        serversPerSU = 20;
                        possibleSpineCounts = [1, 2, 4, 5, 10, 20];
                        break;
                    case 'QM9700':
                        switchPorts = 64;
                        leafUplinks = 32;
                        serversPerSU = 32;
                        possibleSpineCounts = [1, 2, 4, 8, 16, 32];
                        break;
                    case 'Q3400':
                        switchPorts = 144;
                        leafUplinks = 72;
                        serversPerSU = 72;
                        possibleSpineCounts = [1, 2, 3, 4, 6, 8, 9, 12, 18, 24, 36, 72];
                        break;
                    case 'SN5600':
                        switchPorts = 128;
                        leafUplinks = 64;
                        serversPerSU = 64;
                        possibleSpineCounts = [1, 2, 4, 8, 16, 32, 64];
                        break;
                }

                const numSU = Math.ceil(numServers / serversPerSU);
                const numLeafSwitchesPerSU = numNetworkCardsPerServer;
                const numLeafSwitches = numSU * numLeafSwitchesPerSU;
                const numSpineSwitches = possibleSpineCounts.find(count => count >= numLeafSwitches * leafUplinks / switchPorts) || possibleSpineCounts[possibleSpineCounts.length - 1];
                const totalPorts = numLeafSwitches * switchPorts + numSpineSwitches * switchPorts;
                //const totalCables = numServers * numNetworkCardsPerServer + numLeafSwitches * numSpineSwitches;
                const totalCables = numServers * numNetworkCardsPerServer + numLeafSwitches * leafUplinks;

                // 更新信息面板
                document.getElementById('info-switchType').textContent = switchType;
                document.getElementById('info-networkCardType').textContent = networkCardType;
                document.getElementById('info-suCount').textContent = numSU;
                document.getElementById('info-spineCount').textContent = numSpineSwitches;
                document.getElementById('info-leafCount').textContent = numLeafSwitches;
                document.getElementById('info-serverCount').textContent = numServers;
                document.getElementById('info-portCount').textContent = totalPorts;
                document.getElementById('info-cableCount').textContent = totalCables;

                // 绘制拓扑图
                drawTopology(numSU, numSpineSwitches, numLeafSwitches, numServers, numNetworkCardsPerServer, serversPerSU, spineLeafDistance, leafNodeDistance, serversPerRow, diagramHeight, nodeRowSpacing);

                // 更新状态
                updateStatusText("已完成");
                hideLoading();
            }, 500);
        }

        function drawTopology(numSU, numSpine, numLeaf, numServers, numNetworkCardsPerServer, serversPerSU, spineLeafDistance, leafNodeDistance, serversPerRow, diagramHeight, nodeRowSpacing) {
            // 调整宽度基于是否显示所有元素或仅部分元素
            let displayWidth;
            if (numSU <= 2) {
                // 对于所有元素的完整宽度
                displayWidth = Math.max(Math.min(window.innerWidth - 40, 1600), numLeaf * 80);
            } else {
                // 对于简化视图的减少宽度 - 不需要完整宽度
                displayWidth = Math.max(Math.min(window.innerWidth - 40, 1600), 800);
            }

            const width = displayWidth;
            const height = diagramHeight;
            const spineY = 50;
            const leafY = spineY + spineLeafDistance;
            const serverY = leafY + leafNodeDistance;

            // 清除旧图表
            d3.select("#diagram").selectAll("*").remove();

            // 创建新SVG
            svg = d3.select("#diagram")
                .append("svg")
                .attr("viewBox", `0 0 ${width} ${height}`)
                .attr("width", width)
                .attr("height", height);

            // 添加缩放功能
            const zoom = d3.zoom()
                .scaleExtent([0.1, 10])
                .on("zoom", function(event) {
                    container.attr("transform", event.transform);
                });

            svg.call(zoom);

            // 创建主容器组
            const container = svg.append("g");

            // 创建连接和节点组
            connectionsGroup = container.append("g").attr("class", "connections");
            nodesGroup = container.append("g").attr("class", "nodes");

            // 添加网格（默认隐藏）
            const gridSize = 50;
            const grid = container.append("g")
                .attr("class", "grid")
                .attr("display", "none");

            for (let x = 0; x < width; x += gridSize) {
                grid.append("line")
                    .attr("x1", x)
                    .attr("y1", 0)
                    .attr("x2", x)
                    .attr("y2", height)
                    .attr("stroke", "rgba(255, 255, 255, 0.1)")
                    .attr("stroke-width", 0.5);
            }

            for (let y = 0; y < height; y += gridSize) {
                grid.append("line")
                    .attr("x1", 0)
                    .attr("y1", y)
                    .attr("x2", width)
                    .attr("y2", y)
                    .attr("stroke", "rgba(255, 255, 255, 0.1)")
                    .attr("stroke-width", 0.5);
            }

            // 确定基于总数量显示哪些Spine交换机
            let spinesToDisplay = [];
            if (numSpine <= 8) {
                // 如果8个或更少spine，显示所有
                spinesToDisplay = Array.from({ length: numSpine }, (_, i) => i);
            } else {
                // 如果超过8个spine，显示前4个和后4个
                for (let i = 0; i < 4; i++) {
                    spinesToDisplay.push(i);              // 前4个
                }
                for (let i = numSpine - 4; i < numSpine; i++) {
                    spinesToDisplay.push(i);              // 后4个
                }
            }

            // 计算spine交换机X位置的函数
            const spineX = d => {
                if (numSpine <= 8) {
                    // 8个或更少spine的原始计算
                    return (width / (numSpine + 1)) * (d + 1);
                } else {
                    // 显示超过8个spine时的修改计算
                    if (d < 4) {
                        // 前4个spine使用左侧45%的宽度
                        return width * (0.1 + 0.35 * (d / 4));
                    } else {
                        // 后4个spine使用右侧45%的宽度
                        return width * (0.6 + 0.35 * ((d - (numSpine - 4)) / 4));
                    }
                }
            };

            // 仅为显示的spine创建矩形
            spinesToDisplay.forEach(spineIndex => {
                const x = spineX(spineIndex);
                const rect = nodesGroup.append("rect")
                    .attr("class", "spine")
                    .attr("x", x - 30)
                    .attr("y", spineY)
                    .attr("width", 60)
                    .attr("height", 30)
                    .attr("rx", 4)
                    .attr("ry", 4);

                // 添加鼠标悬停事件
                rect.on("mouseover", function(event) {
                    showTooltip(event, `Spine ${spineIndex + 1}<br>连接到 ${numLeaf} 个Leaf`);
                })
                .on("mousemove", function(event) {
                    moveTooltip(event);
                })
                .on("mouseout", function() {
                    hideTooltip();
                });

                nodesGroup.append("text")
                    .attr("class", "spine-label")
                    .attr("x", x)
                    .attr("y", spineY + 15)
                    .attr("text-anchor", "middle")
                    .attr("dominant-baseline", "middle")
                    .attr("font-size", "10px")
                    .attr("fill", "white")
                    .text(`Spine ${spineIndex + 1}`);
            });

            // 如果不显示所有spine，添加省略号
            if (numSpine > 8) {
                nodesGroup.append("text")
                    .attr("x", width / 2)
                    .attr("y", spineY + 15)
                    .attr("text-anchor", "middle")
                    .attr("font-size", "14px")
                    .attr("font-weight", "bold")
                    .attr("fill", "#0c70f2")
                    .text("...");
            }

            // 确定基于总数量和SU显示哪些Leaf交换机
            let leavesToDisplay = [];
            if (numSU <= 2 || numLeaf <= 8) {
                // 如果2个或更少SU或8个或更少叶子，显示所有叶子
                leavesToDisplay = Array.from({ length: numLeaf }, (_, i) => i);
            } else {
                // 如果3+个SU和9+个叶子，仅显示部分叶子
                const leavesPerSU = numNetworkCardsPerServer;

                // 显示第一个SU的叶子
                for (let i = 0; i < leavesPerSU; i++) {
                    leavesToDisplay.push(i);
                }

                // 显示最后一个SU的叶子
                const lastSUStartIndex = numLeaf - leavesPerSU;
                for (let i = lastSUStartIndex; i < numLeaf; i++) {
                    // 仅添加未添加的（避免少数SU的情况下重复）
                    if (!leavesToDisplay.includes(i)) {
                        leavesToDisplay.push(i);
                    }
                }

                // 排序以保持顺序
                leavesToDisplay.sort((a, b) => a - b);
            }

            // 计算leaf交换机X位置的函数
            const leafX = d => {
                if (numSU <= 2 || numLeaf <= 8) {
                    // 少数SU时计算所有叶子的位置
                    return (width / (numLeaf + 1)) * (d + 1);
                } else {
                    // 我们需要修复叶子的间距
                    const leavesPerSide = leavesToDisplay.length / 2;

                    // 确定这是上半部分还是下半部分的叶子
                    if (d < numNetworkCardsPerServer) {
                        // 第一个SU的叶子
                        const index = d;
                        // 位于屏幕左侧40%，间距适当
                        return width * (0.01 + 0.5 * (index + 1) / (leavesPerSide + 1));
                    } else {
                        // 最后一个SU的叶子
                        const index = d - (numLeaf - numNetworkCardsPerServer);
                        // 位于屏幕右侧40%，间距适当
                        return width * (0.5 + 0.5 * (index + 1) / (leavesPerSide + 1));
                    }
                }
            };

            // 仅为显示的leaf创建矩形
            leavesToDisplay.forEach(leafIndex => {
                const x = leafX(leafIndex);
                const rect = nodesGroup.append("rect")
                    .attr("class", "leaf")
                    .attr("x", x - 30)
                    .attr("y", leafY)
                    .attr("width", 60)
                    .attr("height", 30)
                    .attr("rx", 4)
                    .attr("ry", 4);

                // 添加鼠标悬停事件
                rect.on("mouseover", function(event) {
                    //showTooltip(event, `Leaf ${leafIndex + 1}<br>连接到 ${spinesToDisplay.length} 个Spine`);
                    showTooltip(event, `Leaf ${leafIndex + 1}<br>连接到 ${numSpine} 个Spine`);
                })
                .on("mousemove", function(event) {
                    moveTooltip(event);
                })
                .on("mouseout", function() {
                    hideTooltip();
                });

                nodesGroup.append("text")
                    .attr("class", "leaf-label")
                    .attr("x", x)
                    .attr("y", leafY + 15)
                    .attr("text-anchor", "middle")
                    .attr("dominant-baseline", "middle")
                    .attr("font-size", "10px")
                    .attr("fill", "white")
                    .text(`Leaf ${leafIndex + 1}`);
            });

            // 如果不显示所有leaf，添加省略号
            if (numSU > 2 && numLeaf > 8) {
                nodesGroup.append("text")
                    .attr("x", width / 2)
                    .attr("y", leafY + 15)
                    .attr("text-anchor", "middle")
                    .attr("font-size", "14px")
                    .attr("font-weight", "bold")
                    .attr("fill", "#05d9e8")
                    .text("...");
            }

            // 创建显示的spine和leaf之间的曲线连接
            leavesToDisplay.forEach(l => {
                spinesToDisplay.forEach(s => {
                    const startX = spineX(s);
                    const startY = spineY + 30;
                    const endX = leafX(l);
                    const endY = leafY;
                    const midY = (startY + endY) / 2;

                    // 使用更平滑的曲线
                    connectionsGroup.append("path")
                        .attr("d", `M ${startX} ${startY} C ${startX} ${midY}, ${endX} ${midY}, ${endX} ${endY}`)
                        .attr("fill", "none")
                        .attr("stroke", "rgba(255, 255, 255, 0.15)")
                        .attr("stroke-width", 0.5);
                });
            });

            // 服务器节点的常量
            const serverWidth = 50;
            const serverHeight = 20;

            // 根据一行中的服务器数量和可用宽度调整服务器间距
            let serverSpacing;
            if (numSU <= 2) {
                // 对于包含所有SU的普通视图
                serverSpacing = Math.min(60, (width / numSU) / (serversPerRow + 1));
            } else {
                // 对于仅包含第一个和最后一个SU的简化视图
                // 使用更多空间，因为我们只显示2个SU而不是全部
                serverSpacing = Math.min(60, (width / 2) / (serversPerRow + 1));
            }

            const totalRows = Math.ceil(Math.max(...Array.from({ length: numSU }, (_, i) =>
                Math.min(serversPerSU, numServers - i * serversPerSU)
            )) / serversPerRow);

            const totalServerHeight = (totalRows - 1) * nodeRowSpacing;
            const availableHeight = height - serverY - 60;
            const verticalScale = Math.min(1, availableHeight / totalServerHeight);

            // 确定基于总数量显示哪些SU
            let susToDisplay = [];
            if (numSU <= 2) {
                // 如果2个或更少SU，显示所有
                susToDisplay = Array.from({ length: numSU }, (_, i) => i);
            } else {
                // 如果3个或更多SU，仅显示第一个和最后一个SU
                susToDisplay = [0, numSU - 1];
            }

            let lastNodeY = 0;

            // 仅为要显示的SU渲染服务器
            susToDisplay.forEach(su => {
                const serversInThisSU = Math.min(serversPerSU, numServers - su * serversPerSU);

                for (let s = 0; s < serversInThisSU; s++) {
                    const row = Math.floor(s / serversPerRow);
                    const col = s % serversPerRow;

                    // 调整仅显示第一个和最后一个SU时的x坐标计算
                    let x;
                    if (numSU <= 2) {
                        // 对于2个或更少SU - 均匀分布
                        x = width * ((su + 0.5) / numSU) + (col - serversPerRow / 2 + 0.5) * serverSpacing;
                    } else {
                        // 对于3个或更多SU的第一个和最后一个SU
                        // 放置在宽度的1/4和3/4处，间距适当
                        const suPosition = su === 0 ? 0.25 : 0.75;
                        x = width * suPosition + (col - serversPerRow / 2 + 0.5) * serverSpacing;
                    }

                    const y = serverY + row * nodeRowSpacing * verticalScale;
                    lastNodeY = Math.max(lastNodeY, y);

                    // 计算节点的唯一ID
                    const nodeId = su * serversPerSU + s + 1;

                    const rect = nodesGroup.append("rect")
                        .attr("class", "server")
                        .attr("x", x - serverWidth / 2)
                        .attr("y", y - serverHeight / 2)
                        .attr("width", serverWidth)
                        .attr("height", serverHeight)
                        .attr("rx", 5)
                        .attr("ry", 5);

                    // 添加鼠标悬停事件
                    rect.on("mouseover", function(event) {
                        showTooltip(event, `Node ${nodeId}<br>${numNetworkCardsPerServer} 网卡<br>SU ${su + 1}`);
                    })
                    .on("mousemove", function(event) {
                        moveTooltip(event);
                    })
                    .on("mouseout", function() {
                        hideTooltip();
                    });

                    nodesGroup.append("text")
                        .attr("class", "server-label")
                        .attr("x", x)
                        .attr("y", y)
                        .attr("text-anchor", "middle")
                        .attr("dominant-baseline", "middle")
                        .attr("font-size", "8px")
                        .attr("fill", "white")
                        .text(`Node ${nodeId}`);

                    // 创建leaf交换机和服务器之间的曲线连接
                    // 仅创建到可见leaf交换机的连接
                    if (leavesToDisplay.length > 0) {
                        // 确定连接到此服务器的leaf交换机
                        let connectedLeaves = [];

                        if (numSU <= 2 || numLeaf <= 8) {
                            // 显示所有叶子时，连接到此SU的正确叶子
                            for (let nc = 0; nc < numNetworkCardsPerServer; nc++) {
                                const leafIndex = su * numNetworkCardsPerServer + nc;
                                if (leafIndex < numLeaf) {
                                    connectedLeaves.push(leafIndex);
                                }
                            }
                        } else {
                            // 仅显示部分叶子时，建立逻辑连接：
                            if (su === 0) {
                                // 第一个SU服务器连接到第一个SU叶子（leavesToDisplay的前半部分）
                                connectedLeaves = leavesToDisplay.filter(l => l < numNetworkCardsPerServer);
                            } else if (su === numSU - 1) {
                                // 最后一个SU服务器连接到最后一个SU叶子（leavesToDisplay的后半部分）
                                connectedLeaves = leavesToDisplay.filter(l => l >= numLeaf - numNetworkCardsPerServer);
                            }
                        }

                        // 创建连接
                        connectedLeaves.forEach(leafIndex => {
                            if (leavesToDisplay.includes(leafIndex)) {
                                const startX = leafX(leafIndex);
                                const startY = leafY + 30;
                                const endX = x;
                                const endY = y - serverHeight / 2;
                                const midY = (startY + endY) / 2;

                                const path = connectionsGroup.append("path")
                                    .attr("d", `M ${startX} ${startY} C ${startX} ${midY}, ${endX} ${midY}, ${endX} ${endY}`)
                                    .attr("fill", "none")
                                    .attr("stroke", "rgba(255, 255, 255, 0.1)")
                                    .attr("stroke-width", 0.5);

                                // 添加动画效果
                                if (Math.random() > 0.8) {
                                    animateConnectionFlow(path);
                                }
                            }
                        });
                    }
                }
            });

            // 添加标题标签
            nodesGroup.append("text")
                .attr("x", width / 2)
                .attr("y", 30)
                .attr("text-anchor", "middle")
                .attr("font-size", "14px")
                .attr("font-weight", "bold")
                .attr("fill", "rgba(255, 255, 255, 0.9)")
                //.text("Spine 交换机");

            nodesGroup.append("text")
                .attr("x", width / 2)
                .attr("y", leafY - 20)
                .attr("text-anchor", "middle")
                .attr("font-size", "14px")
                .attr("font-weight", "bold")
                .attr("fill", "rgba(255, 255, 255, 0.9)")
                //.text("Leaf 交换机");

            nodesGroup.append("text")
                .attr("x", width / 2)
                .attr("y", serverY - 20)
                .attr("text-anchor", "middle")
                .attr("font-size", "14px")
                .attr("font-weight", "bold")
                .attr("fill", "rgba(255, 255, 255, 0.9)")
                //.text("服务器");

            // 绘制SU边界框
            susToDisplay.forEach(su => {
                // 基于是否显示所有SU或仅第一个/最后一个计算x位置
                let xPosition, boxWidth;

                if (numSU <= 2) {
                    // 2个或更少SU的原始计算
                    xPosition = (width / numSU) * su;
                    boxWidth = width / numSU;
                } else {
                    // 3个或更多SU的第一个和最后一个SU的修改计算
                    if (su === 0) {
                        xPosition = 0;
                        boxWidth = width / 2;
                    } else {
                        xPosition = width / 2;
                        boxWidth = width / 2;
                    }
                }

                connectionsGroup.append("rect")
                    .attr("x", xPosition)
                    .attr("y", 10)
                    .attr("width", boxWidth)
                    .attr("height", lastNodeY + 60)
                    .attr("fill", "none")
                    .attr("stroke", "rgba(255, 255, 255, 0.2)")
                    .attr("stroke-width", 1)
                    .attr("stroke-dasharray", "5,5");

                // 仅当这是第一个SU且有3+个SU且尚未在其他地方添加省略号时添加省略号文本
                if (numSU > 2 && su === 0 && !(numLeaf > 8)) {
                    // 仅当我们在叶子中没有省略号时才在此处添加省略号
                    nodesGroup.append("text")
                        .attr("x", width / 2)
                        .attr("y", lastNodeY + 40)
                        .attr("text-anchor", "middle")
                        .attr("font-size", "16px")
                        .attr("font-weight", "bold")
                        .attr("fill", "rgba(255, 255, 255, 0.7)")
                        .text("...");
                }

                let suLabel = `SU${su + 1}`;
                if (numSU > 2 && su === numSU - 1) {
                    suLabel = `SU${numSU}`;  // 确保最后一个SU显示正确的SU编号
                }

                let labelX;
                if (numSU <= 2) {
                    labelX = xPosition + boxWidth / 2;
                } else {
                    labelX = su === 0 ? width / 4 : width * 3/4;
                }

                const badge = nodesGroup.append("rect")
                    .attr("x", labelX - 30)
                    .attr("y", lastNodeY + 30)
                    .attr("width", 60)
                    .attr("height", 24)
                    .attr("rx", 12)
                    .attr("ry", 12)
                    .attr("fill", "rgba(1, 195, 141, 0.2)")
                    .attr("stroke", "rgba(1, 195, 141, 0.5)")
                    .attr("stroke-width", 1);

                nodesGroup.append("text")
                    .attr("x", labelX)
                    .attr("y", lastNodeY + 42)
                    .attr("text-anchor", "middle")
                    .attr("font-size", "12px")
                    .attr("font-weight", "bold")
                    .attr("fill", "rgba(255, 255, 255, 0.9)")
                    .text(suLabel);
            });

            // 执行自动缩放以适应图表
            zoomToFit();
        }

        function animateConnectionFlow(path) {
            // 创建流动动画效果
            path.append("animate")
                .attr("attributeName", "stroke-dasharray")
                .attr("from", "0,12,0,12")
                .attr("to", "12,12,12,12")
                .attr("dur", "1.5s")
                .attr("repeatCount", "indefinite");

            path.append("animate")
                .attr("attributeName", "stroke")
                .attr("from", "rgba(5, 217, 232, 0.7)")
                .attr("to", "rgba(255, 255, 255, 0.1)")
                .attr("dur", "1.5s")
                .attr("repeatCount", "indefinite");
        }

        function toggleGrid() {
            const grid = svg.select(".grid");
            const button = document.getElementById('toggleGridBtn');

            if (grid.attr("display") === "none") {
                grid.attr("display", "block");
                button.classList.add("active");
            } else {
                grid.attr("display", "none");
                button.classList.remove("active");
            }
        }


	function zoomToFit() {
	    // 获取图表的边界框
	    if (!svg) return;
	
	    const svgNode = svg.node();
	    if (!svgNode) return;
	
	    // 确保有内容元素存在
	    const contentGroup = svgNode.querySelector('.nodes');
	    if (!contentGroup) return;
	    
	    // 获取内容元素的边界框而不是整个SVG的
	    const bounds = contentGroup.getBBox();
	    
	    // 确保边界框是有效的
	    if (bounds.width === 0 || bounds.height === 0) return;
	    
	    const parent = svgNode.parentElement;
	    const fullWidth = parent.clientWidth;
	    const fullHeight = parent.clientHeight;
	
	    // 添加一些填充空间
	    const padding = 40;
	    
	    // 计算合适的缩放比例
	    const scale = 0.95 * Math.min(
	        fullWidth / (bounds.width + padding), 
	        fullHeight / (bounds.height + padding)
	    );
	
	    // 计算平移量以居中
	    const dx = (fullWidth - bounds.width * scale) / 2 - bounds.x * scale;
	    const dy = (fullHeight - bounds.height * scale) / 2 - bounds.y * scale;
	
	    // 先尝试获取现有的zoom行为
	    let zoom = d3.zoom();
	    
	    // 应用变换，确保使用动画过渡
	    svg.transition()
	       .duration(750)
	       .call(
	           zoom.transform,
	           d3.zoomIdentity.translate(dx, dy).scale(scale)
	       );
	       
	    // 记录调试信息以确认函数执行
	    console.log("zoomToFit executed:", {
	        bounds: bounds,
	        viewportSize: { width: fullWidth, height: fullHeight },
	        transform: { scale: scale, dx: dx, dy: dy }
	    });
	}
        function exportSVG() {
            if (!svg) return;

            // 获取SVG内容
            const svgData = new XMLSerializer().serializeToString(svg.node());
            const svgBlob = new Blob([svgData], {type: "image/svg+xml;charset=utf-8"});
            const svgUrl = URL.createObjectURL(svgBlob);

            // 创建下载链接
            const downloadLink = document.createElement("a");
            downloadLink.href = svgUrl;
            downloadLink.download = "network_topology.svg";
            document.body.appendChild(downloadLink);
            downloadLink.click();
            document.body.removeChild(downloadLink);

            updateStatusText("已导出SVG");
        }

        function resetParameters() {
            document.getElementById('switchType').value = 'QM9700';
            document.getElementById('networkCardType').value = '400G';
            document.getElementById('numServers').value = '128';
            document.getElementById('numNetworkCardsPerServer').value = '8';
            document.getElementById('serversPerRow').value = '8';
            document.getElementById('diagramHeight').value = '550';
            document.getElementById('spineLeafDistance').value = '150';
            document.getElementById('leafNodeDistance').value = '120';
            document.getElementById('nodeRowSpacing').value = '60';

            spineLeafValue.textContent = '150px';
            leafNodeValue.textContent = '120px';
            nodeRowValue.textContent = '60px';

            updateStatusText("参数已重置");
        }

        function showTooltip(event, content) {
            tooltip.innerHTML = content;
            tooltip.style.left = (event.pageX) + 'px';
            tooltip.style.top = (event.pageY) + 'px';
            tooltip.style.opacity = 1;
        }

        function moveTooltip(event) {
            tooltip.style.left = (event.pageX) + 'px';
            tooltip.style.top = (event.pageY) + 'px';
        }

        function hideTooltip() {
            tooltip.style.opacity = 0;
        }

        function showLoading() {
            // 创建加载指示器
            const loading = document.createElement('div');
            loading.className = 'loading';
            loading.id = 'loadingIndicator';

            const loader = document.createElement('div');
            loader.className = 'loader';
            loading.appendChild(loader);

            document.getElementById('diagram-container').appendChild(loading);
        }

        function hideLoading() {
            const loading = document.getElementById('loadingIndicator');
            if (loading) {
                loading.remove();
            }
        }

        function updateStatusText(text) {
            document.getElementById('statusText').textContent = text;
        }

        // 监听窗口大小变化，调整图表
        window.addEventListener('resize', debounce(function() {
            if (svg) {
                zoomToFit();
            }
        }, 250));

        // 防抖函数，避免频繁调用
        function debounce(func, wait) {
            let timeout;
            return function() {
                const context = this;
                const args = arguments;
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    func.apply(context, args);
                }, wait);
            };
        }

        // 添加拖动功能
        document.getElementById('diagram-container').addEventListener('mousedown', function(e) {
            if (e.target.tagName === 'svg' || e.target.closest('svg')) {
                isDragging = true;
                lastX = e.pageX;
                lastY = e.pageY;
                document.getElementById('diagram-container').style.cursor = 'grabbing';
            }
        });

        document.addEventListener('mousemove', function(e) {
            if (isDragging) {
                const dx = e.pageX - lastX;
                const dy = e.pageY - lastY;
                lastX = e.pageX;
                lastY = e.pageY;

                // 获取当前变换
                const transform = d3.zoomTransform(svg.node());
                // 应用新的平移
                const newTransform = transform.translate(dx / transform.k, dy / transform.k);
                // 应用变换
                svg.call(d3.zoom().transform, newTransform);
            }
        });

        document.addEventListener('mouseup', function() {
            if (isDragging) {
                isDragging = false;
                document.getElementById('diagram-container').style.cursor = 'auto';
            }
        });

        // 添加滚轮缩放功能
        document.getElementById('diagram-container').addEventListener('wheel', function(e) {
            if (svg) {
                e.preventDefault();
                const direction = e.deltaY < 0 ? 1 : -1;
                const transform = d3.zoomTransform(svg.node());
                const scale = transform.k * (1 + direction * 0.1);
                const newScale = Math.max(0.1, Math.min(10, scale));

                // 计算缩放中心点
                const point = d3.pointer(e, svg.node());

                // 应用新的缩放
                const newTransform = transform.scale(newScale / transform.k, point[0], point[1]);

                // 应用变换
                svg.call(d3.zoom().transform, newTransform);
            }
        });
    });
