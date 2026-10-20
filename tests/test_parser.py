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


class TestParserRobustness:
    @pytest.mark.asyncio
    async def test_prompt_specifies_json_shape(self, config, mock_client, tracker):
        mock_client.chat_completion.return_value.content = "{}"
        agent = ParserAgent(client=mock_client, config=config, tracker=tracker)
        await agent.parse("todo API")
        messages = mock_client.chat_completion.call_args.args[0]
        system = messages[0]["content"]
        assert '"endpoints"' in system and '"path"' in system and '"method"' in system

    @pytest.mark.asyncio
    async def test_parse_json_wrapped_in_prose(self, config, mock_client, tracker):
        mock_client.chat_completion.return_value.content = (
            "Sure! Here is the spec:\n"
            + json.dumps(
                {
                    "title": "Todo API",
                    "endpoints": [{"path": "/todos", "method": "get"}],
                }
            )
            + "\nLet me know if you need more."
        )
        agent = ParserAgent(client=mock_client, config=config, tracker=tracker)
        result = await agent.parse("todo API")
        assert result.title == "Todo API"
        assert [(e.method, e.path) for e in result.endpoints] == [("GET", "/todos")]

    @pytest.mark.asyncio
    async def test_parse_fenced_json(self, config, mock_client, tracker):
        mock_client.chat_completion.return_value.content = (
            '```json\n{"title": "X", "endpoints": []}\n```'
        )
        agent = ParserAgent(client=mock_client, config=config, tracker=tracker)
        result = await agent.parse("x")
        assert result.title == "X"

    @pytest.mark.asyncio
    async def test_parse_non_object_json_falls_back(self, config, mock_client, tracker):
        mock_client.chat_completion.return_value.content = "[1, 2, 3]"
        agent = ParserAgent(client=mock_client, config=config, tracker=tracker)
        result = await agent.parse("x")
        assert result.title == "Parsed API"
