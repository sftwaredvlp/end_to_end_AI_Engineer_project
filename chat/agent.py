"""
OpenAI Function Calling Agent - Konuşma ve tool çağrısı mantığı
"""
import json
import logging
from typing import List, Dict, Any, Optional

from openai import OpenAI
from django.conf import settings

from .tools import TOOLS, execute_tool, ToolResult

logger = logging.getLogger(__name__)


class AIAgent:
    """OpenAI Function Calling Agent"""
    
    def __init__(self, max_turns: int = 10):
        """
        Başlat.
        
        Parametreler:
        - max_turns: Maksimum konuşma turu (sonsuz döngüyü engelle)
        """
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o-mini"
        self.max_turns = max_turns
        self.messages = []
        self.turn_count = 0
    
    def reset(self):
        """Konuşmayı sıfırla"""
        self.messages = []
        self.turn_count = 0
    
    def chat(self, user_message: str) -> Dict[str, Any]:
        """
        Kullanıcı mesajını işle ve cevap döndür.
        
        Akış:
        1. User mesajını messages'a ekle
        2. Model'e gönder
        3. Eğer tool call varsa, tool çalıştır ve sonucu modele döndür
        4. Bu işlemi tekrar et (max_turns'e kadar)
        5. Nihai cevapı döndür
        
        Dönen değer:
        {
            'success': bool,
            'response': str,
            'turns': int,
            'tool_calls': List[Dict],
            'error': Optional[str]
        }
        """
        try:
            # 1. User message ekle
            self.reset()
            self.messages.append({
                "role": "user",
                "content": user_message
            })
            
            logger.info(f"User message: {user_message}")
            
            tool_calls_log = []
            
            # 2. Döngü (max_turns'e kadar)
            while self.turn_count < self.max_turns:
                self.turn_count += 1
                logger.info(f"Turn {self.turn_count}/{self.max_turns}")
                
                # Model'e gönder
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    tools=TOOLS,
                    tool_choice="auto",
                )
                
                logger.debug(f"Model response: {response}")
                
                # Response içindeki message'ı messages'a ekle
                assistant_message = response.choices[0].message
                self.messages.append(assistant_message)
                
                # Tool call var mı?
                if not hasattr(assistant_message, 'tool_calls') or not assistant_message.tool_calls:
                    # Yok, döngüyü bitir
                    logger.info("No tool calls, ending conversation")
                    break
                
                # Tool call'ları işle
                has_tool_calls = False
                for tool_call in assistant_message.tool_calls:
                    has_tool_calls = True
                    tool_name = tool_call.function.name
                    tool_input = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"Tool call: {tool_name} with {tool_input}")
                    
                    # Tool çalıştır
                    tool_result = execute_tool(tool_name, tool_input)
                    
                    tool_calls_log.append({
                        'name': tool_name,
                        'input': tool_input,
                        'result': tool_result.to_dict()
                    })
                    
                    # Tool sonucunu messages'a ekle
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result.to_dict())
                    })
                
                # Eğer tool call yoksa döngüyü bitir
                if not has_tool_calls:
                    break
            
            # 3. Nihai cevapı döndür
            final_response = assistant_message.content
            
            logger.info(f"Final response: {final_response}")
            
            return {
                'success': True,
                'response': final_response,
                'turns': self.turn_count,
                'tool_calls': tool_calls_log,
                'error': None
            }
        
        except Exception as e:
            logger.exception(f"Chat error: {e}")
            return {
                'success': False,
                'response': f"İşlem sırasında hata: {str(e)}",
                'turns': self.turn_count,
                'tool_calls': [],
                'error': str(e)
            }


def create_agent() -> AIAgent:
    """Agent factory"""
    return AIAgent()
