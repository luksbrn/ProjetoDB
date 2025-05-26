1- instala as dependecias com "pip install -r requirements.txt"

2- 
PostgreSQL:

Cria um banco de dados e um usuário

Abre o terminal ou um cliente PostgreSQL (como pgAdmin) e executa:

sql
CREATE DATABASE nomedobanco;
CREATE USER nomeusuario WITH PASSWORD 'senha';
GRANT ALL PRIVILEGES ON DATABASE nomedobanco TO nomeusuario;
Atualize a DATABASE_URL no código

No arquivo record_api.py, substitua a linha:

python
DATABASE_URL = "postgresql://username:password@localhost/dbname"
Pelos seus dados reais:

python
DATABASE_URL = "postgresql://nomeusuario:senha@localhost/nomedobanco"
Para MySQL:

Crie um banco de dados e um usuário

Acessa o MySQL pelo terminal (ou usando o MySQL Workbench) e executa:

sql
CREATE DATABASE nomedobanco;
CREATE USER 'nomeusuario'@'localhost' IDENTIFIED BY 'senha';
GRANT ALL PRIVILEGES ON nomedobanco.* TO 'nomeusuario'@'localhost';
FLUSH PRIVILEGES;
Atualize a DATABASE_URL no código

No arquivo record_api.py, substitua por:

python
DATABASE_URL = "mysql+mysqlconnector://nomeusuario:senha@localhost/nomedobanco"
Importante: No arquivo requirements.txt, descomente (ou adicione) a linha:

txt
mysql-connector-python
E comente (ou remova) a linha:

txt
psycopg2-binary


3- pra rodar: "uvicorn record_api:app --reload"