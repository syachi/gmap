#!/usr/bin/env perl
use ExtUtils::MakeMaker;
 
WriteMakefile(
  PREREQ_PM => {
    'Mojolicious' => '4.91',
    'DBI'         => '1.631',
    'DBD::Pg'     => '3.1.1',
  }
);
