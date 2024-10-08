import vertexai
import os
import discord
import traceback
import tiktoken
import logging
import asyncio
from logging.handlers import RotatingFileHandler
from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel,
    Tool,
    grounding,
)

# Set up the Discord client
discord_client = discord.Client(intents=discord.Intents.default())

DISCORD_BOT_TOKEN = "YOUR_DISCORD_API_KEY_HERE"

logger = logging.getLogger('googlebot')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('googlebot.log', maxBytes=10485760, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./auth.json"

vertexai.init(project="YOUR_PROJECT_NAME_HERE", location="us-central1")

model = GenerativeModel(
  model_name="gemini-1.5-pro",
  system_instruction="You are replying to a discord message. The userID, username, and replied_username tags are for logging purposes ONLY. DO NOT INCLUDE THEM IN YOUR REPLY. If there is a message that the user replied to, it will be included in message_user_replied_to.")

# Use Google Search for grounding
tool = Tool.from_google_search_retrieval(grounding.GoogleSearchRetrieval())

def count_tokens(prompt):
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(prompt))

# Event listener for when the bot is ready
@discord_client.event
async def on_ready():
    message = f'Logged in as {discord_client.user.name} (ID: {discord_client.user.id})'
    logger.info(message)
    print(message)

# Event listener for when an error occurs
@discord_client.event
async def on_error(event, *args, **kwargs):
    error = traceback.format_exc()
    logger.error(f'Error occurred in {event}:')
    logger.error(error)

# Event listener for when a message is received
@discord_client.event
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == discord_client.user:
        return

    if not isinstance(message.channel, discord.TextChannel):
        return

    # Check if the bot is mentioned in the message
    if discord_client.user.mentioned_in(message):

        # Remove the bot mention from the message content
        prompt = message.content.replace(f'<@{discord_client.user.id}>', '').strip()

        if not prompt or prompt.isspace():
            await message.reply(f"Please provide a non-empty message.", allowed_mentions=discord.AllowedMentions.none())
            return
        
        # Check if the message is a reply to another message
        if message.reference:
            try:
                replied_message = await message.channel.fetch_message(message.reference.message_id)
                # Add the replied message and username to the prompt
                prompt = f"<userID>{message.author.id}</userID>\n<username>{message.author.name}</username>\n<replied_username>{replied_message.author.name}</replied_username>\n<message_user_replied_to>{replied_message.content}</message_user_replied_to>\n{prompt}"
            except discord.NotFound:
                # Handle the case when the replied message is not found
                prompt = f"Error: Discord couldn't find the replied message.\n<userID>{message.author.id}</userID>\n<username>{message.author.name}</username>\n{prompt}"
        else:
            # Just add user ID and username to the prompt
            prompt = f"<userID>{message.author.id}</userID>\n<username>{message.author.name}</username>\n{prompt}"

        # Check the token length of the prompt
        token_length = count_tokens(prompt)
        logger.info(f"Token length: {token_length}")
        if token_length > 1000:
            await message.reply(f"Sorry, your message is too long.", allowed_mentions=discord.AllowedMentions.none())
            return

        logger.info(f"Prompt: {prompt}")

        # Send initial status message
        status_message = await message.reply("Got message ✅", mention_author=False, allowed_mentions=discord.AllowedMentions.none())

        # Generate a response using the google API
        response = await generate_response(prompt, status_message)
        logger.info(f"Google reply: {response}")

        # Edit the status message with the generated response
        await asyncio.sleep(0.2)
        await status_message.edit(content=response, allowed_mentions=discord.AllowedMentions.none())

async def generate_response(prompt, status_message):
    try:
        # Update status: Sending prompt
        await asyncio.sleep(0.2)
        await status_message.edit(content="Got message ✅ Sending prompt ✅", allowed_mentions=discord.AllowedMentions.none())

        # Send the prompt to the google API
        response = model.generate_content(
            prompt,
            tools=[tool],
            generation_config=GenerationConfig(
                temperature=0.0,
            ),
        )

        # Update status: Got response
        await asyncio.sleep(0.2)
        await status_message.edit(content="Got message ✅ Sending prompt ✅ Got response ✅", allowed_mentions=discord.AllowedMentions.none())

        # Extract the text from the response
        response_text = response.text

        # Update status: Sending message to Discord
        await asyncio.sleep(0.2)
        await status_message.edit(content="Got message ✅ Sending prompt ✅ Got response ✅ Sending message to Discord ✅", allowed_mentions=discord.AllowedMentions.none())

        # Return the extracted text
        return response_text
    except Exception as e:
        error_message = str(e)
        return f"Error: {error_message}"

def main():
    try:
        # Start the Discord client
        discord_client.run(DISCORD_BOT_TOKEN)
    except discord.errors.LoginFailure as e:
        logger.error(f'Login failed. Please check your bot token. Error: {e}')
    except Exception as e:
        logger.error(f'An error occurred: {e}')

if __name__ == "__main__":
    main()