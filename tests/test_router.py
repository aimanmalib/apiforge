"""Tests for RouterAgent."""
import pytest
from apiforge.agents.router import RouterAgent
from apiforge.agents.parser import APIDescription, ParsedEndpoint

class TestRouterAgent:
    @pytest.mark.asyncio
    async def test_generate_routes(self, config, mock_client, tracker):
        desc = APIDescription(title="T", description="D",
            endpoints=[ParsedEndpoint(path="/items", method="GET", description="List")])
        mock_client.chat_completion.return_value.content = "no code blocks"
        agent = RouterAgent(client=mock_client, config=config, tracker=tracker)
        code = await agent.generate_routes(desc)
        assert isinstance(code, str)
        assert len(code) > 0

    @pytest.mark.asyncio
    async def test_generates_with_params(self, config, mock_client, tracker):
        desc = APIDescription(title="T", description="D",
            endpoints=[ParsedEndpoint(path="/items/{id}", method="GET", description="Get item",
                parameters=[{"name": "id", "in": "path", "type": "integer", "required": True}])])
        mock_client.chat_completion.return_value.content = "no code"
        agent = RouterAgent(client=mock_client, config=config, tracker=tracker)
        code = await agent.generate_routes(desc)
        assert "def " in code
