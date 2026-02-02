# Projeto PBL --- Disciplina de Compiladores

## Título do Projeto

**Construção de um Compilador Funcional para uma Linguagem de
Programação Minimalista (LPM)**

## Resumo da Proposta

Os estudantes desenvolverão ao longo da disciplina um compilador
completo para uma linguagem criada especialmente para o curso: **LPM
(Linguagem de Programação Minimalista)**. O projeto será realizado em
etapas alinhadas aos conteúdos das aulas, aplicando integralmente a
metodologia PBL.

------------------------------------------------------------------------

## Descrição da Linguagem LPM

-   Tipos: inteiro e booleano\
-   Operações: aritméticas, relacionais e lógicas\
-   Comandos: atribuição, if/else, while\
-   Entrada/saída: `print()`, `read()`\
-   Estrutura por blocos `{}`\
-   Variáveis: declaração implícita ou explícita

------------------------------------------------------------------------

## Objetivo Geral

Desenvolver um compilador funcional e documentado para a LPM,
compreendendo e implementando todas as fases da compilação.

## Objetivos Específicos

-   Projetar uma linguagem simples e formalizá-la.\
-   Implementar análise léxica, sintática e semântica.\
-   Construir uma IR (intermediate representation).\
-   Gerar código final (assembly ou bytecode).\
-   Aplicar otimizações básicas.\
-   Testar e documentar o compilador.

------------------------------------------------------------------------

# Metodologia PBL

## Problema Central

**Como construir um compilador completo, confiável e eficiente para uma
linguagem minimalista?**

## Contexto

Os alunos atuam como uma equipe de desenvolvimento de compiladores. O
professor age como facilitador.

## Produto Final

-   Compilador funcional\
-   Documentação técnica\
-   Conjunto de testes\
-   Apresentação final

------------------------------------------------------------------------

# Entregas Parciais

### **Entrega 1 --- Definição da Linguagem (Semana 2)**

-   Sintaxe e gramática BNF/EBNF\
-   Documento inicial da linguagem

### **Entrega 2 --- Analisador Léxico (Semana 4)**

-   Tokens e scanner\
-   Testes de validação

### **Entrega 3 --- Analisador Sintático (Semana 7)**

-   Parser LL/LR\
-   Construção da AST\
-   Tratamento de erros

### **Entrega 4 --- Análise Semântica (Semana 9)**

-   Tabelas de símbolos\
-   Verificação de tipos\
-   Regras de escopo

### **Entrega 5 --- IR (Semana 12)**

-   Definição e implementação da representação intermediária

### **Entrega 6 --- Geração de Código Final (Semana 15)**

-   Seleção de instruções\
-   Alocação de registradores\
-   Geração de assembly/bytecode

### **Entrega 7 --- Otimizações (Semana 17)**

-   Constant folding\
-   Dead code elimination\
-   Strength reduction

### **Entrega 8 --- Finalização e Apresentação (Semana 20)**

-   Demonstração\
-   Relatório e pitch técnico

------------------------------------------------------------------------

# Atividades Semanais

-   Abertura de problema\
-   Estudo independente\
-   Reuniões de equipe\
-   Minientregas semanais\
-   Compartilhamento entre grupos\
-   Feedback por pares

------------------------------------------------------------------------

# Papéis e Responsabilidades

### Estudantes

-   Protagonistas do processo\
-   Tomam decisões de arquitetura e design\
-   Documentam e testam o compilador

### Professor

-   Orienta, provoca e questiona\
-   Não entrega soluções prontas\
-   Media conflitos técnicos

------------------------------------------------------------------------

# Avaliação

### Formativa

-   Participação\
-   Minientregas\
-   Qualidade das decisões de design

### Somativa

-   Funcionamento do compilador (40%)\
-   Documentação (20%)\
-   Otimizações (15%)\
-   Testes e robustez (15%)\
-   Apresentação final (10%)

------------------------------------------------------------------------

# Tecnologias Recomendadas

-   Python, Java, C ou Rust\
-   Flex, Bison, ANTLR\
-   LLVM (opcional)\
-   Git para versionamento\
-   pytest ou JUnit para testes

------------------------------------------------------------------------

# Resultado Esperado

Ao final da disciplina, cada grupo deverá apresentar um compilador
funcional, demonstrando domínio das fases da compilação, capacidade de
trabalho em equipe e autonomia intelectual, conforme os princípios da
metodologia PBL.
