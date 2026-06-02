from search import search_prompt


def main():
    print("=== Chat Iniciado ===")
    print("Digite 'sair' para encerrar.\n")

    while True:
        question = input("Você: ").strip()

        if not question:
            continue

        if question.lower() == "sair":
            print("Encerrando o chat. Até mais!")
            break

        resposta = search_prompt(question)

        if resposta:
            print(f"\nAssistente: {resposta}\n")
        else:
            print("\nAssistente: Não foi possível processar sua pergunta.\n")

if __name__ == "__main__":
    main()