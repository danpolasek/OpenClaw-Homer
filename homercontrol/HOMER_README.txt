================================================================================
      _    _   ____   __  __  _____  ____  
     | |  | | / __ \ |  \/  || ____||  _ \ 
     | |__| || |  | || |\/| ||  _|  | |_) |
     |  __  || |  | || |  | || |___ |  _ < 
     |_|  |_| \____/ |_|  |_||_____||_| \_\
            
            NUCLEAR PLANT CONTROL CENTER v1.1 - MASTER README
================================================================================

1. [ PŘEHLED SYSTÉMU ]
----------------------
Homer Nuclear Plant Control Center (NPCC) je centrální řídicí rozhraní pro 
digitálního asistenta postaveného na frameworku OpenClaw a Signal-CLI. 
Systém běží v izolovaném prostředí pod uživatelem 'clawbot' a je 
ovládán skrze dashboard 'homercontrol.py'.

2. [ ARCHITEKTURA A SLUŽBY ]
----------------------------
Systém se skládá ze dvou kritických komponent (systemd unitů):

* SLUŽBA: signal-daemon.service
  - Účel: Bridge do sítě Signal.
  - Adresa: 127.0.0.1:8080 (HTTP API)
  - Start: screen -dmS signal-daemon dbus-run-session signal-cli daemon
  - Socket: /home/clawbot/.local/share/signal-cli/socket

* SLUŽBA: openclaw-gateway.service
  - Účel: Exekutivní mozek (LLM DeepSeek), správa agentů a pluginů.
  - Adresa: 127.0.0.1:8123 (Websocket)
  - Start: screen -dmS openclaw-gateway openclaw gateway --force
  - Závislost: Vyžaduje spuštěný signal-daemon.

3. [ SOUBOROVÁ STRUKTURA ]
--------------------------
* /home/clawbot/
  ├── .openclaw/
  │   ├── config.json             <- Globální konfigurace (Modely, Pluginy)
  │   ├── homercontrol.py         <- Tento ovládací dashboard
  │   ├── agents/main/            <- Data agentů (sessions, memory)
  │   └── workspace/              <- Pracovní prostor bota
  ├── .screen/                    <- Privátní adresář pro screen sockety
  └── .npm-global/bin/openclaw    <- Exekutivní binárka OpenClaw

4. [ MANUÁL OVLÁDACÍHO PANELU (Příkaz 'homer') ]
------------------------------------------------
Po zadání aliasu 'homer' v terminálu se otevře dashboard s těmito funkcemi:

  start 1 / 2 : Spuštění příslušného modulu.
  stop 1 / 2  : Bezpečné ukončení modulu (přes screen -X quit).
  c1 / c2     : KONZOLE. Přímý vstup do běžícího procesu (Live log).
                Ukončení náhledu: [Ctrl+A], poté [D] (detach).
  t           : OPENCLAW TUI. Grafické rozhraní pro správu agentů.
  h           : HISTORIE. Rychlý náhled posledních 6 zpráv z komunikace.
  w           : WIPE (HARD RESET). Smaže fyzickou paměť agenta na disku 
                a provede restart Gateway (Modul 2) pro vyčištění RAM.
  q           : EXIT. Ukončení dashboardu.

5. [ TECHNICKÁ KONFIGURACE (SUDOERS) ]
--------------------------------------
Pro správnou funkci 'smart_exec' pod uživatelem 'polasdan' jsou v 
/etc/sudoers nastavena tato pravidla:

polasdan ALL=(clawbot) NOPASSWD: /home/clawbot/.npm-global/bin/openclaw tui
polasdan ALL=(clawbot) NOPASSWD: /usr/bin/screen
polasdan ALL=(ALL) NOPASSWD: /usr/bin/systemctl * signal-daemon.service
polasdan ALL=(ALL) NOPASSWD: /usr/bin/systemctl * openclaw-gateway.service

6. [ SCREEN & PERMISSIONS LOGIKA ]
----------------------------------
Z důvodu bezpečnosti a stability systemd používáme vlastní SCREENDIR.
- Adresář: /home/clawbot/.screen (Práva 700, vlastník clawbot)
- Všechny služby i dashboard musí mít v prostředí nastaveno:
  SCREENDIR=/home/clawbot/.screen
- Tím je zabráněno chybám "Permission denied" v /run/screen.

7. [ ŘEŠENÍ PROBLÉMŮ ]
----------------------
* Problém: Gateway se po startu hned vypne.
  - Diagnostika: Vstup do 'c2' a hledej chybu (např. Port 8123 busy).
* Problém: Bot neodpovídá na zprávy.
  - Diagnostika: Ověř 'start 1' (Signal). Bez něj nemá Gateway kudy mluvit.
* Problém: Dashboard neukazuje [ONLINE] i když služba běží.
  - Diagnostika: Zkus 'sudo systemctl is-active openclaw-gateway.service'.

--------------------------------------------------------------------------------
   NUCLEAR PLANT CONTROL CENTER (c) 2026 - SECTOR 7-G - PREPARED BY GEMINI
================================================================================
