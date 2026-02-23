# Tool 1: Proje alma
# Amacı: İzin verilen kaynak klasöründen bir projeyi, çalışma alanına kopyalamak.
# Böylece LLM "şu projeyi al" dediğinde güvenli tek bir yere kopyalanır.

import shutil
from pathlib import Path

from django.conf import settings

from .path_utils import has_traversal, is_path_safe


def copy_project_to_workspace(source_folder_name: str, target_folder_name: str) -> str:
    """
    Kaynak klasörü (source_projects içinden) alıp workspace içinde yeni bir
    klasör adıyla kopyalar.

    Parametreler:
        source_folder_name: Kaynak projenin adı (örn. "deneme_proje")
        target_folder_name: Workspace içinde oluşacak klasör adı (örn. "calisma1")

    Döner:
        Başarı: "Proje X, Y klasörüne kopyalandı."
        Hata: Açıklayıcı hata mesajı (Türkçe)
    """
    # 1) Güvenlik: İsimlerde ".." veya "/" olmasın (dışarı çıkma denemesi)
    if has_traversal(source_folder_name) or has_traversal(target_folder_name):
        return "Hata: Güvenlik nedeniyle '..' veya mutlak yol kullanılamaz."

    workspace_dir = Path(settings.WORKSPACE_DIR)
    source_base = Path(settings.SOURCE_PROJECTS_DIR)
    source_path = source_base / source_folder_name
    target_path = workspace_dir / target_folder_name

    # 2) Kaynak gerçekten izin verilen klasörün içinde mi?
    if not is_path_safe(source_path.resolve(), source_base.resolve()):
        return "Hata: Kaynak klasör izin verilen alanın dışında."

    # 3) Hedef her zaman workspace içinde olsun
    if not is_path_safe(target_path.resolve(), workspace_dir.resolve()):
        return "Hata: Hedef klasör çalışma alanının dışında olamaz."

    # 4) Kaynak var mı?
    if not source_path.exists():
        return f"Hata: Kaynak klasör bulunamadı: {source_folder_name}"

    if not source_path.is_dir():
        return f"Hata: Kaynak bir klasör değil: {source_folder_name}"

    # 5) Hedef zaten var mı? (İkinci kez aynı yere kopyalamayı engelliyoruz)
    if target_path.exists():
        return f"Hata: Hedef klasör zaten var: {target_folder_name}. Farklı bir isim seçin veya önce silin."

    # 6) Kopyala
    try:
        shutil.copytree(source_path, target_path)
        return f"Proje '{source_folder_name}', '{target_folder_name}' klasörüne kopyalandı."
    except OSError as e:
        return f"Hata (kopyalama): {e}"
