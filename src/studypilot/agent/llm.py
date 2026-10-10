"""LLM client wrapper."""
import time
from typing import Dict, Any, List, Optional
import openai
from openai import OpenAI

from src.studypilot.config import (
    GROQ_API_KEY,
    LLM_BASE_URL,
    LLM_MODEL,
    LLM_FALLBACK_MODELS,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    logger
)

class LLMClient:
    def __init__(self) -> None:
        if not GROQ_API_KEY:
            logger.warning("GROQ_API_KEY is not set. LLM calls will fail.")
        
        self.client = OpenAI(
            api_key=GROQ_API_KEY or "dummy_key",
            base_url=LLM_BASE_URL,
        )
        self.primary_model = LLM_MODEL
        self.fallback_models = LLM_FALLBACK_MODELS
    
    def generate(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None, temperature: float = LLM_TEMPERATURE, model: Optional[str] = None) -> Dict[str, Any]:
        if not GROQ_API_KEY:
            return {"role": "assistant", "content": "Error: API key is missing..."}
            
        models_to_try = [model or self.primary_model] + self.fallback_models
        backoff_times = [1, 2, 4]
        
        for current_model in models_to_try:
            for attempt, backoff in enumerate(backoff_times + [0]):
                try:
                    kwargs = {
                        "model": current_model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": LLM_MAX_TOKENS,
                    }
                    if tools:
                        kwargs["tools"] = tools
                        
                    response = self.client.chat.completions.create(**kwargs)
                    
                    choice = response.choices[0].message
                    result = {
                        "role": choice.role,
                        "content": choice.content,
                    }
                    if choice.tool_calls:
                        result["tool_calls"] = [
                            {
                                "id": tc.id,
                                "type": tc.type,
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                }
                            } for tc in choice.tool_calls
                        ]
                    return result
                    
                except (openai.RateLimitError, openai.NotFoundError) as e:
                    logger.warning(f"Error with model {current_model}: {e}")
                    if attempt < len(backoff_times):
                        time.sleep(backoff_times[attempt])
                        continue
                    else:
                        break # Exhausted retries for this model
                except openai.AuthenticationError as e:
                    logger.error(f"Authentication error: {e}")
                    return {"role": "assistant", "content": "Error: API key is missing or invalid..."}
                except openai.APIError as e:
                    logger.error(f"API error: {e}")
                    if attempt < len(backoff_times):
                        time.sleep(backoff_times[attempt])
                        continue
                    else:
                        break
                        
        return {"role": "assistant", "content": "Error: All models failed..."}
        
    def generate_text(self, messages: List[Dict[str, Any]], temperature: float = LLM_TEMPERATURE) -> str:
        response = self.generate(messages, temperature=temperature)
        return response.get("content") or ""
