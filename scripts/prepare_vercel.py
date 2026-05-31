"""Sync frontend assets into public/ before Vercel deploy."""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
PUBLIC = ROOT / "public"

COPY_DIRS = ("css", "js")
COPY_FILES = (
    "index.html",
    "login.html",
    "signup.html",
    "dashboard.html",
    "tasks.html",
    "calendar.html",
    "notes.html",
    "analytics.html",
)


def copy_tree(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            copy_tree(item, target)
        else:
            shutil.copy2(item, target)


def main() -> None:
    PUBLIC.mkdir(exist_ok=True)

    for name in COPY_DIRS:
        src = FRONTEND / name
        dst = PUBLIC / name
        if src.exists():
            copy_tree(src, dst)

    for name in COPY_FILES:
        src = FRONTEND / name
        if src.exists():
            shutil.copy2(src, PUBLIC / name)

    pages_src = FRONTEND / "pages"
    pages_dst = PUBLIC / "pages"
    if pages_src.exists():
        copy_tree(pages_src, pages_dst)

    print("Prepared public/ for Vercel deploy.")


if __name__ == "__main__":
    main()
