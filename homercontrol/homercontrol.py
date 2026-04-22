import os
import json
import subprocess
import time
import getpass
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.align import Align

# --- INICIALIZACE ---
console = Console()
CURRENT_USER = getpass.getuser()

# --- CESTY A PROSTŘEDÍ ---
CLAW_HOME = Path("/home/clawbot")
OPENCLAW_DIR = CLAW_HOME / ".openclaw"
AGENTS_DIR = OPENCLAW_DIR / "agents/main"
NPM_BIN = "/home/clawbot/.npm-global/bin/openclaw"
SCREEN_DIR = "/home/clawbot/.screen"

# Cesty k binárkám a nastavení screenu
PATH_ENV = "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/clawbot/.npm-global/bin:/home/clawbot/.local/bin"
ENV_VARS = f"TERM=xterm-256color SCREENDIR={SCREEN_DIR} {PATH_ENV}"

class HomerNuclearCenter:
    def __init__(self):
        self.services = {
            "1": {"name": "Signal Daemon", "unit": "signal-daemon.service", "addr": "127.0.0.1:8080 (HTTP)"},
            "2": {"name": "OpenClaw Gateway", "unit": "openclaw-gateway.service", "addr": "127.0.0.1:8123 (WS/API)"}
        }

    def get_status(self, unit):
        try:
            cmd = ["/usr/bin/systemctl", "is-active", unit]
            res = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
            return "[bold green]● ONLINE[/bold green]" if res == "active" else "[bold red]○ OFFLINE[/bold red]"
        except:
            return "[dim white]UNKNOWN[/dim white]"

    def draw_dashboard(self):
        # --- 1. HLAVIČKA (Bílá/Červená) ---
        homer_ascii = (
            "  _    _   ____   __  __  _____  ____  \n"
            " | |  | | / __ \ |  \/  || ____||  _ \ \n"
            " | |__| || |  | || |\/| ||  _|  | |_) |\n"
            " |  __  || |  | || |  | || |___ |  _ < \n"
            " |_|  |_| \____/ |_|  |_||_____||_| \_\\"
        )
        header_text = Text()
        header_text.append(homer_ascii, style="bold white")
        header_text.append("\n" + " " * 12 + "NUCLEAR PLANT CONTROL CENTER v1", style="bold red")
        console.print(Panel(Align.center(header_text), border_style="white", box=box.DOUBLE_EDGE))

        # --- 2. SÍŤOVÉ INFO (IP & Porty) ---
        net_table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE, expand=True)
        net_table.add_column("SLUŽBA", style="white")
        net_table.add_column("ADRESA:PORT", style="bold yellow", justify="right")
        
        for sid, info in self.services.items():
            net_table.add_row(info['name'], info['addr'])
        
        console.print(Panel(net_table, title="[bold white]NETWORK INTERFACES[/bold white]", border_style="cyan"))

        # --- 3. MONITOR SLUŽEB ---
        status_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED, expand=True)
        status_table.add_column("ID", width=4, justify="center")
        status_table.add_column("SYSTÉMOVÝ MODUL", style="cyan")
        status_table.add_column("STATUS", justify="right")
        for sid, info in self.services.items():
            status_table.add_row(sid, info['name'], self.get_status(info['unit']))
        
        console.print(Panel(status_table, title="[bold white]SERVICE MONITOR[/bold white]", border_style="blue"))

        # --- 4. OVLÁDACÍ KONZOLE ---
        cmd_table = Table(show_header=False, box=None, padding=(0, 2))
        cmd_table.add_column("Kód", style="bold green")
        cmd_table.add_column("Popis", style="white")
        
        cmd_table.add_row("start 1/2", "Zapnout vybraný modul")
        cmd_table.add_row("stop 1/2", "Vypnout vybraný modul")
        cmd_table.add_row("c1 / c2", "Vstoupit do konzole (Screen)")
        cmd_table.add_row("t", "Spustit OpenClaw TUI")
        cmd_table.add_row("h", "Poslední komunikace")
        cmd_table.add_row("w", "HARD RESET (Wipe + Restart GW)")
        cmd_table.add_row("q", "Ukončit panel")

        console.print(Panel(cmd_table, title="[bold white]COMMAND CONSOLE[/bold white]", border_style="white"))
        console.print(f"[dim]Uživatel: {CURRENT_USER} | Screen: {SCREEN_DIR}[/dim]", justify="center")

    def manage_service(self, action, sid):
        if sid in self.services:
            unit = self.services[sid]['unit']
            with console.status(f"[bold white]Provádím {action}...[/bold white]"):
                subprocess.run(["sudo", "/usr/bin/systemctl", action, unit], capture_output=True)
                time.sleep(1.5)

    def smart_exec(self, cmd):
        full_cmd = f"{ENV_VARS} {cmd}"
        if CURRENT_USER == "polasdan":
            os.system(f"sudo -u clawbot {full_cmd}")
        else:
            os.system(full_cmd)

    def wipe_memory(self):
        confirm = console.input("\n[bold red]Smazat veškerou paměť a restartovat Gateway? (ano/ne): [/bold red]")
        if confirm.lower() == 'ano':
            os.system(f"rm -rf {AGENTS_DIR}/sessions/* {AGENTS_DIR}/memory/*")
            self.manage_service("restart", "2")
            console.print("[bold green]✔ RESET HOTOV.[/bold green]")
            time.sleep(1)

    def show_history(self):
        session_path = AGENTS_DIR / "sessions"
        try:
            logs = sorted(session_path.glob("*.jsonl"), key=os.path.getmtime, reverse=True)
            if not logs:
                console.print(Panel("[dim]Prázdno.[/dim]", border_style="white"))
            else:
                history_text = Text()
                with open(logs[0], "r") as f:
                    lines = f.readlines()[-6:]
                    for line in lines:
                        data = json.loads(line)
                        if data.get("type") == "message":
                            role = data["message"]["role"].upper()
                            text = data["message"]["content"][0]["text"][:100]
                            color = "blue" if role == "USER" else "green"
                            history_text.append(f"{role}: ", style=f"bold {color}")
                            history_text.append(f"{text}...\n", style="white")
                console.print(Panel(history_text, title="[bold blue]Recent Communication[/bold blue]", border_style="blue"))
        except: pass
        input("\nEnter...")

    def run(self):
        while True:
            console.clear()
            self.draw_dashboard()
            try:
                inp = console.input("\nHomer@Nuclear> ").lower().split()
                if not inp: continue
                cmd = inp[0]
                if cmd == 'q': break
                elif cmd == 'start' and len(inp) > 1: self.manage_service("start", inp[1])
                elif cmd == 'stop' and len(inp) > 1: self.manage_service("stop", inp[1])
                elif cmd == 'c1': self.smart_exec("screen -dr signal-daemon")
                elif cmd == 'c2': self.smart_exec("screen -dr openclaw-gateway")
                elif cmd == 't': self.smart_exec(f"{NPM_BIN} tui")
                elif cmd == 'h': self.show_history()
                elif cmd == 'w': self.wipe_memory()
            except KeyboardInterrupt: break

if __name__ == "__main__":
    HomerNuclearCenter().run()
