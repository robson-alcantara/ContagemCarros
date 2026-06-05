# Desafio técnico: Engenheiro de Inteligência Artificial - Visão Computacional

## Visão Geral 

O objetivo deste desafio é avaliar sua capacidade de desenvolver uma solução de Visão Computacional de ponta a ponta. Você receberá o vídeo e deverá extrair informações analíticas sobre o tráfego de veículos em tempo real ou processado.

## Passos para a instalação

- Ter instalado o Python 3 e o PIP instalados

- Na pasta do projeto, executar os comandos abaixo:

 ``python -m venv .venv`` 

 ``.venv\Scripts\activate.ps1``  

- Executar o comando abaixo para instalar as dependências

``python -m pip install -r requirements.txt``

- Executar a migration localizada em .\migrations\InitialMigration.sql

- Adequar a string connection da linha 16 do arquivo contagem_veiculos.py

- Adicionar o video BR232.mp4 à pasta do projeto

- Executar o comando abaixo para executar a aplicação:

``python contagem_veiculos.py``
