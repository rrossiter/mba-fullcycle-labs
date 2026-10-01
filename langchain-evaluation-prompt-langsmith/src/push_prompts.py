"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()

#minhas alterações
from langsmith import Client

def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    client = Client()

    prompt_config = prompt_data["bug_to_user_story_v2"]

    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_config["system_prompt"]),
        ("human", prompt_data["user_prompt"]),
    ])

    url = client.push_prompt(
        prompt_name,
        object=prompt, 
        tags=[
            f"v{prompt_data['version']}",
            f"model: gpt-4o-mini",
        ],
        description=prompt_data["bug_to_user_story_v2"]["description"],
    )
    print(f"Prompt '{prompt_name}' enviado para o LangSmith Hub: {url}")
    return True

def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    errors = []
    
    if "system_prompt" not in prompt_data["bug_to_user_story_v2"]:
        errors.append("Campo 'system_prompt' ausente")
    elif not isinstance(prompt_data["bug_to_user_story_v2"]["system_prompt"], str):
        errors.append("Campo 'system_prompt' deve ser uma string")
    elif len(prompt_data["bug_to_user_story_v2"]["system_prompt"].strip()) == 0:
        errors.append("Campo 'system_prompt' não pode estar vazio")

    if "user_prompt" not in prompt_data:
        errors.append("Campo 'user_prompt' ausente")
    elif "{bug_report}" not in prompt_data["user_prompt"]:
        errors.append("Campo 'user_prompt' deve conter a variável {bug_report}")

    is_valid = len(errors) == 0
    return is_valid, errors

def main():
    prompt_data = load_yaml("prompts/bug_to_user_story_v2.yml")
    isValidPrompt = validate_prompt(prompt_data)
    if not isValidPrompt[0]:
        print("❌ Prompt falhou na validação:")
        for error in isValidPrompt[1]:
            print(f" - {error}")
    else:
        print("✅ Prompt passou na validação!")
        push_success = push_prompt_to_langsmith("bug_to_user_story_v2", prompt_data)
        print_section_header("Resultado do Push")
        if push_success:
            print("✅ Prompt enviado com sucesso para o LangSmith Hub!")
        else:
            print("❌ Falha ao enviar o prompt. Verifique os logs para detalhes.")


if __name__ == "__main__":
    sys.exit(main())