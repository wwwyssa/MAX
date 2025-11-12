import aiomax
import logging

bot = aiomax.Bot("f9LHodD0cOIRY0kxaAAsvfhYqEv2ley3x9B2T7Mn6JIxw7Y6i5U8Wu1eMGbWXUNk1menHVRnTDdwyLRUe6mA", default_format="markdown")



# Функция будет выполняться при отправке любого сообщения
@bot.on_message("/start")
async def echo(message: aiomax.Message):
    print(str(message.sender.user_id))
    await message.send(f"*{message.sender.user_id}*")

if __name__ == "__main__":
    bot.run()