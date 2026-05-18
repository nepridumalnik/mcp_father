# MCP Father Hub

MCP-хаб (Model Context Protocol), который позволяет подключать несколько MCP-серверов как плагины.

## Возможности

- **Управление плагинами**: добавление, включение, отключение и синхронизация MCP-плагинов из Git-репозиториев.
- **Единая конфигурация**: плагины описываются в `repositories/list.yml`, состояние хранится в `~/.mcp_father/settings.json`.
- **Встроенные инструменты**: timestamp, hostname и создание директорий.
- **Динамическое подключение**: включенные плагины монтируются в общий MCP-хаб.

## Установка

1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/your-username/mcp_father.git
   cd mcp_father
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

## Использование

Перед работой с хабом нужно создать локальные конфиги:

```bash
python -m mcp_father init
```

### Инициализация

Создать `repositories/list.yml` и `~/.mcp_father/settings.json`:
```bash
python -m mcp_father init
```

### Управление плагинами

- **Добавить MCP-сервер из другой репы**:
  1. Если конфиги еще не созданы, выполните:
     ```bash
     python -m mcp_father init
     ```

  2. Добавьте репозиторий в `repositories/list.yml`:
     ```yaml
     repositories:
       filesystem:
         url: "https://github.com/modelcontextprotocol/servers.git"
         branch: "main"
         namespace: "filesystem"
         mcp:
           command: "uv"
           args: ["run", "python", "-m", "mcp_server_filesystem"]
     ```

     `filesystem` - локальное имя плагина, `namespace` - префикс при монтировании инструментов, `mcp.command` и `mcp.args` - команда запуска MCP-сервера из этой репы.

  3. Склонируйте/обновите репу и включите плагин:
     ```bash
     python -m mcp_father sync filesystem
     python -m mcp_father enable filesystem
     ```

  4. Запустите хаб:
     ```bash
     python -m mcp_father run
     ```

- **Показать список плагинов**:
  ```bash
  python -m mcp_father list
  ```

- **Включить плагин**:
  ```bash
  python -m mcp_father enable example-plugin
  ```

- **Отключить плагин**:
  ```bash
  python -m mcp_father disable example-plugin
  ```

- **Синхронизировать плагины**:
  ```bash
  python -m mcp_father sync
  # или один конкретный плагин
  python -m mcp_father sync example-plugin
  ```

- **Зафиксировать плагин на commit**:
  ```bash
  python -m mcp_father lock example-plugin <commit-hash>
  ```

### Запуск хаба

Запустить MCP-сервер:
```bash
python -m mcp_father run
```

### Debug-логи

Включить DEBUG-логи можно через `-d` или `--debug` до или после команды:
```bash
python -m mcp_father -d run
python -m mcp_father run -d
```

Логи пишутся в stdout и в `~/.mcp_father/logs/`.

## Пример конфигурации

**repositories/list.yml**
```yaml
repositories:
  example-plugin:
    url: "https://github.com/example/example-mcp.git"
    branch: "main"
    namespace: "example"
    mcp:
      command: "uv"
      args: ["run", "python", "-m", "example_mcp"]
```

**~/.mcp_father/settings.json**
```json
{
  "plugins": {
    "example-plugin": {
      "enabled": true,
      "locked_commit": null
    }
  }
}
```

## Подключение к Claude/Qwen

Настройте MCP-клиент (например Claude Desktop), чтобы он запускал хаб:
```json
{
  "mcpServers": {
    "mcp-father": {
      "command": "python",
      "args": ["/path/to/mcp_father/__main__.py"]
    }
  }
}
```
