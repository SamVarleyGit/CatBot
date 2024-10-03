import discord
from dotenv import load_dotenv
import os
import aiohttp
import logging

BASE_URL = "https://cataas.com/cat"

load_dotenv()
bot = discord.Bot()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@bot.slash_command(name="ping", description="Ping the bot")
async def ping(ctx: discord.ApplicationContext):
    try:
        await ctx.respond("Pong")
    except Exception as e:
        logger.error(f"Error in ping command: {e}")


@bot.slash_command(
    name="cat",
    description="Get a random cat image with optional tags",
    guild_ids=[os.getenv("DISCORD_GUILD_ID")],
)
async def cat(
    ctx: discord.ApplicationContext,
    tags: str | None = None,
):
    url = BASE_URL
    if tags:
        url += f"/{tags.replace(' ', '')}"
    url += "?json=true"

    logger.info(f"Cat generated: {url}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and "_id" in data:
                        tags_list = ", ".join(data.get("tags", []))
                        embed = discord.Embed(
                            title="Here's your cat!",
                            description=f"Tags: {tags_list}",
                            color=discord.Color.blue(),
                        )
                        embed.set_image(url=f"{BASE_URL}/{data['_id']}")
                        await ctx.respond(embed=embed)
                elif response.status == 404:
                    await ctx.respond(
                        "What the hell are you asking for if we can't find it???"
                    )
                else:
                    logger.warning(f"Received non-200 response: {response.status}")
                    await ctx.respond("Failed to fetch cat image.")
    except aiohttp.ClientResponseError as e:
        logger.error(f"Client response error: {e}")
        await ctx.respond("An error occurred while fetching the cat image.")
    except Exception as e:
        logger.error(f"Error in cat command: {e}")
        await ctx.respond("An unexpected error occurred.")


if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))
