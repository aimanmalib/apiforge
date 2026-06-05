"""Tests for SchemaAgent."""

import pytest
from apiforge.agents.schema import SchemaAgent
from apiforge.agents.parser import APIDescription, ParsedEndpoint


class TestSchemaAgent:
    @pytest.mark.asyncio
    async def test_generate_spec(self, config, mock_client, tracker):
        desc = APIDescription(
            title="Test",
            description="Test API",
            endpoints=[
                ParsedEndpoint(path="/items", method="GET", description="List items")
            ],
        )
        agent = SchemaAgent(client=mock_client, config=config, tracker=tracker)
        spec = await agent.generate_spec(desc)
        assert spec["openapi"] == "3.1.0"
        assert spec["info"]["title"] == "Test"

    @pytest.mark.asyncio
    async def test_spec_has_paths(self, config, mock_client, tracker):
        desc = APIDescription(
            title="T",
            description="D",
            endpoints=[ParsedEndpoint(path="/x", method="POST", description="Create")],
        )
        agent = SchemaAgent(client=mock_client, config=config, tracker=tracker)
        spec = await agent.generate_spec(desc)
        assert "/x" in spec["paths"]
        assert "post" in spec["paths"]["/x"]

    @pytest.mark.asyncio
    async def test_spec_has_security(self, config, mock_client, tracker):
        desc = APIDescription(title="T", description="D", auth_type="bearer")
        agent = SchemaAgent(client=mock_client, config=config, tracker=tracker)
        spec = await agent.generate_spec(desc)
        assert "securitySchemes" in spec["components"]

    @pytest.mark.asyncio
    async def test_build_schemas(self, config, mock_client, tracker):
        desc = APIDescription(
            title="T",
            description="D",
            models=[
                {
                    "name": "User",
                    "fields": [{"name": "id", "type": "integer", "required": True}],
                }
            ],
        )
        agent = SchemaAgent(client=mock_client, config=config, tracker=tracker)
        spec = await agent.generate_spec(desc)
        assert "User" in spec["components"]["schemas"]
