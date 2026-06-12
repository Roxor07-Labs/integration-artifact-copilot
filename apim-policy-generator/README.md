# Integration Artifact Copilot

OpenAPI • APIM • Transformations • Logic Apps

Integration Architect Copilot is an AI-powered assistant for integration engineers and architects. It generates transformation artifacts, Azure API Management policies, OpenAPI specifications, Logic App workflows, and security recommendations from existing integration assets and requirements.

## Features

* OpenAPI Analysis and Generation
* Azure API Management Policy Generation
* JSON Transformation Generation
* XML Transformation Generation
* Logic App Workflow Assistance
* API Security Review
* Integration Documentation Generation

## Supported Scenarios

| Scenario              | Description                     |
| --------------------- | ------------------------------- |
| JSON → JSON           | JavaScript transformations      |
| XML → XML             | XSLT transformations            |
| OpenAPI → OpenAPI     | OpenAPI generation and upgrades |
| OpenAPI → APIM Policy | Azure APIM policy generation    |
| APIM Policy Review    | Security and governance review  |
| Logic App Generation  | Workflow generation             |
| Security Analysis     | API security recommendations    |

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/integration-architect-copilot.git

cd integration-architect-copilot

python -m venv .venv

source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env`

```env
ANTHROPIC_API_KEY=your_api_key_here
```

Run:

```bash
uvicorn main:app --reload
```

Open:

```text
http://localhost:8000
```

## Documentation

* HOW_TO_USE.md
* HOW_IT_WORKS.md

## Technology Stack

Frontend:

* HTML
* CSS
* JavaScript

Backend:

* FastAPI
* Python

AI:

* Anthropic Claude

## Roadmap

Planned support:

* Kong Gateway
* Apigee
* NGINX
* Postman Collection Generation
* API Governance Reviews
* Local LLM Support

## Author

Ashwin Kawade

Senior Integration Engineer specializing in Azure API Management, OpenAPI Governance, Integration Architecture, and Azure Integration Services.
