"""Tests for pipeline."""

import json
import pytest
from apiforge.pipeline import APIForgePipeline, PipelineResult


class TestPipeline:
    def test_init_creates_agents(self, config):
        p = APIForgePipeline(config)
        assert p.parser is not None
        assert p.router is not None
        assert p.model is not None
        assert p.auth is not None

    def test_default_config(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "k")
        p = APIForgePipeline()
        assert p.config.mimo_api_key == "k"

    @pytest.mark.asyncio
    async def test_generate_returns_result(self, config, mock_client, tracker):
        from apiforge.client import CompletionResponse

        mock_client.chat_completion.return_value = CompletionResponse(
            content=json.dumps(
                {"title": "T", "description": "D", "endpoints": [], "models": []}
            ),
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
        )
        p = APIForgePipeline(config)
        p.client = mock_client
        for a in [
            p.parser,
            p.schema_agent,
            p.router,
            p.model,
            p.auth,
            p.test_gen,
            p.doc_gen,
        ]:
            a.client = mock_client
        result = await p.generate("test API")
        assert isinstance(result, PipelineResult)
