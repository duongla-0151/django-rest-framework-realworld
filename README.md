# Django REST Framework – RealWorld API (Phases 1–3)

This project implements the initial backend for a RealWorld-style API using **Django 5.x**, **Django REST Framework**, and **MySQL**, following an **Agentic Coding** workflow.

---

## Phase 1 — Project Setup & Core Models

**Goal:**
Establish a stable project structure and database schema.

**Key Tasks:**

* Initialize Django project and apps (`users`, `articles`, `tags`).
* Configure MySQL via environment variables.
* Define core models:

  * User
  * Article
  * Comment
  * Tag
* Set up relationships:

  * Article → author (nullable)
  * Article → tags (ManyToMany)
  * Comment → author (nullable)
  * Comment → article
* Add timestamps to all models.
* Review domain assumptions before applying migrations.
* Generate and apply database migrations.

**Result:**
A clean, validated database schema with no business logic.

---

## Phase 2 — Serialization & Domain Logic

**Goal:**
Expose models through serializers with correct validation and domain behavior.

**Key Tasks:**

* Implement serializers for all core models.
* Enforce domain rules:

  * `password` is required on user creation, optional on update.
* Implement article slug generation.
* Handle RealWorld API conventions:

  * Accept `tagList` (camelCase) in requests.
  * Map to internal tag handling (snake_case, ManyToMany).
* Explicitly implement:

  * Tag creation and association during article creation.
  * Author assignment from `request.user`.
* Optimize queries using `select_related` and `prefetch_related`.

**Result:**
Serializers enforce domain rules and match the RealWorld API specification.

---

## Phase 3 — API Views & Manual Validation

**Goal:**
Complete API endpoints and validate behavior manually.

**Key Tasks:**

* Implement API views and routes:

  * `/api/users`
  * `/api/articles`
  * `/api/tags`
* Start development server.
* Manually test APIs using Postman or curl:

  * User creation and update
  * Article creation with tags
  * Tag listing
  * Author association
* Fix domain issues discovered during testing.
* Defer automated tests until API contracts stabilize.

**Result:**
Fully functional API endpoints validated through manual testing.

---

## Agentic Coding Principles

* Work in explicit phases.
* Review and confirm domain decisions before mutations.
* Do not allow agents to redefine domain rules.
* Validate manually before automation.
* Add automated tests only after API contracts are stable.

---

## Phase 4 — Authentication & Permissions

**Goal:**
Introduce authentication and authorization while preserving existing API contracts.

**Key Decisions:**

* Use **JWT-based authentication**.
* Keep API behavior explicit; no implicit magic.
* Authentication is required for:

  * Creating articles
  * Updating or deleting owned resources
* Public read access remains unchanged.

**Key Tasks:**

* Integrate JWT authentication (e.g. `djangorestframework-simplejwt`).
* Extend User serialization to include:

  * token
  * email
  * username
* Implement auth endpoints:

  * `POST /api/users/login`
  * `GET /api/user` (current authenticated user)
* Protect endpoints using DRF permissions:

  * `IsAuthenticated`
  * Custom permission for resource ownership (author-only edit/delete).
* Ensure anonymous requests:

  * can read articles and tags
  * cannot create or modify protected resources.

**Manual Validation:**

* Login returns a valid JWT token.
* Authenticated requests include `Authorization: Token <jwt>`.
* Unauthorized access returns `401` or `403` as appropriate.

**Outcome:**
Secure APIs with explicit authentication and ownership rules.

---

## Phase 5 — Integration Testing & Stability

**Goal:**
Lock down API behavior with meaningful automated tests after contracts stabilize.

**Testing Strategy:**

* Prefer **integration tests** over unit tests.
* Test APIs at HTTP level using DRF test client.
* Avoid over-mocking internal logic.

**Key Tasks:**

* Set up test database configuration.
* Write integration tests for:

  * User registration and login
  * Authenticated article creation
  * Permission enforcement (author vs non-author)
  * Tag creation via article submission
* Cover both:

  * happy paths
  * critical failure cases (401/403/400)

**What NOT to Test:**

* Django internals
* DRF serializers in isolation
* Implementation details

**Outcome:**
A stable, regression-safe API with confidence in core behaviors.

---

# Phase 6 — Permissions, Filtering, Pagination & Throttling

**Goal:**
Introduce production-grade API controls: **fine-grained permissions, flexible filtering, pagination, and request throttling**, while preserving RealWorld API contracts.

---

## Key Objectives

* Enforce **role-based and object-level permissions**
* Provide **query filtering & ordering**
* Implement **API pagination**
* Add **rate limiting (throttling)** for abuse protection
* Maintain **explicit, predictable API behavior**

---

## Technical Scope

### 1. Permissions

**Goal:**
Control access at both **view-level** and **object-level**.

**Applied Permission Classes:**

* `AllowAny` – Public read-only endpoints
* `IsAuthenticated` – Authenticated-only endpoints
* `IsAdminUser` – Admin-only operations
* Custom permissions:

  * Author-only modification of articles
  * Author-only deletion of comments
  * User-specific operations on profile & favorites

**Rules:**

* Anonymous users:

  * Can read articles, tags, and public profiles
  * Cannot create, modify, or favorite content
* Authenticated users:

  * Can create articles, comments, favorites
  * Can modify only their own resources
* Admin users:

  * May bypass ownership checks when required

---

### 2. Filtering & Ordering

**Goal:**
Enable flexible querying of API resources using URL parameters.

**Tools:**

* `django-filter`
* DRF filter backends:

  * `DjangoFilterBackend`
  * `OrderingFilter`
  * `SearchFilter`

**Implemented Filters (RealWorld spec):**

```
GET /api/articles?tag=foo
GET /api/articles?author=bar
GET /api/articles?favorited=john
```

**Ordering:**

```
GET /api/articles?ordering=-created_at
```

**Implementation:**

* Install `django-filter`
* Add filter backends in DRF settings
* Define filtersets for:

  * Articles
  * Comments (if exposed)
  * Profiles (optional)

---

### 3. Pagination

**Goal:**
Ensure scalable API responses for large datasets.

**Pagination Strategies:**

* `LimitOffsetPagination` (RealWorld-compatible)
* Optional support for:

  * `PageNumberPagination`

**Supported Queries:**

```
GET /api/articles?limit=5&offset=10
```

**Rules:**

* Set global default pagination
* Allow per-view override when needed
* Return metadata:

  * total count
  * next / previous links

---

### 4. Throttling (Rate Limiting)

**Goal:**
Protect API from abuse and accidental overuse.

**Throttle Classes:**

* `AnonRateThrottle`
* `UserRateThrottle`
* Custom throttles (if needed)

**Recommended Limits:**

| Scope          | Limit                |
| -------------- | -------------------- |
| Anonymous      | 100 requests / hour  |
| Authenticated  | 1000 requests / hour |
| Login endpoint | 10 attempts / minute |

**Rules:**

* Login endpoints should be **strictly throttled**
* Read-heavy endpoints should be **lenient**
* Write endpoints should be **moderately restricted**

---

## RealWorld API Enhancements

### Required Endpoints

```
GET  /api/articles?tag=foo&author=bar
GET  /api/articles/feed         (requires login)
POST /api/articles/:slug/favorite   (requires login)
GET  /api/articles?limit=5&offset=10
```

---

### Behavior Rules

| Endpoint                          | Permission                |
| --------------------------------- | ------------------------- |
| GET /api/articles                 | AllowAny                  |
| GET /api/articles/feed            | IsAuthenticated           |
| POST /api/articles                | IsAuthenticated           |
| PUT /api/articles/:slug           | IsAuthenticated + IsOwner |
| DELETE /api/articles/:slug        | IsAuthenticated + IsOwner |
| POST /api/articles/:slug/favorite | IsAuthenticated           |

---

## Implementation Steps

1. Add `django-filter` and configure filter backends.
2. Define filtersets for articles.
3. Implement pagination settings.
4. Add throttling configuration.
5. Implement feed endpoint.
6. Implement article favorite/unfavorite endpoints.
7. Apply permission classes per-view.
8. Perform manual API validation.
9. Add integration tests for:

   * filtering
   * pagination
   * permissions
   * throttling behavior

---

## Manual Validation Checklist

* `/api/articles?tag=django` returns only matching articles
* `/api/articles?author=john` returns only john’s articles
* `/api/articles?limit=3&offset=5` paginates correctly
* `/api/articles/feed` requires authentication
* Unauthorized favorite → `401`
* Excessive requests → `429 Too Many Requests`

---

## Agentic Execution Rules

* Implement **one concern at a time**:

  * permissions → filtering → pagination → throttling
* After each step:

  * run manual tests
  * confirm behavior
* Add automated tests only **after behavior is validated**
* Never mix refactors with behavior changes in one step

---

## Outcome

A **production-grade REST API** with:

* Secure permission control
* Powerful query filtering
* Scalable pagination
* Abuse-resistant throttling

---

## Agentic Testing Principles

* Do not write tests until API contracts are stable.
* Tests validate **decisions**, not experiments.
* Human validation precedes automation.
* Agents generate tests only under explicit instruction.

---
