import discord
from discord.ext import commands
from discord.ui import Select, View
import json
import aiofiles
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configurations
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='+', intents=intents)

categories = {
    "Refund Item": 1272169803557240833,
    "Report Player": 1272170004447760455,
    "Faction Report": 1272170095682261032,
    "Gang Request": 1272170246492655708,
    "Ped Request": 1272170330995298366,
    "3D Request": 1272170396749398037,
    "Police Departement": 1272170686571479111,
    "Management": 1274761639140261949,
    "Question": 1274762825864314890,
    "Owner": 1276876273532010599,
    "Manage": 1276876382911074418
}

roles_for_tickets = {
    "Refund Item": [1186222063925612584, 1186222322647048192, 1186222388258558014, 1271744567393386540, 1186222128601780405],
    "Report Player": [1186222063925612584, 1186222322647048192, 1186222388258558014, 1271744567393386540, 1186222128601780405],
    "Faction Report": [1186222063925612584, 1186222322647048192, 1186222388258558014, 1271744567393386540, 1186222128601780405],
    "Gang Request": [1186222063925612584, 1186222322647048192, 1186222388258558014, 1271744567393386540, 1186222128601780405],
    "Ped Request": [1186222063925612584, 1186222322647048192, 1186222388258558014, 1271744567393386540, 1186222128601780405],
    "3D Request": [1274770007651422336, 1274770015671809410, 1274770025691393025, 1274770034672345477, 1274770045622464001],
    "Police Departement": [1186222063925612584, 1186222322647048192, 1186222388258558014, 1271744567393386540, 1186222128601780405],
    "Management": [1186222063925612584],
    "Question": [1186222063925612584, 1186222322647048192, 1186222388258558014, 1271744567393386540, 1186222128601780405],
    "Owner": [1186222063925612584],  # Example roles for owner
    "Manage": [1186222063925612584, 1186222322647048192]  # Example roles for manage
}

ticket_categories = [1272169803557240833, 1272170004447760455, 1272170095682261032, 1272170246492655708, 1272170330995298366, 1272170396749398037, 1272170686571479111, 1274761639140261949, 1274762825864314890]
channel_id = 1186031537209221250
ticket_data_file = 'ticket_data.json'

# Async file operations
async def save_ticket_data(data):
    async with aiofiles.open(ticket_data_file, 'w') as file:
        await file.write(json.dumps(data, indent=4))

async def load_ticket_data():
    try:
        async with aiofiles.open(ticket_data_file, 'r') as file:
            content = await file.read()
            return json.loads(content)
    except FileNotFoundError:
        return {}

class TicketDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=name, description=f"Create a {name} ticket")
            for name in categories if name not in ["Owner", "Manage"]
        ]
        super().__init__(placeholder="Select the type of ticket...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_category = self.values[0]
        await create_ticket(interaction, selected_category)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())

class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        close_button = discord.ui.Button(label="Close", style=discord.ButtonStyle.red)
        close_button.callback = self.close_ticket
        self.add_item(close_button)

    async def close_ticket(self, interaction: discord.Interaction):
        confirm_view = ConfirmCloseTicketView()
        embed = discord.Embed(title="Are you sure?", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, view=confirm_view)

class ConfirmCloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        yes_button = discord.ui.Button(label="Yes", style=discord.ButtonStyle.green)
        yes_button.callback = self.confirm_close
        self.add_item(yes_button)

        no_button = discord.ui.Button(label="No", style=discord.ButtonStyle.red)
        no_button.callback = self.cancel_close
        self.add_item(no_button)



class ConfirmCloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        yes_button = discord.ui.Button(label="Yes", style=discord.ButtonStyle.green)
        yes_button.callback = self.confirm_close
        self.add_item(yes_button)

        no_button = discord.ui.Button(label="No", style=discord.ButtonStyle.red)
        no_button.callback = self.cancel_close
        self.add_item(no_button)

    async def confirm_close(self, interaction: discord.Interaction):
        # شناسه کانال بک‌آپ
        backup_channel_id = 1272175121565618256  # تغییر به آیدی کانال بک‌آپ شما

        # دریافت کانال بک‌آپ
        backup_channel = bot.get_channel(backup_channel_id)
        if not backup_channel:
            await interaction.response.send_message("Backup channel not found!", ephemeral=True)
            return

        # دریافت کانال تیکت
        channel = interaction.channel

        try:
            # بک‌آپ‌گیری از پیام‌های کانال
            embed = discord.Embed(title=f"Backup of channel: {channel.name}", color=discord.Color.blue())
            async for message in channel.history(limit=None, oldest_first=True):
                embed.add_field(
                    name=f"Message from {message.author}",
                    value=f"{message.content}\n\n**Attachments:** {', '.join([attachment.url for attachment in message.attachments])}",
                    inline=False
                )
                # ارسال پیام‌ها به کانال بک‌آپ
                if len(embed.fields) > 20:  # برای جلوگیری از رسیدن به محدودیت‌ها
                    await backup_channel.send(embed=embed)
                    embed = discord.Embed(title=f"Backup of channel: {channel.name}", color=discord.Color.blue())
            if embed.fields:
                await backup_channel.send(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Failed to backup messages: {e}", ephemeral=True)
            return

        # حذف کانال بعد از بک‌آپ‌گیری
        await channel.delete()

    async def cancel_close(self, interaction: discord.Interaction):
        await interaction.message.delete()


    async def confirm_close(self, interaction: discord.Interaction):
        # کدهای لازم برای بستن تیکت و لاگ‌کردن یا هر عملیات دیگری را اینجا قرار دهید
        await interaction.channel.delete()  # این خط برای بستن چنل است

    async def cancel_close(self, interaction: discord.Interaction):
        await interaction.message.delete()
class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())

class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        close_button = discord.ui.Button(label="Close", style=discord.ButtonStyle.red)
        close_button.callback = self.close_ticket
        self.add_item(close_button)

    async def close_ticket(self, interaction: discord.Interaction):
        confirm_view = ConfirmCloseTicketView()
        embed = discord.Embed(title="Are you sure?", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, view=confirm_view)

class ConfirmCloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        yes_button = discord.ui.Button(label="Yes", style=discord.ButtonStyle.green)
        yes_button.callback = self.confirm_close
        self.add_item(yes_button)

        no_button = discord.ui.Button(label="No", style=discord.ButtonStyle.red)
        no_button.callback = self.cancel_close
        self.add_item(no_button)

class ConfirmCloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        yes_button = discord.ui.Button(label="Yes", style=discord.ButtonStyle.green)
        yes_button.callback = self.confirm_close
        self.add_item(yes_button)

        no_button = discord.ui.Button(label="No", style=discord.ButtonStyle.red)
        no_button.callback = self.cancel_close
        self.add_item(no_button)


    async def confirm_close(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        ticket_data = await load_ticket_data()

        # ذخیره اطلاعات برای حذف در لیست‌های موقت
        keys_to_delete = []
        for user, tickets in ticket_data.items():
            for ticket_type, channel_id_str in list(tickets.items()):
                if int(channel_id_str) == interaction.channel.id:
                    del tickets[ticket_type]
                    if not tickets:
                        keys_to_delete.append(user)
                    break

        # حذف کلیدهای مشخص شده از دیکشنری
        for key in keys_to_delete:
            del ticket_data[key]

        await save_ticket_data(ticket_data)

        # حذف چنل
        await interaction.channel.delete()

    async def cancel_close(self, interaction: discord.Interaction):
        await interaction.message.delete()



@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

    channel = bot.get_channel(channel_id)
    if channel:
        async for msg in channel.history(limit=100):
            if msg.embeds:
                if msg.embeds[0].title == "Select Ticket Type":
                    print("Ticket embed already exists.")
                    return

        embed = discord.Embed(title="Select Ticket Type", description="Choose a category below to create a ticket.", color=discord.Color.dark_gray())
        view = TicketView()
        await channel.send(embed=embed, view=view)
    else:
        print(f"Channel with ID {channel_id} not found.")

    ticket_data = await load_ticket_data()
    for user_id, user_tickets in ticket_data.items():
        for ticket_type, channel_id_str in user_tickets.items():
            channel = bot.get_channel(int(channel_id_str))
            if channel:
                embed = discord.Embed(title="Close Ticket", description="Click the button below to close the ticket.", color=discord.Color.yellow())
                view = CloseTicketView()
                await channel.send(embed=embed, view=view)

async def create_ticket(interaction: discord.Interaction, ticket_type: str):
    user_id = str(interaction.user.id)
    ticket_data = await load_ticket_data()
    user_tickets = ticket_data.get(user_id, {})

    if ticket_type in user_tickets:
        await interaction.response.send_message("You already have an open ticket of this type!", ephemeral=True)
        return

    guild = interaction.guild
    category_id = categories[ticket_type]
    category = guild.get_channel(category_id)

    if category is None:
        await interaction.response.send_message(f"Category with ID {category_id} not found!", ephemeral=True)
        return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    for role_id in roles_for_tickets.get(ticket_type, []):
        role = guild.get_role(role_id)
        if role is None:
            continue
        overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    ticket_channel = await category.create_text_channel(f"{ticket_type}-{interaction.user.name}", overwrites=overwrites)
    user_tickets[ticket_type] = str(ticket_channel.id)
    ticket_data[user_id] = user_tickets
    await save_ticket_data(ticket_data)

    embed = discord.Embed(title="Ticket Created", description="Use the button below to close the ticket when done.", color=discord.Color.green())
    view = CloseTicketView()
    await ticket_channel.send(embed=embed, view=view)

    await interaction.response.send_message(f"{ticket_type} ticket created: {ticket_channel.mention}", ephemeral=True)

@bot.command()
@commands.has_any_role("━━ ≀ Owner", "━━ ≀ Management", "━━ ≀ Administrator")
async def p(ctx, target: str):
    ticket_data = await load_ticket_data()
    user_id = str(ctx.author.id)
    user_tickets = ticket_data.get(user_id, {})

    if not user_tickets:
        await ctx.send("You don't have any open tickets!")
        return

    ticket_channel_id = None
    for ticket_type, channel_id_str in user_tickets.items():
        ticket_channel_id = int(channel_id_str)
        break

    if ticket_channel_id is None:
        await ctx.send("Unable to find your open ticket!")
        return

    ticket_channel = bot.get_channel(ticket_channel_id)

    if target == "owner":
        category_id = 1276876273532010599  # Owner category ID
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
    elif target == "manage":
        category_id = 1276876273532010599  # Manage category ID
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            ctx.guild.get_role(1186222063925612584): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
    elif target == "admin":
        category_id = 1277029706998349877  # Admin category ID
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            ctx.guild.get_role(1186222322647048192): discord.PermissionOverwrite(read_messages=True, send_messages=True),
            ctx.guild.get_role(1186222322647048192): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
    else:
        await ctx.send("Invalid command! Use either +p owner, +p manage, or +p admin.")
        return

    category = bot.get_channel(category_id)
    if category is None:
        await ctx.send(f"Category with ID {category_id} not found!")
        return

    await ticket_channel.edit(category=category, overwrites=overwrites)
    await ctx.send(f"Ticket moved to {category.name} and permissions updated!")

@bot.command()
@commands.has_any_role("━━ ≀ Owner", "━━ ≀ Management", "━━ ≀ Administrator", "━━ ≀ Controller")
async def adduser(ctx, member: discord.Member):
    if ctx.channel.category_id not in ticket_categories:
        await ctx.send("This command can only be used in a ticket channel.")
        return

    await ctx.channel.set_permissions(member, read_messages=True, send_messages=True)
    await ctx.send(f"{member.mention} has been added to the ticket.")

@bot.command()
@commands.has_any_role("━━ ≀ Owner", "━━ ≀ Management", "━━ ≀ Administrator", "━━ ≀ Controller")
async def reuser(ctx, member: discord.Member):
    if ctx.channel.category_id not in ticket_categories:
        await ctx.send("This command can only be used in a ticket channel.")
        return

    await ctx.channel.set_permissions(member, overwrite=None)
    await ctx.send(f"{member.mention} has been removed from the ticket.")

bot.run(os.getenv('DISCORD_TOKEN'))
