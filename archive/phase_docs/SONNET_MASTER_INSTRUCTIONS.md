# 🔵 SONNET MASTER INSTRUCTIONS (FINAL VERSION)

### **UI Generation + Pipeline Assembly + Stage Detection + Health Scoring**

This is the **single source of truth** for correct pipeline assembly, stage detection, and React dashboard generation.

**Use this specification when:**
- Generating React dashboards
- Assembling pipelines
- Detecting pipeline stages
- Computing health scores
- Preventing schema drift and hallucinations

---

# 🟦 SECTION 1 — STRICT SCHEMA (DO NOT DEVIATE)

Sonnet must **ONLY** use the following schema.
Never infer, invent, rename, or restructure anything unless explicitly listed.

## ✓ DataContext Schema

```typescript
DataContext {
  summary: {
    total_sources: number,
    total_files: number,
    total_records: number,
    total_size_bytes: number
  },

  data_sources: {
    [source_name: string]: {
        name: string,
        file_count: number,
        row_count: number,
        total_size_bytes: number,
        location: string,
        file_list: Array<{ name: string, size_bytes: number }>
    }
  },

  pipelines: Pipeline[]         // MUST BE PRESENT when React Developer runs
}
```

---

## ✓ Pipeline Schema

```typescript
Pipeline {
  id: string,
  name: string,
  display_name: string,
  status: string,

  metrics: {
    file_count: number,
    record_count: number,
    data_size: number
  },

  stages: Stage[],
  files: Array<{ name: string, size_bytes: number }>
}
```

---

## ✓ Stage Schema

```typescript
Stage {
  name: string,
  file_count: number,
  total_size_bytes: number,
  status: "complete" | "empty" | "missing" | "unknown"
}
```

---

# 🔥 ABSOLUTE RULES

Sonnet must **NOT** use:

* `metrics.total_records` (use `metrics.record_count`)
* `pipeline.children`
* `pipeline.subdirectories`
* `pipeline.records`
* `pipeline.total_files`
* `pipeline.total_records`
* invented nesting (no tree structures unless provided)
* invented fields of ANY KIND

**This is mandatory.**

---

# 🟦 SECTION 2 — PIPELINE ASSEMBLY RULES (MANDATORY)

The Orchestrator must run these steps in order:

### **1. Discovery** → produces `data_sources`

### **2. Filtering**

### **3. Shaping**

### **3.5 Pipeline Assembly (REQUIRED)**

### **4. Context Assembly**

### **5. UX + React**

Sonnet must **never** call React Developer **before pipeline assembly is completed**.

---

# 🟦 SECTION 3 — PIPELINE ASSEMBLY TOOL (REQUIRED)

Sonnet must implement **exactly this tool**, with no changes:

### **PipelineAssemblyTool Responsibilities**

1. Create `pipelines[]` from `data_sources`
2. Detect stages from raw filesystem
3. Score stage health
4. Compute:
   * file_count
   * record_count
   * data_size
5. Ensure every pipeline has:
   * `stages: []` (minimum)
   * `files: []` (minimum)

### **Rules for filesystem detection**

For a dataset located at:

```
data/raw/<source_name>/<dataset_name>/
```

Every **directory** under `<dataset_name>` is a pipeline stage.

Example:

```
Chemical_data/
    downloads/
    extracted/
    parsed/
    metadata.json         # ignored
```

→ stages = downloads, extracted, parsed

### **Stage Scoring Rules**

```
if folder does not exist → status="missing"
if folder exists but has 0 files → status="empty"
if folder exists and has >=1 files → status="complete"
if exception → status="unknown"
```

File count = number of files
Size = sum of file sizes

These must be returned in the `Stage` object.

---

# 🟦 SECTION 4 — ORCHESTRATOR REQUIREMENTS

Sonnet must ensure:

### Before UX + React agents run:

```python
data_context["pipelines"] = pipeline_assembly_tool.run(data_context["data_sources"])
```

If `pipelines` is missing, frontend will break —
Sonnet must guarantee it exists.

---

# 🟦 SECTION 5 — REACT DEVELOPER RULES (MANDATORY)

Sonnet must:

### ✓ Use ONLY canonical fields

```typescript
pipeline.metrics.record_count
pipeline.metrics.file_count
pipeline.stages
pipeline.files
```

### ❌ Must NEVER use:

```typescript
pipeline.metrics.total_records
pipeline.metrics.records
pipeline.total_files
pipeline.total_records
pipeline.children
pipeline.subdirectories
```

### ✓ UI must always pull from:

```typescript
data.pipelines[]
```

### ✓ The DataSources sidebar must show:

* file_count
* record_count

### ✓ PipelineHealthCard must read:

```typescript
pipeline.stages
```

and compute health from stage statuses.

---

# 🟦 SECTION 6 — FILE EXPLORER RULES

Sonnet must:

* Use `pipeline.files` for file explorer
* Not infer nested folders
* Not build fake tree structures unless given

**Only use what exists.**

---

# 🟦 SECTION 7 — ERROR GUARDS

React Developer must include guardrails:

```typescript
if (!data?.pipelines || !Array.isArray(data.pipelines)) {
    throw new Error("Missing pipelines in DataContext. Ensure PipelineAssemblyTool ran.");
}
```

This prevents "0 stages" bugs.

---

# 🟦 SECTION 8 — OUTPUT FORMAT RULES

Sonnet must output React code using:

* React + TypeScript
* Tailwind
* Functional components
* No mock data
* No auto-generated fake fields

---

# 🟦 SECTION 9 — WHAT SONNET MUST NEVER DO

Sonnet must never:

* Infer or hallucinate stages
* Invent "parsed → qc → analyzed → harmonized" unless they exist
* Create synthetic file structures
* Renumber pipeline IDs
* Collapse multiple datasets into a single pipeline unless instructed
* Change schema keys
* Guess names of folders
* Change pipeline object structure

---

# 🟦 SECTION 10 — SUCCESS CRITERIA

The pipeline UI is considered correct when:

### **1.** Data Sources sidebar shows correct file_count + record_count

### **2.** Main table shows correct records

### **3.** Pipeline health card shows accurate stage statuses

### **4.** Stages reflect real filesystem folders

### **5.** No invented fields appear in the React code

### **6.** `pipelines[]` is populated before React Developer runs

---

# 🟢 IMPLEMENTATION STATUS

## ✅ Completed:

- [x] PipelineAssemblyTool created in `src/agents/tools/pipeline_assembly_tool.py`
- [x] PipelineAssemblyTool added to OrchestratorTools bundle
- [x] Orchestrator updated to call pipeline assembly (Step 2/7)
- [x] React Developer schema rules documented
- [x] Master specification documented

## 📋 Next Steps:

1. **Update UI Orchestrator** to initialize PipelineAssemblyTool in tools bundle
2. **Inject schema rules** into React Developer agent's system prompt
3. **Test with real data** to verify pipeline assembly works correctly
4. **Validate stage detection** works for all pipeline types
5. **Run full generation** to ensure React code uses canonical fields

---

# 📖 Quick Reference Card

## For Orchestrator:

```python
# MANDATORY: Call this BEFORE UX/React
pipelines = tools.pipeline_assembly.assemble_pipelines(data_context)
data_context = tools.pipeline_assembly.update_data_context_with_pipelines(
    data_context, pipelines
)
```

## For React Developer:

```typescript
// ALWAYS validate pipelines exist
if (!data?.pipelines) throw new Error("Missing pipelines");

// ALWAYS use canonical fields
pipeline.metrics.record_count  // ✅
pipeline.metrics.file_count    // ✅
pipeline.stages                // ✅

// NEVER use forbidden fields
pipeline.metrics.total_records // ❌
pipeline.total_files           // ❌
```

## For Stage Health:

```typescript
// ALWAYS compute from stage.status
const health = pipeline.stages.filter(s => s.status === "complete").length
             / pipeline.stages.length * 100;

// NEVER hallucinate
const health = 100; // ❌
```

---

# 🎯 The 3 Golden Rules

1. **Use ONLY canonical fields** (record_count, file_count, data_size)
2. **Read stages from data** (never invent or hallucinate)
3. **Validate pipelines exist** (add error guards)

**Follow these rules religiously and you will generate correct dashboards every time.**

---

# 📞 Support

If you encounter schema drift or hallucinated fields:

1. Check that PipelineAssemblyTool ran before UX/React
2. Verify data_context contains `pipelines[]`
3. Validate React code uses canonical field names
4. Review this specification for correct schema

**This document is the single source of truth.**
