# Documentação do Projeto API de Delivery de Pizza

## 1. Visão Geral do Projeto

Esta é uma API backend para um serviço de delivery de pizza, desenvolvida utilizando **FastAPI**. O sistema permite que usuários se cadastrem, façam login, realizem pedidos de pizza e gerenciem seus pedidos. Administradores (usuários "staff") possuem permissões elevadas para visualizar e gerenciar todos os pedidos, incluindo a atualização de status.

**Principais Tecnologias e Conceitos:**

* **FastAPI:** Framework web Python moderno para construção de APIs.
* **SQLAlchemy:** ORM para interação com o banco de dados PostgreSQL.
* **Pydantic:** Para validação de dados de requisição/resposta e serialização.
* **JWT (JSON Web Tokens):** Utilizado para autenticação stateless, gerenciado via `python-jose`.
* **Passlib:** Para hashing seguro de senhas.
* **Injeção de Dependência:** Mecanismo central do FastAPI, usado para sessões de banco de dados e autenticação.
* **Design Modular:** Rotas de autenticação (`auth_routes.py`) e pedidos (`order_routes.py`) separadas.
* **Controle de Acesso Baseado em Função (RBAC):** Distinção entre usuários comuns e usuários "staff" para certas operações.

---

## 2. Filosofia de Design e Funcionamento

O projeto foi estruturado visando clareza e a aplicação de boas práticas comuns em APIs RESTful com FastAPI.

* **Separação de Responsabilidades:**
    * **Routers:** `auth_routes.py` lida com o registro e login de usuários. `order_routes.py` gerencia todas as operações relacionadas a pedidos.
    * **Models (`models.py`):** Define a estrutura das tabelas do banco de dados (`User`, `Order`) usando SQLAlchemy, incluindo relacionamentos e tipos de dados específicos como `ChoiceType` para status e tamanhos.
    * **Schemas (`schemas.py`):** Contém os modelos Pydantic que definem o formato esperado para os dados de entrada (requisições) e saída (respostas), garantindo validação e documentação automática da API.
    * **Segurança (`security.py`):** Centraliza a lógica de hashing de senhas, criação e verificação de tokens JWT, e a dependência `get_current_user` para proteger rotas.
    * **Banco de Dados (`database.py`):** Configura a conexão com o PostgreSQL e fornece a gestão de sessões transacionais.
* **Autenticação e Autorização:**
    * O acesso a endpoints sensíveis é protegido por tokens JWT.
    * Usuários "staff" têm privilégios para visualizar todos os pedidos e modificar o status dos pedidos, implementando um nível básico de controle de acesso.
* **Validação e Documentação:**
    * As docstrings nos endpoints são utilizadas pelo FastAPI para gerar descrições na documentação OpenAPI (Swagger UI), complementando a validação feita pelos schemas Pydantic.
* **Interação Assíncrona:** Os endpoints são definidos com `async def`, permitindo operações de I/O não bloqueantes, características do FastAPI.

---

## 3. Fluxo de Autenticação e Autorização (`auth_routes.py` e `security.py`)

1.  **Registro de Usuário (`POST /auth/signup`):**
    * **Lógica:** Recebe dados via `SignUpModel` (username, email, password, is_active, is_staff).
    * Verifica se o `username` ou `email` já existem no banco para evitar duplicidade.
    * A senha é hasheada usando `get_password_hash` (bcrypt via Passlib).
    * Um novo `User` é criado e salvo no banco.
    * **Resposta:** Retorna os dados do usuário criado conforme o `SignUpModel`. _Observação: Retornar o `SignUpModel` pode expor campos como `password` (mesmo que hasheado na criação, o schema de resposta o inclui). Seria mais seguro usar um schema de resposta específico (ex: `UserPublic`) que omita dados sensíveis._
    * **Pensamento:** Processo padrão de criação de conta com validação de unicidade e segurança de senha.

2.  **Login e Obtenção de Token (`POST /auth/token`):**
    * **Lógica:** Utiliza `OAuth2PasswordRequestForm` para receber `username` e `password`.
    * Busca o usuário pelo `username`.
    * Verifica a senha fornecida contra o hash armazenado usando `verify_password`.
    * Se as credenciais forem válidas, um token de acesso JWT é gerado por `create_access_token`, tendo o `username` do usuário como "subject" (`sub`).
    * **Pensamento:** Fluxo padrão OAuth2 para obtenção de token, facilitando a integração com clientes.

3.  **Refresh de Token (`POST /auth/refresh_token`):**
    * **Lógica:** Requer um token JWT válido (depende de `get_current_user`).
    * Gera um novo token de acesso para o usuário autenticado, estendendo a sessão.
    * **Pensamento:** Melhora a experiência do usuário ao permitir a renovação da sessão sem re-login completo.

4.  **Mecanismos de Segurança (`security.py`):**
    * `get_password_hash()` e `verify_password()`: Usam `passlib` com o esquema bcrypt para armazenar e verificar senhas de forma segura.
    * `create_access_token()`: Cria tokens JWT com um tempo de expiração (padrão de 15 minutos ou configurável via `ACCESS_TOKEN_EXPIRE_MINUTES`). Os tokens são assinados com `SECRET_KEY` e `ALGORITHM` (HS256).
    * `get_current_user()`: Dependência crucial que utiliza `OAuth2PasswordBearer` para extrair o token do header `Authorization`. Valida o token (assinatura, expiração), decodifica-o para obter o `username` (do campo `sub`) e busca o usuário correspondente no banco. Se qualquer etapa falhar, levanta `HTTPException` (401 Unauthorized).
    * **Pensamento:** Isola a lógica de segurança, tornando os endpoints mais limpos e a gestão da segurança mais centralizada. A `SECRET_KEY` está hardcoded, o que é aceitável para estudo, mas em produção deveria vir de variáveis de ambiente.

---

## 4. Gerenciamento de Pedidos (`order_routes.py`)

1.  **Realizar um Pedido (`POST /orders/order`):**
    * **Lógica:** Requer autenticação (`get_current_user`).
    * Recebe dados do pedido via `OrderModel` (quantity, pizza_size, order_status opcional com default 'PENDING').
    * Cria um novo objeto `Order`, associando-o ao `id` do `current_user`.
    * Salva o pedido no banco.
    * Retorna uma resposta JSON customizada com detalhes do pedido criado.
    * **Pensamento:** Endpoint central para o usuário criar seus pedidos. A associação com o usuário autenticado é automática.

2.  **Listar Todos os Pedidos (Apenas Staff) (`GET /orders/orders`):**
    * **Lógica:** Requer autenticação. Verifica se `current_user.is_staff` é `True`.
    * Se for staff, retorna todos os pedidos do banco.
    * Caso contrário, levanta `HTTPException` (401 Unauthorized).
    * **Pensamento:** Implementa uma restrição de acesso para visualização geral de pedidos, comum em painéis administrativos.

3.  **Obter Pedido por ID (Apenas Staff) (`GET /orders/orders{id}`):**
    * **Lógica:** Requer autenticação e que `current_user.is_staff` seja `True`.
    * Busca um pedido específico pelo `id` fornecido na URL. _Observação: A rota está como `/orders{id}`, provavelmente deveria ser `/orders/{id}` para capturar o parâmetro de path corretamente._
    * **Pensamento:** Permite que administradores consultem pedidos específicos.

4.  **Listar Pedidos do Usuário Logado (`GET /orders/user/orders`):**
    * **Lógica:** Requer autenticação.
    * Acessa diretamente a relação `current_user.orders` (definida no `models.py` via SQLAlchemy) para obter todos os pedidos do usuário autenticado.
    * **Pensamento:** Maneira eficiente de buscar dados relacionados ao usuário, aproveitando o ORM.

5.  **Obter Pedido Específico do Usuário Logado (`GET /orders/user/order/{order_id}`):**
    * **Lógica:** Requer autenticação.
    * Itera sobre os `current_user.orders` para encontrar um pedido com o `id` especificado.
    * Se não encontrar, levanta `HTTPException` (400 Bad Request).
    * **Pensamento:** Permite ao usuário buscar um de seus pedidos específicos.

6.  **Atualizar um Pedido (`PUT /orders/order/update/{order_id}`):**
    * **Lógica:** Requer autenticação. Recebe novos dados via `OrderModel`.
    * Busca o pedido pelo `id`.
    * Atualiza `quantity` e `pizza_size` do pedido.
    * **Alerta de Segurança/Lógica:** Este endpoint, como está, **não verifica se o pedido pertence ao `current_user` ou se o `current_user` é staff**. Qualquer usuário autenticado poderia, teoricamente, atualizar qualquer pedido se souber o ID. Isso deveria ser revisto para adicionar uma verificação de permissão (ex: `if order_to_update.user_id != current_user.id and not current_user.is_staff:`).
    * **Pensamento:** A intenção é permitir a modificação de um pedido, mas a checagem de propriedade é crucial.

7.  **Atualizar Status de um Pedido (Apenas Staff) (`PATCH /orders/order/update{order_id}`):**
    * **Lógica:** Requer autenticação e que `current_user.is_staff` seja `True`.
    * Recebe o novo status via `OrderStatusModel`.
    * Busca o pedido pelo `id`. _Observação: A rota está como `/order/update{order_id}`, provavelmente deveria ser `/order/update/{order_id}`._
    * Atualiza o `order_status` do pedido.
    * Retorna uma resposta JSON customizada.
    * **Pensamento:** Endpoint dedicado para administradores gerenciarem o fluxo dos pedidos.

8.  **Deletar um Pedido (`DELETE /orders/order/delete/{id}`):**
    * **Lógica:** Requer autenticação.
    * Busca o pedido pelo `id` e o remove do banco.
    * Retorna status `204 No Content` e uma mensagem (embora respostas 204 geralmente não devam ter corpo).
    * **Alerta de Segurança/Lógica:** Assim como na atualização, **falta uma verificação para garantir que apenas o proprietário do pedido ou um staff possa deletá-lo**.
    * **Pensamento:** Permite a remoção de pedidos, mas precisa de controle de acesso mais granular.

---

## 5. Modelos de Dados (`models.py`)

* **`User`:**
    * Campos: `id`, `username` (único), `email` (único), `password` (texto), `is_staff` (booleano), `is_active` (booleano).
    * Relacionamento: `orders` (one-to-many com `Order`).
* **`Order`:**
    * Campos: `id`, `quantity`, `order_status` (usando `ChoiceType` com 'PENDING', 'IN-TRANSIT', 'DELIVERED'), `pizza_size` (usando `ChoiceType` com 'SMALL', 'MEDIUM', 'LARGE'), `user_id` (chave estrangeira para `User`).
    * Relacionamento: `user` (many-to-one com `User`).
* **`ChoiceType`:** Vindo de `sqlalchemy-utils`, permite definir colunas com um conjunto restrito de escolhas, o que é ótimo para campos como status e tamanho.
* **Pensamento:** A estrutura dos modelos é clara e os relacionamentos são bem definidos, permitindo consultas eficientes como `current_user.orders`.

---

## 6. Schemas de Dados (`schemas.py`)

* **`SignUpModel`:** Usado para o payload de registro de usuário.
* **`LoginModel`:** Definido, mas o endpoint `/auth/token` usa `OAuth2PasswordRequestForm` diretamente. Poderia ser usado se uma validação Pydantic customizada fosse necessária antes do `OAuth2PasswordRequestForm`.
* **`Token`:** Estrutura padrão para a resposta do token de acesso.
* **`OrderModel`:** Para criar/atualizar pedidos. Inclui valores default e um exemplo no `json_schema_extra` para a documentação OpenAPI.
* **`OrderStatusModel`:** Schema específico para atualizar apenas o status de um pedido.
* **Pensamento:** Os schemas garantem que os dados trocados com a API sejam válidos e bem estruturados. O uso de `Optional` e valores default nos schemas para pedidos (`OrderModel`, `OrderStatusModel`) oferece flexibilidade.

---

## 7. Interação com Banco de Dados (`database.py`)

* **Configuração:** `DATABASE_URL` aponta para um banco PostgreSQL. `engine` é criado com `echo=True`, útil para debugging durante o desenvolvimento, pois loga as queries SQL.
* **Sessões:** `SessionLocal` é um factory para criar sessões de banco de dados.
* **`get_db()`:** Função de dependência que fornece uma sessão (`db`) para os endpoints. Usa `try/finally` para garantir que a sessão seja fechada após o uso.
* **`get_session()`:** Uma função similar a `get_db()`, mas usando `with Session(engine) as session:`. Apenas `get_db()` é referenciada nos routers fornecidos.
* **Pensamento:** A gestão de sessão por requisição via `get_db()` é uma prática padrão para garantir que cada transação tenha sua própria sessão e que ela seja corretamente fechada.

---

## 8. Pontos de Atenção e Melhorias Potenciais

* **Segurança em Endpoints de Pedido:** Vários endpoints de pedido (`PUT /order/update/{id}`, `DELETE /order/delete/{id}`) não verificam se o `current_user` é o proprietário do pedido ou um staff. Isso deve ser implementado para evitar que usuários modifiquem ou apaguem pedidos alheios.
* **Schema de Resposta do Signup:** O endpoint de signup retorna `SignUpModel`, que pode conter dados que não deveriam ser expostos (como o campo password, mesmo que seu valor venha do input e seja hasheado antes de salvar). Idealmente, usaria um schema de resposta diferente, como um `UserPublicModel`.
* **Consistência nas Rotas:** Algumas rotas de pedido têm `id` como parte do path sem as chaves (ex: `/orders{id}`), o que não funcionará como parâmetro de path no FastAPI. Deveriam ser `/orders/{id}`.
* **Resposta do Delete:** O endpoint de delete retorna status `204 No Content` mas também um corpo JSON com uma mensagem. Respostas 204 tipicamente não devem conter corpo.
* **Variáveis de Ambiente:** A `SECRET_KEY` e `DATABASE_URL` estão hardcoded. Em um ambiente de produção, devem ser gerenciadas através de variáveis de ambiente.

Esta documentação detalha a lógica e o funcionamento do seu projeto de API para delivery de pizza. A estrutura é boa e aplica muitos conceitos importantes do FastAPI!
