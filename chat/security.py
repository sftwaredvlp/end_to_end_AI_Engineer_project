"""
Güvenlik kuralları ve path validation
"""
import os
from pathlib import Path


def validate_workspace_path(file_path: str, workspace_root: str) -> bool:
    """
    Çalışma alanı içinde güvenli path kontrolü yapar.
    
    Girdiler:
    - file_path: Kontrol edilecek dosya yolu
    - workspace_root: Çalışma alanının root klasörü
    
    Dönen değer:
    - True: Path güvenli
    - False: Path güvenli değil (ÜstDizine çıkış vs)
    
    Kurallar:
    1. Yalnızca workspace_root içindeki dosyalara erişim
    2. ../ ile ust dizine cikis denemesine karsi kontrol
    3. Symlink kontrolleri
    """
    try:
        workspace_path = Path(workspace_root).resolve()
        target_path = Path(file_path).resolve()
        
        # Path'in workspace'in altında olduğunu kontrol et
        target_path.relative_to(workspace_path)
        return True
    except (ValueError, OSError):
        # Path workspace disi
        return False


def validate_source_project_path(project_path: str, allowed_source: str) -> bool:
    """
    Lokal kaynak klasöre erişim kontrolü.
    
    Girdiler:
    - project_path: Projenin path'i
    - allowed_source: İzinli kaynak klasör
    
    Dönen değer:
    - True: Kaynak klasör içinde
    - False: Orası dışı
    """
    try:
        source_path = Path(allowed_source).resolve()
        target_path = Path(project_path).resolve()
        
        # Kaynağın altında olduğunu kontrol et
        target_path.relative_to(source_path)
        return True
    except (ValueError, OSError):
        return False


def is_path_exists_and_accessible(file_path: str) -> bool:
    """
    Dosya veya klasörün var olup erişilebilir olduğunu kontrol et.
    
    Dönen değer:
    - True: Var ve erişilebilir
    - False: Yok veya erişilemez
    """
    try:
        path = Path(file_path)
        return path.exists() and (path.is_file() or path.is_dir())
    except (OSError, PermissionError):
        return False


def check_duplicate_project(project_name: str, workspace_root: str) -> bool:
    """
    Aynı adlı projenin daha önceden alınıp alınmadığını kontrol et.
    
    Dönen değer:
    - True: Zaten var
    - False: Yeni projektir
    """
    project_path = Path(workspace_root) / project_name
    return project_path.exists()
