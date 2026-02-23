# Tool: Workspace içinde klasör listeleme
# Amaç: Agent önce "ne var?" diye keşfedebilsin; sonra oku/değiştir kararını versin.

from pathlib import Path

from django.conf import settings

from .path_utils import has_traversal, is_path_safe


def list_files_in_workspace(relative_path: str = "") -> str:
    """
    Workspace içindeki bir klasörün içeriğini listeler (dosya ve alt klasör adları).

    Parametre:
        relative_path: Workspace'e göre klasör yolu. Boş veya "." = workspace kökü.

    Döner:
        Başarı: Her satırda bir öğe; klasörler "ad/" ile, dosyalar "ad" ile.
        Hata: Açıklayıcı hata mesajı (Türkçe).
    """
    if has_traversal(relative_path):
        return "Hata: Güvenlik nedeniyle '..' veya mutlak yol kullanılamaz."

    workspace_dir = Path(settings.WORKSPACE_DIR)
    target = (workspace_dir / relative_path.strip() if relative_path.strip() else workspace_dir).resolve()

    if not is_path_safe(target, workspace_dir.resolve()):
        return "Hata: Yol çalışma alanının dışında olamaz."

    if not target.exists():
        return f"Hata: Klasör bulunamadı: {relative_path or '(workspace kökü)'}"

    if not target.is_dir():
        return f"Hata: Bu bir klasör değil (dosya olabilir): {relative_path}"

    try:
        entries = sorted(target.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        lines = []
        for p in entries:
            name = p.name
            if p.is_dir():
                lines.append(f"{name}/")
            else:
                lines.append(name)
        if not lines:
            return "(boş klasör)"
        return "\n".join(lines)
    except OSError as e:
        return f"Hata: Klasör okunamadı: {e}"
