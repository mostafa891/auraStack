# Database Architecture

This document details the database schemas, optimization strategies, and data retention patterns within AuraStack.

---

## 🔑 1. UUID Primary Keys
To prevent sequential ID enumeration (which leads to IDOR/BOLA security vulnerabilities), all tables exposed to the API use **UUIDv4** as their primary keys instead of auto-incrementing integers.

*Example implementation:*
```python
import uuid
from django.db import models

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
```
*   **Security Outcome:** A malicious actor cannot guess user or workspace records by incrementing IDs (e.g., `workspace/1` -> `workspace/2`).

---

## 🗑️ 2. Soft Delete Pattern
Critical business data (such as workspaces, memberships, and payment history) is never permanently deleted from the database. Instead, we use a Soft Delete pattern.

*   **SoftDeleteMixin:** Adds a `deleted_at` timestamp.
*   **Custom Managers:** Overrides default queryset filters to hide deleted items by default, while allowing administrators to query them if needed (`objects.all()` vs `objects.all_with_deleted()`).

```python
class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return self.update(deleted_at=timezone.now())

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)
```

---

## ⚡ 3. Indexes & Query Optimization
Indexes are configured for all foreign key lookups and fields queried frequently:
*   **Workspaces & Memberships:** Indexes on `workspace_id`, `user_id`, and `role` to speed up active permission checks.
*   **Users:** Unique index on `email` (lowercased) to ensure high-performance login queries.
*   **Subscriptions:** Index on `subscription_id` to quickly match webhook payloads.

---

## 🔒 4. Database Transactions & Concurrency
We enforce database transactions on all state-mutating actions (like payment processing or invitations) using Django’s `transaction.atomic()`.

### Row Locking (`select_for_update`)
To prevent double-billing or race conditions when receiving webhooks concurrently, we lock the target row inside the database transaction:
```python
from django.db import transaction

with transaction.atomic():
    subscription = Subscription.objects.select_for_update().get(id=sub_id)
    # Perform calculations and database writes safely...
```
*   **Outcome:** Multiple parallel requests targeting the same subscription are queued sequentially at the database engine level, avoiding state corruption.
