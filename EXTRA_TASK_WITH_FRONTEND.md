# Web UI - Additional Frontend

Beyond the core technical requirements, this project includes a web interface to demonstrate the system working end-to-end.

## Why It Exists

The assessment asked for a backend system with WebSocket integration. The web UI is just a way to test everything works without needing to write API calls yourself. It's a simple HTML/CSS/JS page that connects to the backend and shows real-time updates.

## What It Does

The interface lets you:

1. **Create Users** - Add users with email, first name, last name
2. **Manage Wallets** - Add Ethereum addresses to users
3. **Monitor Deposits** - Watch real-time deposit updates via WebSocket
4. **View History** - See all deposits with their status and confirmation counts

It's basically a GUI wrapper around most of the REST API and WebSocket functionality.

## How to Use It

### Start the Services

```bash
bash start_local.sh
```

This starts everything (database, API, monitor). Then open `http://localhost:8000`.

### Basic Workflow

1. **Create a User**
   - Enter email (e.g., `test@example.com`)
   - Enter first and last name
   - Click "Create User"

2. **Add a Wallet**
   - Search for your user
   - Enter Ethereum address
   - Pick a network (Sepolia for testing)
   - Optionally add a label
   - Click "Add Wallet"

3. **Monitor Deposits**
   - Select your wallet from the dropdown
   - Click "Start Monitoring"
   - WebSocket connects automatically
   - Send a test transaction and watch it appear in real-time

### Getting Test ETH

To actually see deposits happen, you need test ETH on Sepolia:

- https://sepoliafaucet.com/
- https://www.alchemy.com/faucets/ethereum-sepolia
- https://sepolia-faucet.pk910.de/

Send ETH from another wallet to your monitored address, then watch the UI update.

## What You'll See

When a deposit happens:

1. **Immediate Detection** - Toast notification appears
2. **Pending Status** - Shows 0 confirmations
3. **Live Updates** - Every ~12 seconds, confirmation count increases
4. **Completion** - After 12 confirmations, status changes to "Completed"

The UI shows this all in real-time without page refreshes.

![Web UI Example](imgs/Extra-Front-End%20UI.png)

The interface shows live confirmation updates in real-time as blocks are mined.

## Files

The frontend code lives in `static/`:
- `index.html` - Main page
- `css/style.css` - Styling
- `js/app.js` - WebSocket connection and logic

It's all vanilla HTML/CSS/JS - no frameworks needed. The code is straightforward if you want to customize it.

## Testing the Backend Without the UI

If you want to test the backend without the UI, use Swagger at `http://localhost:8000/docs` or curl/Postman. The web UI is totally optional - the core functionality is in the REST API and WebSocket endpoints.
