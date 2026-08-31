"""
把標準格式的 markdown 檔案解析成 Article 物件，反之也能把 Article 的
metadata（date/permalink/author）寫回 markdown 的 frontmatter。

標準格式，欄位名對齊常見 SSG（Jekyll/Hugo）慣例：

    ---
    title: 標題
    tags: [PHP, AI, Legacy]
    draft: false
    date: 2026-08-31T15:00:00+08:00
    permalink: https://ithelp.ithome.com.tw/articles/10406474
    author: recca0120
    ---
    內文...

只有 title 是必要欄位。tags 選填（flow style）。draft 選填，預設
False（不是草稿），人工控制用——寫成 true 代表「還沒要自動發表」，
呼叫端（例如自動發文流程）要自己檢查並跳過，這個模組不會主動略過任何
東西。date/permalink/author 都是發表後才會有值的 metadata，不需要
人工先寫，是自動回填的。
"""
import re
from pathlib import Path

from .article import Article

_SCALAR_FIELDS = ("title", "date", "permalink", "author")


def parse_markdown(text: str) -> Article:
    frontmatter, body = _split_frontmatter(text)
    fields = _parse_scalar_fields(frontmatter)

    if "title" not in fields:
        raise ValueError("frontmatter 缺少必要的 title 欄位")

    return Article(
        subject=fields["title"],
        description=body.lstrip("\n"),
        tags=_parse_tags(frontmatter),
        date=fields.get("date"),
        permalink=fields.get("permalink"),
        author=fields.get("author"),
        draft=_parse_draft(frontmatter),
    )


def parse_markdown_file(path: str | Path) -> Article:
    text = Path(path).read_text(encoding="utf-8")
    return parse_markdown(text)


def update_frontmatter(text: str, **updates: str) -> str:
    """
    把 updates 裡的欄位寫進（已存在就覆蓋、不存在就新增）frontmatter，
    回傳新的完整檔案內容。不動其他既有欄位，也不動 body。

    典型用途：發表/更新文章成功後，把 date/permalink/author 回填進
    原始 markdown 檔案。

    Args:
        text: 原始檔案內容，必須已經有 frontmatter
        **updates: 要新增或覆蓋的欄位，值一律當成單行純量字串處理

    Raises:
        ValueError: 檔案沒有 frontmatter
    """
    frontmatter, body = _split_frontmatter(text)

    remaining = dict(updates)
    new_lines = []
    for line in frontmatter.splitlines():
        m = re.match(r"^(\w+):", line)
        if m and m.group(1) in remaining:
            key = m.group(1)
            new_lines.append(f"{key}: {remaining.pop(key)}")
        else:
            new_lines.append(line)
    for key, value in remaining.items():
        new_lines.append(f"{key}: {value}")

    new_frontmatter = "\n".join(new_lines)
    return f"---\n{new_frontmatter}\n---\n{body}"


def _split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("markdown 必須以 frontmatter 開頭（--- 開始的一段），需要包含 title")

    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("frontmatter 沒有結尾的 ---")

    return text[4:end], text[end + 5:]


def _parse_scalar_fields(frontmatter: str) -> dict:
    fields = {}
    for key in _SCALAR_FIELDS:
        m = re.search(rf"^{key}:\s*(.+)$", frontmatter, flags=re.MULTILINE)
        if m:
            fields[key] = m.group(1).strip().strip("'\"")
    return fields


def _parse_tags(frontmatter: str) -> list[str]:
    m = re.search(r"^tags:\s*\[(.*?)\]\s*$", frontmatter, flags=re.MULTILINE)
    if not m:
        return []
    return [t.strip().strip("'\"") for t in m.group(1).split(",") if t.strip()]


def _parse_draft(frontmatter: str) -> bool:
    m = re.search(r"^draft:\s*(\S+)\s*$", frontmatter, flags=re.MULTILINE)
    if not m:
        return False
    return m.group(1).strip().lower() == "true"
