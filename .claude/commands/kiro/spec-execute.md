---
description: Execute spec tasks using TDD methodology with kent-beck-tdd-developer
allowed-tools: Task, Read, Glob, LS, Bash, TodoWrite
argument-hint: <task-numbers> | --all | --help | [feature-name]
---

# Execute Spec Tasks with TDD

Execute implementation tasks from spec using Kent Beck's Test-Driven Development methodology.

## Arguments: $ARGUMENTS

## Current Specs
Available specs: !`ls .kiro/specs/ 2>/dev/null || echo "No specs found"`

## Instructions

### Help Mode (--help)
If arguments contain "--help", show usage:
```
/kiro:spec-execute <task-numbers> | --all | [feature-name]

Examples:
  /kiro:spec-execute 1              # Execute task 1 from latest spec
  /kiro:spec-execute 1,2,3          # Execute tasks 1, 2, 3
  /kiro:spec-execute --all          # Execute all pending tasks
  /kiro:spec-execute face-mosaic-app 1  # Execute task 1 from specific spec
```

### Task Execution
1. **Determine spec**: Use provided feature name or find latest spec with completed tasks
2. **Parse task numbers**: Extract from arguments (support: "1", "1,2,3", "--all")
3. **Execute with TDD**: Use kent-beck-tdd-developer for implementation

### For Each Task
Use the Task tool with kent-beck-tdd-developer:

**Prompt for kent-beck-tdd-developer:**
```
Implement spec task using strict TDD methodology.

**Context Files:**
- Requirements: @.kiro/specs/[spec-name]/requirements.md
- Design: @.kiro/specs/[spec-name]/design.md  
- Tasks: @.kiro/specs/[spec-name]/tasks.md

**Task to Execute:**
[Extract specific task content from tasks.md based on task number]

**TDD Instructions:**
1. RED: Write failing test first
2. GREEN: Minimum code to pass test
3. REFACTOR: Improve while tests pass
4. Update task checkbox to [x] when complete

Execute ONLY the specified task. Follow Kent Beck's methodology strictly.
```

## Implementation Logic

1. **Parse Arguments**:
   - If contains "--help": Show help and exit
   - If contains "--all": Execute all unchecked tasks
   - If starts with feature name: Extract feature name and task numbers
   - Otherwise: Use latest spec and parse task numbers

2. **Validate**:
   - Spec exists and has tasks.md
   - Task numbers are valid
   - Tasks are not already completed

3. **Execute**:
   - Call kent-beck-tdd-developer for each task
   - Provide full spec context
   - Focus on single task implementation