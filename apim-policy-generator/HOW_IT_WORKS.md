# How Integration Architect Copilot Works

## Architecture Overview

The application follows a scenario-driven architecture.

```text
User Input
     |
     v
Format Detection
     |
     v
Scenario Detection
     |
     +--------------------------+
     |                          |
     v                          v

Transformation        API Management

     |                          |
     +------------+-------------+
                  |
                  v

         Artifact Generator

                  |
                  v

          Result Processor

                  |
                  v

             UI Renderer

                  |
                  v

             ZIP Export
```

---

## Step 1: Format Detection

The application first identifies the input type.

Supported formats:

* JSON
* XML
* OpenAPI 3.x
* Swagger 2.0
* Azure APIM Policy
* Plain Text Requirements

Example:

```yaml
openapi: 3.0.0
```

Detected as:

```text
openapi_v3
```

---

## Step 2: Scenario Detection

The system determines what the user wants to generate.

Examples:

| Input   | Artifact        | Scenario           |
| ------- | --------------- | ------------------ |
| JSON    | JavaScript      | json_transform     |
| XML     | XSLT            | xml_transform      |
| OpenAPI | OpenAPI         | openapi_generation |
| OpenAPI | APIM Policy     | azure_apim_policy  |
| Any     | Security Report | security_report    |

---

## Step 3: Artifact Generation

Each scenario is routed to a dedicated generator.

### Transformation Generator

Produces:

* JavaScript
* XSLT
* Mapping Analysis

### APIM Generator

Produces:

* Azure APIM Policy XML
* Security Recommendations

### OpenAPI Generator

Produces:

* OpenAPI 3.x Specifications
* Specification Improvements

### Logic App Generator

Produces:

* Workflow Skeletons
* Inline Code Blocks

### Security Generator

Produces:

* Findings
* Risk Assessment
* Recommendations

---

## Step 4: Result Processing

All generated artifacts are normalized into a common response structure.

```json
{
  "scenario": "...",
  "analysis": {},
  "policy_xml": "...",
  "openapi_spec": "...",
  "javascript_code": "...",
  "xslt_code": "...",
  "logic_app_block": {}
}
```

This allows the frontend to render outputs dynamically.

---

## Step 5: Dynamic User Interface

The frontend displays only relevant tabs.

Examples:

### JSON Transformation

```text
Analysis
JavaScript
Logic App
```

### OpenAPI Generation

```text
Analysis
OpenAPI
```

### APIM Policy Generation

```text
Analysis
Policy XML
Security
```

---

## Step 6: Download Package

Generated artifacts are packaged into a ZIP archive.

Possible outputs:

```text
report.md
openapi.yaml
policy.xml
transform.js
transform.xslt
logicapp-action.json
security-findings.json
```

Only relevant artifacts are included.

---

## Design Principles

The project was built around four principles:

### Simplicity

Keep the user experience focused and easy to understand.

### Scenario-Based Routing

Generate only the artifacts relevant to the selected use case.

### Explainability

Provide analysis and recommendations alongside generated code.

### Extensibility

Future support can be added for:

* Kong Gateway
* Apigee
* NGINX
* MuleSoft
* Azure Functions

without changing the overall architecture.
