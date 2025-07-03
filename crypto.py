import logging
import os
import asyncio
import requests
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, function_tool

# Correct logging setup
logging.getLogger("httpx").setLevel(logging.WARNING)
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set in .env")

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

@function_tool
def get_coin_price(currency: str = "BTCUSDT") -> str:
    """Get cryptocurrency price from Binance"""
    # Format the URL with the currency parameter
    url = f"https://api.binance.com/api/v3/ticker/price"
    response = requests.get(url)
    
    if response.status_code != 200:
        return f"❌ Failed to fetch price for {currency.upper()}"
    
    data = response.json()
    return f"✅ {data['symbol']}: {data['price']} USDT"

# Create agent
agent = Agent(
    name="Binance Agent",
    instructions="You are a helpful crypto assistant that provides live cryptocurrency prices from Binance",
    model=model,
    tools=[get_coin_price]
)

async def main():
    user_query = input("Ask about crypto prices: ")
    result = await Runner.run(
        agent, 
        user_query, 
        run_config=RunConfig()  # Create proper RunConfig instance
    )
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())