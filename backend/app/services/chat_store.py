"""In-memory thread/item store for ChatKit."""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any

from chatkit.store import NotFoundError, Store
from chatkit.types import Attachment, Page, ThreadItem, ThreadMetadata

logger = logging.getLogger(__name__)


class InMemoryStore(Store[dict[str, Any]]):
    """Simple in-memory Store for the workshop. Not suitable for production."""

    def __init__(self) -> None:
        self.threads: dict[str, ThreadMetadata] = {}
        self.items: dict[str, list[ThreadItem]] = defaultdict(list)

    async def load_thread(self, thread_id: str, context: dict[str, Any]) -> ThreadMetadata:
        if thread_id not in self.threads:
            raise NotFoundError(f"Thread {thread_id} not found")
        return self.threads[thread_id]

    async def save_thread(self, thread: ThreadMetadata, context: dict[str, Any]) -> None:
        self.threads[thread.id] = thread

    async def load_threads(
        self, limit: int, after: str | None, order: str, context: dict[str, Any]
    ) -> Page[ThreadMetadata]:
        return self._paginate(
            list(self.threads.values()),
            after,
            limit,
            order,
            sort_key=lambda t: t.created_at or datetime.min,
            cursor_key=lambda t: t.id,
        )

    async def load_thread_items(
        self,
        thread_id: str,
        after: str | None,
        limit: int,
        order: str,
        context: dict[str, Any],
    ) -> Page[ThreadItem]:
        return self._paginate(
            list(self.items.get(thread_id, [])),
            after,
            limit,
            order,
            sort_key=lambda i: getattr(i, "created_at", datetime.min),
            cursor_key=lambda i: i.id,
        )

    async def add_thread_item(self, thread_id: str, item: ThreadItem, context: dict[str, Any]) -> None:
        self.items[thread_id].append(item)

    async def save_item(self, thread_id: str, item: ThreadItem, context: dict[str, Any]) -> None:
        items = self.items[thread_id]
        for idx, existing in enumerate(items):
            if existing.id == item.id:
                items[idx] = item
                return
        items.append(item)

    async def load_item(self, thread_id: str, item_id: str, context: dict[str, Any]) -> ThreadItem:
        for item in self.items.get(thread_id, []):
            if item.id == item_id:
                return item
        raise NotFoundError(f"Item {item_id} not found in thread {thread_id}")

    async def delete_thread(self, thread_id: str, context: dict[str, Any]) -> None:
        self.threads.pop(thread_id, None)
        self.items.pop(thread_id, None)

    async def delete_thread_item(self, thread_id: str, item_id: str, context: dict[str, Any]) -> None:
        self.items[thread_id] = [i for i in self.items.get(thread_id, []) if i.id != item_id]

    async def save_attachment(self, attachment: Attachment, context: dict[str, Any]) -> None:
        raise NotImplementedError("Attachments not supported in this workshop demo.")

    async def load_attachment(self, attachment_id: str, context: dict[str, Any]) -> Attachment:
        raise NotImplementedError("Attachments not supported in this workshop demo.")

    async def delete_attachment(self, attachment_id: str, context: dict[str, Any]) -> None:
        raise NotImplementedError("Attachments not supported in this workshop demo.")

    @staticmethod
    def _paginate(rows, after, limit, order, sort_key, cursor_key):
        sorted_rows = sorted(rows, key=sort_key, reverse=(order == "desc"))
        start = 0
        if after:
            for idx, row in enumerate(sorted_rows):
                if cursor_key(row) == after:
                    start = idx + 1
                    break
        data = sorted_rows[start : start + limit]
        has_more = start + limit < len(sorted_rows)
        next_after = cursor_key(data[-1]) if has_more and data else None
        return Page(data=data, has_more=has_more, after=next_after)
