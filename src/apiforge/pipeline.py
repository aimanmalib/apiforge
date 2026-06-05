"""Pipeline orchestrator for APIForge."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from .client import MiMoClient
from .config import APIForgeConfig
from .token_tracker import TokenTracker
from .agents.parser import ParserAgent, APIDescription
from .agents.schema import SchemaAgent
from .agents.router import RouterAgent
from .agents.model import ModelAgent
from .agents.auth import AuthAgent
from .agents.test_gen import TestAgent
from .agents.doc_gen import DocAgent
from .agents.validator import ValidateAgent, ValidationResult


@dataclass
class PipelineResult:
    description: APIDescription
    openapi_spec: dict[str, Any]
    router_code: str
    model_code: str
    auth_code: str
    test_code: str
    docs: str
    validation: ValidationResult
    token_summary: dict[str, Any] = field(default_factory=dict)


class APIForgePipeline:
    """Orchestrate the full API scaffolding pipeline."""

    def __init__(self, config: APIForgeConfig | None = None) -> None:
        self.config = config or APIForgeConfig.from_env()
        self.client = MiMoClient(self.config)
        self.tracker = TokenTracker()
        self.parser = ParserAgent(
            client=self.client, config=self.config, tracker=self.tracker
        )
        self.schema_agent = SchemaAgent(
            client=self.client, config=self.config, tracker=self.tracker
        )
        self.router = RouterAgent(
            client=self.client, config=self.config, tracker=self.tracker
        )
        self.model = ModelAgent(
            client=self.client, config=self.config, tracker=self.tracker
        )
        self.auth = AuthAgent(
            client=self.client, config=self.config, tracker=self.tracker
        )
        self.test_gen = TestAgent(
            client=self.client, config=self.config, tracker=self.tracker
        )
        self.doc_gen = DocAgent(
            client=self.client, config=self.config, tracker=self.tracker
        )
        self.validator = ValidateAgent(
            client=self.client, config=self.config, tracker=self.tracker
        )

    async def generate(self, description: str) -> PipelineResult:
        """Run full pipeline: parse -> schema -> code -> test -> docs -> validate."""
        parsed = await self.parser.parse(description)
        spec = await self.schema_agent.generate_spec(desc=parsed)
        router_code = await self.router.generate_routes(desc=parsed)
        model_code = await self.model.generate_models(desc=parsed)
        auth_code = await self.auth.generate_auth(auth_type=parsed.auth_type)
        test_code = await self.test_gen.generate_tests(desc=parsed)
        docs = await self.doc_gen.generate_docs(desc=parsed)
        validation = await self.validator.validate(spec=spec)
        await self.client.close()
        return PipelineResult(
            description=parsed,
            openapi_spec=spec,
            router_code=router_code,
            model_code=model_code,
            auth_code=auth_code,
            test_code=test_code,
            docs=docs,
            validation=validation,
            token_summary=self.tracker.summary(),
        )
