# React Developer - STRICT SCHEMA ENFORCEMENT

## 🔴 MANDATORY READING FOR ALL REACT CODE GENERATION

This document defines the **ONLY** schema you are allowed to use when generating React dashboards.
**ANY DEVIATION FROM THIS SCHEMA WILL CAUSE BUGS.**

---

## ✅ CANONICAL DATA CONTEXT SCHEMA

When you receive `data_context`, it will have this EXACT structure:

```typescript
interface DataContext {
  summary: {
    total_sources: number;
    total_files: number;
    total_records: number;
    total_size_bytes: number;
  };

  data_sources: {
    [source_name: string]: {
      name: string;
      file_count: number;
      row_count: number;
      total_size_bytes: number;
      location: string;
      file_list: Array<{ name: string; size_bytes: number }>;
    };
  };

  pipelines: Pipeline[];  // MUST BE PRESENT - guaranteed by PipelineAssemblyTool
}
```

---

## ✅ CANONICAL PIPELINE SCHEMA

```typescript
interface Pipeline {
  id: string;
  name: string;
  display_name: string;
  status: string;

  metrics: {
    file_count: number;      // CANONICAL
    record_count: number;    // CANONICAL (NOT total_records)
    data_size: number;       // CANONICAL (in bytes)
  };

  stages: Stage[];           // REQUIRED - populated by PipelineAssemblyTool
  files: Array<{             // REQUIRED
    name: string;
    size_bytes: number;
  }>;
}
```

---

## ✅ CANONICAL STAGE SCHEMA

```typescript
interface Stage {
  name: string;                                          // Stage name (e.g., "downloads", "parsed")
  file_count: number;                                    // Number of files in this stage
  total_size_bytes: number;                              // Total size of files in bytes
  status: "complete" | "empty" | "missing" | "unknown";  // Health status
}
```

---

## ❌ FORBIDDEN FIELDS (DO NOT USE THESE!)

### In Pipeline:
- ❌ `metrics.total_records` (use `metrics.record_count`)
- ❌ `metrics.records` (use `metrics.record_count`)
- ❌ `pipeline.children`
- ❌ `pipeline.subdirectories`
- ❌ `pipeline.records`
- ❌ `pipeline.total_files`
- ❌ `pipeline.total_records`

### In Stage:
- ❌ Any field not listed in canonical schema above

---

## 🔥 CRITICAL RULES FOR REACT GENERATION

### 1. **ALWAYS** Check for Pipelines

Before rendering, validate that pipelines exist:

```typescript
if (!data?.pipelines || !Array.isArray(data.pipelines)) {
  throw new Error("Missing pipelines in DataContext. Ensure PipelineAssemblyTool ran.");
}
```

### 2. **NEVER** Use Forbidden Fields

If you see `pipeline.metrics.total_records`, you **MUST** use `pipeline.metrics.record_count` instead.

### 3. **ALWAYS** Use Canonical Field Names

```typescript
// ✅ CORRECT
{pipeline.metrics.file_count}
{pipeline.metrics.record_count}
{pipeline.metrics.data_size}

// ❌ WRONG
{pipeline.metrics.total_files}
{pipeline.metrics.total_records}
{pipeline.total_files}
```

### 4. **ALWAYS** Access Stages from Pipeline

```typescript
// ✅ CORRECT
{pipeline.stages.map(stage => (
  <div key={stage.name}>
    {stage.name}: {stage.status} ({stage.file_count} files)
  </div>
))}

// ❌ WRONG - Do NOT infer or hallucinate stages
const stages = ["downloads", "parsed", "qc", "analyzed"]; // NEVER DO THIS
```

### 5. **ALWAYS** Compute Health from Stage Status

```typescript
// ✅ CORRECT - Read from stage.status
const completeStages = pipeline.stages.filter(s => s.status === "complete").length;
const totalStages = pipeline.stages.length;
const health = totalStages > 0 ? (completeStages / totalStages) * 100 : 0;

// ❌ WRONG - Do NOT hallucinate health calculation
const health = pipeline.health || 100; // NEVER DO THIS
```

---

## 📊 UI COMPONENT REQUIREMENTS

### DataSources Sidebar

**MUST display:**
- Source name
- `file_count` (from data_sources)
- `row_count` (from data_sources)

```tsx
// ✅ CORRECT
<div className="source-card">
  <h3>{source.name}</h3>
  <p>Files: {source.file_count}</p>
  <p>Records: {source.row_count}</p>
</div>
```

### Pipelines Table

**MUST display:**
- Pipeline name
- `metrics.file_count`
- `metrics.record_count`
- `metrics.data_size`
- Computed health from `stages`

```tsx
// ✅ CORRECT
<table>
  <thead>
    <tr>
      <th>Pipeline</th>
      <th>Files</th>
      <th>Records</th>
      <th>Size</th>
      <th>Health</th>
    </tr>
  </thead>
  <tbody>
    {data.pipelines.map(pipeline => (
      <tr key={pipeline.id}>
        <td>{pipeline.display_name}</td>
        <td>{pipeline.metrics.file_count}</td>
        <td>{pipeline.metrics.record_count.toLocaleString()}</td>
        <td>{formatBytes(pipeline.metrics.data_size)}</td>
        <td>{computeHealth(pipeline.stages)}%</td>
      </tr>
    ))}
  </tbody>
</table>
```

### PipelineHealthCard

**MUST display:**
- Stage breakdown from `pipeline.stages`
- Status badges for each stage
- File counts per stage

```tsx
// ✅ CORRECT
<div className="health-card">
  <h3>Pipeline Health</h3>
  {pipeline.stages.map(stage => (
    <div key={stage.name} className="stage-row">
      <span>{stage.name}</span>
      <span className={`badge badge-${stage.status}`}>
        {stage.status}
      </span>
      <span>{stage.file_count} files</span>
    </div>
  ))}
</div>

// ❌ WRONG - Do NOT invent stages
const stages = [
  { name: "raw", status: "complete" },
  { name: "cleaned", status: "complete" },
  { name: "enriched", status: "empty" }
]; // NEVER DO THIS
```

### File Explorer

**MUST use:**
- `pipeline.files` array

```tsx
// ✅ CORRECT
<div className="file-explorer">
  {pipeline.files.map(file => (
    <div key={file.name} className="file-item">
      <span>{file.name}</span>
      <span>{formatBytes(file.size_bytes)}</span>
    </div>
  ))}
</div>

// ❌ WRONG - Do NOT build fake tree structures
const fakeTree = buildTreeFromNothing(); // NEVER DO THIS
```

---

## 🚨 ERROR PREVENTION CHECKLIST

Before generating React code, verify:

- [ ] I am reading from `data.pipelines` (not `data.datasets`, `data.sources`, etc.)
- [ ] I am using `pipeline.metrics.record_count` (not `total_records`)
- [ ] I am using `pipeline.metrics.file_count` (not `total_files`)
- [ ] I am reading `pipeline.stages` from data (not inventing them)
- [ ] I am computing health from `stage.status` (not hallucinating)
- [ ] I am NOT using any forbidden fields
- [ ] I have error guards for missing pipelines
- [ ] I am NOT creating mock data or placeholders

---

## 🎯 FINAL VALIDATION

Every React component you generate MUST pass these tests:

1. **Does it use `data.pipelines`?** ✅ Yes / ❌ No
2. **Does it use `metrics.record_count`?** ✅ Yes / ❌ No
3. **Does it read `pipeline.stages` from data?** ✅ Yes / ❌ No
4. **Does it avoid forbidden fields?** ✅ Yes / ❌ No
5. **Does it have error guards?** ✅ Yes / ❌ No

**If ANY answer is ❌, the code will FAIL in production.**

---

## 📖 Summary: The 3 Golden Rules

1. **Use ONLY canonical fields** (record_count, file_count, data_size)
2. **Read stages from data** (never invent or hallucinate)
3. **Validate pipelines exist** (add error guards)

**Follow these rules religiously and you will generate correct dashboards every time.**
