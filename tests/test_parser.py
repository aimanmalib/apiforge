"""Tests for ParserAgent."""

import json
import pytest
from apiforge.agents.parser import ParserAgent, APIDescription, ParsedEndpoint


class TestParserAgent:
    @pytest.mark.asyncio
    async def test_parse_returns_description(self, config, mock_client, tracker):
        mock_client.chat_completion.return_value.content = json.dumps(
            {
                "title": "Blog API",
                "description": "A blog",
                "endpoints": [
                    {"path": "/posts", "method": "GET", "description": "List posts"}
                ],
                "models": [],
            }
        )
        agent = ParserAgent(client=mock_client, config=config, tracker=tracker)
        result = await agent.parse("A blog API with posts")
        assert isinstance(result, APIDescription)
        assert result.title == "Blog API"

    @pytest.mark.asyncio
    async def test_parse_extracts_endpoints(self, config, mock_client, tracker):
        mock_client.chat_completion.return_value.content = json.dumps(
            {
                "title": "T",
                "description": "D",
                "endpoints": [
                    {"path": "/users", "method": "GET", "description": "List users"},
                    {"path": "/users", "method": "POST", "description": "Create user"},
                ],
                "models": [],
            }
        )
        agent = ParserAgent(client=mock_client, config=config, tracker=tracker)
        result = await agent.parse("users API")
        assert len(result.endpoints) == 2

    @pytest.mark.asyncio
    async def test_parse_handles_invalid_json(self, config, mock_client, tracker):
        mock_client.chat_completion.return_value.content = "not json"
        agent = ParserAgent(client=mock_client, config=config, tracker=tracker)
        result = await agent.parse("test")
        assert isinstance(result, APIDescription)

    def test_parsed_endpoint_defaults(self):
        ep = ParsedEndpoint(path="/x", method="GET", description="test")
        assert ep.auth_required is True
        assert ep.parameters == []
