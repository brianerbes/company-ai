from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List
from uuid import UUID

from .agent import Agent


@dataclass
class Company:
    """
    The main runtime context for an entire company instance. It's responsible
    for loading the company's configuration and discovering all its agents.
    """

    # --- Core Attributes ---
    path: Path
    name: str = field(init=False)
    manifest: Dict[str, Any] = field(init=False)

    # --- Agent Management ---
    agents: Dict[UUID, Agent] = field(default_factory=dict, repr=False)
    agent_manifests: Dict[UUID, Path] = field(default_factory=dict, repr=False)
    agent_role_registry: Dict[str, List[UUID]] = field(default_factory=dict, repr=False)

    def __post_init__(self):
        """Initializes the company by loading manifests and building registries."""
        self._load_manifest()
        self._discover_agents()
        self._build_registry()

    def _load_manifest(self):
        """Loads the company's primary manifest.json file."""
        manifest_path = self.path / "manifest.json"
        try:
            with manifest_path.open("r") as f:
                self.manifest = json.load(f)
            self.name = self.manifest["identity"]["name"]
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as exc:
            raise ValueError("Invalid or missing manifest.json file") from exc

    def _discover_agents(self):
        """Discovers all agent manifest files within the workspace."""
        agents_dir = self.path / "agents"
        if not agents_dir.exists():
            return
        for subdir in agents_dir.iterdir():
            if subdir.is_dir():
                meta_file = subdir / ".agent_meta.json"
                if meta_file.exists():
                    try:
                        with meta_file.open("r") as f:
                            agent_data = json.load(f)
                        agent_id = UUID(agent_data["agent_id"])
                        self.agent_manifests[agent_id] = meta_file
                    except (json.JSONDecodeError, KeyError, ValueError):
                        # Skip corrupted or invalid agent manifests
                        continue

    def _build_registry(self):
        """Builds the role-to-agent registry for quick lookups."""
        for _, meta_path in self.agent_manifests.items():
            try:
                with meta_path.open("r") as f:
                    agent_data = json.load(f)
                role = agent_data.get("role")
                agent_id = UUID(agent_data["agent_id"])
                if role:
                    if role not in self.agent_role_registry:
                        self.agent_role_registry[role] = []
                    self.agent_role_registry[role].append(agent_id)
            except (json.JSONDecodeError, KeyError, ValueError):
                # Skip corrupted or invalid agent manifests
                continue

    def get_agent(self, agent_id: UUID) -> Agent | None:
        """
        Retrieves an agent by its ID, loading it from its manifest if not already cached.
        """
        if agent_id in self.agents:
            return self.agents[agent_id]

        if agent_id in self.agent_manifests:
            try:
                with self.agent_manifests[agent_id].open("r") as f:
                    agent_data = json.load(f)
                agent = Agent(
                    id=agent_id,
                    role=agent_data.get("role", ""),
                    traits=agent_data.get("traits", []),
                    capabilities=agent_data.get("capabilities", {}),
                    company=self,
                    _raw_system_prompt=agent_data.get("system_prompt", ""),
                )
                self.agents[agent_id] = agent
                return agent
            except (json.JSONDecodeError, KeyError):
                return None
        return None
