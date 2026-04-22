#!/bin/bash
# Přidá všechny změny
git add .
# Vytvoří verzi s časovým razítkem
git commit -m "Automatická aktualizace $(date +'%Y-%m-%d %H:%M')"
# Odešle na GitHub
git push origin main
