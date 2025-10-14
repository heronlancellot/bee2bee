from uagents import Agent, Context, Model
 
class Message(Model):
    message: str
 
sigmar = Agent(name="sigmar", seed="sigmar recovery phrase", port=8000, endpoint=["http://localhost:8000/submit"])
SLAANESH_ADDRESS = "agent1qddw8cfn685e3p082lcn9dxe63yrqf03s77puv4d0as8a4j7c84s572juzj"
 
@sigmar.on_interval(period=3.0)
async def send_message(ctx: Context):
    await ctx.send(SLAANESH_ADDRESS, Message(message="hello there slaanesh"))
 
@sigmar.on_message(model=Message)
async def sigmar_message_handler(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f"Received message from {sender}: {msg.message}")
 
if __name__ == "__main__":
    sigmar.run()    