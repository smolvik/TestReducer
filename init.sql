drop table if exists Profiles;
drop table if exists Cyclograms;
drop table if exists COptions;

/* Profiles - таблица параметров режима эксплуатационного цикла 
name - 				Наименование режима
speed_in - 			Скорость вращения входного вала
rd_ratio - 			Передаточное отношения механизма
numrot_in - 		Полный рабочий ход входного вала
max_torque_out - 	Максимальный тормозной крутящиймомент на выходном валу
cyclogram_id - 		Циклограмма
*/

create table Profiles(
	id INTEGER PRIMARY KEY AUTOINCREMENT, 
	name VARCHAR(255) NOT NULL UNIQUE,
	speed_in integer not null,
	rd_ratio real not null,
	numrot_in integer not null,
	max_torque_out real not null,
	cyclogram_id integer not null,
	foreign key(cyclogram_id) references Cyclograms(id)
	);


/* Cyclograms - таблица параметров циклограмм 
name - Наименование циклограммы
n1 - рабочий ход входного вала в точке 1
n2 - рабочий ход входного вала в точке 2
n3 - рабочий ход входного вала в точке 3
n4 - рабочий ход входного вала в точке 4
n5 - рабочий ход входного вала в точке 5
m1 - рабочий ход входного вала в точке 1
m2 - рабочий ход входного вала в точке 2
m3 - рабочий ход входного вала в точке 3
m4 - рабочий ход входного вала в точке 4
m5 - рабочий ход входного вала в точке 5
*/

create table Cyclograms(
	id INTEGER PRIMARY KEY AUTOINCREMENT, 
	name VARCHAR(255) NOT NULL UNIQUE,
	n1 integer not null,
	n2 integer not null,
	n3 integer not null,
	n4 integer not null,
	n5 integer not null,
	m1 integer not null,
	m2 integer not null,
	m3 integer not null,
	m4 integer not null,
	m5 integer not null
	);
