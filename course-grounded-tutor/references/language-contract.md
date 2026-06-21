# Language Contract

## Reply Language

Set `reply_language` once at course setup:

- If the user wrote a meaningful message, use that message's language.
- If the user only uploaded materials, use the dominant language of the course materials.
- If neither can be determined, ask the user to choose.

After `reply_language` is set, do not change it unless the user explicitly requests a durable language change.

Explicit examples:

- "From now on, answer in English."
- "以后都用中文讲。"
- "Switch the teaching language to Japanese."

Non-explicit examples:

- The user asks a question in another language.
- The user uses first-language phrasing to check their understanding.
- The user asks for a translation of one sentence or term.
- The user quotes an exam question in another language.

## Note Language

Set `note_language` separately:

- Default to `reply_language`.
- Change only when the user explicitly asks for notes in another language.
- Changing note language does not automatically change reply language.
- Changing reply language does not rewrite existing notes unless the user asks.

Explicit examples:

- "整理英文笔记。"
- "Make the notes in Chinese but keep teaching in English."
- "以后笔记用日文。"

## Stable Terminology

Write the main text in the locked language, but preserve course terms that students must recognize in exams. On first use, include both the localized term and course term when useful:

```text
standard error
标准误 (standard error)
```

Formula symbols, variable names, function names, software commands, and labels from course materials do not translate.

## State Format

Store both contracts in `course.yml`:

```yaml
reply_language:
  value: en
  source: first_user_message
  locked: true
  change_rule: explicit_user_request_only
note_language:
  value: zh-CN
  source: explicit_user_request
  locked: true
  change_rule: explicit_user_request_only
```

