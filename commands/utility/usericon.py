# commands/utility/usericon.py
import discord
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='usericon', help='<:user:1374846273706000434> Displays a user\'s icon.')
    async def usericon(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        # Handle case where user has no avatar
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        
        embed = discord.Embed(
            title=f'<:Multipurpose:1373371000271409416> {member.display_name}\'s Icon',
            color=discord.Color.blue()
        )
        embed.set_image(url=avatar_url)
        await ctx.send(embed=embed)

    @commands.command(name='welcome', help='<:Exclmationmark:1374504177841082379> <:Join:1373605236354056346> Sets the welcome channel.')
    @commands.has_permissions(manage_channels=True)
    async def set_welcome_channel(self, ctx, channel: discord.TextChannel):
        try:
            async with self.bot.pool.acquire() as connection:
                await connection.execute('''
                    INSERT INTO settings (key, server_id, value)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (key, server_id) DO UPDATE SET value = $3
                ''', 'welcome_channel', ctx.guild.id, str(channel.id))
            await ctx.send(f"✅ Welcome channel set to {channel.mention}")
        except Exception as e:
            print(f"Error setting welcome channel: {e}")
            await ctx.send("❌ An error occurred while setting the welcome channel.")

    @commands.command(name='servericon', help='<:Information:1374848638798397442> Displays the server\'s icon.')
    async def servericon(self, ctx):
        if ctx.guild and ctx.guild.icon:
            embed = discord.Embed(title=f"<:Information:1374848638798397442> {ctx.guild.name}'s Icon", color=discord.Color.blue())
            embed.set_image(url=ctx.guild.icon.url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ This server doesn't have an icon.")

    @commands.command(name='serverinfo', help='<:Information:1374848638798397442> Displays information about the server.')
    async def serverinfo(self, ctx):
        if ctx.guild:
            guild = ctx.guild
            embed = discord.Embed(
                title=f"<:Information:1374848638798397442> Server Info: {guild.name}",
                color=discord.Color.blue()
            )
            embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
            embed.add_field(name="<:Clipboard:1373605336820220097> Server ID", value=guild.id, inline=True)
            embed.add_field(name="<:user:1374846273706000434> Owner", value=guild.owner, inline=True)
            embed.add_field(name="<:Golden:1374768659771428995> Creation Date", value=f'`{guild.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")}`', inline=True)
            embed.add_field(name="<:user:1374846273706000434> Members", value=guild.member_count, inline=True)
            embed.add_field(name="<:booster:1374848115907235890> Boost Level", value=guild.premium_tier, inline=True)
            embed.add_field(name="<:booster:1374848115907235890> Boosts", value=guild.premium_subscription_count, inline=True)
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ This command can only be used in a server.")

    @commands.command(name='userinfo', help='<:user:1374846273706000434> Displays information about a user.')
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(
            title=f"<:Briefcase:1374848333956255884> User Info: {member.display_name}",
            color=discord.Color.blue()
        )
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name="<:Clipboard:1373605336820220097> User ID", value=member.id, inline=True)
        embed.add_field(name="<:Golden:1374768659771428995> Created At", value=f'`{member.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")}`', inline=True)
        embed.add_field(name="<:Join:1373605236354056346> Joined At", value=f'`{member.joined_at.strftime("%Y-%m-%d %H:%M:%S UTC")}`', inline=True)
        roles = ', '.join([role.name for role in member.roles[1:]]) if len(member.roles) > 1 else 'None'
        embed.add_field(name="<:role:1374834526005497998> Roles", value=roles, inline=False)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild is None:
            return

        welcome_channel_id = None
        try:
            async with self.bot.pool.acquire() as connection:
                record = await connection.fetchrow(
                    'SELECT value FROM settings WHERE key = $1 AND server_id = $2',
                    'welcome_channel', member.guild.id
                )
                if record:
                    welcome_channel_id = int(record['value'])
        except Exception as e:
            print(f"Error retrieving welcome channel: {e}")
            return

        if welcome_channel_id:
            welcome_channel = self.bot.get_channel(welcome_channel_id)

            if welcome_channel and isinstance(welcome_channel, discord.TextChannel):
                server = member.guild
                member_count = len(server.members)

                embed = discord.Embed(
                    title=f"<:Exclmationmark:1374504177841082379> Welcome to {server.name}!",
                    description=f"<:Join:1373605236354056346> Please welcome {member.mention} to the server!",
                    color=discord.Color.green()
                )
                avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
                embed.set_thumbnail(url=avatar_url)
                embed.add_field(name="<:user:1374846273706000434> Total Members", value=member_count, inline=True)

                try:
                    await welcome_channel.send(embed=embed)
                except discord.Forbidden:
                    print(f"Missing permissions to send messages in welcome channel {welcome_channel.id} on server {server.id}.")
                except Exception as e:
                    print(f"Error sending welcome message: {e}")

async def setup(bot):
    await bot.add_cog(Utility(bot)) 