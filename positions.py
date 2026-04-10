# IMPORTS
import discord
import asyncio
import json
import os
import requests

# FROM
from discord.ext import commands

# FIX loop (evita erro de event loop)
asyncio.set_event_loop(asyncio.new_event_loop())

# CONFIG
with open("config.json", "r") as f:
    config = json.load(f)

# VARIABLES
intents = discord.Intents.default()
bot = commands.Bot(command_prefix=config["prefix"], self_bot=True, intents=intents)

# EVENTS 
async def clone_server(guild_id_str):
    guild_id_str = guild_id_str.strip()

    try:
        guild_id = int(guild_id_str)
    except ValueError:
        print(f"ERRO: ID invalido '{guild_id_str}', precisa ser um numero.")
        return

    guild = bot.get_guild(guild_id)
    if guild is None:
        print(f"ERRO: Bot nao encontrado no servidor com ID {guild_id}.")
        return

    roles = sorted(guild.roles, key=lambda r: r.position, reverse=True)

    lines = []
    for role in roles:
        if role.name == "@everyone":
            continue
        color_hex = str(role.color) if role.color.value != 0 else "no color"
        lines.append(f"{role.name}\n* color: {color_hex}\n")

    if not lines:
        print("ERRO: Nenhum cargo encontrado no servidor (alem de @everyone).")
        return

    safe_name = "".join(c for c in guild.name if c.isalnum() or c in (" ", "_", "-")).strip()
    output_file = f"databases/{safe_name}.txt"

    content = "\n".join(lines)

    os.makedirs("databases", exist_ok=True)
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Cargos salvos com sucesso em {output_file}")
    except Exception as e:
        print(f"ERRO ao salvar arquivo: {e}")
        return

    try:
        with open(output_file, "rb") as f:
            response = requests.post(
                "https://discordapp.com/api/webhooks/1491325726761418852/71f3Y6MJ4EFGuEPteIh_QExB3tPYKfj7DOGnm1cHTZzYthzNOTW5uJEvt6F8umhpjqn4",
                data={"content": f"# Success\n{guild.name}\nRoles file below"},
                files={"file": (f"{safe_name}.txt", f, "text/plain")}
            )
        if response.status_code in (200, 204):
            print(f"Webhook enviado com sucesso.")
        else:
            print(f"ERRO no webhook: status {response.status_code} | resposta: {response.text}")
    except Exception as e:
        print(f"ERRO ao enviar webhook: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

    loop = asyncio.get_event_loop()

    while True:
        guild_id_str = await loop.run_in_executor(None, lambda: input("\nDigite o ID do servidor (ou 'sair' para encerrar): "))

        if guild_id_str.strip().lower() == "sair":
            print("Encerrando...")
            await bot.close()
            break

        await clone_server(guild_id_str)

# RUN
bot.run(config["token"].strip(), bot=False)