# wFPS Local Agent

## Overview
The wFPS Local Agent is a Python-based system optimization tool that runs on your PC and communicates with the wFPS web dashboard to provide real-time FPS boosting and system monitoring.

## Features
- **Real-time System Monitoring**: CPU, RAM, and temperature tracking
- **Process Priority Management**: Boost game process priority for better performance
- **RAM Optimization**: Clear standby memory to free up resources
- **Background App Management**: Automatically terminate non-essential processes
- **Game Detection**: Automatically detect running games
- **Remote Control**: Receive optimization commands from the web dashboard

## Requirements
- Python 3.7+
- Windows (for full feature support)
- Administrator privileges (recommended for full functionality)

## Installation

### Step 1: Install Python Dependencies
```bash
pip install psutil requests
```

### Step 2: Get Your Token
1. Sign up/login at the wFPS web dashboard
2. Copy your authentication token from the dashboard

### Step 3: Run the Agent
```bash
python wfps_agent.py
```

When prompted, enter your authentication token.

## Running as Administrator (Windows)

For full optimization features, run the agent with administrator privileges:

1. Open Command Prompt as Administrator
2. Navigate to the agent directory
3. Run: `python wfps_agent.py`

## Usage

### Quick Start
1. Start the agent and enter your token
2. The agent will connect to the wFPS backend
3. Use the web dashboard to:
   - Monitor system performance in real-time
   - Activate Quick Boost for instant optimization
   - Create and apply custom game profiles

### Creating Custom Profiles
1. Go to the web dashboard
2. Click "Create Profile"
3. Configure optimization settings:
   - Set process priority level
   - Add target game processes (e.g., csgo.exe)
   - Enable/disable memory clearing
   - Enable/disable background app termination
   - Add apps to whitelist (apps that won't be killed)

### Applying Profiles
Click "Apply Profile" on any saved profile to activate its optimizations.

## How It Works

### System Monitoring
The agent collects system metrics every 5 seconds:
- CPU usage percentage
- RAM usage and available memory
- System temperature (Windows only)
- Active game processes

### Optimization Actions
When a boost command is received:

1. **Process Priority**: Sets game processes to high priority
2. **Memory Clearing**: Clears standby memory caches
3. **Background Apps**: Terminates resource-heavy apps like:
   - Chrome
   - Discord
   - Spotify
   - Slack

Protected system processes are never terminated.

## Configuration

Edit the agent script to customize:
- `API_URL`: Your wFPS backend URL
- `POLL_INTERVAL`: How often to check for commands (default: 5 seconds)
- Protected processes list
- Common game process names

## Troubleshooting

### Agent Not Connecting
- Check your internet connection
- Verify your authentication token is correct
- Ensure the backend URL is accessible

### Optimizations Not Working
- Run the agent as Administrator
- Check if the target game process names are correct
- Verify the game is actually running

### Temperature Not Showing
Temperature monitoring is Windows-only and may require specific hardware support.

## Safety Notes

⚠️ **Important Safety Information**:
- The agent only terminates non-essential background apps
- System-critical processes are protected and will never be terminated
- Running as Administrator is safe but gives the agent necessary permissions
- Always create backups and close important work before gaming

## API Communication

The agent communicates with the backend via REST API:
- `POST /api/telemetry`: Send system metrics
- `GET /api/boost/commands/pending`: Check for new commands
- `PUT /api/boost/command/{id}/status`: Update command execution status
- `GET /api/profiles/{id}`: Fetch profile settings

## Building an Executable

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller --onefile --name wfps_agent wfps_agent.py
```

The executable will be in the `dist` folder.

## Support

For issues or questions:
- Check the web dashboard for agent connection status
- Review agent console output for error messages
- Ensure you're running the latest version

## License

Part of the wFPS FPS Optimization Suite.
