### Funcionalidades

- [x] Implementação da memória temporária com `ConversationBufferMemory`
- [x] Cache de respostas em RAM para reaproveitamento de interações durante a sessão
- [x] Modularização do projeto com diretórios: `core/`, `ui/`, `services/`, `models/`
- [x] Layout interativo com `typing_effect` e tela de boas-vindas
- [x] Docker Compose configurado para execução local

### Segurança

- [x] Sessão isolada por usuário (via `st.session_state`)
- [x] Nenhum dado persistido no disco
- [x] Estrutura preparada para autenticação segura com senha e OAuth

### Melhorias internas

- [x] Separação clara entre lógica, apresentação e serviços
- [x] `llm_agent.py` refatorado para facilitar extensão com histórico de memória

### Observações

- A autenticação (login tradicional e social) ainda será implementada nas próximas versões
- Este release é uma versão **beta** para testes e feedback
