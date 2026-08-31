"""
Article 值物件：任何 parser（markdown、未來可能的其他格式）的標準輸出，
也是 Client.create_article/update_article 除了 dict 之外的另一種輸入。
"""
from dataclasses import dataclass, field


@dataclass
class Article:
    subject: str
    description: str
    tags: list[str] = field(default_factory=list)
    category_id: str | None = None
    article_id: str | None = None

    # 以下三個都是「發表後自動回填」的 metadata，不是人工先寫的內容欄位；
    # 純粹是本地追蹤用，不會送給 iThome（to_dict() 不包含這三個）。
    # frontmatter 欄位名沿用 Jekyll/Hugo 一類 SSG 的慣例。
    date: str | None = None
    """最後一次成功發表/更新的時間（ISO 8601 字串）"""
    permalink: str | None = None
    """發表成功後的實際文章網址（從 article_id 組出來）"""
    author: str | None = None
    """發表/更新時實際使用的 iThome 帳號"""

    draft: bool = False
    """
    標記這篇還不該自動發表（例如寫到一半）。不是 metadata，是人工控制欄位，
    自動發文流程要主動檢查、跳過 draft 為 True 的檔案；成功發表後應該把它
    改回 False（呼叫端負責，這個物件本身不會自動改）。
    """

    def to_dict(self) -> dict:
        """
        轉成 create_article/update_article 原本吃的 dict 格式。
        category_id/article_id 是 None 就不放進去，讓呼叫端自己決定
        （通常是外面另外指定要建立還是更新）。date/permalink/author
        是本地 metadata，iThome 不需要，不放進去。
        """
        data: dict = {
            "subject": self.subject,
            "description": self.description,
            "tags": self.tags,
        }
        if self.category_id is not None:
            data["category_id"] = self.category_id
        if self.article_id is not None:
            data["article_id"] = self.article_id
        return data
