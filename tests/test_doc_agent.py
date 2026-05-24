"""Tests for DocAgent."""
import pytest
from apiforge.agents.doc_gen import DocAgent
from apiforge.agents.parser import APIDescription, ParsedEndpoint

class TestDocAgent:
    @pytest.mark.asyncio
    async def test_generate_docs(self, config, mock_client, tracker):
        desc = APIDescription(title="Test", description="A test API",
            endpoints=[ParsedEndpoint(path="/items", method="GET", description="List items")])
        mock_client.chat_completion.return_value.content = "# Test API"
        agent = DocAgent(client=mock_client, config=config, tracker=tracker)
        docs = await agent.generate_docs(desc)
        assert isinstance(docs, str)
        assert len(docs) > 0

    @pytest.mark.asyncio
    async def test_generate_docs_fallback(self, config, mock_client, tracker):
        desc = APIDescription(title="T", description="D",
            endpoints=[ParsedEndpoint(path="/x", method="GET", description="X",
                parameters=[{"name": "q", "in": "query", "type": "string"}])])
        mock_client.chat_completion.return_value.content = ""
        agent = DocAgent(client=mock_client, config=config, tracker=tracker)
        docs = await agent.generate_docs(desc)
        assert "Test" in docs or "T" in docs or "q" in docs
