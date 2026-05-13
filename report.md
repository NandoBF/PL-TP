Daniel Pereira- a106912
Fernando Ferreira - a106878
José Fernandes - a104159

Grupo 61

Abstract

Para a _UC_ de Processamento de Linguagens, foi desenvolvido um compilador de _Fortran 77_,
este é capaz de analisar, interpretar e traduzir código _Fortran_ para um formato intermediário e deste para código máquina, que pode posteriormente ser executado na _VM EWVM_ disponibilizada pelo corpo docente.

## Arquitetura

### Léxica

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

A fase final do compilador é responsável por traduzir a Árvore de Sintaxe Abstrata, já otimizada, num ficheiro com extensão `.vm`, compatível com a arquitetura da máquina virtual  _EWVM_. Semelhante à análise semântica, a geração de código baseia-se no padrão _Visitor_ para percorrer hierarquicamente os nós da árvore, ao emitir as instruções equivalentes de forma sequencial através da função `emit`.

```
def traverse(self, node):
    if node is None:
        return

if isinstance(node, list):
    for n in node:
        self.traverse(n)
        return
        
node_type = node[0]
method_name = f'visit_{node_type}'
visitor = getattr(self, method_name, self.generic_visit)
visitor(node)

```

Durante o processamento das declarações (`visit_declare`), o compilador calcula o espaço necessário para acomodar escalares e vetoriais, emitindo a instrução `PUSHN` com a dimensão exata para a alocação do espaço para execução. Simultaneamente, o gerador interage com a Tabela de Símbolos para diferenciar contextos. Quando deteta o processamento de uma variável numa operação aritmética ou de atribuição, o compilador consulta ativamente a tabela para averiguar se a variável pertence ao âmbito global ou se é nativa da função atual.

```
# Exemplo da distinção na geração de código baseada no âmbito da variável 
info = self.table.lookup(name)
if info['is_global']: 
	self.emit(f"STOREG {address}") 
else: 
	self.emit(f"STOREL {address}")
```

Caso seja global, emite instruções focadas no Endereço Global (`STOREG`, `PUSHG`), caso contrário, recorre a instruções locais (`STOREL`, `PUSHL`). O endereço numérico da variável `address` é gerido autonomamente pela tabela ao longo de toda a compilação.

O acesso a _arrays_ exige uma lógica adicional, em vez de aceder a uma posição estática, o compilador emite instruções para colocar o endereço base na pilha (`PUSHGP` ou `PUSHFP`), calcula dinamicamente o índice, e utiliza a instrução de adição de endereços (`PADD`) combinada com uma subtração (`SUB`) para alinhar o acesso real na memória. Nas operações comuns, este mapeia diretamente as expressões matemáticas para as instruções nativas equivalentes . Nas operações _IO_, o compilador consulta o tipo da variável para assegurar a emissão da instrução correta: `WRITEI` para inteiros, `WRITEF` para reais e `WRITES` para series caracteres.

No que diz respeito aos subprogramas, a arquitetura  aquando da definição de uma função,  reserva preventivamente uma posição na memória com a instrução de empilhamento `PUSHN 1` dedicada exclusivamente a armazenar o valor de retorno. Em seguida, os argumentos originais são empilhados na ordem de leitura, antecedendo a instrução de salto para o bloco `CALL`.

O processamento do controlo de fluxo é executado mediante a geração e gestão dinâmica de referências. Este possui um mecanismo incremental de _labels, usado para demarcar os limites de blocos lógicos, como ciclos ou condições. O desvio das condições na instrução `IF` é gerido da seguinte forma: o código avalia as condições booleanas recorrendo aos operadores lógicos da máquina (como por exemplo `SUP` para comparações do tipo "maior que") e acopla ao resultado a instrução de salto caso zero (`JZ`),  isto força a máquina a ignorar as linhas subsequentes do ramo _True_ caso a expressão matemática do cabeçalho avalie de forma negativa.

```
# Exemplo do processamento de saltos condicionais 
self.traverse(cond) 
if else_branch is None: 
	end_label = self.new_label() 
	self.emit(f"JZ {end_label}") 
	self.traverse(then_branch) 
	self.emit(f"{end_label}:")
```

Por fim, os ciclos iterativos do Fortran 77 são mapeados de forma não linear. Quando o nó `DO` é lido, este avalia e guarda o valor inicial na variável de controlo, este fixa o rótulo da linha de reinício da repetição no documento. Posteriormente, e de forma isolada, quando o nó correspondente ao `CONTINUE` é atingido no fundo da árvore, o analisador reabre o ficheiro .vm, escreve as instruções para incrementar a variável de controlo em uma unidade (`PUSHI 1`, `ADD`) e efetua a verificação relacional do limite final da iteração (`INFEQ`). Se o limite não tiver sido quebrado, emite a instrução de salto cego em direção ao topo daquele rótulo de reinício.

## Testes

Para garantir a integridade do compilador, foi implementada um conjunto de testes. Esta arquitetura de validação recorre à framework nativa `unittest` do Python. A estratégia de testes encontra-se dividida em três conjuntos de análise. O primeiro foca-se na validação de sucesso através da função de teste de ficheiros válidos. O ficheiro de testes percorre a diretoria de ficheiros corretos, submetendo cada documento ao compilador. O teste apenas é considerado bem-sucedido se o sistema conseguir atravessar as fases léxica, sintática e semântica sem levantar exceções, culminando na verificação física da existência do ficheiro final com extensão `.vm` gerado.

```
# Validação da geração de código para ficheiros corretos 
compile_file(filepath, output_path) 
self.assertTrue(os.path.exists(output_path))
```

O segundo destina-se a testar o analisador perante código malformado. Através do processamento de uma pasta com ficheiros com falhas de escrita propositadas, o sistema de testes invoca o compilador exigindo, estritamente, que este falhe. A validação comprova que o módulo interceta a quebra das regras gramaticais e bloqueia a execução, confirmando o levantamento da exceção interna de erro sintático (`SyntaxError`).

```
# Verificação de falha obrigatória perante código malformado 
with self.assertRaises(SyntaxError, msg=f"File {filename} should have failed syntax analysis."): 
	compile_file(filepath)
```

Por fim, o terceiro  foca-se na validação de contexto e regras da linguagem. O sistema carrega um conjunto de programas com sintaxe perfeita, mas com erros lógicos introduzidos, como a utilização de variáveis não declaradas, invocações de subprogramas com inexistentes ou operações matemáticas com incompatibilidade de tipos. Este teste exige que o compilador aborte o processo e devolva o erro semântico específico (`SemanticError`).

```
# Interceção de erros lógicos e estruturais da linguagem
with self.assertRaises(SemanticError, msg=f"File {filename} should have failed semantic analysis."): 
	compile_file(filepath)
```

## Instruções de Utilização

Este capítulo detalha os procedimentos necessários para operar o compilador, desde a preparação do ambiente até à execução do código gerado na máquina virtual.

#### Pré-requisitos

O compilador foi desenvolvido em Python, exigindo que a máquina do utilizador possua o interpretador na versão 3 ou superior. Adicionalmente, a arquitetura de análise léxica e sintática depende da biblioteca externa PLY (Python Lex-Yacc). Por conseguinte, antes da primeira execução, o utilizador deve garantir a presença desta dependência.

#### Processo de Compilação

Para iniciar o processo de tradução do código escrito em Fortran 77, o utilizador deve assegurar que o documento de texto com o código se encontra na mesma pasta do projeto. A compilação é feita ao executar o ficheiro principal através do interpretador, passando o nome do ficheiro como argumento direto, com a seguinte sintaxe:

Bash

```
python main.py codigo.f
```

#### 4.3. Tratamento de Erros e Output

O comportamento do sistema perante a submissão de código obedece a dois cenários. No caso de uma compilação com sucesso, em que o código Fortran se apresenta válido e isento de erros lógicos, o resultado é a geração de um novo ficheiro na mesma diretoria, que preserva o nome original do documento, mas adota a extensão de máquina virtual `.vm`.

Pelo contrário, no caso de o analisador detetar falhas o ficheiro não é gerado e são imprimidos no terminal o motivo e a localização do erro detetado, orientando o utilizador para a respetiva correção no ficheiro.

#### 4.4. Execução

Concluída a compilação com êxito, o ficheiro resultante encontra-se pronto a ser processado. Para observar o comportamento prático do código, o utilizador deve invocar o executável da máquina virtual através da página fornecida pelos docentes em,  https://ewvm.epl.di.uminho.pt/.

## Conclusão


