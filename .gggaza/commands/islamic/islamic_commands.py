import json
import random
import discord
from discord.ext import commands
from discord import app_commands, Interaction

# List of duas
DUAS = [
  {
    "id": 1,
    "arabic": "رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً وَفِي الآخِرَةِ حَسَنَةً وَقِنَا عَذَابَ النَّارِ",
    "translation": "Our Lord! Give us in this world good and in the Hereafter good, and protect us from the punishment of the Fire.",
    "count": 1
  },
  {
    "id": 2,
    "arabic": "رَبِّ اغْفِرْ لِي وَلِوَالِدَيَّ",
    "translation": "My Lord, forgive me and my parents.",
    "count": 1
  },
  {
    "id": 3,
    "arabic": "اللَّهُمَّ إِنِّي أَسْأَلُكَ الْعَفْوَ وَالْعَافِيَةَ",
    "translation": "O Allah, I ask You for forgiveness and well-being.",
    "count": 1
  },
  {
    "id": 4,
    "arabic": "اللَّهُمَّ اهْدِنِي وَسَدِّدْنِي",
    "translation": "O Allah, guide me and keep me steadfast.",
    "count": 1
  },
  {
    "id": 5,
    "arabic": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْهَمِّ وَالْحَزَنِ",
    "translation": "O Allah, I seek refuge in You from worry and sadness.",
    "count": 1
  },
  {
    "id": 6,
    "arabic": "اللَّهُمَّ اجْعَلْنِي مِنَ التَّوَّابِينَ وَمِنَ الْمُتَطَهِّرِينَ",
    "translation": "O Allah, make me among those who repent often and purify themselves.",
    "count": 1
  },
  {
    "id": 7,
    "arabic": "اللَّهُمَّ إِنِّي أَسْأَلُكَ الْجَنَّةَ وَأَعُوذُ بِكَ مِنَ النَّارِ",
    "translation": "O Allah, I ask You for Paradise and seek refuge from Hellfire.",
    "count": 1
  },
  {
    "id": 8,
    "arabic": "اللَّهُمَّ ارْزُقْنِي حُبَّكَ وَحُبَّ مَنْ يُحِبُّكَ",
    "translation": "O Allah, grant me Your love and the love of those who love You.",
    "count": 1
  },
  {
    "id": 9,
    "arabic": "رَبِّ زِدْنِي عِلْمًا",
    "translation": "My Lord, increase me in knowledge.",
    "count": 1
  },
  {
    "id": 10,
    "arabic": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْكُفْرِ وَالْفَقْرِ",
    "translation": "O Allah, I seek refuge in You from disbelief and poverty.",
    "count": 1
  },
  {
    "id": 11,
    "arabic": "اللَّهُمَّ بَارِكْ لَنَا فِيمَا رَزَقْتَنَا",
    "translation": "O Allah, bless what You have provided us.",
    "count": 1
  },
  {
    "id": 12,
    "arabic": "اللَّهُمَّ اغْفِرْ لِي، وَارْحَمْنِي، وَاهْدِنِي، وَعَافِنِي، وَارْزُقْنِي",
    "translation": "O Allah, forgive me, have mercy on me, guide me, protect me, and provide for me.",
    "count": 1
  },
  {
    "id": 13,
    "arabic": "رَبَّنَا تَقَبَّلْ مِنَّا إِنَّكَ أَنتَ السَّمِيعُ الْعَلِيمُ",
    "translation": "Our Lord! Accept from us. You are the All-Hearing, All-Knowing.",
    "count": 1
  },
  {
    "id": 14,
    "arabic": "رَبِّ اجْعَلْنِي مُقِيمَ الصَّلَاةِ وَمِن ذُرِّيَّتِي",
    "translation": "My Lord, make me one who establishes prayer, and from my descendants.",
    "count": 1
  },
  {
    "id": 15,
    "arabic": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنْ غَلَبَةِ الدَّيْنِ وَقَهْرِ الرِّجَالِ",
    "translation": "O Allah, I seek refuge in You from debt and oppression of people.",
    "count": 1
  },
  {
    "id": 16,
    "arabic": "اللَّهُمَّ اجْعَلْ خَيْرَ عُمُرِي آخِرَهُ",
    "translation": "O Allah, make the best of my life the end of it.",
    "count": 1
  },
  {
    "id": 17,
    "arabic": "اللَّهُمَّ اجْعَلْ خَيْرَ أَعْمَالِي خَوَاتِيمَهَا",
    "translation": "O Allah, make the best of my deeds the last of them.",
    "count": 1
  },
  {
    "id": 18,
    "arabic": "اللَّهُمَّ اجْعَلْ خَيْرَ أَيَّامِي يَوْمَ أَلْقَاكَ",
    "translation": "O Allah, make the best of my days the day I meet You.",
    "count": 1
  },
  {
    "id": 19,
    "arabic": "اللَّهُمَّ طَهِّرْ قَلْبِي مِنَ النِّفَاقِ",
    "translation": "O Allah, purify my heart from hypocrisy.",
    "count": 1
  },
  {
    "id": 20,
    "arabic": "اللَّهُمَّ نَوِّرْ قَلْبِي بِالْقُرْآنِ",
    "translation": "O Allah, illuminate my heart with the Qur'an.",
    "count": 1
  },
  {
    "id": 21,
    "arabic": "رَبِّ نَجِّنِي مِنَ الْقَوْمِ الظَّالِمِينَ",
    "translation": "My Lord, save me from the wrongdoing people.",
    "count": 1
  },
  {
    "id": 22,
    "arabic": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنَ الْعَجْزِ وَالْكَسَلِ",
    "translation": "O Allah, I seek refuge in You from incapacity and laziness.",
    "count": 1
  },
  {
    "id": 23,
    "arabic": "رَبِّ هَبْ لِي حُكْمًا وَأَلْحِقْنِي بِالصَّالِحِينَ",
    "translation": "My Lord, grant me wisdom and join me with the righteous.",
    "count": 1
  },
  {
    "id": 24,
    "arabic": "اللَّهُمَّ إِنِّي أَسْتَوْدِعُكَ مَا عَلَّمْتَنِي",
    "translation": "O Allah, I entrust to You what You taught me.",
    "count": 1
  },
  {
    "id": 25,
    "arabic": "اللَّهُمَّ إِنِّي أَسْأَلُكَ عِلْمًا نَافِعًا",
    "translation": "O Allah, I ask You for beneficial knowledge.",
    "count": 1
  },
  {
    "id": 26,
    "arabic": "اللَّهُمَّ اجْعَلْنِي شَاكِرًا لِنِعْمَتِكَ",
    "translation": "O Allah, make me grateful for Your blessings.",
    "count": 1
  },
  {
    "id": 27,
    "arabic": "اللَّهُمَّ إِنِّي أَسْأَلُكَ حُسْنَ الْخَاتِمَةِ",
    "translation": "O Allah, I ask You for a good end.",
    "count": 1
  },
  {
    "id": 28,
    "arabic": "اللَّهُمَّ بَلِّغْنَا رَمَضَانَ",
    "translation": "O Allah, let us reach Ramadan.",
    "count": 1
  },
  {
    "id": 29,
    "arabic": "اللَّهُمَّ اجْعَلْنَا مِمَّنْ قَامَ رَمَضَانَ إِيمَانًا وَاحْتِسَابًا",
    "translation": "O Allah, make us among those who stand in Ramadan with faith and hope.",
    "count": 1
  },
  {
    "id": 30,
    "arabic": "اللَّهُمَّ اجْعَلْنَا مِنْ عُتَقَائِكَ مِنَ النَّارِ",
    "translation": "O Allah, make us among those You free from the Fire.",
    "count": 1
  },
  {
    "id": 31,
    "arabic": "اللَّهُمَّ طَهِّرْنِي مِنَ الذُّنُوبِ وَالْخَطَايَا",
    "translation": "O Allah, purify me from sins and mistakes.",
    "count": 1
  },
  {
    "id": 32,
    "arabic": "اللَّهُمَّ اكْفِنِي بِحَلَالِكَ عَنْ حَرَامِكَ",
    "translation": "O Allah, suffice me with what is lawful from what is unlawful.",
    "count": 1
  },
  {
    "id": 33,
    "arabic": "اللَّهُمَّ اجْعَلْنِي لَكَ شَكَّارًا، لَكَ ذَكَّارًا",
    "translation": "O Allah, make me one who is very thankful and remembers You much.",
    "count": 1
  },
  {
    "id": 34,
    "arabic": "اللَّهُمَّ إِنِّي أَعُوذُ بِكَ مِنْ زَوَالِ نِعْمَتِكَ",
    "translation": "O Allah, I seek refuge in You from the loss of Your blessings.",
    "count": 1
  },
  {
    "id": 35,
    "arabic": "اللَّهُمَّ اجْعَلْنِي مِنَ الرَّاشِدِينَ",
    "translation": "O Allah, make me among the rightly guided.",
    "count": 1
  },
  {
    "id": 36,
    "arabic": "اللَّهُمَّ اجْعَلْنِي مُحِبًّا لِصَالِحِ الْأَعْمَالِ",
    "translation": "O Allah, make me love righteous deeds.",
    "count": 1
  },
  {
    "id": 37,
    "arabic": "اللَّهُمَّ اجْعَلْ قَلْبِي مُتَعَلِّقًا بِالْآخِرَةِ",
    "translation": "O Allah, make my heart attached to the Hereafter.",
    "count": 1
  },
  {
    "id": 38,
    "arabic": "اللَّهُمَّ إِنِّي أَسْأَلُكَ صَبْرًا جَمِيلًا",
    "translation": "O Allah, I ask You for beautiful patience.",
    "count": 1
  },
  {
    "id": 39,
    "arabic": "اللَّهُمَّ اجْعَلْنِي مِنَ الْمُخْلِصِينَ",
    "translation": "O Allah, make me from the sincere ones.",
    "count": 1
  },
  {
    "id": 40,
    "arabic": "اللَّهُمَّ أَحْسِنْ عَاقِبَتِي فِي الْأُمُورِ كُلِّهَا",
    "translation": "O Allah, make the end of all my affairs good.",
    "count": 1
  }
]

class Islamic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hadiths = []
        try:
            with open('commands/islamic/hadiths.json', 'r', encoding='utf-8') as f:
                self.hadiths = json.load(f)
        except FileNotFoundError:
            print("hadiths.json not found. Hadith command will not work.")
        except json.JSONDecodeError:
            print("Error decoding hadiths.json. Hadith command will not work.")

        self.zikrs = []
        try:
            with open('commands/islamic/zikrs.json', 'r', encoding='utf-8') as f:
                self.zikrs = json.load(f)
        except FileNotFoundError:
            print("zikrs.json not found. Zikr command will not work.")
        except json.JSONDecodeError:
            print("Error decoding zikrs.json. Zikr command will not work.")

    # --- Dua ---
    @commands.command(name='dua', help='Fetches and displays a random Dua.')
    async def dua_command(self, ctx, *, query: str = None):
        await self.send_dua(ctx)

    @app_commands.command(name='dua', description='Fetches and displays a random Dua.')
    async def dua_slash(self, interaction: Interaction):
        await self.send_dua(interaction)

    async def send_dua(self, dest):
        dua = random.choice(DUAS)
        embed = discord.Embed(
            title=f"Dua #{dua['id']}",
            description=f"**Arabic:** {dua['arabic']}\n\n**Translation:** {dua['translation']}",
            color=discord.Color.green()
        )
        if isinstance(dest, Interaction):
            await dest.response.send_message(embed=embed)
        else:
            await dest.send(embed=embed)

    # --- Hadith ---
    @commands.command(name='hadith', help='Fetches and displays a random or specific Hadith.')
    async def hadith_command(self, ctx, *, query: str = None):
        await self.send_hadith(ctx, query)

    @app_commands.command(name='hadith', description='Fetches and displays a random or specific Hadith.')
    @app_commands.describe(query='ID or keyword to search for a hadith (optional)')
    async def hadith_slash(self, interaction: Interaction, query: str = None):
        await self.send_hadith(interaction, query)

    async def send_hadith(self, dest, query=None):
        if not self.hadiths:
            msg = "Hadith data is not available."
            if isinstance(dest, Interaction):
                await dest.response.send_message(msg)
            else:
                await dest.send(msg)
            return
        hadith = None
        if query:
            try:
                hadith_id = int(query)
                hadith = next((h for h in self.hadiths if h['id'] == hadith_id), None)
            except ValueError:
                query = query.lower()
                matching_hadiths = [h for h in self.hadiths if query in h['text'].lower() or query in h['arabic_text'].lower() or query in h['book'].lower() or query in h['reference'].lower()]
                if matching_hadiths:
                    hadith = random.choice(matching_hadiths)
                else:
                    msg = f"No hadith found matching '{query}'."
                    if isinstance(dest, Interaction):
                        await dest.response.send_message(msg)
                    else:
                        await dest.send(msg)
                    return
        else:
            hadith = random.choice(self.hadiths)
        if hadith:
            embed = discord.Embed(
                title=f"Hadith | {hadith['book']} {hadith['hadith_number']}",
                description=f"{hadith['text']}\n\n{hadith['arabic_text']}",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Reference: {hadith['reference']}")
            if isinstance(dest, Interaction):
                await dest.response.send_message(embed=embed)
            else:
                await dest.send(embed=embed)
        else:
            msg = "Could not retrieve hadith."
            if isinstance(dest, Interaction):
                await dest.response.send_message(msg)
            else:
                await dest.send(msg)

    # --- Zikr ---
    @commands.command(name='zikr', help='Provides a reminder for Zikr or displays a specific Zikr.')
    async def zikr_command(self, ctx, *, query: str = None):
        await self.send_zikr(ctx, query)

    @app_commands.command(name='zikr', description='Provides a reminder for Zikr or displays a specific Zikr.')
    @app_commands.describe(query='ID or keyword to search for a zikr (optional)')
    async def zikr_slash(self, interaction: Interaction, query: str = None):
        await self.send_zikr(interaction, query)

    async def send_zikr(self, dest, query=None):
        if not self.zikrs:
            msg = "Zikr data is not available."
            if isinstance(dest, Interaction):
                await dest.response.send_message(msg)
            else:
                await dest.send(msg)
            return
        zikr = None
        if query:
            try:
                zikr_id = int(query)
                zikr = next((z for z in self.zikrs if z['id'] == zikr_id), None)
            except ValueError:
                query = query.lower()
                matching_zikrs = [z for z in self.zikrs if query in z['translation'].lower() or query in z['arabic'].lower()]
                if matching_zikrs:
                    zikr = random.choice(matching_zikrs)
                else:
                    msg = f"No zikr found matching '{query}'."
                    if isinstance(dest, Interaction):
                        await dest.response.send_message(msg)
                    else:
                        await dest.send(msg)
                    return
        else:
            zikr = random.choice(self.zikrs)
        if zikr:
            embed = discord.Embed(
                title="Zikr Reminder",
                description=f"{zikr['arabic']}\n\n{zikr['translation']}",
                color=discord.Color.green()
            )
            if zikr.get('count') and zikr['count'] > 1:
                embed.add_field(name="Recommended Count", value=zikr['count'], inline=True)
            if isinstance(dest, Interaction):
                await dest.response.send_message(embed=embed)
            else:
                await dest.send(embed=embed)
        else:
            msg = "Could not retrieve zikr."
            if isinstance(dest, Interaction):
                await dest.response.send_message(msg)
            else:
                await dest.send(msg)

    # --- Quran (placeholder, still TODO) ---
    @commands.command(name='quran', help='Fetches and displays a Quranic Ayat translation.')
    async def quran_command(self, ctx, surah: int, ayat: int, *, translation: str = 'en'):
        await self.send_quran(ctx, surah, ayat, translation)

    @app_commands.command(name='quran', description='Fetches and displays a Quranic Ayat translation.')
    @app_commands.describe(surah='Surah number', ayat='Ayat number', translation='Translation language (default: en)')
    async def quran_slash(self, interaction: Interaction, surah: int, ayat: int, translation: str = 'en'):
        await self.send_quran(interaction, surah, ayat, translation)

    async def send_quran(self, dest, surah, ayat, translation):
        # TODO: Implement logic to fetch and display Quran Ayat translation
        msg = f"Fetching Ayat {ayat} from Surah {surah}... (translation: {translation})"
        if isinstance(dest, Interaction):
            await dest.response.send_message(msg)
        else:
            await dest.send(msg)

    async def cog_load(self):
        self.bot.tree.add_command(self.dua_slash)
        self.bot.tree.add_command(self.hadith_slash)
        self.bot.tree.add_command(self.zikr_slash)
        self.bot.tree.add_command(self.quran_slash)

async def setup(bot):
    await bot.add_cog(Islamic(bot)) 