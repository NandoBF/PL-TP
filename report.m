
Daniel Pereira- a106912
Fernando Ferreira - a106878
José Fernandes - a104159

Grupo 61

Abstract

Para a _UC_ de Processamento de Linguagens, foi desenvolvido um compilador de _Fortran 77_,
este é capaz de analisar, interpretar e traduzir código _Fortran_ para um formato intermediário e deste para código máquina, que pode posteriormente ser executado na _VM EWVM_ disponibilizada pelo corpo docente.

## Arquitetura

### Léxica

(variaveis scope local)
(como diferenciar programa de funcao porque acaba ambos em end)

Inicialmente implementamos um _lexer_ responsável por converter o código _Fortran_ para uma lista de _tokens_, foi utilizada a biblioteca _ply.lex_. Este é encarregue de processar o código e descartar caracteres não semânticos restando apenas a lógica.
No que diz respeito às palavras-chaves o nosso sistema identifica 18 instruções distintas. Entre estas, definições de blocos e subprogramas (`PROGRAM`, `END`, `FUNCTION`, `SUBROUTINE`, `CALL` e `RETURN`), tipos de dados (`INTEGER`, `REAL` e `LOGICAL`), estruturas de controlo de fluxo (`IF`, `THEN`, `ELSE`, `ENDIF`, `DO`, `GOTO` e `CONTINUE`) e comandos de _IO_ (`READ` e `PRINT`). Para otimizar a deteção e suportar sintaxe  de forma _case sensitive_ optámos por capturar  primeiro o identificador genérico, transformá-lo em maiúsculas e validá-lo com um dicionário das palavras suportadas. Devido ao _Fortran_ utilizar pontos para operadores lógicos , definimos expressões regulares para isolar estes operadores como no caso de `.EQ.`, `.AND.` ou `.TRUE.` para garantir que estes não são identificados como pontuação, simultaneamente processamos os simbolos de operações aritméticas, parênteses e sinais de forma direta. Para valores numéricos o _lexer_ desenvolvido  faz a distinção de inteiros e decimais e para _strings_ é feita a separação  por plicas. Por fim é feita
uma contagem de quebras de linha para identificar o numero exato de linha e de modo a permitir o fluxo normal do _lexer_ sem interrupções, é feito um processamento de tolerância de erros quando é detetado um carácter não suportado.

### Sintática 

A seguinte etapa passa por analisar sintaticamente recorrendo ao módulo `ply.yacc`, que implementa  um parser _LALR(1)_, este consome os tokens gerados para validar a estrutura gramatical do código. Esta fase tem como objetivo validar a sintaxe e construir a Árvore de Sintaxe Abstrata (_AST_). O _AST_ na nossa implementação utiliza uma hierarquia de tuplos em _Python_ onde cada nó gerado representa uma operação ou estrutura, com o identificador da ação e as respetivas operações ou sub-blocos. Para reduzir  conflitos no _shift/reduce_, definimos uma tabela de prioridade, com atribuição de maior importância aos operadores de multiplicação, divisão  e de seguida adição e subtração. Num nivel de prioridade inferior agrupámos os operadores de comparação, durante esta etapa foi sempre establecida uma associação à esquerda para as operações, à parte do `NOT`  para que estas sejam lidas da forma expectada.

Em relação à amplitude da linguagem, a gramática implementada cobre os requisitos estipulados para o projeto, o nó raiz da estrutura sintática armazena unidades de compilação genéricas que se podem separar de forma modular no bloco principal do programa ou em subprogramas auxiliares, incluindo tanto funções com retorno como sub-rotinas. A partir do nó principal do programa, o analisador sintático desce para as regras específicas da linguagem. Na declaração de variáveis, o sistema distingue uma variável simples de um _array_ verificando a presença de parênteses com um valor numérico associado. Os comandos de entrada e saída, como `READ` e `PRINT`, foram implementados para suportar listas de expressões ou variáveis, oque permite operações com múltiplos valores numa única linha. De igual forma, as instruções de atribuição e o processamento de expressões matemáticas são resolvidos de forma direta, apartir da tabela de precedência já antes referida .

No que diz respeito ao controlo de fluxo, a gramática processa as condições e os ciclos de forma objetiva. Para a instrução `IF`, a regra avalia o comprimento dos _tokens_ capturados para perceber se o utilizador escreveu apenas um bloco `THEN` ou se incluiu também um bloco `ELSE`, construindo o nó da árvore em conformidade. Para os ciclos `DO`, é capturado o rótulo numérico de salto, a variável de iteração e os valores de início e fim. É importante notar que, nesta etapa, o compilador apenas guarda o rótulo numérico na estrutura da árvore, a verificação real para garantir que esse número corresponde a um comando `CONTINUE` válido é deixada exclusivamente para a análise semântica.

### Semântica

A fase de análise semântica foi implementada com recorrência ao padrão arquitetural _Visitor_, que percorre a Árvore de Sintaxe Abstrata (_AST_) de forma recursiva para validar o significado das operações. O isolamento de variáveis entre o programa principal e os subprogramas é garantido através de um sistema de tabelas temporárias. Antes de ler as instruções internas de um subprograma, o analisador cria uma nova tabela de símbolos temporária, que assim que a leitura desse bloco termina, a tabela local é descartada, garantindo que uma variável criada dentro de uma função não interfere com as variáveis do resto do programa.

Em simultâneo, a tabela de símbolos guarda o contexto de cada elemento, indicando estruturalmente se se trata de uma variável simples, um vetor ou uma função. Antes de iniciar a travessia principal, o analisador executa uma passagem para registar funções, como funções genéricas, e as definições escritas pelo utilizador. O sistema impõe também restrições léxicas do Fortran 77, que bloqueiam a compilação no caso de deteção de identificadores com caracteres não suportados.

Na validação de tipos (_Type Checking_), o compilador garante a consistência das operações, durante a atribuição, impede a mistura de tipos lógicos ou _strings_ com variáveis numéricas. Nas operações matemáticas, bloqueia cálculos entre booleanos e assegura a mudança automática do tipo inteiro para real quando operandos diferentes interagem. Através da consulta contínua à tabela de símbolos, o compilador consegue também emitir um aviso no terminal sempre que uma variável tenta ser utilizada sem ter sido previamente inicializada com um valor.

 Para os ciclos iterativos, o analisador captura os rótulos numéricos dos comandos `DO` e armazena-os numa _stack_. Quando um comando `CONTINUE` é encontrado, o sistema retira o elemento do topo dessa pilha e confirma a correspondência exata dos números, assegurando que não existem ciclos abertos ou fechados fora de ordem. Em paralelo, todas as instruções de salto `GOTO` são intercetadas e, no final da análise, cruzadas com a lista de rótulos existentes no código, interrompendo a compilação se detetar um salto para uma referência inexistente.

Por fim, o motor valida os subprogramas inspecionando cada comando `CALL` e invocações de funções. O analisador confirma não só a distinção correta entre os dois procedimentos, como verifica se o número de argumentos passados corresponde exatamente ao número exigido aquando da declaração na tabela de símbolos.

## Valorização

A otimização de código realizada incide diretamente na Árvore de Sintaxe Abstrata em tempo de compilação. A técnica principal implementada é _Constant Folding_, que deteta operações onde ambos os operandos são literais conhecidos e em vez de gerar múltiplas instruções para a máquina virtual, como empilhar dois valores distintos para depois executar uma adição, o compilador resolve o cálculo antecipadamente e gera um nó único com o resultado final. Este método aplica-se a todas as operações aritméticas e relacionais. Por exemplo, uma comparação matemática entre duas constantes é imediatamente reduzida a um valor lógico, o que poupa instruções geradas e liberta recursos de processamento.

Adicionalmente, foi incluída uma lógica de _Boolean Short-Circuit_. Numa operação lógica do tipo `AND`, se o lado esquerdo for avaliado como falso, o resultado final será garantidamente falso, tornando inútil a avaliação do lado direito. Nestes casos, o compilador simplesmente apaga o ramo direito da árvore e todo o seu processamento pendente, reduzindo o nó inteiro a uma constante falsa.

Este mecanismo alimenta de forma direta a eliminação de código morto nas estruturas condicionais. Se a condição de um bloco `IF` resultar numa constante estritamente verdadeira, o otimizador remove a instrução condicional e as respetivas referências de salto da máquina virtual, integrando os comandos executáveis diretamente no fluxo linear do programa. Pelo contrário, se a condição for avaliada como falsa, todo o código dentro do bloco `THEN` é apagado da geração final. Isto assegura que não é exportado código inalcançável para a máquina virtual oque reduz o espaço em disco e tempo de execução.

## Tradução



## Testes

## Instruções de Utilização

## Conclusão

