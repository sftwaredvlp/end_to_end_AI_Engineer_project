# Güvenlik: Tüm tool'lar sadece izin verilen klasörler içinde çalışsın.
# Bu dosya "path güvenli mi?" kontrolünü tek yerde toplar.

from pathlib import Path


def is_path_safe(resolved_path: Path, allowed_base: Path) -> bool:
    """
    Bu path, izin verilen base klasörünün İÇİNDE mi?
    Örnek: allowed_base = /proje/workspace
            resolved_path = /proje/workspace/abc  -> True
            resolved_path = /proje/workspace/../etc -> False (dışarı çıkmış)
    """
    try:
        resolved_path.resolve().relative_to(allowed_base.resolve())
        return True
    except ValueError:
        return False


def has_traversal(name: str) -> bool:
    """
    İsimde ".." veya mutlak yol var mı? Varsa üst dizine çıkma denemesi sayarız.
    """
    return ".." in name or name.startswith("/")
