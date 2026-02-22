"""
Tool tanımları - Function Calling için
"""
import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Any

from django.conf import settings
from .security import (
    validate_workspace_path,
    validate_source_project_path,
    is_path_exists_and_accessible,
    check_duplicate_project
)

logger = logging.getLogger(__name__)


class ToolResult:
    """Tool çkışı standardı"""
    
    def __init__(self, success: bool, message: str, data: Any = None):
        self.success = success
        self.message = message
        self.data = data
    
    def to_dict(self):
        return {
            'success': self.success,
            'message': self.message,
            'data': self.data,
        }


# ==================== TOOL 1: Proje Alma ====================
def pull_project_from_source(project_name: str) -> ToolResult:
    """
    Lokal kaynak klasörden bir projeyi calisma alanina alma araci.
    
    Amaç:
    - Belirlenmiş kaynak klasörden projeyi kopyala
    - Çalışma alanında proje oluştur
    
    Girdi:
    - project_name: Kopyalanacak proje adı
    
    Başarı durumu:
    - Proje başarıyla kopyalandı -> success=True
    - Kaynak yok -> success=False, Kaynak klasör yok hatasını dön
    - Hedef varsa -> success=False, Zaten var uyarısını dön
    - Erişim hatası -> success=False, İzin hatası mesajı dön
    
    Dönen değer:
    - ToolResult(success, message, data)
    """
    try:
        workspace_root = settings.WORKSPACE_DIR
        source_root = settings.SOURCE_PROJECT_DIR
        
        # 1. Workspace kontrol et
        workspace_path = Path(workspace_root)
        if not workspace_path.exists():
            workspace_path.mkdir(parents=True, exist_ok=True)
        
        # 2. Kaynak proje path'i
        source_project = Path(source_root) / project_name
        
        # 3. Kaynak proje kontrol et - var mı?
        if not is_path_exists_and_accessible(str(source_project)):
            return ToolResult(
                success=False,
                message=f"Kaynak proje bulunamadi: {project_name}",
                data={'source_path': str(source_project)}
            )
        
        # 4. Kaynak güvenlik kontrolü
        if not validate_source_project_path(str(source_project), source_root):
            return ToolResult(
                success=False,
                message="Güvenlik hatasi: Izinli kaynak klasor disinda proje.",
                data=None
            )
        
        # 5. Hedef path kontrol et
        target_project = workspace_path / project_name
        
        # Duplicate kontrol
        if check_duplicate_project(project_name, workspace_root):
            return ToolResult(
                success=False,
                message=f"Bu proje zaten calisma alaninda var: {target_project}",
                data={'target_path': str(target_project)}
            )
        
        # 6. Proje kopyala
        shutil.copytree(str(source_project), str(target_project))
        
        logger.info(f"Proje basariyla kopyalandi: {source_project} -> {target_project}")
        
        return ToolResult(
            success=True,
            message=f"Proje basariyla calisma alanina alindi: {project_name}",
            data={'target_path': str(target_project)}
        )
    
    except PermissionError:
        return ToolResult(
            success=False,
            message="Yetki hatasi: Proje kopyalamayi yapmaya yetkiniz yok.",
            data=None
        )
    except Exception as e:
        logger.exception(f"Proje alma hatasi: {e}")
        return ToolResult(
            success=False,
            message=f"Proje alma sirasinda hata: {str(e)[:100]}",
            data=None
        )


# ==================== TOOL 2: Dosya Okuma ====================
def read_file_from_workspace(file_path: str) -> ToolResult:
    """
    Çalışma alanından dosya okuma araci.
    
    Amaç:
    - Workspace içindeki bir dosyayı oku
    - Dosya içeriğini döndür
    
    Girdi:
    - file_path: Okunacak dosyaya göreceli path
    
    Başarı durumu:
    - Dosya başarıyla okundu -> success=True, içerik data'da
    - Dosya yok -> success=False, Olmayan dosya mesaji
    - Path güvenli değil -> success=False, Security mesajı
    - Okuma hatası -> success=False, Hata mesajı
    
    Dönen değer:
    - ToolResult(success, message, data)
    """
    try:
        workspace_root = settings.WORKSPACE_DIR
        
        # 1. Path güvenlik kontrolü
        if not validate_workspace_path(file_path, workspace_root):
            return ToolResult(
                success=False,
                message=f"Guvenlik hatasi: {file_path} calisma alani disinda.",
                data=None
            )
        
        # 2. Dosya var mı kontrol et
        full_path = Path(workspace_root) / file_path
        if not is_path_exists_and_accessible(str(full_path)):
            return ToolResult(
                success=False,
                message=f"Dosya bulunamadi: {file_path}",
                data={'requested_path': str(full_path)}
            )
        
        # 3. Dosyaysa oku
        if not full_path.is_file():
            return ToolResult(
                success=False,
                message=f"Bu bir dosya degil, klasor: {file_path}",
                data=None
            )
        
        # 4. Oku
        content = full_path.read_text(encoding='utf-8')
        
        logger.info(f"Dosya okundu: {file_path}")
        
        return ToolResult(
            success=True,
            message=f"Dosya basariyla okundu: {file_path}",
            data={
                'file_path': str(full_path),
                'content': content,
                'size': len(content)
            }
        )
    
    except UnicodeDecodeError:
        return ToolResult(
            success=False,
            message=f"Dosya teksti okunamadi (ikili format?): {file_path}",
            data=None
        )
    except PermissionError:
        return ToolResult(
            success=False,
            message=f"Yetki hatasi: Dosyayi okumayi yapmaya yetkiniz yok: {file_path}",
            data=None
        )
    except Exception as e:
        logger.exception(f"Dosya okuma hatasi: {e}")
        return ToolResult(
            success=False,
            message=f"Dosya okuma sirasinda hata: {str(e)[:100]}",
            data=None
        )


# ==================== TOOL 3: Dosya Degistirme ====================
def replace_file_content(file_path: str, old_text: str, new_text: str) -> ToolResult:
    """
    Dosya içeriğinde bir metni başka bir metinle değiştirme araci.
    
    Amaç:
    - Workspace içindeki bir dosyada metin değişikliği yap
    - Eski metni yeni metinle değiştir
    
    Girdiler:
    - file_path: Değiştirilecek dosya (göreceli path)
    - old_text: Bulunacak metin
    - new_text: Yerine konulacak metin
    
    Başarı durumu:
    - Değişiklik yapıldı -> success=True, kaç yerden değiştirildiği data'da
    - Dosya yok -> success=False, Olmayan dosya mesaji
    - Metni bulunamadı -> success=False, Metin bulunamadı
    - Path güvenli değil -> success=False, Security mesajı
    
    Dönen değer:
    - ToolResult(success, message, data)
    """
    try:
        workspace_root = settings.WORKSPACE_DIR
        
        # 1. Path güvenlik kontrolü
        if not validate_workspace_path(file_path, workspace_root):
            return ToolResult(
                success=False,
                message=f"Guvenlik hatasi: {file_path} calisma alani disinda.",
                data=None
            )
        
        # 2. Dosya var mı kontrol et
        full_path = Path(workspace_root) / file_path
        if not is_path_exists_and_accessible(str(full_path)):
            return ToolResult(
                success=False,
                message=f"Dosya bulunamadi: {file_path}",
                data={'requested_path': str(full_path)}
            )
        
        # 3. Dosyaysa oku
        if not full_path.is_file():
            return ToolResult(
                success=False,
                message=f"Bu bir dosya degil, klasor: {file_path}",
                data=None
            )
        
        # 4. Dosya içeriğini oku
        content = full_path.read_text(encoding='utf-8')
        
        # 5. Metni Bul ve değiştir
        if old_text not in content:
            return ToolResult(
                success=False,
                message=f"Hedef metin dosyada bulunamadi.",
                data={
                    'file_path': str(full_path),
                    'looking_for': old_text[:100] + '...' if len(old_text) > 100 else old_text
                }
            )
        
        # Kaç yerden değiştirilecek kontrol et
        count = content.count(old_text)
        new_content = content.replace(old_text, new_text)
        
        # 6. Dosyaya yaz
        full_path.write_text(new_content, encoding='utf-8')
        
        logger.info(f"Dosya degistirildi: {file_path} ({count} sayi)")
        
        return ToolResult(
            success=True,
            message=f"Dosya basariyla degistirildi: {file_path} ({count} yer)",
            data={
                'file_path': str(full_path),
                'replacements_made': count
            }
        )
    
    except UnicodeDecodeError:
        return ToolResult(
            success=False,
            message=f"Dosya teksti okunamadi (ikili format?): {file_path}",
            data=None
        )
    except PermissionError:
        return ToolResult(
            success=False,
            message=f"Yetki hatasi: Dosyayi duzenlemeyeyi yapmaya yetkiniz yok: {file_path}",
            data=None
        )
    except Exception as e:
        logger.exception(f"Dosya degistirme hatasi: {e}")
        return ToolResult(
            success=False,
            message=f"Dosya degistirme sirasinda hata: {str(e)[:100]}",
            data=None
        )


# Tool definitions for Function Calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "pull_project_from_source",
            "description": "Lokal kaynak klasorden bir projeyi calisma alanina kopyalar",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_name": {
                        "type": "string",
                        "description": "Kopyalanacak proje klasorununun adi"
                    }
                },
                "required": ["project_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file_from_workspace",
            "description": "Calisma alanindaki bir dosyanin icerigini okur",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Okunacak dosyanin workspace icinde goreli yolu"
                    }
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "replace_file_content",
            "description": "Dosya iceriginde bir metni diger bir metinle degistirir",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Degistirilecek dosyanin workspace icinde goreli yolu"
                    },
                    "old_text": {
                        "type": "string",
                        "description": "Bulunacak metin"
                    },
                    "new_text": {
                        "type": "string",
                        "description": "Yerine konulacak metin"
                    }
                },
                "required": ["file_path", "old_text", "new_text"]
            }
        }
    }
]


def execute_tool(tool_name: str, tool_input: Dict[str, Any]) -> ToolResult:
    """
    Tool'u adı ve parametreleri ile çalıştır.
    
    Dönen değer: ToolResult
    """
    if tool_name == "pull_project_from_source":
        return pull_project_from_source(tool_input.get("project_name", ""))
    elif tool_name == "read_file_from_workspace":
        return read_file_from_workspace(tool_input.get("file_path", ""))
    elif tool_name == "replace_file_content":
        return replace_file_content(
            tool_input.get("file_path", ""),
            tool_input.get("old_text", ""),
            tool_input.get("new_text", "")
        )
    else:
        return ToolResult(
            success=False,
            message=f"Bilinmeyen tool: {tool_name}",
            data=None
        )
