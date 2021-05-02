import discord
import term_backend
import asyncio
import os

TOKEN = "NTczNzQ4OTU3MTU5NjIwNjA5.XkYOfA._fWd8bZXR-kNe8EHnixXyvB8YzI"  # put your own tokon here
client = discord.Client()
channel_id = 827063908929634355   # put your vimbot channel here
term_running = False
filetype = 'txt'
filetype_changed = False

help_text = """```
How to use:
    Send text to this channel and Vim will interpret it.
    Alternatively, you can type `:end vim` to end the session.
    Special keys can be sent by using the shortcuts below.

Shortcuts:
    <esc>     Escape
    <cr>      Return
    <bs>      Backspace
    <tab>     Tab
    <space>   Space
    <C-key>   Control + Key (works for any key)
    <up>      Up Arrow
    <down>    Down Arrow
    <left>    Left Arrow
    <right>   Right Arrow

Example:
    `ihello world<esc>` will insert "hello world" and then exit insert mode.
```"""

@client.event
async def on_ready():
    print('ready')
    global channel
    channel = client.get_channel(channel_id)

async def start_vim():
    global term_running, term_message, term, help_message, filetype_changed
    term_running = True
    term = term_backend.Term('disterm_session', 'vim')
    await asyncio.sleep(1)
    help_message = await channel.send(help_text)
    term_message = await channel.send(f"```loading vim```")
    last_screen = ''
    await asyncio.sleep(0.5)
    while term_running:
        screen = term.get_screen()
        if screen:
            if filetype_changed or last_screen != screen:
                filetype_changed = False
                last_screen = screen
                screen = screen.replace("`", "´")
                await term_message.edit(content=f"```{filetype}\n{screen}```")
        else:
            await term_message.edit(content='```vim session ended```')
            term_running = False
        await asyncio.sleep(1)


async def end_vim():
    global term_running
    term.end()
    term_running = False
    await help_message.delete()
    await term_message.edit(content="```vim session ended```")



@client.event
async def on_message(message):
    global filetype, filetype_changed
    if message.author == client.user:
        return

    if message.channel.id != channel_id:
        return

    if not term_running:
        if message.content == ':start vim':
            await start_vim()

    elif message.content == ':end vim':
        await end_vim()

    else:
        if message.content == ':toggle cursor':
            term.toggle_cursor()
        elif message.content.startswith(':sethighlight'):
            try:
                filetype = message.content.split()[1]
            except IndexError:
                filetype = 'txt'
            filetype_changed = True
        else:
            term.send_keys(message.content)

        await message.delete()


client.run(TOKEN)
