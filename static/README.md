# Crypto Deposit Monitor - Web UI

A simple, intuitive web interface for testing and demonstrating the Crypto Deposit Monitor API.

## Features

### 👤 User Management
- **Create New Users**: Enter email, first name, and last name to create a new user account
- **Search Users**: Find existing users by their email address
- **Update Users**: Modify user information (email, first name, last name) - all fields optional

### 👛 Wallet Management
- **Add Wallets**: Associate Ethereum wallet addresses with users
- **Label Wallets**: Optionally add descriptive labels to wallets for easy identification
- **View All Wallets**: See all wallets associated with the current user
- **Quick Monitor**: Select any wallet to start monitoring immediately

### 📊 Real-Time Deposit Monitoring
- **Live WebSocket Updates**: Real-time notifications for blockchain events
- **Deposit History**: View all historical deposits for a wallet
- **Status Tracking**: Visual indicators for pending, confirmed, and orphaned deposits
- **Confirmation Counts**: Track confirmation progress for each deposit
- **Event Log**: Live feed showing all deposit-related events as they happen

### ⛓️ Network Information
- **Supported Networks**: View configured blockchain networks
- **Network Details**: See chain IDs, confirmation requirements, and block times

## Getting Started

### Prerequisites
Make sure the backend API is running:
```bash
# Option 1: Using Docker
docker-compose up

# Option 2: Local development
uvicorn app.main:app --reload
```

### Access the UI
Once the backend is running, open your browser and navigate to:
```
http://localhost:8000
```

## Usage Guide

### Step 1: Create or Find a User
1. **Create New User**:
   - Enter email, first name, and last name in the "Create New User" form
   - Click "Create User"
   - The user will be automatically selected

2. **Search Existing User**:
   - Enter the user's email in the "Search User by Email" field
   - Click "Search" or press Enter
   - If found, the user will be displayed and selected

### Step 2: Add a Wallet
1. Make sure a user is selected (you should see "Current User" section)
2. Enter a valid Ethereum wallet address (must start with `0x` and be 42 characters)
3. Optionally add a label for easy identification (e.g., "Main Wallet", "Test Wallet")
4. Click "Add Wallet"
5. The wallet will appear in the "User Wallets" list below

### Step 3: Start Monitoring
1. **Quick Method**: Click "Monitor" button on any wallet in the list
2. **Dropdown Method**: 
   - Select a wallet from the "Select a wallet to monitor" dropdown
   - Click "Start Monitoring"

### Step 4: Watch for Deposits
1. **Get Test ETH**: Visit a Sepolia testnet faucet (e.g., https://sepoliafaucet.com)
2. **Send ETH**: Transfer Sepolia ETH to your monitored wallet address
3. **Watch Live Updates**: 
   - The "Live Updates" section will show real-time events
   - Events include: deposit detected, confirmation updates, deposit completed
   - Each event shows transaction hash, amount, confirmations, and status
4. **Check History**: The "Deposit History" section shows all deposits with full details

## Status Indicators

### API Status
- 🟢 **Healthy**: API is responding normally
- 🟡 **Checking**: Initial connection attempt
- 🔴 **Offline**: Cannot connect to API

### WebSocket Status
- 🟢 **Connected**: Receiving real-time updates
- 🔴 **Disconnected**: Not receiving updates
- 🟡 **Reconnecting**: Attempting to restore connection

### Deposit Status
- 🟡 **Pending**: Waiting for confirmations (< required confirmations)
- 🟢 **Confirmed**: Fully confirmed (≥ required confirmations)
- 🔴 **Orphaned**: Transaction removed due to blockchain reorganization

## WebSocket Events

The UI displays four types of real-time events:

1. **Deposit Detected** (Blue): New transaction found on the blockchain
2. **Confirmation Update** (Orange): Confirmation count increased
3. **Deposit Completed** (Green): Deposit reached required confirmations
4. **Deposit Orphaned** (Red): Transaction removed due to blockchain reorg

## Tips & Best Practices

### Testing Deposits
- Use Sepolia testnet to avoid spending real ETH
- Multiple small deposits are better for testing than one large deposit
- Wait a few seconds between transactions to see distinct events

### Monitoring
- Keep the WebSocket connected for real-time updates
- If disconnected, the UI will automatically attempt to reconnect
- Use "Refresh" button to manually reload deposit history

### Managing Multiple Wallets
- Add descriptive labels to wallets for easy identification
- Monitor one wallet at a time for clearest results
- Stop monitoring before switching to a different wallet

### Updating User Information
- All update fields are optional - update only what you need
- Leave fields empty to keep current values
- Changes take effect immediately

## Keyboard Shortcuts

- **Enter** in search email field: Triggers user search
- **Tab**: Navigate between form fields
- **Escape**: (Future) Close update forms

## Browser Compatibility

This UI works best with modern browsers:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

WebSocket support is required for real-time monitoring.

## Troubleshooting

### "Cannot connect to API"
- Ensure the backend server is running on port 8000
- Check if you can access http://localhost:8000/docs

### "WebSocket connection error"
- Check browser console for detailed error messages
- Ensure CORS is properly configured in the backend
- Verify firewall settings aren't blocking WebSocket connections

### "No deposits showing"
- Confirm the wallet address is correct
- Verify you sent ETH to the monitored address
- Check that transactions are on Sepolia testnet (not mainnet)
- Wait a few blocks for the blockchain monitor to detect the transaction

### Updates not appearing
- Check WebSocket status indicator (should be green "Connected")
- Try stopping and restarting monitoring
- Refresh the page if necessary

## Architecture

The UI is built with:
- **HTML5**: Semantic markup
- **CSS3**: Modern, responsive styling with CSS variables
- **Vanilla JavaScript**: No frameworks - pure ES6+
- **Native WebSocket API**: For real-time updates
- **Fetch API**: For REST API calls

Files:
- `index.html` - Main application structure
- `css/styles.css` - All styling and responsive design
- `js/app.js` - Application logic and API integration

## Development

To modify the UI:

1. Edit the files in the `static/` directory
2. Refresh your browser (no build step needed!)
3. Check browser console for any JavaScript errors

The UI is served directly by FastAPI, so changes are immediately visible.

## API Endpoints Used

The UI interacts with these API endpoints:

- `GET /health` - Health check
- `POST /users/` - Create user
- `GET /users/by-email/{email}` - Search user
- `PUT /users/{user_id}` - Update user
- `POST /wallets/` - Add wallet
- `GET /wallets/user/{user_id}` - Get user wallets
- `GET /deposits/wallet/{wallet_id}` - Get wallet deposits
- `GET /blockchain-networks/` - Get network info
- `WS /ws?wallet_address={address}` - WebSocket connection

Full API documentation: http://localhost:8000/docs

## Contributing

This UI is part of a technical assessment project. Feel free to:
- Report bugs or issues
- Suggest improvements
- Fork and customize for your needs

## License

Part of the Crypto Deposit Monitor project.