// API Configuration
const API_BASE_URL = window.location.origin;
const WS_BASE_URL = window.location.origin.replace("http", "ws");

// Application State
let currentUser = null;
let currentWallets = [];
let websocket = null;
let monitoredWalletAddress = null;
let liveUpdates = [];
let deposits = [];
let networks = [];
let defaultNetworkId = null;

// Initialize the application
document.addEventListener("DOMContentLoaded", () => {
  initializeApp();
  setupEventListeners();
});

async function initializeApp() {
  await checkApiStatus();
  await loadNetworks();
}

function setupEventListeners() {
  // User forms
  document
    .getElementById("createUserForm")
    .addEventListener("submit", handleCreateUser);
  document
    .getElementById("updateForm")
    .addEventListener("submit", handleUpdateUser);
  document.getElementById("searchEmail").addEventListener("keypress", (e) => {
    if (e.key === "Enter") searchUserByEmail();
  });

  // Wallet form
  document
    .getElementById("addWalletForm")
    .addEventListener("submit", handleAddWallet);
}

// ============ API Status ============
async function checkApiStatus() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (response.ok) {
      updateStatusIndicator("apiStatus", "Healthy", "connected");
    } else {
      updateStatusIndicator("apiStatus", "Error", "disconnected");
    }
  } catch (error) {
    updateStatusIndicator("apiStatus", "Offline", "disconnected");
    showToast("Cannot connect to API", "error");
  }
}

function updateStatusIndicator(elementId, text, statusClass) {
  const element = document.getElementById(elementId);
  element.textContent = text;
  element.className = `status-value status-${statusClass}`;
}

// ============ Toast Notifications ============
function showToast(message, type = "info") {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className = `toast ${type}`;
  toast.classList.add("show");

  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}

// ============ User Management ============
async function handleCreateUser(e) {
  e.preventDefault();

  const email = document.getElementById("userEmail").value;
  const firstName = document.getElementById("userFirstName").value;
  const lastName = document.getElementById("userLastName").value;

  try {
    const response = await fetch(`${API_BASE_URL}/users/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email,
        first_name: firstName,
        last_name: lastName,
      }),
    });

    if (response.ok) {
      const user = await response.json();
      showToast("User created successfully!", "success");
      displayCurrentUser(user);
      document.getElementById("createUserForm").reset();
    } else {
      const error = await response.json();
      showToast(error.detail || "Failed to create user", "error");
    }
  } catch (error) {
    showToast("Error creating user: " + error.message, "error");
  }
}

async function searchUserByEmail() {
  const email = document.getElementById("searchEmail").value.trim();
  if (!email) {
    showToast("Please enter an email address", "warning");
    return;
  }

  try {
    const response = await fetch(
      `${API_BASE_URL}/users/by-email/${encodeURIComponent(email)}`,
    );

    if (response.ok) {
      const user = await response.json();
      displayCurrentUser(user);
      showToast("User found!", "success");
    } else if (response.status === 404) {
      showToast("User not found", "warning");
    } else {
      const error = await response.json();
      showToast(error.detail || "Failed to search user", "error");
    }
  } catch (error) {
    showToast("Error searching user: " + error.message, "error");
  }
}

function displayCurrentUser(user) {
  currentUser = user;

  document.getElementById("currentUserId").textContent = user.id;
  document.getElementById("currentUserName").textContent =
    `${user.first_name} ${user.last_name}`;
  document.getElementById("currentUserEmail").textContent = user.email;
  document.getElementById("currentUser").style.display = "block";

  // Enable wallet form
  document.getElementById("addWalletBtn").disabled = false;

  // Load user's wallets
  loadUserWallets(user.id);
}

function showUpdateUserForm() {
  document.getElementById("updateUserForm").style.display = "block";

  // Pre-fill current values
  document.getElementById("updateEmail").placeholder = currentUser.email;
  document.getElementById("updateFirstName").placeholder =
    currentUser.first_name;
  document.getElementById("updateLastName").placeholder = currentUser.last_name;
}

function hideUpdateUserForm() {
  document.getElementById("updateUserForm").style.display = "none";
  document.getElementById("updateForm").reset();
}

async function handleUpdateUser(e) {
  e.preventDefault();

  if (!currentUser) {
    showToast("No user selected", "warning");
    return;
  }

  const email = document.getElementById("updateEmail").value.trim();
  const firstName = document.getElementById("updateFirstName").value.trim();
  const lastName = document.getElementById("updateLastName").value.trim();

  // Build update object with only provided fields
  const updateData = {};
  if (email) updateData.email = email;
  if (firstName) updateData.first_name = firstName;
  if (lastName) updateData.last_name = lastName;

  if (Object.keys(updateData).length === 0) {
    showToast("Please provide at least one field to update", "warning");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/users/${currentUser.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updateData),
    });

    if (response.ok) {
      const updatedUser = await response.json();
      displayCurrentUser(updatedUser);
      hideUpdateUserForm();
      showToast("User updated successfully!", "success");
    } else {
      const error = await response.json();
      showToast(error.detail || "Failed to update user", "error");
    }
  } catch (error) {
    showToast("Error updating user: " + error.message, "error");
  }
}

// ============ Wallet Management ============
async function handleAddWallet(e) {
  e.preventDefault();

  if (!currentUser) {
    showToast("Please select a user first", "warning");
    return;
  }

  if (!defaultNetworkId) {
    showToast(
      "Network information not loaded. Please refresh the page.",
      "error",
    );
    return;
  }

  const address = document.getElementById("walletAddress").value.trim();
  const label = document.getElementById("walletLabel").value.trim();

  try {
    const response = await fetch(`${API_BASE_URL}/wallets/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: currentUser.id,
        address: address,
        label: label || null,
        blockchain_network_id: defaultNetworkId,
      }),
    });

    if (response.ok) {
      const wallet = await response.json();
      showToast("Wallet added successfully!", "success");
      document.getElementById("addWalletForm").reset();
      await loadUserWallets(currentUser.id);
    } else {
      const error = await response.json();
      showToast(error.detail || "Failed to add wallet", "error");
    }
  } catch (error) {
    showToast("Error adding wallet: " + error.message, "error");
  }
}

async function loadUserWallets(userId) {
  try {
    const response = await fetch(`${API_BASE_URL}/wallets/user/${userId}`);

    if (response.ok) {
      const wallets = await response.json();
      currentWallets = wallets;
      displayWallets(wallets);
    } else {
      showToast("Failed to load wallets", "error");
    }
  } catch (error) {
    showToast("Error loading wallets: " + error.message, "error");
  }
}

function displayWallets(wallets) {
  const walletsContainer = document.getElementById("walletsList");
  const walletsContent = document.getElementById("walletsContent");
  const walletSelect = document.getElementById("walletSelect");
  const monitoringControls = document.getElementById("monitoringControls");
  const noWalletMessage = document.getElementById("noWalletMessage");

  if (wallets.length === 0) {
    walletsContainer.style.display = "none";
    monitoringControls.style.display = "none";
    noWalletMessage.style.display = "block";
    return;
  }

  walletsContainer.style.display = "block";
  monitoringControls.style.display = "block";
  noWalletMessage.style.display = "none";

  // Display wallet list
  walletsContent.innerHTML = wallets
    .map(
      (wallet) => `
        <div class="wallet-item">
            <div class="wallet-info">
                <div class="wallet-address">${wallet.address}</div>
                ${wallet.label ? `<div class="wallet-label">${wallet.label}</div>` : ""}
                <span class="wallet-network">Ethereum Sepolia</span>
            </div>
            <div class="wallet-actions">
                <button class="btn btn-small btn-primary" onclick="selectWalletForMonitoring('${wallet.address}')">
                    Monitor
                </button>
            </div>
        </div>
    `,
    )
    .join("");

  // Update wallet select dropdown
  walletSelect.innerHTML =
    '<option value="">Select a wallet to monitor</option>' +
    wallets
      .map(
        (wallet) => `
            <option value="${wallet.address}">
                ${wallet.label ? wallet.label + " - " : ""}${wallet.address.substring(0, 10)}...${wallet.address.substring(wallet.address.length - 8)}
            </option>
        `,
      )
      .join("");
}

function selectWalletForMonitoring(address) {
  document.getElementById("walletSelect").value = address;
  startMonitoring();
}

// ============ WebSocket & Monitoring ============
function startMonitoring() {
  const selectedAddress = document.getElementById("walletSelect").value;

  if (!selectedAddress) {
    showToast("Please select a wallet to monitor", "warning");
    return;
  }

  // Stop existing connection if any
  if (websocket) {
    stopMonitoring();
  }

  monitoredWalletAddress = selectedAddress;

  // Connect WebSocket
  connectWebSocket(selectedAddress);

  // Update UI
  document.getElementById("startMonitorBtn").style.display = "none";
  document.getElementById("stopMonitorBtn").style.display = "block";
  document.getElementById("monitoringActive").style.display = "block";
  document.getElementById("monitoredAddress").textContent = selectedAddress;

  // Clear previous data
  liveUpdates = [];
  document.getElementById("liveUpdatesList").innerHTML =
    '<div class="empty-state"><p>Waiting for updates...</p></div>';

  // Load existing deposits
  loadDeposits(selectedAddress);

  showToast("Monitoring started!", "success");
}

function stopMonitoring() {
  if (websocket) {
    websocket.close();
    websocket = null;
  }

  monitoredWalletAddress = null;

  document.getElementById("startMonitorBtn").style.display = "block";
  document.getElementById("stopMonitorBtn").style.display = "none";
  document.getElementById("monitoringActive").style.display = "none";

  updateStatusIndicator("wsStatus", "Disconnected", "disconnected");
  showToast("Monitoring stopped", "info");
}

function connectWebSocket(walletAddress) {
  const wsUrl = `${WS_BASE_URL}/ws/?wallet_address=${walletAddress}`;

  try {
    websocket = new WebSocket(wsUrl);
    let pingInterval = null;

    websocket.onopen = () => {
      updateStatusIndicator("wsStatus", "Connected", "connected");
      showToast("WebSocket connected", "success");

      // Start sending ping messages every 30 seconds to keep connection alive
      pingInterval = setInterval(() => {
        if (websocket && websocket.readyState === WebSocket.OPEN) {
          websocket.send("ping");
        }
      }, 30000);
    };

    websocket.onmessage = (event) => {
      console.log("WebSocket message received:", event.data);
      
      // Handle pong responses
      if (event.data === "pong") {
        console.log("Received pong from server");
        return;
      }

      try {
        const message = JSON.parse(event.data);
        console.log("Parsed message:", message);

        // Handle connection confirmation message
        if (message.type === "connected") {
          console.log("WebSocket connection confirmed:", message.message);
          return;
        }

        handleWebSocketMessage(message);
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    };

    websocket.onerror = (error) => {
      console.error("WebSocket error:", error);
      updateStatusIndicator("wsStatus", "Error", "disconnected");
      showToast("WebSocket connection error", "error");
      if (pingInterval) clearInterval(pingInterval);
    };

    websocket.onclose = () => {
      updateStatusIndicator("wsStatus", "Disconnected", "disconnected");
      if (pingInterval) clearInterval(pingInterval);

      if (monitoredWalletAddress) {
        showToast(
          "WebSocket disconnected. Attempting to reconnect...",
          "warning",
        );
        // Attempt to reconnect after 5 seconds
        setTimeout(() => {
          if (monitoredWalletAddress) {
            connectWebSocket(monitoredWalletAddress);
          }
        }, 5000);
      }
    };
  } catch (error) {
    showToast("Failed to connect WebSocket: " + error.message, "error");
  }
}

function handleWebSocketMessage(message) {
  console.log("Handling WebSocket message:", message);

  const update = {
    type: message.type,
    data: message.data || message, // Handle confirmation_update which doesn't have data wrapper
    timestamp: new Date(),
  };

  liveUpdates.unshift(update);
  console.log("Added to liveUpdates, total:", liveUpdates.length);
  displayLiveUpdates();

  // Show toast for important events
  switch (message.type) {
    case "deposit_update":
      const amount = parseFloat(message.data.amount).toFixed(6);
      showToast(`New deposit detected: ${amount} ETH`, "info");
      refreshDeposits();
      break;
    case "deposit_detected":
      const detectedAmount = parseFloat(message.data.amount).toFixed(6);
      showToast(`New deposit detected: ${detectedAmount} ETH`, "info");
      refreshDeposits();
      break;
    case "deposit_completed":
      showToast(
        `Deposit completed: ${message.data.tx_hash.substring(0, 10)}...`,
        "success",
      );
      refreshDeposits();
      break;
    case "deposit_orphaned":
      showToast(
        `Deposit orphaned (reorg): ${message.data.tx_hash.substring(0, 10)}...`,
        "warning",
      );
      refreshDeposits();
      break;
    case "confirmation_update":
      console.log("Confirmation update received:", message);
      const confirmations = message.confirmations || message.data?.confirmations || 0;
      const tx_hash = message.tx_hash || message.data?.tx_hash || '';
      const status = message.status || message.data?.status || '';
      
      showToast(`Confirmations updated: ${confirmations} (Status: ${status})`, "info");
      refreshDeposits();
      break;
  }
}

function displayLiveUpdates() {
  const container = document.getElementById("liveUpdatesList");

  if (liveUpdates.length === 0) {
    container.innerHTML =
      '<div class="empty-state"><p>Waiting for updates...</p></div>';
    return;
  }

  container.innerHTML = liveUpdates
    .slice(0, 10)
    .map((update) => {
      const typeClass = update.type.replace(/_/g, "-");
      const typeLabel = update.type.replace(/_/g, " ");

      return `
            <div class="update-item ${typeClass}">
                <div class="update-type">${typeLabel}</div>
                <div class="update-time">${formatTime(update.timestamp)}</div>
                <div class="update-details">
                    ${formatUpdateDetails(update)}
                </div>
            </div>
        `;
    })
    .join("");
}

function formatUpdateDetails(update) {
  const data = update.data || update;
  let details = [];

  if (data.tx_hash) {
    details.push(
      `TX: ${data.tx_hash.substring(0, 10)}...${data.tx_hash.substring(data.tx_hash.length - 8)}`,
    );
  }
  if (data.amount) {
    const formattedAmount = parseFloat(data.amount).toFixed(6);
    details.push(`Amount: ${formattedAmount} ETH`);
  }
  if (data.confirmations !== undefined) {
    details.push(`Confirmations: ${data.confirmations}`);
  }
  if (data.status) {
    details.push(`Status: ${data.status}`);
  }

  return details.join(" • ");
}

function formatTime(date) {
  return date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

// ============ Deposits ============
async function loadDeposits(walletAddress) {
  try {
    // First, get the wallet ID from the address
    const wallet = currentWallets.find(
      (w) => w.address.toLowerCase() === walletAddress.toLowerCase(),
    );

    if (!wallet) {
      showToast("Wallet not found", "error");
      return;
    }

    const response = await fetch(
      `${API_BASE_URL}/deposits/wallet/${wallet.id}`,
    );

    if (response.ok) {
      deposits = await response.json();
      displayDeposits(deposits);
    } else if (response.status === 404) {
      deposits = [];
      displayDeposits([]);
    } else {
      showToast("Failed to load deposits", "error");
    }
  } catch (error) {
    showToast("Error loading deposits: " + error.message, "error");
  }
}

function displayDeposits(deposits) {
  const container = document.getElementById("depositsList");

  if (deposits.length === 0) {
    container.innerHTML =
      '<div class="empty-state"><p>No deposits found</p><p>Send ETH to this wallet address to see it appear here!</p></div>';
    return;
  }

    container.innerHTML = deposits
    .map((deposit) => {
      const statusClass = deposit.status.toLowerCase().replace(" ", "-");
      // Format amount to 6 decimal places
      const formattedAmount = parseFloat(deposit.amount).toFixed(6);

      return `
            <div class="deposit-item">
                <div class="deposit-header">
                    <div class="deposit-hash">${deposit.tx_hash.substring(0, 10)}...${deposit.tx_hash.substring(deposit.tx_hash.length - 8)}</div>
                    <span class="deposit-status status-${statusClass}">${deposit.status}</span>
                </div>
                <div class="deposit-details">
                    <div class="detail-item">
                        <span class="detail-label">Amount</span>
                        <span class="detail-value amount-value">${formattedAmount} ETH</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Confirmations</span>
                        <span class="detail-value">${deposit.confirmations}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Block Number</span>
                        <span class="detail-value">${deposit.block_number}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Detected At</span>
                        <span class="detail-value">${formatDate(deposit.created_at)}</span>
                    </div>
                    ${
                      deposit.status === "completed" && deposit.updated_at
                        ? `
                        <div class="detail-item">
                            <span class="detail-label">Confirmed At</span>
                            <span class="detail-value">${formatDate(deposit.updated_at)}</span>
                        </div>
                    `
                        : ""
                    }
                </div>
            </div>
        `;
    })
    .join("");
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

async function refreshDeposits() {
  if (monitoredWalletAddress) {
    await loadDeposits(monitoredWalletAddress);
  }
}

// ============ Networks ============
async function loadNetworks() {
  try {
    const response = await fetch(`${API_BASE_URL}/blockchain-networks/`);

    if (response.ok) {
      networks = await response.json();
      if (networks.length > 0) {
        // Set the first active network as default
        const activeNetwork = networks.find((n) => n.is_active) || networks[0];
        defaultNetworkId = activeNetwork.id;
      }
      displayNetworks(networks);
    } else {
      console.error("Failed to load networks");
    }
  } catch (error) {
    console.error("Error loading networks:", error);
  }
}

function displayNetworks(networks) {
  const container = document.getElementById("networksList");

  if (networks.length === 0) {
    container.innerHTML =
      '<div class="empty-state"><p>No networks configured</p></div>';
    return;
  }

  container.innerHTML = networks
    .map(
      (network) => `
        <div class="network-item">
            <div class="network-name">${network.name}</div>
            <div class="network-detail"><strong>Chain ID:</strong> ${network.chain_id}</div>
            <div class="network-detail"><strong>Confirmations Required:</strong> ${network.confirmations_required}</div>
            <div class="network-detail"><strong>Block Time:</strong> ${network.block_time || 'N/A'}s</div>
        </div>
    `,
    )
    .join("");
}

// ============ Utility Functions ============
function truncateAddress(address) {
  if (!address) return "";
  return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
}
