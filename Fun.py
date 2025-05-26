import discord
from discord import app_commands
from discord.ext import commands
import akinator
import asyncio
import random

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1350005670421860353  # Replace with your server ID
guild = discord.Object(id=GUILD_ID)
tree = bot.tree

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    await tree.sync(guild=guild)
    activity = discord.Activity(type=discord.ActivityType.playing, name="with slash commands")
    await bot.change_presence(activity=activity)
    print(f"Slash commands synced to guild {GUILD_ID}")

@tree.command(name="akinator", description="Play Akinator", guild=guild)
async def akinator_command(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Think of a character. Reply with: yes, no, don't know, probably, probably not. Type 'stop' to quit."
    )
    aki = akinator.Akinator(language='en')
    try:
        question = aki.start_game()
    except Exception as e:
        await interaction.followup.send(f"Error starting game: {e}")
        return
    await interaction.followup.send(question)

    def check(m):
        return (
            m.author == interaction.user
            and m.channel == interaction.channel
            and m.content.lower() in ["yes", "no", "don't know", "probably", "probably not", "stop"]
        )

    while aki.progression <= 80:
        try:
            msg = await bot.wait_for("message", check=check, timeout=60)
        except asyncio.TimeoutError:
            await interaction.followup.send("Timeout. Game ended.")
            return
        if msg.content.lower() == "stop":
            await interaction.followup.send("Game stopped.")
            return
        try:
            question = aki.answer(msg.content.lower())
        except Exception as e:
            await interaction.followup.send(f"Error: {e}")
            return
        await interaction.followup.send(question)
    try:
        aki.win()
    except Exception as e:
        await interaction.followup.send(f"Error finishing game: {e}")
        return
    guess = f"I guess: **{aki.first_guess['name']}** - {aki.first_guess['description']}\nWas I correct? Reply yes or no."
    await interaction.followup.send(guess)
    try:
        final_msg = await bot.wait_for(
            "message",
            check=lambda m: m.author == interaction.user and m.channel == interaction.channel and m.content.lower() in ["yes", "no"],
            timeout=30,
        )
    except asyncio.TimeoutError:
        await interaction.followup.send("Timeout. Game ended.")
        return
    if final_msg.content.lower() == "yes":
        await interaction.followup.send("I guessed it right!")
    else:
        await interaction.followup.send("I'll try better next time.")

@tree.command(name="joke", description="Get a random joke", guild=guild)
async def joke_command(interaction: discord.Interaction):
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything.",
        "Why did the scarecrow win an award? Because he was outstanding in his field.",
        "Why don't programmers like nature? Too many bugs.",
        "I told my computer I needed a break, and now it won’t stop sending me Kit-Kats.",
    ]
    await interaction.response.send_message(random.choice(jokes))

@tree.command(name="dadjoke", description="Get a random dad joke", guild=guild)
async def dadjoke_command(interaction: discord.Interaction):
    dad_jokes = [
        "I'm reading a book on anti-gravity. It's impossible to put down!",
        "Why did the math book look sad? Because it had too many problems.",
        "I would tell you a joke about construction, but I'm still working on it.",
        "Why don't eggs tell jokes? They'd crack each other up.",
    ]
    await interaction.response.send_message(random.choice(dad_jokes))

@tree.command(name="roast", description="Get a random roast", guild=guild)
async def roast_command(interaction: discord.Interaction):
    roasts = [
        "You're as useless as the 'ueue' in 'queue'.",
        "You're the reason the gene pool needs a lifeguard.",
        "If I wanted to kill myself, I'd climb your ego and jump to your IQ.",
        "You're like a cloud. When you disappear, it's a beautiful day.",
    ]
    await interaction.response.send_message(random.choice(roasts))

@tree.command(name="knockknock", description="Get a knock knock joke", guild=guild)
async def knockknock_command(interaction: discord.Interaction):
    jokes = [
        ("Knock knock!", "Who's there?", "Lettuce.", "Lettuce who?", "Lettuce in, it's cold out here!"),
        ("Knock knock!", "Who's there?", "Cow says.", "Cow says who?", "No, a cow says mooooo!"),
        ("Knock knock!", "Who's there?", "Tank.", "Tank who?", "You're welcome!"),
    ]
    joke = random.choice(jokes)
    await interaction.response.send_message(joke[0])
    channel = interaction.channel

    def check(m):
        return m.author == interaction.user and m.channel == channel

    for part in joke[1:]:
        try:
            msg = await bot.wait_for("message", check=check, timeout=30)
        except asyncio.TimeoutError:
            await channel.send("Timeout. Knock knock joke ended.")
            return
        await channel.send(part)

@tree.command(name="8ball", description="Ask the magic 8ball a question", guild=guild)
@app_commands.describe(question="Your question")
async def eight_ball(interaction: discord.Interaction, question: str):
    responses = [
        "It is certain.",
        "Without a doubt.",
        "You may rely on it.",
        "Ask again later.",
        "Cannot predict now.",
        "Don't count on it.",
        "My reply is no.",
        "Very doubtful.",
    ]
    answer = random.choice(responses)
    await interaction.response.send_message(f"Question: {question}\nAnswer: {answer}")

@tree.command(name="coinflip", description="Flip a coin", guild=guild)
async def coinflip_command(interaction: discord.Interaction):
    result = random.choice(["Heads", "Tails"])
    await interaction.response.send_message(f"The coin landed on: {result}")

@tree.command(name="roll", description="Roll a dice", guild=guild)
@app_commands.describe(sides="Number of sides on the dice")
async def roll_command(interaction: discord.Interaction, sides: int = 6):
    if sides < 2:
        await interaction.response.send_message("Dice must have at least 2 sides!")
        return
    result = random.randint(1, sides)
    await interaction.response.send_message(f"You rolled a {result} on a {sides}-sided dice!")

@tree.command(name="grabip", description="Grab someone's IP address", guild=guild)
async def fakeip_command(interaction: discord.Interaction):
    first_octet = random.choice([i for i in range(1, 256) if i not in [10, 127, 169, 172, 192] and not (224 <= i <= 255)])
    other_octets = [str(random.randint(1, 254)) for _ in range(3)]
    fake_ip = f"{first_octet}." + ".".join(other_octets)
    await interaction.response.send_message(f"Looking for IP address: `{fake_ip}`")

@tree.command(name="biblequote", description="Get a random Bible quote", guild=guild)
async def biblequote_command(interaction: discord.Interaction):
    quotes = [
        "For God so loved the world, that he gave his only Son. - John 3:16",
        "I can do all things through Christ who strengthens me. - Philippians 4:13",
        "The Lord is my shepherd; I shall not want. - Psalm 23:1",
        "Trust in the Lord with all your heart. - Proverbs 3:5",
        "Be strong and courageous. - Joshua 1:9",
    ]
    await interaction.response.send_message(random.choice(quotes))

@tree.command(name="rizz", description="Get a rizz line", guild=guild)
async def rizz_command(interaction: discord.Interaction):
    rizz_lines = [
        "Are you a magician? Because whenever I look at you, everyone else disappears.",
        "Do you have a map? I just got lost in your eyes.",
        "Is your name Wi-Fi? Because I'm really feeling a connection.",
        "If you were a vegetable, you'd be a cute-cumber.",
    ]
    await interaction.response.send_message(random.choice(rizz_lines))

@tree.command(name="like", description="Like a user", guild=guild)
@app_commands.describe(user="User to like")
async def like_command(interaction: discord.Interaction, user: discord.Member):
    if user == interaction.user:
        await interaction.response.send_message("You liked yourself, self-love is important!")
    else:
        await interaction.response.send_message(f"{interaction.user.mention} liked {user.mention}!")

@tree.command(name="funfact", description="Get a random fun fact", guild=guild)
async def funfact_command(interaction: discord.Interaction):
    facts = [
        "Bananas are berries, but strawberries aren't.",
        "Honey never spoils and can be eaten thousands of years later.",
        "Octopuses have three hearts.",
        "A day on Venus is longer than a year on Venus.",
        "There are more stars in the universe than grains of sand on Earth.",
        "The Eiffel Tower can be 15 cm taller during the summer.",
    ]
    await interaction.response.send_message(random.choice(facts))


bot.run("")