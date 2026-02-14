"""野球ファンハートエージェント。ファンの熱意を心で表現"""

import discord
from db import AgentDatabase

class BaseballFanHeartAgent(discord.Client):
    """野球ファンハートエージェント。ファンの熱意を心で表現"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = AgentDatabase(f"baseball-fan-heart-agent.db")

    async def on_ready(self):
        print(f"{self.user} is ready!")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith("!"):
            await self.handle_command(message)

    async def handle_command(self, message):
        command = message.content[1:].split()[0]

        if command == "help":
            await self.show_help(message)
        elif command == "status":
            await self.show_status(message)
        elif command == "list":
            await self.list_items(message)
        else:
            await message.channel.send(f"Unknown command: {command}")

    async def show_help(self, message):
        help_text = f"""
        baseball-fan-heart-agent - 野球ファンハートエージェント。ファンの熱意を心で表現

        Commands:
        !help - Show this help
        !status - Show status
        !list - List items
        """
        await message.channel.send(help_text)

    async def show_status(self, message):
        status = self.db.get_status()
        await message.channel.send(f"Status: {status}")

    async def list_items(self, message):
        items = self.db.list_items()
        await message.channel.send(f"Items: {items}")
