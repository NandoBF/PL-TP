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
No que diz respeito às palavras-chaves o nosso sistema identifica 18 instruções distintas. Entre estas, definições de blocos como _PROGRAM_, _FUNCTION_ e _SUBROUTINE_, tipos de dados _INTEGER_, _REAL_ e _LOGICAL_, estruturas de controlo de fluxo _IF_, _DO_, _GOTO_ e comandos de _IO_ _READ_ e _PRINT_. Para otimizar a deteção e suportar sintaxe  de forma _case sensitive_ optámos por capturar  primeiro o identificador genérico, transformá-lo em maiúsculas e validá-lo com um dicionário das palavras suportadas. Devido ao _Fortran_ utilizar pontos para operadores lógicos , definimos expressões regulares para isolar estes operadores como no caso de _.EQ._, _.AND._ ou _.TRUE._ para garantir que estes não são identificados como pontuação, simultaneamente processamos os simbolos de operações aritméticas, parênteses e sinais de forma direta. Para valores numéricos o _lexer_ desenvolvido  faz a distinção de inteiros e decimais e para _strings_ é feita a separação  por plicas. Por fim é feita
uma contagem de quebras de linha para identificar o numero exato de linha e de modo a permitir o fluxo normal do _lexer_ sem interrupções, é feito um processamento de tolerância de erros quando é detetado um carácter não suportado.

### Sintática 

### Semântica

## Valorização

## Tradução

## Instruções de Utilização

## Conclusão


