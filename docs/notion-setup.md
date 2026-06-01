# Notion setup

MeetMind writes each meeting to a row in a Notion **database**. Set it up once.

## 1. Create the integration (get the token)

1. Go to <https://www.notion.so/my-integrations> → **New integration**.
2. Name it (e.g. `MeetMind`), select your workspace, **Submit**.
3. Copy the **Internal Integration Secret** → this is `NOTION_TOKEN`.

## 2. Create the database

1. In Notion, create a new **full-page database** (type `/database` → *Database - Full page*). Name it e.g. `Meeting Notes`.
2. Set up exactly these three columns (the backend writes to them by name):

   | Column      | Type          | Notes                          |
   |-------------|---------------|--------------------------------|
   | `Name`      | Title         | Default first column. Keep name `Name`. |
   | `Date`      | Date          | Meeting date.                  |
   | `Attendees` | Multi-select  | Filled from extracted attendees. |

## 3. Connect the integration to the database

Open the database → top-right **⋯** menu → **Connections** / **Add connections** → pick your `MeetMind` integration → **Confirm**.

> Skipping this causes `404 Object not found` from the API.

## 4. Copy the database ID

Open the database as a full page and look at the URL:

```
https://www.notion.so/<workspace>/<DATABASE_ID>?v=<view_id>
```

The 32-character hex string before `?` is `NOTION_DATABASE_ID`.

## 5. Put them in backend/.env

```env
NOTION_TOKEN=ntn_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Page layout produced

- **📌 Meeting Summary** — heading + paragraph
- **✅ To-do List** — one `👤 <person>` heading per attendee; under each, a checkbox
  per task with child blocks for `📅 deadline · 📑 Slide N` and the verbatim quote.
