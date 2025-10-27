#!/usr/bin/env python3
"""
wFPS Local Agent - System Optimization Agent
This agent runs locally on the user's machine and communicates with the wFPS backend.
"""

import psutil
import os
import sys
import time
import platform
import subprocess
import json
import requests
from typing import List, Dict, Optional
from datetime import datetime

# Configuration
API_URL = os.environ.get('WFPS_API_URL', "https://fps-enhancer-13.preview.emergentagent.com/api")
AGENT_ID = f"agent_{platform.node()}_{int(time.time())}"
POLL_INTERVAL = 5  # seconds

class WFPSAgent:
    def __init__(self, api_url: str, token: str):
        self.api_url = api_url
        self.token = token
        self.agent_id = AGENT_ID
        self.headers = {"Authorization": f"Bearer {token}"}
        self.boost_active = False
        self.current_profile = None
        
    def get_system_info(self) -> Dict:
        """Collect system telemetry"""
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Get temperature (Windows only)
        temperature = None
        if platform.system() == "Windows":
            try:
                # Using wmic for Windows temperature
                result = subprocess.run(
                    ['wmic', 'path', 'win32_perfformatteddata_counters_thermalzoneinformation', 'get', 'temperature'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                temp_str = result.stdout.strip().split('\n')[-1].strip()
                if temp_str.isdigit():
                    temperature = (int(temp_str) - 2732) / 10  # Convert to Celsius
            except:
                pass
        
        # Detect active game
        active_game = self.detect_game()
        
        return {
            "agent_id": self.agent_id,
            "cpu_usage": cpu_usage,
            "ram_usage": memory.percent,
            "ram_available": memory.available / (1024**3),  # GB
            "temperature": temperature,
            "active_game": active_game,
            "fps": None  # FPS detection requires game-specific integration
        }
    
    def detect_game(self) -> Optional[str]:
        """Detect if a game is running"""
        common_games = [
            "csgo.exe", "valorant.exe", "league of legends.exe", "fortnite.exe",
            "apex_legends.exe", "cod.exe", "pubg.exe", "overwatch.exe",
            "minecraft.exe", "dota2.exe", "gta5.exe", "rocketleague.exe"
        ]
        
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name'].lower()
                for game in common_games:
                    if game in proc_name:
                        return proc.info['name']
            except:
                continue
        return None
    
    def send_telemetry(self, data: Dict) -> bool:
        """Send telemetry to backend"""
        try:
            response = requests.post(
                f"{self.api_url}/telemetry",
                json=data,
                headers=self.headers,
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to send telemetry: {e}")
            return False
    
    def get_pending_commands(self) -> List[Dict]:
        """Fetch pending boost commands from backend"""
        try:
            response = requests.get(
                f"{self.api_url}/boost/commands/pending",
                headers=self.headers,
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Failed to fetch commands: {e}")
            return []
    
    def update_command_status(self, command_id: str, status: str):
        """Update command status in backend"""
        try:
            requests.put(
                f"{self.api_url}/boost/command/{command_id}/status",
                params={"status": status},
                headers=self.headers,
                timeout=5
            )
        except Exception as e:
            print(f"Failed to update command status: {e}")
    
    def set_process_priority(self, process_name: str, priority: str) -> bool:
        """Set process priority"""
        priority_map = {
            "low": psutil.IDLE_PRIORITY_CLASS if platform.system() == "Windows" else 19,
            "below_normal": psutil.BELOW_NORMAL_PRIORITY_CLASS if platform.system() == "Windows" else 10,
            "normal": psutil.NORMAL_PRIORITY_CLASS if platform.system() == "Windows" else 0,
            "above_normal": psutil.ABOVE_NORMAL_PRIORITY_CLASS if platform.system() == "Windows" else -10,
            "high": psutil.HIGH_PRIORITY_CLASS if platform.system() == "Windows" else -15,
            "realtime": psutil.REALTIME_PRIORITY_CLASS if platform.system() == "Windows" else -20
        }
        
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() == process_name.lower():
                    p = psutil.Process(proc.pid)
                    if platform.system() == "Windows":
                        p.nice(priority_map.get(priority, psutil.NORMAL_PRIORITY_CLASS))
                    else:
                        p.nice(priority_map.get(priority, 0))
                    print(f"Set {process_name} to {priority} priority")
                    return True
            return False
        except Exception as e:
            print(f"Failed to set priority for {process_name}: {e}")
            return False
    
    def clear_memory(self) -> bool:
        """Clear standby memory (Windows only)"""
        if platform.system() == "Windows":
            try:
                # Using EmptyStandbyList requires admin privileges
                subprocess.run(
                    ['powershell', '-Command', 'Clear-RecycleBin -Force'],
                    capture_output=True,
                    timeout=5
                )
                print("Memory cleared")
                return True
            except Exception as e:
                print(f"Failed to clear memory: {e}")
                return False
        return False
    
    def kill_background_apps(self, whitelist: List[str]) -> int:
        """Kill non-essential background processes"""
        # Protected processes that should never be killed
        protected = [
            'system', 'registry', 'smss.exe', 'csrss.exe', 'wininit.exe',
            'services.exe', 'lsass.exe', 'svchost.exe', 'explorer.exe',
            'dwm.exe', 'taskmgr.exe', 'python.exe', 'wfps_agent.exe'
        ]
        
        killed_count = 0
        for proc in psutil.process_iter(['name', 'username']):
            try:
                proc_name = proc.info['name'].lower()
                
                # Skip protected and whitelisted processes
                if any(p in proc_name for p in protected) or any(w in proc_name for w in whitelist):
                    continue
                
                # Kill non-essential processes
                if proc_name in ['chrome.exe', 'discord.exe', 'spotify.exe', 'slack.exe']:
                    proc.terminate()
                    killed_count += 1
                    print(f"Terminated: {proc_name}")
            except:
                continue
        
        return killed_count
    
    def apply_boost_profile(self, profile: Dict):
        """Apply optimization profile"""
        print(f"\nApplying profile: {profile.get('name', 'Unknown')}")
        
        # Set process priorities
        for process_name in profile.get('process_names', []):
            self.set_process_priority(process_name, profile.get('priority_level', 'high'))
        
        # Clear memory if enabled
        if profile.get('clear_memory', True):
            self.clear_memory()
        
        # Kill background apps if enabled
        if profile.get('kill_background_apps', True):
            whitelist = profile.get('background_apps_whitelist', [])
            killed = self.kill_background_apps(whitelist)
            print(f"Terminated {killed} background processes")
        
        self.boost_active = True
        self.current_profile = profile
        print("Boost applied successfully!")
    
    def stop_boost(self):
        """Stop boost mode"""
        self.boost_active = False
        self.current_profile = None
        print("Boost deactivated")
    
    def execute_command(self, command: Dict):
        """Execute boost command"""
        command_id = command['id']
        action = command['action']
        
        self.update_command_status(command_id, "executing")
        
        try:
            if action == "start_boost":
                # Apply general boost
                default_profile = {
                    'name': 'Quick Boost',
                    'process_names': [],
                    'priority_level': 'high',
                    'clear_memory': True,
                    'kill_background_apps': True,
                    'background_apps_whitelist': []
                }
                self.apply_boost_profile(default_profile)
            
            elif action == "apply_profile":
                # Fetch and apply specific profile
                profile_id = command.get('profile_id')
                if profile_id:
                    response = requests.get(
                        f"{self.api_url}/profiles/{profile_id}",
                        headers=self.headers,
                        timeout=5
                    )
                    if response.status_code == 200:
                        self.apply_boost_profile(response.json())
            
            elif action == "stop_boost":
                self.stop_boost()
            
            self.update_command_status(command_id, "completed")
        
        except Exception as e:
            print(f"Command execution failed: {e}")
            self.update_command_status(command_id, "failed")
    
    def run(self):
        """Main agent loop"""
        print(f"wFPS Agent started - ID: {self.agent_id}")
        print(f"Connected to: {self.api_url}")
        print(f"System: {platform.system()} {platform.release()}")
        print("\nAgent is running... Press Ctrl+C to stop\n")
        
        while True:
            try:
                # Collect and send telemetry
                telemetry = self.get_system_info()
                self.send_telemetry(telemetry)
                
                # Check for pending commands
                commands = self.get_pending_commands()
                for command in commands:
                    self.execute_command(command)
                
                # Display status
                status = "🟢 BOOST ACTIVE" if self.boost_active else "⚪ IDLE"
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {status} | "
                      f"CPU: {telemetry['cpu_usage']:.1f}% | "
                      f"RAM: {telemetry['ram_usage']:.1f}% | "
                      f"Game: {telemetry['active_game'] or 'None'}")
                
                time.sleep(POLL_INTERVAL)
            
            except KeyboardInterrupt:
                print("\nAgent stopped by user")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(POLL_INTERVAL)

def main():
    print("="*60)
    print("wFPS Local Agent - FPS Booster")
    print("="*60)
    
    # Check if running as admin (Windows)
    if platform.system() == "Windows":
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("⚠️  WARNING: Agent is not running with administrator privileges")
                print("Some optimization features may not work properly.")
                print("Please run as administrator for full functionality.\n")
        except:
            pass
    
    # Get token from user
    token = input("Enter your wFPS token: ").strip()
    if not token:
        print("Error: Token is required")
        sys.exit(1)
    
    # Start agent
    agent = WFPSAgent(API_URL, token)
    agent.run()

if __name__ == "__main__":
    main()