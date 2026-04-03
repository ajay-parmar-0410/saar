import asyncio
from dotenv import load_dotenv
from graph.build_graph import build_graph


load_dotenv()

async def main():
    graph = build_graph()

    result = await graph.ainvoke({
        "command": "Generate daily briefing",
        "logs": []
    })

    print("\nFinal State:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())

