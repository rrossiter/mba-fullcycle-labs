"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

#minhas alterações
from langsmith import Client
from datetime import date
import yaml

load_dotenv()

client = Client()

def save_prompt_locally(prompt, prompt_name: str):
    Path("prompts").mkdir(exist_ok=True)

    system_template = prompt.messages[0].prompt.template
    human_template = prompt.messages[1].prompt.template
    print(f"Prompt Original: {prompt}\n")
    print(f"System Template:\n{system_template}\n")
    print(f"Human Template:\n{human_template}\n")

    # Extrair o nome
    short_name = prompt_name.split("/")[-1]

    #Para deixar conforme o exemplo que foi mandado
    data = {
        short_name: {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_template.strip(),
        },
        "user_prompt": human_template.strip(),
        "version": "v1",
        "created_at": str(date.today()),
        "tags": ["bug-analysis", "user-story", "product-management"],
    }

    filename = f"prompts/{short_name}.yml"

    with open(filename, "w", encoding="utf-8") as f:
        
        yaml_str = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
        yaml_str = yaml_str.replace("user_prompt: '{bug_report}'", 'user_prompt: "{bug_report}"')
        
        # Corrigi as tags
        yaml_str = yaml_str.replace("User Story gerada:'", "User Story gerada:")
        tags_inline = str(data["tags"]).replace("'", '"')
        yaml_str = yaml_str.replace("tags:\n- bug-analysis\n- user-story\n- product-management", f"tags: {tags_inline}")
        
        f.write(yaml_str)

    print(f"Prompt salvo em {filename}")

def pull_prompts_from_langsmith(prompt_name: str):
    prompt = client.pull_prompt(prompt_name)
    print(f"Prompt puxado do LangSmith Hub")
    return prompt


def main():
    """Função principal"""
    prompt_name = "leonanluppi/bug_to_user_story_v1"
    prompt = pull_prompts_from_langsmith(prompt_name)
    save_prompt_locally(prompt, prompt_name)


if __name__ == "__main__":
    sys.exit(main())