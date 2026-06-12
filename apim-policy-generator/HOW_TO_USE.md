# How To Use Integration Artifact Copilot

## Overview

The application accepts an existing integration asset and generates one or more implementation artifacts.

Typical inputs include:

* OpenAPI specifications
* Swagger specifications
* APIM policies
* JSON payloads
* XML payloads
* Integration requirements

---

## OpenAPI to APIM Policy

### Input

Platform:

```text
Azure API Management
```

Artifact:

```text
Azure APIM Policy XML
```

Input:

```yaml
openapi: 3.0.0
```

Requirement:

```text
Require JWT validation
Enable CORS
Rate limit to 100 requests per minute
```

### Output

Generated:

* APIM Policy XML
* Security Recommendations
* Analysis Report

---

## OpenAPI Upgrade

### Input

Platform:

```text
Azure API Management
```

Artifact:

```text
OpenAPI v3 Spec
```

Input:

```yaml
swagger: "2.0"
```

Requirement:

```text
Upgrade to OpenAPI 3.0
```

### Output

Generated:

* OpenAPI v3 Specification
* Improvement Recommendations

---

## JSON Transformation

### Input

Platform:

```text
Generic Transformation
```

Artifact:

```text
JavaScript Transform
```

Source:

```json
{
  "customer_id": "123",
  "first_name": "John",
  "last_name": "Smith"
}
```

Target:

```json
{
  "customerId": "123",
  "fullName": "John Smith"
}
```

### Output

Generated:

* JavaScript Transformation
* Logic App Inline Code
* Mapping Analysis

---

## XML Transformation

### Input

Platform:

```text
Generic Transformation
```

Artifact:

```text
XSLT Transform
```

Source:

```xml
<Customer>
    <Id>123</Id>
</Customer>
```

Target:

```xml
<Client>
    <CustomerId>123</CustomerId>
</Client>
```

### Output

Generated:

* XSLT
* Mapping Guidance

---

## Logic App Generation

### Input

Platform:

```text
Azure Logic Apps
```

Artifact:

```text
Logic App Workflow
```

Requirement:

```text
Receive HTTP request
Transform payload
Call backend API
Return response
```

### Output

Generated:

* Workflow Skeleton
* Inline Code Actions
* Connector Recommendations

---

## Security Review

### Input

Artifact:

```text
Security Report
```

Supported inputs:

* OpenAPI
* APIM Policy
* JSON
* XML

### Output

Generated:

* Security Findings
* Risk Assessment
* Recommendations

---

## Download Package

Generated artifacts can be downloaded as a ZIP package.

Typical contents:

```text
report.md
policy.xml
openapi.yaml
transform.js
transform.xslt
logicapp-action.json
security-findings.json
```
