from fastmcp import FastMCP
import requests
import os

API_URL = "http://localhost:8000"
TOKEN = os.getenv("MCP_TOKEN")

mcp = FastMCP(name="President-MCP", json_response=True)

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

@mcp.tool()
def presidents():
    return requests.get(f"{API_URL}/presidents", headers=headers).json()

@mcp.tool()
def create_president(prenom: str, nom: str, code: int, solde: int):
    return requests.post(
        f"{API_URL}/presidents",
        headers=headers,
        json={"prenom": prenom, "nom": nom, "code": code, "solde": solde}
    ).json()

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=9000,
        path="/mcp"
    )
