from project import model
import asyncio
from agents import Agent,Runner,RunContextWrapper,GuardrailFunctionOutput,input_guardrail
from pydantic import BaseModel

# enable_verbose_stdout_logging()
class IsDataRelatedToHotels(BaseModel):
    """Checks if the query is related to relevant hotels"""
    user_hotel_mension_name: str
    reasoning_summary_of_hotels: str=""

guardrail_agent =Agent(name="Guardrail Agent", model=model, output_type=IsDataRelatedToHotels,instructions="Check the query is related to hotels .")

@input_guardrail
async def hotel_guardrail(ctx: RunContextWrapper, agent: Agent, input_text: str) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input_text, context=ctx.context)
    output = result.final_output
    return GuardrailFunctionOutput(output_info=output, tripwire_triggered= not output.user_hotel_mension_name)

def get_hotel_instructions(hotel_name:str):
    return f"""
       J You are a helpful assistant for {hotel_name}.
        Always greet guests warmly and mention the hotel's name in your greeting.
        Provide recommendations for nearby attractions.
        If a guest asks about {hotel_name}, give details about rooms, facilities, and dining options with dummy details.
        Answers user every query related to hotels with dummy details"""

async def main():
    try: 
        user_context=IsDataRelatedToHotels(user_hotel_mension_name="Barbad hotel")
        agent =Agent(name="GeneralAgent", model=model, input_guardrails=[hotel_guardrail],
            instructions=get_hotel_instructions(user_context.user_hotel_mension_name))

        guard_result = await Runner.run(agent, "Give details hotel",context=user_context)
        print(guard_result.final_output)

    except Exception as er:
        print("Tripwire triggered :", str(er))

if __name__ =="__main__":
    asyncio.run(main())

# Output
# Greetings! Welcome to Barbad Hotel. I'm happy to provide you with details about our hotel.

# **Rooms:**

# *   We offer a variety of rooms to suit your needs, including standard rooms, deluxe rooms, and suites.
# *   All rooms are equipped with comfortable beds, private bathrooms, air conditioning, and free Wi-Fi.
# *   Suites also include a separate living area and a balcony with stunning views.

# **Facilities:**

# *   We have a swimming pool, a fitness center, and a spa.
# *   We also offer a business center and meeting rooms for our corporate guests.
# *   Free parking is available for all guests.

# **Dining:**

# *   We have a restaurant that serves breakfast, lunch, and dinner.
# *   We also have a bar that serves drinks and snacks.
# *   Room service is available 24 hours a day.

# Is there anything specific you'd like to know about our hotel?
