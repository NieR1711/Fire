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

from datadog import initialize, statsd, ThreadStats
from sentry_sdk import push_scope
from discord.ext import commands
import sentry_sdk
import discord
import asyncpg
import json

class Fire(commands.Bot):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.config: dict = json.load(open('config.json', 'r'))
		self.db: asyncpg.pool.Pool = None
		self.datadog: ThreadStats = None
		if 'sentry' in self.config:
			sentry_sdk.init(self.config['sentry'])
		if 'datadogapi' in self.config and 'datadogapp' in self.config:
			datadogopt = {
				'api_key': self.config['datadogapi'],
				'app_key': self.config['datadogapp']
			}
			initialize(**datadogopt)
			self.datadog = ThreadStats()
			self.datadog.start()

	def isadmin(self, ctx: commands.Context) -> bool:
		if str(ctx.author.id) not in self.config['admins']:
			admin = False
		else:
			admin = True
		return admin

	def sentry_exc(error: commands.CommandError, userscope: dict, exclevel: str, extra: dict):
		with push_scope() as scope:
			scope.user = userscope
			scope.level = exclevel
			for key in extra:
				scope.set_tag(key, extra[key])
			sentry_sdk.capture_exception(error)

	async def is_team_owner(self, user: typing.Union[discord.User, discord.Member]):
		if user.id == self.owner_id:
			return True
		else:
			return False