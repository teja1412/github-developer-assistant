import asyncio
import sys

from mcp import Client,StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent

from google import genai
# from google.genai import types
from dotenv import load_dotenv
import os
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
# model = "gemini-3.1-flash-lite"
model = "gemini-3.6-flash"
# model = "gemini-3.5-flash-lite"
# model = "gemini-4-argon"
genai_client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))

def server_params(server_script_path: str) -> StdioServerParameters:
    """Describe the subprocess that runs an MCP server

    Args:
        server_script_path: Path to the server script (.py or .js)
    """
    if server_script_path.endswith(".py"):
        command = "python"
    elif server_script_path.endswith(".js"):
        command = "node"
    else:
        raise ValueError("Server script must be a .py or .js file")

    env = {}
    if os.getenv("GITHUB_TOKEN"):
        env["GITHUB_TOKEN"] = os.environ["GITHUB_TOKEN"]

    return StdioServerParameters(command=command, args=[server_script_path], env=env)

async def process_query(client:Client,query:str) -> str:
    """Process a query using Claude and available tools"""
    user_query = query
    # messages = [
    #     {
    #         "role": "user",
    #         "content": query
    #     }
    # ]
    system_instructions = """You are an intelligent GitHub Developer Assistant.

        Your responsibility is to understand the user's intent, retrieve relevant GitHub information when necessary, and provide accurate, useful, and concise responses.

        ### Intent Understanding
        - Carefully understand what the user is asking before taking any action.
        - Identify the specific information required to answer the query.
        - Distinguish between profile information, repository information, issues, pull requests, and analytical questions.
        - Interpret natural-language queries correctly, including implicit references such as "my repositories" or "my PRs".

        ### Tool Usage
        - Select tools dynamically based on the user's intent.
        - Use only the tools necessary to fulfill the request.
        - Avoid unnecessary tool calls and redundant information retrieval.
        - Do not retrieve additional information unless it contributes meaningfully to the answer.
        - **IMPORTANT**: For questions requiring multiple sources of information, retrieve the relevant data by calling multiple tools and combine the results.
        - When performing comparisons or analysis, ensure that the required data has actually been retrieved.

        ### Accuracy and Reliability
        - Treat retrieved GitHub data as the source of truth.
        - Never fabricate repository details, statistics, issues, pull requests, or user information.
        - Do not assume missing values or incomplete results.
        - Clearly distinguish retrieved facts from your own analysis.
        - If the information is insufficient, explain what is missing.
        - If a tool fails, communicate the failure rather than inventing an answer.

        ### Response Quality
        - Answer the user's question directly.
        - Keep responses concise unless the user requests detailed explanations.
        - Use tables and bullet points when they improve readability.
        - Summarize large tool responses instead of reproducing raw data.
        - Highlight important findings and conclusions.
        - Avoid irrelevant details and repetitive explanations.

        ### General Behavior
        - Do not execute unrelated actions.
        - Do not make assumptions about the user's intent when clarification is necessary.
        - Do not claim to have performed actions that were not executed.
        - Focus on providing meaningful answers rather than simply displaying retrieved data.
        """

    query = f"{system_instructions}\n\nUser Query: {query}"

    tool_list = await client.list_tools()

    available_tools = [{
            "type": "function",
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": tool.input_schema["properties"],
                "required": tool.input_schema["required"],
            },
        } for tool in tool_list.tools]

    interaction = genai_client.interactions.create(
        model=model,
        input=query,
        tools=available_tools,
        )

    for step in interaction.steps:
        if step.type == "function_call":
            tool_name = step.name
            tool_input = step.arguments
            logger.info("Tool name: %s, Tool input: %s", tool_name, tool_input)
            tool_response = await client.call_tool(tool_name,tool_input)
            print(f"Tool response: {tool_response}")
            result = {
                    "type": "tool_result",
                    "tool_use_id": step.id,
                    "content": "\n".join(
                        block.text
                        for block in tool_response.content
                        if isinstance(block, TextContent)
                    ),
                    "is_error": tool_response.is_error
                }
    interaction = genai_client.interactions.create(
        model=model,
    input=(
        "Answer the user's request using only the supplied tool results. "
        "Keep the response concise, readable, and tailored to the request. "
        "For a repository-list request, first write one short sentence identifying "
        "the GitHub owner and total repositories returned, then add a blank line "
        "and a Markdown table with a header row and separator row. Use columns "
        "Repository, Description, Language, Stars, and Open issues; link repository "
        "names to their GitHub URLs when available. Put each repository on its own "
        "table row, with spaces around every cell value and pipe. Show unavailable "
        "values as —. Do not output a long numbered list or an archived section "
        "unless the user asks for that detail. For a profile request, start with a "
        "brief overview of the user (name, username, bio, followers, and public "
        "repository count when available), then include a repository table only if "
        "it helps answer the request. For issues and pull requests, add a short "
        "context sentence and use a similarly well-spaced table when listing multiple "
        "items. Always place a blank line before and after Markdown tables. "
        "Do not include fields irrelevant to the user's request.\n\n"
        f"User request: {user_query}\n\nTool results: {result}"
    )
    )
    # print(f"Final response: {interaction.output_text}")
    return interaction.output_text


async def chat_loop(client:Client) -> None:
    """Run an interactive chat loop"""
    logger.info("\nMCP Client Started!")
    logger.info("Type your queries or 'quit' to exit.")

    while(True):
        try:
            query = (await asyncio.to_thread(input, "\nQuery: ")).strip()
        except EOFError:
            break

        if query.lower() == "quit":
            break

        try:
            await process_query(client,query)
            logger.info("Processs completed successfully.")
        except Exception as e:
            logger.error(f"\n Error: {e}")



async def main():
    if len(sys.argv)<2:
        logger.info("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    async with Client(stdio_client(server_params(sys.argv[1]))) as client:
        tool_list = await client.list_tools()

        tool_names = [tool.name for tool in tool_list.tools]
        logger.info("\nConnected to server with tools: %s", tool_names)

        await chat_loop(client)


if __name__=="__main__":
    asyncio.run(main())