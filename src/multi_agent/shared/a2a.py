"""
A2A (Agent-to-Agent) Protocol implementation.

A2A enables communication between distributed agents running on
different machines or processes. This module provides:
- AgentCard: Agent identity and capabilities descriptor
- A2AServer: HTTP server for receiving agent messages
- A2AClient: Client for sending messages to remote agents
- TaskDispatcher: Distribute tasks across agent network

Learn more: https://google.github.io/A2A/
"""

import json
import asyncio
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Awaitable
from enum import Enum
from datetime import datetime
import uuid

from loguru import logger


class TaskState(str, Enum):
    """Task execution states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentCard:
    """
    Agent Card - describes an agent's identity and capabilities.

    The Agent Card is how agents advertise themselves on the network.
    It contains metadata about the agent's skills and how to contact it.
    """

    name: str
    description: str
    url: str  # Base URL for A2A endpoints
    version: str = "1.0.0"
    skills: list[str] = field(default_factory=list)
    input_modes: list[str] = field(default_factory=lambda: ["text"])
    output_modes: list[str] = field(default_factory=lambda: ["text"])

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentCard":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class A2AMessage:
    """
    Message exchanged between agents.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    receiver: str = ""
    content: str = ""
    content_type: str = "text"
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "A2AMessage":
        return cls(**data)


@dataclass
class A2ATask:
    """
    Task submitted to an agent.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    state: TaskState = TaskState.PENDING
    result: str = ""
    error: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["state"] = self.state.value
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "A2ATask":
        data["state"] = TaskState(data.get("state", "pending"))
        return cls(**data)


class A2AServer:
    """
    A2A Server - receives and processes messages from other agents.

    Exposes HTTP endpoints for A2A protocol:
    - GET /.well-known/agent.json - Agent Card
    - POST /tasks - Submit a task
    - GET /tasks/{id} - Get task status
    - POST /messages - Send a message

    Example:
        >>> agent_card = AgentCard(
        ...     name="coder",
        ...     description="Code generation agent",
        ...     url="http://localhost:8001",
        ...     skills=["python", "javascript"]
        ... )
        >>> server = A2AServer(agent_card)
        >>>
        >>> @server.on_task
        >>> async def handle_task(task: A2ATask) -> str:
        ...     return f"Completed: {task.description}"
        >>>
        >>> server.run(port=8001)
    """

    def __init__(self, agent_card: AgentCard):
        self.agent_card = agent_card
        self.tasks: dict[str, A2ATask] = {}
        self.messages: list[A2AMessage] = []
        self._task_handler: Callable[[A2ATask], Awaitable[str]] | None = None
        self._message_handler: Callable[[A2AMessage], Awaitable[str]] | None = None

    def on_task(self, handler: Callable[[A2ATask], Awaitable[str]]):
        """Decorator to register task handler."""
        self._task_handler = handler
        return handler

    def on_message(self, handler: Callable[[A2AMessage], Awaitable[str]]):
        """Decorator to register message handler."""
        self._message_handler = handler
        return handler

    async def handle_request(
        self, method: str, path: str, body: dict | None = None
    ) -> tuple[int, dict]:
        """
        Handle incoming HTTP request.

        Returns:
            Tuple of (status_code, response_body)
        """
        try:
            if method == "GET" and path == "/.well-known/agent.json":
                return 200, self.agent_card.to_dict()

            elif method == "POST" and path == "/tasks":
                return await self._handle_create_task(body or {})

            elif method == "GET" and path.startswith("/tasks/"):
                task_id = path.split("/")[-1]
                return self._handle_get_task(task_id)

            elif method == "POST" and path == "/messages":
                return await self._handle_message(body or {})

            else:
                return 404, {"error": "Not found"}

        except Exception as e:
            logger.exception(f"Error handling request: {e}")
            return 500, {"error": str(e)}

    async def _handle_create_task(self, body: dict) -> tuple[int, dict]:
        """Handle task creation."""
        task = A2ATask(
            description=body.get("description", ""),
            metadata=body.get("metadata", {}),
        )
        self.tasks[task.id] = task

        # Process task asynchronously
        asyncio.create_task(self._process_task(task))

        return 201, task.to_dict()

    async def _process_task(self, task: A2ATask):
        """Process a task in background."""
        task.state = TaskState.RUNNING

        try:
            if self._task_handler:
                result = await self._task_handler(task)
                task.result = result
                task.state = TaskState.COMPLETED
            else:
                task.error = "No task handler registered"
                task.state = TaskState.FAILED
        except Exception as e:
            task.error = str(e)
            task.state = TaskState.FAILED
            logger.exception(f"Task {task.id} failed: {e}")
        finally:
            task.completed_at = datetime.now().isoformat()

    def _handle_get_task(self, task_id: str) -> tuple[int, dict]:
        """Handle task status query."""
        if task_id not in self.tasks:
            return 404, {"error": f"Task not found: {task_id}"}
        return 200, self.tasks[task_id].to_dict()

    async def _handle_message(self, body: dict) -> tuple[int, dict]:
        """Handle incoming message."""
        message = A2AMessage.from_dict(body)
        message.receiver = self.agent_card.name
        self.messages.append(message)

        response = ""
        if self._message_handler:
            response = await self._message_handler(message)

        return 200, {"status": "received", "response": response}

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Run the A2A server.

        Uses aiohttp for async HTTP server.
        """
        try:
            from aiohttp import web
        except ImportError:
            logger.error("aiohttp required. Install with: pip install aiohttp")
            return

        async def handle(request: web.Request) -> web.Response:
            method = request.method
            path = request.path
            body = None
            if method in ("POST", "PUT"):
                body = await request.json()

            status, response = await self.handle_request(method, path, body)
            return web.json_response(response, status=status)

        app = web.Application()
        app.router.add_route("*", "/{path:.*}", handle)

        logger.info(f"Starting A2A server '{self.agent_card.name}' on {host}:{port}")
        web.run_app(app, host=host, port=port)


class A2AClient:
    """
    A2A Client - sends messages and tasks to remote agents.

    Example:
        >>> client = A2AClient()
        >>>
        >>> # Discover agent
        >>> card = await client.get_agent_card("http://localhost:8001")
        >>> print(card.skills)
        >>>
        >>> # Submit a task
        >>> task = await client.submit_task(
        ...     "http://localhost:8001",
        ...     "Write a hello world in Python"
        ... )
        >>>
        >>> # Wait for completion
        >>> result = await client.wait_for_task(
        ...     "http://localhost:8001",
        ...     task["id"]
        ... )
    """

    def __init__(self):
        self._session = None

    async def _get_session(self):
        """Get or create aiohttp session."""
        if self._session is None:
            try:
                import aiohttp

                self._session = aiohttp.ClientSession()
            except ImportError:
                raise ImportError("aiohttp required. Install with: pip install aiohttp")
        return self._session

    async def close(self):
        """Close the client session."""
        if self._session:
            await self._session.close()
            self._session = None

    async def get_agent_card(self, agent_url: str) -> AgentCard:
        """
        Fetch agent's card to discover capabilities.

        Args:
            agent_url: Base URL of the agent

        Returns:
            AgentCard with agent info and skills
        """
        session = await self._get_session()
        async with session.get(f"{agent_url}/.well-known/agent.json") as resp:
            data = await resp.json()
            return AgentCard.from_dict(data)

    async def submit_task(
        self,
        agent_url: str,
        description: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Submit a task to an agent.

        Args:
            agent_url: Base URL of the agent
            description: Task description
            metadata: Optional task metadata

        Returns:
            Task info including ID
        """
        session = await self._get_session()
        payload = {"description": description, "metadata": metadata or {}}

        async with session.post(f"{agent_url}/tasks", json=payload) as resp:
            return await resp.json()

    async def get_task_status(self, agent_url: str, task_id: str) -> dict[str, Any]:
        """Get task status."""
        session = await self._get_session()
        async with session.get(f"{agent_url}/tasks/{task_id}") as resp:
            return await resp.json()

    async def wait_for_task(
        self,
        agent_url: str,
        task_id: str,
        timeout: float = 60.0,
        poll_interval: float = 1.0,
    ) -> dict[str, Any]:
        """
        Wait for a task to complete.

        Args:
            agent_url: Base URL of the agent
            task_id: Task ID to wait for
            timeout: Maximum wait time in seconds
            poll_interval: How often to check status

        Returns:
            Final task state
        """
        import time

        start = time.time()

        while time.time() - start < timeout:
            status = await self.get_task_status(agent_url, task_id)
            state = status.get("state")

            if state in (TaskState.COMPLETED.value, TaskState.FAILED.value):
                return status

            await asyncio.sleep(poll_interval)

        raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")

    async def send_message(
        self,
        agent_url: str,
        content: str,
        sender: str = "client",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Send a message to an agent.

        Args:
            agent_url: Base URL of the agent
            content: Message content
            sender: Sender name
            metadata: Optional metadata

        Returns:
            Response from agent
        """
        session = await self._get_session()
        message = A2AMessage(
            sender=sender,
            content=content,
            metadata=metadata or {},
        )

        async with session.post(
            f"{agent_url}/messages", json=message.to_dict()
        ) as resp:
            return await resp.json()


class AgentNetwork:
    """
    Network of distributed agents.

    Manages a registry of agents and enables task distribution.

    Example:
        >>> network = AgentNetwork()
        >>> network.register("http://localhost:8001")
        >>> network.register("http://localhost:8002")
        >>>
        >>> # Find agent with skill
        >>> agent = await network.find_agent_with_skill("python")
        >>>
        >>> # Submit to best agent
        >>> result = await network.submit_task("Write code", skill="python")
    """

    def __init__(self):
        self.agents: dict[str, AgentCard] = {}
        self.client = A2AClient()

    async def register(self, agent_url: str) -> AgentCard:
        """
        Register an agent by discovering its card.

        Args:
            agent_url: Base URL of the agent

        Returns:
            Discovered AgentCard
        """
        card = await self.client.get_agent_card(agent_url)
        self.agents[card.name] = card
        logger.info(f"Registered agent: {card.name} ({agent_url})")
        return card

    def find_agent_with_skill(self, skill: str) -> AgentCard | None:
        """Find an agent that has a specific skill."""
        for card in self.agents.values():
            if skill.lower() in [s.lower() for s in card.skills]:
                return card
        return None

    async def submit_task_to(
        self,
        agent_name: str,
        description: str,
        wait: bool = True,
    ) -> dict[str, Any]:
        """Submit task to a specific agent."""
        if agent_name not in self.agents:
            raise ValueError(f"Agent not found: {agent_name}")

        card = self.agents[agent_name]
        task = await self.client.submit_task(card.url, description)

        if wait:
            return await self.client.wait_for_task(card.url, task["id"])
        return task

    async def submit_task(
        self,
        description: str,
        skill: str | None = None,
        wait: bool = True,
    ) -> dict[str, Any]:
        """
        Submit task to an agent, optionally filtering by skill.

        Args:
            description: Task description
            skill: Required skill (optional)
            wait: Whether to wait for completion

        Returns:
            Task result
        """
        # Find suitable agent
        if skill:
            card = self.find_agent_with_skill(skill)
            if not card:
                raise ValueError(f"No agent found with skill: {skill}")
        else:
            # Just pick the first available
            if not self.agents:
                raise ValueError("No agents registered")
            card = list(self.agents.values())[0]

        return await self.submit_task_to(card.name, description, wait)

    async def broadcast_message(self, content: str, sender: str = "network"):
        """Send a message to all registered agents."""
        for card in self.agents.values():
            try:
                await self.client.send_message(card.url, content, sender)
            except Exception as e:
                logger.error(f"Failed to send to {card.name}: {e}")

    async def close(self):
        """Close network connections."""
        await self.client.close()
