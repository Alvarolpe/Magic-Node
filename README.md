# HackUDC 2026 Submission

## Instalation
1. Crea usuario de Denodo [https://auth.denodo.com/user-management/express-previous-register] o inicia sesión si ya tienes

2. Instala docker y docker desktop
    en Ubuntu/Debian
    ```sh
    apt install docker docker-compose
    ```
    para otras distros busca en los repositorios correspondientes.

3. accede a [https://harbor.open.denodo.com/harbor/projects] e inicia sesión con la cuenta de denodo. Clica en tu perfil en la parte superior derecha y en User Profile. Guarda el usuario y el CLI secret.

4. ejecuta
    ```sh
    docker login harbor.open.denodo.com
    ```
    e inserta el usuario y el CLI secret del anterior paso.

5. Registrate en [https://aistudio.google.com]

6. Crea una clave de api en la seccion de la parte inferior izquierda

7. Cambia los campos GOOGLE_AI_STUDIO_API_KEY para insertar esta clave

8. Crea el entorno de docker
    ```sh
    docker compose pull
    docker compose up -d
    ```

9. espera a que inicie, tarda unos minutos. Puede que dé error de autenticacion al principio mientras inicia incluso si parece que ha cargado.

10. conectate a la base de datos con
    ```sh
    sudo docker exec -it postgres-db psql -U denodo_user -d my_database
    ```
    La contraseña es denodo_password.
    Pega la siguiente sentencia:
    ```sql
    create table if not exists files (
      id bigserial not null unique primary key,
      name text not null,
      contents text[] not null,
      creation_date timestamp not null,
      extra json not null
    );
    ```

11. entra en [http://localhost:9090/denodo-design-studio/]
    añade una base de datos postgres en "connect to a datasource".
    el host es "172.18.0.1" y el puerto es 5432. User denodo_user, password denodo_password y base de datos my_database.

    Crea una nueva vista sobre esta base de datos eligiendo la tabla "files".

12. entra en [http://localhost:9090/denodo-data-catalog]. Clica en Administration y Sync with VDP. Next hasta que acabe para sincronizarlos.


## Uso
Para la aplicación CLI, instala `pypdf`. se ejecuta con `python3 src/main.py [comando] [flags]`. Hay un comando de ayuda disponible con `python3 src/main.py --help`.

Para la aplicación gráfica, instala `pypdf` y `nodejs_25`. Desde `frontend/`, ejecuta `npm run dev` y, en otra terminal, desde `backend`, `python app.py`. La aplicación estará en `localhost:5173`
