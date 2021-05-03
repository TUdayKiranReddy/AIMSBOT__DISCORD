import discord
from discord.ext import commands
import os
import emoji
from optimise_grade import optimise_grade
from AIMS import AIMS

TOKEN = 'Your-TOKEN-for-Discord-Bot'



client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.command()
async def ping(ctx):
	await ctx.send('Pong! '+str(round(client.latency*1000))+' ms')

@client.command()
async def report(ctx):
	Session = AIMS()
	loginStat = 0
	flag = 0

	while(True):
		if loginStat == 0:
			print(emoji.emojize('Loggin in, Please wait :sunny:.'))
			await ctx.send(emoji.emojize('Loggin in, Please wait :sunny:.'))
			loginStat=Session.login(firstime=True)
			Session.driver.implicitly_wait(5)

		if loginStat == 1:
			print('We are logged in.')
			await ctx.send('We are logged in.')
			cgpa = Session.get_CGPA()
			await ctx.send('Your CGPA is {}.'.format(str(cgpa)))

			@client.command()
			async def maxcg(ctx, *, constraints):
				pconst = ['la', 'ca', 'fe', 'de', 'total']
				consts = constraints.split(" ")
				ipconsts = [0, 0, 0, 0, None]
				for i in consts:
					for j in range(len(pconst)):
						if i[:2] == pconst[j]:
							ipconsts[j] = int((i.split("=")[1]))
				await ctx.send(optimise_grade(Session.cData, minLA=ipconsts[0], minCA=ipconsts[1], minFE=ipconsts[2], minDE=ipconsts[3], minCred=ipconsts[4]))

			@client.command()
			async def update(ctx):
				df = Session.any_new_grade()
				if df.all()!=None:
					s = 'The following courses grades are released:-\n'
					for i in df['Course']:
						s += (df['Course Title'].iloc[i] + '\t' + df['Grade'].iloc[i])
					await ctx.send(s)
				else:
					await ctx.send(emoji.emojize('No new courses grade is released :poop:.'))

			@client.command()
			async def logout(ctx):
				Session.logout()
				await ctx.send("Succesfully Logged out!")
			break

		elif loginStat == 2:
			await ctx.send("AIMS Message: Please wait for 30 minutes to proceed")
			break

		else:
			if not flag:
				print('AI is not able to recognise the CAPTCHA. Please see the CAPTCHA and send the text.')
				await ctx.send('AI is not able to recognise the CAPTCHA. Please see the CAPTCHA and send the text.')
				await ctx.send(file=discord.File('captcha.png'))
				flag = 1
				loginStat=-1
				continue
			if flag:
				@client.command()
				async def captcha(ctx, text):
					loginStat = Session.login(text=text, firstime=False)
					print('We are logged in with mannual input.')
					await ctx.send('We are logged in.')
					cgpa = Session.get_CGPA()
					await ctx.send('Your CGPA is {}.'.format(str(cgpa)))

				@client.command()
				async def maxcg(ctx, *, constraints):
					pconst = ['la', 'ca', 'fe', 'de', 'total']
					consts = constraints.split(" ")
					ipconsts = [0, 0, 0, 0, None]
					for i in consts:
						for j in range(len(pconst)):
							if i[:2] == pconst[j]:
								ipconsts[j] = int((i.split("=")[1]))
					await ctx.send(optimise_grade(Session.cData, minLA=ipconsts[0], minCA=ipconsts[1], minFE=ipconsts[2], minDE=ipconsts[3], minCred=ipconsts[4]))

				@client.command()
				async def update(ctx):
					df = Session.any_new_grade()
					if not df.empty:
						s = 'The following courses grades are released:-\n'
						for i in range(len(df['Course Title'])):
							s += (df['Course Title'].iloc[i] + '\t' + df['Grade'].iloc[i] + '\n')
						await ctx.send(s)
					else:
						await ctx.send(emoji.emojize('No new courses grade is released :poop:.'))

				@client.command()
				async def logout(ctx):
					Session.logout()
					await ctx.send("Succesfully Logged out!")

				break

@client.command()
async def clear(ctx, amount=100):
	await ctx.channel.purge(limit=amount)


client.run(TOKEN)
