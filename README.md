# MUID (Magic Unique Identifier)

[![CI](https://github.com/magicaleks/muid/actions/workflows/ci.yml/badge.svg)](https://github.com/magicaleks/muid/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/magicid)](https://pypi.org/project/magicid/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

Библиотека для работы с уникальными идентификаторами MUID.

## Почему MUID?
1. Всегда уникален даже в распределённой системе. Позволяет генерировать MUID на клиенте без обращения к серверу.
2. Монотонен. TS метка и счётчик позволяют оптимально добавлять новые записи в B-Tree.
3. Подходит для распределённых и высоконагруженных систем. Каждый процесс получает свой отпечаток. Счётчик позволяет генерировать минимум 33554432 уникальных MUID в рамках одной миллисекунды.
4. Мало предсказуем, даже зная `ts` и `proc_fn` математически сложно угадать следующий MUID за счёт `secure rand`. **ВАЖНО:** размер и стойкость `secure rand` может меняться в будущих версиях. Для реальной энтропии требуется от 36 битов, я взял 40 бит.

## Быстрый старт
Установите пакет
```shell
pip install magicid
```

И создайте первый MUID
```python
from muid import MagicID

muid = MagicID()

print(muid)
# 0001-8EA1C900-0F6F8410-1E7C1CA4
```

Или через консоль
```shell
muid new -n 5
#0002-977F0200-0300034F-EA9CE3FA
#0002-977F0200-050003FC-97B34993
#0002-977F0200-0700034B-FEAB9541
#0002-977F0200-090003A4-D18816C8
#0002-977F0200-0B00034D-FF2FD3F8
```

## Использование в `Pydantic`

```python
from muid import MagicID
from pydantic import BaseModel, Field


class User(BaseModel):
    id: MagicID = Field(default_factory=MagicID)
    
user = User()
print(user.id)
# 0001-8EA1C900-0F6F8410-1E7C1CA4

json_user = {"id": "0001-8EA1C900-0F6F8410-1E7C1CA4"}

user = User.model_validate(json_user)
print(user.id)
# 0001-8EA1C900-0F6F8410-1E7C1CA4
```

## Принцип работы

MUID состоит из 4 частей:
\[ts ms 42 bits]-\[counter 13 bits]-\[proc_fn 17 bits]-\[secure rand 40 bits]

Всего 14 байт, в HEX представлении 31 символ, включая дефисы.

При инициализации пакета генерируется `proc_fn` и используется до следующей инициализации.
При переполнении `counter` ждёт до следующей миллисекунды (ref. Snowflake ID)

## Лицензия
Проект инициирован, разработан и поддерживается Aleksandr @magicaleks.
Распространяется на основании лицензии Apache-2.0.
