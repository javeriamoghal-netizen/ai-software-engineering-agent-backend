from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from pydantic import BaseModel

from dotenv import load_dotenv

from groq import Groq

from pathlib import Path

import os
import json
import re
import zipfile



# =========================
# ENVIRONMENT
# =========================

load_dotenv()


client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)



# =========================
# FASTAPI APP
# =========================


app = FastAPI(

    title="AI Software Engineering Agent",

    version="1.0"

)





# =========================
# CORS
# =========================


app.add_middleware(

    CORSMiddleware,

    allow_origins=[

        "http://localhost:5173"

    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)







# =========================
# REQUEST MODELS
# =========================


class RequirementRequest(BaseModel):

    requirement: str




class ArchitectureRequest(BaseModel):

    requirement: str




class BackendRequest(BaseModel):

    requirement: str




class CodeReviewRequest(BaseModel):

    code: str




class TestCaseRequest(BaseModel):

    code: str




class DockerRequest(BaseModel):

    requirement: str




class ReadmeRequest(BaseModel):

    requirement: str







# =========================
# AI SYSTEM PROMPT
# =========================


STRICT_JSON = """

You are an expert AI Software Engineering Agent.

Rules:

1. Return ONLY valid JSON.
2. Never use markdown.
3. Never use code blocks.
4. Never explain outside JSON.
5. Always use double quotes.
6. JSON must be directly parseable.

"""








# =========================
# LLM FUNCTION
# =========================


def call_llm(

    prompt,

    system_prompt=STRICT_JSON

):


    response = client.chat.completions.create(


        model="llama-3.3-70b-versatile",


        temperature=0.2,


        messages=[


            {

                "role":"system",

                "content":system_prompt

            },


            {

                "role":"user",

                "content":prompt

            }


        ]

    )



    result = (

        response
        .choices[0]
        .message
        .content
        .strip()

    )



    print("\n========== AI RESPONSE ==========\n")

    print(result)

    # Remove markdown if present




    # remove markdown

    result = re.sub(

        r"^```json\s*",

        "",

        result,

        flags=re.I

    )


    result = re.sub(

        r"\s*```$",

        "",

        result

    )





    # extract JSON

    start = result.find("{")

    end = result.rfind("}") + 1




    if start != -1 and end > start:

        result = result[start:end]




    try:

        return json.loads(result)



    except Exception as e:


        print(

            "JSON ERROR:",

            e

        )


        return {


            "error":

            "Invalid JSON from AI",


            "raw_response":

            result

        }







# =========================
# PROJECT SAVE FUNCTION
# =========================


def clean_project_name(name):


    name = name.strip()


    name = name.replace(

        " ",

        "_"

    )


    name = re.sub(

        r"[^a-zA-Z0-9_-]",

        "",

        name

    )


    return name or "ai_generated_project"







def save_generated_project(project_data):


    project_name = clean_project_name(

        project_data.get(

            "project_name",

            "ai_generated_project"

        )

    )



    project_path = (

        Path("generated_projects")

        /

        project_name

    )



    project_path.mkdir(

        parents=True,

        exist_ok=True

    )



    for file in project_data.get(

        "files",

        []

    ):


        filename = file.get(

            "filename"

        )


        code = file.get(

            "code",

            ""

        )



        if filename:


            file_path = (

                project_path

                /

                filename

            )


            file_path.parent.mkdir(

                parents=True,

                exist_ok=True

            )


            with open(

                file_path,

                "w",

                encoding="utf-8"

            ) as f:


                f.write(code)




    print(

        "PROJECT CREATED:",

        project_path

    )


    return project_path
# =========================
# ZIP CREATION FUNCTION
# =========================


def zip_generated_project(project_path: Path):


    zip_path = project_path.parent / f"{project_path.name}.zip"



    with zipfile.ZipFile(

        zip_path,

        "w",

        zipfile.ZIP_DEFLATED

    ) as zipf:


        for file in project_path.rglob("*"):


            if file.is_file():


                zipf.write(

                    file,

                    file.relative_to(

                        project_path.parent

                    )

                )



    print(

        "ZIP CREATED:",

        zip_path

    )


    return zip_path








# =========================
# HOME API
# =========================


@app.get("/")
def home():


    return {


        "message":

        "Welcome to AI Software Engineering Agent"


    }








# =========================
# REQUIREMENT ANALYSIS AGENT
# =========================


@app.post("/analyze-requirement")
def analyze_requirement(

    request: RequirementRequest

):


    prompt = f"""


You are a Senior Business Analyst and Software Architect.



Analyze this software requirement.



Return ONLY JSON.



FORMAT:



{{
"project_name":"",

"project_type":"",

"problem_statement":"",

"target_users":[],

"core_features":[],

"functional_requirements":[],

"non_functional_requirements":[],

"technology_stack":{{

    "frontend":"",

    "backend":"",

    "database":"",

    "authentication":"",

    "deployment":""

}},

"modules":[],

"security_requirements":[],

"future_improvements":[]

}}



Rules:

- Do not give generic answers.
- Extract real modules.
- Suggest realistic technologies.
- Think like a professional software architect.



Requirement:


{request.requirement}


"""


    return call_llm(prompt)









# =========================
# SOFTWARE ARCHITECT AGENT
# =========================


@app.post("/generate-architecture")
def generate_architecture(

    request: ArchitectureRequest

):


    prompt = f"""


You are a Principal Software Architect.



Design the complete architecture for this software.



Return ONLY JSON.



IMPORTANT:

Do NOT always choose Microservices.

Choose architecture based on:

- Application size
- Complexity
- Number of users
- Scalability
- Maintenance requirements



Possible architecture styles:


- Modular Monolith

- Clean Architecture

- Layered Architecture

- Event Driven Architecture

- Microservices Architecture

- Serverless Architecture




FORMAT:



{{
"project_name":"",

"architecture_type":"",

"architecture_reason":"",


"system_components":[

    {{
    "name":"",
    "responsibility":"",
    "technology":""
    }}

],



"folder_structure":[

    ""

],



"database_design":{{

    "database":"",

    "tables":[

        {{
        "name":"",
        "purpose":"",
        "fields":[]
        }}

    ]

}},



"api_design":[

    {{
    "method":"",
    "endpoint":"",
    "purpose":""
    }}

],



"authentication_flow":"",



"deployment_architecture":[

    ""

],



"development_flow":[

    ""

]

}}



Requirement:


{request.requirement}


"""


    return call_llm(prompt)
# =========================
# BACKEND GENERATOR AGENT
# =========================


@app.post("/generate-backend")
def generate_backend(

    request: BackendRequest

):


    prompt = f"""


You are a Senior Backend Engineer.



Generate a complete production-ready FastAPI backend.



Return ONLY JSON.



FORMAT:



{{
"project_name":"",

"description":"",

"folder_structure":[

    ""

],


"files":[

    {{

    "filename":"",

    "code":""

    }}

]

}}




Required files:



- main.py

- requirements.txt

- .env.example

- database.py

- models/

- schemas/

- routers/

- services/

- utils/

- authentication



Backend requirements:



- FastAPI

- SQLAlchemy

- Pydantic

- REST APIs

- Database integration

- Authentication support

- Error handling

- Clean architecture



Rules:



- Generate complete code.

- No TODO.

- No placeholders.

- Every file must contain code.

- Keep imports correct.

- Project should run after installation.



Requirement:



{request.requirement}



"""



    result = call_llm(prompt)




    if "error" in result:


        return result





    project_path = save_generated_project(

        result

    )



    zip_path = zip_generated_project(

        project_path

    )





    result["saved_location"] = str(

        project_path

    )



    result["zip_file"] = str(

        zip_path

    )



    result["download_name"] = (

        project_path.name

    )





    print(

        "DOWNLOAD NAME:",

        result["download_name"]

    )


    return result










# =========================
# DOWNLOAD ZIP API
# =========================


@app.get("/download/{project_name}")
def download_project(

    project_name: str

):


    # Convert spaces again for safety

    project_name = clean_project_name(

        project_name

    )



    zip_path = (

        Path("generated_projects")

        /

        f"{project_name}.zip"

    )



    print(

        "SEARCHING ZIP:",

        zip_path

    )





    if zip_path.exists():


        return FileResponse(

            path=str(zip_path),

            filename=f"{project_name}.zip",

            media_type="application/zip"

        )




    return {


        "error":

        "Project ZIP not found",


        "searched_path":

        str(zip_path)


    }
# =========================
# CODE REVIEW AGENT
# =========================


@app.post("/review-code")
def review_code(

    request: CodeReviewRequest

):


    prompt = f"""


You are a Senior Software Engineer and Code Reviewer.



Review this code.



Return ONLY JSON.



FORMAT:



{{
"overall_rating":"",

"code_quality":"",

"strengths":[],

"bugs":[],

"security_issues":[],

"performance_issues":[],

"architecture_issues":[],

"best_practices":[],

"improvements":[]

}}



Analyze:

- Bugs
- Security vulnerabilities
- Performance problems
- Maintainability
- Scalability
- Coding standards



Code:



{request.code}



"""


    return call_llm(prompt)









# =========================
# TEST GENERATION AGENT
# =========================


@app.post("/generate-tests")
def generate_tests(

    request: TestCaseRequest

):


    prompt = f"""


You are an Expert QA Automation Engineer.



Create a complete testing strategy.



Return ONLY JSON.



FORMAT:



{{
"testing_strategy":"",

"unit_tests":[],

"integration_tests":[],

"api_tests":[],

"edge_cases":[],

"negative_tests":[],

"security_tests":[]

}}



Include:

- Normal test cases
- Failure scenarios
- Boundary cases
- API validation
- Security testing



Code:



{request.code}



"""


    return call_llm(prompt)









# =========================
# DOCKER GENERATOR AGENT
# =========================


@app.post("/generate-docker")
def generate_docker(

    request: DockerRequest

):


    prompt = f"""


You are a Senior DevOps Engineer.



Create deployment configuration.



Return ONLY JSON.



FORMAT:



{{
"dockerfile":"",

"docker_compose":"",

"environment_variables":[],

"deployment_steps":[]

}}



Include:

- Production Dockerfile
- Docker compose
- Environment variables
- Deployment process



Requirement:



{request.requirement}



"""


    return call_llm(prompt)









# =========================
# README GENERATOR AGENT
# =========================


@app.post("/generate-readme")
def generate_readme(

    request: ReadmeRequest

):


    prompt = f"""


You are a Professional Technical Writer.



Create complete GitHub README documentation.



Return ONLY JSON.



FORMAT:



{{
"readme":""

}}



README must contain:



# Project Overview

# Features

# Technology Stack

# Installation

# Environment Setup

# API Documentation

# Running Application

# Docker Deployment

# Future Improvements



Requirement:



{request.requirement}



"""


    return call_llm(prompt)