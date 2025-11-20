import discord
import os
from dotenv import load_dotenv
from pytz import timezone

# Load environment variables from the .env file (like DISCORD_TOKEN)
load_dotenv()

# Get the Discord token from environment variables
TOKEN = os.getenv("DISCORD_TOKEN")

# Set the timezone to Eastern Standard Time (America/New_York)
eastern = timezone("America/New_York")

# Define intents (permissions) for the bot
intents = discord.Intents.default()

# Create a new instance of the bot client
bot = discord.Client(intents=intents)

# Path to the file that stores the streak count
counter_file = "counter.txt"

# Function to read the current streak from the file
def read_streak():
    if not os.path.exists(counter_file):  # If the streak file doesn't exist
        with open(counter_file, "w") as f:  # Create a new streak file and set it to 0
            f.write("0")
        return 0
    with open(counter_file, "r") as f:  # If the file exists, read the current streak value
        return int(f.read().strip())  # Return the streak as an integer

# Function to update the streak in the file
def write_streak(count):
    with open(counter_file, "w") as f:  # Write the new streak count to the file
        f.write(str(count))

# Event triggered when the bot has successfully connected and is ready
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")  # Print the bot's username when logged in

    # Try to find a text channel where the bot can send messages
    channel = None
    for guild in bot.guilds:  # Iterate through all the guilds (servers) the bot is part of
        for text_channel in guild.text_channels:  # Iterate through all text channels in the guild
            if text_channel.permissions_for(guild.me).send_messages:  # Check if the bot can send messages in the channel
                channel = text_channel  # If so, set the channel to the one where the bot can send messages
                break
        if channel:  # If a suitable channel is found, break out of the loop
            break

    if channel is None:  # If no suitable channel was found
        print("❌ No suitable channel found.")  # Print an error message
        await bot.close()  # Close the bot
        return  # Exit the function early

    # Load streak, image, and fact for the day
    day_count = read_streak() + 1  # Increment the streak count for the next day
    write_streak(day_count)  # Update the streak file with the new count

    # Open the "facts.txt" file, read all non-empty lines, and store them in a list
    with open("facts.txt", "r", encoding="utf-8") as f:
        facts = [line.strip() for line in f.readlines() if line.strip()]

    # Get the fact for the current day using modulo to loop through the list if needed
    fact = facts[(day_count - 1) % len(facts)]

    # Load image for the day
    image_dir = "images"  # Path to the directory containing images
    image_files = sorted([file for file in os.listdir(image_dir) if file.lower().endswith(('.jpg', '.png', '.jpeg'))])  # List all image files (jpg, png, jpeg) and sort them

    # Get the image for the current day using modulo to loop through the images if needed
    image_path = os.path.join(image_dir, image_files[(day_count - 1) % len(image_files)])

    # Open the selected image file in binary mode and send it to the Discord channel
    with open(image_path, 'rb') as img:
        file = discord.File(img)  # Create a discord file object for the image
        # Send the image with a message about the Shark Streak and the Shark Fact
        await channel.send(f"📅 **Day {day_count} of the Shark Streak!**\n📸 **Shark of The Day #SOTD** 🦈\n*{fact}*", file=file)

    print(f"✅ Posted to {channel.guild.name} > #{channel.name}. Shutting down.")  # Log the post details
    await bot.close()  # Close the bot once the message is sent

# Run the bot with the token
bot.run(TOKEN)