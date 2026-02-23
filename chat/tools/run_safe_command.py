# Tool: Workspace içinde güvenli test ve lint çalıştırma
# Sadece beyaz listeye alınmış komutlar; workspace dışına çıkılmaz, timeout ve çıktı sınırı var.

import subprocess
from pathlib import Path

from django.conf import settings

from .path_utils import has_traversal, is_path_safe

WORKSPACE_DIR = Path(settings.WORKSPACE_DIR)
TIMEOUT_TESTS = 60
TIMEOUT_LINTER = 30
MAX_OUTPUT_CHARS = 32_000


def _run(cmd: list[str], cwd: Path, timeout_sec: int) -> str:
    """Komutu cwd'de çalıştırır; stdout+stderr birleşik döner, en fazla MAX_OUTPUT_CHARS."""
    try:
        r = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            encoding="utf-8",
            errors="replace",
        )
        out = (r.stdout or "") + (r.stderr or "")
        if len(out) > MAX_OUTPUT_CHARS:
            out = out[:MAX_OUTPUT_CHARS] + "\n... (çıktı kısaltıldı)"
        if r.returncode != 0:
            out = f"[çıkış kodu: {r.returncode}]\n{out}"
        return out.strip() or "(boş çıktı)"
    except subprocess.TimeoutExpired:
        return f"Hata: İşlem {timeout_sec} saniye içinde tamamlanmadı (zaman aşımı)."
    except FileNotFoundError:
        return "Hata: Komut bulunamadı (örn. pytest veya linter yüklü değil)."
    except Exception as e:
        return f"Hata: {e}"


def run_tests_in_workspace(relative_path: str = "") -> str:
    """
    Workspace içindeki belirtilen klasörde pytest çalıştırır.
    relative_path boşsa workspace kökünde çalışır.
    """
    if has_traversal(relative_path):
        return "Hata: Güvenlik nedeniyle '..' veya mutlak yol kullanılamaz."

    target = (WORKSPACE_DIR / relative_path.strip()).resolve() if relative_path.strip() else WORKSPACE_DIR.resolve()

    if not is_path_safe(target, WORKSPACE_DIR.resolve()):
        return "Hata: Yol çalışma alanının dışında olamaz."

    if not target.exists() or not target.is_dir():
        return f"Hata: Klasör bulunamadı veya geçersiz: {relative_path or '(workspace kökü)'}"

    cmd = ["python", "-m", "pytest", "--tb=short", "-q", "."]
    return _run(cmd, target, TIMEOUT_TESTS)


def run_linter_in_workspace(relative_path: str, linter: str = "py_compile") -> str:
    """
    Workspace içindeki dosya veya klasörde linter çalıştırır.
    linter: "py_compile" (sadece sözdizimi), "pylint", "flake8"
    """
    if has_traversal(relative_path):
        return "Hata: Güvenlik nedeniyle '..' veya mutlak yol kullanılamaz."

    workspace_resolved = WORKSPACE_DIR.resolve()
    target = (WORKSPACE_DIR / relative_path.strip()).resolve()

    if not is_path_safe(target, workspace_resolved):
        return "Hata: Yol çalışma alanının dışında olamaz."

    if not target.exists():
        return f"Hata: Dosya veya klasör bulunamadı: {relative_path}"

    allowed = ("py_compile", "pylint", "flake8")
    if linter not in allowed:
        return f"Hata: Linter şunlardan biri olmalı: {', '.join(allowed)}"

    if linter == "py_compile":
        if not target.is_file():
            return "Hata: py_compile için bir .py dosya yolu verin."
        cmd = ["python", "-m", "py_compile", str(target)]
        cwd = workspace_resolved
    else:
        # pylint veya flake8: dosya veya klasör
        cmd = ["python", "-m", linter, str(target)]
        cwd = workspace_resolved

    return _run(cmd, cwd, TIMEOUT_LINTER)
