import os
import ollama
from dotenv import load_dotenv


load_dotenv()


class ReasoningStreamParser:
    """Parses streaming output to separate reasoning (<think>...</think>) from output content."""

    def __init__(self, on_reasoning=None, on_content=None):
        self.on_reasoning = on_reasoning
        self.on_content = on_content
        self.in_think = False
        self.buffer = ""
        self.full_reasoning = ""
        self.full_content = ""

    def feed(self, chunk: str, explicit_reasoning: str = None):
        if explicit_reasoning:
            self.full_reasoning += explicit_reasoning
            if self.on_reasoning:
                self.on_reasoning(explicit_reasoning)
        
        if not chunk:
            return

        self.buffer += chunk

        while self.buffer:
            if not self.in_think:
                think_start = self.buffer.find("<think>")
                if think_start != -1:
                    pre_content = self.buffer[:think_start]
                    if pre_content:
                        self.full_content += pre_content
                        if self.on_content:
                            self.on_content(pre_content)
                    
                    self.in_think = True
                    self.buffer = self.buffer[think_start + 7:]
                else:
                    partial_match = False
                    for i in range(1, min(7, len(self.buffer) + 1)):
                        if "<think>".startswith(self.buffer[-i:]):
                            safe_content = self.buffer[:-i]
                            if safe_content:
                                self.full_content += safe_content
                                if self.on_content:
                                    self.on_content(safe_content)
                            self.buffer = self.buffer[-i:]
                            partial_match = True
                            break
                    if not partial_match:
                        self.full_content += self.buffer
                        if self.on_content:
                            self.on_content(self.buffer)
                        self.buffer = ""
            else:
                think_end = self.buffer.find("</think>")
                if think_end != -1:
                    reasoning_part = self.buffer[:think_end]
                    if reasoning_part:
                        self.full_reasoning += reasoning_part
                        if self.on_reasoning:
                            self.on_reasoning(reasoning_part)
                    
                    self.in_think = False
                    self.buffer = self.buffer[think_end + 8:]
                else:
                    partial_match = False
                    for i in range(1, min(8, len(self.buffer) + 1)):
                        if "</think>".startswith(self.buffer[-i:]):
                            safe_reasoning = self.buffer[:-i]
                            if safe_reasoning:
                                self.full_reasoning += safe_reasoning
                                if self.on_reasoning:
                                    self.on_reasoning(safe_reasoning)
                            self.buffer = self.buffer[-i:]
                            partial_match = True
                            break
                    if not partial_match:
                        self.full_reasoning += self.buffer
                        if self.on_reasoning:
                            self.on_reasoning(self.buffer)
                        self.buffer = ""

    def flush(self):
        if self.buffer:
            if self.in_think:
                self.full_reasoning += self.buffer
                if self.on_reasoning:
                    self.on_reasoning(self.buffer)
            else:
                self.full_content += self.buffer
                if self.on_content:
                    self.on_content(self.buffer)
            self.buffer = ""


class QwenLLM:
    
    def __init__(self, model_name: str = None):
        host = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model_name = model_name or os.getenv("OLLAMA_MODEL", "qwen3:4b")
        self.client = ollama.Client(host=host)
        self.async_client = ollama.AsyncClient(host=host)
        
    def get_options(self):
        num_ctx = int(os.getenv("OLLAMA_NUM_CTX", "2048"))
        num_thread = int(os.getenv("OLLAMA_NUM_THREAD", "0"))  # 0 = auto
        num_predict = int(os.getenv("OLLAMA_NUM_PREDICT", "512"))
        return {
            "temperature": 0.0,
            "num_ctx": num_ctx,
            "num_thread": num_thread,
            "num_predict": num_predict,
        }

    async def run_stream(self, messages: list, on_reasoning=None, on_content=None) -> tuple[str, str]:
        """Run LLM with streaming output, separating reasoning and content."""
        parser = ReasoningStreamParser(on_reasoning=on_reasoning, on_content=on_content)
        options = self.get_options()

        response_stream = await self.async_client.chat(
            model=self.model_name,
            messages=messages,
            options=options,
            keep_alive=-1,
            stream=True,
        )

        async for chunk in response_stream:
            msg = chunk.get("message", {})
            content = msg.get("content", "")
            reasoning = msg.get("reasoning", "") or msg.get("thinking", "")
            parser.feed(content, explicit_reasoning=reasoning)

        parser.flush()
        return parser.full_reasoning.strip(), parser.full_content.strip()

    def run(self, messages: list) -> str:
        """Run LLM response synchronously with performance options."""
        options = self.get_options()
        response = self.client.chat(
            model=self.model_name,
            messages=messages,
            options=options,
            keep_alive=-1,
        )
        content = response["message"]["content"].strip()
        parser = ReasoningStreamParser()
        parser.feed(content)
        parser.flush()
        return parser.full_content.strip()


               

                
              



        
