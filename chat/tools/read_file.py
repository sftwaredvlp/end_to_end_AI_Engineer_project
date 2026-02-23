# Tool 2: Dosya okuma
# Amacı: Çalışma alanı (workspace) içindeki bir metin dosyasının içeriğini döndürmek.
# LLM "şu dosyayı oku" dediğinde sadece workspace içindeki dosyalara izin veririz.

from pathlib import Path

from django.conf import settings

from .path_utils import has_traversal, is_path_safe


def read_file_in_workspace(relative_path: str) -> str:
    """
    Workspace içindeki bir dosyayı okur, içeriğini metin olarak döndürür.

    Parametre:
        relative_path: Workspace'e göre dosya yolu (örn. "calisma2/merhaba.txt")

    Döner:
        Başarı: Dosyanın metin içeriği
        Hata: Açıklayıcı hata mesajı (Türkçe)
    """
    if has_traversal(relative_path):
        return "Hata: Güvenlik nedeniyle '..' veya mutlak yol kullanılamaz."

    workspace_dir = Path(settings.WORKSPACE_DIR)
    # Path birleştirirken normalize eder; sonra güvenlik kontrolü
    file_path = (workspace_dir / relative_path).resolve()

    if not is_path_safe(file_path, workspace_dir.resolve()):
        return "Hata: Dosya yolu çalışma alanının dışında olamaz."

    if not file_path.exists():
        return f"Hata: Dosya bulunamadı: {relative_path}"

    if not file_path.is_file():
        return f"Hata: Bu bir dosya değil (klasör olabilir): {relative_path}"

    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"Hata: Dosya metin olarak okunamadı (UTF-8 değil): {relative_path}"
