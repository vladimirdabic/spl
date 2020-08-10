# SPL (Serbian Programming Language, Srpski Programski Jezik)
SPL је програмски језик написан у пајтону 3.8 из забаве.\
Синтакса језика је инспирисана од стране C++ и C#.

Покретање програма помоћу spl.ехе (У команд промпту):
```
Pokrenuti fajl:
spl.exe <file name>

Uci u Interactive Shell:
spl.exe
```

### Само једна цака, све је на српском!
Добро није баш све на српском, изоставио сам ствари као
bool, true, false, null, and \
**AND нисам хтео превести на "i" јер онда не бих могли имати вариаблу која се зове i**


Коришћен је пајтон модул **"sly"** који је олакшао много јер нисам морао да напишем цео Parser и Lexer.


# Примери

Hello World Program
```
napisi("Hello, World!");
```

Matematicke operacije
```
napisi(2+2*2);
// Output: 6
```

Logicne operacije
```
broj a = 20;
broj b = 10;
ako (a == b)
{
  napisi("Jednaki su!");
}
inace
{
  napisi("Nisu jednaki");
}
```

Unos i pozdrav
```
niska ime = unos("Unesi ime: ");
napisi("Pozdrav, " + ime + "!");
```

Pogodi nasumican broj\
[Primer pogodi_broj.txt](https://github.com/vladimirdabic/srpski-prog-jezik/blob/master/spl/Primer%20pogodi_broj.txt)
