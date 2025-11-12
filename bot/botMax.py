import aiomax

bot = aiomax.Bot("f9LHodD0cOIRY0kxaAAsvfhYqEv2ley3x9B2T7Mn6JIxw7Y6i5U8Wu1eMGbWXUNk1menHVRnTDdwyLRUe6mA", default_format="markdown")

taps = 0

kb = aiomax.buttons.KeyboardBuilder()
button = aiomax.buttons.CallbackButton('Нажми на меня!', 'click')
kb.add(button)

@bot.on_bot_start()
async def info(pd: aiomax.BotStartPayload):
    await pd.send(f"**Жми**!\nТапы: {taps}", keyboard=kb)


# Отправляем сообщение с кнопкой при вводе команды /tap
@bot.on_command('tap')
async def tap_command(ctx: aiomax.CommandContext):
    await ctx.reply(f"**Жми!**\nТапы: {taps}", keyboard=kb)


# Обрабатываем нажатие на кнопку в сообщении
@bot.on_button_callback('click')
async def on_tap(callback: aiomax.Callback):
    global taps
    taps += 1
    await callback.answer(text=f"Жми!\nТапы: **{taps}**")

@bot.on_message()
async def on_message(message: aiomax.Message):
    await message.reply("Используй команду /tap чтобы начать играть!")


if __name__ == "__main__":
    bot.run()