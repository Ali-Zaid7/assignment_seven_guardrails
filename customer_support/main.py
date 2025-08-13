from project import model
import asyncio
from classes import IsQueryAboutOrder, IsOutputPolitical, IsLanguageOfUserIsOffensive
from agents import Agent, Runner, RunContextWrapper, GuardrailFunctionOutput, function_tool, input_guardrail, output_guardrail,ModelSettings
from mock_db import faq_db, orders_db

guardrail_agent = Agent(name="Language Guardrail agent",instructions="check for offensive or negative language" ,model=model, output_type=IsLanguageOfUserIsOffensive)
 #Plotical Output guardrail
political_agent_guardrail=Agent(name="Political Guardrail Agent", model=model, output_type=IsOutputPolitical ,
                                instructions="Check if the response contains political topics or references to political figures.")

@input_guardrail
async def inp_guard(ctx:RunContextWrapper , agent:Agent , input_text:str)->GuardrailFunctionOutput:
    result =await Runner.run(guardrail_agent, input_text, context=ctx.context)
    output = result.final_output
    return GuardrailFunctionOutput(output_info=output, tripwire_triggered=any(output.is_user_use_negative_words) or any(output.is_user_use_offensive_language))

@output_guardrail
async def outp_guardrail(ctx:RunContextWrapper, agent:Agent ,output_text:str)->GuardrailFunctionOutput:
    res = await Runner.run(political_agent_guardrail, output_text ,context=ctx.context)
    output = res.final_output
    return GuardrailFunctionOutput(output_info= output , tripwire_triggered=output.contains_political_content)

query_checker_agent = Agent(name="Query Checker Agent",instructions="Agent that check the query content is about order or not." 
                            ,output_type=IsQueryAboutOrder ,model=model,model_settings=ModelSettings(max_tokens=50))
resf =Runner.run_sync(query_checker_agent, "Tell me about the Prime Minister")
is_about_order = bool(resf.final_output)  # Extract boolean

@function_tool(is_enabled=is_about_order)
def get_order_status(order_id)->dict:
    """Fetch order details from database"""
    if order_id not in orders_db:
        raise ValueError("Order ID not found!")
    else:
        print(orders_db[order_id])

@function_tool
def get_faq_data()->dict:
    return faq_db

humanAgent = Agent(name="Human Agent",instructions="Handles complex or escalated queries." ,model=model, model_settings=ModelSettings(temperature=0.7) ) # More creative responses

botAgent = Agent(name="Bot Agent",instructions="Agent handles basic FAQs, fetch order statuses, and escalate to a human agent when necessary" ,
                 model=model, input_guardrails=[inp_guard], output_guardrails=[outp_guardrail], tools=[get_order_status,get_faq_data], 
                 handoffs=[humanAgent] , model_settings=ModelSettings(tool_choice="required"))
# print(is_about_order=bool(resf))

async def main():
    bot_output = (await Runner.run(botAgent, "top 5 bullsihitter PMs of the world")).final_output
    human_output = (await Runner.run(humanAgent, "I want to refund order of Order ID:ORD123 because it is not much good as it was looking in picture.")).final_output
    
    print("BOT AGENT:", bot_output)
    print("HUMAN AGENT:", human_output)

if __name__ == "__main__":
    asyncio.run(main())