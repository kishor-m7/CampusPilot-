# CampusPilot — AWS Deployment & Hackathon Readiness Guide

This document outlines the cloud deployment architecture, security model, and demonstration flows for **CampusPilot** in the Amazon AppDev 2026 Alexa+ Hackathon.

---

## 1. Cloud Architecture Overview

```
                          ┌────────────────────────┐
                          │   Alexa+ Echo Device   │
                          │   (Voice Experience)   │
                          └───────────┬────────────┘
                                      │ Alexa Voice Service
                                      ▼
┌─────────────────┐       ┌────────────────────────┐       ┌──────────────────────┐
│  React / Vite   │       │     AWS App Runner     │       │   Google Gemini LLM  │
│    Frontend     │◀─────▶│    (FastAPI + MCP)     │◀─────▶│ (gemini-3-flash-prv) │
│ (S3+CloudFront) │ HTTPS │   Port 8000 / Port 8001│ HTTPS │ Function Calling     │
└─────────────────┘       └───────────┬────────────┘       └──────────────────────┘
                                      │
                                      ▼
                          ┌────────────────────────┐
                          │  Supabase PostgreSQL   │
                          │ (AWS Region Hosted DB) │
                          └────────────────────────┘
```

### Hosting Options Evaluated
1. **AWS App Runner (Recommended for Hackathon)**:
   - Native containerized web service hosting.
   - Built-in automatic TLS / HTTPS certificate provisioning.
   - Fully supports Streamable HTTP and long-lived streaming connections.
   - Auto-scaling from zero to handle hackathon judging bursts.
2. **AWS ECS Fargate**:
   - Ideal for multi-container deployments (FastAPI + Standalone MCP on 8001).
   - Backed by Application Load Balancer (ALB).
3. **AWS S3 + CloudFront (Frontend)**:
   - High-speed global edge distribution for the React Vite static build (`client/dist`).

---

## 2. IAM Roles and Least Privilege Security

### Recommended Execution Role: `CampusPilotAppRunnerRole`
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogStreams"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/apprunner/campuspilot*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:campuspilot/*"
    }
  ]
}
```

---

## 3. CloudWatch Logging & Observability

Configure FastAPI to stream structured JSON logs to AWS CloudWatch:
- Log Group: `/aws/campuspilot/api`
- Metrics:
  - `MCP_Tool_Execution_Duration`
  - `Gemini_API_Latency`
  - `Alexa_Sync_Events`

---

## 4. Optional Amazon Bedrock Integration

CampusPilot uses Google Gen AI (`gemini-3-flash-preview` / `gemini-3.8-flash`) as its primary LLM engine. For judges wishing to evaluate Amazon Bedrock (e.g. Anthropic Claude 3.5 Sonnet / Amazon Titan), the tool calling sequence is identical:

```python
# Optional Bedrock Adapter Snippet (backend/bedrock_adapter.py)
import boto3
import json

def invoke_bedrock_agent(prompt: str, mcp_tools: list):
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    # Formats MCP tools into Bedrock toolSpec format
    # Invokes converse API with toolConfig
    # Dispatches tool execution to backend/services.py
```

---

## 5. End-to-End Hackathon Demonstration Scenario

### Scenario: "The High-Stakes Exam Week"

1. **Step 1: Student Overview & Day Planning**
   - Student opens CampusPilot dashboard.
   - 4 pending assignments and 2 upcoming exams are displayed with real-time countdown badges.
   - Student clicks **"Plan My Day"**: CampusPilot aggregates their pending kernel lab assignment and Cybersecurity exam, creates an optimized 3-hour focus session, and pushes the schedule to connected Alexa devices.

2. **Step 2: Alexa Voice Routine Sync**
   - The morning briefing voice routine triggers on the Alexa device:
     *"Good morning! CampusPilot has synced 4 study sessions for your Morning Briefing. Your first focus block is Kernel Memory Allocator Lab."*

3. **Step 3: Conversational Copilot & MCP Tool Execution**
   - In the AI Assistant tab, student asks:
     *"What are my upcoming assignment deadlines and what should I work on first?"*
   - CampusPilot AI activates the `get_student_tasks` MCP tool, retrieves live deadlines from Supabase, and outputs an actionable table.
   - Student clicks the **microphone** icon and speaks:
     *"Remind me to study Operating Systems buddy allocator tonight at 8 PM."*
   - CampusPilot invokes the `create_reminder` MCP tool and schedules the alert.

4. **Step 4: Pomodoro Focus & Syllabus Checklist**
   - Student switches to the **Exams** tab and checks off completed units (*"Public Key Cryptography & RSA"*). The preparation progress bar increments in real-time.
   - Student starts the **25-min Pomodoro timer** on the Overview dashboard to enter deep focus.
