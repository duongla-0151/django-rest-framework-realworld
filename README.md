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
