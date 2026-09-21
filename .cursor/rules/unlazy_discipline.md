# Completion Discipline & Verification Rule (Unlazy Standard)

Every agent executing in this workspace must adhere to the **Unlazy Completion Standard**:

## 1. Zero Placeholders or Truncation
- Never leave `# TODO`, `// implement later`, `/* ... */`, or ellipsis comments in generated code.
- Provide complete, robust, drop-in replacement code.

## 2. Pre-Execution Acceptance Gates
- For tasks with multiple steps or complex logic, define the acceptance criteria before touching code.
- Every gate must have an empirical check (e.g. unit test, curl/http probe, exit code verification).

## 3. Mandatory Evidence Before "Done"
- Never claim a task or bug is resolved without running terminal verification and inspecting output.
- Output snippets proving success must accompany any completion statement.
