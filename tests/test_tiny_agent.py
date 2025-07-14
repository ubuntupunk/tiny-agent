import pytest
import asyncio
from tiny_agent.core import Agent, Memory, ToolResult
from tiny_agent.tools import HTTPTool, FileTool, ShellTool


class TestTool:
    """Test tool for testing purposes."""
    name = "test_tool"
    description = "A test tool"
    
    async def execute(self, **kwargs) -> ToolResult:
        return ToolResult(success=True, data={"test": "success"})


class TestMemory:
    """Test memory functionality."""
    
    def test_memory_set_get(self):
        memory = Memory()
        memory.set("test_key", "test_value")
        assert memory.get("test_key") == "test_value"
    
    def test_memory_default(self):
        memory = Memory()
        assert memory.get("nonexistent", "default") == "default"
    
    def test_memory_delete(self):
        memory = Memory()
        memory.set("test_key", "test_value")
        memory.delete("test_key")
        assert memory.get("test_key") is None
    
    def test_memory_history(self):
        memory = Memory()
        memory.set("key1", "value1")
        memory.set("key2", "value2")
        memory.delete("key1")
        
        history = memory.get_history()
        assert len(history) == 3
        assert history[0]["action"] == "set"
        assert history[0]["key"] == "key1"


class TestAgent:
    """Test agent functionality."""
    
    @pytest.fixture
    def agent(self):
        return Agent("test-agent")
    
    @pytest.mark.asyncio
    async def test_agent_registration(self, agent):
        tool = TestTool()
        agent.register_tool(tool)
        assert tool.name in agent.tools
    
    @pytest.mark.asyncio
    async def test_agent_execute_tool(self, agent):
        tool = TestTool()
        agent.register_tool(tool)
        
        result = await agent.execute_tool("test_tool")
        assert result.success is True
        assert result.data["test"] == "success"
    
    @pytest.mark.asyncio
    async def test_agent_execute_nonexistent_tool(self, agent):
        result = await agent.execute_tool("nonexistent")
        assert result.success is False
        assert "not found" in result.error
    
    @pytest.mark.asyncio
    async def test_agent_run(self, agent):
        tool = TestTool()
        agent.register_tool(tool)
        
        result = await agent.run("test task")
        assert result["task"] == "test task"
        assert result["status"] == "completed"


class TestHTTPTool:
    """Test HTTP tool functionality."""
    
    @pytest.mark.asyncio
    async def test_http_get(self):
        tool = HTTPTool()
        result = await tool.execute(method="GET", url="https://httpbin.org/json")
        assert result.success is True
        assert result.data["status_code"] == 200
        assert result.data["json"] is not None
    
    @pytest.mark.asyncio
    async def test_http_invalid_url(self):
        tool = HTTPTool()
        result = await tool.execute(method="GET", url="https://invalid-url-12345.com")
        assert result.success is False


class TestFileTool:
    """Test file tool functionality."""
    
    @pytest.fixture
    def temp_file(self, tmp_path):
        file_path = tmp_path / "test.txt"
        file_path.write_text("test content")
        return file_path
    
    @pytest.mark.asyncio
    async def test_file_read(self, temp_file):
        tool = FileTool()
        result = await tool.execute(action="read", filepath=str(temp_file))
        assert result.success is True
        assert result.data["content"] == "test content"
    
    @pytest.mark.asyncio
    async def test_file_write(self, tmp_path):
        tool = FileTool()
        file_path = tmp_path / "write_test.txt"
        result = await tool.execute(
            action="write", 
            filepath=str(file_path), 
            content="new content"
        )
        assert result.success is True
        assert file_path.read_text() == "new content"
    
    @pytest.mark.asyncio
    async def test_file_exists(self, temp_file):
        tool = FileTool()
        result = await tool.execute(action="exists", filepath=str(temp_file))
        assert result.success is True
        assert result.data["exists"] is True


class TestShellTool:
    """Test shell tool functionality."""
    
    @pytest.mark.asyncio
    async def test_shell_success(self):
        tool = ShellTool()
        result = await tool.execute(command="echo 'hello world'")
        assert result.success is True
        assert "hello world" in result.data["stdout"]
    
    @pytest.mark.asyncio
    async def test_shell_error(self):
        tool = ShellTool()
        result = await tool.execute(command="false")
        assert result.success is False
        assert result.data["returncode"] == 1
    
    @pytest.mark.asyncio
    async def test_shell_timeout(self):
        tool = ShellTool()
        result = await tool.execute(command="sleep 5", timeout=1)
        assert result.success is False
        assert "timed out" in result.error