# Desafio técnico: Engenheiro de Inteligencia Artificial - Visão Computacional

## Visão Geral

O objetivo deste desafio e avaliar sua capacidade de desenvolver uma solução de Visão Computacional de ponta a ponta. Voce receberá o video e deverá extrair informações analíticas sobre o tráfego de veiculos em tempo real ou processado.

## Instalação

- Ter instalado o Python 3 e o PIP.

- Executar a migration localizada em `.\migrations\InitialMigration.sql`.

### Passos para instalação local

- Na pasta do projeto, executar os comandos abaixo:

```powershell
python -m venv .venv
```

```powershell
.venv\Scripts\activate.ps1
```

- Executar o comando abaixo para instalar as dependências:

```powershell
python -m pip install -r requirements.txt
```

- Para executar localmente no Windows, use `.env.local` ou configure a connection string para `.\SQLEXPRESS`.

- Executar a aplicação localmente:

```powershell
python contagem_veiculos.py
```

### Passos para instalação em docker

- Para executar em Docker com SQL Server Express local, confira a porta TCP da instancia:

```powershell
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Microsoft SQL Server\MSSQL16.SQLEXPRESS\MSSQLServer\SuperSocketNetLib\Tcp\IPAll' | Select-Object TcpDynamicPorts, TcpPort
```

Use essa porta em `.env.docker`, por exemplo:

```env
SQLSERVER_SERVER=host.docker.internal,60672
```

No Docker, use um login do SQL Server em `.env.docker`:

```env
SQLSERVER_USER=sa
SQLSERVER_PASSWORD=sua_senha_real
```

O SQL Server precisa estar com autenticacao mista habilitada, e o login informado precisa ter acesso ao banco `ContagemVeiculos`.

- Adicionar o video `BR232.mp4` a pasta do projeto.

- Executar a aplicação com Docker:

```powershell
docker compose up --build
```