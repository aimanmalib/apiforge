"""Tests for BaseAgent."""
import pytest
from unittest.mock import AsyncMock
from apiforge.agents.base import BaseAgent
from apiforge.client import CompletionResponse

class ConcreteAgent(BaseAgent):
    name = "test"
    async def run(self, **kwargs):
        return "done"

class TestBaseAgent:
    def test_init(self, config, tracker):
        a = ConcreteAgent(config=config, tracker=tracker)
        assert a.name == "test"

    def test_repr(self, config, tracker):
        a = ConcreteAgent(config=config, tracker=tracker)
        assert "test" in repr(a)

    def test_system_prompt(self, config, tracker):
        a = ConcreteAgent(config=config, tracker=tracker)
        prompt = a._build_system_prompt()
        assert "test" in prompt

    @pytest.mark.asyncio
    async def test_call_mimo(self, config, mock_client, tracker):
        mock_client.chat_completion.return_value = CompletionResponse(
            content="response", prompt_tokens=10, completion_tokens=5, total_tokens=15)
        a = ConcreteAgent(client=mock_client, config=config, tracker=tracker)
        resp = await a._call_mimo("test prompt")
        assert resp.content == "response"
        assert tracker.total_calls() == 1

    @pytest.mark.asyncio
    async def test_run(self, config, mock_client, tracker):
        a = ConcreteAgent(client=mock_client, config=config, tracker=tracker)
        result = await a.run()
        assert result == "done"
