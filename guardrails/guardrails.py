from project import model
from agents import Agent, OutputGuardrailTripwireTriggered,Runner,RunContextWrapper,GuardrailFunctionOutput,output_guardrail
from pydantic import BaseModel
import asyncio

class IsQueryIsPolitical(BaseModel):
    is_query_contains_political_content: bool
    political_name_mentioned: bool
    political_criticsm:bool
    reasoning: str

political_guardrail_agent = Agent(name="Guardrail Output Agent", model=model , output_type=IsQueryIsPolitical,
                            instructions="Check if the output contains any political name ,political affairs or political criticism.")

@output_guardrail
async def output_guardrail_def(ctx:RunContextWrapper, agent:Agent, output:IsQueryIsPolitical)->GuardrailFunctionOutput:
    result=await Runner.run(political_guardrail_agent, output , context=ctx.context)
    response=result.final_output
    return GuardrailFunctionOutput(output_info=response, tripwire_triggered= (response.is_query_contains_political_content or
                         response.political_name_mentioned or response.political_criticsm))

agwnt = Agent(name="General Agent", instructions="You`re helpful Assistant", output_guardrails=[output_guardrail_def], model=model)

async def main():
    try:
        result=await Runner.run(agwnt, "Who is Donurt Trump , the Boolshitter")
        print(result.final_output)
    except OutputGuardrailTripwireTriggered:
        print("Output Guardrail tripped!")

if __name__ == "__main__":
    asyncio.run(main())