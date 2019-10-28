"""
MIT License
Copyright (c) 2019 GamingGeek

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction, 
including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, 
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF 
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION 
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from core.permissions import has_permission
from discord.ext import commands
import discord

class Prefix(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name='prefix', permissions=['commands.prefix', 'Administrator'])
	@commands.guild_only()
	@has_permission('commands.prefix', administrator=True)
	async def prefix(self, ctx, pfx: str = None):
		if pfx == None:
			await ctx.send("Missing argument for prefix! (Note: For prefixes with a space, surround it in \"\")")
		else:
			query = 'SELECT * FROM prefixes WHERE gid = $1;'
			prefixraw = await self.bot.db.fetch(query, ctx.guild.id)
			con = await self.bot.db.acquire()
			if not prefixraw: #INSERT INTO prefixes (\"name\", \"gid\", \"prefix\") VALUES (\"{ctx.guild.name}\", {ctx.guild.id}, \"{pfx}\");
				async with con.transaction():
					query = 'INSERT INTO prefixes (\"name\", \"gid\", \"prefix\") VALUES ($1, $2, $3);'
					await self.bot.db.execute(query, ctx.guild.name, ctx.guild.id, pfx)
				await self.bot.db.release(con)
			else: #UPDATE prefixes SET prefix = \"{pfx}\" WHERE gid = {ctx.guild.id};
				async with con.transaction():
					query = 'UPDATE prefixes SET prefix = $1 WHERE gid = $2;'
					await self.bot.db.execute(query, pfx, ctx.guild.id)
				await self.bot.db.release(con)
			await ctx.send(f'Ok, {discord.utils.escape_mentions(ctx.guild.name)}\'s prefix is now {pfx}!')

def setup(bot):
	try:
		bot.add_cog(Prefix(bot))
	except Exception as e:
		errortb = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
		print(f'Error while adding cog "prefix";\n{errortb}')