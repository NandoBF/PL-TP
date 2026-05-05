# Otimização de Código 

## 1. Constant Folding (Dobragem de Constantes Aritméticas)
O Constant Folding é uma otimização executada em tempo de compilação que deteta operações em que ambos os operandos são literais conhecidos. Em vez de empilhar valores e deixar a máquina virtual EWVM executar uma instrução de `ADD` ou `MUL` em tempo de execução, o compilador faz as contas e gera um nó único com o valor final da conta (e.g. gera um `PUSHI 5` em vez de um `PUSHI 2`, `PUSHI 3`, `ADD`).
- **Aritmética:** Otimização suportada em todos os nós binários (`+`, `-`, `*`, `/`).
- **Relacional:** As igualdades e disparidades também são avaliadas previamente se os números forem constantes (ex: `10 .GT. 5` é imediatamente encurtado para um nó booleano `True`, reduzindo instruções e o uso de recursos de processamento).

## 2. Short-Circuit Booleano e Avaliação Lógica
Os nós de expressões com `.AND.`, `.OR.`, e `.NOT.` também contêm heurísticas de otimização:
- Duas constantes booleanas interagem diretamente para criar uma constante única (ex: `.TRUE. .AND. .FALSE.` vira logo um nó `False`).
- **Short-circuit:** Quando há operações booleanas pendentes em que o lado esquerdo é garantidamente determinístico na equação, o lado direito (e todo o seu processamento posterior) é apagado do código intermédio (Ex: Em `False .AND. (variável + 3 .GT. 10)`, uma vez que o lado esquerdo de um "AND" é falso, a AST cancela o ramo da direita e encolhe o nó inteiro apenas para a constante `False`).

## 3. Eliminação de Código Morto em IFs (Dead Code Elimination)
Uma análise de fluxo condicional básica foi incluída, que interseta o momento após o decorrer da Otimização Booleana:
- Caso o avaliador da condição no ramo de um `IF` resulte numa constante explícita `.TRUE.`, o gerador desfaz a instrução do `IF` e da *label* do salto (`JZ`), integrando diretamente os comandos do bloco "Then" de forma livre.
- Se, por outro lado, a condição der `.FALSE.`, o código inteiro que se encontra dentro do bloco `THEN` é completamente excluído (*Dead Code*) na geração do binário, salvaguardando espaço de disco e tempo de compilação.

