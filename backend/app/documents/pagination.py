from dataclasses import dataclass
from app.documents.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.documents.errors import DocumentValidationError


@dataclass(frozen=True)
class PageWindow:
    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


def page_window(page: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> PageWindow:
    if page < 1:
        raise DocumentValidationError("Page must be at least 1")
    if page_size < 1 or page_size > MAX_PAGE_SIZE:
        raise DocumentValidationError("Page size is outside the allowed range", details={"max_page_size": MAX_PAGE_SIZE})
    return PageWindow(page=page, page_size=page_size)


def page_count(total: int, page_size: int) -> int:
    if total <= 0:
        return 0
    return (total + page_size - 1) // page_size
