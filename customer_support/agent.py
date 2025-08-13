from project import model
import asyncio
from agents import Agent, Runner, function_tool, input_guardrail, output_guardrail, GuardrailFunctionOutput, RunContextWrapper
from pydantic import BaseModel
from typing import List

# 1. Data Models
class LanguageAnalysis(BaseModel):
    is_offensive: bool
    detected_terms: List[str]

class PoliticalContentCheck(BaseModel):
    contains_political_content: bool

class OrderCheck(BaseModel):
    is_order_query: bool

# 2. Mock Databases
faq_db = {
    "return policy": "30-day return policy",
    "shipping": "3-5 business days",
    "warranty": "1-year manufacturer warranty"
}

orders_db = {
    "ORD123": {"status": "shipped", "items": ["T-shirt", "Jeans"]},
    "ORD456": {"status": "processing", "items": ["Shoes"]}
}

# 3. Initialize Agents (Only Once)
language_guard = Agent(
    name="LanguageGuard",
    model=model,
    output_type=LanguageAnalysis,
    instructions="Check if text contains offensive language. Return boolean flag and detected terms."
)

political_guard = Agent(
    name="PoliticalGuard",
    model=model,
    output_type=PoliticalContentCheck,
    instructions="Check if text contains political content. Return only boolean flag."
)

query_checker = Agent(
    name="OrderChecker",
    model=model,
    output_type=OrderCheck,
    instructions="Check if query is about orders. Return only boolean flag."
)

# 4. Core Functionality
@function_tool(
    is_enabled=lambda ctx: "order" in ctx.input_text.lower(),
    error_function=lambda e: "⚠️ Please provide a valid order number"
)
def get_order_status(order_id: str) -> dict:
    """Fetch order details with validation"""
    if order_id not in orders_db:
        raise ValueError("Order not found")
    return orders_db[order_id]

@function_tool
def get_faq_answer(question: str) -> str:
    """Answer common product questions"""
    return faq_db.get(question.lower(), "I don't have information on that topic")

# 5. Guardrails
@input_guardrail
async def language_check(ctx: RunContextWrapper, agent: Agent, text: str):
    result = await Runner.run(language_guard, text)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_offensive
    )

@output_guardrail
async def political_check(ctx: RunContextWrapper, agent: Agent, text: str):
    result = await Runner.run(political_guard, text)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.contains_political_content
    )

# 6. Configure Main Agents
support_bot = Agent(
    name="SupportBot",
    model=model,
    tools=[get_order_status, get_faq_answer],
    input_guardrails=[language_check],
    output_guardrails=[political_check],
    model_settings={
        "tool_choice": "auto",
        "metadata": {"dept": "customer_support"}
    }
)

human_agent = Agent(
    name="HumanAgent",
    model=model,
    instructions="You are a human customer service representative."
)

# 7. Complete Handler
async def handle_query(query: str):
    try:
        result = await Runner.run(support_bot, query)
        if result.tripwire_triggered:
            human_response = await Runner.run(human_agent, query)
            return human_response.final_output
        return result.final_output
    except Exception as e:
        return f"Error: {str(e)}"

# 8. Test Cases
async def test():
    queries = [
        "Where's my order ORD123?",  # Valid order
        "What's your return policy?", # FAQ
        "This is fucking terrible!",  # Offensive
        "What do you think about the president?" # Political
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("Response:", await handle_query(query))

if __name__ == "__main__":
    asyncio.run(test())