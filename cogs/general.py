'''
The `General` cog for IgKnite.
---

License can be found here:
https://github.com/IgKniteDev/IgKnite/blob/main/LICENSE
'''


# Imports.
import time
from datetime import datetime

import core
import disnake
from core.embeds import TypicalEmbed
from disnake import Option, OptionType
from disnake.ext import commands


# Backend for ping-labelled commands.
# Do not use it within other commands unless really necessary.
async def _ping_backend(inter: disnake.CommandInteraction) -> TypicalEmbed:
    system_latency = round(inter.bot.latency * 1000)

    start_time = time.time()
    await inter.response.defer()
    end_time = time.time()

    api_latency = round((end_time - start_time) * 1000)

    uptime = round(datetime.timestamp(datetime.now())) - core.running_since
    h, m, s = uptime // 3600, uptime % 3600 // 60, uptime % 3600 % 60

    embed = (
        core.TypicalEmbed(inter=inter, disabled_footer=True)
        .add_field(
            name='System Latency',
            value=f'{system_latency}ms [{inter.bot.shard_count} shard(s)]',
            inline=False,
        )
        .add_field(name='API Latency', value=f'{api_latency}ms', inline=False)
        .add_field(name='Uptime', value=f'{h}h {m}m {s}s')
        .add_field(name='Patch Version', value=core.BOT_METADATA['VERSION'], inline=False)
    )

    return embed


# View for the `ping` command.
class PingCommandView(disnake.ui.View):
    def __init__(self, inter: disnake.CommandInteraction, timeout: float = 60) -> None:
        super().__init__(timeout=timeout)
        self.inter = inter

    @disnake.ui.button(label='Refresh', style=disnake.ButtonStyle.gray)
    async def _refresh(self, _: disnake.ui.Button, inter: disnake.Interaction) -> None:
        embed = await _ping_backend(inter)
        await inter.edit_original_message(embed=embed, view=self)

    async def on_timeout(self) -> None:
        for children in self.children:
            children.disabled = True

        await self.inter.edit_original_message(view=self)


# The actual cog.
class General(commands.Cog):
    def __init__(self, bot: core.IgKnite) -> None:
        self.bot = bot

    # ping
    @commands.slash_command(name='ping', description='Shows my current response time.')
    async def _ping(self, inter: disnake.CommandInteraction) -> None:
        embed = await _ping_backend(inter)
        await inter.send(embed=embed, view=PingCommandView(inter=inter))


# The setup() function for the cog.
def setup(bot: core.IgKnite) -> None:
    bot.add_cog(General(bot))
