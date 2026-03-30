import discord
from discord import app_commands
import os
import asyncio
import random

TOKEN = os.environ.get("DISCORD_TOKEN")
GUILD_ID = int(os.environ.get("GUILD_ID"))

class Bot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        self.tree.clear_commands(guild=None)
        await self.tree.sync()

bot = Bot()

VALORES = {
    "x-c obliterator": {
        "info": "Value 345, Demand 5/10, Hatched 49",
        "imagen": "images/x-c-obliterator.png"
    },
    "x-c robot": {
        "info": "Value 1.3K, Demand 7.5/10, Hatched 5",
        "imagen": None
    },
    "x-c archa": {
        "info": "Value 2K, Demand 9/10, Hatched 2",
        "imagen": None
    },
}

async def pet_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=name.title(), value=name)
        for name in VALORES
        if current.lower() in name.lower()
    ]

@bot.tree.command(name="value", description="Check the value of a pet")
@app_commands.describe(pet="Pet name")
@app_commands.autocomplete(pet=pet_autocomplete)
async def value(interaction: discord.Interaction, pet: str):
    pet_lower = pet.lower()
    if pet_lower in VALORES:
        data = VALORES[pet_lower]
        embed = discord.Embed(
            title=pet.title(),
            description=data["info"],
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("Pet not found ❌")

@bot.tree.command(name="purge", description="Delete messages from the channel")
@app_commands.describe(amount="Number of messages to delete")
@app_commands.checks.has_permissions(manage_messages=True)
async def purge(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"🗑️ {len(deleted)} messages deleted.", ephemeral=True)

@purge.error
async def purge_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You don't have permission to delete messages ❌", ephemeral=True)

@bot.tree.command(name="info", description="Value list information")
async def info(interaction: discord.Interaction):
    message = (
        "**VALUELIST INFO:**\n"
        "-The value list will be updated every 2 days.\n"
        "-Values will be changing according pet demand.\n"
        "-O/C (Owner Choice), thats mean you can choose the value from the pet.\n"
        "-N/A, the pet doesnt exist.\n\n"
        "**CREDITS**\n"
        "Value List Maker:\n"
        "@._.benjaminn\n"
        "Main Credits:\n"
        "@gok984"
    )
    await interaction.response.send_message(message)

@bot.tree.command(name="giveaway", description="Start a giveaway")
@app_commands.describe(
    prize="What are you giving away?",
    duration="Duration in minutes",
    winners="Number of winners (default: 1)"
)
@app_commands.checks.has_permissions(manage_messages=True)
async def giveaway(interaction: discord.Interaction, prize: str, duration: int, winners: int = 1):
    embed = discord.Embed(
        title="🎉 GIVEAWAY 🎉",
        description=f"**Prize:** {prize}\n**Winners:** {winners}\n**Duration:** {duration} minute(s)\n\nReact with 🎉 to enter!",
        color=discord.Color.gold()
    )
    embed.set_footer(text=f"Hosted by {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    await message.add_reaction("🎉")
    await asyncio.sleep(duration * 60)
    message = await interaction.channel.fetch_message(message.id)
    users = [user async for user in message.reactions[0].users() if not user.bot]
    if len(users) == 0:
        await interaction.channel.send("❌ No one entered the giveaway.")
        return
    chosen = random.sample(users, min(winners, len(users)))
    winner_mentions = ", ".join(w.mention for w in chosen)
    result_embed = discord.Embed(
        title="🎉 GIVEAWAY ENDED 🎉",
        description=f"**Prize:** {prize}\n**Winner(s):** {winner_mentions}",
        color=discord.Color.green()
    )
    await message.edit(embed=result_embed)
    await interaction.channel.send(f"Congratulations {winner_mentions}! You won **{prize}**! 🎉")

@bot.tree.command(name="codes", description="Shows the active codes")
async def codes(interaction: discord.Interaction):
    await interaction.response.send_message("**Working Codes:**\nEASTER\nBUNNY")

@bot.event
async def on_ready():
    print(f"Connected as {bot.user}")

bot.run(TOKEN)
