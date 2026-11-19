# ClassEval-T — 94 classes com gpt-4.1-mini

Atualizado em 19/11/2026 00:47 (São Paulo). API oficial OpenAI; uma execução por classe e direção.
Cobertura: **188/188** traduções registradas.

## Resumo

| Direção | Classes | Passaram | Falharam | Erros | Sem testes executados | Testes corretos | Smells após tradução | Após correção | Finais | Iterações de correção | Iterações de smells |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| python_to_java | 94/94 | 54 | 40 | 0 | 27 | 1309/1366 | 282 | 202 | 136 | 180 | 61 |
| java_to_python | 94/94 | 45 | 49 | 0 | 1 | 1422/2048 | 1429 | 1315 | 1098 | 188 | 135 |

`Testes corretos` soma os testes da linguagem de destino das classes concluídas. `0/0` significa que nenhum teste foi executado com sucesso, por exemplo por falha de compilação; essas classes continuam no denominador de 94 classes e não entram no denominador de testes. Smells são somas por direção: PMD 7.1.0 em Java e Pylint em Python. As contagens entre ferramentas não são diretamente comparáveis.

## Resultado por classe

Na trajetória, `T0` é a tradução inicial, `C1–C3` são correções e `S1–S3` são candidatos de redução de smells. Cada parêntese mostra `testes corretos/total; smells`. `✓` indica refatoração aceita e `×`, rejeitada.

| Direção | Classe | Estado | Testes finais | Smells T/C/F | Correções | Loops de smells | Trajetória |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| python_to_java | AccessGatewayFilter | failed | 17/18 | 8/8/8 | 3 | 0 | T0 (17/18; 8) → C1 (17/18; 8) → C2 (17/18; 8) → C3 (17/18; 8) |
| python_to_java | AreaCalculator | passed | 26/26 | 7/0/0 | 1 | 0 | T0 (0/0; 7) → C1 (26/26; 0) |
| python_to_java | ArgumentParser | passed | 21/21 | 0/0/0 | 3 | 0 | T0 (0/0; 0) → C1 (0/0; 1) → C2 (0/0; 0) → C3 (21/21; 0) |
| python_to_java | ArrangementCalculator | passed | 27/27 | 3/0/0 | 1 | 0 | T0 (0/0; 3) → C1 (27/27; 0) |
| python_to_java | AssessmentSystem | passed | 31/31 | 8/2/2 | 2 | 3 | T0 (0/0; 8) → C1 (0/0; 2) → C2 (31/31; 2) → S1 (0/0; 0 ×) → S2 (0/0; 0 ×) → S3 (0/0; 0 ×) |
| python_to_java | AutomaticGuitarSimulator | passed | 14/14 | 0/3/3 | 2 | 3 | T0 (0/0; 0) → C1 (12/14; 2) → C2 (14/14; 3) → S1 (12/14; 0 ×) → S2 (12/14; 0 ×) → S3 (12/14; 0 ×) |
| python_to_java | AvgPartition | passed | 12/12 | 0/0/0 | 0 | 0 | T0 (12/12; 0) |
| python_to_java | BalancedBrackets | passed | 15/15 | 0/0/0 | 1 | 0 | T0 (0/0; 0) → C1 (15/15; 0) |
| python_to_java | BankAccount | passed | 23/23 | 2/0/0 | 1 | 0 | T0 (0/0; 2) → C1 (23/23; 0) |
| python_to_java | BigNumCalculator | passed | 17/17 | 4/4/4 | 1 | 3 | T0 (11/17; 4) → C1 (17/17; 4) → S1 (0/0; 0 ×) → S2 (0/0; 0 ×) → S3 (0/0; 0 ×) |
| python_to_java | BinaryDataProcessor | failed | 0/0 | 0/2/2 | 3 | 0 | T0 (0/0; 0) → C1 (0/0; 2) → C2 (0/0; 0) → C3 (0/0; 2) |
| python_to_java | BitStatusUtil | passed | 22/22 | 1/1/0 | 1 | 1 | T0 (0/0; 1) → C1 (22/22; 1) → S1 (22/22; 0 ✓) |
| python_to_java | BlackjackGame | passed | 17/17 | 0/0/0 | 1 | 0 | T0 (0/0; 0) → C1 (17/17; 0) |
| python_to_java | BookManagement | passed | 20/20 | 0/0/0 | 0 | 0 | T0 (20/20; 0) |
| python_to_java | BookManagementDB | failed | 0/7 | 7/7/7 | 3 | 0 | T0 (0/0; 7) → C1 (0/7; 7) → C2 (0/7; 7) → C3 (0/7; 7) |
| python_to_java | BoyerMooreSearch | failed | 0/0 | 3/0/0 | 3 | 0 | T0 (0/0; 3) → C1 (0/0; 0) → C2 (0/0; 0) → C3 (0/0; 0) |
| python_to_java | CSVProcessor | failed | 0/0 | 7/4/4 | 3 | 0 | T0 (0/0; 7) → C1 (0/0; 4) → C2 (0/0; 4) → C3 (0/0; 4) |
| python_to_java | Calculator | passed | 20/20 | 1/5/5 | 1 | 3 | T0 (0/0; 1) → C1 (20/20; 5) → S1 (0/0; 0 ×) → S2 (0/0; 0 ×) → S3 (0/0; 0 ×) |
| python_to_java | CalendarUtil | failed | 0/0 | 4/6/6 | 3 | 0 | T0 (0/0; 4) → C1 (0/0; 6) → C2 (0/0; 6) → C3 (0/0; 6) |
| python_to_java | CamelCaseMap | failed | 0/0 | 1/0/0 | 3 | 0 | T0 (0/0; 1) → C1 (0/0; 0) → C2 (0/0; 0) → C3 (0/0; 0) |
| python_to_java | ChandrasekharSieve | passed | 11/11 | 0/0/0 | 0 | 0 | T0 (11/11; 0) |
| python_to_java | Chat | passed | 22/22 | 0/2/0 | 1 | 1 | T0 (0/0; 0) → C1 (22/22; 2) → S1 (22/22; 0 ✓) |
| python_to_java | ClassRegistrationSystem | passed | 16/16 | 1/3/0 | 2 | 1 | T0 (0/0; 1) → C1 (0/0; 3) → C2 (16/16; 3) → S1 (16/16; 0 ✓) |
| python_to_java | Classroom | failed | 0/0 | 0/2/2 | 3 | 0 | T0 (0/0; 0) → C1 (0/0; 0) → C2 (0/0; 0) → C3 (0/0; 2) |
| python_to_java | CombinationCalculator | failed | 0/0 | 3/1/1 | 3 | 0 | T0 (0/0; 3) → C1 (0/0; 1) → C2 (0/0; 1) → C3 (0/0; 1) |
| python_to_java | ComplexCalculator | passed | 21/21 | 3/3/3 | 1 | 3 | T0 (0/0; 3) → C1 (21/21; 3) → S1 (0/0; 0 ×) → S2 (0/0; 0 ×) → S3 (0/0; 0 ×) |
| python_to_java | CookiesUtil | passed | 19/19 | 1/4/4 | 2 | 3 | T0 (0/0; 1) → C1 (0/0; 4) → C2 (19/19; 4) → S1 (0/0; 0 ×) → S2 (0/0; 0 ×) → S3 (0/0; 0 ×) |
| python_to_java | CurrencyConverter | failed | 22/23 | 2/2/2 | 3 | 0 | T0 (0/0; 2) → C1 (22/23; 2) → C2 (0/0; 2) → C3 (22/23; 2) |
| python_to_java | DataStatistics | passed | 16/16 | 1/1/0 | 1 | 1 | T0 (0/0; 1) → C1 (16/16; 1) → S1 (16/16; 0 ✓) |
| python_to_java | DataStatistics2 | passed | 30/30 | 6/0/0 | 1 | 0 | T0 (0/0; 6) → C1 (30/30; 0) |
| python_to_java | DataStatistics4 | failed | 0/0 | 6/5/5 | 3 | 0 | T0 (0/0; 6) → C1 (0/0; 5) → C2 (0/0; 5) → C3 (0/0; 5) |
| python_to_java | DatabaseProcessor | failed | 0/4 | 0/0/0 | 3 | 0 | T0 (0/0; 0) → C1 (0/0; 0) → C2 (0/4; 0) → C3 (0/4; 0) |
| python_to_java | DecryptionUtils | passed | 19/19 | 5/1/0 | 1 | 1 | T0 (0/0; 5) → C1 (19/19; 1) → S1 (19/19; 0 ✓) |
| python_to_java | DiscountStrategy | failed | 0/0 | 3/0/0 | 3 | 0 | T0 (0/0; 3) → C1 (0/0; 3) → C2 (0/0; 0) → C3 (0/0; 0) |
| python_to_java | EightPuzzle | passed | 13/13 | 8/8/1 | 0 | 3 | T0 (13/13; 8) → S1 (13/13; 4 ✓) → S2 (13/13; 1 ✓) → S3 (13/13; 1 ×) |
| python_to_java | EmailClient | passed | 20/20 | 9/2/2 | 2 | 3 | T0 (0/0; 9) → C1 (17/20; 2) → C2 (20/20; 2) → S1 (19/20; 1 ×) → S2 (19/20; 1 ×) → S3 (19/20; 1 ×) |
| python_to_java | EncryptionUtils | passed | 18/18 | 10/2/0 | 1 | 1 | T0 (0/0; 10) → C1 (18/18; 2) → S1 (18/18; 0 ✓) |
| python_to_java | ExcelProcessor | failed | 0/0 | 7/6/6 | 3 | 0 | T0 (0/0; 7) → C1 (0/0; 6) → C2 (0/0; 6) → C3 (0/0; 6) |
| python_to_java | ExpressionCalculator | failed | 0/0 | 1/1/1 | 3 | 0 | T0 (0/0; 1) → C1 (0/0; 1) → C2 (0/0; 1) → C3 (0/0; 1) |
| python_to_java | FitnessTracker | passed | 16/16 | 6/3/0 | 3 | 1 | T0 (0/0; 6) → C1 (10/16; 5) → C2 (10/16; 3) → C3 (16/16; 3) → S1 (16/16; 0 ✓) |
| python_to_java | GomokuGame | failed | 0/0 | 0/0/0 | 3 | 0 | T0 (0/0; 0) → C1 (0/0; 0) → C2 (0/0; 0) → C3 (0/0; 0) |
| python_to_java | HRManagementSystem | failed | 0/0 | 1/0/0 | 3 | 0 | T0 (0/0; 1) → C1 (0/0; 1) → C2 (0/0; 0) → C3 (0/0; 0) |
| python_to_java | Hotel | failed | 0/0 | 1/0/0 | 3 | 0 | T0 (0/0; 1) → C1 (0/0; 0) → C2 (18/23; 0) → C3 (0/0; 0) |
| python_to_java | IPAddress | passed | 15/15 | 0/0/0 | 1 | 0 | T0 (10/15; 0) → C1 (15/15; 0) |
| python_to_java | Interpolation | passed | 12/12 | 9/7/0 | 1 | 1 | T0 (0/0; 9) → C1 (12/12; 7) → S1 (12/12; 0 ✓) |
| python_to_java | IpUtil | failed | 0/0 | 1/2/2 | 3 | 0 | T0 (0/0; 1) → C1 (0/0; 2) → C2 (0/0; 2) → C3 (0/0; 2) |
| python_to_java | JSONProcessor | failed | 0/0 | 3/4/4 | 3 | 0 | T0 (0/0; 3) → C1 (0/0; 6) → C2 (0/0; 4) → C3 (0/0; 4) |
| python_to_java | JobMarketplace | passed | 36/36 | 4/8/0 | 2 | 1 | T0 (0/0; 4) → C1 (0/0; 15) → C2 (36/36; 8) → S1 (36/36; 0 ✓) |
| python_to_java | KappaCalculator | passed | 10/10 | 10/9/0 | 1 | 1 | T0 (0/0; 10) → C1 (10/10; 9) → S1 (10/10; 0 ✓) |
| python_to_java | LongestWord | passed | 10/10 | 1/1/1 | 1 | 3 | T0 (0/0; 1) → C1 (10/10; 1) → S1 (0/0; 0 ×) → S2 (0/0; 0 ×) → S3 (0/0; 0 ×) |
| python_to_java | MahjongConnect | failed | 22/28 | 10/12/12 | 3 | 0 | T0 (0/0; 10) → C1 (22/28; 11) → C2 (22/28; 11) → C3 (22/28; 12) |
| python_to_java | Manacher | failed | 0/0 | 0/0/0 | 3 | 0 | T0 (0/0; 0) → C1 (0/0; 0) → C2 (0/0; 0) → C3 (0/0; 0) |
| python_to_java | MetricsCalculator | passed | 29/29 | 11/10/10 | 2 | 3 | T0 (0/0; 11) → C1 (0/0; 11) → C2 (29/29; 10) → S1 (0/0; 0 ×) → S2 (0/0; 0 ×) → S3 (0/0; 0 ×) |
| python_to_java | MetricsCalculator2 | passed | 16/16 | 1/1/0 | 2 | 1 | T0 (0/0; 1) → C1 (0/0; 1) → C2 (16/16; 1) → S1 (16/16; 0 ✓) |
| python_to_java | MovieBookingSystem | failed | 0/0 | 8/5/5 | 3 | 0 | T0 (0/0; 8) → C1 (0/0; 7) → C2 (0/0; 7) → C3 (0/0; 5) |
| python_to_java | MovieTicketDB | failed | 0/0 | 4/4/4 | 3 | 0 | T0 (0/0; 4) → C1 (0/0; 4) → C2 (0/16; 4) → C3 (0/0; 4) |
| python_to_java | MusicPlayer | failed | 0/0 | 7/0/0 | 3 | 0 | T0 (0/0; 7) → C1 (0/0; 0) → C2 (0/0; 0) → C3 (0/0; 0) |
| python_to_java | NLPDataProcessor | passed | 11/11 | 0/0/0 | 0 | 0 | T0 (11/11; 0) |
| python_to_java | NLPDataProcessor2 | failed | 0/0 | 3/1/1 | 3 | 0 | T0 (0/0; 3) → C1 (0/0; 1) → C2 (0/0; 2) → C3 (0/0; 1) |
| python_to_java | NumberConverter | passed | 31/31 | 1/1/0 | 0 | 1 | T0 (31/31; 1) → S1 (31/31; 0 ✓) |
| python_to_java | NumberWordFormatter | passed | 28/28 | 4/4/0 | 0 | 1 | T0 (28/28; 4) → S1 (28/28; 0 ✓) |
| python_to_java | NumericEntityUnescaper | failed | 13/17 | 1/1/1 | 3 | 0 | T0 (15/17; 1) → C1 (15/17; 1) → C2 (16/17; 1) → C3 (13/17; 1) |
| python_to_java | Order | passed | 17/17 | 2/0/0 | 3 | 0 | T0 (0/0; 2) → C1 (7/17; 0) → C2 (12/17; 0) → C3 (17/17; 0) |
| python_to_java | PageUtil | passed | 16/16 | 0/4/0 | 2 | 1 | T0 (0/0; 0) → C1 (15/16; 4) → C2 (16/16; 4) → S1 (16/16; 0 ✓) |
| python_to_java | PersonRequest | passed | 16/16 | 0/0/0 | 0 | 0 | T0 (16/16; 0) |
| python_to_java | PushBoxGame | failed | 0/0 | 4/4/4 | 3 | 0 | T0 (0/0; 4) → C1 (14/16; 4) → C2 (0/0; 4) → C3 (0/0; 4) |
| python_to_java | RPGCharacter | passed | 26/26 | 0/0/0 | 0 | 0 | T0 (26/26; 0) |
| python_to_java | RegexUtils | failed | 0/0 | 7/0/0 | 3 | 0 | T0 (0/0; 7) → C1 (0/0; 0) → C2 (0/0; 0) → C3 (0/0; 0) |
| python_to_java | SQLGenerator | failed | 0/0 | 2/2/2 | 3 | 0 | T0 (0/0; 2) → C1 (0/0; 2) → C2 (0/0; 2) → C3 (0/0; 2) |
| python_to_java | SQLQueryBuilder | failed | 18/25 | 1/1/1 | 3 | 0 | T0 (0/0; 1) → C1 (18/25; 1) → C2 (0/0; 1) → C3 (18/25; 1) |
| python_to_java | Server | failed | 14/26 | 2/0/0 | 3 | 0 | T0 (0/0; 2) → C1 (14/26; 0) → C2 (14/26; 0) → C3 (14/26; 0) |
| python_to_java | ShoppingCart | passed | 23/23 | 6/2/0 | 2 | 1 | T0 (0/0; 6) → C1 (22/23; 2) → C2 (23/23; 2) → S1 (23/23; 0 ✓) |
| python_to_java | SignInSystem | passed | 26/26 | 0/0/0 | 0 | 0 | T0 (26/26; 0) |
| python_to_java | Snake | passed | 21/21 | 0/2/0 | 2 | 1 | T0 (0/0; 0) → C1 (0/0; 2) → C2 (21/21; 2) → S1 (21/21; 0 ✓) |
| python_to_java | SplitSentence | passed | 16/16 | 4/0/0 | 1 | 0 | T0 (0/0; 4) → C1 (16/16; 0) |
| python_to_java | Statistics3 | failed | 35/36 | 3/3/3 | 3 | 0 | T0 (0/0; 3) → C1 (0/0; 3) → C2 (0/0; 3) → C3 (35/36; 3) |
| python_to_java | StockPortfolioTracker | failed | 12/14 | 2/6/6 | 3 | 0 | T0 (12/14; 2) → C1 (12/14; 6) → C2 (12/14; 6) → C3 (12/14; 6) |
| python_to_java | StudentDatabaseProcessor | failed | 0/0 | 0/0/0 | 3 | 0 | T0 (0/0; 0) → C1 (0/0; 0) → C2 (0/0; 2) → C3 (0/0; 0) |
| python_to_java | TextFileProcessor | passed | 20/20 | 0/4/4 | 1 | 3 | T0 (0/0; 0) → C1 (20/20; 4) → S1 (0/0; 0 ×) → S2 (0/0; 0 ×) → S3 (0/0; 0 ×) |
| python_to_java | Thermostat | passed | 36/36 | 0/0/0 | 1 | 0 | T0 (0/0; 0) → C1 (36/36; 0) |
| python_to_java | TicTacToe | passed | 16/16 | 4/1/0 | 1 | 1 | T0 (0/0; 4) → C1 (16/16; 1) → S1 (16/16; 0 ✓) |
| python_to_java | TimeUtils | passed | 36/36 | 9/2/2 | 1 | 3 | T0 (0/0; 9) → C1 (36/36; 2) → S1 (0/0; 0 ×) → S2 (0/0; 0 ×) → S3 (0/0; 0 ×) |
| python_to_java | TriCalculator | failed | 0/0 | 2/2/2 | 3 | 0 | T0 (0/0; 2) → C1 (0/0; 2) → C2 (0/0; 2) → C3 (0/0; 2) |
| python_to_java | TwentyFourPointGame | failed | 10/18 | 1/0/0 | 3 | 0 | T0 (0/0; 1) → C1 (10/18; 0) → C2 (0/0; 0) → C3 (10/18; 0) |
| python_to_java | URLHandler | passed | 32/32 | 7/1/1 | 1 | 3 | T0 (0/0; 7) → C1 (32/32; 1) → S1 (31/32; 0 ×) → S2 (31/32; 0 ×) → S3 (31/32; 0 ×) |
| python_to_java | UrlPath | passed | 19/19 | 2/2/0 | 0 | 1 | T0 (19/19; 2) → S1 (19/19; 0 ✓) |
| python_to_java | UserLoginDB | failed | 0/0 | 1/0/0 | 3 | 0 | T0 (0/0; 1) → C1 (0/0; 0) → C2 (0/0; 1) → C3 (0/0; 0) |
| python_to_java | VectorUtil | passed | 22/22 | 2/1/0 | 1 | 1 | T0 (0/0; 2) → C1 (22/22; 1) → S1 (22/22; 0 ✓) |
| python_to_java | VendingMachine | passed | 27/27 | 8/2/0 | 2 | 1 | T0 (0/0; 8) → C1 (19/27; 2) → C2 (27/27; 2) → S1 (27/27; 0 ✓) |
| python_to_java | Warehouse | failed | 29/32 | 0/0/0 | 3 | 0 | T0 (0/0; 0) → C1 (29/32; 0) → C2 (0/0; 0) → C3 (29/32; 0) |
| python_to_java | WeatherSystem | failed | 21/22 | 2/3/3 | 3 | 0 | T0 (0/0; 2) → C1 (21/22; 3) → C2 (0/0; 2) → C3 (21/22; 3) |
| python_to_java | Words2Numbers | passed | 13/13 | 2/1/0 | 1 | 1 | T0 (0/0; 2) → C1 (13/13; 1) → S1 (13/13; 0 ✓) |
| python_to_java | XMLProcessor | passed | 12/12 | 1/1/0 | 1 | 1 | T0 (0/0; 1) → C1 (12/12; 1) → S1 (12/12; 0 ✓) |
| python_to_java | ZipFileProcessor | passed | 18/18 | 0/0/0 | 0 | 0 | T0 (18/18; 0) |
| java_to_python | AccessGatewayFilter | failed | 9/19 | 12/12/12 | 3 | 0 | T0 (9/19; 12) → C1 (9/19; 12) → C2 (9/19; 12) → C3 (9/19; 12) |
| java_to_python | AreaCalculator | failed | 21/26 | 8/8/8 | 3 | 0 | T0 (21/26; 8) → C1 (21/26; 8) → C2 (21/26; 8) → C3 (21/26; 8) |
| java_to_python | ArgumentParser | failed | 0/21 | 20/20/20 | 3 | 0 | T0 (0/21; 20) → C1 (0/21; 20) → C2 (0/21; 20) → C3 (0/21; 20) |
| java_to_python | ArrangementCalculator | passed | 27/27 | 15/13/2 | 1 | 3 | T0 (15/27; 15) → C1 (27/27; 13) → S1 (27/27; 8 ✓) → S2 (27/27; 2 ✓) → S3 (27/27; 2 ×) |
| java_to_python | AssessmentSystem | failed | 10/31 | 26/16/16 | 3 | 0 | T0 (0/31; 26) → C1 (6/31; 15) → C2 (6/31; 16) → C3 (10/31; 16) |
| java_to_python | AutomaticGuitarSimulator | failed | 1/15 | 10/11/11 | 3 | 0 | T0 (1/15; 10) → C1 (1/15; 10) → C2 (7/15; 11) → C3 (1/15; 11) |
| java_to_python | AvgPartition | passed | 11/11 | 6/6/6 | 1 | 3 | T0 (5/11; 6) → C1 (11/11; 6) → S1 (5/11; 3 ×) → S2 (5/11; 3 ×) → S3 (5/11; 3 ×) |
| java_to_python | BalancedBrackets | passed | 15/15 | 14/11/11 | 1 | 3 | T0 (0/15; 14) → C1 (15/15; 11) → S1 (7/15; 3 ×) → S2 (7/15; 4 ×) → S3 (7/15; 3 ×) |
| java_to_python | BankAccount | passed | 22/22 | 9/7/3 | 1 | 3 | T0 (9/22; 9) → C1 (22/22; 7) → S1 (22/22; 3 ✓) → S2 (12/22; 6 ×) → S3 (22/22; 6 ×) |
| java_to_python | BigNumCalculator | passed | 17/17 | 6/6/3 | 0 | 3 | T0 (17/17; 6) → S1 (17/17; 3 ✓) → S2 (17/17; 3 ×) → S3 (17/17; 3 ×) |
| java_to_python | BinaryDataProcessor | passed | 21/21 | 14/11/8 | 1 | 3 | T0 (15/21; 14) → C1 (21/21; 11) → S1 (21/21; 8 ✓) → S2 (15/21; 9 ×) → S3 (15/21; 8 ×) |
| java_to_python | BitStatusUtil | passed | 21/21 | 7/7/2 | 1 | 3 | T0 (15/21; 7) → C1 (21/21; 7) → S1 (21/21; 2 ✓) → S2 (21/21; 2 ×) → S3 (21/21; 2 ×) |
| java_to_python | BlackjackGame | passed | 18/18 | 9/9/4 | 0 | 3 | T0 (18/18; 9) → S1 (18/18; 4 ✓) → S2 (18/18; 4 ×) → S3 (18/18; 4 ×) |
| java_to_python | BookManagement | passed | 21/21 | 8/8/2 | 1 | 3 | T0 (9/21; 8) → C1 (21/21; 8) → S1 (21/21; 2 ✓) → S2 (5/21; 6 ×) → S3 (5/21; 6 ×) |
| java_to_python | BookManagementDB | failed | 0/7 | 37/37/37 | 3 | 0 | T0 (0/7; 37) → C1 (0/7; 37) → C2 (0/7; 37) → C3 (0/7; 37) |
| java_to_python | BoyerMooreSearch | passed | 16/16 | 6/6/4 | 0 | 3 | T0 (16/16; 6) → S1 (16/16; 4 ✓) → S2 (16/16; 4 ×) → S3 (16/16; 4 ×) |
| java_to_python | CSVProcessor | passed | 17/17 | 18/15/15 | 1 | 3 | T0 (0/17; 18) → C1 (17/17; 15) → S1 (0/1; 2 ×) → S2 (0/1; 2 ×) → S3 (0/1; 2 ×) |
| java_to_python | Calculator | failed | 13/19 | 10/9/9 | 3 | 0 | T0 (13/19; 10) → C1 (13/19; 10) → C2 (13/19; 10) → C3 (13/19; 9) |
| java_to_python | CalendarUtil | failed | 11/29 | 12/13/13 | 3 | 0 | T0 (11/29; 12) → C1 (11/29; 13) → C2 (11/29; 13) → C3 (11/29; 13) |
| java_to_python | CamelCaseMap | failed | 0/0 | 10/8/8 | 3 | 0 | T0 (10/37; 10) → C1 (0/0; 10) → C2 (11/37; 11) → C3 (0/0; 8) |
| java_to_python | ChandrasekharSieve | passed | 11/11 | 5/5/5 | 1 | 3 | T0 (1/11; 5) → C1 (11/11; 5) → S1 (1/11; 3 ×) → S2 (1/11; 3 ×) → S3 (1/11; 3 ×) |
| java_to_python | Chat | failed | 16/22 | 24/15/15 | 3 | 0 | T0 (0/22; 24) → C1 (16/22; 15) → C2 (16/22; 15) → C3 (16/22; 15) |
| java_to_python | ClassRegistrationSystem | failed | 0/16 | 31/31/31 | 3 | 0 | T0 (0/16; 31) → C1 (0/16; 31) → C2 (3/16; 26) → C3 (0/16; 31) |
| java_to_python | Classroom | failed | 23/24 | 9/15/15 | 3 | 0 | T0 (12/24; 9) → C1 (17/24; 10) → C2 (22/24; 15) → C3 (23/24; 15) |
| java_to_python | CombinationCalculator | failed | 18/26 | 15/13/13 | 3 | 0 | T0 (10/26; 15) → C1 (18/26; 13) → C2 (10/26; 15) → C3 (18/26; 13) |
| java_to_python | ComplexCalculator | passed | 21/21 | 17/19/10 | 2 | 3 | T0 (0/21; 17) → C1 (0/21; 18) → C2 (21/21; 19) → S1 (21/21; 10 ✓) → S2 (21/21; 10 ×) → S3 (21/21; 10 ×) |
| java_to_python | CookiesUtil | passed | 19/19 | 8/8/8 | 0 | 3 | T0 (19/19; 8) → S1 (2/19; 9 ×) → S2 (2/19; 9 ×) → S3 (2/19; 9 ×) |
| java_to_python | CurrencyConverter | passed | 24/24 | 8/8/8 | 1 | 3 | T0 (17/24; 8) → C1 (24/24; 8) → S1 (12/24; 2 ×) → S2 (12/24; 2 ×) → S3 (12/24; 2 ×) |
| java_to_python | DataStatistics | passed | 16/16 | 9/9/2 | 0 | 3 | T0 (16/16; 9) → S1 (16/16; 5 ✓) → S2 (16/16; 2 ✓) → S3 (16/16; 2 ×) |
| java_to_python | DataStatistics2 | passed | 31/31 | 16/10/3 | 2 | 3 | T0 (0/31; 16) → C1 (25/31; 10) → C2 (31/31; 10) → S1 (31/31; 3 ✓) → S2 (31/31; 9 ×) → S3 (31/31; 9 ×) |
| java_to_python | DataStatistics4 | failed | 19/21 | 9/8/8 | 3 | 0 | T0 (14/21; 9) → C1 (19/21; 8) → C2 (19/21; 8) → C3 (19/21; 8) |
| java_to_python | DatabaseProcessor | passed | 21/21 | 9/9/9 | 1 | 3 | T0 (18/21; 9) → C1 (21/21; 9) → S1 (0/21; 10 ×) → S2 (0/21; 14 ×) → S3 (0/21; 10 ×) |
| java_to_python | DecryptionUtils | passed | 19/19 | 12/9/3 | 1 | 3 | T0 (0/19; 12) → C1 (19/19; 9) → S1 (19/19; 3 ✓) → S2 (19/19; 5 ×) → S3 (19/19; 5 ×) |
| java_to_python | DiscountStrategy | failed | 0/26 | 28/28/28 | 3 | 0 | T0 (0/26; 28) → C1 (0/26; 28) → C2 (0/26; 28) → C3 (0/26; 28) |
| java_to_python | EightPuzzle | passed | 21/21 | 13/13/13 | 1 | 3 | T0 (19/21; 13) → C1 (21/21; 13) → S1 (16/21; 12 ×) → S2 (16/21; 8 ×) → S3 (16/21; 10 ×) |
| java_to_python | EmailClient | failed | 12/26 | 13/13/13 | 3 | 0 | T0 (12/26; 13) → C1 (12/26; 13) → C2 (12/26; 12) → C3 (12/26; 13) |
| java_to_python | EncryptionUtils | passed | 18/18 | 15/12/2 | 1 | 3 | T0 (0/18; 15) → C1 (18/18; 12) → S1 (18/18; 2 ✓) → S2 (18/18; 3 ×) → S3 (18/18; 3 ×) |
| java_to_python | ExcelProcessor | failed | 0/19 | 13/16/16 | 3 | 0 | T0 (0/1; 13) → C1 (0/1; 12) → C2 (0/19; 13) → C3 (0/19; 16) |
| java_to_python | ExpressionCalculator | failed | 23/37 | 19/13/13 | 3 | 0 | T0 (18/37; 19) → C1 (23/37; 12) → C2 (23/37; 12) → C3 (23/37; 13) |
| java_to_python | FitnessTracker | passed | 16/16 | 14/12/12 | 1 | 3 | T0 (0/16; 14) → C1 (16/16; 12) → S1 (10/16; 2 ×) → S2 (10/16; 2 ×) → S3 (10/16; 2 ×) |
| java_to_python | GomokuGame | passed | 16/16 | 6/5/5 | 1 | 3 | T0 (10/16; 6) → C1 (16/16; 5) → S1 (10/16; 2 ×) → S2 (10/16; 2 ×) → S3 (10/16; 2 ×) |
| java_to_python | HRManagementSystem | passed | 28/28 | 30/25/2 | 1 | 3 | T0 (0/28; 30) → C1 (28/28; 25) → S1 (28/28; 8 ✓) → S2 (28/28; 7 ✓) → S3 (28/28; 2 ✓) |
| java_to_python | Hotel | failed | 19/23 | 22/9/9 | 3 | 0 | T0 (0/23; 22) → C1 (19/23; 9) → C2 (21/23; 9) → C3 (19/23; 9) |
| java_to_python | IPAddress | passed | 16/16 | 6/6/2 | 0 | 3 | T0 (16/16; 6) → S1 (16/16; 2 ✓) → S2 (16/16; 5 ×) → S3 (16/16; 5 ×) |
| java_to_python | Interpolation | passed | 13/13 | 8/8/4 | 1 | 3 | T0 (0/13; 8) → C1 (13/13; 8) → S1 (13/13; 4 ✓) → S2 (13/13; 5 ×) → S3 (13/13; 5 ×) |
| java_to_python | IpUtil | failed | 15/16 | 13/11/11 | 3 | 0 | T0 (0/16; 13) → C1 (15/16; 10) → C2 (15/16; 11) → C3 (15/16; 11) |
| java_to_python | JSONProcessor | passed | 16/16 | 11/11/11 | 1 | 3 | T0 (8/16; 11) → C1 (16/16; 11) → S1 (8/16; 9 ×) → S2 (8/16; 8 ×) → S3 (8/16; 9 ×) |
| java_to_python | JobMarketplace | failed | 10/36 | 24/26/26 | 3 | 0 | T0 (10/36; 24) → C1 (10/36; 26) → C2 (10/36; 26) → C3 (10/36; 26) |
| java_to_python | KappaCalculator | failed | 9/11 | 16/15/15 | 3 | 0 | T0 (5/11; 16) → C1 (9/11; 15) → C2 (9/11; 15) → C3 (9/11; 15) |
| java_to_python | LongestWord | passed | 10/10 | 12/7/4 | 2 | 3 | T0 (0/10; 12) → C1 (5/10; 10) → C2 (10/10; 7) → S1 (10/10; 6 ✓) → S2 (10/10; 4 ✓) → S3 (5/10; 6 ×) |
| java_to_python | MahjongConnect | passed | 28/28 | 16/16/16 | 0 | 3 | T0 (28/28; 16) → S1 (22/28; 10 ×) → S2 (22/28; 9 ×) → S3 (22/28; 9 ×) |
| java_to_python | Manacher | failed | 10/11 | 7/6/6 | 3 | 0 | T0 (0/11; 7) → C1 (10/11; 5) → C2 (5/11; 5) → C3 (10/11; 6) |
| java_to_python | MetricsCalculator | passed | 30/30 | 23/19/3 | 1 | 3 | T0 (18/30; 23) → C1 (30/30; 19) → S1 (30/30; 3 ✓) → S2 (30/30; 3 ×) → S3 (30/30; 3 ×) |
| java_to_python | MetricsCalculator2 | failed | 2/20 | 18/24/24 | 3 | 0 | T0 (2/20; 18) → C1 (2/20; 23) → C2 (2/20; 24) → C3 (2/20; 24) |
| java_to_python | MovieBookingSystem | failed | 11/16 | 20/16/16 | 3 | 0 | T0 (0/16; 20) → C1 (11/16; 17) → C2 (11/16; 17) → C3 (11/16; 16) |
| java_to_python | MovieTicketDB | passed | 16/16 | 31/30/6 | 2 | 3 | T0 (0/16; 31) → C1 (0/16; 28) → C2 (16/16; 30) → S1 (16/16; 24 ✓) → S2 (16/16; 11 ✓) → S3 (16/16; 6 ✓) |
| java_to_python | MusicPlayer | failed | 38/42 | 18/18/18 | 3 | 0 | T0 (38/42; 18) → C1 (38/42; 18) → C2 (38/42; 19) → C3 (38/42; 18) |
| java_to_python | NLPDataProcessor | failed | 10/11 | 6/6/6 | 3 | 0 | T0 (10/11; 6) → C1 (7/11; 7) → C2 (10/11; 7) → C3 (10/11; 6) |
| java_to_python | NLPDataProcessor2 | failed | 8/16 | 28/26/26 | 3 | 0 | T0 (0/16; 28) → C1 (8/16; 26) → C2 (8/16; 26) → C3 (8/16; 26) |
| java_to_python | NumberConverter | passed | 31/31 | 9/9/3 | 0 | 3 | T0 (31/31; 9) → S1 (31/31; 3 ✓) → S2 (31/31; 3 ×) → S3 (31/31; 3 ×) |
| java_to_python | NumberWordFormatter | failed | 6/28 | 17/17/17 | 3 | 0 | T0 (6/28; 17) → C1 (6/28; 17) → C2 (6/28; 17) → C3 (6/28; 17) |
| java_to_python | NumericEntityUnescaper | failed | 15/17 | 6/6/6 | 3 | 0 | T0 (15/17; 6) → C1 (15/17; 6) → C2 (15/17; 6) → C3 (15/17; 6) |
| java_to_python | Order | failed | 16/17 | 7/7/7 | 3 | 0 | T0 (16/17; 7) → C1 (16/17; 9) → C2 (11/17; 7) → C3 (16/17; 7) |
| java_to_python | PageUtil | failed | 5/16 | 11/11/11 | 3 | 0 | T0 (5/16; 11) → C1 (15/16; 11) → C2 (5/16; 11) → C3 (5/16; 11) |
| java_to_python | PersonRequest | passed | 16/16 | 9/12/12 | 1 | 3 | T0 (0/16; 9) → C1 (16/16; 12) → S1 (10/16; 6 ×) → S2 (10/16; 6 ×) → S3 (10/16; 6 ×) |
| java_to_python | PushBoxGame | failed | 6/16 | 52/51/51 | 3 | 0 | T0 (2/16; 52) → C1 (4/16; 50) → C2 (14/16; 47) → C3 (6/16; 51) |
| java_to_python | RPGCharacter | passed | 26/26 | 15/15/2 | 0 | 3 | T0 (26/26; 15) → S1 (26/26; 2 ✓) → S2 (26/26; 2 ×) → S3 (26/26; 2 ×) |
| java_to_python | RegexUtils | failed | 48/51 | 22/18/18 | 3 | 0 | T0 (20/51; 22) → C1 (48/51; 15) → C2 (48/51; 17) → C3 (48/51; 18) |
| java_to_python | SQLGenerator | passed | 32/32 | 13/9/2 | 1 | 3 | T0 (20/32; 13) → C1 (32/32; 9) → S1 (32/32; 2 ✓) → S2 (32/32; 8 ×) → S3 (32/32; 2 ×) |
| java_to_python | SQLQueryBuilder | passed | 25/25 | 7/7/2 | 1 | 3 | T0 (21/25; 7) → C1 (25/25; 7) → S1 (25/25; 2 ✓) → S2 (25/25; 2 ×) → S3 (25/25; 2 ×) |
| java_to_python | Server | passed | 26/26 | 17/12/7 | 2 | 3 | T0 (3/26; 17) → C1 (18/26; 12) → C2 (26/26; 12) → S1 (26/26; 7 ✓) → S2 (7/26; 2 ×) → S3 (7/26; 2 ×) |
| java_to_python | ShoppingCart | failed | 0/23 | 20/20/20 | 3 | 0 | T0 (0/23; 20) → C1 (5/23; 16) → C2 (10/23; 18) → C3 (0/23; 20) |
| java_to_python | SignInSystem | passed | 26/26 | 13/8/2 | 1 | 3 | T0 (0/26; 13) → C1 (26/26; 8) → S1 (26/26; 2 ✓) → S2 (26/26; 7 ×) → S3 (26/26; 7 ×) |
| java_to_python | Snake | failed | 15/21 | 36/42/42 | 3 | 0 | T0 (0/21; 36) → C1 (0/21; 36) → C2 (10/21; 37) → C3 (15/21; 42) |
| java_to_python | SplitSentence | passed | 16/16 | 14/9/4 | 1 | 3 | T0 (0/16; 14) → C1 (16/16; 9) → S1 (16/16; 4 ✓) → S2 (16/16; 5 ×) → S3 (16/16; 5 ×) |
| java_to_python | Statistics3 | passed | 36/36 | 16/13/9 | 2 | 3 | T0 (20/36; 16) → C1 (35/36; 13) → C2 (36/36; 13) → S1 (36/36; 11 ✓) → S2 (36/36; 11 ×) → S3 (36/36; 9 ✓) |
| java_to_python | StockPortfolioTracker | failed | 1/38 | 15/19/19 | 3 | 0 | T0 (2/38; 15) → C1 (0/38; 18) → C2 (2/38; 17) → C3 (1/38; 19) |
| java_to_python | StudentDatabaseProcessor | failed | -16/16 | 18/18/18 | 3 | 0 | T0 (-16/16; 18) → C1 (-16/16; 18) → C2 (-16/16; 18) → C3 (-16/16; 18) |
| java_to_python | TextFileProcessor | passed | 21/21 | 10/10/5 | 0 | 3 | T0 (21/21; 10) → S1 (21/21; 10 ×) → S2 (21/21; 7 ✓) → S3 (21/21; 5 ✓) |
| java_to_python | Thermostat | passed | 36/36 | 26/22/22 | 2 | 3 | T0 (0/36; 26) → C1 (30/36; 26) → C2 (36/36; 22) → S1 (6/36; 8 ×) → S2 (2/36; 2 ×) → S3 (6/36; 2 ×) |
| java_to_python | TicTacToe | passed | 16/16 | 13/8/2 | 1 | 3 | T0 (0/16; 13) → C1 (16/16; 8) → S1 (16/16; 2 ✓) → S2 (16/16; 3 ×) → S3 (16/16; 3 ×) |
| java_to_python | TimeUtils | failed | 0/36 | 23/23/23 | 3 | 0 | T0 (0/36; 23) → C1 (0/36; 23) → C2 (0/36; 23) → C3 (0/36; 23) |
| java_to_python | TriCalculator | failed | 24/26 | 10/10/10 | 3 | 0 | T0 (24/26; 10) → C1 (24/26; 10) → C2 (24/26; 10) → C3 (24/26; 10) |
| java_to_python | TwentyFourPointGame | failed | 16/18 | 15/16/16 | 3 | 0 | T0 (10/18; 15) → C1 (16/18; 16) → C2 (16/18; 16) → C3 (16/18; 16) |
| java_to_python | URLHandler | failed | 0/32 | 13/14/14 | 3 | 0 | T0 (0/32; 13) → C1 (0/32; 14) → C2 (0/32; 14) → C3 (0/32; 14) |
| java_to_python | UrlPath | passed | 19/19 | 11/11/11 | 0 | 3 | T0 (19/19; 11) → S1 (6/19; 9 ×) → S2 (1/19; 10 ×) → S3 (1/19; 10 ×) |
| java_to_python | UserLoginDB | failed | 0/21 | 10/10/10 | 3 | 0 | T0 (0/21; 10) → C1 (0/21; 10) → C2 (0/21; 10) → C3 (0/21; 10) |
| java_to_python | VectorUtil | failed | 6/22 | 22/9/9 | 3 | 0 | T0 (1/22; 22) → C1 (6/22; 9) → C2 (6/22; 9) → C3 (6/22; 9) |
| java_to_python | VendingMachine | failed | 8/27 | 21/22/22 | 3 | 0 | T0 (8/27; 21) → C1 (8/27; 22) → C2 (8/27; 22) → C3 (8/27; 22) |
| java_to_python | Warehouse | failed | 5/32 | 19/25/25 | 3 | 0 | T0 (13/32; 19) → C1 (31/32; 40) → C2 (12/32; 19) → C3 (5/32; 25) |
| java_to_python | WeatherSystem | failed | 19/22 | 19/11/11 | 3 | 0 | T0 (0/22; 19) → C1 (19/22; 11) → C2 (2/22; 19) → C3 (19/22; 11) |
| java_to_python | Words2Numbers | passed | 13/13 | 9/8/5 | 1 | 3 | T0 (6/13; 9) → C1 (13/13; 8) → S1 (13/13; 5 ✓) → S2 (13/13; 5 ×) → S3 (13/13; 5 ×) |
| java_to_python | XMLProcessor | failed | 2/23 | 15/14/14 | 3 | 0 | T0 (2/23; 15) → C1 (2/23; 14) → C2 (2/23; 14) → C3 (2/23; 14) |
| java_to_python | ZipFileProcessor | failed | 3/25 | 17/16/16 | 3 | 0 | T0 (3/25; 17) → C1 (3/25; 16) → C2 (3/25; 16) → C3 (3/25; 16) |

## Dados brutos

Os quatro arquivos JSONL de entrada contêm os resultados completos, inclusive `loop_trace`, duração e contagens por etapa:

- `classeval_openai_gpt41mini_2026-11-19.jsonl`
- `classeval_openai_gpt41mini_python_to_java_51-94_2026-11-19.jsonl`
- `classeval_openai_gpt41mini_java_to_python_2026-11-19.jsonl`
- `classeval_openai_gpt41mini_java_to_python_51-94_2026-11-19.jsonl`
