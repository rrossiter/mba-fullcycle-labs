import pytest
import yaml
from pathlib import Path


PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_prompts(file_path: Path):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_system_prompt(prompt_name: str) -> str:
    """Retorna o system prompt de um prompt específico."""
    prompt = load_prompts(PROMPTS_DIR / f"{prompt_name}.yml")
    return prompt[prompt_name]["system_prompt"]


class TestPrompts:

    def test_prompt_has_system_prompt(self):
        """Verifica se o system_prompt existe e não está vazio."""
        system_prompt = get_system_prompt("bug_to_user_story_v1")

        assert system_prompt is not None
        assert system_prompt.strip() != ""

    def test_v2_has_role_prompting(self):
        """Verifica se o prompt utiliza Role Prompting."""
        system_prompt = get_system_prompt("bug_to_user_story_v2")

        assert "[ROLE PROMPTING]" in system_prompt
        assert "Product Manager Sênior" in system_prompt
        assert "Analista de Requisitos" in system_prompt
        assert "backend" in system_prompt

    def test_v2_has_few_shot_prompting(self):
        """Verifica se o prompt utiliza Few-Shot Prompting."""
        system_prompt = get_system_prompt("bug_to_user_story_v2")

        assert "[FEW-SHOT PROMPTING]" in system_prompt
        assert "Exemplo 1" in system_prompt
        assert "Exemplo 2" in system_prompt
        assert "Relato de Bug:" in system_prompt
        assert "User Story:" in system_prompt
        assert "Critérios de Aceitação:" in system_prompt

    def test_v2_has_chain_of_thought(self):
        """Verifica se o prompt possui orientação de análise estruturada (CoT)."""
        system_prompt = get_system_prompt("bug_to_user_story_v2")

        assert "[CHAIN OF THOUGHT" in system_prompt
        assert "Análise Estruturada" in system_prompt
        assert "comportamento atual" in system_prompt
        assert "comportamento esperado" in system_prompt
        assert "problema principal" in system_prompt
        assert "Não exponha o raciocínio interno" in system_prompt

    def test_v2_has_tree_of_thought(self):
        """Verifica se o prompt utiliza estratégia inspirada em Tree of Thought."""
        system_prompt = get_system_prompt("bug_to_user_story_v2")

        assert "[TREE OF THOUGHT]" in system_prompt
        assert "diferentes interpretações" in system_prompt
        assert "sustentada pelo relato" in system_prompt
        assert "informações não fornecidas" in system_prompt

    def test_v2_has_skeleton_of_thought(self):
        """Verifica se o prompt utiliza Skeleton of Thought."""
        system_prompt = get_system_prompt("bug_to_user_story_v2")

        assert "[SKELETON OF THOUGHT" in system_prompt
        assert "1. User Story" in system_prompt
        assert "2. Critérios de Aceitação" in system_prompt
        assert "3. Contexto Técnico" in system_prompt
        assert "4. Tasks Técnicas" in system_prompt

    def test_v2_has_gherkin_format(self):
        """Verifica se os critérios de aceitação utilizam Gherkin."""
        system_prompt = get_system_prompt("bug_to_user_story_v2")

        assert "Dado que" in system_prompt
        assert "Quando" in system_prompt
        assert "Então" in system_prompt

    def test_v2_has_complexity_handling(self):
        """Verifica se o prompt trata diferentes níveis de complexidade."""
        system_prompt = get_system_prompt("bug_to_user_story_v2")

        assert "[COMPLEXITY HANDLING]" in system_prompt
        assert "### Simples" in system_prompt
        assert "### Médio" in system_prompt
        assert "### Complexo" in system_prompt
        assert "nível de detalhamento" in system_prompt

    def test_v2_has_input_validation(self):
        """Verifica se o prompt valida se o relato realmente descreve um bug."""
        system_prompt = get_system_prompt("bug_to_user_story_v2")

        assert "[INPUT VALIDATION]" in system_prompt
        assert "não descrever um bug" in system_prompt
        assert "O relato fornecido não descreve um bug." in system_prompt
        assert "incompleto ou vago" in system_prompt

    def test_v2_has_no_invention_rule(self):
        """Verifica se o prompt proíbe a criação de informações não fornecidas."""
        system_prompt = get_system_prompt("bug_to_user_story_v2")

        assert "Não invente informações." in system_prompt
        assert "Não altere o significado do relato." in system_prompt
        assert "Não presuma causa técnica sem evidência." in system_prompt
        assert "Não transforme hipóteses em fatos." in system_prompt

    def test_v2_has_backend_focus(self):
        """Verifica se o papel do prompt está direcionado a backend."""
        system_prompt = get_system_prompt("bug_to_user_story_v2")

        assert "software backend" in system_prompt
        assert "APIs" in system_prompt
        assert "sistemas distribuídos" in system_prompt

    def test_v2_has_structured_output(self):
        """Verifica se o prompt define a estrutura esperada da User Story."""
        system_prompt = get_system_prompt("bug_to_user_story_v2")

        required_sections = [
            "User Story",
            "Critérios de Aceitação",
            "Contexto Técnico",
            "Tasks Técnicas",
        ]

        for section in required_sections:
            assert section in system_prompt, (
                f"O prompt deve conter a seção: {section}"
            )

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        system_prompt = get_system_prompt("bug_to_user_story_v2")

        assert "[TODO]" not in system_prompt, "system_prompt contém [TODO] não resolvido"

    def test_minimum_techniques(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = get_system_prompt("bug_to_user_story_v2")

        assert "[ROLE PROMPTING]" in system_prompt, "system_prompt contém [ROLE PROMPTING]"
        assert "[FEW-SHOT PROMPTING]" in system_prompt, "system_prompt contém [FEW-SHOT PROMPTING]"
        assert "[CHAIN OF THOUGHT — CoT]" in system_prompt, "system_prompt contém [CHAIN OF THOUGHT — CoT]"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])