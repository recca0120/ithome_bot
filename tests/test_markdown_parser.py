"""
測試 markdown_parser：把 markdown 文字解析成 Article 物件
純邏輯測試，不需要瀏覽器

標準格式，frontmatter 欄位對齊常見 SSG（Jekyll/Hugo）慣例：

    ---
    title: Day 01：標題
    date: 2026-08-31T15:00:00+08:00
    tags: [PHP, AI, Legacy]
    permalink: https://ithelp.ithome.com.tw/articles/10406474
    author: recca0120
    ---
    內文...

title 是唯一必要欄位；tags/date/permalink/author 都選填。
date/permalink/author 是發表後自動回填的 metadata，不需要人工先寫。
"""
import pytest

from ithome_bot.article import Article
from ithome_bot.markdown_parser import parse_markdown, update_frontmatter


def test_parses_title_and_tags_from_frontmatter():
    text = "---\ntags: [PHP, AI, Legacy]\ntitle: Day 01：標題\n---\n內文第一段\n\n內文第二段"

    article = parse_markdown(text)

    assert isinstance(article, Article)
    assert article.subject == "Day 01：標題"
    assert article.description == "內文第一段\n\n內文第二段"
    assert article.tags == ["PHP", "AI", "Legacy"]


def test_title_can_come_before_tags_in_frontmatter():
    text = "---\ntitle: 標題\ntags: [PHP]\n---\n內文"

    article = parse_markdown(text)

    assert article.subject == "標題"
    assert article.tags == ["PHP"]


def test_tags_are_optional():
    text = "---\ntitle: 標題\n---\n內文"

    article = parse_markdown(text)

    assert article.subject == "標題"
    assert article.tags == []


def test_frontmatter_tags_can_be_quoted():
    text = '---\ntitle: 標題\ntags: ["PHP", \'AI\']\n---\n內文'

    article = parse_markdown(text)

    assert article.tags == ["PHP", "AI"]


def test_title_value_can_be_quoted():
    text = '---\ntitle: "Day 01：標題"\n---\n內文'

    article = parse_markdown(text)

    assert article.subject == "Day 01：標題"


def test_raises_without_frontmatter():
    text = "# 標題\n\n內文，沒有 frontmatter"

    with pytest.raises(ValueError):
        parse_markdown(text)


def test_raises_when_frontmatter_missing_title():
    text = "---\ntags: [PHP]\n---\n內文"

    with pytest.raises(ValueError):
        parse_markdown(text)


def test_raises_when_frontmatter_not_closed():
    text = "---\ntitle: 標題\n內文（沒有結尾的 ---）"

    with pytest.raises(ValueError):
        parse_markdown(text)


def test_body_leading_blank_lines_are_stripped():
    text = "---\ntitle: 標題\n---\n\n\n內文前面有多餘空行"

    article = parse_markdown(text)

    assert article.description == "內文前面有多餘空行"


@pytest.mark.parametrize("field", ["date", "permalink", "author"])
def test_optional_metadata_fields_default_to_none(field):
    text = "---\ntitle: 標題\n---\n內文"

    article = parse_markdown(text)

    assert getattr(article, field) is None


def test_draft_defaults_to_false_when_absent():
    text = "---\ntitle: 標題\n---\n內文"

    article = parse_markdown(text)

    assert article.draft is False


@pytest.mark.parametrize("value,expected", [("true", True), ("false", False), ("True", True), ("False", False)])
def test_parses_draft_boolean(value, expected):
    text = f"---\ntitle: 標題\ndraft: {value}\n---\n內文"

    article = parse_markdown(text)

    assert article.draft is expected


def test_parses_date_permalink_author_when_present():
    text = (
        "---\n"
        "title: 標題\n"
        "date: 2026-08-31T15:00:00+08:00\n"
        "permalink: https://ithelp.ithome.com.tw/articles/10406474\n"
        "author: recca0120\n"
        "---\n內文"
    )

    article = parse_markdown(text)

    assert article.date == "2026-08-31T15:00:00+08:00"
    assert article.permalink == "https://ithelp.ithome.com.tw/articles/10406474"
    assert article.author == "recca0120"


class TestUpdateFrontmatter:
    """
    update_frontmatter(text, **fields) 把指定欄位寫進（或更新）frontmatter，
    回傳新的完整檔案內容字串。只動 frontmatter 裡指定的欄位，
    其他欄位跟 body 都不動。
    """

    def test_adds_fields_when_not_present(self):
        text = "---\ntitle: 標題\ntags: [PHP]\n---\n內文"

        new_text = update_frontmatter(text, date="2026-08-31T15:00:00+08:00", author="recca0120")

        article = parse_markdown(new_text)
        assert article.date == "2026-08-31T15:00:00+08:00"
        assert article.author == "recca0120"
        # 其他欄位跟 body 都不該被動到
        assert article.subject == "標題"
        assert article.tags == ["PHP"]
        assert article.description == "內文"

    def test_overwrites_existing_field(self):
        text = "---\ntitle: 標題\ndate: 2026-08-30T00:00:00+08:00\n---\n內文"

        new_text = update_frontmatter(text, date="2026-08-31T15:00:00+08:00")

        article = parse_markdown(new_text)
        assert article.date == "2026-08-31T15:00:00+08:00"

    def test_raises_without_frontmatter(self):
        with pytest.raises(ValueError):
            update_frontmatter("內文，沒有 frontmatter", date="2026-08-31T15:00:00+08:00")

    def test_can_flip_draft_to_false(self):
        text = "---\ntitle: 標題\ndraft: true\n---\n內文"

        new_text = update_frontmatter(text, draft="false")

        article = parse_markdown(new_text)
        assert article.draft is False
