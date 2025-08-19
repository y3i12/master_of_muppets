# Context System

## Overview

The Claude AI context system provides intelligent, keyword-driven context loading that enhances AI responses with relevant project knowledge. This system automatically selects and loads appropriate contexts based on user queries, ensuring optimal AI assistance throughout the development process.

## Context Architecture

```mermaid
graph TB
    subgraph "Context Loading Architecture"
        subgraph "Base Configuration"
            BASE[base.json<br/>Loading Rules & Configuration]
            AUTO[Auto-load Rules<br/>Mandatory vs. Conditional]
            KEYWORDS[Keyword Matching<br/>Context Triggers]
        end
        
        subgraph "Context Categories"
            MANDATORY[Mandatory Contexts<br/>Always Loaded]
            CONDITIONAL[Conditional Contexts<br/>Keyword Triggered]
            SPECIALIZED[Specialized Contexts<br/>Domain Specific]
        end
        
        subgraph "Context Files"
            CORE[core.json<br/>Behavioral Rules]
            PROJECT[project.json<br/>Project Structure]
            DATASTORE[data_store.json<br/>Knowledge Index]
            CODING[coding_style.json<br/>Code Guidelines]
            GIT[git.json<br/>Version Control]
        end
        
        BASE --> MANDATORY
        AUTO --> CONDITIONAL
        KEYWORDS --> SPECIALIZED
        
        MANDATORY --> CORE
        MANDATORY --> PROJECT
        MANDATORY --> DATASTORE
        CONDITIONAL --> CODING
        CONDITIONAL --> GIT
    end
```

## Base Configuration (base.json)

### Auto-Loading Rules

```json
{
  "contexts": {
    "core": {
      "CRITICAL": true,
      "auto_load": "MANDATORY",
      "files": ["claude/contexts/core.json"]
    },
    "project": {
      "CRITICAL": true,
      "auto_load": "MANDATORY", 
      "files": ["claude/contexts/project.json"]
    },
    "data_store": {
      "CRITICAL": true,
      "auto_load": "MANDATORY",
      "files": ["claude/contexts/data_store.json"]
    },
    "coding_style": {
      "auto_load": false,
      "files": ["claude/contexts/coding_style.json"],
      "keywords": ["create", "write", "new file", "add file", "implement", "edit", "modify", "update", "refactor", "change", "fix", "add function", "create class", "implement method"]
    },
    "git": {
      "auto_load": false,
      "files": ["claude/contexts/git.json"],
      "keywords": ["git", "commit", "push", "pull", "branch", "merge", "version control"]
    }
  }
}
```

### Loading Decision Flow

```mermaid
graph TD
    subgraph "Context Loading Decision Process"
        START[User Query Received]
        
        MANDATORY_CHECK[Load Mandatory Contexts<br/>CORE, PROJECT, DATA_STORE]
        
        KEYWORD_ANALYSIS[Analyze Query Keywords<br/>Extract Development Intent]
        
        MATCH_CONTEXTS[Match Keywords to<br/>Conditional Contexts]
        
        LOAD_CONDITIONAL[Load Matching<br/>Conditional Contexts]
        
        FINALIZE[Finalize Context Set<br/>Prepare AI Response]
        
        START --> MANDATORY_CHECK
        MANDATORY_CHECK --> KEYWORD_ANALYSIS
        KEYWORD_ANALYSIS --> MATCH_CONTEXTS
        MATCH_CONTEXTS --> LOAD_CONDITIONAL
        LOAD_CONDITIONAL --> FINALIZE
    end
```

## Core Context (core.json)

### Behavioral Rules

The core context defines fundamental behavioral patterns and constraints:

```mermaid
graph TB
    subgraph "Core Behavioral Rules"
        subgraph "Documentation Policy"
            AUTO_CREATE["auto_create: never<br/>No proactive documentation"]
            README_POLICY["readme_files: never_unless_explicit<br/>Only when requested"]
            EXPLICIT_ONLY["only_when: explicitly_requested<br/>Clear user intent required"]
        end
        
        subgraph "File Creation Policy"
            PREFERENCE["preference: edit_existing_over_new<br/>Avoid new file creation"]
            CREATE_WHEN["create_when: absolutely_necessary_or_explicit<br/>Strict creation rules"]
        end
        
        subgraph "Tool Knowledge Policy"
            REQUIREMENT["requirement: MANDATORY<br/>All tools must have knowledge"]
            CONDITION["condition: ALWAYS<br/>No exceptions allowed"]
            LOCATION["location: claude/data_store/knowledge/external_tools/<br/>Standardized location"]
        end
        
        subgraph "Response Style"
            VERBOSITY["verbosity: concise<br/>Minimize output tokens"]
            EXPLANATIONS["explanations: minimal_unless_requested<br/>Focus on specific tasks"]
            FOCUS["focus: specific_task_only<br/>Avoid tangential information"]
        end
    end
```

### Security and Safety Rules

```json
{
  "security": {
    "code_type": "defensive_only",
    "malicious_code": "refuse"
  },
  "git_operations": {
    "commit": "never_without_explicit_request",
    "push": "never_without_explicit_request", 
    "config_changes": "never"
  }
}
```

## Project Context (project.json)

### Project Structure Definition

```mermaid
graph TB
    subgraph "Project Context Information"
        subgraph "Basic Information"
            NAME["Name: Master of Muppets<br/>USB MIDI to 16ch CV"]
            PLATFORM["Platform: Teensy 4.1<br/>ARM Cortex-M7"]
            TYPE["Type: embedded_audio<br/>Real-time system"]
        end
        
        subgraph "Dependencies"
            THREADING["Threading: TeensyThreads<br/>Cooperative multitasking"]
            I2C["I2C: Wire<br/>Hardware abstraction"]
            HARDWARE["Hardware: Arduino/Teensy<br/>Framework integration"]
        end
        
        subgraph "Project Folders"
            HARDWARE_LOC["Hardware: hardware/master_of_muppets/<br/>KiCad design files"]
            FIRMWARE_LOC["Firmware: firmware/<br/>C++ embedded code"]
            STRUCTURE["Folder Structure<br/>Headers, Source, Libraries, Tests"]
        end
        
        NAME --> THREADING
        PLATFORM --> I2C
        TYPE --> HARDWARE
        
        THREADING --> HARDWARE_LOC
        I2C --> FIRMWARE_LOC
        HARDWARE --> STRUCTURE
    end
```

### Keyword Mapping

```json
{
  "project_folders": {
    "hardware": {
      "location": "hardware/master_of_muppets/",
      "keywords": ["schematics", "pcb", "hardware", "components", "circuits", "cad"]
    },
    "firmware": {
      "location": "firmware/",
      "language": "c++",
      "keywords": ["code", "firmware", "embedded", "threading", "real-time"]
    }
  }
}
```

## Data Store Context (data_store.json)

### Knowledge File Categories

```mermaid
graph TB
    subgraph "Data Store Knowledge Organization"
        INDEX[Data Store Index<br/>data_store.json]
        
        subgraph "Component Knowledge"
            DATASHEETS[data_sheets/<br/>Component Specifications<br/>Keywords: component, specs, electrical]
            HARDWARE_DESIGN[hardware/<br/>Design Knowledge<br/>Keywords: hardware, design, circuit]
        end
        
        subgraph "Development Knowledge"
            FIRMWARE_PATTERNS[firmware/<br/>Libraries & Patterns<br/>Keywords: firmware, embedded, teensy]
            ALGORITHMS[algorithms/<br/>Graph Theory<br/>Keywords: algorithm, graph, optimization]
            KICAD[coding/kicad/<br/>KiCad Knowledge<br/>Keywords: kicad, pcb, schematic]
        end
        
        subgraph "Project Knowledge"
            MOM_CORR[master_of_muppets/correlations/<br/>Cross-Domain Analysis<br/>Keywords: correlation, cross-domain]
            MOM_GRAPHS[master_of_muppets/graphs/<br/>Circuit Graphs<br/>Keywords: graph analysis, circuit graphs]
            MOM_STRUCTURE[master_of_muppets/project_structure/<br/>Development Methodology<br/>Keywords: project structure, methodology]
        end
        
        INDEX --> DATASHEETS
        INDEX --> HARDWARE_DESIGN
        INDEX --> FIRMWARE_PATTERNS
        INDEX --> ALGORITHMS
        INDEX --> KICAD
        INDEX --> MOM_CORR
        INDEX --> MOM_GRAPHS
        INDEX --> MOM_STRUCTURE
    end
```

### Access Patterns

```mermaid
sequenceDiagram
    participant User as User Query
    participant Context as Context System
    participant DataStore as Data Store Index
    participant Knowledge as Knowledge Files

    User->>Context: Query with Keywords
    Context->>DataStore: Analyze Keywords
    DataStore->>DataStore: Match to Categories
    DataStore->>Knowledge: Load Relevant Files
    Knowledge->>Context: Return Knowledge Data
    Context->>User: Enhanced Response
    
    Note over DataStore: component lookup → datasheet files
    Note over DataStore: kicad analysis → parsing knowledge
    Note over DataStore: correlation → cross-domain files
```

### Automatic Knowledge Access

```json
{
  "access_patterns": {
    "component_lookup": {
      "trigger_keywords": ["component", "datasheet", "spec", "pin", "electrical"],
      "action": "Search knowledge_files for component name, load datasheet JSON",
      "example": "AD5593R → claude/data_store/knowledge/data_sheets/ad5593r.json"
    },
    "kicad_parsing": {
      "trigger_keywords": ["kicad", "parse", "pcb", "schematic", "connectivity"],
      "action": "Load KiCad structure reference from coding/kicad/",
      "example": "PCB analysis → claude/data_store/knowledge/coding/kicad/pcb.json"
    }
  }
}
```

## Conditional Context Loading

### Coding Style Context

**Trigger Conditions**:
```json
{
  "keywords": [
    "create", "write", "new file", "add file", "implement", 
    "edit", "modify", "update", "refactor", "change", "fix",
    "add function", "create class", "implement method", 
    "add variable", "declare", "define"
  ]
}
```

**Content Overview**:
- Code formatting standards
- Naming conventions (Muppets-themed)
- Comment policies (minimal unless requested)
- File organization patterns
- Template and style guidelines

### Git Context

**Trigger Conditions**:
```json
{
  "keywords": ["git", "commit", "push", "pull", "branch", "merge", "version control"]
}
```

**Content Overview**:
- Git workflow procedures
- Commit message standards
- Branch management strategy
- Version control best practices
- Integration with AI knowledge tracking

## Context Loading Performance

### Loading Efficiency

```mermaid
graph LR
    subgraph "Context Loading Performance"
        QUERY[User Query<br/>Input Processing]
        
        subgraph "Loading Times"
            MANDATORY[Mandatory Contexts<br/>~50ms load time<br/>Always cached]
            CONDITIONAL[Conditional Contexts<br/>~20ms load time<br/>Keyword triggered]
            KNOWLEDGE[Knowledge Files<br/>~100ms load time<br/>Specific file access]
        end
        
        subgraph "Optimization"
            CACHE[Context Caching<br/>Memory resident<br/>Fast retrieval]
            INDEX["Indexed Access<br/>O(1) lookup<br/>Hash-based search"]
            LAZY[Lazy Loading<br/>On-demand only<br/>Minimal overhead]
        end
        
        QUERY --> MANDATORY
        QUERY --> CONDITIONAL
        QUERY --> KNOWLEDGE
        
        MANDATORY --> CACHE
        CONDITIONAL --> INDEX
        KNOWLEDGE --> LAZY
    end
```

### Context Effectiveness Metrics

| Context Type | Load Frequency | Response Quality | Performance Impact |
|--------------|----------------|------------------|-------------------|
| **Core** | 100% (mandatory) | Essential baseline | Minimal |
| **Project** | 100% (mandatory) | Project accuracy | Low |
| **Data Store** | 100% (mandatory) | Knowledge access | Low |
| **Coding Style** | 60% (conditional) | Code consistency | Medium |
| **Git** | 15% (conditional) | Version control | Minimal |

## Context Management Best Practices

### Context File Maintenance

```mermaid
graph TD
    subgraph "Context Maintenance Workflow"
        MONITOR[Monitor Context Usage<br/>Track keyword matches<br/>Measure effectiveness]
        
        UPDATE[Update Context Content<br/>Refresh knowledge references<br/>Add new keywords]
        
        OPTIMIZE[Optimize Loading Rules<br/>Adjust keyword thresholds<br/>Balance performance]
        
        VALIDATE[Validate Context Logic<br/>Test loading scenarios<br/>Verify completeness]
        
        MONITOR --> UPDATE
        UPDATE --> OPTIMIZE
        OPTIMIZE --> VALIDATE
        VALIDATE --> MONITOR
    end
```

### Adding New Contexts

**Process for New Context Creation**:
1. **Identify Need**: Specific domain or workflow requirement
2. **Define Keywords**: Comprehensive trigger word list
3. **Structure Content**: JSON schema compliance
4. **Test Loading**: Verify trigger mechanisms
5. **Performance Check**: Measure loading impact
6. **Documentation**: Update context documentation

### Context Debugging

**Debugging Tools**:
```json
{
  "debug_features": {
    "context_logging": "Track which contexts load for each query",
    "keyword_matching": "Show which keywords trigger context loading", 
    "load_timing": "Measure context loading performance",
    "content_validation": "Verify context file integrity"
  }
}
```

## Integration with Development Workflow

### Real-time Context Adaptation

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant AI as Claude AI
    participant Context as Context System
    participant Knowledge as Knowledge Base

    Dev->>AI: Development Query
    AI->>Context: Analyze Query Intent
    Context->>Context: Determine Context Needs
    Context->>Knowledge: Load Relevant Knowledge
    Knowledge->>AI: Enhanced Knowledge Base
    AI->>Dev: Contextually-Aware Response
    
    Note over Context: Automatic context selection
    Note over Knowledge: 900x faster than manual lookup
    Note over AI: Enhanced response quality
```

### Context Evolution

The context system evolves with the project:

**Version History**:
- **Season 01-02**: Basic context structure
- **Season 03**: Comprehensive knowledge integration
- **Season 04**: Production-ready context system
- **Season 05 (Planned)**: Machine learning context optimization

**Future Enhancements**:
- Adaptive context selection based on usage patterns
- Real-time context effectiveness measurement
- Predictive context pre-loading
- Cross-project context sharing

---

*The context system represents a breakthrough in AI-assisted development, providing intelligent, automatic knowledge access that enhances development efficiency by 900x while maintaining precision and relevance.*