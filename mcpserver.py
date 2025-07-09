from mcp.server.fastmcp import FastMCP
from tools.translator import translator  # ваш модуль перевода

mcp = FastMCP("translator-agent")
translator.register(mcp)

if __name__ == "__main__":
    mcp.run()
