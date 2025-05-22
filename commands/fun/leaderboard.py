import discord
from discord.ext import commands
import math
import datetime
import re

# Assuming user data is stored in bot.user_data as {user_id: {'xp': 0, 'messages': 0}}

# Basic leveling formula (should be consistent with level.py)
def get_level_from_xp(xp):
    return math.floor(0.1 * math.sqrt(xp))

class LeaderboardView(discord.ui.View):
    def __init__(self, sorted_users, ctx, bot, users_per_page=10):
        super().__init__(timeout=180)
        self.sorted_users = sorted_users
        self.ctx = ctx
        self.bot = bot
        self.users_per_page = users_per_page
        self.current_page = 0
        self.update_buttons() # Call initially to set button states

    async def get_leaderboard_embed(self):
        start_index = self.current_page * self.users_per_page
        end_index = start_index + self.users_per_page
        users_on_page = self.sorted_users[start_index:end_index]

        embed = discord.Embed(
            title='Levels Leaderboard',
            description=f'Top members in {self.ctx.guild.name}',
            color=discord.Color.blue()
        )

        for i, (user_id, data) in enumerate(users_on_page):
            user = self.bot.get_user(int(user_id))
            if user:
                level = get_level_from_xp(data['xp'])
                rank = start_index + i + 1
                
                emoji_str = ''
                if rank == 1:
                    emoji_str = '<:Golden:1374768659771428995>'
                elif rank == 2:
                    emoji_str = '<:Silver:1374504846216003596>'
                elif rank == 3:
                    emoji_str = '<:bronz:1374505042144661644>'
                else:
                    emoji_str = '<:Prefix:1373605377609957426>'

                # Create PartialEmoji object from string
                match = re.match(r'<:(.*?):(\d+)>', emoji_str)
                emoji_obj = None
                if match:
                    emoji_name = match.group(1)
                    emoji_id = int(match.group(2))
                    emoji_obj = discord.PartialEmoji(name=emoji_name, id=emoji_id)
                else:
                    # Fallback to the string itself if not a custom emoji format
                    emoji_obj = emoji_str

                print(f"DEBUG: Using emoji string: {emoji_obj}") # Debug print
                print(f"DEBUG: Embed field name string: {emoji_obj} #{rank} {user.display_name}") # Debug print

                embed.add_field(
                    name=f'{emoji_obj} #{rank} {user.display_name}',
                    value=f'Level: {level} | Messages: {data["messages"]}',
                    inline=False
                )
            else:
                # Handle cases where the user is no longer in a shared server
                 # We'll still apply the rank emoji even if the user is left
                 rank = start_index + i + 1
                 emoji_str = ''
                 if rank == 1:
                     emoji_str = '<:Golden:1374768659771428995>'
                 elif rank == 2:
                     emoji_str = '<:Silver:1374504846216003596>'
                 elif rank == 3:
                     emoji_str = '<:bronz:1374505042144661644>'
                 else:
                     emoji_str = '<:Prefix:1373605377609957426>'

                 # Create PartialEmoji object from string
                 match = re.match(r'<:(.*?):(\d+)>', emoji_str)
                 emoji_obj = None
                 if match:
                     emoji_name = match.group(1)
                     emoji_id = int(match.group(2))
                     emoji_obj = discord.PartialEmoji(name=emoji_name, id=emoji_id)
                 else:
                      # Fallback to the string itself if not a custom emoji format
                      emoji_obj = emoji_str

                 print(f"DEBUG: Using emoji string for User Left: {emoji_obj}") # Debug print
                 print(f"DEBUG: Embed field name string for User Left: {emoji_obj} #{start_index + i + 1} User Left") # Debug print

                 embed.add_field(
                    name=f'{emoji_obj} #{start_index + i + 1} User Left',
                    value=f'Level: {get_level_from_xp(data["xp"])} | Messages: {data["messages"]}',
                    inline=False
                )

        # Add footer
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        embed.set_footer(text=f'Requested by {self.ctx.author.display_name} at {now}')

        return embed

    @discord.ui.button(label='Previous Page', style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        embed = await self.get_leaderboard_embed()
        await interaction.response.edit_message(embed=embed, view=self)
        self.update_buttons()

    @discord.ui.button(label='Next Page', style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        embed = await self.get_leaderboard_embed()
        await interaction.response.edit_message(embed=embed, view=self)
        self.update_buttons()

    def update_buttons(self):
        total_pages = math.ceil(len(self.sorted_users) / self.users_per_page)
        self.children[0].disabled = self.current_page == 0
        self.children[1].disabled = self.current_page >= total_pages - 1
        # Ensure the next button is disabled if there's only one page
        if total_pages <= 1:
            self.children[1].disabled = True


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='leaderboard', help='Shows the top members in the server by level and XP.')
    async def leaderboard_command(self, ctx):
        if self.bot.pool is None:
            await ctx.send("Database connection not available.")
            return

        async with self.bot.pool.acquire() as connection:
            # Fetch all user data from the database
            db_users = await connection.fetch('SELECT user_id, xp, messages FROM users')

        if not db_users:
            await ctx.send("No user data available yet. Send some messages to gain XP!")
            return

        # Format fetched data and sort users by level (descending) and then XP (descending)
        # We'll create a list of tuples: (user_id, {'xp': xp, 'messages': messages})
        user_data_list = [(row['user_id'], {'xp': row['xp'], 'messages': row['messages']}) for row in db_users]

        sorted_users = sorted(
            user_data_list,
            key=lambda item: (get_level_from_xp(item[1]['xp']), item[1]['xp']),
            reverse=True
        )

        # Create and send the initial embed with the view
        view = LeaderboardView(sorted_users, ctx, self.bot)
        embed = await view.get_leaderboard_embed()
        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Leaderboard(bot)) 