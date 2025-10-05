CREATE DATABASE todo_app;
USE todo_app;

CREATE TABLE prioridades(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL
);

CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE tarefas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    priority_id INT NOT NULL,
    category_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES usuarios(id),
    FOREIGN KEY (priority_id) REFERENCES prioridades(id),
    FOREIGN KEY (category_id) REFERENCES categorias(id)
);

INSERT INTO prioridades(name) VALUES ('Baixa'), ('Média'), ('Alta');
INSERT INTO categorias (name) VALUES ('Saúde'), ('Educação'), ('Casa'), ('Trabalho'), ('Financeiro'), ('Outros');