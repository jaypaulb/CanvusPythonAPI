# Parent ID Widget Position Bug Fix Investigation

## Problem Description

When a widget's `parent_id` is updated via API call, the widget appears to "move" because its location (`loc`) and scale properties are relative to its parent. This causes unexpected visual changes when reorganizing widget hierarchies.

## Investigation Plan

### Phase 1: Data Collection
1. Create test canvas with notes at specific known locations
2. Record initial widget properties (loc, scale, parent_id)
3. Change parent_id of notes to different parents
4. Record new widget properties after parent_id change
5. Create comprehensive data table of before/after positions

### Phase 2: Analysis
1. Analyze coordinate transformation patterns
2. Identify mathematical relationships between old and new coordinates
3. Document exact behavior and coordinate system
4. Create transformation formulas

### Phase 3: Solution Design
1. Design algorithm to adjust widget properties for new parent
2. Create mathematical model for coordinate conversion
3. Design API wrapper to handle parent_id changes transparently

## Test Scenarios

### Scenario 1: Root to Parent
- Create note at root level (parent_id = null)
- Move to specific parent widget
- Record coordinate changes

### Scenario 2: Parent to Parent
- Create note under parent A
- Move to parent B
- Record coordinate changes

### Scenario 3: Parent to Root
- Create note under parent widget
- Move to root level
- Record coordinate changes

### Scenario 4: Nested Hierarchy
- Create note under parent A
- Move to child of parent A (nested)
- Record coordinate changes

## Data Collection Format

| Test ID | Widget ID | Initial Parent | Final Parent | Initial Loc | Final Loc | Initial Scale | Final Scale | Notes |
|---------|-----------|----------------|--------------|-------------|-----------|---------------|-------------|-------|
| T001    | note_001  | null           | parent_001   | [x1, y1]    | [x2, y2]  | [sx1, sy1]    | [sx2, sy2]  | Root to parent |

## Files

- `test_parent_id_changes.py` - Main investigation script
- `data_collection_results.csv` - Raw test data
- `analysis_results.md` - Analysis of coordinate transformations
- `solution_design.md` - Proposed solution design 