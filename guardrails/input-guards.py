from project import model
import asyncio
from agents import Agent,Runner,RunContextWrapper,GuardrailFunctionOutput,input_guardrail,enable_verbose_stdout_logging
from pydantic import BaseModel

enable_verbose_stdout_logging()

class IsDataRelatedToHotels(BaseModel):
    """Checks if the query is related to relevant hotels"""
    is_query_related_to_sannata_hotel: bool
    is_query_related_to_veerana_hotel: bool
    reasoning_summary_of_hotels: str
    user_asked_about_hotel_name:str

guardrail_agent =Agent(name="Guardrail Agent", model=model, output_type=IsDataRelatedToHotels
    ,instructions="Check the query is related to Sannata or Veerana hotels or both.If yes, extract the user discussed hotel name the user name is asking about.")

@input_guardrail
async def hotel_guardrail(ctx: RunContextWrapper, agent: Agent, input_text: str) -> GuardrailFunctionOutput:
    result = await Runner.run(guardrail_agent, input_text, context=ctx.context)
    output = result.final_output        
    return GuardrailFunctionOutput(output_info=output, tripwire_triggered=not (output.is_query_related_to_sannata_hotel or output.is_query_related_to_veerana_hotel, ))

def dynamic_instructions(ctx: RunContextWrapper[IsDataRelatedToHotels], agent: Agent):
    return f"Print the hotel name: {ctx.context.user_asked_about_hotel_name}"

agent =Agent(name="GeneralAgent", model=model, input_guardrails=[hotel_guardrail],
    instructions=dynamic_instructions)

async def main():
    try:
        guard_result = await Runner.run(agent, "WHow`re the owner of Veerana and Sannat hotels"),
        print(guard_result.final_output)

    except Exception as er:
        print("Tripwire triggered :", str(er))

if __name__ =="__main__":
    asyncio.run(main())
