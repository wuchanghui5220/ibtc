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
  
  calculateAndDraw();
}

function calculateAndDraw() {
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
  const numSpineSwitches = possibleSpineCounts.find(count => count >= numLeafSwitches * leafUplinks / switchPorts);
  const totalPorts = numLeafSwitches * switchPorts + numSpineSwitches * switchPorts;
  const totalCables = numServers * numNetworkCardsPerServer + numLeafSwitches * numSpineSwitches;
  const cablesPerLineLeafToSpine = Math.floor(leafUplinks / numSpineSwitches);
  const cablesPerLineLeafToNode = 1;

  const results = `
    <p><strong>Switch Type:</strong> ${switchType}</p>
    <p><strong>Network Card Type:</strong> ${networkCardType}</p>
    <p><strong>Number of Scalable Units (SUs):</strong> ${numSU}</p>
    <p><strong>Number of Spine Switches:</strong> ${numSpineSwitches}</p>
    <p><strong>Number of Leaf Switches:</strong> ${numLeafSwitches}</p>
    <p><strong>Total number of servers:</strong> ${numServers}</p>
    <p><strong>Total number of switch ports:</strong> ${totalPorts}</p>
    <p><strong>Total number of cables:</strong> ${totalCables}</p>
    <p><strong>Cables per line in diagram:</strong></p>
    <ul>
      <li>Leaf to Spine: ${cablesPerLineLeafToSpine}</li>
      <li>Leaf to Node: ${cablesPerLineLeafToNode}</li>
    </ul>
  `;
  
  document.getElementById('results').innerHTML = results;
  
  drawTopology(numSU, numSpineSwitches, numLeafSwitches, numServers, numNetworkCardsPerServer, serversPerSU, spineLeafDistance, leafNodeDistance, serversPerRow, diagramHeight, nodeRowSpacing);
}

function drawTopology(numSU, numSpine, numLeaf, numServers, numNetworkCardsPerServer, serversPerSU, spineLeafDistance, leafNodeDistance, serversPerRow, diagramHeight, nodeRowSpacing) {
  // Adjust width based on whether we're showing all elements or just some
  let displayWidth;
  if (numSU <= 2) {
    // Full width for all elements
    displayWidth = Math.max(Math.min(window.innerWidth - 40, 1200), numLeaf * 80);
  } else {
    // Reduced width for simplified view - no need for full width
    displayWidth = Math.max(Math.min(window.innerWidth - 40, 1200), 800);
  }
  
  const width = displayWidth;
  const height = diagramHeight;
  const spineY = 50;
  const leafY = spineY + spineLeafDistance;
  const serverY = leafY + leafNodeDistance;
  
  d3.select("#diagram").selectAll("*").remove();
  const svg = d3.select("#diagram")
    .append("svg")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("width", width)
    .attr("height", height);

  const connectionsGroup = svg.append("g").attr("class", "connections");
  const nodesGroup = svg.append("g").attr("class", "nodes");
  
  // Determine which Spine switches to display based on the total number
  let spinesToDisplay = [];
  if (numSpine <= 8) {
    // If 8 or fewer spines, display all of them
    spinesToDisplay = Array.from({ length: numSpine }, (_, i) => i);
  } else {
    // If more than 8 spines, display first 4 and last 4
    for (let i = 0; i < 4; i++) {
      spinesToDisplay.push(i);              // First 4
    }
    for (let i = numSpine - 4; i < numSpine; i++) {
      spinesToDisplay.push(i);              // Last 4
    }
  }
  
  // Function to calculate X position of spine switches
  const spineX = d => {
    if (numSpine <= 8) {
      // Original calculation for 8 or fewer spines
      return (width / (numSpine + 1)) * (d + 1);
    } else {
      // Modified calculation for displayed spines when more than 8
      if (d < 4) {
        // First 4 spines use left 45% of width
        return width * (0.1 + 0.35 * (d / 4));
      } else {
        // Last 4 spines use right 45% of width
        return width * (0.6 + 0.35 * ((d - (numSpine - 4)) / 4));
      }
    }
  };
  
  // Create spine switch rectangles for displayed spines only
  spinesToDisplay.forEach(spineIndex => {
    nodesGroup.append("rect")
      .attr("class", "spine")
      .attr("x", spineX(spineIndex) - 30)
      .attr("y", spineY)
      .attr("width", 60)
      .attr("height", 30)
      .attr("fill", "#3498db");
      
    nodesGroup.append("text")
      .attr("class", "spine-label")
      .attr("x", spineX(spineIndex))
      .attr("y", spineY + 15)
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("font-size", "10px")
      .attr("fill", "white")
      .text(`Spine ${spineIndex + 1}`);
  });
  
  // Add ellipsis for spine switches if we're not showing all
  if (numSpine > 8) {
    nodesGroup.append("text")
      .attr("x", width / 2)
      .attr("y", spineY + 15)
      .attr("text-anchor", "middle")
      .attr("font-size", "14px")
      .attr("font-weight", "bold")
      .attr("fill", "#3498db")
      .text("...");
  }
  
  // Determine which Leaf switches to display based on the total number and SUs
  let leavesToDisplay = [];
  if (numSU <= 2 || numLeaf <= 8) {
    // If 2 or fewer SUs or 8 or fewer leaves, display all leaves
    leavesToDisplay = Array.from({ length: numLeaf }, (_, i) => i);
  } else {
    // If 3+ SUs and 9+ leaves, display only some leaves
    const leavesPerSU = numNetworkCardsPerServer;
    
    // Show leaves for first SU
    for (let i = 0; i < leavesPerSU; i++) {
      leavesToDisplay.push(i);
    }
    
    // Show leaves for last SU
    const lastSUStartIndex = numLeaf - leavesPerSU;
    for (let i = lastSUStartIndex; i < numLeaf; i++) {
      // Only add if not already added (avoid duplicates in case of few SUs)
      if (!leavesToDisplay.includes(i)) {
        leavesToDisplay.push(i);
      }
    }
    
    // Sort to maintain order
    leavesToDisplay.sort((a, b) => a - b);
  }
  
  // Function to calculate X position of leaf switches - FIXED to prevent overlap
  const leafX = d => {
    if (numSU <= 2 || numLeaf <= 8) {
      // Calculate position for all leaves when few SUs
      return (width / (numLeaf + 1)) * (d + 1);
    } else {
      // We need to fix the spacing for leaves
      const leavesPerSide = leavesToDisplay.length / 2;
      
      // Figure out if this is a first half or second half leaf
      if (d < numNetworkCardsPerServer) {
        // First SU leaves
        const index = d;
        // Position in left 40% of screen with proper spacing
        return width * (0.01 + 0.5 * (index + 1) / (leavesPerSide + 1));
      } else {
        // Last SU leaves
        const index = d - (numLeaf - numNetworkCardsPerServer);
        // Position in right 40% of screen with proper spacing
        return width * (0.5 + 0.5 * (index + 1) / (leavesPerSide + 1));
      }
    }
  };
  
  // Create leaf switch rectangles for displayed leaves only
  leavesToDisplay.forEach(leafIndex => {
    nodesGroup.append("rect")
      .attr("class", "leaf")
      .attr("x", leafX(leafIndex) - 30)
      .attr("y", leafY)
      .attr("width", 60)
      .attr("height", 30)
      .attr("fill", "#3498db");
      
    nodesGroup.append("text")
      .attr("class", "leaf-label")
      .attr("x", leafX(leafIndex))
      .attr("y", leafY + 15)
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("font-size", "10px")
      .attr("fill", "white")
      .text(`Leaf ${leafIndex + 1}`);
  });
  
  // Add ellipsis for leaf switches if we're not showing all
  if (numSU > 2 && numLeaf > 8) {
    nodesGroup.append("text")
      .attr("x", width / 2)
      .attr("y", leafY + 15)
      .attr("text-anchor", "middle")
      .attr("font-size", "14px")
      .attr("font-weight", "bold")
      .attr("fill", "#3498db")
      .text("...");
  }
  
  // Create curved connections between displayed spine and leaf switches
  leavesToDisplay.forEach(l => {
    spinesToDisplay.forEach(s => {
      const startX = spineX(s);
      const startY = spineY + 30;
      const endX = leafX(l);
      const endY = leafY;
      const midY = (startY + endY) / 2;

      connectionsGroup.append("path")
        .attr("d", `M ${startX} ${startY} C ${startX} ${midY}, ${endX} ${midY}, ${endX} ${endY}`)
        .attr("fill", "none")
        .attr("stroke", "#34495e")
        .attr("stroke-width", 0.5);
    });
  });
  
  // Constants for server nodes
  const serverWidth = 50;
  const serverHeight = 20;
  
  // Adjust server spacing based on the number of servers in a row and available width
  let serverSpacing;
  if (numSU <= 2) {
    // For normal view with all SUs
    serverSpacing = Math.min(60, (width / numSU) / (serversPerRow + 1));
  } else {
    // For simplified view with just first and last SU
    // Use more space since we're only showing 2 SUs instead of all
    serverSpacing = Math.min(60, (width / 2) / (serversPerRow + 1));
  }
  
  const totalRows = Math.ceil(Math.max(...Array.from({ length: numSU }, (_, i) => 
    Math.min(serversPerSU, numServers - i * serversPerSU)
  )) / serversPerRow);
  
  const totalServerHeight = (totalRows - 1) * nodeRowSpacing;
  const availableHeight = height - serverY - 60;
  const verticalScale = Math.min(1, availableHeight / totalServerHeight);
  
  // Determine which SUs to display based on the total number
  let susToDisplay = [];
  if (numSU <= 2) {
    // If 2 or fewer SUs, display all of them
    susToDisplay = Array.from({ length: numSU }, (_, i) => i);
  } else {
    // If 3 or more SUs, display only the first and last SU
    susToDisplay = [0, numSU - 1];
  }
  
  let lastNodeY = 0;
  
  // Only render the servers for the SUs we want to display
  susToDisplay.forEach(su => {
    const serversInThisSU = Math.min(serversPerSU, numServers - su * serversPerSU);
    
    for (let s = 0; s < serversInThisSU; s++) {
      const row = Math.floor(s / serversPerRow);
      const col = s % serversPerRow;
      
      // Adjust x-coordinate calculation for when only showing first and last SU
      let x;
      if (numSU <= 2) {
        // For 2 or fewer SUs - evenly distributed
        x = width * ((su + 0.5) / numSU) + (col - serversPerRow / 2 + 0.5) * serverSpacing;
      } else {
        // For first and last SU when 3 or more SUs
        // Place at 1/4 and 3/4 of width with proper spacing
        const suPosition = su === 0 ? 0.25 : 0.75;
        x = width * suPosition + (col - serversPerRow / 2 + 0.5) * serverSpacing;
      }
      
      const y = serverY + row * nodeRowSpacing * verticalScale;
      lastNodeY = Math.max(lastNodeY, y);
      
      // Calculate a unique ID for the node
      const nodeId = su * serversPerSU + s + 1;
      
      nodesGroup.append("rect")
        .attr("class", "server")
        .attr("x", x - serverWidth / 2)
        .attr("y", y - serverHeight / 2)
        .attr("width", serverWidth)
        .attr("height", serverHeight)
        .attr("rx", 5)
        .attr("ry", 5)
        .attr("fill", "#2ecc71");
      
      nodesGroup.append("text")
        .attr("class", "server-label")
        .attr("x", x)
        .attr("y", y)
        .attr("text-anchor", "middle")
        .attr("dominant-baseline", "middle")
        .attr("font-size", "8px")
        .attr("fill", "white")
        .text(`Node ${nodeId}`);
      
      // Create curved connections between leaf switches and servers
      // Only create connections to visible leaf switches
      if (leavesToDisplay.length > 0) {
        // Determine which leaf switches connect to this server
        let connectedLeaves = [];
        
        if (numSU <= 2 || numLeaf <= 8) {
          // When showing all leaves, connect to the correct ones for this SU
          for (let nc = 0; nc < numNetworkCardsPerServer; nc++) {
            const leafIndex = su * numNetworkCardsPerServer + nc;
            if (leafIndex < numLeaf) {
              connectedLeaves.push(leafIndex);
            }
          }
        } else {
          // When showing only some leaves, make logical connections:
          if (su === 0) {
            // First SU servers connect to first SU leaves (first half of leavesToDisplay)
            connectedLeaves = leavesToDisplay.filter(l => l < numNetworkCardsPerServer);
          } else if (su === numSU - 1) {
            // Last SU servers connect to last SU leaves (second half of leavesToDisplay)
            connectedLeaves = leavesToDisplay.filter(l => l >= numLeaf - numNetworkCardsPerServer);
          }
        }
        
        // Create connections
        connectedLeaves.forEach(leafIndex => {
          if (leavesToDisplay.includes(leafIndex)) {
            const startX = leafX(leafIndex);
            const startY = leafY + 30;
            const endX = x;
            const endY = y - serverHeight / 2;
            const midY = (startY + endY) / 2;

            connectionsGroup.append("path")
              .attr("d", `M ${startX} ${startY} C ${startX} ${midY}, ${endX} ${midY}, ${endX} ${endY}`)
              .attr("fill", "none")
              .attr("stroke", "#bdc3c7")
              .attr("stroke-width", 0.5);
          }
        });
      }
    }
  });
  
  // Add title labels
  nodesGroup.append("text")
    .attr("x", width / 2)
    .attr("y", 30)
    .attr("text-anchor", "middle")
    .attr("font-size", "14px")
    .attr("font-weight", "bold")
    .text("Spine Switches");
  
  nodesGroup.append("text")
    .attr("x", width / 2)
    .attr("y", leafY - 20)
    .attr("text-anchor", "middle")
    .attr("font-size", "14px")
    .attr("font-weight", "bold")
    .text("Leaf Switches");
  
  nodesGroup.append("text")
    .attr("x", width / 2)
    .attr("y", serverY - 20)
    .attr("text-anchor", "middle")
    .attr("font-size", "14px")
    .attr("font-weight", "bold")
    .text("Servers");
  
  // Draw SU boundary boxes
  susToDisplay.forEach(su => {
    // Calculate x position based on whether we're showing all SUs or just first/last
    let xPosition, boxWidth;
    
    if (numSU <= 2) {
      // Original calculation for 2 or fewer SUs
      xPosition = (width / numSU) * su;
      boxWidth = width / numSU;
    } else {
      // Modified calculation for first and last SU when 3 or more SUs
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
      .attr("stroke", "#95a5a6")
      .attr("stroke-width", 2)
      .attr("stroke-dasharray", "5,5");
    
    // Only add ellipsis text if this is the first SU and we have 3+ SUs
    // and it hasn't been added elsewhere already
    if (numSU > 2 && su === 0 && !(numLeaf > 8)) { 
      // Only add ellipsis here if we don't already have one in the leaves
      nodesGroup.append("text")
        .attr("x", width / 2)
        .attr("y", lastNodeY + 40)
        .attr("text-anchor", "middle")
        .attr("font-size", "16px")
        .attr("font-weight", "bold")
        .text("...");
    }
    
    let suLabel = `SU${su + 1}`;
    if (numSU > 2 && su === numSU - 1) {
      suLabel = `SU${numSU}`;  // Make sure to show the correct SU number for the last SU
    }
    
    let labelX;
    if (numSU <= 2) {
      labelX = xPosition + boxWidth / 2;
    } else {
      labelX = su === 0 ? width / 4 : width * 3/4;
    }
    
    nodesGroup.append("text")
      .attr("x", labelX)
      .attr("y", lastNodeY + 40)
      .attr("text-anchor", "middle")
      .attr("font-size", "14px")
      .attr("font-weight", "bold")
      .text(suLabel);
  });
}
