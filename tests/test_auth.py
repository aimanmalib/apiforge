"""Tests for AuthAgent."""

import pytest
from apiforge.agents.auth import AuthAgent


class TestAuthAgent:
    @pytest.mark.asyncio
    async def test_generate_bearer(self, config, mock_client, tracker):
        mock_client.chat_completion.return_value.content = "no code"
        agent = AuthAgent(client=mock_client, config=config, tracker=tracker)
        code = await agent.generate_auth("bearer")
        assert len(code) > 0

    @pytest.mark.asyncio
    async def test_generate_apikey(self, config, mock_client, tracker):
        mock_client.chat_completion.return_value.content = "no code"
        agent = AuthAgent(client=mock_client, config=config, tracker=tracker)
        code = await agent.generate_auth("api_key")
        assert len(code) > 0
