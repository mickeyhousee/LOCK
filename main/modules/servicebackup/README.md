# Guia de Utilização do Monitor de Ficheiros

Este documento serve como um guia para a instalação, configuração e utilização do Monitor de Ficheiros, uma ferramenta desenvolvida pela Equipa de Desenvolvimento COCIBER PT. Esta ferramenta foi criada para monitorizar, fazer backup e transferir via SCP ficheiros específicos, garantindo a sua integridade e disponibilidade.

# Descrição

O Monitor de Ficheiros é uma aplicação robusta que observa mudanças em ficheiros especificados, realiza backups e, se necessário, restaura ficheiros a partir desses backups. Adicionalmente, os backups são enviados para um servidor via SCP para armazenamento remoto. Esta ferramenta é essencial para a manutenção da integridade dos dados críticos.

# Instalação

A ferramenta é distribuída como um executável, simplificando o processo de instalação. Siga os passos abaixo para instalar:

    Transfira o executável do Monitor de Ficheiros para o seu sistema.
    Garanta que o executável tem permissões de execução. No Linux, isto pode ser feito com o comando chmod +x nome_do_executável.
    (Opcional) Mova o executável para um diretório incluído no seu PATH para facilitar o seu acesso.

# Configuração

Antes de utilizar a ferramenta, é necessário configurar os ficheiros a serem monitorizados e os detalhes do servidor SCP. Isto é feito através do ficheiro services.cfg e da configuração das variáveis de ambiente, respectivamente
---
# ⚠️⚠️ IMPORTANTE ⚠️⚠️

**_Enviar para a equipa de desenvolvimento todos os ficheiros a serem monitorizados pelo script. **

-----
# Configuração SCP

    Configure as seguintes variáveis de ambiente com os detalhes do seu servidor SCP:
        SCP_SERVER: O endereço IP ou nome do host do servidor SCP.
        SCP_USER: O nome de usuário para autenticação no servidor SCP.
        SCP_PASSWORD: A senha para autenticação no servidor SCP. (Recomenda-se a utilização de autenticação por chave SSH para maior segurança.)

# Utilização

Para iniciar a monitorização, execute o aplicativo no terminal ou linha de comando. A ferramenta iniciará imediatamente a monitorização dos ficheiros especificados no services.cfg, realizando backups e transferências SCP conforme necessário.

# Paragem Segura

Para interromper a ferramenta de forma segura, utilize os sinais SIGTERM ou SIGINT (Ctrl+C no terminal). Isto garantirá que todos os processos sejam encerrados corretamente e que o diretório de backup local seja eliminado para não deixar dados residuais.
