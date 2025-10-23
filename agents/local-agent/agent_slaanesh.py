from uagents import Agent, Context, Model
 
class Message(Model):
    message: str
 
slaanesh = Agent(name="slaanesh", seed="slaanesh recovery phrase", port=8001, endpoint=["http://localhost:8001/submit"])
 
@slaanesh.on_message(model=Message)
async def slaanesh_message_handler(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f"Received message from {sender}: {msg.message}")
    await ctx.send(sender, Message(message="hello there sigmar"))
 
if __name__ == "__main__":
    slaanesh.run()