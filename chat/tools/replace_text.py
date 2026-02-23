# Tool 3: Metin değiştirme
# Amacı: Workspace içindeki bir dosyada belirtilen metni bulup başka bir metinle değiştirmek.
# LLM "şu dosyada X'i Y yap" dediğinde güvenli şekilde sadece workspace içinde değişiklik yapar.

from pathlib import Path

from django.conf import settings

from .path_utils import has_traversal, is_path_safe


def replace_text_in_file(relative_path: str, old_text: str, new_text: str) -> str:
    """
    Workspace içindeki bir dosyada 'old_text' geçen yerleri 'new_text' ile değiştirir.
    Tüm eşleşmeler değiştirilir.

    Parametreler:
        relative_path: Workspace'e göre dosya yolu (örn. "calisma2/merhaba.txt")
        old_text: Aranacak / değiştirilecek metin
        new_text: Yerine yazılacak metin

    Döner:
        Başarı: "Dosyada N yerde '...' metni '...' ile değiştirildi."
        Hata: Açıklayıcı hata mesajı (Türkçe)
    """
    if has_traversal(relative_path):
        return "Hata: Güvenlik nedeniyle '..' veya mutlak yol kullanılamaz."

    workspace_dir = Path(settings.WORKSPACE_DIR)
    file_path = (workspace_dir / relative_path).resolve()

    if not is_path_safe(file_path, workspace_dir.resolve()):
        return "Hata: Dosya yolu çalışma alanının dışında olamaz."

    if not file_path.exists():
        return f"Hata: Dosya bulunamadı: {relative_path}"

    if not file_path.is_file():
        return f"Hata: Bu bir dosya değil (klasör olabilir): {relative_path}"

    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"Hata: Dosya metin olarak okunamadı (UTF-8 değil): {relative_path}"

    if old_text not in content:
        return f"Hata: Aranan metin dosyada bulunamadı: '{old_text[:50]}{'...' if len(old_text) > 50 else ''}'"

    count = content.count(old_text)
    new_content = content.replace(old_text, new_text)
    file_path.write_text(new_content, encoding="utf-8")

    return f"Dosyada {count} yerde '{old_text[:30]}{'...' if len(old_text) > 30 else ''}' metni değiştirildi."
