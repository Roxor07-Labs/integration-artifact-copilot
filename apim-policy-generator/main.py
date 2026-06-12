from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import anthropic
import json
import os
import zipfile
import tempfile

load_dotenv()

app = FastAPI(title="Integration Artifact Copilot", version="1.0.0")

MODEL = "claude-haiku-4-5-20251001"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None


class TransformRequest(BaseModel):
    input_content: str
    target_output: str
    target_format: str
    context: str = ""


class AnalyzeRequest(BaseModel):
    input_content: str
    target_output: str = "auto"


COMING_SOON_PLATFORMS = {"kong", "nginx", "apigee"}


def call_claude(prompt: str, max_tokens: int = 2048) -> dict:
    if client is None:
        raise HTTPException(
            status_code=500,
            detail="ANTHROPIC_API_KEY is missing. Add it to your .env file.",
        )

    message = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = message.content[0].text.strip()

    if "```" in raw:
        for part in raw.split("```"):
            text = part.strip()
            if text.startswith("json"):
                text = text[4:].strip()
            try:
                return json.loads(text)
            except Exception:
                continue

    try:
        return json.loads(raw)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=f"Model did not return valid JSON. Raw response: {raw[:500]}",
        )


def detect_input_format(input_content: str) -> str:
    text = input_content.strip()
    lower = text.lower()

    if not text:
        return "empty"

    if text.startswith("{") or text.startswith("["):
        return "json"

    if text.startswith("<"):
        if "<policies" in lower or "<inbound" in lower:
            return "apim_policy"
        return "xml"

    if "openapi:" in lower or '"openapi"' in lower:
        return "openapi_v3"

    if "swagger:" in lower or '"swagger"' in lower:
        return "openapi_v2"

    return "plain_text"


def detect_scenario(req: TransformRequest) -> str:
    source_format = detect_input_format(req.input_content)
    platform = req.target_output
    target_format = req.target_format

    if platform in COMING_SOON_PLATFORMS:
        return "coming_soon"

    if target_format == "security_report":
        return "security_report"

    if target_format == "documentation":
        return "documentation"

    if target_format == "openapi_v3":
        return "openapi_generation"

    if platform == "azure_apim":
        if target_format == "policy_xml":
            return "azure_apim_policy"

    if platform == "logic_app":
        return "logic_app"

    if target_format == "logic_app_json":
        return "logic_app"

    if source_format == "json" or target_format == "javascript_transform":
        return "json_transform"

    if source_format == "xml" or target_format == "xslt_transform":
        return "xml_transform"

    return "generic_transform"


def empty_result(scenario: str, detected: dict) -> dict:
    return {
        "scenario": scenario,
        "detected": detected,
        "policy_xml": None,
        "openapi_spec": None,
        "xslt_code": None,
        "javascript_code": None,
        "python_code": None,
        "jq_script": None,
        "logic_app_block": {},
        "security_findings": [],
        "explanation": "",
        "analysis": {
            "input_summary": detected.get("summary", ""),
            "transformation_approach": "",
            "confidence_score": 75,
            "warnings": detected.get("warnings", []),
            "recommendations": [],
            "field_mappings": [],
        },
    }


@app.get("/", response_class=HTMLResponse)
async def root():
    with open("index.html", "r", encoding="utf-8") as file:
        return file.read()


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model": MODEL,
        "active_platforms": ["generic", "azure_apim", "logic_app"],
        "coming_soon": list(COMING_SOON_PLATFORMS),
    }


@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    input_format = detect_input_format(req.input_content)

    prompt = f"""
You are an Integration Architect.

Analyze the input and return ONLY valid JSON.

Return:
{{
  "detected_format": "{input_format}",
  "detected_platform": "azure_apim|logic_app|generic|unknown",
  "summary": "one sentence summary",
  "key_elements": ["up to 5 key elements"],
  "complexity": "low|medium|high",
  "warnings": ["obvious issues only"]
}}

INPUT:
{req.input_content[:3000]}

TARGET REQUESTED:
{req.target_output}
"""

    try:
        return call_claude(prompt, max_tokens=700)
    except Exception:
        return {
            "detected_format": input_format,
            "detected_platform": "generic",
            "summary": f"Detected {input_format} input.",
            "key_elements": [],
            "complexity": "medium",
            "warnings": [],
        }


@app.post("/generate/transformation")
async def generate_transformation(req: TransformRequest):
    prompt = f"""
You are an integration transformation expert.

Generate transformation artifacts.

Rules:
- Convert SOURCE into the EXACT TARGET SHAPE from desired output/context.
- Do not include extra fields from source unless they exist in the target.
- If target contains only id and status, output only id and status.
- For JSON input/output, generate JavaScript.
- For XML input/output, generate XSLT where possible.
- Return ONLY valid JSON.

Return:
{{
  "xslt_code": null,
  "javascript_code": "complete JavaScript transform function or null",
  "python_code": null,
  "jq_script": null,
  "field_mappings": [
    {{"source": "source path", "target": "target path", "notes": "mapping reason"}}
  ],
  "explanation": "short explanation"
}}

SOURCE:
{req.input_content[:4000]}

TARGET / DESIRED OUTPUT:
{req.context[:4000]}

TARGET FORMAT:
{req.target_format}
"""
    return call_claude(prompt, max_tokens=2600)


@app.post("/generate/apim")
async def generate_apim(req: TransformRequest):
    prompt = f"""
You are an Azure API Management expert.

Generate Azure APIM policy XML.

Rules:
- Return ONLY valid JSON.
- Generate APIM policy XML only.
- Include <policies>, <inbound>, <backend>, <outbound>, and <on-error>.
- Use placeholders where needed.
- Do not generate OpenAPI here.
- Do not generate JavaScript transformation code unless APIM set-body transformation is explicitly requested.

Return:
{{
  "policy_xml": "complete APIM policy XML",
  "explanation": "short explanation",
  "recommendations": ["recommended next steps"]
}}

SOURCE:
{req.input_content[:4000]}

DESIRED APIM POLICY BEHAVIOR:
{req.context[:4000]}
"""
    return call_claude(prompt, max_tokens=2600)


@app.post("/generate/openapi")
async def generate_openapi(req: TransformRequest):
    prompt = f"""
You are an OpenAPI expert.

Generate or improve an OpenAPI v3 specification.

Rules:
- Return ONLY valid JSON.
- Output must be valid OpenAPI 3.x YAML as a string.
- If input is Swagger 2.0, convert it to OpenAPI 3.x.
- If input is already OpenAPI 3.x, improve it based on the desired requirement.
- Add security schemes only if requested or obviously missing.
- Do not generate APIM policy XML here.

Return:
{{
  "openapi_spec": "complete OpenAPI v3 YAML",
  "explanation": "short explanation",
  "recommendations": ["recommended improvements"]
}}

SOURCE:
{req.input_content[:5000]}

DESIRED OPENAPI CHANGE:
{req.context[:4000]}
"""
    return call_claude(prompt, max_tokens=3500)


@app.post("/generate/logicapp")
async def generate_logicapp(req: TransformRequest):
    prompt = f"""
You are an Azure Logic Apps expert.

Generate Logic App artifacts.

Rules:
- Return ONLY valid JSON.
- If this is a JSON transformation, use Inline Code action.
- If this is a workflow request, generate a minimal workflow/action skeleton.
- Do not generate APIM policy XML.

Return:
{{
  "action_block": "Logic App action JSON or null",
  "arm_template_snippet": null,
  "connector_config": "short connector/config notes",
  "explanation": "short explanation"
}}

SOURCE:
{req.input_content[:4000]}

TARGET / DESIRED OUTPUT:
{req.context[:4000]}

TARGET FORMAT:
{req.target_format}
"""
    return call_claude(prompt, max_tokens=2200)


@app.post("/generate/security")
async def generate_security(req: AnalyzeRequest):
    prompt = f"""
You are an API security expert.

Audit this API, OpenAPI spec, policy, JSON, or XML for obvious security issues.

Return ONLY valid JSON:
{{
  "security_findings": [
    {{
      "severity": "high|medium|low|info",
      "finding": "description",
      "recommendation": "how to fix"
    }}
  ],
  "overall_risk": "high|medium|low",
  "summary": "one sentence summary"
}}

INPUT:
{req.input_content[:4000]}
"""
    return call_claude(prompt, max_tokens=1400)


@app.post("/generate/documentation")
async def generate_documentation(req: TransformRequest):
    prompt = f"""
You are an Integration Architect.

Explain the input and desired output in clear technical documentation.

Return ONLY valid JSON:
{{
  "documentation": "markdown documentation",
  "explanation": "short explanation",
  "recommendations": ["recommended next steps"]
}}

SOURCE:
{req.input_content[:4000]}

CONTEXT:
{req.context[:4000]}
"""
    return call_claude(prompt, max_tokens=2200)


@app.post("/transform")
async def transform(req: TransformRequest):
    scenario = detect_scenario(req)

    detected = await analyze(
        AnalyzeRequest(
            input_content=req.input_content,
            target_output=req.target_output,
        )
    )

    result = empty_result(scenario, detected)

    if scenario == "coming_soon":
        result["explanation"] = (
            f"{req.target_output} support is planned but not implemented in this POC."
        )
        result["analysis"]["transformation_approach"] = "Coming soon"
        result["analysis"]["warnings"].append(
            f"{req.target_output} generation is not implemented yet."
        )
        result["analysis"]["recommendations"] = [
            "Use Generic Transformation for JSON/XML mappings.",
            "Use Azure APIM for policy generation.",
            "Use Azure Logic Apps for workflow artifacts.",
        ]

    elif scenario == "json_transform":
        code = await generate_transformation(req)
        logicapp = await generate_logicapp(req)

        result["javascript_code"] = code.get("javascript_code")
        result["python_code"] = code.get("python_code")
        result["jq_script"] = code.get("jq_script")
        result["logic_app_block"] = {
            "action_block": logicapp.get("action_block"),
            "arm_template_snippet": logicapp.get("arm_template_snippet"),
            "connector_config": logicapp.get("connector_config"),
        }
        result["explanation"] = code.get("explanation", "Generated JSON transformation artifacts.")
        result["analysis"]["transformation_approach"] = "JSON transformation"
        result["analysis"]["field_mappings"] = code.get("field_mappings", [])
        result["analysis"]["confidence_score"] = 85
        result["analysis"]["recommendations"] = [
            "Validate generated code with real payloads.",
            "Add null checks before production use.",
            "Add unit tests for missing and optional fields.",
        ]

    elif scenario == "xml_transform":
        code = await generate_transformation(req)
        logicapp = await generate_logicapp(req)

        result["xslt_code"] = code.get("xslt_code")
        result["javascript_code"] = code.get("javascript_code")
        result["logic_app_block"] = {
            "action_block": logicapp.get("action_block"),
            "arm_template_snippet": logicapp.get("arm_template_snippet"),
            "connector_config": logicapp.get("connector_config"),
        }
        result["explanation"] = code.get("explanation", "Generated XML transformation artifacts.")
        result["analysis"]["transformation_approach"] = "XML transformation"
        result["analysis"]["field_mappings"] = code.get("field_mappings", [])
        result["analysis"]["confidence_score"] = 80

    elif scenario == "azure_apim_policy":
        apim = await generate_apim(req)
        security = await generate_security(AnalyzeRequest(input_content=req.input_content))

        result["policy_xml"] = apim.get("policy_xml")
        result["explanation"] = apim.get("explanation", "Generated Azure APIM policy XML.")
        result["security_findings"] = security.get("security_findings", [])
        result["analysis"]["transformation_approach"] = "Azure APIM policy generation"
        result["analysis"]["confidence_score"] = 82
        result["analysis"]["recommendations"] = apim.get("recommendations", []) + [
            "Replace placeholders before applying the policy.",
            "Validate the policy inside Azure API Management.",
            "Review authentication, CORS, rate-limit, and backend settings.",
        ]

    elif scenario == "openapi_generation":
        openapi = await generate_openapi(req)

        result["openapi_spec"] = openapi.get("openapi_spec")
        result["explanation"] = openapi.get("explanation", "Generated OpenAPI v3 specification.")
        result["analysis"]["transformation_approach"] = "OpenAPI generation / upgrade"
        result["analysis"]["confidence_score"] = 82
        result["analysis"]["recommendations"] = openapi.get("recommendations", [])

    elif scenario == "logic_app":
        logicapp = await generate_logicapp(req)

        result["logic_app_block"] = {
            "action_block": logicapp.get("action_block"),
            "arm_template_snippet": logicapp.get("arm_template_snippet"),
            "connector_config": logicapp.get("connector_config"),
        }
        result["explanation"] = logicapp.get("explanation", "Generated Logic App artifact.")
        result["analysis"]["transformation_approach"] = "Azure Logic Apps artifact generation"
        result["analysis"]["confidence_score"] = 80
        result["analysis"]["recommendations"] = [
            "Validate connector names and authentication settings.",
            "Add retry policies and error handling scopes.",
            "Add monitoring and tracked properties.",
        ]

    elif scenario == "security_report":
        security = await generate_security(AnalyzeRequest(input_content=req.input_content))

        result["security_findings"] = security.get("security_findings", [])
        result["explanation"] = security.get("summary", "Generated security report.")
        result["analysis"]["transformation_approach"] = "Security review"
        result["analysis"]["confidence_score"] = 80

    elif scenario == "documentation":
        docs = await generate_documentation(req)

        result["explanation"] = docs.get("documentation") or docs.get("explanation")
        result["analysis"]["transformation_approach"] = "Documentation generation"
        result["analysis"]["confidence_score"] = 80
        result["analysis"]["recommendations"] = docs.get("recommendations", [])

    else:
        code = await generate_transformation(req)

        result["javascript_code"] = code.get("javascript_code")
        result["python_code"] = code.get("python_code")
        result["jq_script"] = code.get("jq_script")
        result["explanation"] = code.get("explanation", "Generated generic integration transformation.")
        result["analysis"]["transformation_approach"] = "Generic transformation"
        result["analysis"]["field_mappings"] = code.get("field_mappings", [])
        result["analysis"]["confidence_score"] = 75

    return result


@app.post("/download")
async def download(req: TransformRequest):
    result = await transform(req)

    tmp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(tmp_dir, "integration-artifacts.zip")

    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("input.txt", req.input_content)

        zf.writestr(
            "report.md",
            f"""# Integration Artifact Copilot Report

## Scenario
{result.get("scenario")}

## Explanation
{result.get("explanation", "")}

## Analysis
{json.dumps(result.get("analysis", {}), indent=2)}

## Detected
{json.dumps(result.get("detected", {}), indent=2)}
""",
        )

        if result.get("policy_xml"):
            zf.writestr("policy.xml", result["policy_xml"])

        if result.get("openapi_spec"):
            zf.writestr("openapi.yaml", result["openapi_spec"])

        if result.get("xslt_code"):
            zf.writestr("transform.xslt", result["xslt_code"])

        if result.get("javascript_code"):
            zf.writestr("transform.js", result["javascript_code"])

        if result.get("python_code"):
            zf.writestr("transform.py", result["python_code"])

        if result.get("jq_script"):
            zf.writestr("transform.jq", result["jq_script"])

        logic_app = result.get("logic_app_block", {})
        if logic_app.get("action_block"):
            action = logic_app["action_block"]
            zf.writestr(
                "logicapp-action.json",
                json.dumps(action, indent=2) if isinstance(action, dict) else str(action),
            )

        if result.get("security_findings"):
            zf.writestr(
                "security-findings.json",
                json.dumps(result["security_findings"], indent=2),
            )

    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename="integration-artifacts.zip",
    )
