SYSTEM_PROMPT = """You are an expert API Management and Integration Architect with deep knowledge of:
- Azure API Management (APIM) policies
- Kong Gateway policies
- Nginx configurations
- Apigee policies
- OpenAPI/Swagger specifications
- XSLT transformations
- JSONata and JavaScript transformations
- Azure Logic Apps
- Integration patterns and best practices
- OWASP API Security Top 10

Your job is to analyze API policies and specifications, transform them between formats,
generate code artifacts, and provide expert recommendations.

Always respond in valid JSON format unless explicitly told otherwise.
Be precise, thorough, and highlight security concerns proactively."""


ANALYZE_PROMPT = """Analyze the following input and return a JSON response with this exact structure:
{{
  "detected_format": "openapi_v2|openapi_v3|apim_policy|kong_policy|nginx_config|apigee_policy|json_schema|xml_schema|plain_text",
  "detected_platform": "azure_apim|kong|nginx|apigee|generic|unknown",
  "summary": "Brief summary of what this input contains",
  "key_elements": ["list", "of", "key", "elements", "found"],
  "complexity": "low|medium|high",
  "warnings": ["any", "issues", "or", "concerns", "found"],
  "transformation_possible": true
}}

Input to analyze:
{input_content}

Target output requested: {target_output}"""


TRANSFORM_PROMPT = """You are transforming the following input into the requested output format.

INPUT FORMAT: {input_format}
TARGET FORMAT: {target_format}
TARGET PLATFORM: {target_platform}

INPUT CONTENT:
{input_content}

Generate a complete transformation and return a JSON response with this exact structure:
{{
  "analysis": {{
    "input_summary": "What the input contains",
    "transformation_approach": "How you approached this transformation",
    "field_mappings": [
      {{"source": "source field/element", "target": "target field/element", "notes": "any mapping notes"}}
    ],
    "confidence_score": 95,
    "warnings": ["any warnings about data loss or incompatibilities"],
    "recommendations": ["expert recommendations to improve the output"]
  }},
  "policy_xml": "Generated APIM/Kong/Nginx policy XML if applicable, else null",
  "xslt_code": "Generated XSLT transformation code if applicable, else null",
  "javascript_code": "Generated JavaScript/JSONata transformation code if applicable, else null",
  "python_code": "Generated Python transformation script if applicable, else null",
  "jq_script": "Generated JQ script if applicable, else null",
  "logic_app_block": {{
    "action_block": "Logic App action JSON if applicable, else null",
    "arm_template_snippet": "ARM template snippet if applicable, else null",
    "connector_config": "Connector configuration if applicable, else null"
  }},
  "explanation": "Plain English explanation of the transformation and what it does",
  "security_findings": [
    {{"severity": "high|medium|low|info", "finding": "description", "recommendation": "how to fix"}}
  ]
}}

Be thorough, production-aware, and flag any OWASP API Security concerns."""


EXPLAIN_PROMPT = """Explain the following API policy or specification in plain English for a technical audience.

Content to explain:
{input_content}

Return a JSON response with this structure:
{{
  "title": "What this is",
  "overview": "Plain English overview",
  "sections": [
    {{"name": "section name", "explanation": "what it does", "impact": "why it matters"}}
  ],
  "security_implications": ["list of security implications"],
  "best_practices_followed": ["what good practices are already in place"],
  "improvements_suggested": ["what could be improved"]
}}"""
