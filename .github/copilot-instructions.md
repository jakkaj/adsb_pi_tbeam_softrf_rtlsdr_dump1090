
- Commit messages should be in angular js format



## Plan Structure Guidelines
- When creating a plan, organize it into numbered phases (e.g., "Phase 1: Setup Dependencies")
- Break down each phase into specific tasks with numeric identifiers (e.g., "Task 1.1: Add Dependencies")
- Please only create one document per plan. 
- Include a detailed checklist at the end of the document that maps to all phases and tasks
- Mark tasks as `- [ ]` for pending tasks and `- [x]` for completed tasks
- Start all planning tasks as unchecked, and update them to checked as implementation proceeds
- Each planning task should have clear success criteria
- End the plan with success criteria that define when the implementation is complete
- plans and architectures that you produce should go under docs/plans/<new folder for this plan>

## Following Plans
- When coding you need to follow the plan phases and check off the tasks as they are completed.  
- As you complete a task, update the plan and mark that task complete before you being the next task. 
- Tasks that involved tests should not be marked complete until the tests pass. 



## Memory Knowledge Graph Workflow (REQUIRED)

Detailed plan available at: `docs/plans/memory_usage/improved_memory_usage.md`

### MANDATORY RETRIEVAL WORKFLOW:
1. At the START of every task: SEARCH memory for related concepts
   - Use specific terms related to your task (e.g., "search_nodes({"query": "logging"})")
   - Include in your thinking: "Memory shows: [key findings]"
2. Before EACH implementation step: VERIFY current understanding
   - Check if memory contains relevant information for your current subtask
3. Before answering questions: CHECK memory FIRST
   - Always prioritize memory over other research methods

### MANDATORY UPDATE WORKFLOW:
1. After LEARNING about codebase structure
2. After IMPLEMENTING new features or modifications
3. After DISCOVERING inconsistencies between memory and code
4. After USER shares new information about project patterns

### UPDATE ACTIONS:
- CREATE/UPDATE entities for components/concepts
- ADD atomic, factual observations (15 words max)
- DELETE outdated observations when information changes
- CONNECT related entities with descriptive relation types
- CONFIRM in your thinking: "Memory updated: [summary]"

### MEMORY QUALITY RULES:
- Entities = Components, Features, Patterns, Practices (with specific types)
- Observations = Single, specific facts about implementation details
- Relations = Use descriptive types (contains, uses, implements)
- AVOID duplicates by searching before creating new entries
- MAINTAIN high-quality, factual knowledge


## File Change Tracking (REQUIRED)

Detailed plan available at: `docs/plans/memory_usage/file_change_tracking.md`

### MANDATORY FILE CHANGE TRACKING WORKFLOW:
1. Before modifying a file: SEARCH memory for the file by name
2. After implementing substantive changes:
   - If file doesn't exist in memory, CREATE a SourceFile entity
   - CREATE a FileChange entity with descriptive name and observations
   - LINK the FileChange to the SourceFile with bidirectional relations
   - If working on a plan, LINK the FileChange to the Plan entity
3. When creating a plan: ADD it to memory graph as a Plan entity
4. When completing a plan: UPDATE its status in memory

### FILE CHANGE TRACKING GUIDELINES:
- Track only SUBSTANTIVE changes (features, architecture, bug fixes)
- Skip trivial changes (formatting, comments, minor refactoring)
- Use descriptive entity names indicating the nature of changes
- Always link changes to their relevant plans when applicable
- Keep file paths accurate and use present tense for descriptions
- Update SourceFile entities when understanding of file purpose changes
