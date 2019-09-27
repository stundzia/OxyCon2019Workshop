CREATE DATABASE IF NOT EXISTS `oxy_con`;

USE `oxy_con`;

create table oxy_con.jobs
(
	id bigint(11) auto_increment
		primary key,
	target varchar(50) not null,
	url varchar(2048) null,
	query varchar(2048) null,
	geo_location varchar(150) null,
	domain varchar(9) null,
	parse boolean default 0,
	status varchar(50) default 'init' null
);

create table oxy_con.job_results
(
	id bigint auto_increment,
	internal_id bigint null,
	job_id bigint null,
	content mediumblob null,
	page int null,
	status_code int null,
	url varchar(2048) null,
	constraint job_results_id_uindex
		unique (id)
);

alter table oxy_con.job_results
	add primary key (id);
