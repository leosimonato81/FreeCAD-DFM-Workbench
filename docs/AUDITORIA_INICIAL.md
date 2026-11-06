# Auditoria inicial: DFM com FEM acoplado

Data: 2026-11-06  
Base: repositório `ryankembrey/FreeCAD-DFM-Workbench`, branch de trabalho `codex/dfm-fem-integration`.

## Material recebido

- `README.md`: requisitos do projeto, restrições e etapas de desenvolvimento.
- `a_PETG_DFM_2026-11-05.pdf` e `a_PETG_DFM_2026-11-06.pdf`: dois relatórios DFM do modelo `Shroud 001` (FDM, PETG), cada um com 33 erros, 8 avisos e 3 regras aprovadas. A diferença visível entre eles é principalmente a paginação e a distribuição das imagens de viewport; ambos reportam espessura mínima, ângulo de balanço e altura de cusp.
- `Imagem colada.png`: viewport FEM com malha, apoios e legenda de resultado.
- `Imagem colada (2).png`: viewport FEM com “Magnitude de Deslocamento”, malha e campo de cores.
- `Imagem colada (3).png`: histograma da magnitude de deslocamento em mm.
- Foram recebidos `a.FCStd` e um backup `.FCBak`. A versão corrigida de `a.FCStd` contém o documento `Shroud 001`, objetos FEM, malha e `CCX_Results`; a inspeção anterior que concluiu ausência de resultados corresponde a uma cópia anterior do arquivo. O backup antigo não contém resultados FEM.

## Estrutura e arquitetura encontradas

- `freecad/DFM/init_gui.py` registra a bancada, comandos e páginas de preferências. Os comandos principais aparecem na toolbar/menu “DFM”; a configuração e o painel de resultados são fluxos de tarefas separados.
- `freecad/DFM/gui/task_setup.py` configura o processo e lança análise. `app/analysis_runner.py` executa os analisadores. Os resultados estruturados usam `core/models.py` e regras/analisadores em `core/`.
- `freecad/DFM/gui/results/` contém a camada do painel, presenter, ponte de viewport e cena de destaque. `gui/results/bridge.py` coordena visibilidade e `HighlightScene`; o destaque atual esconde temporariamente o objeto e desenha uma cópia Coin com faces/arestas coloridas. `restore()` remove a cena e recupera a visibilidade anterior. Não encontrei alteração persistente de `ShapeColor` no caminho de destaque analisado.
- `freecad/DFM/gui/report/` implementa um fluxo de exportação mais novo: `ReportData` é o snapshot DFM, `ReportSettings` controla conteúdo e layout, `ReportDialog` oferece configuração/prévia, `ViewportCapture` captura imagens, e `layout.py`/`exporter.py` montam o PDF. A captura atual troca temporariamente a cena/câmera para imagens DFM e restaura a seleção de destaques e câmera ao finalizar.
- `gui/results/pdf_report.py` contém uma implementação PDF anterior, mas a busca estática encontrou a classe somente em sua definição. O fluxo chamado pelo presenter abre `gui/report/dialog.py`; a integração deve estender esse fluxo atual.
- `freecad/DFM/gui/utils/direction_row.py` já contém `DirectionRow`; a correção mencionada no README do projeto principal parece estar presente nesta revisão, mas isso precisa ser conferido com o patch específico usado na instalação Flatpak do usuário.
- `package.xml` declara FreeCAD mínimo 1.1.0, Python mínimo 3.11 e dependências `cadquery-ocp` e `gmsh`. A cópia não altera a instalação do FreeCAD nem instala dependências.

## Consequências para a integração

1. **Manter a análise DFM independente.** A integração deve ser uma ferramenta/aba própria. Ela pode receber um snapshot opcional dos resultados DFM e os resultados FEM disponíveis, sem tornar `AnalysisRunner` dependente de FEM.
2. **Reutilizar o pipeline novo de relatório.** Separar o conteúdo geral (metadados, imagens e tabelas) dos dados exclusivos da DFM é um passo necessário. Um modelo de relatório agregado pode conter blocos DFM e FEM opcionais, preservando a geração de relatórios quando um deles estiver ausente.
3. **Captura FEM da viewport atual.** O requisito de respeitar câmera, enquadramento e representação visível difere da captura DFM atual, que posiciona a câmera, substitui temporariamente a representação por `HighlightScene` e desenha destaques. A captura FEM deve ter caminho separado, chamando a API de imagem do viewport sem mudar a cena, com validação de restauração/estado e tratamento de falha.
4. **Aparência original.** O destaque DFM atual não colore o `ViewObject` diretamente, o que reduz risco de perder cores originais. Porém a cena alternativa pode ocultar o objeto e não é adequada para fotografar a visualização FEM já preparada. A futura integração deve controlar a sessão de destaque e restaurá-la antes de fotografar FEM; também deve considerar overlays/marcadores DFM e estados de visibilidade.
5. **Dados numéricos FEM.** O adaptador somente de leitura em `freecad/DFM/fem/results.py` lê `NodeNumbers`, `DisplacementLengths` e `vonMises` salvos no objeto de resultado. Não executa solver nem modifica malha ou resultados. O relatório mostra extremos, unidades e nós associados; não infere segurança ou falha sem critério de material. Reações e deformações ficam fora desta versão.
6. **Tarefas e bancadas.** O seletor mantém a bancada `DFM` original e oferece `DFM + FEM` com as ferramentas DFM mais o comando `DFM_FEMReport`. O comando abre o fluxo FEM-only sem análise DFM; a aba FEM também fica disponível no painel de resultados.

## Arquivos de referência para as próximas alterações

| Necessidade | Arquivos principais |
|---|---|
| Registro de comandos e menu | `freecad/DFM/init_gui.py`, `freecad/DFM/gui/tools/` |
| Painel Tasks / setup | `freecad/DFM/gui/task_setup.py`, `freecad/DFM/gui/task_results.py` |
| Estado e visualização DFM | `freecad/DFM/gui/results/bridge.py`, `highlight_scene.py`, `presenter.py` |
| Captura de viewport | `freecad/DFM/gui/report/capture.py` |
| Dados/opções e prévia do PDF | `freecad/DFM/gui/report/data.py`, `settings.py`, `dialog.py`, `layout.py`, `exporter.py` |
| Modelo de resultados e tipos | `freecad/DFM/core/models.py`, `freecad/DFM/gui/results/models.py` |

## Próxima sequência recomendada

1. Feito: o relatório atual foi estendido com conteúdo DFM/FEM independente e fluxo FEM-only, mantendo o snapshot DFM original.
2. Feito: o leitor foi conferido contra os arrays do `CCX_Results` corrigido e ganhou testes unitários de extremos, associação de nós e CSV.
3. Feito: a aba aceita várias capturas da viewport com legenda e inclusão individual. A captura combinada desliga realces DFM por padrão e restaura os realces após salvar a imagem.
4. Pendente: executar a validação visual e exportação integrada no FreeCAD 1.1.4. Não foi possível concluir esse teste pelo `FreeCADCmd` neste ambiente; portanto, a integração de GUI/PDF permanece sem validação nativa.

## Validação realizada nesta auditoria

- Leitura do README do projeto e documentação de arquitetura.
- Inspeção estática dos módulos de comandos, Tasks, destaques e relatório.
- Consulta à documentação oficial do FreeCAD sobre [resultados CalculiX](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/FEM_CalculiX.md) e [visualização de objetos Result](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/FEM_ResultShow.md), além do código oficial de pós-processamento FEM.
- Implementado o adaptador somente de leitura em `freecad/DFM/fem/results.py`, o resumo no PDF e CSV nodal opcional.
- Leitura dos arrays salvos em `CCX_Results` de `a.FCStd`: 40.349 nós; `DisplacementLengths` de 0,0 (nó 1) a 0,0001871214183540997 (nó 830); `vonMises` de 5,884090319394411e-06 (nó 1666) a 0,6137031012160827 (nó 19045). Os arrays permanecem pareados por índice com `NodeNumbers`.
- O backup `.FCBak` é anterior à análise e não substitui o `a.FCStd` corrigido como amostra FEM.
- Leitura de texto dos dois PDFs e inspeção visual das três imagens.
- `python3 tests/test_fem_results.py`: 3 testes aprovados. AST parse dos módulos Python e `git diff --check` também aprovados.
- A execução de `FreeCADCmd --console <macro>` falhou com `Unknown file`; nenhuma captura, janela de relatório ou PDF foi validada dentro do FreeCAD 1.1.4. Esse aceite integrado permanece pendente.
