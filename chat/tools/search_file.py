# Tool: Workspace içinde metin ara (grep benzeri)
# Amaç: Agent "şu metin nerede geçiyor?" diye arayıp ilgili dosyayı okuyup değiştirebilsin.

import re
from pathlib import Path

from django.conf import settings

from .path_utils import has_traversal, is_path_safe

# Arama sınırları (güvenlik ve performans)
MAX_FILE_SIZE = 100_000  # byte
MAX_MATCHES = 50
MAX_DEPTH = 5
TEXT_EXTENSIONS = {".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".yml", ".yaml", ".xml", ".csv", ".env", ""}


def _is_text_file(path: Path) -> bool:
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    return path.suffix == "" and path.name.startswith(".")


def search_in_workspace(pattern: str, relative_path: str = "") -> str:
    """
    Workspace içinde (belirtilen klasör altında) metin arar; eşleşen satırları döndürür.

    Parametreler:
        pattern: Aranacak metin (düz metin; büyük/küçük harf duyarlı değil).
        relative_path: Aramanın yapılacağı klasör. Boş = tüm workspace.

    Döner:
        Başarı: Her eşleşme "dosya_yolu:satır_no: satır_içeriği" formatında.
        Hata: Açıklayıcı hata mesajı (Türkçe).
    """
    if has_traversal(relative_path):
        return "Hata: Güvenlik nedeniyle '..' veya mutlak yol kullanılamaz."

    workspace_dir = Path(settings.WORKSPACE_DIR)
    search_root = (workspace_dir / relative_path.strip() if relative_path.strip() else workspace_dir).resolve()

    if not is_path_safe(search_root, workspace_dir.resolve()):
        return "Hata: Yol çalışma alanının dışında olamaz."

    if search_root.exists() and not search_root.is_dir():
        return "Hata: Belirtilen yol bir klasör değil."

    if not pattern.strip():
        return "Hata: Aranacak metin (pattern) boş olamaz."

    try:
        regex = re.compile(re.escape(pattern.strip()), re.IGNORECASE)
    except re.error:
        return "Hata: Geçersiz arama ifadesi."

    matches = []
    root_resolved = workspace_dir.resolve()

    def scan_dir(directory: Path, depth: int) -> None:
        if depth > MAX_DEPTH or len(matches) >= MAX_MATCHES:
            return
        try:
            for p in directory.iterdir():
                if len(matches) >= MAX_MATCHES:
                    return
                if p.is_dir():
                    scan_dir(p, depth + 1)
                    continue
                if not _is_text_file(p):
                    continue
                try:
                    if p.stat().st_size > MAX_FILE_SIZE:
                        continue
                    text = p.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                try:
                    rel = p.resolve().relative_to(root_resolved)
                except ValueError:
                    continue
                rel_str = str(rel).replace("\\", "/")
                for i, line in enumerate(text.splitlines(), 1):
                    if regex.search(line):
                        matches.append(f"{rel_str}:{i}: {line.strip()[:200]}")
                        if len(matches) >= MAX_MATCHES:
                            return
        except OSError:
            pass

    if search_root.exists():
        scan_dir(search_root, 0)
    else:
        return f"Hata: Klasör bulunamadı: {relative_path or '(workspace kökü)'}"

    if not matches:
        return f"Eşleşme bulunamadı: '{pattern.strip()}'"
    return "\n".join(matches)
