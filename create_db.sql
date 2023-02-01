create table categories(
    name PRIMARY KEY
);

create table recipes(
    name PRIMARY KEY,
    category,
    ingridients,
    description,
    photo_id,
    FOREIGN KEY(category) REFERENCES categories(name)
);


insert into categories values
('Горячее'),
('Выпечка'),
('Соусы'),
('Салаты'),
('Соленья'),
('Варенья')