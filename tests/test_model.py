"""Tests for ModelAgent."""

import pytest
from apiforge.agents.model import ModelAgent
from apiforge.agents.parser import APIDescription


class TestModelAgent:
    @pytest.mark.asyncio
    async def test_generate_models(self, config, mock_client, tracker):
        desc = APIDescription(
            title="T",
            description="D",
            models=[
                {
                    "name": "Item",
                    "fields": [{"name": "title", "type": "string", "required": True}],
                }
            ],
        )
        mock_client.chat_completion.return_value.content = "no code"
        agent = ModelAgent(client=mock_client, config=config, tracker=tracker)
        code = await agent.generate_models(desc)
        assert "class Item" in code
